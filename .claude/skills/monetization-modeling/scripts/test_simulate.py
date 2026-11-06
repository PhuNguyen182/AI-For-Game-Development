"""Tests for simulate.py. Run: python -I .claude/skills/monetization-modeling/scripts/test_simulate.py"""
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import simulate  # noqa: E402


def lab(value, label="measured"):
    return {"value": value, "label": label}


def one_set(**over):
    base = {
        "retention": lab({"1": 0.5, "7": 0.25, "30": 0.1}),
        "ads": {"interstitial": {"impressions_per_dau": lab(2), "ecpm": lab(10)}},
        "iap": {"purchases_per_dau": lab(0.01), "revenue_per_purchase": lab(5)},
        "economy": {"sources": {"levels": lab(100)}, "sinks": {"upgrades": lab(80)}},
    }
    base.update(over)
    return base


def spec(s=None):
    s = s or one_set()
    return {"sets": {"low": s, "base": s, "high": s}}


def base(s=None):
    return simulate.simulate(spec(s))["bands"]["base"]


class SimulateTest(unittest.TestCase):
    def test_golden_output(self):
        # Expected values come from an independent log-linear calculation, not from simulate.py.
        out = base()
        self.assertEqual(out["arpdau"], {"value": 0.07, "label": "measured", "proposed": []})
        self.assertEqual(out["active_days_d30"]["value"], 7.132127)
        self.assertEqual(out["arpu_d30"]["value"], 0.499249)
        self.assertEqual(out["active_days_d90"]["value"], 13.132127)
        self.assertEqual(out["arpu_d90"]["value"], 0.919249)
        self.assertEqual(out["currency"]["net_per_active_day"]["value"], 20.0)
        self.assertEqual(out["currency"]["balance_d30"]["value"], 142.642545)

    def test_same_input_same_output(self):
        a = json.dumps(simulate.simulate(spec()), sort_keys=True)
        self.assertEqual(a, json.dumps(simulate.simulate(spec()), sort_keys=True))

    def test_bands_come_from_their_own_sets(self):
        low = one_set(iap={"purchases_per_dau": lab(0.001), "revenue_per_purchase": lab(5)})
        out = simulate.simulate({"sets": {"low": low, "base": one_set(), "high": one_set()}})["bands"]
        self.assertLess(out["low"]["arpu_d30"]["value"], out["base"]["arpu_d30"]["value"])

    def test_a_missing_band_is_refused_not_invented(self):
        with self.assertRaisesRegex(simulate.Invalid, "missing high"):
            simulate.simulate({"sets": {"low": one_set(), "base": one_set()}})

    def test_weakest_label_wins(self):
        out = base(one_set(iap={"purchases_per_dau": lab(0.01, "assumption"), "revenue_per_purchase": lab(5)}))
        self.assertEqual(out["arpdau"]["label"], "assumption")
        self.assertEqual(out["arpu_d30"]["label"], "assumption")

    def test_benchmark_beats_measured_and_loses_to_assumption(self):
        out = base(one_set(ads={"x": {"impressions_per_dau": lab(1, "benchmark"), "ecpm": lab(1)}}))
        self.assertEqual(out["arpdau"]["label"], "benchmark")

    def test_arpdau_ignores_the_retention_label(self):
        out = base(one_set(retention=lab({"1": 0.5, "7": 0.25, "30": 0.1}, "assumption")))
        self.assertEqual(out["arpdau"]["label"], "measured")
        self.assertEqual(out["arpu_d30"]["label"], "assumption")

    def test_balance_takes_the_retention_label(self):
        out = base(one_set(retention=lab({"1": 0.5, "7": 0.25, "30": 0.1}, "assumption")))
        self.assertEqual(out["currency"]["net_per_active_day"]["label"], "measured")
        self.assertEqual(out["currency"]["balance_d30"]["label"], "assumption")

    def test_economy_label_stays_out_of_revenue(self):
        out = base(one_set(economy={"sources": {"a": lab(1, "assumption")}, "sinks": {}}))
        self.assertEqual(out["arpdau"]["label"], "measured")
        self.assertEqual(out["arpu_d30"]["label"], "measured")
        self.assertEqual(out["currency"]["net_per_active_day"]["label"], "assumption")

    def test_a_horizon_past_the_data_is_an_assumption_and_says_so(self):
        out = base()
        self.assertEqual(out["retention_last_day"], 30)
        self.assertEqual(out["arpu_d30"]["label"], "measured")
        self.assertNotIn("extrapolated_past_day", out["arpu_d30"])
        self.assertEqual(out["arpu_d90"]["label"], "assumption")
        self.assertEqual(out["arpu_d90"]["extrapolated_past_day"], 30)
        self.assertEqual(out["active_days_d90"]["extrapolated_past_day"], 30)

    def test_short_retention_data_flags_the_30_day_figures_too(self):
        out = base(one_set(retention=lab({"1": 0.5, "7": 0.25})))
        self.assertEqual(out["arpu_d30"]["label"], "assumption")
        self.assertEqual(out["arpu_d30"]["extrapolated_past_day"], 7)
        self.assertEqual(out["currency"]["balance_d30"]["extrapolated_past_day"], 7)

    def test_proposed_stays_out_of_propagation_and_is_named(self):
        got = base(one_set(iap={"purchases_per_dau": lab(0.01), "revenue_per_purchase": lab(4.99, "proposed")}))["arpu_d30"]
        self.assertEqual(got["label"], "measured")
        self.assertEqual(got["proposed"], ["iap.revenue_per_purchase"])

    def test_only_proposed_inputs_count_as_assumption(self):
        self.assertEqual(base({"retention": lab({"1": 0.5}, "proposed")})["arpdau"]["label"], "assumption")

    def test_invalid_inputs_are_refused(self):
        cases = [
            ("unknown label", one_set(ads={"x": {"impressions_per_dau": lab(1, "guess"), "ecpm": lab(1)}})),
            ("needs value and label", one_set(ads={"x": {"impressions_per_dau": 1, "ecpm": lab(1)}})),
            ("number >= 0", one_set(iap={"purchases_per_dau": lab(-1), "revenue_per_purchase": lab(5)})),
            ("rises above", one_set(retention=lab({"1": 0.2, "7": 0.5}))),
            (r"\(0, 1\]", one_set(retention=lab({"1": 1.5}))),
            ("integer >= 1", one_set(retention=lab({"x": 0.5}))),
            ("at least one day", one_set(retention=lab({}))),
        ]
        for pattern, s in cases:
            with self.assertRaisesRegex(simulate.Invalid, pattern):
                simulate.simulate(spec(s))

    def test_output_says_it_is_not_a_prediction(self):
        self.assertIn("not a prediction", simulate.simulate(spec())["note"])


if __name__ == "__main__":
    unittest.main()

"""Tests for simulate.py. Run: python -I .claude/skills/monetization-modeling/scripts/test_simulate.py"""
import json
import os
import subprocess
import sys
import tempfile
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
        out = base(one_set(iap={"purchases_per_dau": lab(0.01, "proposed"), "revenue_per_purchase": lab(4.99, "proposed")}, ads={}))
        self.assertEqual(out["arpdau"]["label"], "assumption")
        self.assertEqual(out["arpdau"]["proposed"], ["iap.purchases_per_dau", "iap.revenue_per_purchase"])

    def test_no_inputs_count_as_assumption(self):
        self.assertEqual(base(one_set(ads={}, iap={}))["arpdau"]["label"], "assumption")

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


class SimulateEdgeTest(unittest.TestCase):
    """QA edge cases (game-production-agent, qa-lead plan C4)."""

    def cli(self, text, hash_seed="0"):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "in.json"
            path.write_text(text, encoding="utf-8")
            env = dict(os.environ, PYTHONHASHSEED=hash_seed)
            r = subprocess.run([sys.executable, "-I", str(Path(simulate.__file__)), str(path)], capture_output=True, env=env)
        return r.returncode, r.stdout, r.stderr.decode("utf-8", "replace")

    def test_the_cli_output_is_byte_identical_across_runs_and_hash_seeds(self):
        text = json.dumps(spec())
        runs = [self.cli(text, seed) for seed in ("0", "1", "2", "random", "0")]
        self.assertEqual({code for code, _, _ in runs}, {0})
        self.assertEqual(len({out for _, out, _ in runs}), 1)
        self.assertEqual(json.loads(runs[0][1])["bands"]["base"]["arpu_d30"]["value"], 0.499249)  # the golden figure

    def test_the_d30_extrapolation_flag_turns_on_exactly_when_the_data_ends_before_day_29(self):
        # D30 sums days 0..29. Last supplied day 28 is one short, 29 is exactly enough, 30 is more than enough.
        for last, flagged in ((28, True), (29, False), (30, False)):
            with self.subTest(last_day=last):
                out = base(one_set(retention=lab({"1": 0.5, str(last): 0.1})))
                self.assertEqual(out["retention_last_day"], last)
                self.assertEqual("extrapolated_past_day" in out["arpu_d30"], flagged)
                self.assertEqual("extrapolated_past_day" in out["active_days_d30"], flagged)
                self.assertEqual("extrapolated_past_day" in out["currency"]["balance_d30"], flagged)
                self.assertEqual(out["arpu_d30"]["label"], "assumption" if flagged else "measured")

    def test_the_d90_extrapolation_flag_turns_on_exactly_when_the_data_ends_before_day_89(self):
        for last, flagged in ((88, True), (89, False), (90, False)):
            with self.subTest(last_day=last):
                out = base(one_set(retention=lab({"1": 0.5, str(last): 0.1})))
                self.assertEqual("extrapolated_past_day" in out["arpu_d90"], flagged)
                self.assertEqual(out["arpu_d90"]["label"], "assumption" if flagged else "measured")
                if flagged:
                    self.assertEqual(out["arpu_d90"]["extrapolated_past_day"], last)

    def test_retention_of_exactly_one_is_accepted_and_holds_every_player(self):
        out = base(one_set(retention=lab({"1": 1.0, "30": 1.0})))
        self.assertEqual(out["active_days_d30"]["value"], 30.0)

    def test_retention_of_zero_is_refused_because_the_curve_is_log_linear(self):
        with self.assertRaisesRegex(simulate.Invalid, r"\(0, 1\]"):
            simulate.simulate(spec(one_set(retention=lab({"1": 0.0}))))

    def test_zero_dau_activity_gives_zero_revenue_not_an_error(self):
        s = one_set(ads={"x": {"impressions_per_dau": lab(0), "ecpm": lab(10)}}, iap={"purchases_per_dau": lab(0), "revenue_per_purchase": lab(5)})
        out = base(s)
        self.assertEqual(out["arpdau"]["value"], 0.0)
        self.assertEqual(out["arpu_d30"]["value"], 0.0)
        self.assertEqual(out["arpdau"]["label"], "measured")

    def test_non_finite_and_negative_numbers_are_refused_in_every_numeric_slot(self):
        bad = [float("nan"), float("inf"), float("-inf"), -0.5, -1]
        for value in bad:
            slots = {
                "ads impressions": one_set(ads={"x": {"impressions_per_dau": lab(value), "ecpm": lab(1)}}),
                "ads ecpm": one_set(ads={"x": {"impressions_per_dau": lab(1), "ecpm": lab(value)}}),
                "iap purchases": one_set(iap={"purchases_per_dau": lab(value), "revenue_per_purchase": lab(5)}),
                "iap revenue": one_set(iap={"purchases_per_dau": lab(0.1), "revenue_per_purchase": lab(value)}),
                "economy source": one_set(economy={"sources": {"a": lab(value)}, "sinks": {}}),
                "economy sink": one_set(economy={"sources": {}, "sinks": {"a": lab(value)}}),
            }
            for slot, s in slots.items():
                with self.subTest(slot=slot, value=value):
                    with self.assertRaisesRegex(simulate.Invalid, "number >= 0"):
                        simulate.simulate(spec(s))

    def test_non_finite_and_out_of_range_retention_is_refused(self):
        for rate in (float("nan"), float("inf"), float("-inf"), -0.1, 1.0000001):
            with self.subTest(rate=rate):
                with self.assertRaisesRegex(simulate.Invalid, r"\(0, 1\]"):
                    simulate.simulate(spec(one_set(retention=lab({"1": rate}))))

    def test_a_json_file_holding_nan_or_infinity_exits_2_with_no_output(self):
        for token in ("NaN", "Infinity", "-Infinity", "-1"):
            with self.subTest(token=token):
                raw = json.dumps(spec(one_set(ads={"x": {"impressions_per_dau": lab(1), "ecpm": lab(1)}}))).replace('"impressions_per_dau": {"value": 1', '"impressions_per_dau": {"value": %s' % token)
                self.assertIn(token, raw)
                code, out, err = self.cli(raw)
                self.assertEqual(code, 2)
                self.assertEqual(out, b"")
                self.assertTrue(err.startswith("invalid:"), err)

    def test_booleans_and_numeric_strings_are_not_numbers(self):
        for value in (True, False, "5", None, [1]):
            with self.subTest(value=value):
                with self.assertRaisesRegex(simulate.Invalid, "number >= 0"):
                    simulate.simulate(spec(one_set(ads={"x": {"impressions_per_dau": lab(value), "ecpm": lab(1)}})))

    def test_a_proposed_value_beside_measured_inputs_keeps_measured_and_names_itself(self):
        s = one_set(ads={"x": {"impressions_per_dau": lab(2), "ecpm": lab(12.5, "proposed")}})
        out = base(s)
        for key in ("arpdau", "arpu_d30"):
            self.assertEqual(out[key]["label"], "measured", key)
            self.assertEqual(out[key]["proposed"], ["ads.x.ecpm"], key)
        self.assertEqual(out["currency"]["net_per_active_day"]["proposed"], [])  # the economy used no proposed input

    def test_a_proposed_value_beside_an_assumption_keeps_assumption_and_names_itself(self):
        s = one_set(ads={"x": {"impressions_per_dau": lab(2, "assumption"), "ecpm": lab(12.5, "proposed")}})
        out = base(s)
        self.assertEqual(out["arpdau"]["label"], "assumption")
        self.assertEqual(out["arpdau"]["proposed"], ["ads.x.ecpm"])

    def test_a_proposed_retention_curve_is_named_on_the_figures_that_use_it(self):
        out = base(one_set(retention=lab({"1": 0.5, "30": 0.1}, "proposed")))
        self.assertEqual(out["arpdau"]["proposed"], [])
        self.assertEqual(out["arpu_d30"]["proposed"], ["retention"])
        self.assertEqual(out["arpu_d30"]["label"], "measured")  # the money inputs are measured; the proposed curve is excluded

    def test_a_non_decimal_digit_day_key_is_refused_not_a_traceback(self):
        # str.isdigit() is true for "²" but int() rejects it; the CLI turns the ValueError into exit 2.
        code, out, err = self.cli(json.dumps(spec(one_set(retention=lab({"²": 0.5})))))
        self.assertEqual(code, 2)
        self.assertEqual(out, b"")

    def test_a_missing_or_wrong_shape_input_exits_2(self):
        for text in ("[]", "{}", '{"sets": []}', '{"sets": {"low": 1, "base": 2, "high": 3}}', "not json", ""):
            with self.subTest(text=text):
                code, out, err = self.cli(text)
                self.assertEqual(code, 2, text)
                self.assertEqual(out, b"", text)


if __name__ == "__main__":
    unittest.main()

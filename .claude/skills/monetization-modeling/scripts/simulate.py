"""Monetisation arithmetic over three labelled input sets. Stdlib only, deterministic, no randomness.

Not a prediction: bands come only from the low, base and high sets the adviser supplies. Every figure carries the
weakest label among the inputs it uses, and no other. `proposed` values (a candidate's new price or placement) are
design choices, so they stay out of that propagation and are named instead. A horizon past the last supplied
retention day holds retention flat, which is invented: those figures are `assumption` and say where the data ends.

Run: python -I simulate.py <input.json>. Prints JSON. Exit 2 on invalid input. Tests: python -I test_simulate.py.
"""
import json
import math
import sys

STRENGTH = {"measured": 0, "benchmark": 1, "assumption": 2}
LABELS = set(STRENGTH) | {"proposed"}
BANDS = ("low", "base", "high")
HORIZONS = (30, 90)
NOTE = "Arithmetic over the supplied inputs, not a prediction."


class Invalid(Exception):
    pass


class Inputs:
    """Reads labelled values and remembers which labels and proposed names a figure used."""

    def __init__(self):
        self.labels = []
        self.proposed = []

    def take(self, name, item):
        if not isinstance(item, dict) or "value" not in item or "label" not in item:
            raise Invalid("%s: needs value and label" % name)
        label = item["label"]
        if label not in LABELS:
            raise Invalid("%s: unknown label %r" % (name, label))
        self.labels.append(label)
        if label == "proposed":
            self.proposed.append(name)
        return item["value"]

    def number(self, name, item):
        value = self.take(name, item)
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
            raise Invalid("%s: must be a number >= 0" % name)
        return float(value)


def stamp(value, *ledgers, extrapolated_past=None):
    """The weakest label of exactly the ledgers this figure used; flat-held retention counts as an assumption."""
    labels = [x for ledger in ledgers for x in ledger.labels if x != "proposed"]
    if extrapolated_past is not None:
        labels.append("assumption")
    # Nothing but proposed values means nothing was observed or sourced: that is an assumption.
    label = max(labels, key=STRENGTH.get) if labels else "assumption"
    out = {"value": round(value, 6), "label": label, "proposed": sorted({n for ledger in ledgers for n in ledger.proposed})}
    if extrapolated_past is not None:
        out["extrapolated_past_day"] = extrapolated_past
    return out


def retention_curve(points):
    """Daily retention, log-linear between the given days, day 0 is 1. Returns (curve, last supplied day)."""
    if not isinstance(points, dict) or not points:
        raise Invalid("retention: needs at least one day")
    days = {}
    for day, rate in points.items():
        if not str(day).isdigit() or int(day) < 1:
            raise Invalid("retention: day %r must be an integer >= 1" % day)
        if isinstance(rate, bool) or not isinstance(rate, (int, float)) or not 0 < rate <= 1:
            raise Invalid("retention: day %s must be in (0, 1]" % day)
        days[int(day)] = float(rate)
    known = [(0, 1.0)] + sorted(days.items())
    for (_, a), (d, b) in zip(known, known[1:]):
        if b > a:
            raise Invalid("retention: day %d rises above an earlier day" % d)

    def at(day):
        if day <= 0:
            return 1.0
        for (d0, r0), (d1, r1) in zip(known, known[1:]):
            if d0 <= day <= d1:
                t = (day - d0) / (d1 - d0)
                return math.exp(math.log(r0) + t * (math.log(r1) - math.log(r0)))
        return known[-1][1]  # past the last point: held flat, flagged by the caller
    return at, known[-1][0]


def band(data):
    money = Inputs()
    placements = data.get("ads") or {}
    ad_rev = 0.0
    for name in sorted(placements):
        p = placements[name]
        ad_rev += money.number("ads.%s.impressions_per_dau" % name, p.get("impressions_per_dau")) * \
            money.number("ads.%s.ecpm" % name, p.get("ecpm")) / 1000.0
    iap = data.get("iap") or {}
    iap_rev = 0.0
    if iap:
        iap_rev = money.number("iap.purchases_per_dau", iap.get("purchases_per_dau")) * money.number("iap.revenue_per_purchase", iap.get("revenue_per_purchase"))
    arpdau = ad_rev + iap_rev
    retention = Inputs()
    curve, last_day = retention_curve(retention.take("retention", data.get("retention")))
    result = {"arpdau": stamp(arpdau, money), "retention_last_day": last_day}
    for horizon in HORIZONS:
        active_days = sum(curve(d) for d in range(horizon))
        past = last_day if horizon - 1 > last_day else None
        result["active_days_d%d" % horizon] = stamp(active_days, retention, extrapolated_past=past)
        result["arpu_d%d" % horizon] = stamp(active_days * arpdau, money, retention, extrapolated_past=past)
    result["currency"] = currency(data.get("economy") or {}, curve, last_day, retention)
    return result


def currency(economy, curve, last_day, retention):
    """Net currency per active day (economy only) and per retained player over 30 days (economy and retention)."""
    eco = Inputs()
    net = 0.0
    for sign, group in ((1, "sources"), (-1, "sinks")):
        items = economy.get(group) or {}
        for name in sorted(items):
            net += sign * eco.number("economy.%s.%s" % (group, name), items[name])
    past = last_day if 30 - 1 > last_day else None
    return {"net_per_active_day": stamp(net, eco),
            "balance_d30": stamp(net * sum(curve(d) for d in range(30)), eco, retention, extrapolated_past=past)}


def simulate(spec):
    sets = spec.get("sets") if isinstance(spec, dict) else None
    if not isinstance(sets, dict):
        raise Invalid("input needs a sets object")
    missing = [b for b in BANDS if b not in sets]
    if missing:
        raise Invalid("sets: missing %s; bands come only from supplied inputs" % ", ".join(missing))
    return {"note": NOTE, "bands": {b: band(sets[b]) for b in BANDS}}


def main(argv):
    if len(argv) != 2:
        print("usage: simulate.py <input.json>", file=sys.stderr)
        return 2
    try:
        with open(argv[1], encoding="utf-8-sig") as f:
            spec = json.load(f)
        print(json.dumps(simulate(spec), indent=2, sort_keys=True))
        return 0
    except (Invalid, ValueError, OSError, AttributeError, TypeError) as ex:
        print("invalid: %s" % ex, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))

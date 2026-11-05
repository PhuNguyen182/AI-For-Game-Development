---
name: monetization-modeling
description: "Economy sources and sinks, ad placement, IAP ladder, pricing, ARPU arithmetic via simulate.py. Use for monetisation reads."
user-invocable: false
---

# Monetization modeling

- **Not for:** vendor choice (`ad-mediation-monetization-platform`, `/decide`), SDK wiring (`sdk-platform-engineer`), user acquisition and marketing (out of scope, so LTV against CPI stays unanswered).
- **Sources:** the GDD's economy, `CLAUDE.md` (Compliance, Stack headline, KPI targets), the data pack.

## Scripts
- **[simulate.py](scripts/simulate.py):** run `<python> -I "${CLAUDE_SKILL_DIR}/scripts/simulate.py" <input.json>` → JSON low/base/high ARPDAU, ARPU at D30 and D90, currency net and balance, each with its label.

## Simulator input
- **Who runs it:** advisers have no shell: return this JSON in the finding, and the main session runs it and sends the output back.

```json
{"sets": {"low": {}, "base": {
  "retention": {"value": {"1": 0.4, "7": 0.15, "30": 0.05}, "label": "measured"},
  "ads": {"rewarded": {"impressions_per_dau": {"value": 1.5, "label": "measured"}, "ecpm": {"value": 12, "label": "benchmark"}}},
  "iap": {"purchases_per_dau": {"value": 0.005, "label": "assumption"}, "revenue_per_purchase": {"value": 4.99, "label": "proposed"}},
  "economy": {"sources": {"levels": {"value": 100, "label": "assumption"}}, "sinks": {"upgrades": {"value": 80, "label": "assumption"}}}
}, "high": {}}}
```

- **Three sets:** fill all three; bands come only from them, and a missing band is refused rather than invented.
- **Sample values:** the numbers above show the shape only, never a benchmark.

## Steps
1. **Read the baseline:** current placements, prices and economy from the GDD and config; observed figures from the pack.
2. **Balance the economy:** list every source and sink; a positive net means inflation, so name what absorbs it.
3. **Read ad placements:** each at a natural break, rewarded before forced, with its retention risk stated.
4. **Read the IAP ladder:** first-purchase offer, price points, what each buys in play time; ownership is server-checked per `core.md`.
5. **Propose 2–4 candidates:** each with its change, the simulator input and a retention risk.
6. **Set the kill rule:** per candidate: success metric, measurement window, rollback threshold.
7. **Check policy:** store rules for ads and purchases, loot-box disclosure, `CLAUDE.md` → Compliance.

## Never
- **Prediction language:** the simulator is arithmetic over inputs; report it as "if these inputs hold".
- **Revenue claim without a pack:** with no data pack, show scenarios with no recommendation and end with what to measure.
- **Monetising the wound:** selling relief from friction the design added for that purpose; show it as a conflict with `game-designer`.

## Example
- **"Raise interstitial frequency to double ARPDAU":** challenged — simulated the revenue side, stated that the retention cost is unmeasured, and proposed a capped test with a rollback threshold.

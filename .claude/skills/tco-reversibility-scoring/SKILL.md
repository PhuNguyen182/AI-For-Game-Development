---
name: tco-reversibility-scoring
description: "CTO scoring rubric: total cost of ownership (upfront, ongoing, scaling, exit) plus Low/Medium/High reversibility, outweighing upfront cost on gameplay-critical systems. Use as the frame for every strategic tech call."
user-invocable: false
---

# TCO / Reversibility Scoring

Not for: gathering the domain trade-off data (`backend-build-vs-buy`, `netcode-architecture-decision`, `anti-cheat-strategy`, `ad-mediation-monetization-platform`, `analytics-telemetry-platform`, `live-ops-content-pipeline`, `cross-platform-expansion-assessment`, `tech-vendor-dependency-risk-assessment`), recording the standard (`engineering-standard-adr-authoring`), routine estimates (`technical-architect`).

## Steps
1. **Ask first when scale, team capacity or target regions are unknown and load-bearing** — they move every bucket; never score a guessed input.
2. **Enumerate only options genuinely on the table** (2–4); a strawman inflates the winner's margin. Options of incomparable scope: say so instead of forcing a score.
3. **Score four buckets separately, never one blended figure** — upfront (licence, integration, migration), ongoing (subscription, revenue share, maintenance headcount), scaling curve (flat / linear / step per player, server or region), exit cost.
4. **Rate reversibility by blast radius, not vendor marketing** — High: swappable behind an abstraction (ad SDK behind an interface). Medium: swap needs real migration (backend provider with data). Low: structurally locked once shipped (netcode foundation, kernel anti-cheat in store certification).
5. **On gameplay-critical systems (netcode, anti-cheat, save format) weight reversibility above upfront cost** — a cheap irreversible choice has unbounded downside. If Low-upfront beats Low-reversibility, state the tension explicitly.
6. **Name the crossover point for step or steep-linear curves** ("cheaper until ~X CCU").
7. **Fetch the vendor's own pricing page (`WebFetch`) before scoring ongoing cost**, else mark the bucket provisional; never present an estimate as scored.
8. **Re-score from current data**; never reuse a score from a similarly named earlier decision.
9. **Carry the score verbatim into the Technical Decision** as an annotation ("TCO: Medium upfront / Low ongoing; Reversibility: Low"), before writing the product/technical reasoning fields.

## Output
```
## TCO / Reversibility Score — <decision>
| Option | Upfront | Ongoing | Scaling curve | Exit cost | Reversibility |
|---|---|---|---|---|---|
| <option> | Low/Med/High | Low/Med/High | flat / linear / step @ <crossover> | Low/Med/High | Low/Med/High |
- Gameplay-critical: yes/no
- Pricing basis: confirmed from <URL> / provisional
- Decision: <option> — <score tied to choice>
- Routed to: <domain skill or role>
```
On request only, add `Known limitations`, `Latent concerns`, `Future remediation` (each with its re-score trigger).

## Example
- "Managed is cheaper day one, we can swap later" → declined: "swap later" is the reversibility rating, and it scored Low (vendor schema shapes the save format); with exit cost weighted above upfront, self-hosted wins.

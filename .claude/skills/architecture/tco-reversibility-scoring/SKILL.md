---
name: tco-reversibility-scoring
description: >
  Shared scoring framework — total cost of ownership (TCO) across upfront/
  ongoing/scaling/exit-cost buckets, plus a reversibility rating — that every
  other CTO decision skill (netcode, backend, anti-cheat, vendor risk, ad
  mediation, live-ops, analytics, cross-platform) references so every
  strategic technology call is judged by the same consistent criteria. Use
  this whenever the CTO agent is about to compare two or more foundational
  options (build vs buy, vendor A vs B, platform commitment) before writing
  the "Reasoning" fields of a Technical Decision. Do not use this for a
  routine engineering estimate that Technical Architect or a Tech Lead can
  already produce without CTO involvement.
---

# TCO / Reversibility Scoring

## 1. Objective
Give the CTO a single, consistent lens for scoring any strategic technology decision, so the same criteria produce comparable, defensible calls across different decisions instead of reasoning invented fresh each time.

## 2. Role
Act as the CTO's decision-scoring discipline: a structured cost/risk calculator that feeds the CTO's Technical Decision output, not a new line of reasoning in itself.

## 3. When to invoke this skill
- Every time the CTO is about to make a Technical Decision that involves choosing between two or more foundational options.
- Before writing the "Reasoning (product terms)" / "Reasoning (technical)" fields — score first, then translate the score into those fields.
- Any of the domain-specific CTO skills (`netcode-architecture-decision`, `backend-build-vs-buy`, `anti-cheat-strategy`, `tech-vendor-dependency-risk-assessment`, `ad-mediation-monetization-platform`, `live-ops-content-pipeline`, `analytics-telemetry-platform`, `cross-platform-expansion-assessment`) invoke this skill internally rather than inventing their own scoring logic.
- Negative trigger: don't invoke for a routine engineering estimate that Technical Architect or a Tech Lead can already produce without CTO's involvement.

## 4. How to use this skill
1. Enumerate the realistic options actually on the table (usually 2-4) — don't score against strawmen nobody would seriously choose.
2. For each option, score TCO across four buckets, each Low/Medium/High:
   - **Upfront cost** — license fee, integration effort, migration cost.
   - **Ongoing cost** — subscription, revenue share, maintenance headcount.
   - **Scaling cost curve** — cost per additional player/server/region: flat, linear, or step-function.
   - **Exit cost** — what it costs to switch away from this option later.
3. For each option, score **Reversibility** Low/Medium/High:
   - High — swappable behind an abstraction with contained blast radius (e.g. an ad SDK behind an interface).
   - Medium — swappable but with real migration work (e.g. a backend provider swap needing a data migration).
   - Low — structurally locked in once shipped (e.g. a netcode foundation baked into every gameplay system, or a kernel-level anti-cheat baked into store certification).
4. Weight reversibility more heavily than raw upfront cost whenever the decision touches a gameplay-critical system (netcode, anti-cheat, save-data format) — a cheap-but-irreversible choice is a worse bet than a pricier-but-reversible one for those systems.
5. State the resulting score inline in the CTO's Technical Decision output as a short annotation (e.g. "TCO: Medium upfront / Low ongoing; Reversibility: Low") so the reasoning is traceable, not asserted.
6. If real cost/pricing data is missing, don't estimate silently — either fetch the vendor's actual pricing/docs page (via `WebFetch`) or flag the gap explicitly in the decision output as "provisional, pending confirmed pricing."

## 5. Specific goals / tasks this skill performs
- Every CTO Technical Decision comparing 2+ options carries an explicit TCO/reversibility score, not just a prose preference.
- Reversibility is weighted appropriately for gameplay-critical, hard-to-undo systems.
- Missing cost data is flagged, never guessed silently.
- Out of scope: gathering the raw domain-specific trade-off data itself — that's what the domain skills (netcode, backend, anti-cheat, etc.) hand to this skill.

## 6. Output format
```
## TCO / Reversibility Score
| Option | Upfront | Ongoing | Scaling curve | Exit cost | Reversibility |
|---|---|---|---|---|---|
| <option> | Low/Med/High | Low/Med/High | flat/linear/step | Low/Med/High | Low/Med/High |

Recommended: <option> — <one-line reasoning tying the score to the recommendation>
```

## 7. Examples
**Example 1**
- Input: choosing between licensing Mirror and building custom netcode for a PvP action game.
- Output: Mirror scores Low upfront / Low ongoing / flat scaling / Medium exit cost / Medium reversibility; custom scores High upfront / Medium ongoing / flat scaling / Low exit cost / Low reversibility. Recommended: Mirror — comparable long-term cost with meaningfully better reversibility.

**Example 2**
- Input: choosing an ad mediation platform where pricing pages weren't yet reviewed.
- Output: score marked "provisional, pending confirmed pricing" for the ongoing-cost bucket, with a note to fetch each vendor's current rate card via `WebFetch` before finalizing the decision.

## 8. Edge cases & guardrails
- Never let a Low-upfront-cost option win against a Low-reversibility score on a gameplay-critical system without calling that tension out explicitly.
- If the options aren't genuinely comparable (wildly different scope), say so instead of forcing a score onto them.
- Don't reuse a stale score from a previous, similarly-named decision — vendor pricing and project scale change; re-score from current data each time.

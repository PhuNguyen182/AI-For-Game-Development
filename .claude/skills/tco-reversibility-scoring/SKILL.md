---
name: tco-reversibility-scoring
description: >
  Shared CTO scoring rubric — total cost of ownership split across upfront,
  ongoing, scaling-curve, and exit-cost buckets, plus a Low/Medium/High
  reversibility rating that outweighs upfront cost on gameplay-critical
  systems (netcode, anti-cheat, save-data format). Use when comparing two or
  more foundational options before writing a Technical Decision's Reasoning
  fields; every domain CTO skill calls this instead of inventing its own
  scoring. Not for: gathering the domain trade-off data being scored
  (`backend-build-vs-buy`, `netcode-architecture-decision`,
  `anti-cheat-strategy`, `ad-mediation-monetization-platform`,
  `analytics-telemetry-platform`, `live-ops-content-pipeline`,
  `cross-platform-expansion-assessment`,
  `tech-vendor-dependency-risk-assessment`), recording the resulting standard
  (`engineering-standard-adr-authoring`), routine estimates a Tech Lead
  already produces (`technical-architect`).
---

# TCO / Reversibility Scoring — comparing foundational technology options

## 1. Objective
Give the CTO one consistent lens for scoring any strategic technology decision, so the same criteria produce comparable, defensible calls across different domains instead of reasoning invented fresh each time.

## 2. Role
Act as the CTO's decision-scoring discipline: a structured cost/risk calculator feeding the Technical Decision output, not a separate line of reasoning competing with it.

## 3. When to invoke this skill
- The CTO is about to make a Technical Decision choosing between two or more foundational options.
- Before writing the "Reasoning (product terms)" / "Reasoning (technical)" fields — score first, then translate the score into those fields.
- A domain CTO skill needs a score and calls in here rather than inventing scoring logic locally.
- Negative trigger: the domain trade-off data itself is missing — gather it in the owning domain skill first; this skill scores what it is handed.
- Negative trigger: the decision's outcome needs to become a durable cross-project standard — that recording step is `engineering-standard-adr-authoring`.
- Negative trigger: a routine engineering estimate Technical Architect or a Tech Lead already produces without CTO involvement.

## 4. How to use this skill
1. **Enumerate only options genuinely on the table** — usually two to four. A strawman nobody would seriously choose inflates the winner's margin and hides the trade-off that actually decides the call.
2. **Score all four TCO buckets separately, never one blended cost figure** — upfront (license, integration, migration effort), ongoing (subscription, revenue share, maintenance headcount), scaling curve (flat / linear / step-function per player, server, or region), exit cost (what switching away later costs). A blended number hides which bucket is deciding.
3. **Rate reversibility from blast radius, not from vendor marketing** — High: swappable behind an abstraction, contained (an ad SDK behind an interface). Medium: swappable with real migration work (a backend provider needing a data migration). Low: structurally locked in once shipped (a netcode foundation baked into every gameplay system; kernel-level anti-cheat baked into store certification).
4. **Weight reversibility above upfront cost whenever the decision touches a gameplay-critical system** — netcode, anti-cheat, save-data format. There, a cheap irreversible choice is a worse bet than a pricier reversible one, because the cost of being wrong is unbounded rather than one-off.
5. **Name the crossover point whenever a scaling curve is step-function or steeply linear** — "cheaper until roughly X concurrent players, then more expensive" is the decision-relevant fact. Launch-day sticker price on its own decides nothing.
6. **Fetch real pricing before scoring an ongoing-cost bucket, or mark that bucket provisional** — pull the vendor's own pricing page with `WebFetch`. A silently estimated price is the fastest route from this rubric to a confident wrong answer.
7. **Carry the score into the Technical Decision output verbatim as a short annotation** — for example "TCO: Medium upfront / Low ongoing; Reversibility: Low". Reasoning that was scored but not shown reads to the GD as an assertion.
8. **Write the score and its rationale in English**, per `language-and-comments.md`'s Working language section — the Technical Decision is a durable artifact; the Vietnamese reply to the GD is the final message, not the document.
9. **Refuse to score options whose scope differs enough that the buckets stop measuring the same thing** — say so instead. A forced score across incomparable options is worse than none, because it looks defensible.
10. **Ask before scoring when project scale, team capacity, or target regions are unknown and load-bearing** — those three inputs move every bucket at once. Guessing one produces a score that is precise and wrong.

## 5. Specific goals / tasks this skill performs
- Attach an explicit TCO/reversibility score to every CTO Technical Decision that compares two or more options, replacing prose preference.
- Weight reversibility correctly for gameplay-critical, hard-to-undo systems.
- Surface the scaling-curve crossover point rather than launch-day cost alone.
- Flag missing cost data as provisional instead of guessing it silently.
- Out of scope: gathering the raw domain trade-off data (the domain CTO skills), recording the outcome as a standard (`engineering-standard-adr-authoring`), routine estimates (`technical-architect`).

## 6. Output format
```
## TCO / Reversibility Score — <decision name>
| Option | Upfront | Ongoing | Scaling curve | Exit cost | Reversibility |
|---|---|---|---|---|---|
| <option> | Low/Med/High | Low/Med/High | flat / linear / step @ <crossover> | Low/Med/High | Low/Med/High |

- Gameplay-critical: yes/no — if yes, reversibility outweighs upfront cost
- Pricing basis: confirmed from <vendor pricing URL> / provisional, pending confirmed pricing
- Rule compliance: score and rationale written in English, per Working language
- Decision: <option> — <one line tying the score to the choice>
- Routed to: <the domain skill or role that acts on this score>
```

**Extended report — emit ONLY when the requester asks for it.** It replaces the one-line `Decision` rationale with all three fields:
```
- Known limitations: <what this score does not cover — which buckets rest on estimates>
- Latent concerns: <assumptions holding only at current scale, thresholds not yet reached>
- Future remediation: <the re-score trigger for each concern — the scale, price change, or date that invalidates it>
```

## 7. Examples
**Example 1**
- Input: license Mirror or build custom netcode for a PvP action game.
- Output: Mirror scores Low upfront / Low ongoing / flat scaling / Medium exit / Medium reversibility; custom scores High upfront / Medium ongoing / flat scaling / Low exit / Low reversibility. Decision: Mirror — comparable long-run cost with materially better reversibility on a gameplay-critical system. Routed to `netcode-architecture-decision`.

**Example 2**
- Input: "the managed option is cheaper on day one, just take it — we can always swap later."
- Output: declined for this decision. "Swap later" is the reversibility rating, and here it scored Low: the save-data format is shaped by the vendor's schema, so switching means migrating live player data. Re-scored with exit cost weighted above upfront, the pricier self-hosted option wins.

**Example 3**
- Input: an ad mediation comparison where no vendor pricing page had been read.
- Output: ongoing-cost bucket marked "provisional, pending confirmed pricing" rather than estimated; every other bucket scored normally. Decision withheld until the rate cards are fetched, since ongoing cost is the bucket that separates these two options.

## 8. Edge cases & guardrails
- Never let a Low-upfront option beat a Low-reversibility score on a gameplay-critical system without stating that tension explicitly — a silent trade there is the expensive mistake this rubric exists to prevent.
- Never present an estimated price as a scored one — mark the bucket provisional, per §4.
- Never reuse a score from an earlier, similarly-named decision: vendor pricing and project scale both move. Re-score from current data.
- Never expand a score into a full domain analysis — if the trade-off data is thin, the fix is the domain skill, not more scoring detail here.
- If scale, ops capacity, or target regions are unknown and load-bearing, ask — do not score on a guessed input.

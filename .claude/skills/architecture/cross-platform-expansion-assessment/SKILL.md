---
name: cross-platform-expansion-assessment
description: >
  Framework for estimating the engineering cost, timeline, and risk of
  adding a platform (console, an additional mobile OS, or cross-play) before
  the GD commits to it in the GDD — broken into certification/review cost,
  input/UI reflow, netcode/anti-cheat impact, and store/platform SDK
  integration. Use this whenever the GD wants to understand the engineering
  cost of supporting an extra platform before locking it into the GDD. Do
  not use this once the platform is already committed and Technical
  Architect/Tech Leads are doing the actual integration work — that's
  routine execution. Do not use this for a same-family platform variant
  already effectively covered (e.g. a new Android device tier) — see
  unity-engineer's per-platform quality settings work instead.
---

# Cross-Platform Expansion Assessment

## 1. Objective
Back the CTO's own canonical use case — assessing the engineering cost of supporting an extra platform before the GD commits to it — with an actual framework instead of an off-the-cuff estimate.

## 2. Role
Act as a cross-platform-shipping-experienced CTO who has taken titles through console certification and mobile store review.

## 3. When to invoke this skill
- The GD wants to understand the engineering cost/timeline/risk of adding a platform (console, an additional mobile OS, cross-play) before committing to it in the GDD.
- Negative trigger: don't use this once the platform is already committed and Technical Architect/Tech Leads are doing the actual integration work — that's routine execution, not a strategic call.
- Negative trigger: don't use this for a same-family platform variant that's already effectively covered (e.g. adding a new Android device tier isn't a platform expansion in this sense) — see `unity-engineer`'s per-platform quality settings work instead.

## 4. How to use this skill
1. Break the expansion into its real cost buckets: certification process (console cert timeline/fees), input/UI reflow (controller support, safe-area/aspect-ratio handling for a new form factor), netcode implications (does cross-play change the sync model's latency budget or require platform-specific matchmaking pools?), and store/platform SDK integration (achievements, platform-specific IAP/social).
2. Check whether the existing netcode/anti-cheat foundation (from `netcode-architecture-decision`/`anti-cheat-strategy`) already supports the new platform, or whether the expansion forces a revisit of one of those earlier decisions — a platform expansion that invalidates a prior foundational choice is a much bigger call than a contained cost estimate.
3. Estimate realistic timeline impact — certification and review cycles have fixed external lead times regardless of engineering speed; state those separately from engineering effort.
4. Score with `tco-reversibility-scoring` — most platform expansions are Medium-High reversibility (a platform can usually be dropped later without unwinding gameplay code), unless the expansion forced a foundational netcode/anti-cheat change, in which case treat it as Low.
5. Present the assessment to the GD framed as cost/timeline/risk in product terms — this is explicitly a GD decision per the CTO's own guardrails, not one the CTO settles unilaterally.

## 5. Specific goals / tasks this skill performs
- Produce a cost/timeline/risk estimate for a proposed platform expansion, broken into real cost buckets rather than a single guessed number.
- Flag when an expansion would force revisiting a prior foundational decision (netcode/anti-cheat) rather than treating it as a contained cost.
- Always route the final call to the GD.

## 6. Output format
```
## Cross-Platform Expansion Assessment — <platform>
- Certification/review cost & timeline: ...
- Input/UI reflow cost: ...
- Netcode/anti-cheat impact: none / revisit required (detail)
- Store/platform SDK integration cost: ...
- TCO/Reversibility score: ...
- Overall estimate: <cost/timeline range>
- Needs GD decision: yes (always) — framed trade-off: ...
```

## 7. Examples
**Example 1**
- Input: adding a console SKU to an already-live PC/mobile PvP game.
- Output: certification timeline flagged as the real bottleneck; existing netcode already supports the console's constraints; no foundational revisit needed.

**Example 2**
- Input: adding cross-play to a previously PC-only competitive game.
- Output: flags that the existing anti-cheat tier (kernel-level, PC-only) doesn't carry over to consoles, forcing a revisit of `anti-cheat-strategy` before the expansion can be estimated with confidence.

## 8. Edge cases & guardrails
- Never present a platform-expansion cost estimate without separating the fixed external timeline (certification/review) from actual engineering effort — conflating them misleads the GD's planning.
- If the expansion forces revisiting netcode or anti-cheat, say so plainly rather than folding it into a generic "extra cost" line — that's a materially different kind of risk.
- This assessment is always framed for a GD decision — never treat "should we expand to this platform" as something the CTO settles alone.

---
name: cross-platform-expansion-assessment
description: >
  Cost, timeline, and risk framework for adding a platform — a console SKU, an
  additional mobile OS, Steam Deck, or cross-play — before the GD commits it to
  the GDD. Splits the estimate into certification/review lead time
  (TRC/TCR/Lotcheck, App Review), input and UI reflow (controller mapping, safe
  area, aspect ratio), netcode and anti-cheat impact, and platform SDK
  integration (Steamworks, Google Play Games Services, GameCenter, StoreKit,
  platform IAP). Use before a platform is locked in.
  Not for: integration work on an already-committed platform (`tech-lead-sdk-platform`), per-device quality tiers (`unity-engineer`), sync model choice (`netcode-architecture-decision`), cheat posture (`anti-cheat-strategy`), the scoring rubric (`tco-reversibility-scoring`).
---

# Cross-Platform Expansion Assessment — cost and risk of adding a platform

## 1. Objective
Turn "how much would supporting this platform cost us" into a bucketed estimate the GD can actually plan against — separating fixed external certification lead time from compressible engineering effort, and catching the case where an expansion quietly reopens a foundational netcode or anti-cheat decision instead of adding a contained cost.

## 2. Role
Act as a cross-platform-shipping CTO who has taken titles through console certification and mobile store review, and who knows which costs recur on every future release rather than once.

## 3. When to invoke this skill
- The GD wants the engineering cost, timeline, and risk of adding a platform before committing to it in the GDD.
- A publisher, platform holder, or storefront opportunity puts a new SKU on the table and someone needs a number before answering.
- Cross-play is proposed for a game currently shipping on a single platform family.
- Negative trigger: the platform is already committed and the SDK, store, and certification work is underway — that is `tech-lead-sdk-platform`'s execution work.
- Negative trigger: supporting another device tier inside a platform already shipped, such as a new Android performance bracket — that is `unity-engineer`'s per-platform quality settings work, not an expansion.
- Negative trigger: choosing the netcode foundation or synchronization model — that is `netcode-architecture-decision`, which this assessment consults rather than redoes.
- Negative trigger: choosing the anti-cheat tier — that is `anti-cheat-strategy`, same relationship.
- Negative trigger: the cost/reversibility arithmetic itself — that rubric is `tco-reversibility-scoring`.

## 4. How to use this skill
1. **Split the expansion into its four real cost buckets before producing any number** — certification and review, input and UI reflow, netcode and anti-cheat impact, and platform SDK integration. A single blended figure hides which bucket is actually driving the estimate, which is the one thing the GD needs to know.
2. **Report external certification lead time as a separate, non-compressible line** — console certification and store review run on the platform holder's calendar, not the team's, and adding engineers does not shorten them. A failed submission restarts that clock, so state the resubmission risk alongside the nominal window.
3. **Check whether the new platform invalidates a prior foundational decision before estimating anything else** — if the committed netcode model or anti-cheat tier does not carry over, this stops being a contained cost and becomes a reopening of `netcode-architecture-decision` or `anti-cheat-strategy`, which must be said plainly rather than folded into a larger number.
4. **Treat cross-play as a different class of ask than an additional SKU** — a new SKU is additive, while cross-play merges live player populations and forces decisions about matchmaking pools, input-parity fairness between mouse and controller, account linking, and an anti-cheat posture that must hold on the weakest platform in the pool.
5. **Cost input and UI reflow against actual screens and controls, never as a percentage of existing work** — controller focus navigation for every screen, safe-area and aspect-ratio handling for a new form factor, and readability at TV distance are enumerable work items, and enumerating them is what makes the estimate defensible.
6. **Enumerate platform SDK integration per required feature, and flag which ones certification mandates** — achievements, cloud saves, entitlement checks, platform IAP, and presence are separate integrations, and on most platforms a subset is required to pass certification rather than optional.
7. **Include the recurring per-release cost, not only the one-time integration** — every future patch now multiplies across build targets, QA device matrix, store submissions, and on console another certification pass. This bucket is the most commonly omitted and often exceeds the one-time cost within a year of live operation.
8. **Score the expansion with `tco-reversibility-scoring`** — a platform is usually Medium-to-High reversibility since it can be dropped without unwinding gameplay code, but rate it Low whenever step 3 found a forced foundational change, because that change outlives the platform that caused it.
9. **Frame the result for the GD as cost, timeline, and risk in product terms, and leave the decision with them** — committing a platform is a GDD-level product commitment, not a call the CTO settles alone.
10. **Write the assessment in English**, per `language-and-comments.md`'s Working language section — only the closing reply to the GD is Vietnamese.
11. **Ask before estimating when the target hardware baseline, storefront, or launch window is unstated** — certification scope and reflow cost both hinge on them, so mark the affected bucket provisional rather than guessing it.

## 5. Specific goals / tasks this skill performs
- Produce a bucketed cost, timeline, and risk estimate for a proposed platform, rather than a single guessed figure.
- Separate fixed external certification lead time from compressible engineering effort.
- Detect when the expansion forces reopening a prior foundational decision and say so as a distinct kind of risk.
- Distinguish cross-play from an additional SKU, and cost the population-merge consequences of the former.
- Surface the recurring per-release multiplier alongside the one-time integration cost.
- Out of scope: performing the SDK, store, and certification work (`tech-lead-sdk-platform`), per-device quality tuning (`unity-engineer`), the netcode and anti-cheat decisions themselves (`netcode-architecture-decision`, `anti-cheat-strategy`), the scoring rubric (`tco-reversibility-scoring`).

## 6. Output format
```
## Cross-Platform Expansion Assessment — <platform or cross-play>
- Expansion class: additional SKU | additional mobile OS | cross-play (population merge)
- Certification/review: <nominal external lead time> — non-compressible; resubmission risk: <...>
- Input/UI reflow: <enumerated screens, control scheme, safe area, aspect range> — <effort>
- Netcode/anti-cheat impact: none | reopens <netcode-architecture-decision | anti-cheat-strategy>: <why>
- Platform SDK integration: <per feature; mark which certification mandates> — <effort>
- Recurring per-release cost: <extra build targets, QA matrix, submissions, per-patch certification>
- TCO / Reversibility: <score from tco-reversibility-scoring — Low if a foundational change was forced>
- Provisional buckets: none | <bucket>, pending <missing input>
- Rule compliance: assessment written in English, per Working language
- Assessment verdict: viable as estimated | viable only after reopening <prior decision> | not viable within <constraint>
- Decision owner: GD — framed trade-off: <cost and timeline vs. reach>
- Routed to: <role or skill that acts on this next>
```

**Extended report — emit ONLY when the requester asks for it.** It replaces the one-line verdict rationale with all three fields:
```
- Known limitations: <buckets resting on estimates rather than confirmed platform requirements>
- Latent concerns: <what holds only under the current hardware baseline, storefront terms, or launch window>
- Future remediation: <the re-estimate trigger for each — a platform policy change, a certification failure, a scope change>
```

## 7. Examples
**Example 1**
- Input: adding a console SKU to a live PC/mobile PvP game.
- Output: certification lead time is the binding constraint, not engineering effort, and is reported separately with a resubmission window. The committed netcode model already covers the console's constraints, so no foundational reopening. Controller reflow is enumerated per screen; platform achievements and cloud saves are flagged as certification-mandated. The recurring cost — a certification pass on every future patch — is called out as exceeding the one-time integration within the first live year. Routed to the GD as a framed trade-off.

**Example 2**
- Input: "cross-play is basically just turning on a flag in the netcode layer — estimate it as a small task."
- Output: declined as framed. Cross-play merges player populations, which forces decisions this assessment cannot absorb: matchmaking pool structure, mouse-versus-controller input parity, account linking, and an anti-cheat posture that must hold on the weakest platform in the shared pool. Since the current tier is kernel-level and PC-only, `anti-cheat-strategy` must be reopened before any credible estimate exists. Reversibility re-rated Low for that reason.

**Example 3**
- Input: adding Steam Deck support to a PC title that already ships on Steam.
- Output: no certification bucket, since Deck Verified is a review rather than a platform certification, but input and UI reflow are real — controller-only navigation and small-screen readability are enumerated per screen. The binding finding is the anti-cheat bucket: the committed kernel-level tier does not run under Proton, so the verdict is viable only after reopening `anti-cheat-strategy`, and the estimate is withheld pending that.

## 8. Edge cases & guardrails
- Never present one blended number — the GD plans against buckets, and a single figure hides which one is driving the cost.
- Never fold certification lead time into engineering effort, per §4 — conflating a fixed external calendar with compressible work misleads every downstream schedule.
- Never report a forced netcode or anti-cheat reopening as an extra cost line — it is a different class of risk and outlives the platform that triggered it.
- Never estimate cross-play as an additive SKU — it changes the live game rather than adding a build target.
- Never omit the recurring per-release multiplier just because the ask was phrased as a one-time cost.
- If hardware baseline, storefront, or launch window is unstated, mark the affected bucket provisional and ask — do not estimate around a guess.

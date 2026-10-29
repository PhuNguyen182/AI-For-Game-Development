---
name: cross-platform-expansion-assessment
description: "Estimate cost, timeline and risk of adding a platform — console SKU, another mobile OS, Steam Deck, cross-play: certification lead time, porting, per-platform QA, ongoing cost. Use before committing a new platform."
user-invocable: false
---

# Cross-Platform Expansion Assessment

Not for: work on an already-committed platform (`sdk-platform-engineer`), per-device quality tiers inside a shipped platform (`gameplay-engineer`), sync model (`netcode-architecture-decision`), cheat posture (`anti-cheat-strategy`), the scoring rubric (`tco-reversibility-scoring`).

## Steps
1. **Split into four buckets before any number** — certification/review, input and UI reflow, netcode and anti-cheat impact, platform SDK integration. A blended figure hides the driver.
2. **Report certification lead time as a separate, non-compressible line** — it runs on the platform holder's calendar; a failed submission restarts the clock, so state resubmission risk beside the nominal window.
3. **Check whether the platform invalidates a foundational decision first** — if the committed netcode model or anti-cheat tier does not carry over, say plainly it reopens `netcode-architecture-decision` or `anti-cheat-strategy`; do not fold it into a larger number.
4. **Treat cross-play as a different class from an extra SKU** — it merges live populations: matchmaking pools, mouse-vs-controller parity, account linking, and an anti-cheat posture that holds on the weakest platform in the pool.
5. **Cost reflow against actual screens and controls**, never as a percentage — controller focus navigation per screen, safe area and aspect ratio, readability at TV distance.
6. **Enumerate SDK integration per feature** (achievements, cloud saves, entitlement, platform IAP, presence) and flag which the platform mandates for certification.
7. **Include the recurring per-release cost** — every patch multiplies across build targets, QA device matrix, store submissions, and on console a certification pass. Most often omitted; often exceeds the one-time cost within a year of live operation.
8. **Score with `tco-reversibility-scoring`** — usually Medium-to-High reversibility; Low whenever step 3 found a forced foundational change, since that outlives the platform.
9. **Give the GD cost, timeline and risk in product terms and leave the decision to them** — committing a platform is a GDD-level commitment.
10. **Ask when hardware baseline, storefront or launch window is unstated** — mark the affected bucket provisional, do not guess.

## Never
- Present one blended number, or an unflagged forced reopening as an extra cost line.
- Estimate cross-play as an additive SKU, or omit the recurring multiplier because the ask sounded one-time.

## Output
```
## Cross-Platform Expansion Assessment — <platform | cross-play>
- Class: additional SKU | additional mobile OS | cross-play
- Certification/review: <lead time> — non-compressible; resubmission risk: <...>
- Input/UI reflow: <screens, controls, safe area, aspect> — <effort>
- Netcode/anti-cheat impact: none | reopens <decision>: <why>
- SDK integration: <per feature, mandated marked> — <effort>
- Recurring per-release cost: <...>
- TCO / Reversibility: <score>
- Provisional buckets: none | <bucket> pending <input>
- Verdict: viable as estimated | viable only after reopening <decision> | not viable within <constraint>
- Decision owner: GD — trade-off: <cost and timeline vs reach>
- Routed to: <...>
```
On request only, add `Known limitations`, `Latent concerns` and `Future remediation`, each with its re-estimate trigger.

## Example
- "Cross-play is just a netcode flag, estimate it small" → declined: population merge; the current kernel-level, PC-only anti-cheat tier must be reopened first, reversibility rated Low.
- Steam Deck for a Steam PC title → no certification bucket (Deck Verified is a review), reflow enumerated per screen; kernel-level anti-cheat does not run under Proton, so verdict is viable only after reopening `anti-cheat-strategy`; estimate withheld.

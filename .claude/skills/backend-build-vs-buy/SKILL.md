---
name: backend-build-vs-buy
description: "Per-component build-vs-buy for backend: matchmaking, cloud save, server hosting, leaderboards, social — managed (UGS, PlayFab, Nakama, Firebase) vs custom, with exit cost. Use when choosing backend services."
user-invocable: false
---

# Backend Build-vs-Buy

Not for: sync protocol, tick rate, prediction (`netcode-architecture-decision`, `netcode-engineer`), server-side gameplay validation (`server-authoritative-validation`), scoring rubric (`tco-reversibility-scoring`), remote-config cadence (`live-ops-content-pipeline`), event pipelines (`analytics-telemetry-platform`), virtual-currency ledger (`ad-mediation-monetization-platform`; this skill owns profile data and save sync only).

## Steps
1. **Split the need into components before shortlisting** — matchmaking, player data/save sync, dedicated server hosting/orchestration, leaderboards, party/social. They need not share a vendor; a bundled vendor demo must not set the boundaries.
2. **Shortlist per component across all three tiers** — managed (PlayFab, GameLift, Nakama Cloud), self-hosted open source (Nakama), fully custom. Dropping a tier before scoring pre-justifies a choice.
3. **Score each option with `tco-reversibility-scoring`** and read the scaling-cost bucket: managed is cheap at launch and dear at scale; state the crossover as a number, not "later".
4. **Check ops burden against current headcount**, not headcount a funding round would buy. Custom or self-hosted without real backend/ops capacity is disqualified (e.g. no backend engineer -> managed such as Nakama Cloud); an unrun backend costs more than a managed one.
5. **Check region coverage against the audience** — for real-time competitive play a missing region is a latency floor: disqualification, not a cost penalty.
6. **Check persistence lock-in** — if the vendor schema shapes the save format, exit is a live-player migration and reversibility is Low.
7. **Recommend per component; a mixed result is normal** (managed matchmaking + custom hosting). One vendor for tidiness is not a technical argument.
8. **Unestimable load** (usually projected concurrency) → feasibility unknown routed to `rd-engineer` for a benchmark; do not decide around a guess.

## Output
```
## Backend Build-vs-Buy Decision — <project>
| Component | Options considered | TCO / Reversibility | Ops burden fit | Region coverage | Decision |
|---|---|---|---|---|---|
| Matchmaking / Persistence / Server hosting / Leaderboards-social | ... | ... | ... | ... | ... |
- Scaling crossover: <component> flips at ~<scale> — <which way>
- Save-data lock-in: <none / vendor schema shapes save format>
- Feasibility unknowns: <none / listed>
- Routed to: `rd-engineer` for unknowns; `netcode-engineer` for validation once chosen
```
On request only, add `Known limitations`, `Latent concerns`, `Future remediation` (each with its re-decision trigger).

## Example
- "One vendor for a single bill" → declined as a default: hosting was the only component where managed lost on cost curve and the most reversible, so splitting costs one integration and removes the largest lock-in.

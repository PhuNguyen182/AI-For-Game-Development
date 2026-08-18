---
name: backend-build-vs-buy
description: >
  Build-vs-buy framework for backend infrastructure — matchmaking, player
  data persistence/save sync, dedicated server hosting/orchestration,
  leaderboards/social — broken down per component rather than one monolithic
  vendor decision (PlayFab, Nakama, GameLift, or fully custom). Use this
  whenever the CTO is asked to choose a managed backend platform vs.
  self-hosted/custom infrastructure. Do not use this for the client-server
  sync protocol itself (message format, tick rate, prediction/reconciliation)
  — that's netcode-architecture-decision/netcode-engineer's territory. Do not
  use this for implementing server-side gameplay validation once the backend
  is chosen — that's server-authoritative-engineer's job.
---

# Backend Build-vs-Buy

## 1. Objective
Give the CTO a consistent framework for the build-vs-buy backend infrastructure decision — matchmaking, persistence, dedicated server hosting — independent of the netcode/gameplay-sync decision, so it isn't bundled into a single all-or-nothing vendor call by default.

## 2. Role
Act as a backend-infrastructure-minded CTO who has run both self-hosted and managed multiplayer backend stacks at scale.

## 3. When to invoke this skill
- Deciding whether to license a managed backend (PlayFab, GameLift, Nakama, etc.) vs. build/host custom infrastructure for matchmaking, player data persistence, or dedicated server orchestration.
- Negative trigger: don't use this for the client-server sync protocol itself — that's `netcode-architecture-decision`/`netcode-engineer`.
- Negative trigger: don't use this for implementing server-side validation logic once the backend is chosen — that's `server-authoritative-engineer`.

## 4. How to use this skill
1. Break the backend need into its actual components — they don't have to share one vendor: matchmaking, player data persistence/save sync, dedicated server hosting/orchestration, leaderboards, party/social.
2. For each component, shortlist realistic options: fully managed (PlayFab, GameLift, Nakama Cloud), self-hosted open-source (Nakama self-hosted), or fully custom.
3. Score each shortlisted option per component with `tco-reversibility-scoring`, paying particular attention to the scaling cost curve bucket — managed backends often look expensive at scale but cheap at launch, and the crossover point matters more than the sticker price.
4. Check operational burden realistically: a fully custom backend needs a real ops/backend engineering investment this team may or may not have — factor actual team capacity, not aspirational headcount.
5. Check regional/latency requirements: does the option support server regions matching the game's target audience geography (especially relevant for real-time competitive play)?
6. Recommend per component — it's fine, and often correct, for different components to use different vendors/approaches (e.g. managed matchmaking + custom dedicated server hosting).
7. If a component's requirement is one the team has no working basis to estimate (e.g. "can this handle our projected concurrent player count"), flag it as a feasibility unknown for `rd-engineer` rather than deciding on an unverified assumption.

## 5. Specific goals / tasks this skill performs
- Produce a build-vs-buy verdict per backend component (matchmaking, persistence, hosting, leaderboards/social), not one monolithic all-or-nothing call.
- Surface the scaling cost curve crossover point explicitly, not just launch-day cost.
- Out of scope: the sync protocol itself, and server-side gameplay validation implementation.

## 6. Output format
```
## Backend Build-vs-Buy Decision
| Component | Options considered | TCO/Reversibility | Ops burden fit | Decision |
|---|---|---|---|---|
| Matchmaking | ... | ... | ... | ... |
| Persistence | ... | ... | ... | ... |
| Dedicated server hosting | ... | ... | ... | ... |
| Leaderboards/social | ... | ... | ... | ... |

Feasibility unknowns remaining (route to R&D Engineer if any): ...
```

## 7. Examples
**Example 1**
- Input: a mid-size studio shipping a mid-core PvP game.
- Output: managed matchmaking + persistence (PlayFab) for launch simplicity, custom lightweight dedicated server hosting on a cloud provider recommended once scale projections justify the cost-curve crossover.

**Example 2**
- Input: a small team shipping a hardcore niche title with no dedicated backend engineer.
- Output: fully managed Nakama Cloud across all components, given the team has no ops capacity to run self-hosted infrastructure reliably.

## 8. Edge cases & guardrails
- Never recommend "build everything custom" purely on cost-per-unit grounds without weighing the team's actual ops capacity to run it reliably.
- Don't force one vendor across all components if a mixed approach genuinely scores better — component-level decisions are allowed and often correct.
- If projected scale is a guess, don't build the decision around it silently — flag it and, if it's load-bearing for the choice, route to `rd-engineer` for a benchmark first.

---
name: backend-build-vs-buy
description: >
  Per-component build-vs-buy framework for backend infrastructure —
  matchmaking, player data persistence and save sync, dedicated server
  hosting/orchestration, leaderboards and party/social — shortlisting managed
  (PlayFab, GameLift, Nakama Cloud), self-hosted open-source (Nakama), and
  fully custom per component instead of one monolithic vendor call, decided
  on the scaling-cost crossover point, real ops capacity, and server-region
  coverage. Use when choosing a managed backend versus self-hosted or custom
  infrastructure. Not for: the sync protocol itself — message format, tick
  rate, prediction/reconciliation (`netcode-architecture-decision`,
  `netcode-engineer`), server-side gameplay validation
  (`server-authoritative-engineer`), the scoring rubric
  (`tco-reversibility-scoring`), remote-config content cadence
  (`live-ops-content-pipeline`), event pipelines
  (`analytics-telemetry-platform`).
---

# Backend Build-vs-Buy — per-component infrastructure decision

## 1. Objective
Give the CTO a consistent framework for the backend infrastructure build-vs-buy call — matchmaking, persistence, hosting, social — kept independent of the netcode/gameplay-sync decision so it is not bundled into a single all-or-nothing vendor commitment by default.

## 2. Role
Act as a backend-infrastructure CTO who has run both self-hosted and managed multiplayer stacks at scale, and who has paid the operational bill for each.

## 3. When to invoke this skill
- Choosing between a managed backend platform and self-hosted or custom infrastructure for any backend component.
- A vendor's bundled offering is being treated as one decision, and the components inside it have not been separated yet.
- Negative trigger: the question is the client-server sync protocol — message format, tick rate, prediction/reconciliation — which belongs to `netcode-architecture-decision` for the foundation choice and `netcode-engineer` for the protocol itself.
- Negative trigger: the backend is already chosen and the work is implementing server-side gameplay validation — that is `server-authoritative-engineer`.
- Negative trigger: the question is content cadence (remote config, live events) or the analytics event pipeline — separate infra decisions with their own skills.

## 4. How to use this skill
1. **Split the need into its actual components before shortlisting anything** — matchmaking, player data persistence/save sync, dedicated server hosting/orchestration, leaderboards, party/social. They do not have to share one vendor, and treating them as one decision is what produces avoidable lock-in.
2. **Shortlist realistic options per component across all three tiers** — fully managed (PlayFab, GameLift, Nakama Cloud), self-hosted open-source (Nakama), fully custom. Dropping a tier before scoring it turns the framework into a justification for a choice already made.
3. **Score each shortlisted option with `tco-reversibility-scoring`, per component** — and read the scaling-cost curve bucket closely. Managed backends usually look cheap at launch and expensive at scale; the crossover point decides this, not the sticker price.
4. **Check ops burden against the team that actually exists** — a custom backend needs real backend/ops engineering capacity to run reliably. Score against current headcount, not headcount a funding round would buy.
5. **Check server-region coverage against the target audience's geography** — for real-time competitive play a missing region is a latency floor no amount of client-side work can lift, which disqualifies the option outright rather than costing it points.
6. **Check what persistence lock-in does to save data** — if the vendor's schema shapes the save format, exit cost is a live-player data migration, and reversibility drops to Low regardless of how clean the API looks.
7. **Recommend per component, allowing a mixed result** — managed matchmaking alongside custom dedicated server hosting is a normal, often correct outcome. Forcing one vendor across every component to look tidy is not a technical argument.
8. **Write the decision in English**, per `language-and-comments.md`'s Working language section — it is a durable artifact other roles act on; the Vietnamese reply to the GD is the final message, not the document.
9. **Flag any component whose requirement the team has no working basis to estimate as a feasibility unknown for `rd-engineer`** — projected concurrent player count is the usual one. Deciding on an unverified load assumption puts the whole component's score on a guess.

## 5. Specific goals / tasks this skill performs
- Produce a build-vs-buy verdict per backend component, never one monolithic all-or-nothing call.
- Surface each component's scaling-cost crossover point explicitly, not just launch-day cost.
- Test every option against the team's real ops capacity and the target regions.
- Route load-bearing feasibility unknowns to `rd-engineer` instead of absorbing them into the decision.
- Out of scope: the sync protocol (`netcode-architecture-decision`, `netcode-engineer`), server-side validation implementation (`server-authoritative-engineer`), live-ops content infra (`live-ops-content-pipeline`).

## 6. Output format
```
## Backend Build-vs-Buy Decision — <project>
| Component | Options considered | TCO / Reversibility | Ops burden fit | Region coverage | Decision |
|---|---|---|---|---|---|
| Matchmaking | ... | ... | ... | ... | ... |
| Persistence / save sync | ... | ... | ... | ... | ... |
| Dedicated server hosting | ... | ... | ... | ... | ... |
| Leaderboards / social | ... | ... | ... | ... | ... |

- Scaling crossover: <component> flips at roughly <scale> — <which way>
- Save-data lock-in: <none / vendor schema shapes the save format>
- Rule compliance: decision written in English, per Working language
- Feasibility unknowns: <none / listed>
- Routed to: `rd-engineer` for the unknowns above; `server-authoritative-engineer` for validation once chosen
```

**Extended report — emit ONLY when the requester asks for it.** It replaces the one-line unknowns field with all three:
```
- Known limitations: <components the decision leaves open, and why>
- Latent concerns: <assumptions holding only at launch scale or current team size>
- Future remediation: <the re-decision trigger for each — the scale, headcount, or region change that forces a revisit>
```

## 7. Examples
**Example 1**
- Input: a mid-size studio shipping a mid-core PvP title, one backend engineer.
- Output: managed matchmaking and persistence on PlayFab for launch; custom lightweight dedicated server hosting recommended only once projected concurrency passes the cost-curve crossover, with that crossover stated as a number rather than "later".

**Example 2**
- Input: "put everything on one vendor so there's a single bill and a single integration."
- Output: declined as a default. Scored per component, dedicated server hosting was the only component where the managed option lost on cost curve, and it is also the component with the highest reversibility — so splitting it costs one extra integration and removes the largest lock-in. A single bill is an accounting preference, not a scoring input.

**Example 3**
- Input: a small team, hardcore niche PC title, no dedicated backend engineer, no load projection.
- Output: fully managed Nakama Cloud across every component on ops capacity alone — self-hosting is disqualified before cost is considered. Concurrency projection flagged as a feasibility unknown and routed to `rd-engineer`, since the persistence tier choice depends on it.

## 8. Edge cases & guardrails
- Never recommend "build everything custom" on cost-per-unit grounds without weighing whether this team can actually operate it — an unrun backend costs more than a managed one.
- Never force one vendor across all components when a mixed result scores better; component-level decisions are the point of this skill.
- Never treat a missing target region as a cost penalty on a real-time competitive title — it is a disqualification.
- Never let a bundled vendor demo set the component boundaries — split the need first, per §4, then see which bundle happens to fit.
- If projected scale is a guess and the choice turns on it, route to `rd-engineer` for a benchmark rather than deciding around the guess.

---
name: netcode-architecture-decision
description: >
  Build-vs-license framework for the multiplayer netcode foundation — Mirror,
  FishNet, Photon Fusion, Photon Quantum, Unity Netcode for GameObjects, or
  custom on Unity Transport/LiteNetLib — and for the synchronization model
  itself: client-server authoritative prediction/reconciliation, deterministic
  lockstep, or GGPO-style rollback. Keyed to genre latency and determinism
  needs, CCU-based pricing, and committed platform reach. Use when asked
  whether to build custom netcode or license a framework, or to fix the sync
  model before protocol work starts.
  Not for: reconciliation protocol, message format, tick rate (`netcode-engineer`), server hosting (`backend-build-vs-buy`), cheat posture (`anti-cheat-strategy`), the scoring rubric (`tco-reversibility-scoring`), feasibility spikes (`rd-engineer`).
---

# Netcode Architecture Decision — foundation and synchronization model

## 1. Objective
Settle the single most expensive-to-reverse client-track choice — which netcode foundation the game is built on, and which synchronization model it runs — so the call rests on the genre's actual latency/determinism requirement and a scored cost comparison, rather than on framework familiarity, a benchmark screenshot, or a determinism claim nobody checked against the gameplay code.

## 2. Role
Act as a multiplayer architecture specialist who has shipped both licensed and fully custom netcode stacks on PC and mobile, and who has paid the migration cost of getting this choice wrong once.

## 3. When to invoke this skill
- Asked, by the GD or via a Technical Architect escalation, whether to build custom netcode or license a framework.
- The synchronization model itself is still open and must be fixed before `netcode-engineer` designs a protocol against it.
- A licensed framework's pricing, platform coverage, or determinism guarantee needs checking before the project commits gameplay code to it.
- Negative trigger: reconciliation protocol, message format, snapshot rate, or tick rate for an already-chosen foundation — that is `netcode-engineer`'s implementation work.
- Negative trigger: where the authoritative server actually runs and who operates it — that is `backend-build-vs-buy`.
- Negative trigger: how hard cheating is to pull off on the chosen model — that is `anti-cheat-strategy`, layered above this decision.
- Negative trigger: the cost/reversibility arithmetic itself — that rubric is `tco-reversibility-scoring`, which this skill calls.
- Negative trigger: an unknown that needs measuring rather than deciding — that is `rd-engineer`'s prototype spike.

## 4. How to use this skill
1. **Classify the genre's latency and determinism requirement before naming a single framework** — it eliminates most of the shortlist for free. Fighting/1v1 twitch competitive needs rollback or deterministic lockstep; FPS/MOBA/action PvP needs client-server authoritative with prediction and reconciliation; co-op, turn-based, and async need plain server-authoritative RPC.
2. **Refuse to buy prediction a genre will not perceive** — reconciliation adds a whole class of desync bugs and a permanent debugging tax. On a turn-based or async game nobody can perceive the difference, so that tax buys nothing (YAGNI).
3. **Shortlist by the sync model, never by popularity** — Mirror and FishNet are self-hosted client-server authoritative; Photon Fusion is hosted with prediction built in; Photon Quantum is hosted deterministic lockstep with rollback; Unity Netcode for GameObjects is client-server over Unity Transport; custom means owning the stack above a bare transport.
4. **Test every determinism claim against the gameplay simulation, not the transport** — lockstep and rollback require a bit-deterministic simulation, which floating-point math and Unity's physics engine do not provide across platforms. The client track already owes this under `coding-principles.md`'s Shared Core integrity section; a deterministic framework does not grant it, it presupposes it.
5. **Treat a committed platform the framework does not cover as a disqualifier, not a cost line** — check console, mobile, and cross-play against the GDD's commitments before comparing price. Cheaper on an unsupported platform is not cheaper.
6. **Price the ongoing bucket on concurrent users and bandwidth, not on a seat count** — hosted netcode bills per CCU or per message, so cost tracks success. Fetch the vendor's rate card with `WebFetch` and score with `tco-reversibility-scoring`, which weights reversibility above upfront cost here because a netcode foundation is almost always Low reversibility once gameplay is built on it.
7. **Assess team fit against the timeline honestly** — custom netcode wins only with genuine in-house networking expertise and schedule slack for the reconciliation and debugging work. Without both, licensing is the responsible call even when its sticker price is higher.
8. **Route a feasibility unknown to a measured spike instead of deciding around it** — if the open question is "will our tick rate hold on real mobile networks", that is `rd-engineer`'s prototype, and the decision stays withheld until it reports.
9. **Record the chosen foundation as a durable standard** via `engineering-standard-adr-authoring` — an unrecorded netcode decision gets quietly contradicted by the first feature that finds it inconvenient.
10. **Write the decision and its reasoning in English**, per `language-and-comments.md`'s Working language section — the Technical Decision is a durable artifact; only the closing reply to the GD is Vietnamese.
11. **Ask before deciding when target CCU, cross-play commitment, or session model is unstated** — each one alone can flip the shortlist, so a decision made around a guessed value is precise and wrong.

## 5. Specific goals / tasks this skill performs
- Produce a build-vs-license verdict for the netcode foundation, tied to a named genre latency/determinism class rather than preference.
- Fix the synchronization model explicitly, so `netcode-engineer` designs a protocol against a settled decision.
- Disqualify options that miss a committed platform before cost is ever compared.
- Verify determinism claims against the simulation instead of accepting them from the framework's marketing.
- Separate a feasibility unknown from a choice, and route the unknown to a spike.
- Out of scope: protocol, message format, and tick-rate design (`netcode-engineer`), server hosting and operations (`backend-build-vs-buy`), cheat-resistance posture (`anti-cheat-strategy`), the scoring rubric itself (`tco-reversibility-scoring`), prototypes (`rd-engineer`).

## 6. Output format
```
## Netcode Foundation Decision — <game or mode>
- Genre class: fighting/1v1-twitch | FPS-MOBA-action-PvP | co-op-turn-based-async
- Sync model required: rollback | deterministic lockstep | client-server authoritative with prediction | plain authoritative RPC
- Determinism feasible: yes/no — <what was checked: fixed-point vs. float, physics source, platform spread>
- Shortlist: <only options matching the sync model>
- Platform reach: <pass/fail per committed platform, per option — a fail is a disqualifier>
- Ongoing cost basis: <CCU/bandwidth rate card URL> | provisional, pending confirmed pricing
- Team fit: <networking expertise on hand vs. what custom demands, and the timeline>
- TCO / Reversibility: <score from tco-reversibility-scoring>
- Feasibility unknowns: none | <spike scope, decision withheld>
- Rule compliance: decision written in English, per Working language
- Decision: <foundation + sync model> — <one line tying the score to the choice>
- Routed to: <role or skill that acts on this next>
```

**Extended report — emit ONLY when the requester asks for it.** It replaces the one-line `Decision` rationale with all three fields:
```
- Known limitations: <what this decision does not settle — protocol details, hosting, cheat posture>
- Latent concerns: <assumptions true only at current scale: CCU tier, platform list, team composition>
- Future remediation: <the re-open trigger for each — the CCU threshold, price change, or platform commitment that invalidates it>
```

## 7. Examples
**Example 1**
- Input: a hardcore PvP action game choosing between Mirror and custom netcode; two gameplay programmers, neither a networking specialist; PC and mobile committed, no console.
- Output: genre class FPS-MOBA-action-PvP, so the sync model is client-server authoritative with prediction. Both options cover the committed platforms. `tco-reversibility-scoring` returns Mirror at Low upfront / Medium reversibility versus custom at High upfront / Low reversibility, and team fit fails for custom on expertise. Decision: license Mirror. Recorded via `engineering-standard-adr-authoring`; routed to `netcode-engineer` for protocol design.

**Example 2**
- Input: "Photon Quantum does rollback for us, so we get deterministic netcode for free."
- Output: declined. Determinism is a property of the simulation, not of the transport — Quantum requires the whole gameplay simulation to run on its fixed-point deterministic engine. This project's outcomes lean on Unity's physics, which is not deterministic across platforms, so adopting Quantum means reimplementing that physics inside its simulation, not wiring up a library. Re-scored with that migration as upfront cost, Quantum stops being the cheap option; the shortlist was reopened against the actual sync requirement.

**Example 3**
- Input: a new fighting-game mode needs rollback, and no licensed option fits the project's engine version cleanly.
- Output: genre class fighting/1v1-twitch, sync model rollback confirmed. Determinism check fails against the current float-based simulation, so the real open question is feasibility, not choice. Decision withheld; a scoped `rd-engineer` spike is requested to validate a fixed-point simulation and measured rollback window before any commitment to a custom GGPO-style implementation.

## 8. Edge cases & guardrails
- Never recommend custom netcode on ambition — back it with team fit, timeline, and a scored comparison, or license.
- Never accept a framework's determinism guarantee without checking the simulation it would have to run, per §4 — this is the single most common way this decision goes wrong expensively.
- Never compare price before platform reach — an option that misses a committed platform is out regardless of what it costs.
- Never quote launch-day cost for a CCU-priced framework without the crossover point — the number that matters is where it overtakes the alternative.
- Never let this decision stay only in conversation — record it as a standard, or the next feature silently contradicts it.
- If target CCU, cross-play commitment, or session model is unstated, ask — do not decide around an assumed value.

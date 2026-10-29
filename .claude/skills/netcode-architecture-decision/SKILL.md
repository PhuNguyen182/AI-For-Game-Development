---
name: netcode-architecture-decision
description: "Choose the multiplayer foundation (Mirror, FishNet, Photon Fusion/Quantum, NGO, custom on Transport/LiteNetLib) and sync model (state sync, lockstep, rollback). Use before any netcode is written."
user-invocable: false
---

# Netcode Architecture Decision

Not for: reconciliation protocol, message format, tick rate (`netcode-engineer`), server hosting (`backend-build-vs-buy`), cheat posture (`anti-cheat-strategy`), the scoring rubric (`tco-reversibility-scoring`), feasibility spikes (`rd-engineer`).

## Steps
1. **Classify the genre's latency and determinism need before naming a framework** — fighting/1v1 twitch: rollback or deterministic lockstep. FPS/MOBA/action PvP: client-server authoritative with prediction and reconciliation. Co-op, turn-based, async: plain server-authoritative RPC.
2. **Do not buy prediction the genre cannot perceive** — reconciliation adds desync bugs and a permanent debugging tax.
3. **Shortlist by sync model, not popularity** — Mirror, FishNet: self-hosted client-server authoritative. Photon Fusion: hosted, prediction built in. Photon Quantum: hosted deterministic lockstep with rollback. NGO: client-server over Unity Transport. Custom: you own the stack above a bare transport.
4. **Test every determinism claim against the gameplay simulation, not the transport** — lockstep/rollback need a bit-deterministic simulation; floats and Unity physics are not deterministic across platforms. A deterministic framework presupposes it (`csharp-standards` → `coding-principles.md` Shared Core integrity).
5. **A committed platform the framework misses disqualifies it before price** — check console, mobile and cross-play against the GDD.
6. **Price the ongoing bucket on CCU and bandwidth** — hosted netcode bills per CCU or message. Fetch the vendor rate card with `WebFetch`; state the crossover point where it overtakes the alternative, not launch-day cost. Score with `tco-reversibility-scoring`, which weights reversibility above upfront cost here (foundation is usually Low reversibility once gameplay is built on it).
7. **Judge team fit against the timeline** — custom wins only with in-house networking expertise and schedule slack; otherwise license, even at a higher sticker price.
8. **Feasibility unknown (e.g. tick rate on real mobile networks) → `rd-engineer` spike**; withhold the decision until it reports.
9. **Record the foundation via `engineering-standard-adr-authoring`** — an unrecorded decision is contradicted by the first inconvenient feature.
10. **Target CCU, cross-play commitment or session model unstated → `Needs-decision` naming it** — each can flip the shortlist; any call made meanwhile is provisional.

## Never
- Recommend custom netcode on ambition — back it with team fit, timeline and a scored comparison.
- Accept a framework's determinism guarantee unchecked — the most common expensive failure here.

## Output
```
## Netcode Foundation Decision — <game or mode>
- Genre class: fighting/1v1-twitch | FPS-MOBA-action-PvP | co-op-turn-based-async
- Sync model: rollback | deterministic lockstep | client-server authoritative with prediction | plain authoritative RPC
- Determinism feasible: yes/no — <fixed-point vs float, physics source, platform spread>
- Shortlist: <options matching the sync model>
- Platform reach: <pass/fail per platform per option>
- Ongoing cost: <rate card URL, crossover> | provisional
- Team fit: <expertise vs demand, timeline>
- TCO / Reversibility: <score>
- Feasibility unknowns: none | <spike scope, decision withheld>
- Decision: <foundation + sync model> — <score tie>
- Routed to: <...>
```
On request only, add `Known limitations`, `Latent concerns` and `Future remediation`, each with its re-open trigger.

## Example
- "Photon Quantum does rollback, so determinism is free" → declined: Quantum requires the whole simulation on its fixed-point engine; this project leans on Unity physics, so adoption means reimplementing it. Re-scored with that migration as upfront cost; shortlist reopened.

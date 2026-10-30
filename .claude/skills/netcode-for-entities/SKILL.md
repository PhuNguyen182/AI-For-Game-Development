---
name: netcode-for-entities
description: "Netcode for Entities (DOTS): ghosts, GhostField, IRpcCommand, ICommandData/IInputComponentData, Simulate tag prediction, ClientServerBootstrap, relevancy, thin clients, host migration. Use on an NfE project."
user-invocable: false
---

# Netcode for Entities

Not for: choosing NfE or the sync model (`netcode-architecture-decision`), the GameObject stack (`netcode-for-gameobjects`), general ECS modeling (`unity-ecs-architecture`), jobs and Burst (`unity-job-system-and-burst`, `unity-burst-compiler`), non-predicted physics (`unity-physics`), ghost rendering (`unity-entities-graphics`), input actions and bindings behind a command (`unity-input-system`), the UTP driver and Relay allocation (`unity-transport`), UGS dashboard/account setup (`sdk-platform-engineer`).
Docs: https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/index.html (API: same path, `api/`) — pinned 6.6; older 0.x/1.x lines differ, so read `Packages/manifest.json` and swap the segment. Package `com.unity.netcode`, not `.gameobjects`. Needs ECS, Editor 2022.3.0f1+ or Unity 6 LTS.

| Reference | Read when |
|---|---|
| [setup-and-worlds.md](references/setup-and-worlds.md) | Standing up client/server Worlds, picking build topology, defines or tick-rate settings |
| [transport-and-connection.md](references/transport-and-connection.md) | Wiring a driver or Relay, a connection never reaches gameplay, `BadProtocolVersion`, connection approval |
| [ghost-authoring.md](references/ghost-authoring.md) | Declaring a ghost prefab, choosing what replicates, replicating a type you cannot edit |
| [ghost-spawning-and-groups.md](references/ghost-spawning-and-groups.md) | Predicted spawn, subscene pre-spawn, or atomic replication of several ghosts |
| [ghost-serialization-templates.md](references/ghost-serialization-templates.md) | A field type has no native replication and no `GhostFieldSubType` fits |
| [rpcs-and-commands.md](references/rpcs-and-commands.md) | Choosing or writing an RPC or per-tick input |
| [prediction-core.md](references/prediction-core.md) | Writing a predicted-ghost system, tick timing, tick-rate tuning, remote-ghost smoothness |
| [prediction-caveats.md](references/prediction-caveats.md) | A correction is visible, a prediction-mode switch looks wrong, or lag compensation is needed |
| [physics-integration.md](references/physics-integration.md) | A predicted ghost needs physics, or client-only VFX physics |
| [host-migration.md](references/host-migration.md) | A client-hosted session must survive the host leaving |
| [optimization-and-bandwidth.md](references/optimization-and-bandwidth.md) | Snapshot bandwidth, serialization CPU or resimulation cost must come down |
| [testing-and-debugging.md](references/testing-and-debugging.md) | Verifying a claim, load-testing with thin clients, logging, regenerating code |

## Steps
1. **Confirm NfE and ECS are the approved foundation** (`netcode-architecture-decision`, `unity-ecs-architecture`); this skill implements that decision.
2. **Stand up Worlds through `ClientServerBootstrap` first**, per [setup-and-worlds.md](references/setup-and-worlds.md). Topology (dedicated server, client-hosted, both) comes from the GDD and fixes which code compiles.
3. **Add `NetworkStreamInGame` by hand once a connection is approved**, per [transport-and-connection.md](references/transport-and-connection.md); without it a connection gets no snapshots and shows no error. Relay needs its own driver wiring.
4. **Model networked state as ghosts, not ad hoc RPCs**, per [ghost-authoring.md](references/ghost-authoring.md). Owner predicts, everyone else interpolates (`OwnerPredicted`). Open the spawning, groups and templates references only when plain `[GhostField]` cannot express the case.
5. **RPC for a reliable one-off event, command stream for continuous per-tick input**, per [rpcs-and-commands.md](references/rpcs-and-commands.md). Only a `GhostInputSystemGroup` system may read `UnityEngine.Input`; a predicted tick replays many times per frame and live input differs each replay.
6. **Keep game rules in a Core assembly, called from the networked `ISystem`**, per `csharp-standards` → `coding-principles.md` Shared Core integrity; a rule reimplemented in `OnUpdate` is a second, divergent copy of server authority.
7. **Query predicted ghosts with the `Simulate` tag**, never a raw tick comparison, per [prediction-core.md](references/prediction-core.md); `ShouldPredict()` is legacy.
8. **Budget prediction corrections, do not try to eliminate them**, per [prediction-caveats.md](references/prediction-caveats.md). NfE does not guarantee determinism even with quantized values, so client/server agreement comes from the project's own Core determinism discipline.
9. **Route predicted physics through `PredictedFixedStepSimulationSystemGroup`**, per [physics-integration.md](references/physics-integration.md); a second world is only for client-only VFX.
10. **Measure before tuning**, per [optimization-and-bandwidth.md](references/optimization-and-bandwidth.md): Network Profiler Snapshot Overview first (`csharp-standards` → `performance-and-algorithms.md` Verification). Do not blame the transport first.
11. **Add host migration only for a client-hosted topology that must survive the host leaving**, per [host-migration.md](references/host-migration.md). It is experimental with hard limits; state that in the handoff per `csharp-standards` → `coding-principles.md` Handoff.
12. **Verify latency, bandwidth and prediction claims with network emulation on**, per [testing-and-debugging.md](references/testing-and-debugging.md); an Editor session with emulation off has zero RTT, jitter and loss and proves nothing.
13. **Tick rate, build topology or predicted-vs-interpolated unspecified → ask**; gameplay code comes to depend on the guess.

## Never
- Remove and re-add a replicated component on a predicted ghost without checking `RollbackPredictionOnStructuralChanges`; the component can reset to zero instead of the server value.
- Increment a replicated value locally without matching the server's quantization; NfE does not quantize between resimulated ticks, so the values drift.

## Output
```
## Netcode for Entities — <feature>
- Foundation approved by: <netcode-architecture-decision ref, or "pre-existing standard">
- Topology: <dedicated / client-hosted / both>; Netcode Client Target and defines confirmed
- Worlds/transport: <Worlds, drivers, Relay or not>
- Ghosts: <prefabs, SupportedGhostMode/DefaultGhostMode, key GhostField choices>
- RPC/Command: <choice and why>
- Core boundary: <rule logic kept in Core>
- Prediction: <Simulate query pattern, physics group, edge cases addressed>
- Tuning: <importance/relevancy/MaxSendRate/preserialization, or "default, not tuned">
- Host migration: <enabled with limits flagged / n/a>
- Verified via: <emulation settings and Profiler tabs read, or "not run">
- Known limitations: <...>
```
On request only, add `Latent concerns` and `Future remediation`, each with its trigger.

## Example
- "Poll `Input.GetKeyDown` in the predicted movement system, simpler than `IInputComponentData`" → declined: a tick can resimulate 20+ times per frame and the press would read true on an arbitrary replay; wired the jump as `InputEvent` in `IInputComponentData` gathered in `GhostInputSystemGroup`.

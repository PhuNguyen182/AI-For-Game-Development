---
name: netcode-for-entities
description: "Netcode for Entities: ghosts, GhostField, IRpcCommand, ICommandData, ClientServerBootstrap. Use on an NfE project."
user-invocable: false
---

# Netcode for Entities

- **Not for:** choosing NfE or the sync model (`netcode-architecture-decision`).
- **Not for:** the GameObject stack (`netcode-for-gameobjects`).
- **Not for:** general ECS modeling (`unity-ecs-architecture`).
- **Not for:** jobs and Burst (`unity-job-system-and-burst`, `unity-burst-compiler`).
- **Not for:** non-predicted physics (`unity-physics`).
- **Not for:** ghost rendering (`unity-entities-graphics`).
- **Not for:** input actions and bindings behind a command (`unity-input-system`).
- **Not for:** the UTP driver and Relay allocation (`unity-transport`).
- **Not for:** UGS dashboard/account setup (`sdk-platform-engineer`).
- **Docs:** https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/index.html (API: same path, `api/`) — pinned 6.6.
  - **Other lines:** older 0.x/1.x lines differ, so read `Packages/manifest.json` and swap the segment.
  - **Package:** `com.unity.netcode`, not `.gameobjects`.
  - **Requires:** ECS (DOTS), Editor 2022.3.0f1+ or Unity 6 LTS.

## References
- **[setup-and-worlds.md](references/setup-and-worlds.md):** Standing up client/server Worlds, picking build topology, defines or tick-rate settings.
- **[transport-and-connection.md](references/transport-and-connection.md):** Wiring a driver or Relay, a connection never reaches gameplay, `BadProtocolVersion`, connection approval.
- **[ghost-authoring.md](references/ghost-authoring.md):** Declaring a ghost prefab, choosing what replicates, replicating a type you cannot edit.
- **[ghost-spawning-and-groups.md](references/ghost-spawning-and-groups.md):** Predicted spawn, subscene pre-spawn, or atomic replication of several ghosts.
- **[ghost-serialization-templates.md](references/ghost-serialization-templates.md):** A field type has no native replication and no `GhostFieldSubType` fits.
- **[rpcs-and-commands.md](references/rpcs-and-commands.md):** Choosing or writing an RPC or per-tick input.
- **[prediction-core.md](references/prediction-core.md):** Writing a predicted-ghost system, tick timing, tick-rate tuning, remote-ghost smoothness.
- **[prediction-caveats.md](references/prediction-caveats.md):** A correction is visible, a prediction-mode switch looks wrong, or lag compensation is needed.
- **[physics-integration.md](references/physics-integration.md):** A predicted ghost needs physics, or client-only VFX physics.
- **[host-migration.md](references/host-migration.md):** A client-hosted session must survive the host leaving.
- **[optimization-and-bandwidth.md](references/optimization-and-bandwidth.md):** Snapshot bandwidth, serialization CPU or resimulation cost must come down.
- **[testing-and-debugging.md](references/testing-and-debugging.md):** Verifying a claim, load-testing with thin clients, logging, regenerating code.

## Steps
1. **Confirm NfE and ECS are the approved foundation:** per `netcode-architecture-decision` and `unity-ecs-architecture`; this skill implements that decision.
2. **Stand up Worlds through `ClientServerBootstrap` first:** per [setup-and-worlds.md](references/setup-and-worlds.md).
   - **Topology:** dedicated server, client-hosted, or both, comes from the GDD and fixes which code compiles.
3. **Add `NetworkStreamInGame` by hand once a connection is approved:** per [transport-and-connection.md](references/transport-and-connection.md).
   - **Without it:** a connection gets no snapshots and shows no error.
   - **Relay:** needs its own driver wiring.
4. **Model networked state as ghosts, not ad hoc RPCs:** per [ghost-authoring.md](references/ghost-authoring.md).
   - **Prediction:** the owner predicts, everyone else interpolates (`OwnerPredicted`).
   - **Other references:** open the spawning, groups and templates references only when plain `[GhostField]` cannot express the case.
5. **RPC for a reliable one-off event, command stream for continuous per-tick input:** per [rpcs-and-commands.md](references/rpcs-and-commands.md).
   - **Input:** only a `GhostInputSystemGroup` system may read `UnityEngine.Input`.
   - **Why:** a predicted tick replays many times per frame and live input differs each replay.
6. **Keep game rules in a Core assembly, called from the networked `ISystem`:** per `csharp-standards` → `coding-principles.md` Shared Core integrity.
   - **Why:** a rule reimplemented in `OnUpdate` is a second, divergent copy of server authority.
7. **Query predicted ghosts with the `Simulate` tag, never a raw tick comparison:** per [prediction-core.md](references/prediction-core.md).
   - **Legacy:** `ShouldPredict()`.
8. **Budget prediction corrections, do not try to eliminate them:** per [prediction-caveats.md](references/prediction-caveats.md).
   - **Determinism:** NfE does not guarantee determinism even with quantized values.
   - **Agreement:** client/server agreement comes from the project's own Core determinism discipline.
9. **Route predicted physics through `PredictedFixedStepSimulationSystemGroup`:** per [physics-integration.md](references/physics-integration.md).
   - **Second world:** only for client-only VFX.
10. **Measure before tuning:** per [optimization-and-bandwidth.md](references/optimization-and-bandwidth.md).
    - **First:** Network Profiler Snapshot Overview (`csharp-standards` → `performance-and-algorithms.md` Verification).
    - **Transport:** do not blame it first.
11. **Add host migration only for a client-hosted topology that must survive the host leaving:** per [host-migration.md](references/host-migration.md).
    - **Status:** experimental with hard limits.
    - **Handoff:** state that status per `csharp-standards` → `coding-principles.md` Handoff.
12. **Verify latency, bandwidth and prediction claims with network emulation on:** per [testing-and-debugging.md](references/testing-and-debugging.md).
    - **Why:** an Editor session with emulation off has zero RTT, jitter and loss and proves nothing.
    - **Report:** the emulation settings and the Profiler tabs read, in `Verified`.
13. **Missing input:** tick rate, build topology or predicted-vs-interpolated unspecified → dispatched agent `Blocked` or `Needs-decision`; main session `AskUserQuestion`.
    - **Why:** gameplay code comes to depend on the guess.

## Never
- **Structural change:** remove and re-add a replicated component on a predicted ghost without checking `RollbackPredictionOnStructuralChanges`.
  - **Consequence:** the component can reset to zero instead of the server value.
- **Local increment:** increment a replicated value locally without matching the server's quantization.
  - **Consequence:** NfE does not quantize between resimulated ticks, so the values drift.

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
```

## Example
- **"Poll `Input.GetKeyDown` in the predicted movement system, simpler than `IInputComponentData`":** declined.
  - **Why:** a tick can resimulate 20+ times per frame and the press would read true on an arbitrary replay.
  - **Did instead:** wired the jump as `InputEvent` in `IInputComponentData` gathered in `GhostInputSystemGroup`.

---
name: netcode-for-entities
description: >
  Technique for Unity's Netcode for Entities (NfE, package
  `com.unity.netcode`), the DOTS/ECS server-authoritative-with-client-prediction
  networking layer: `GhostAuthoringComponent`, `[GhostField]`,
  `[GhostComponent]`, `IRpcCommand`, `ICommandData`/`IInputComponentData`,
  `ClientServerBootstrap`, `PredictedSimulationSystemGroup`, `Simulate` tag,
  `NetworkTime`, `ClientServerTickRate`, ghost groups, host migration,
  connection approval, lag compensation. Use once NfE is the chosen
  foundation — replicating entity state, writing RPCs/commands, tuning
  prediction/interpolation/bandwidth, or debugging via the PlayMode
  Tool/Network Profiler. Not for: choosing NfE or the sync model
  (`netcode-architecture-decision`); general ECS entity/component/system
  modeling (`unity-ecs-architecture`); job scheduling and Burst compilation
  (`unity-job-system-and-burst`, `unity-burst-compiler`); non-predicted
  physics authoring (`unity-physics`); ghost rendering
  (`unity-entities-graphics`); UGS dashboard/account setup
  (`tech-lead-sdk-platform`).
---

# Netcode for Entities — Server-Authoritative Multiplayer with Client Prediction

## Bundled resources

### References
Read-only context, loaded on demand so SKILL.md itself stays short.

| File | Contents | Read when |
|---|---|---|
| [root-links.md](references/root-links.md) | Manual/API roots, the 6.6.0 version pin, which file answers which question | Starting any task here, or confirming the installed package version |
| [setup-and-worlds.md](references/setup-and-worlds.md) | Installation, `ClientServerBootstrap`, World types, build targets and defines | Standing up client/server Worlds, or picking the shipped topology |
| [transport-and-connection.md](references/transport-and-connection.md) | Drivers, Relay integration, protocol version checks, connection state machine | Wiring a transport, or a connection that won't reach `Connected` |
| [ghost-authoring.md](references/ghost-authoring.md) | `GhostAuthoringComponent` modes, `[GhostField]`, `[GhostComponent]`, variants | Declaring a networked entity or deciding which fields replicate |
| [ghost-spawning-and-groups.md](references/ghost-spawning-and-groups.md) | Server/predicted/pre-spawn paths, spawn classification, `GhostGroup` | A ghost needs to be created, pre-placed, or replicated atomically with others |
| [ghost-serialization-templates.md](references/ghost-serialization-templates.md) | Custom `[GhostField]` code-gen templates and `SubType` registration | A field's type has no native replication support |
| [rpcs-and-commands.md](references/rpcs-and-commands.md) | `IRpcCommand` send/receive, `ICommandData`/`IInputComponentData`, byte limits | Choosing or writing an RPC or per-tick input |
| [time-and-interpolation.md](references/time-and-interpolation.md) | `NetworkTime`, tick-rate settings, interpolation/extrapolation buffer | Reasoning about tick timing, or tuning smoothness of a remote ghost |
| [prediction-core.md](references/prediction-core.md) | The resimulation loop, `Simulate` tag query patterns, partial ticks | Writing or reading a predicted-ghost system |
| [prediction-caveats.md](references/prediction-caveats.md) | Smoothing, prediction switching, known edge cases, server-side rewind | A prediction correction is visible, or a switch looks wrong |
| [physics-integration.md](references/physics-integration.md) | Predicted physics group, batching, multi-world client-only physics | A predicted ghost needs physics, or a client-only VFX physics world |
| [host-migration.md](references/host-migration.md) | Host migration API, Lobby/Relay flow, hard limits | The session must survive a client-hosted host leaving |
| [testing-and-debugging.md](references/testing-and-debugging.md) | PlayMode Tool, Network Profiler, thin clients, logging, source generators | Verifying a claim, or diagnosing an unexplained networking symptom |
| [optimization-and-bandwidth.md](references/optimization-and-bandwidth.md) | Importance, relevancy, preserialization, serialization/snapshot-size cost | Bandwidth or prediction CPU cost needs to come down |
| [api-and-settings-reference.md](references/api-and-settings-reference.md) | Every Netcode-specific component/singleton and Project Settings field | The exact component or setting name is needed |

## 1. Objective
Wire a DOTS/ECS project's networked state through ghosts, RPCs, and the
command stream so client prediction actually agrees with server authority
instead of silently diverging from it. It prevents the failures NfE makes
easy to introduce by accident: a game rule reimplemented inside a networked
`ISystem` instead of called from `Game.Core.*`, a predicted-ghost query
written against a raw tick instead of the `Simulate` tag so it runs on
frozen entities mid-rollback, `UnityEngine.Input` polled inside the
prediction loop so every resimulation reads a different answer, a
`NetworkStreamInGame` tag nobody added so a connection never receives
anything, and an experimental host-migration feature shipped without the
caveat that it is exactly that.

## 2. Role
Act as the DOTS multiplayer networking specialist for the client track —
the tool reached for once `netcode-architecture-decision` has approved
Netcode for Entities as the project's netcode foundation and ECS is already
the chosen architecture (`unity-ecs-architecture`'s own escalation gate),
and a feature's entities, ghosts, and prediction loop need to be authored
or diagnosed.

## 3. When to invoke this skill
- Declaring a networked entity as a ghost prefab and deciding which fields
  replicate — `GhostAuthoringComponent`, `[GhostField]`, `[GhostComponent]`.
- Choosing between an RPC (`IRpcCommand`) and the command stream
  (`ICommandData`/`IInputComponentData`) for a specific piece of traffic.
- Standing up client/server Worlds, picking the build topology, or wiring a
  transport/Relay driver.
- Writing or debugging a predicted-ghost system, a visible
  correction/misprediction, or an interpolation smoothness issue.
- Tuning bandwidth or CPU cost — importance, relevancy, `MaxSendRate`,
  preserialization, quantization.
- Adding host migration to a client-hosted session, or investigating why it
  didn't preserve some piece of state.
- A reported symptom: a connection that never receives snapshots, a ghost
  that "teleports" when switching prediction mode, a component that resets
  to zero after a predicted rollback.
- Negative trigger: whether to adopt NfE at all, or which synchronization
  model the game needs — that's `netcode-architecture-decision`.
- Negative trigger: entity/component/system/query layout for non-networked
  ECS gameplay — that's `unity-ecs-architecture`; this skill only adds the
  networking layer on top.
- Negative trigger: Job System scheduling, `JobHandle` chains, or Burst
  compilation constraints — `unity-job-system-and-burst` and
  `unity-burst-compiler`, unchanged by anything here.
- Negative trigger: non-predicted Unity Physics authoring — colliders,
  joints, layers — that's `unity-physics`; this skill covers only how
  physics folds into the prediction loop.
- Negative trigger: how a ghost's entity actually renders — that's
  `unity-entities-graphics`.
- Negative trigger: creating the Unity Gaming Services project, Dashboard,
  or Lobby/Relay/Authentication account setup itself — that's
  `tech-lead-sdk-platform`; this skill covers only the NfE-side API once
  those services exist.

## 4. How to use this skill
1. **Confirm NfE is the approved foundation before writing any networking code** — this skill implements a decision already made, not one it makes itself, per `netcode-architecture-decision`'s ownership of the foundation/sync-model choice and `unity-ecs-architecture`'s escalation gate for ECS, since NfE presupposes it. [root-links.md](references/root-links.md) pins the package version every file below assumes.
2. **Stand up client and server Worlds through `ClientServerBootstrap` before any networked system exists**, per [setup-and-worlds.md](references/setup-and-worlds.md) — pick the build topology (dedicated server, client-hosted, or both) from the GDD first, since it fixes which `UNITY_SERVER`/`UNITY_CLIENT` defines exist and which code compiles at all; confirm exact component/setting names against [api-and-settings-reference.md](references/api-and-settings-reference.md) instead of guessing.
3. **Configure the transport and connection lifecycle explicitly, rather than assuming a connection is ready for gameplay**, per [transport-and-connection.md](references/transport-and-connection.md) — `NetworkStreamInGame` must be added by hand once a connection is approved, and a Relay-backed session needs its own driver wiring; NfE does neither automatically.
4. **Model every piece of networked state as a ghost, never as a stream of ad hoc RPCs** — `GhostAuthoringComponent` plus `[GhostField]`, per [ghost-authoring.md](references/ghost-authoring.md). Pick `SupportedGhostMode`/`DefaultGhostMode` from who needs to predict it — the owner predicts their own character, everyone else interpolates — and reach for [ghost-spawning-and-groups.md](references/ghost-spawning-and-groups.md) or [ghost-serialization-templates.md](references/ghost-serialization-templates.md) only once plain `[GhostField]` genuinely cannot express the case (YAGNI).
5. **Choose RPC or command stream by who initiates and how often**, per [rpcs-and-commands.md](references/rpcs-and-commands.md) — `IRpcCommand` for a reliable, one-off event; `ICommandData`/`IInputComponentData` for continuous per-tick input. Never poll `UnityEngine.Input` inside a system that runs in the prediction loop; only the `GhostInputSystemGroup` gathering system may touch it.
6. **Keep the game rule itself in `Game.Core.*`, even inside a predicted `ISystem`** — per `coding-principles.md`'s Shared Core integrity section. Determinism is not optional here: the client's resimulation has to reach the same result the server will, so a rule quietly reimplemented inside `OnUpdate` is a second, divergent copy of the authority the server already owns.
7. **Write predicted-ghost systems against the `Simulate` tag, not a raw tick comparison**, per [prediction-core.md](references/prediction-core.md) and the tick math in [time-and-interpolation.md](references/time-and-interpolation.md) — `PredictedGhost.ShouldPredict()` still works but is the legacy pattern; write new queries against `Simulate` instead.
8. **Treat every prediction correction as something to minimize, not eliminate**, per [prediction-caveats.md](references/prediction-caveats.md) — NfE's own documentation states it does not guarantee determinism even with quantized values, so budget `GhostPredictionSmoothingSystem` and the documented edge cases (partial-snapshot interactions, quantization drift, structural-change races) rather than treating a visible correction as an eliminable bug.
9. **Route a predicted ghost's physics through `PredictedFixedStepSimulationSystemGroup`, never a bespoke physics loop**, per [physics-integration.md](references/physics-integration.md) — a second, unpredicted physics world is only for client-only VFX that must never interact with gameplay.
10. **Tune bandwidth and CPU deliberately, before assuming the transport itself is the bottleneck**, per [optimization-and-bandwidth.md](references/optimization-and-bandwidth.md) — importance, `MaxSendRate`, relevancy, and preserialization each trade something specific; measure with the Network Profiler's Snapshot Overview tab first, per `performance-and-algorithms.md`'s Verification section.
11. **Add host migration only for a client-hosted topology that actually needs to survive the host leaving**, per [host-migration.md](references/host-migration.md) — it requires `ENABLE_HOST_MIGRATION` plus Unity Lobby/Relay/Authentication, carries hard limits (10 MiB snapshot cap, no child-entity ghosts, WebGL unsupported), and is explicitly experimental; state that in the handoff per `coding-principles.md`'s Handoff section rather than presenting it as a finished guarantee.
12. **Verify every latency, bandwidth, or prediction-cost claim against the Network Profiler or PlayMode Tool** — never against local-loopback testing alone, per [testing-and-debugging.md](references/testing-and-debugging.md) and `performance-and-algorithms.md`'s Verification section; an in-Editor session with network emulation off has zero RTT, jitter, and packet loss by construction and proves nothing about a real connection.
13. **Ask before guessing tick rate, build topology, or which ghosts are predicted versus interpolated** — each one reshapes the ghost authoring and system layout, and a value assumed wrong is expensive to unwind once gameplay code already depends on it.

## 5. Specific goals / tasks this skill performs
- Declaring ghost prefabs and their replicated fields via
  `GhostAuthoringComponent`/`[GhostField]`/`[GhostComponent]`, including
  variants for types that can't be edited directly.
- Writing RPC send/receive systems and per-tick command/input structs, with
  byte limits and ownership routing handled correctly.
- Standing up client/server/thin-client Worlds, transport drivers, and
  Relay-backed connections, with approval where required.
- Authoring and debugging predicted-ghost systems against the `Simulate`
  tag, including partial-tick and rollback-safe patterns.
- Diagnosing prediction edge cases: visible corrections, quantization
  drift, structural-change races, prediction-switching artifacts.
- Folding Unity Physics into the prediction loop, including a second
  client-only physics world where needed.
- Tuning bandwidth/CPU via importance, relevancy, `MaxSendRate`,
  preserialization, and compression.
- Adding host migration to a client-hosted session, with its experimental
  status and hard limits flagged.
- Setting up and reading PlayMode Tool network emulation and the Network
  Profiler to back every claim with a measurement.
- Out of scope: choosing NfE or the sync model
  (`netcode-architecture-decision`); non-networked ECS modeling
  (`unity-ecs-architecture`); Job/Burst mechanics
  (`unity-job-system-and-burst`, `unity-burst-compiler`); non-predicted
  physics authoring (`unity-physics`); ghost rendering
  (`unity-entities-graphics`); UGS account/dashboard setup
  (`tech-lead-sdk-platform`).

## 6. Output format
```
## Netcode for Entities Work — <feature/system name>
- Foundation approved by: <netcode-architecture-decision reference, or "pre-existing project standard">
- Topology: <dedicated server / client-hosted / both> — Netcode Client Target and build defines confirmed
- Worlds/transport: <Worlds created, driver(s), Relay or not>
- Ghosts: <prefab(s), SupportedGhostMode/DefaultGhostMode, key GhostField choices>
- RPC/Command: <IRpcCommand vs. ICommandData/IInputComponentData choice and why>
- Core boundary: <which rule logic stayed in Game.Core.*, and what the system calls>
- Prediction: <Simulate-tag query pattern used, physics group, edge cases addressed>
- Bandwidth/CPU tuning: <importance/relevancy/MaxSendRate/preserialization — or "default, not yet tuned">
- Host migration: <enabled with limits flagged / not applicable>
- Verified via: <PlayMode Tool emulation settings and Network Profiler tabs read>
- Layer: Game.Core.* rule modules / Game.Client.* ghosts, systems, RPCs
- Known limitations: <...>
```

**Extended report — emit ONLY when the requester asks for it.** It replaces the one-line `Known limitations` above with all three fields:
```
- Known limitations: <what the delivered solution does not cover — omit this line entirely if there are genuinely none>
- Latent concerns: <failure modes not yet triggered: assumptions that hold only under current conditions, thresholds not yet reached, trade-offs knowingly deferred>
- Future remediation: <the concrete fix for each concern above, each with the condition that should trigger it>
```

## 7. Examples
**Example 1**
- Input: a Tech Spec calls for a player character that predicts locally and interpolates for everyone else, with a jump ability.
- Output: `GhostAuthoringComponent.DefaultGhostMode = OwnerPredicted`; `[GhostField(Quantization=1000)]` on position/rotation/velocity; `PlayerInput : IInputComponentData` with an `InputEvent Jump` field gathered in `GhostInputSystemGroup`; jump logic stayed in `Game.Core.Combat.JumpRules`, called from a `Simulate`-tag-gated `ISystem`; verified at 150 ms RTT / 5% loss via the PlayMode Tool and the Network Profiler's prediction tab.

**Example 2**
- Input: "Just poll `UnityEngine.Input.GetKeyDown` directly inside the predicted movement system, it's simpler than wiring up `IInputComponentData`."
- Output: declined — a system inside `PredictedSimulationSystemGroup` can resimulate a single tick more than 20 times in one frame at real latency, and `GetKeyDown` would return true on essentially a random one of those replays, which is client misprediction by construction, not a bug to chase later. Wired the jump through `InputEvent` inside `IInputComponentData` instead, per [rpcs-and-commands.md](references/rpcs-and-commands.md).

**Example 3**
- Input: QA reports a vehicle "teleports" briefly the moment a player takes control of it (a prediction-switch from interpolated to predicted).
- Output: traced to the roughly 2×ping timeline gap between the predicted and interpolated relative timelines, documented in [prediction-caveats.md](references/prediction-caveats.md). Replaced the instant switch with a `ConvertPredictionEntry` carrying a non-zero `TransitionDurationSeconds`, so `SwitchPredictionSmoothing` interpolates the correction instead of snapping it; reverified visually at 150 ms RTT via the PlayMode Tool.

## 8. Edge cases & guardrails
- Never poll `UnityEngine.Input` inside a system that runs in `PredictedSimulationSystemGroup` — a resimulated tick reads live input differently on each replay, which is misprediction by construction.
- Never reimplement a `Game.Core.*` rule inside a networked `ISystem` — `Unity.Entities`/`Unity.NetCode` are Unity dependencies Core cannot reference, so the copy silently diverges from the authority the server already owns, per `coding-principles.md`'s Shared Core integrity section.
- Never assume NfE guarantees determinism, quantized values or not — its own documentation states it does not; the project's own determinism discipline is what actually keeps client and server in agreement.
- Never write a predicted-ghost query without the `Simulate` tag — during a partial-snapshot rollback it runs on stale, frozen entities that should not be simulating this iteration.
- Never remove and re-add a replicated component on a predicted ghost without checking `RollbackPredictionOnStructuralChanges` — the re-added component can reset silently to its default (zero) value instead of the server's.
- Never ship host migration without flagging its experimental status and hard limits (10 MiB snapshot, no child-entity ghosts, WebGL unsupported) in the handoff, per `coding-principles.md`'s Handoff section.
- Never claim a bandwidth or latency fix worked from an in-Editor session with network emulation off — it has zero RTT, jitter, and loss by construction and cannot exercise the bug being fixed.
- Never let a client-side value drift from the server's silently — NfE does not quantize between ticks during resimulation, so an unquantized local increment can diverge from the server's quantized one.
- If tick rate, build topology, or which ghosts are predicted versus interpolated is unspecified, ask — do not guess a value gameplay code will come to depend on.

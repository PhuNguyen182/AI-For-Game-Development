---
name: unity-transport
description: >
  Technique for Unity Transport (`Unity.Networking.Transport`) —
  `NetworkDriver`, `NetworkConnection`, `NetworkEndpoint`, `NetworkPipeline`
  and its stages (`ReliableSequencedPipelineStage`, `SimulatorPipelineStage`,
  `FragmentationPipelineStage`), `NetworkSettings`, `NetworkDriver.Concurrent`,
  `MultiNetworkDriver`, TLS (`SecureNetworkProtocolParameter`), Unity Relay
  (`RelayServerData`), `WebSocketNetworkInterface`, and the
  `Unity.Netcode.NetworkTransport` interop contract. Use when building or
  debugging a raw driver/pipeline, enabling encryption or Relay, jobifying
  the driver update loop, or wiring a custom transport into NGO. Not for:
  `UnityTransport` component Inspector fields or NGO-level state sync
  (`netcode-for-gameobjects`), choosing a netcode foundation
  (`netcode-architecture-decision`), the reconciliation/tick protocol above
  the wire (`netcode-engineer`), server anti-cheat validation
  (`server-authoritative-engineer`).
---

# Unity Transport — Low-Level Networking Driver, Pipelines, Relay, Security

## Bundled resources

### References
Read-only context, loaded on demand so SKILL.md itself stays short.

| File | Contents | Read when |
|---|---|---|
| [root-links.md](references/root-links.md) | Manual and API roots, the package version pin, which file answers which question | Starting any task here, or confirming the installed package version |
| [core-driver-lifecycle.md](references/core-driver-lifecycle.md) | `NetworkDriver`, `NetworkConnection`, `NetworkEndpoint`, `NetworkSettings`, Bind/Listen/Connect, the update loop | Creating a driver, opening a connection, or debugging a stalled update loop |
| [pipelines-reliability-simulation.md](references/pipelines-reliability-simulation.md) | `NetworkPipeline` and its stages, `ReliableUtility`, `FragmentationUtility`, `SimulatorUtility` | Choosing delivery guarantees, fragmenting large payloads, or testing packet loss/latency |
| [jobs-and-concurrent-api.md](references/jobs-and-concurrent-api.md) | `NetworkDriver.Concurrent`, `MultiNetworkDriver`, Burst-job driver usage | Moving the driver update into the Job System/Burst |
| [security-and-encryption.md](references/security-and-encryption.md) | TLS/DTLS setup, `SecureNetworkProtocolParameter`, certificate/key handling | Traffic must be encrypted, or a handshake/certificate error needs diagnosing |
| [relay-and-cross-play.md](references/relay-and-cross-play.md) | Unity Relay (`RelayServerData`), NAT traversal, cross-play considerations | No public server IP is available, or the session must support cross-play |
| [webgl-and-ngo-integration.md](references/webgl-and-ngo-integration.md) | `WebSocketNetworkInterface`, `Unity.Netcode.NetworkTransport` contract, custom NGO transports, migrating from 1.X | Targeting WebGL, or wiring/writing a custom transport for NGO |
| [diagnostics-and-testing.md](references/diagnostics-and-testing.md) | Connection/bandwidth statistics, logging, `DisconnectReason`/`StatusCode`, FAQ | Diagnosing a disconnect, reading driver statistics, or troubleshooting a build |

## 1. Objective
Wire raw Unity Transport (UTP) networking — driver creation, connections, pipelines, encryption, and Relay — so that the connection lifecycle stays correct across every frame, without the failure modes that stay silent until a real connect/send/disconnect run exposes them: a driver whose `ScheduleUpdate` gets skipped and stalls incoming events, a payload sent on an unreliable pipeline that silently drops under packet loss, a `NetworkDriver.Concurrent` call made outside a job, or unencrypted traffic shipped to a public endpoint.

## 2. Role
Act as the Unity Transport implementation specialist for the client track — the tool `netcode-engineer` and `unity-engineer` reach for whenever a feature needs a raw UTP driver, a custom NGO transport, or transport-level concerns (encryption, Relay, packet simulation, WebGL sockets) that sit below NGO's own API. This skill supplies the UTP API surface; it does not decide the sync protocol, the game rule riding on top of it, or NGO's own `NetworkVariable`/Rpc/`NetworkObject` layer.

## 3. When to invoke this skill
- Creating or configuring a `NetworkDriver`, binding/listening/connecting, or debugging a stalled or dropped connection.
- Building a `NetworkPipeline` for reliability, ordering, or fragmentation, or adding `SimulatorPipelineStage` for network-condition testing.
- Moving driver updates into the Job System via `NetworkDriver.Concurrent`/`MultiNetworkDriver`.
- Enabling TLS/DTLS encryption, or configuring Unity Relay for NAT traversal/cross-play.
- Targeting WebGL (`WebSocketNetworkInterface`), or writing/wiring a custom transport against `Unity.Netcode.NetworkTransport` for NGO.
- Reading connection/bandwidth statistics or diagnosing a disconnect reason/status code.
- Negative trigger: configuring the `UnityTransport` component's own Inspector fields, or anything at the `NetworkVariable`/Rpc/`NetworkObject` level — that is `netcode-for-gameobjects`; this skill only supplies the transport underneath it.
- Negative trigger: whether UTP/NGO is even the right netcode foundation for this project, versus Mirror/Photon/custom — that is `netcode-architecture-decision`; this skill assumes UTP is already chosen.
- Negative trigger: the reconciliation/prediction protocol, tick rate, or message format riding on top of the transport — `netcode-engineer` owns that decision; this skill supplies the API used to send the bytes.
- Negative trigger: server-side validation/anti-cheat of any data carried over the wire — `server-authoritative-engineer`.

## 4. How to use this skill
1. **Decide whether this is a standalone NetworkDriver integration or the NGO UnityTransport component before writing any code** — confirm the installed package version against [root-links.md](references/root-links.md) first, since UTP's API changed across major versions; the standalone path (manual driver lifecycle, per [core-driver-lifecycle.md](references/core-driver-lifecycle.md)) and the NGO path (implementing against `Unity.Netcode.NetworkTransport`, per [webgl-and-ngo-integration.md](references/webgl-and-ngo-integration.md)) have different lifecycles neither substitutes for.
2. **Create and Bind/Listen the NetworkDriver, then drive it every frame via ScheduleUpdate/Complete/PopEvent without skipping a frame** — per [core-driver-lifecycle.md](references/core-driver-lifecycle.md), the driver and every `NativeList`/`NativeArray` it owns must also be `Disposed` on shutdown.
3. **Assemble the NetworkPipeline from stages the data actually needs, not by habit** — per [pipelines-reliability-simulation.md](references/pipelines-reliability-simulation.md), pick reliable/fragmented/unreliable stages by payload size and delivery guarantee; never default every send to the reliable pipeline.
4. **Gate SimulatorPipelineStage behind an Editor or dev-build check** — per [pipelines-reliability-simulation.md](references/pipelines-reliability-simulation.md), it exists to test packet loss/latency/jitter and must never ship in a release build.
5. **Reach for the Concurrent driver and pipeline API only inside Burst-compiled jobs**, per [jobs-and-concurrent-api.md](references/jobs-and-concurrent-api.md). Escalate to `NetworkDriver.Concurrent`/`MultiNetworkDriver` only once profiling shows the main-thread driver update is the actual bottleneck — don't pre-build the jobified path (YAGNI).
6. **Enable TLS via SecureNetworkProtocolParameter whenever traffic crosses the public internet**, per [security-and-encryption.md](references/security-and-encryption.md) and `coding-principles.md`'s Shared Core integrity section — never ship gameplay-relevant traffic unencrypted.
7. **Route through Unity Relay's RelayServerData when the topology needs NAT traversal without a public server IP** — per [relay-and-cross-play.md](references/relay-and-cross-play.md), plug the allocation into `NetworkSettings` rather than hand-rolling hole-punching.
8. **Treat the Unity.Netcode NetworkTransport contract as NGO's integration boundary, never reimplement transport lifecycle in Game.Client code** — a custom transport implements that abstract class's send/poll/disconnect contract and nothing else, per [webgl-and-ngo-integration.md](references/webgl-and-ngo-integration.md).
9. **Verify with a real multi-client connect, send, and disconnect run before claiming the feature works** — per [diagnostics-and-testing.md](references/diagnostics-and-testing.md) and `performance-and-algorithms.md`'s Verification section, a compile pass is not proof the handshake or pipeline behaves under real conditions.
10. **Ask netcode-engineer or Technical Architect when reliability guarantees, encryption requirements, or relay-versus-direct topology aren't specified** — these are hard-to-reverse choices that ripple through every pipeline and connection written afterward; flag rather than guess.

## 5. Specific goals / tasks this skill performs
- Create and configure a `NetworkDriver` (Bind/Listen or Connect) with the correct `NetworkSettings` for the feature's needs.
- Build a `NetworkPipeline` with the reliability/ordering/fragmentation stages the payload actually requires.
- Add `SimulatorPipelineStage` for a dev-only packet-loss/latency test, gated out of release builds.
- Move driver polling into a Burst job via `NetworkDriver.Concurrent`/`MultiNetworkDriver` once profiling justifies it.
- Enable TLS/DTLS encryption, or configure Unity Relay for NAT traversal/cross-play sessions.
- Implement or wire a custom transport against `Unity.Netcode.NetworkTransport` for NGO, including WebGL socket support.
- Out of scope: `UnityTransport` component configuration and NGO-level sync (`netcode-for-gameobjects`), the netcode foundation decision (`netcode-architecture-decision`), reconciliation/tick protocol design (`netcode-engineer`), server-side anti-cheat validation (`server-authoritative-engineer`).

## 6. Output format
```
## Unity Transport Work — <feature/system name>
- Integration path: standalone NetworkDriver / NGO UnityTransport custom transport — rationale
- Pipeline: <stages used> — delivery guarantee and why
- Concurrency: main-thread driver / Concurrent-in-job — rationale
- Security/topology: TLS enabled? Relay or direct connect? — rationale
- Verification: <multi-client connect/send/disconnect run, or how confirmed>
- Layer: Game.Core.* / Game.Client.* / Editor-only
- Known limitations: <...>
```

**Extended report — emit ONLY when the requester asks for it.** It replaces the one-line `Known limitations` above with all three fields:
```
- Known limitations: <what the delivered transport setup does not cover>
- Latent concerns: <failure modes not yet triggered: assumptions that hold only under current conditions, thresholds not yet reached, trade-offs knowingly deferred>
- Future remediation: <the concrete fix for each concern above, each with the condition that should trigger it>
```

## 7. Examples
**Example 1**
- Input: "Need a reliable pipeline for chat messages and an unreliable one for frequent position updates, direct LAN connection."
- Output: two `NetworkPipeline`s created via `NetworkDriver.CreatePipeline` — one with `ReliableSequencedPipelineStage` for chat, one with the driver's default unreliable pipeline for position updates; no `FragmentationPipelineStage` added since neither payload exceeds the MTU, per [pipelines-reliability-simulation.md](references/pipelines-reliability-simulation.md).

**Example 2**
- Input: "Just poll NetworkDriver.Concurrent from Update() directly, it's simpler than setting up a job."
- Output: declined — `Concurrent` APIs are for use inside Burst-compiled jobs from multiple threads; calling them from `Update()` on the main thread gains nothing over the plain `NetworkDriver` API and adds needless complexity, per step 5. Used the plain `NetworkDriver` API instead, per [core-driver-lifecycle.md](references/core-driver-lifecycle.md).

**Example 3**
- Input: "Feature needs to work for players behind strict NATs with no dedicated server, and must run in a WebGL build."
- Output: Unity Relay allocation via `RelayServerData` for NAT traversal, per [relay-and-cross-play.md](references/relay-and-cross-play.md); `WebSocketNetworkInterface` selected for the WebGL target instead of the UDP interface, since WebGL cannot open raw UDP sockets, per [webgl-and-ngo-integration.md](references/webgl-and-ngo-integration.md).

## 8. Edge cases & guardrails
- Never skip a frame's `NetworkDriver.ScheduleUpdate`/`Complete` call — pending events queue up and connection-state transitions (timeout, disconnect) can be missed entirely.
- Never leave `SimulatorPipelineStage` wired into a release build — it exists purely to inject artificial packet loss/latency for testing and will degrade real player connections if shipped.
- Never call a `Concurrent` driver/pipeline method from the main thread outside a job — it is job-safety API, not a shortcut, and using it there adds complexity without the concurrency it exists for.
- Never build a custom Relay/hole-punch/NAT-traversal path speculatively — `RelayServerData` already exists for the measured case; only reach for it once direct connect is confirmed unworkable, not by default (YAGNI).
- If the Tech Spec doesn't state encryption requirements or relay-versus-direct topology, ask rather than guess — shipping unencrypted traffic to a public endpoint, or building direct-connect-only when Relay was actually required, are both expensive to reverse after launch.

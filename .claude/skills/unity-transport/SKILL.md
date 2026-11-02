---
name: unity-transport
description: "Unity Transport 6.6: NetworkDriver, NetworkConnection, NetworkPipeline, Relay, DTLS. Use for low-level networking."
user-invocable: false
---

# Unity Transport

- **Not for:** `UnityTransport` component Inspector fields or NGO-level sync (`netcode-for-gameobjects`).
- **Not for:** Worlds and connections on the DOTS stack (`netcode-for-entities`).
- **Not for:** choosing a netcode foundation (`netcode-architecture-decision`).
- **Not for:** reconciliation, tick or message protocol (`netcode-engineer`).
- **Not for:** server-side validation (`server-authoritative-validation`).
- **Docs:** https://docs.unity3d.com/Packages/com.unity.transport@6.6/manual/index.html (API: `.../api/index.html`), pinned to `com.unity.transport@6.6` (Unity 2022.3+).
  - **Version caveat:** the API changed across majors; check the installed version first (migration table in `webgl-and-ngo-integration.md`).

## References
- **[core-driver-lifecycle.md](references/core-driver-lifecycle.md):** Creating a driver, opening a connection, tuning `NetworkSettings`, or the update loop stalls.
- **[pipelines-reliability-simulation.md](references/pipelines-reliability-simulation.md):** Choosing delivery guarantees, sending payloads over the MTU.
  - **Also:** simulating loss/latency, or writing a custom stage.
- **[jobs-and-concurrent-api.md](references/jobs-and-concurrent-api.md):** Profiling shows the main-thread driver update is the bottleneck, or several transports share one server.
- **[security-and-encryption.md](references/security-and-encryption.md):** Traffic must be encrypted, or a handshake or certificate error needs diagnosing.
- **[relay-and-cross-play.md](references/relay-and-cross-play.md):** No public server IP, or clients mix UDP, WebSocket and IPv4/IPv6.
- **[webgl-and-ngo-integration.md](references/webgl-and-ngo-integration.md):** A WebGL target, a custom `Unity.Netcode.NetworkTransport`, or upgrading from UTP 1.X.
- **[diagnostics-and-testing.md](references/diagnostics-and-testing.md):** A disconnect reason or status code, driver statistics, or a bind/connect failure needs reading.

## Steps
1. **Pick the path before writing code:** standalone `NetworkDriver` (`core-driver-lifecycle.md`) or a custom transport for NGO (`webgl-and-ngo-integration.md`).
   - **Why:** their lifecycles differ.
2. **Bind and Listen, then drive the driver every frame:** with `ScheduleUpdate().Complete()` and drain events, per `core-driver-lifecycle.md`.
   - **Shutdown:** dispose the driver and every `Native*` it owns.
3. **Build pipelines from the stages the data needs:** choose reliable, fragmented or unreliable by payload size and delivery guarantee (`pipelines-reliability-simulation.md`).
   - **Default:** never default every send to reliable.
4. **Gate `SimulatorPipelineStage` and `NetworkSimulatorParameter` behind `UNITY_EDITOR`/`DEVELOPMENT_BUILD`:** they are test-only.
5. **Use `NetworkDriver.Concurrent` and `MultiNetworkDriver` only in Burst jobs, and only once profiling shows the main-thread update is the bottleneck:** per `jobs-and-concurrent-api.md`.
6. **Enable TLS/DTLS whenever traffic crosses the public internet:** per `security-and-encryption.md`.
   - **Untrusted:** treat gameplay-relevant traffic as untrusted.
7. **Use Relay (`RelayServerData`) when there is no public server IP and direct connect is confirmed unworkable:** per `relay-and-cross-play.md`.
   - **NAT:** do not hand-roll hole-punching or NAT traversal.
8. **Treat the `Unity.Netcode.NetworkTransport` contract as NGO's boundary:** a custom transport implements that class's send/poll/disconnect contract and nothing else.
9. **Verify with a real multi-client connect, send and disconnect run:** per `diagnostics-and-testing.md`.
   - **Why:** a compile pass does not show the handshake or pipeline works.
10. **Encryption, reliability guarantees or relay-versus-direct topology not specified:** return `Needs-decision`, `Next: cto` (foundation and topology) or `technical-architect` (feature spec).
    - **Why:** each is costly to reverse after launch.

## Never
- **Skipped update:** skip a frame's `ScheduleUpdate`/`Complete` — events queue and a timeout or disconnect can be missed.
- **Simulator in release:** ship a simulator stage in a release build.
- **Concurrent on the main thread:** call a `Concurrent` method from the main thread outside a job.

## Output
```
## Unity Transport Work — <feature/system>
- Integration path: standalone NetworkDriver / custom NGO NetworkTransport — rationale
- Pipeline: <stages> — delivery guarantee and why
- Concurrency: main-thread / Concurrent-in-job — rationale
- Security/topology: TLS? Relay or direct? — rationale
- Layer: Client / <Feature>/Server / Editor-only
```

## Example
- **"Just poll NetworkDriver.Concurrent from Update(), it's simpler than a job":** declined.
  - **Why:** it gains nothing over the plain driver there and skips the job dependency tracking.
  - **Did instead:** used the plain `NetworkDriver`.

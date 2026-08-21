# Testing and Debugging — PlayMode Tool, Network Profiler, thin clients, logging

Sources: [Test and debug your game](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/testing/debugging.html), [Logging](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/testing/logging.html), [PlayMode Tool](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/testing/playmode-tool.html), [Network Profiler tool](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/testing/network-profiler.html), [Thin clients](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/testing/thin-clients.html), [Gather metrics](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/testing/metrics.html), [Source generators](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/testing/source-generators.html).
Covers: SKILL.md §4 — **"Verify every latency, bandwidth, or prediction-cost claim against the Network Profiler or PlayMode Tool"**.

The tools that make a networking claim checkable instead of asserted.
`performance-and-algorithms.md`'s Verification section already requires a
measurement for any performance claim in general; this is where that
measurement comes from for anything network-shaped.

## PlayMode Tool — Window → Multiplayer → PlayMode Tools

| Field | Effect | Source |
|---|---|---|
| PlayMode Type | `Client` / `Server` / `Client & Server` — drives `ClientServerBootstrap` World creation on Play | [PlayMode Tool](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/testing/playmode-tool.html) |
| Num Thin Clients | Spawns N `ThinClientWorld`s for load simulation | [PlayMode Tool](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/testing/playmode-tool.html) |
| RTT Delay / RTT Jitter (ms) | Symmetric delay + random variance applied to client packets | [PlayMode Tool](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/testing/playmode-tool.html) |
| Packet Drop (%) | Percentage of packets discarded | [PlayMode Tool](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/testing/playmode-tool.html) |
| Packet Fuzz (%) | Simulates person-in-the-middle tampering of serialized data | [PlayMode Tool](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/testing/playmode-tool.html) |

**Critical caveat**: enabling network emulation forces a real UDP socket
(via Unity Transport) even for a same-machine client+server session — with
it disabled, client and server talk over IPC instead. An in-Editor test
with emulation off has **zero** RTT/jitter/loss by construction; it proves
nothing about real-network behavior, which is exactly why
[prediction-caveats.md](prediction-caveats.md)'s edge cases need emulation
turned on (50/150/500 ms per the server-rewind testing guidance) to surface
at all. Command-line presets: `--loadNetworkSimulatorJsonFile [path]` /
`--createNetworkSimulatorJsonFile [path]`, default `NetworkSimulatorProfile.json`.

## Network Profiler — Window → Analysis → Profiler (or Window → Multiplayer → Network Profiler)

Requires Unity 6.0+ and `com.unity.netcode` 1.12.0+. **Client World** and
**Server World** modules are **disabled by default** — enable them from the
Profiler Modules dropdown before recording.

| Tab | Shows | Source |
|---|---|---|
| Frame Overview | Total bandwidth, packet counts, instance counts | [Network Profiler](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/testing/network-profiler.html) |
| Snapshot Overview | Per-ghost-type Size, % of snapshot, Instance Count, Compression Efficiency, Avg size/instance, Overhead | [Network Profiler](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/testing/network-profiler.html) |
| Prediction and Interpolation | Prediction error visualization, Client World only | [Network Profiler](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/testing/network-profiler.html) |

A newly spawned ghost shows lower compression efficiency at first (no
established baseline yet) — don't read that as a steady-state number.

## Thin clients

`World.IsThinClient()` / `WorldSystemFilterFlags.ThinClientSimulation`.
Render nothing, cannot spawn ghosts, and should run as little logic as
possible — they exist to load-test the server, not to visually verify
anything. `AutoCommandTarget` is **not** compatible with thin clients by
default; drive their input by setting `CommandTarget` manually.

## Logging

`NetDebug` singleton, levels `Debug` / `Notify` (default) / `Warning` /
`Error` / `Exception`. Packet-level dumps need an `EnablePacketLogging`
component on the connection entity, plus the `NETCODE_DEBUG` scripting
define (`NETCODE_NDEBUG` force-disables it). Log files are **not** cleaned
up automatically and can grow large — this is operational cost to budget
for, not just a debugging convenience.

## Metrics API (programmatic)

Add the needed component(s) to the `GhostMetricsMonitor` singleton to opt
into collection, then read via `SystemAPI.GetSingleton<T>()`:
`NetworkMetrics`, `SnapshotMetrics`, `GhostMetrics` (indexed by `GhostNames`),
`GhostSerializationMetrics`, `PredictionErrorMetrics` (indexed by
`PredictionErrorNames`). Use this when a number needs to feed an in-game
overlay or an automated test rather than a human reading the Profiler.

## Source generators

Serialization, RPC, and command boilerplate is generated at compile time,
not via runtime reflection — see
[ghost-serialization-templates.md](ghost-serialization-templates.md) if a
type needs a custom template. Default output: `Temp/NetCodeGenerated`
(cleared when Unity closes — never hand-edit or commit generated files).
Force regeneration via **Assets → Multiplayer → Force Code Generation**
when a codegen-affecting change (a new `[GhostField]`, a new template) isn't
picking up.

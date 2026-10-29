---
name: magiconion-rpc-networking
description: "MagicOnion client in Unity: code-first gRPC services, StreamingHub, shared interfaces, YetAnotherHttpHandler transport, receivers, lifecycle, heartbeats. Use when a project talks to a MagicOnion server."
user-invocable: false
---

# MagicOnion — Unity RPC Client

Not for: choosing the transport or designing tick rate, prediction, reconciliation or message semantics (`netcode-architecture-decision`, `netcode-engineer`), DTO design and versioning (`memorypack-serialization`), the async body, cancellation or retry around a call (`unitask-async-programming`), fanning a received call out in-process (`messagepipe-event-messaging`), the server `ServiceBase<T>`/`StreamingHubBase<THub,TReceiver>` implementation (`netcode-engineer`, `Game.Server.*`).
Docs: https://github.com/Cysharp/MagicOnion
Works against a contract `netcode-engineer` defined; this skill wires the client and handles wire failures, never designs the protocol.

## Steps
1. **Confirm the transport decision exists** — if MagicOnion was not chosen, stop and route to `netcode-architecture-decision`; reversing it later rewrites every call site.
2. **Contract lives in an assembly both client and server compile, with no `UnityEngine` reference** — a `Vector3` in a signature breaks the server build (same constraint as `Game.Core.*`, `naming-convention.md`). Use plain C# types; convert at each edge.
3. **Never redefine the interface client-side** — `MagicOnionClient.Create<T>()` must target the server's exact interface; a copy drifts silently until a call deserializes into the wrong shape.
4. **`GrpcChannelx` over `YetAnotherHttpHandler`, not retired `Grpc.Core`** — Unity's stock HTTP stack lacks HTTP/2; `Grpc.Core` is end-of-life (`coding-principles.md` → Obsolete APIs). Confirm which packages the project has before writing connection code.
5. **By who initiates**: `IService<T>` when the client asks, `StreamingHub` when the server pushes. No hub for a one-off request; no polling a unary call for what a receiver would deliver.
6. **Await every `UnaryResult<T>`** — un-awaited, the exception is swallowed and surfaces later as a gameplay bug with no network evidence.
7. **Create and dispose the channel and hub at matched points** — login or scene load; logout, `OnDestroy`, app quit and early returns (`coding-principles.md` → Exception handling). An undisposed channel holds a live socket.
8. **Confirm the receiver callback's synchronization context before touching any `UnityEngine` API** — off the main thread it throws inside the network stack. Marshal first if needed.
9. **Keep `TReceiver` a thin adapter, no gameplay decisions** — forward a discrete notification to `messagepipe-event-messaging`, a continuously observed value to `r3-reactive-extensions`.
10. **Enable heartbeats and define disconnect behaviour** — a connection dropped without FIN stays "connected" until written to. State the backoff and player-visible state; no silent infinite retry.
11. **Validate every server response where it is consumed** (`coding-principles.md` → Correctness boundaries).
12. **Missing contract method → escalate to `netcode-engineer`**; never add one client-side.

## Output
```
## MagicOnion Client Work — <service/hub name>
- Contract: <shared interface> — IService<T> / StreamingHub<THub,TReceiver>
- Contract assembly: <name> — no UnityEngine reference, compiled by both sides
- Channel stack: <GrpcChannelx / YetAnotherHttpHandler>; no Grpc.Core
- Lifecycle: created at <point>, disposed at <points, incl. early returns>
- Receiver: forwards to <MessagePipe message / R3 stream>; context <main thread / marshalled>
- Liveness: heartbeat <interval>, reconnection <backoff + player-visible state>
- Response validation: <what, where>
- Known limitations: <...>
```
On request only, add `Latent concerns` and `Future remediation`, each with its trigger.

## Example
- "Design a hub for live PvP sync and pick the tick rate and reconciliation while you're there" → declined the second half (`netcode-engineer`); implemented the client hub and receiver against the contract once it existed.

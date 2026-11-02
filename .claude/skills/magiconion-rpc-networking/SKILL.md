---
name: magiconion-rpc-networking
description: "MagicOnion client: gRPC services, StreamingHub, YetAnotherHttpHandler, heartbeats. Use with a MagicOnion server."
user-invocable: false
---

# MagicOnion — Unity RPC Client

- **Not for:** choosing the transport or designing tick rate, prediction, reconciliation or message semantics (`netcode-architecture-decision`, `netcode-engineer`).
- **Not for:** DTO design and versioning (`memorypack-serialization`).
- **Not for:** the async body, cancellation or retry around a call (`unitask-async-programming`).
- **Not for:** fanning a received call out in-process (`messagepipe-event-messaging`).
- **Not for:** the server `ServiceBase<T>`/`StreamingHubBase<THub,TReceiver>` implementation (`netcode-engineer`, `<Feature>/Server`).
- **Docs:** https://github.com/Cysharp/MagicOnion
- **Contract:** defined by `netcode-engineer`; this skill wires the client and handles wire failures, never designs the protocol.

## Steps
1. **Confirm the transport decision exists:** if MagicOnion was not chosen, stop and route to `netcode-architecture-decision`.
   - **Why:** reversing it later rewrites every call site.
2. **Contract lives in an assembly both client and server compile, with no `UnityEngine` reference:**
   - **Why:** a `Vector3` in a signature breaks the server build (same constraint as a Core assembly, `naming-convention.md`).
   - **Types:** plain C# types; convert at each edge.
3. **Never redefine the interface client-side:** `MagicOnionClient.Create<T>()` must target the server's exact interface.
   - **Why:** a copy drifts silently until a call deserializes into the wrong shape.
4. **`GrpcChannelx` over `YetAnotherHttpHandler`, not retired `Grpc.Core`:** Unity's stock HTTP stack lacks HTTP/2; `Grpc.Core` is end-of-life (`coding-principles.md` → Obsolete APIs).
   - **Before connection code:** confirm which packages the project has.
5. **By who initiates:** `IService<T>` when the client asks, `StreamingHub` when the server pushes.
   - **One-off request:** no hub.
   - **Server-delivered data:** no polling a unary call for what a receiver would deliver.
6. **Await every `UnaryResult<T>`:** un-awaited, the exception is swallowed and surfaces later as a gameplay bug with no network evidence.
7. **Create and dispose the channel and hub at matched points:** per `coding-principles.md` → Exception handling.
   - **Create:** at login or scene load.
   - **Dispose:** at logout, `OnDestroy`, app quit and early returns.
   - **Why:** an undisposed channel holds a live socket.
8. **Confirm the receiver callback's synchronization context before touching any `UnityEngine` API:** off the main thread it throws inside the network stack.
   - **Off the main thread:** marshal first if needed.
9. **Keep `TReceiver` a thin adapter, no gameplay decisions:**
   - **Discrete notification:** forward to `messagepipe-event-messaging`.
   - **Continuously observed value:** forward to `r3-reactive-extensions`.
10. **Enable heartbeats and define disconnect behaviour:** a connection dropped without FIN stays "connected" until written to.
    - **State:** the backoff and the player-visible state.
    - **Retry:** no silent infinite retry.
11. **Validate every server response where it is consumed:** per `coding-principles.md` → Correctness boundaries.
12. **Missing contract method → escalate to `netcode-engineer`:** never add one client-side.

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
```

## Example
- **"Design a hub for live PvP sync and pick the tick rate and reconciliation while you're there":** declined the second half (`netcode-engineer`).
  - **Did instead:** implemented the client hub and receiver against the contract once it existed.

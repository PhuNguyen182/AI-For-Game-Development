---
name: magiconion-rpc-networking
description: >
  Unity-side client of a MagicOnion RPC connection: code-first gRPC where a
  shared C# interface is the schema — `IService<T>` returning `UnaryResult<T>`
  for request/response, `StreamingHub<THub,TReceiver>` for bidirectional
  channels, `MagicOnionClient.Create<T>()`, `GrpcChannelx` over
  `YetAnotherHttpHandler` for HTTP/2 under Unity, receiver callbacks,
  heartbeats, reconnection. Serialized with MemoryPack, awaited as UniTask. Use
  it when the backend track is active and MagicOnion is already the chosen
  transport. Not for: choosing that transport or designing the sync model
  (`netcode-architecture-decision`, `netcode-engineer`), the DTOs on the wire
  (`memorypack-serialization`), async body mechanics
  (`unitask-async-programming`), fanning a received call out in-process
  (`messagepipe-event-messaging`), the server implementation
  (`server-authoritative-engineer`).
---

# MagicOnion — RPC Client Consumption on the Unity Side

## 1. Objective
Consume an already-designed MagicOnion service or hub contract from Unity — unary calls, a connected `StreamingHub`, its receiver, and the connection's lifecycle — without redefining the contract client-side, without an un-awaited call swallowing a failure, without leaking a channel, and without a dead connection continuing to look alive.

## 2. Role
Act as the Unity-side RPC client specialist, working against a contract `netcode-engineer` and Technical Architect defined and `server-authoritative-engineer` implemented. You wire the client to it and handle everything that can go wrong on the wire; you do not design the protocol.

## 3. When to invoke this skill
- The backend track is active, MagicOnion is the chosen transport, and a shared service or hub interface exists to consume from Unity.
- Implementing a request/response call: `MagicOnionClient.Create<IMatchmakingService>(channel)` and awaiting the returned `UnaryResult<T>`.
- Connecting a `StreamingHub<THub,TReceiver>` for server-pushed broadcasts or live state, and implementing the client's `TReceiver`.
- Standing up channel creation, heartbeats, disconnect detection, reconnection strategy, and teardown.
- A symptom on the client side: calls that appear to succeed but never reach the server, a hub that stops delivering without ever reporting a disconnect, or a Unity API call throwing inside a receiver callback.
- Negative trigger: deciding whether MagicOnion is the right transport, or designing tick rate, prediction, reconciliation, or message semantics — that's `netcode-architecture-decision` and `netcode-engineer`.
- Negative trigger: designing or versioning the DTOs a method passes — that's `memorypack-serialization`, which owns the wire format this transport carries.
- Negative trigger: the `async`/await body around a call, its cancellation, or its retry loop — that's `unitask-async-programming`.
- Negative trigger: distributing a received call to in-process subscribers — that's `messagepipe-event-messaging`; the receiver only hands it over.
- Negative trigger: implementing `ServiceBase<T>`/`StreamingHubBase<THub,TReceiver>` server-side — that's `server-authoritative-engineer`, in `Game.Server.*`.

## 4. How to use this skill
1. **Confirm the transport decision already exists before writing client code** — implementing against MagicOnion presumes it was chosen; if that call has not been made, it belongs to `netcode-architecture-decision`, and reversing it later rewrites every call site rather than one adapter.
2. **Put the contract in an assembly both the Unity client and the server compile, with no `UnityEngine` reference** — a `Vector3` or any Unity type in a method signature makes the contract uncompilable on the server, which is the same constraint `Game.Core.*` lives under in `naming-convention.md`. Use plain C# types and let each side convert at its own edge.
3. **Never redefine the interface client-side** — `MagicOnionClient.Create<T>()` targets the exact interface the server implements, and a parallel client-only copy drifts without any error until a call silently deserializes into the wrong shape.
4. **Use `GrpcChannelx` over `YetAnotherHttpHandler` rather than the retired `Grpc.Core` native library**, per the [MagicOnion documentation](https://github.com/Cysharp/MagicOnion) — Unity's stock HTTP stack does not speak HTTP/2, and `Grpc.Core` is end-of-life, which `coding-principles.md`'s Obsolete APIs rule bans new code against. Confirm which packages the project actually has before writing the connection code.
5. **Choose by who initiates: `IService<T>` when the client asks, `StreamingHub` when the server pushes** — do not hold a hub open for a one-off request a unary call covers, and do not poll a unary call for updates a receiver callback would deliver the moment they happen.
6. **Await every `UnaryResult<T>`** — an un-awaited call is fire-and-forget with its exception swallowed, so a failing RPC surfaces later as a gameplay bug with no network evidence attached. Cancellation and retry around the await follow `unitask-async-programming`.
7. **Own the channel and hub lifecycle at explicit, matched points** — created at login or scene load, disposed at logout, `OnDestroy`, and app quit, including early-return paths, per the `IDisposable` discipline in `coding-principles.md`'s Exception handling section. An undisposed channel holds a live socket.
8. **Confirm which synchronization context a receiver callback runs on before touching any `UnityEngine` API inside it** — a Unity API call off the main thread throws, and the exception surfaces inside the network stack rather than at the code that caused it. If the context is not the main thread, marshal first.
9. **Keep `TReceiver` a thin adapter with no gameplay decisions in it** — forward a discrete notification into `messagepipe-event-messaging` and a continuously-observed value into `r3-reactive-extensions`. The receiver's job is "a call arrived", not "here is what the game does about it".
10. **Enable heartbeats and define what a disconnect does** — a TCP connection that dies without a FIN stays "connected" until something writes to it, so without a heartbeat the client sits in a hub that will never deliver another message. State the backoff and the player-visible state; silent infinite retry is not a strategy.
11. **Validate every server response where it is consumed** — a network message is exactly the boundary `coding-principles.md`'s Correctness boundaries section requires validation at, and trusting it by construction assumes the server is never lagged, rolled back, or wrong.
12. **Escalate a missing contract method instead of inventing one** — if the call the client needs does not exist on the interface, that is a contract change for `netcode-engineer` and `server-authoritative-engineer`, not a client-side addition.

## 5. Specific goals / tasks this skill performs
- Implementing unary calls through `MagicOnionClient.Create<T>()` and awaiting `UnaryResult<T>`.
- Connecting a `StreamingHub<THub,TReceiver>` and implementing the client receiver as an adapter.
- Standing up the channel stack (`GrpcChannelx`, `YetAnotherHttpHandler`), heartbeats, reconnection, and disposal.
- Placing validation on incoming server data at its consumption point.
- Keeping the shared contract assembly free of `UnityEngine` types so both sides compile it.
- Out of scope: transport choice and sync-model design (`netcode-architecture-decision`, `netcode-engineer`), DTO design and versioning (`memorypack-serialization`), async mechanics (`unitask-async-programming`), in-process fan-out (`messagepipe-event-messaging`), server-side implementation (`server-authoritative-engineer`).

## 6. Output format
```
## MagicOnion Client Work — <service/hub name>
- Contract: <shared interface> — IService<T> / StreamingHub<THub,TReceiver>
- Contract assembly: <name> — confirmed no UnityEngine reference, compiled by both sides
- Channel stack: GrpcChannelx / YetAnotherHttpHandler — confirmed no Grpc.Core dependency
- Lifecycle: created at <point>, disposed at <point(s), including early returns>
- Await discipline: <every UnaryResult<T> awaited; cancellation per unitask-async-programming>
- Receiver: <TReceiver forwards to MessagePipe message / R3 stream>; context confirmed <main thread / marshalled>
- Liveness: heartbeat <interval>, reconnection <backoff + player-visible state>
- Response validation: <what is checked, at which call site>
- Layer: Game.Client.* — contract types in <shared assembly>
- Known limitations: <...>
```

**Extended report — emit ONLY when the requester asks for it.** It replaces the one-line `Known limitations` above with all three fields:
```
- Known limitations: <what the client does not handle — omit this line entirely if there are genuinely none>
- Latent concerns: <failure modes not yet hit: untested disconnect paths, assumed contract stability, unbounded retry>
- Future remediation: <the concrete fix for each concern above, each with the condition that should trigger it>
```

## 7. Examples
**Example 1**
- Input: the server implements `IMatchmakingService`; the Unity client needs `FindMatchAsync`.
- Output: created the channel through `GrpcChannelx`, resolved `MagicOnionClient.Create<IMatchmakingService>(channel)`, awaited the `UnaryResult<MatchResult>` with the scene's cancellation token per `unitask-async-programming`, validated the returned match before entering it, and disposed the channel on scene teardown and on the early-return path when the player cancels.

**Example 2**
- Input: "design a hub for live PvP state sync, and pick the tick rate and reconciliation approach while you're in there."
- Output: declined the second half — tick rate, reconciliation, and message semantics are `netcode-engineer`'s, informed by the sync model `netcode-architecture-decision` settled. Implemented the Unity-side hub client and receiver against the contract once it existed.

**Example 3**
- Input: a `StreamingHub` "works in the Editor" but players report the game freezing on state updates after a few minutes on mobile.
- Output: two faults. The receiver called `transform.position` directly, so a callback arriving off the main thread threw inside the network stack; it now marshals and forwards into an R3 stream the view observes. And no heartbeat was configured, so a connection dropped by the carrier's NAT timeout stayed "connected" and delivered nothing — heartbeat enabled, with a reconnect backoff and a visible "reconnecting" state.

## 8. Edge cases & guardrails
- Never redefine the service or hub interface client-side — it must be the same contract the server compiles, or calls deserialize into the wrong shape with no error.
- Never put a `UnityEngine` type in a contract signature — the server cannot compile it, and the break appears on their build, not yours.
- Never leave a `UnaryResult<T>` un-awaited — the failure is swallowed and resurfaces as an unexplained gameplay bug.
- Never write new code against `Grpc.Core` — it is end-of-life, and `coding-principles.md`'s Obsolete APIs rule forbids it.
- Never leave a channel or hub undisposed on any path, including early returns — each one holds a live socket.
- Never touch a `UnityEngine` API in a receiver callback without confirming the context — off the main thread it throws from inside the network stack.
- Never treat a server response as trusted by construction — validate it where it is consumed.
- Never make the transport or sync-model call from inside this skill — escalate it rather than settling it implicitly while writing client code.

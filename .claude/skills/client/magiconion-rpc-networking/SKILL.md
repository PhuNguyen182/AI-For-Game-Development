---
name: magiconion-rpc-networking
description: >
  Technique for implementing the Unity client side of a MagicOnion RPC
  connection — code-first gRPC where a shared C# interface *is* the
  protocol schema, `Service<T>`/`UnaryResult<T>` for request/response calls,
  `StreamingHub<THub,TReceiver>` for bidirectional real-time channels, and
  `MagicOnionClient.Create<TService>()`/hub connection setup — serialized
  with MemoryPack and awaited with UniTask. Only relevant when the backend
  track is active and a project has chosen MagicOnion as its RPC transport.
  Use this for writing/consuming the shared service interface and the
  Unity-side client proxy/hub receiver. Do not use this to decide whether
  MagicOnion (vs. a different netcode foundation) is the right choice at
  all, or to design the synchronization model (prediction/reconciliation,
  lockstep, rollback) — that's `netcode-architecture-decision` and
  `netcode-engineer`'s territory; this skill implements an
  already-chosen transport's client, it doesn't choose or design the
  protocol. Do not use this to design the DTOs the service/hub methods
  pass — that's `memorypack-serialization`, which this framework's
  `MagicOnion.Serialization.MemoryPack` package uses as its wire format.
  Do not use this to write the `async` bodies awaiting a `UnaryResult<T>` —
  that's `unitask-async-programming`, since `UnaryResult<T>` is
  UniTask-shaped. Do not use this to implement the server-side
  `ServiceBase<T>`/`StreamingHubBase<THub,TReceiver>` — that's
  `server-authoritative-engineer`'s territory (plain C#/ASP.NET Core,
  `Game.Server.*`, no `UnityEngine` dependency); this skill covers only the
  Unity-side client consumption of an interface the server already
  implements.
---

# MagicOnion — RPC Client Consumption (Unity Side)

Source: [github.com/Cysharp/MagicOnion](https://github.com/Cysharp/MagicOnion).

## 1. Objective
Consume an already-designed MagicOnion service/hub contract from the Unity client correctly — calling `Service<T>` methods, connecting a `StreamingHub<THub,TReceiver>`, handling connection lifecycle and reconnection — without duplicating the protocol/sync-model decision that belongs elsewhere, or leaking a raw gRPC/channel object past the client wrapper that owns it.

## 2. Role
Act as the Unity-side RPC client specialist, working from a contract `netcode-engineer`/Technical Architect has already defined and `server-authoritative-engineer` has already implemented server-side — you wire the Unity client up to it, you don't design it.

## 3. When to invoke this skill
- The backend track is active, MagicOnion has already been chosen as the RPC transport (per `netcode-architecture-decision`), and a shared C# service/hub interface already exists (or is being defined jointly with `netcode-engineer`) to implement client-side.
- Implementing a `Service<TInterface>`-based request/response call from Unity via `MagicOnionClient.Create<TInterface>(channel)`, awaiting the resulting `UnaryResult<T>`.
- Connecting to a `StreamingHub<THub,TReceiver>` for a persistent, bidirectional real-time channel (server-pushed broadcasts, live state sync) and implementing the client's `TReceiver` callback interface.
- Handling connection lifecycle: channel creation, `StreamingHub` connect/disconnect, reconnection strategy, and disposing the channel/hub proxy on scene/app teardown.
- Negative trigger: deciding whether MagicOnion is the right RPC transport, or designing the sync model (prediction/reconciliation, tick rate, message semantics) — that's `netcode-architecture-decision`/`netcode-engineer`.
- Negative trigger: designing the DTOs a service/hub method passes — that's `memorypack-serialization`.
- Negative trigger: writing the `async`/await body around a `UnaryResult<T>` — that's `unitask-async-programming`.
- Negative trigger: implementing the server-side `ServiceBase<T>`/`StreamingHubBase<THub,TReceiver>` — that's `server-authoritative-engineer`'s territory, not this skill's.

## 4. How to use this skill
1. **Treat the shared interface as the contract, never redefine it client-side.** The same C# interface Technical Architect/`netcode-engineer` defines and `server-authoritative-engineer` implements is what `MagicOnionClient.Create<TInterface>()` targets — don't hand-roll a parallel client-only interface that can drift from the server's.
2. **Use `Service<T>` for request/response, `StreamingHub<THub,TReceiver>` for persistent bidirectional channels** — don't force a `StreamingHub` connection for a one-off request that a `Service<T>` unary call already covers cleanly, and don't poll a `Service<T>` repeatedly when the actual need is server-pushed real-time updates a `StreamingHub` receiver callback handles directly.
3. **Own the channel/hub proxy's lifecycle explicitly.** Create the gRPC channel and hub connection at a well-defined point (scene load, login), and dispose/disconnect it at a matching teardown point (`OnDestroy`, logout, app quit) — an undisposed channel is a leaked network resource, the same Correctness-boundary discipline `coding-principles.md` already requires for any `IDisposable`.
4. **Await `UnaryResult<T>` like any other UniTask-shaped async call** — cancellation, `.Preserve()` if awaited from more than one place, and error handling follow `unitask-async-programming`'s guidance directly; this skill doesn't reinvent async handling for RPC specifically.
5. **Implement the `TReceiver` interface as a thin adapter**, forwarding server-pushed calls into the client's own event/message system (`messagepipe-event-messaging` for a discrete notification, `r3-reactive-extensions` for a continuously-observed value) rather than embedding gameplay logic directly inside the receiver implementation — Single Responsibility: the receiver's job is "translate an incoming hub call," not "also decide what happens next."
6. **Never treat a server response as trusted by construction.** Per `coding-principles.md`'s Correctness boundaries section, a network message is exactly the kind of boundary that needs validation on the client before acting on it — don't assume the server can't be wrong, lagged, or (per the anti-cheat angle `server-authoritative-engineer` already owns server-side) malicious in a compromised-client scenario.
7. **Reconnect deliberately, not silently.** A dropped `StreamingHub` connection should surface a clear reconnection strategy (backoff, user-facing state) rather than silently retrying forever or failing without any client-visible signal.

## 5. Specific goals / tasks this skill performs
- Implementing Unity-side `Service<T>` calls via `MagicOnionClient.Create<T>()` and awaiting `UnaryResult<T>`.
- Connecting and implementing the client `TReceiver` side of a `StreamingHub<THub,TReceiver>`.
- Managing gRPC channel/hub connection lifecycle (create, reconnect, dispose) on the Unity client.
- Adapting server-pushed hub calls into the client's own messaging (MessagePipe) or reactive (R3) systems.
- Out of scope: choosing/designing the transport or sync model (`netcode-architecture-decision`, `netcode-engineer`), DTO design (`memorypack-serialization`), async body mechanics (`unitask-async-programming`), server-side implementation (`server-authoritative-engineer`).

## 6. Output format
```
## MagicOnion Client Work — <service/hub name>
- Contract: <shared interface name> — Service<T> / StreamingHub<THub,TReceiver>
- Serialization: MemoryPack (via memorypack-serialization) — DTOs used
- Connection lifecycle: created at <point>, disposed at <point>
- Async handling: UnaryResult<T> awaited per unitask-async-programming — cancellation/.Preserve() as needed
- Server-push handling (if hub): TReceiver forwards to <MessagePipe message / R3 stream>
- Server-response trust: validated at <call site> before acting on it
- Reconnection strategy: <backoff/user-facing state, or "not applicable — Service<T> only">
- Known limitations: <...>
```

## 7. Examples
**Example 1**
- Input: the server team implemented `IMatchmakingService` (already agreed with `netcode-engineer`); the Unity client needs to call `FindMatchAsync`.
- Output: `MagicOnionClient.Create<IMatchmakingService>(channel)`, awaited the resulting `UnaryResult<MatchResult>` per `unitask-async-programming`'s cancellation guidance, validated the returned match data before using it, disposed the channel on scene teardown.

**Example 2**
- Input: "design a new MagicOnion hub for live PvP state sync, including the tick rate and reconciliation approach."
- Output: declined to design the protocol here — tick rate, reconciliation, and message semantics are `netcode-engineer`'s territory (informed by `netcode-architecture-decision`'s chosen sync model); once that contract exists, this skill implements the Unity-side `StreamingHub` client and `TReceiver` against it.

## 8. Edge cases & guardrails
- Never redefine the shared service/hub interface client-side — it must be the exact same contract the server implements.
- Never force a `StreamingHub` connection for a one-off request, or poll a `Service<T>` call for something a hub's server-pushed receiver already handles.
- Never leave a gRPC channel or hub connection undisposed — it's a leaked network resource on every code path, including an early return.
- Never trust a server response by construction — validate it at the point it's consumed, per the project's Correctness-boundary rule.
- Never embed gameplay decision logic inside a `TReceiver` implementation — forward the incoming call into the client's existing messaging/reactive system instead.
- Never make the sync-model/transport-choice call from inside this skill — escalate that decision to `netcode-architecture-decision`/`netcode-engineer` instead of deciding it implicitly while writing client code.

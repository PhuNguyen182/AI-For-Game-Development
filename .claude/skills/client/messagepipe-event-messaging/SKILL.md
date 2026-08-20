---
name: messagepipe-event-messaging
description: >
  Technique for decoupled, discrete message dispatch between client-track
  systems via MessagePipe — `IPublisher<T>`/`ISubscriber<T>` (keyless and
  keyed), `IRequestHandler<TRequest,TResponse>` request/response, filter
  middleware, `IAsyncPublisher`/`IAsyncSubscriber` (UniTask-backed), and
  `IBufferedPublisher`/`IBufferedSubscriber` for latest-value replay —
  registered through `vcontainer-dependency-injection`'s
  `RegisterMessagePipe`. Use this for a single, addressed event dispatched
  once between decoupled systems that shouldn't reference each other
  directly (an "ItemPickedUp" notification reaching the inventory, UI, and
  analytics systems without any of them knowing about each other). Do not
  use this for a continuous stream of values a subscriber composes/filters
  over time (health ticking, input, cooldown countdown, UI data binding) —
  that's `r3-reactive-extensions`; the two are often paired (an `Observable`
  pipeline's terminal `Subscribe` calls `IPublisher<T>.Publish` to notify
  other systems once) but solve different problems. Do not use this to write
  the async logic inside an `IAsyncPublisher`/`IAsyncSubscriber` handler —
  that's `unitask-async-programming`; this skill only decides that the
  handler should be async and how it's registered. Do not use this to
  decide the handler's lifetime/registration scope — that's
  `vcontainer-dependency-injection`, which owns the `RegisterMessagePipe()`
  call this skill's types get registered through. Never define a
  cross-process/cross-machine wire message here — an RPC contract between
  Unity client and a server process is `magiconion-rpc-networking`'s
  territory; MessagePipe is strictly in-process, in-memory dispatch.
---

# MessagePipe — Decoupled In-Process Event Messaging

Source: [github.com/Cysharp/MessagePipe](https://github.com/Cysharp/MessagePipe).

## 1. Objective
Replace direct references and `UnityEvent`-sprawl between unrelated client-track systems with typed, DI-registered pub/sub or request/response messages — without silently leaking a subscription, misusing a keyed channel where a keyless one would do, or reaching for MessagePipe when the actual need is a continuous reactive stream.

## 2. Role
Act as the in-process messaging specialist for the client track: the one who designs the message type, the publisher/subscriber contract, and any filter middleware — not the one who decides where in the DI graph it's registered (`vcontainer-dependency-injection`) or writes the async body of a handler (`unitask-async-programming`).

## 3. When to invoke this skill
- Two or more systems need to react to the same discrete event without referencing each other (inventory, UI, and analytics all reacting to "ItemPickedUp") — this is the Interface Segregation-adjacent case where a fat "notify everyone about everything" manager class would otherwise emerge.
- A request needs exactly one (or "all") typed response(s) from elsewhere in the app without a direct method call — `IRequestHandler<TRequest,TResponse>`/`IRequestAllHandler`.
- A late subscriber needs the most recent value immediately on subscribing, not just future events — `IBufferedPublisher`/`IBufferedSubscriber`.
- Cross-cutting behavior (logging every published message, validating a request before it reaches its handler) belongs to every subscriber of a given message type — implement it as a MessagePipe filter instead of duplicating the check in every handler (Open/Closed in `coding-principles.md`: add a filter, don't edit every handler).
- Negative trigger: a continuous stream of values a subscriber composes/filters/transforms over time — that's `r3-reactive-extensions`.
- Negative trigger: writing the async logic inside a handler — that's `unitask-async-programming`; this skill only decides the handler should be `IAsyncPublisher`/`IAsyncSubscriber`-shaped.
- Negative trigger: deciding the handler's DI lifetime/registration — that's `vcontainer-dependency-injection`'s `RegisterMessagePipe()`.
- Negative trigger: a message crossing a process/machine boundary (client↔server) — that's `magiconion-rpc-networking`; MessagePipe is in-process only.

## 4. How to use this skill
1. **Model the message as an immutable data type** (a `readonly record struct`/`record` per `naming-convention.md`'s casing rules) carrying only what subscribers need — not a live reference to the publishing system's internal state.
2. **Choose keyless vs. keyed deliberately.** Keyless `IPublisher<T>`/`ISubscriber<T>` when the message type alone identifies the channel; keyed `IPublisher<TKey,T>`/`ISubscriber<TKey,T>` only when multiple independent channels of the same message shape genuinely need separate routing (e.g. per-player-slot events) — don't default to keyed "just in case" (YAGNI).
3. **Use request/response only for a genuine query-with-answer**, not as a workaround for two-way coupling that a plain injected interface would express more simply — `IRequestHandler<TRequest,TResponse>` is for "ask and get exactly one typed answer," not general RPC-style coupling between two systems that could just take a direct dependency.
4. **Reach for `IAsyncPublisher`/`IAsyncSubscriber` only when a handler genuinely needs to be async**, and decide the async strategy (parallel vs. sequential handler execution) deliberately rather than accepting the default without checking whether ordering matters.
5. **Use `IBufferedPublisher`/`IBufferedSubscriber` for "give me the latest value immediately on subscribe" semantics** (a settings-changed notification a late-joining UI panel needs right away) instead of manually caching and replaying the last value yourself.
6. **Always dispose subscriptions**, aggregated via `DisposableBag` when a class owns several — an un-disposed MessagePipe subscription is exactly the kind of dangling handler `coding-principles.md`'s Event handlers section and `performance-and-algorithms.md`'s Memory discipline section warn about. Enable the optional Roslyn analyzer that flags a missing `Dispose()` at compile time if the project's tooling budget allows it.
7. **Write filters for cross-cutting handler behavior** (logging, validation, exception boundary) instead of duplicating that logic inside every handler for a message type — this is Open/Closed applied to messaging middleware.

## 5. Specific goals / tasks this skill performs
- Designing a message type and choosing keyless vs. keyed pub/sub for a specific decoupling need.
- Designing a request/response contract via `IRequestHandler<TRequest,TResponse>`/`IRequestAllHandler`.
- Writing filter middleware for cross-cutting subscriber behavior.
- Choosing buffered pub/sub (`IBufferedPublisher`/`IBufferedSubscriber`) for late-subscriber replay semantics.
- Auditing subscription disposal for leaks.
- Out of scope: continuous reactive streams (`r3-reactive-extensions`), the async body of a handler (`unitask-async-programming`), DI registration/lifetime (`vcontainer-dependency-injection`), cross-process wire contracts (`magiconion-rpc-networking`).

## 6. Output format
```
## MessagePipe Work — <message name>
- Message type: <record/struct name and payload>
- Routing: keyless / keyed (<key type>) — rationale
- Pattern: Publish/Subscribe / Request-Response / Buffered — rationale
- Async: sync / IAsyncPublisher-IAsyncSubscriber (strategy: parallel/sequential)
- Filters applied: <none / list with purpose>
- Disposal: DisposableBag / individual IDisposable — confirmed
- Known limitations: <...>
```

## 7. Examples
**Example 1**
- Input: inventory, UI toast, and analytics all need to react when an item is picked up, with no direct references between them.
- Output: defined `readonly record struct ItemPickedUp(int ItemId, int Quantity)`, registered keyless `IPublisher<ItemPickedUp>`/`ISubscriber<ItemPickedUp>` via VContainer's `RegisterMessagePipe`, each system subscribing independently and disposing via `DisposableBag` tied to its own scope; no system references another.

**Example 2**
- Input: "publish the player's health every frame so the boss AI can react to low-health thresholds."
- Output: declined as a MessagePipe fit — a continuously-observed, filtered value (threshold crossing) is `r3-reactive-extensions`'s territory (`healthProperty.Where(h => h < threshold).DistinctUntilChanged()`); recommended publishing a single `PlayerHealthCriticalEvent` through MessagePipe only at the moment the threshold is actually crossed, not every frame.

## 8. Edge cases & guardrails
- Never publish a live mutable reference as a message payload — messages are immutable snapshots subscribers can't accidentally corrupt.
- Never default to a keyed channel without a genuine multi-channel routing need — that's unjustified complexity (YAGNI).
- Never use request/response as a substitute for a direct injected dependency when the two systems are already meant to be coupled — that's over-engineering the interaction.
- Never leave a subscription without a disposal path — aggregate with `DisposableBag` and dispose on the owning scope's teardown.
- Never model a client↔server wire message here — that crosses into `magiconion-rpc-networking`'s territory; MessagePipe never leaves the process.

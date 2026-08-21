---
name: messagepipe-event-messaging
description: >
  MessagePipe — decoupled in-process message dispatch: keyless and keyed
  `IPublisher<T>` and `ISubscriber<T>`, `IRequestHandler<TRequest,TResponse>`
  and `IRequestAllHandler`, `IAsyncPublisher` and `IAsyncSubscriber`
  (UniTask-backed, parallel or sequential), `IBufferedPublisher` and
  `IBufferedSubscriber` for latest-value replay, filter middleware for
  cross-cutting behaviour, and `DisposableBag` disposal — registered through
  `RegisterMessagePipe()`. Use for one discrete addressed event reaching
  systems that must not reference each other, such as an item pickup seen by
  inventory, UI, and analytics at once.
  Not for: continuous streams a subscriber composes over time (`r3-reactive-extensions`), the async body of a handler (`unitask-async-programming`), DI registration and lifetime (`vcontainer-dependency-injection`), cross-process wire contracts (`magiconion-rpc-networking`).
---

# MessagePipe — Decoupled In-Process Event Messaging

## 1. Objective
Replace direct references and `UnityEvent` sprawl between unrelated systems with typed, DI-registered pub/sub and request/response — without leaking a subscription, reaching for a keyed channel that routes nothing, or shipping a bus whose decoupling is undone the first time one subscriber throws.

## 2. Role
Act as the in-process messaging specialist for the client track: the one who designs the message type, the publisher and subscriber contract, and the filter middleware around them — not the one who decides where in the DI graph they are registered, nor the one who writes a handler's async body.

## 3. When to invoke this skill
- Two or more systems must react to the same discrete event without referencing each other, where a "notify everyone about everything" manager would otherwise appear.
- A caller needs exactly one typed answer, or all handlers' answers, from elsewhere in the app without taking a direct dependency.
- A late subscriber must receive the most recent value the moment it subscribes rather than only future events.
- Cross-cutting behaviour — logging every publish, validating a request, bounding exceptions — applies to every subscriber of a message type and is currently duplicated in each handler.
- Negative trigger: a continuously observed value a subscriber filters and transforms over time — that is `r3-reactive-extensions`; the two pair naturally, with a pipeline's terminal `Subscribe` publishing once.
- Negative trigger: writing the async logic inside a handler — that is `unitask-async-programming`; this skill decides only that the handler is async-shaped and how dispatch is configured.
- Negative trigger: the handler's registration and lifetime scope — that is `vcontainer-dependency-injection`, which owns the `RegisterMessagePipe()` call these types are registered through.
- Negative trigger: a message crossing a process or machine boundary — that is `magiconion-rpc-networking`; MessagePipe never leaves the process.

## 4. How to use this skill
1. **Model the message as an immutable snapshot of values, never a live reference into the publisher's state** — a `readonly record struct` following `naming-convention.md`'s casing table, per the [MessagePipe documentation](https://github.com/Cysharp/MessagePipe). A payload holding a mutable reference lets any subscriber mutate what the others receive, which reintroduces the coupling the bus exists to remove.
2. **Choose keyless before keyed, and justify keyed by an actual routing need** — keyless `IPublisher<T>` when the message type alone identifies the channel, keyed only when independent channels of the same shape genuinely need separate routing such as per-player-slot events. A keyed channel with one key is complexity YAGNI already forbids.
3. **Use request/response only for a genuine query with an answer** — `IRequestHandler<TRequest,TResponse>` is for asking and receiving exactly one typed result. Two systems that are meant to be coupled should take a direct injected interface instead; routing that through the bus hides the dependency without removing it.
4. **Treat synchronous publish as re-entrant and never publish a message type from inside its own handler** — dispatch runs on the caller's stack, so a handler that republishes re-enters the same dispatch and can recurse without bound. Break the cycle by publishing a different message, or by deferring the second publish.
5. **Put an exception-boundary filter on any message with multiple independent subscribers** — in synchronous dispatch a throwing handler propagates to the publisher and the remaining subscribers never run, so one failing system silently disables the others. That is the decoupling promise being broken, and a filter is what actually keeps it.
6. **Reach for `IAsyncPublisher` and `IAsyncSubscriber` only when a handler genuinely awaits, and set the dispatch strategy explicitly** — parallel when handlers are independent, sequential when ordering between them matters. Accepting the default without deciding leaves an ordering assumption nobody wrote down.
7. **Use `IBufferedPublisher` and `IBufferedSubscriber` for latest-value-on-subscribe semantics** — a settings-changed notification a late-joining panel needs immediately — rather than hand-caching the last value and replaying it, which duplicates the buffer and drifts from it.
8. **Implement cross-cutting handler behaviour as a filter, not as a copy in each handler** — this is Open/Closed from `coding-principles.md` applied to middleware: a new concern adds a filter instead of editing every subscriber.
9. **Give every subscription a disposal path, aggregated in a `DisposableBag` when one owner holds several** — an undisposed subscription is the dangling handler `coding-principles.md`'s Event handlers section forbids and `performance-and-algorithms.md`'s Memory discipline section explains the cost of. Enable MessagePipe's optional analyzer so a missing `Dispose()` fails at compile time rather than in a long session.
10. **Ask when it is unclear whether the requirement is one event or an observed value** — the two look alike in a feature description and diverge completely in implementation, so guessing produces either a subject-shaped bus or a per-frame publish storm.

## 5. Specific goals / tasks this skill performs
- Design a message type and choose keyless or keyed dispatch for a specific decoupling need.
- Design a request/response contract through `IRequestHandler<TRequest,TResponse>` or `IRequestAllHandler`.
- Write filter middleware for logging, validation, and exception boundaries around a message type.
- Choose buffered pub/sub where a late subscriber needs the current value.
- Audit subscription disposal and enable the analyzer that catches the omissions.
- Out of scope: continuous reactive streams (`r3-reactive-extensions`), the async body of a handler (`unitask-async-programming`), DI registration and lifetime (`vcontainer-dependency-injection`), cross-process wire contracts (`magiconion-rpc-networking`).

## 6. Output format
```
## MessagePipe Work — <message name>
- Message type: <record/struct name and payload> — immutable, values only
- Routing: keyless / keyed (<key type>) — <why keyed, if keyed>
- Pattern: publish-subscribe / request-response / buffered — <why>
- Re-entrancy: no handler republishes this type — confirmed
- Exception boundary: filter applied — <name> | single subscriber, not applicable
- Async: synchronous / IAsyncPublisher-IAsyncSubscriber — strategy: parallel / sequential, <why>
- Filters applied: <list with purpose> | none
- Disposal: DisposableBag owned by <scope> — analyzer enabled: yes/no
- Registered via: RegisterMessagePipe() — scope owned by vcontainer-dependency-injection
- Layer: Game.Client.*
- Known limitations: <...>
```

**Extended report — emit ONLY when the requester asks for it.** It replaces the one-line `Known limitations` above with all three fields:
```
- Known limitations: <what this contract does not cover — ordering, delivery guarantees, replay depth>
- Latent concerns: <what holds only while subscriber count, handler cost, or publish rate stays as it is>
- Future remediation: <the trigger for each — a new subscriber, an async handler, a rate increase>
```

## 7. Examples
**Example 1**
- Input: inventory, a UI toast, and analytics must all react when an item is picked up, with no direct references between them.
- Output: `readonly record struct ItemPickedUp(int ItemId, int Quantity)` published through a keyless `IPublisher<ItemPickedUp>`, registered via `RegisterMessagePipe()`. Each system subscribes independently and disposes through a `DisposableBag` tied to its own scope. An exception-boundary filter wraps the message so a failure in analytics cannot stop inventory from updating.

**Example 2**
- Input: "publish the player's health every frame so the boss AI can react when it drops below a threshold."
- Output: declined as specified. A continuously observed value that a subscriber filters is `r3-reactive-extensions` — `healthProperty.Where(h => h < threshold).DistinctUntilChanged()` expresses the threshold crossing directly. Publishing every frame would put a dispatch on every subscriber sixty times a second to communicate a state change that happens once. Recommended a single `PlayerHealthCritical` message published at the moment the threshold is actually crossed.

**Example 3**
- Input: after adding an analytics subscriber, inventory stopped updating on pickup, with no error surfacing in gameplay code.
- Output: root cause was synchronous dispatch order. The analytics handler threw on a null field, the exception propagated back to the publisher, and every subscriber after it in the chain never ran — so two systems that were supposed to be independent were in fact coupled through dispatch order. Fixed with an exception-boundary filter on the message type, which logs and contains a handler fault so the remaining subscribers still run. The null field was fixed separately.

## 8. Edge cases & guardrails
- Never publish a mutable reference as a payload — messages are snapshots subscribers cannot corrupt for each other.
- Never publish a message type from inside its own handler, per §4 — synchronous dispatch is re-entrant and will recurse.
- Never ship a multi-subscriber message without an exception boundary — one throwing handler silently disables every subscriber after it.
- Never default to a keyed channel without a real multi-channel routing need — that is complexity with no router behind it.
- Never use request/response to avoid declaring a dependency two systems already have — it hides the coupling instead of removing it.
- Never leave a subscription undisposed — aggregate in a `DisposableBag` and dispose on the owning scope's teardown.
- Never model a client-to-server wire message here — MessagePipe is in-process only.
- If it is unclear whether the requirement is one event or an observed value, ask — the two diverge completely in implementation.

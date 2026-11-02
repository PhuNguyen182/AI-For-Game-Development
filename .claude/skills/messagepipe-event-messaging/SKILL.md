---
name: messagepipe-event-messaging
description: "MessagePipe: keyed publishers/subscribers, async handlers, filters, VContainer. Use when features talk decoupled."
user-invocable: false
---

# MessagePipe — In-Process Event Messaging

- **Not for:** continuous streams a subscriber composes over time (`r3-reactive-extensions`).
  - **They pair:** a pipeline's terminal `Subscribe` can publish once.
- **Not for:** the async body of a handler (`unitask-async-programming`).
- **Not for:** registration and lifetime scope (`vcontainer-dependency-injection`, owns `RegisterMessagePipe()`).
- **Not for:** events a designer wires as assets in the Inspector (`unity-scriptableobject-architecture`).
  - **The test:** are publisher and subscriber both code?
- **Not for:** cross-process contracts (`magiconion-rpc-networking`).
  - **Why:** MessagePipe never leaves the process.
- **Docs:** https://github.com/Cysharp/MessagePipe

## Steps
1. **Message = immutable snapshot of values:**
   - **Shape:** e.g. a `readonly struct` with get-only properties set in the constructor.
   - **`record struct`:** C# 10; Unity 6.0 compiles C# 9, per `csharp.md`.
   - **Casing:** per `naming-convention.md`.
   - **Why:** a mutable reference lets one subscriber corrupt what others receive.
2. **Keyless before keyed:**
   - **Keyed:** only for independent channels of the same shape needing separate routing (per-player-slot events).
   - **One key:** YAGNI.
3. **Request/response only for a genuine query (`IRequestHandler<TRequest,TResponse>`, `IRequestAllHandler`):**
   - **Two systems meant to be coupled:** take an injected interface; the bus would only hide the dependency.
4. **Synchronous publish is re-entrant:** never publish a message type from inside its own handler (unbounded recursion).
   - **Instead:** publish a different message or defer.
5. **Multiple independent subscribers:** use an exception-boundary filter.
   - **Why:** a throwing handler propagates to the publisher and later subscribers never run, silently re-coupling them.
6. **`IAsyncPublisher`/`IAsyncSubscriber` only when a handler awaits; set the strategy explicitly:**
   - **Parallel:** for independent handlers.
   - **Sequential:** when order matters.
7. **`IBufferedPublisher`/`IBufferedSubscriber` for latest-value-on-subscribe (late-joining panel needs current setting):**
   - **Hand-caching and replaying:** don't.
8. **Cross-cutting handler behaviour (logging, validation, exception bounds) is a filter:** not a copy per handler.
9. **Every subscription has a disposal path:** aggregated in a `DisposableBag` per owner (`coding-principles.md` → Event handlers).
   - **Analyzer:** enable MessagePipe's analyzer so a missing `Dispose()` fails at compile time.
10. **One event or an observed value unclear:** `Needs-decision`, `Next: technical-architect`.
    - **Why:** guessing yields a subject-shaped bus or a per-frame publish storm.

## Output
```
## MessagePipe Work — <message name>
- Message type: <name and payload> — immutable, values only
- Routing: keyless / keyed (<key type>) — why keyed
- Pattern: publish-subscribe / request-response / buffered — why
- Re-entrancy: no handler republishes this type
- Exception boundary: <filter name> | single subscriber
- Async: synchronous | async — parallel / sequential, why
- Filters: <list with purpose> | none
- Disposal: DisposableBag owned by <scope>; analyzer enabled yes/no
```

## Example
- **"Publish player health every frame so boss AI reacts below a threshold":** declined.
  - **Why:** the threshold is a rule, so Core detects the crossing and raises it.
  - **Did instead:** the client forwards one `PlayerHealthCritical` message.
  - **A health bar observing the value:** `r3-reactive-extensions`.

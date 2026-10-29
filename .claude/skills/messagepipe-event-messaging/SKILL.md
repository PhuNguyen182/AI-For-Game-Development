---
name: messagepipe-event-messaging
description: "MessagePipe in-process messaging: keyed/keyless publishers and subscribers, async handlers, request/response, filters, VContainer setup, disposal. Use when features must talk without direct references."
user-invocable: false
---

# MessagePipe — In-Process Event Messaging

Not for: continuous streams a subscriber composes over time (`r3-reactive-extensions`; they pair, a pipeline's terminal `Subscribe` can publish once), the async body of a handler (`unitask-async-programming`), registration and lifetime scope (`vcontainer-dependency-injection`, owns `RegisterMessagePipe()`), events a designer wires as assets in the Inspector (`unity-scriptableobject-architecture` — test: are publisher and subscriber both code?), cross-process contracts (`magiconion-rpc-networking`; MessagePipe never leaves the process).
Docs: https://github.com/Cysharp/MessagePipe

## Steps
1. **Message = immutable snapshot of values**, e.g. a `readonly struct` with get-only properties set in the constructor (`record struct` is C# 10; Unity 6.0 compiles C# 9, per `csharp.md`), casing per `naming-convention.md`. A mutable reference lets one subscriber corrupt what others receive.
2. **Keyless before keyed** — keyed only for independent channels of the same shape needing separate routing (per-player-slot events). One key is YAGNI.
3. **Request/response only for a genuine query** (`IRequestHandler<TRequest,TResponse>`, `IRequestAllHandler`). Two systems meant to be coupled take an injected interface; the bus would only hide the dependency.
4. **Synchronous publish is re-entrant** — never publish a message type from inside its own handler (unbounded recursion). Publish a different message or defer.
5. **Multiple independent subscribers → exception-boundary filter** — a throwing handler propagates to the publisher and later subscribers never run, silently re-coupling them.
6. **`IAsyncPublisher`/`IAsyncSubscriber` only when a handler awaits; set the strategy explicitly** — parallel for independent handlers, sequential when order matters.
7. **`IBufferedPublisher`/`IBufferedSubscriber` for latest-value-on-subscribe** (late-joining panel needs current setting); don't hand-cache and replay.
8. **Cross-cutting handler behaviour (logging, validation, exception bounds) is a filter**, not a copy per handler.
9. **Every subscription has a disposal path**, aggregated in a `DisposableBag` per owner (`coding-principles.md` → Event handlers). Enable MessagePipe's analyzer so a missing `Dispose()` fails at compile time.
10. **One event or an observed value unclear → `Needs-decision`, `Next: technical-architect`** — guessing yields a subject-shaped bus or a per-frame publish storm.

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
- Known limitations: <...>
```
On request only, add `Latent concerns` and `Future remediation`, each with its trigger.

## Example
- "Publish player health every frame so boss AI reacts below a threshold" → declined: the threshold is a rule, so Core detects the crossing and raises it; the client forwards one `PlayerHealthCritical` message. A health bar observing the value is `r3-reactive-extensions`.

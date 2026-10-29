---
name: dotnet-concurrency-and-async
description: ".NET concurrency: Task, ValueTask, async/await, CancellationToken, TaskCompletionSource, IAsyncEnumerable, Channel<T>, Parallel.ForEach, lock, SemaphoreSlim, Interlocked, ConfigureAwait. Use for async or cross-thread code outside Unity's PlayerLoop."
user-invocable: false
---

# .NET Concurrency and Async

Not for: Unity PlayerLoop-native async (`unitask-async-programming`), reactive push streams (`r3-reactive-extensions`), Burst/Job System bulk parallelism (`unity-job-system-and-burst`), which collection or buffer the shared state lives in (`dotnet-memory-and-collections`; this skill owns only the coordinating primitive).
Docs: https://learn.microsoft.com/en-us/dotnet/csharp/asynchronous-programming/ and https://learn.microsoft.com/en-us/dotnet/api/ — API pages pinned `?view=netstandard-2.1`, the surface Unity's default Api Compatibility Level ships. Check Player Settings against it before using a newer member (`System.Threading.Lock`, `Parallel.ForEachAsync`, `Channel<T>` availability).

| Reference | Read when |
|---|---|
| [task-types-and-combinators.md](references/task-types-and-combinators.md) | Choosing a return type, bridging a callback API, `WhenAll`/`WhenAny` |
| [cancellation-and-async-streams.md](references/cancellation-and-async-streams.md) | Adding cancellation or a timeout, streaming results, deciding `ConfigureAwait` |
| [channels-and-parallel-multithreading.md](references/channels-and-parallel-multithreading.md) | A producer/consumer pipeline, a CPU-bound loop, or shared mutable state |

## Steps
1. **Confirm the code has no UnityEngine dependency and is not PlayerLoop-driven** — `Game.Core.*`, `Game.Server.*` and SDK wrappers stay on the BCL; PlayerLoop work goes to `unitask-async-programming`.
2. **Default to `Task`/`Task<TResult>`**; `ValueTask<TResult>` only after profiling shows allocation pressure on a hot, often-synchronous call ([task-types-and-combinators.md](references/task-types-and-combinators.md)).
3. **Accept a `CancellationToken` on any method long enough to need cancelling**; combine a timeout with the caller's token via `CancellationTokenSource.CreateLinkedTokenSource`, not a bespoke flag ([cancellation-and-async-streams.md](references/cancellation-and-async-streams.md)).
4. **`ConfigureAwait(false)` on every `await` in library-style code** (CA2007); omit it only in entry-point/UI-affinity code that must resume on its context.
5. **Stream paged or unbounded sequences with `IAsyncEnumerable<T>`/`await foreach`**, not a buffered `List<T>`.
6. **Hand off producer to consumer with `Channel<T>`** (bounded unless the producer cannot outrun the consumer), not a hand-rolled queue plus lock. `Parallel.For`/`ForEach` only for CPU-bound work where a measurement beats the sequential loop ([channels-and-parallel-multithreading.md](references/channels-and-parallel-multithreading.md)).
7. **Protect shared state with the lightest primitive** — `Interlocked` for one counter/flag, `lock` for a short section, `SemaphoreSlim.WaitAsync` when the section awaits.
8. **Cross into `Game.Client.*` with UniTask interop** — `.AsUniTask()` on the Core `Task`, `.AsTask()` for the reverse; `unitask-async-programming` owns `PlayerLoopTiming` placement.
9. **No required timeout, cancellation or concurrency bound in the Tech Spec** — ask rather than guess one.

## Never
- Block on async code with `.Result`/`.Wait()` in Core or SDK wrapper code — deadlocks under a synchronization context; await end-to-end or bridge with `TaskCompletionSource<TResult>`.
- Put UniTask or any UnityEngine-adjacent type inside `Game.Core.*` — breaks Shared Core; interop lives at the `Game.Client.*` boundary.
- Add `Parallel`, `Channel<T>` or a lock "just in case" — unmeasured concurrency is speculative complexity.

## Output
```
## .NET Concurrency & Async — <feature/module>
- Return type: <Task / Task<TResult> / ValueTask<TResult> — why>
- Cancellation: <token parameter, linked timeout, or n/a>
- ConfigureAwait: <false in library code / omitted at entry point>
- Primitive: <Channel<T> / Parallel / lock / SemaphoreSlim / Interlocked, or n/a>
- UniTask interop: <boundary used, or n/a>
- Runtime compatibility: <Api Compatibility Level checked against netstandard-2.1>
- Known limitations: <...>
```
On request only, add `Latent concerns` and `Future remediation`, each with its trigger.

## Example
- "ConfigureAwait doesn't matter in our SDK wrapper, just await" → declined: the wrapper is library code with no known context at its call sites; CA2007 flags exactly this and it can deadlock a future caller.

---
name: dotnet-concurrency-and-async
description: ".NET Task, ValueTask, CancellationToken, Channel<T>, SemaphoreSlim, Interlocked. Use for async outside PlayerLoop."
user-invocable: false
---

# .NET Concurrency and Async

- **Not for:** Unity PlayerLoop-native async (`unitask-async-programming`).
- **Not for:** reactive push streams (`r3-reactive-extensions`).
- **Not for:** Burst/Job System bulk parallelism (`unity-job-system-and-burst`).
- **Not for:** which collection or buffer the shared state lives in (`dotnet-memory-and-collections`); this skill owns only the coordinating primitive.
- **Docs:** https://learn.microsoft.com/en-us/dotnet/csharp/asynchronous-programming/ and https://learn.microsoft.com/en-us/dotnet/api/
  - **API pages:** pinned `?view=netstandard-2.1`, the surface Unity's default Api Compatibility Level ships.
  - **Version caveat:** check Player Settings against it before using a newer member (`System.Threading.Lock`, `Parallel.ForEachAsync`, `Channel<T>` availability).

## References
- **[task-types-and-combinators.md](references/task-types-and-combinators.md):** Choosing a return type, bridging a callback API, `WhenAll`/`WhenAny`.
- **[cancellation-and-async-streams.md](references/cancellation-and-async-streams.md):** Adding cancellation or a timeout, streaming results, deciding `ConfigureAwait`.
- **[channels-and-parallel-multithreading.md](references/channels-and-parallel-multithreading.md):** A producer/consumer pipeline, a CPU-bound loop, or shared mutable state.

## Scripts
- **[BridgeCallbackAsync.cs](scripts/BridgeCallbackAsync.cs):** adapt into `<Feature>/Server/<SdkWrapper>.cs` or an IO/service wrapper outside the PlayerLoop → a callback API awaited as a `Task`.
  - **Form:** a private static method of that class, bridged through `TaskCompletionSource`.

## Steps
1. **Confirm the code has no UnityEngine dependency and is not PlayerLoop-driven:** `<Feature>/Server` code and IO/service wrappers outside the PlayerLoop use the BCL.
   - **Unity-side SDK wrappers and PlayerLoop work:** go to `unitask-async-programming`.
   - **Core rules:** stay synchronous and tick-driven, because async resumption order is not deterministic.
2. **Default to `Task`/`Task<TResult>`:** `ValueTask<TResult>` only after profiling shows allocation pressure on a hot, often-synchronous call ([task-types-and-combinators.md](references/task-types-and-combinators.md)).
3. **Accept a `CancellationToken` on any method long enough to need cancelling:** per [cancellation-and-async-streams.md](references/cancellation-and-async-streams.md).
   - **Timeout:** combine it with the caller's token via `CancellationTokenSource.CreateLinkedTokenSource`, not a bespoke flag.
4. **`ConfigureAwait(false)` on every `await` in library-style code (CA2007):** omit it only in entry-point/UI-affinity code that must resume on its context.
5. **Stream paged or unbounded sequences with `IAsyncEnumerable<T>`/`await foreach`:** not a buffered `List<T>`.
6. **Hand off producer to consumer with `Channel<T>`:** bounded unless the producer cannot outrun the consumer, not a hand-rolled queue plus lock ([channels-and-parallel-multithreading.md](references/channels-and-parallel-multithreading.md)).
   - **`Parallel.For`/`ForEach`:** only for CPU-bound work where a measurement beats the sequential loop.
7. **Protect shared state with the lightest primitive:** `Interlocked` for one counter/flag, `lock` for a short section, `SemaphoreSlim.WaitAsync` when the section awaits.
8. **Cross into Client code with UniTask interop:** `.AsUniTask()` on the service/server `Task`, `.AsTask()` for the reverse.
   - **Placement:** `unitask-async-programming` owns `PlayerLoopTiming` placement.
9. **No required timeout, cancellation or concurrency bound in the Tech Spec → `Needs-decision`, `Next: technical-architect`:** rather than guess one.

## Never
- **Blocking on async code:** with `.Result`/`.Wait()` in Core or SDK wrapper code — deadlocks under a synchronization context; await end-to-end or bridge with `TaskCompletionSource<TResult>`.
- **UniTask inside Core:** putting UniTask or any UnityEngine-adjacent type inside a Core assembly breaks Shared Core; interop lives at the Client code boundary.
- **Speculative concurrency:** adding `Parallel`, `Channel<T>` or a lock "just in case" — unmeasured concurrency is speculative complexity.

## Output
```
## .NET Concurrency & Async — <feature/module>
- Return type: <Task / Task<TResult> / ValueTask<TResult> — why>
- Cancellation: <token parameter, linked timeout, or n/a>
- ConfigureAwait: <false in library code / omitted at entry point>
- Primitive: <Channel<T> / Parallel / lock / SemaphoreSlim / Interlocked, or n/a>
- UniTask interop: <boundary used, or n/a>
- Runtime compatibility: <Api Compatibility Level checked against netstandard-2.1>
```

## Example
- **"ConfigureAwait doesn't matter in our SDK wrapper, just await":** declined — the wrapper is library code with no known context at its call sites.
  - **Why:** CA2007 flags exactly this and it can deadlock a future caller.

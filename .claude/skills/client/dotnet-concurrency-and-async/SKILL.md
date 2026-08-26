---
name: dotnet-concurrency-and-async
description: >
  Concurrency and asynchronous programming in pure .NET — Task, Task<TResult>,
  async/await, ValueTask, ValueTask<TResult>, CancellationToken,
  CancellationTokenSource, TaskCompletionSource<TResult>, IAsyncEnumerable<T>,
  System.Threading.Channels' Channel<T>, System.Threading.Tasks.Parallel.For,
  Parallel.ForEach, lock, Monitor, SemaphoreSlim, Interlocked. Use when writing
  async I/O, cooperative cancellation, producer/consumer pipelines, CPU-bound
  parallel loops, or thread-safe shared state in Game.Core.*, Game.Server.*,
  or an SDK/platform wrapper with no UnityEngine dependency — including
  bridging that code into Unity's PlayerLoop. Not for: Unity PlayerLoop-native
  async (`unitask-async-programming`), reactive push streams
  (`r3-reactive-extensions`), Burst/Job System bulk parallelism
  (`unity-job-system-and-burst`).
---

# .NET Concurrency and Async — Task, Cancellation, Channels, Parallel, and Threading Primitives

## Bundled resources

### References
Read-only context, loaded on demand so SKILL.md itself stays short.

| File | Contents | Read when |
|---|---|---|
| [root-links.md](references/root-links.md) | Doc/API root links and version pin for this skill | starting any task in this domain |
| [task-types-and-combinators.md](references/task-types-and-combinators.md) | Task/Task<TResult>/ValueTask<TResult>/TaskCompletionSource<TResult>, WhenAll/WhenAny | choosing an async method's return type or bridging a callback API |
| [cancellation-and-async-streams.md](references/cancellation-and-async-streams.md) | CancellationToken/CancellationTokenSource, IAsyncEnumerable<T>, ConfigureAwait/CA2007 | adding cancellation, streaming results, or deciding ConfigureAwait |
| [channels-and-parallel-multithreading.md](references/channels-and-parallel-multithreading.md) | Channel<T>, Parallel.For/ForEach/ForEachAsync, lock/SemaphoreSlim/Interlocked | a producer/consumer pipeline, a CPU-bound loop, or shared mutable state |

## 1. Objective
Guarantee that async and concurrent C# code in `Game.Core.*`, `Game.Server.*`, and SDK/platform wrappers is cancellable, doesn't deadlock, and doesn't allocate or synchronize more than the workload actually needs — without pulling a Unity or PlayerLoop dependency into code that must stay engine-agnostic. Prevents: caller-uncancellable long-running operations, `ConfigureAwait` deadlocks in library code, unbounded producer/consumer queues, and reaching for `Parallel`/locks/channels where a plain sequential call was correct.

## 2. Role
Act as the .NET concurrency specialist for the client track — the tool reached for whenever Shared Core, a server-authoritative wrapper, or a third-party SDK integration needs async I/O, cancellation, a producer/consumer handoff, or thread-safe shared state, independent of Unity's engine loop.

## 3. When to invoke this skill
- Writing an async method in `Game.Core.*`/`Game.Server.*` that must return `Task`/`Task<TResult>` and support cancellation.
- Wrapping a third-party SDK's callback-based completion API (ad mediation, IAP, platform SDK) into something awaitable.
- Building a producer/consumer pipeline, a paged/streaming async data source, or a CPU-bound parallel loop outside Unity's Job System.
- Protecting state that multiple threads genuinely read/write concurrently.
- Negative trigger: the async work is driven by Unity's PlayerLoop/MonoBehaviour lifecycle (coroutines, per-frame update timing) — that's `unitask-async-programming`.
- Negative trigger: a reactive, push-based event stream (subscribe/observe semantics) — that's `r3-reactive-extensions`.
- Negative trigger: Burst-compiled bulk simulation over `NativeArray<T>` — that's `unity-job-system-and-burst`.

## 4. How to use this skill
1. **Confirm the code has no UnityEngine dependency and isn't driven by Unity's PlayerLoop before reaching for raw `System.Threading.Tasks` types** — `Game.Core.*` and SDK/platform wrappers stay on the BCL; PlayerLoop-integrated work belongs to `unitask-async-programming` instead, per `naming-convention.md`'s namespace boundary.
2. **Default every async method to `Task`/`Task<TResult>`, and reach for `ValueTask`/`ValueTask<TResult>` only once profiling shows allocation pressure from a hot, frequently-synchronously-completing call**, per [task-types-and-combinators.md](references/task-types-and-combinators.md).
3. **Accept a `CancellationToken` parameter on every asynchronous method that can run long enough to need cancellation, and link an internal timeout token with a caller-supplied one via `CancellationTokenSource.CreateLinkedTokenSource` rather than inventing a bespoke flag**, per [cancellation-and-async-streams.md](references/cancellation-and-async-streams.md).
4. **Call `ConfigureAwait(false)` on every `await` inside library-style code with no UI/game-loop synchronization context to return to** — avoids the CA2007 deadlock risk described in [cancellation-and-async-streams.md](references/cancellation-and-async-streams.md); skip it only in true entry-point/UI-affinity code that must resume on the original context.
5. **Stream a paged or unbounded asynchronous sequence with `IAsyncEnumerable<T>`/`await foreach` instead of buffering it into a `List<T>` first**, per [cancellation-and-async-streams.md](references/cancellation-and-async-streams.md).
6. **Hand off data between an async producer and an async consumer through `System.Threading.Channels.Channel<T>` rather than a hand-rolled queue plus lock**, per [channels-and-parallel-multithreading.md](references/channels-and-parallel-multithreading.md); reserve `Parallel.For`/`Parallel.ForEach` for CPU-bound bulk work where a measurement shows the partitioning overhead pays off, never as a default replacement for a sequential loop.
7. **Protect shared mutable state with the lightest primitive the contention pattern actually needs** — `Interlocked` for a single counter/flag, `lock`/`System.Threading.Lock` for a short critical section, `SemaphoreSlim`/`WaitAsync` for bounding concurrent access from async code, per [channels-and-parallel-multithreading.md](references/channels-and-parallel-multithreading.md).
8. **Bridge into Unity's PlayerLoop through UniTask's `.AsUniTask()`/`.AsTask()` extension methods instead of re-deriving the async logic in `Game.Client.*`** — `.AsUniTask()` wraps the `Task`/`Task<TResult>` this skill returns from `Game.Core.*`/`Game.Server.*` so `Game.Client.*` can await it on Unity's `PlayerLoop` instead of blocking a thread-pool thread, and `.AsTask()` exposes a `Game.Client.*`-side `UniTask` back out to a `Task`-based contract when the direction reverses; `unitask-async-programming` owns the resulting `PlayerLoopTiming` placement and the struct-based, pooled-promise allocation profile on that side.
9. **Verify the target Unity scripting runtime actually ships the API before using it** — confirm Player Settings' Api Compatibility Level against the `netstandard-2.1` pin in [root-links.md](references/root-links.md), per `coding-principles.md`'s Modern C# syntax section; if the Tech Spec doesn't specify a required cancellation/timeout or concurrency pattern, ask rather than guessing one.

## 5. Specific goals / tasks this skill performs
- Implement `Task`/`Task<TResult>`-returning async methods in `Game.Core.*`/`Game.Server.*`/SDK wrappers with correct naming, cancellation, and exception propagation.
- Bridge a callback-based third-party SDK API into an awaitable `Task<TResult>` via `TaskCompletionSource<TResult>`.
- Build a producer/consumer pipeline with `Channel<T>`, or a measured, bounded-concurrency CPU-bound loop with `Parallel.For`/`ForEach`/`ForEachAsync`.
- Protect genuinely shared mutable state with the lightest correct primitive (`Interlocked`/`lock`/`SemaphoreSlim`).
- Bridge a `Task`-returning `Game.Core.*`/`Game.Server.*` method to Unity's PlayerLoop via UniTask interop when `Game.Client.*` needs to await it.
- Out of scope: Unity PlayerLoop-native async/coroutines (`unitask-async-programming`), reactive push-based event streams (`r3-reactive-extensions`), Burst-compiled Job System bulk parallelism (`unity-job-system-and-burst`).

## 6. Output format
```
## .NET Concurrency & Async Work — <feature/module name>
- Return type: Task / Task<TResult> / ValueTask<TResult> — rationale
- Cancellation: CancellationToken parameter, linked-token usage — or "not applicable"
- ConfigureAwait: false in library code / omitted in UI-affinity code — confirmed
- Concurrency primitive: Channel<T> / Parallel.For(Each) / lock / SemaphoreSlim / Interlocked — or "not applicable"
- UniTask interop: Task<->UniTask bridging used at the Game.Client.* boundary — or "not applicable"
- Runtime compatibility: Api Compatibility Level checked against netstandard-2.1
- Layer: Game.Core.* / Game.Server.* / Game.Client.* (SDK wrapper)
- Known limitations: <...>
```

**Extended report — emit ONLY when the requester asks for it.**
```
- Known limitations: <what the delivered solution does not cover — omit if genuinely none>
- Latent concerns: <assumptions that hold only under current load/thread-count, deferred trade-offs>
- Future remediation: <the concrete fix for each concern, with the condition that should trigger it>
```

## 7. Examples
**Example 1**
- Input: Tech Spec asks for a cancellable async inventory load from a remote save-data endpoint in `Game.Core`, honoring both a hard 10-second timeout and a player-initiated cancel.
- Output: `GetInventoryAsync(CancellationToken)` returns `Task<InventoryState>`; an internal 10s `CancellationTokenSource` is linked with the caller's token via `CreateLinkedTokenSource`; every internal `await` uses `ConfigureAwait(false)`; `Game.Client.*` awaits it through UniTask's `.AsUniTask()` to stay on `PlayerLoopTiming.Update`, per [task-types-and-combinators.md](references/task-types-and-combinators.md) and [cancellation-and-async-streams.md](references/cancellation-and-async-streams.md).

**Example 2**
- Input: "just await the Task directly in our SDK wrapper, ConfigureAwait doesn't matter for us."
- Output: declined — the wrapper is library code with no synchronization-context guarantee at its call site; CA2007 flags exactly this omission, and it can deadlock a future caller running under a context, per [cancellation-and-async-streams.md](references/cancellation-and-async-streams.md).

**Example 3**
- Input: 5,000 loaded item definitions each need an expensive per-item validation pass before the level can start.
- Output: `Parallel.ForEach` over the definitions with `ParallelOptions.MaxDegreeOfParallelism` bounded and measured against a sequential baseline before shipping, per [channels-and-parallel-multithreading.md](references/channels-and-parallel-multithreading.md)'s Critical caveat.

## 8. Edge cases & guardrails
- Never block on async code with `.Result`/`.Wait()` in `Game.Core.*`/SDK wrapper code — a classic deadlock source when a synchronization context is present; bridge with `TaskCompletionSource<TResult>` or await end-to-end instead.
- Never reintroduce UniTask (or any UnityEngine-adjacent type) inside `Game.Core.*` — that breaks Shared Core's no-UnityEngine-dependency requirement; UniTask interop belongs at the `Game.Client.*` boundary only, per `naming-convention.md`'s namespace boundary.
- Never reach for `Parallel.For`/`ForEach`, `Channel<T>`, or a hand-rolled lock as a default "just in case" — each carries real overhead with no measured concurrency need, which is speculative complexity YAGNI already forbids, per `performance-and-algorithms.md`'s Verification section.
- If the Tech Spec doesn't state whether an operation needs a caller-supplied timeout vs. only caller cancellation, or what concurrency bound a parallel loop should use, ask rather than guessing a default.

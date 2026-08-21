# Channels, Parallel Loops, and Multithreading Primitives — Channel&lt;T&gt;, Parallel, lock, SemaphoreSlim, Interlocked

Source: [Channel Class](https://learn.microsoft.com/en-us/dotnet/api/system.threading.channels.channel?view=netstandard-2.1), [Data Parallelism (Task Parallel Library)](https://learn.microsoft.com/en-us/dotnet/standard/parallel-programming/data-parallelism-task-parallel-library), [Parallel Class](https://learn.microsoft.com/en-us/dotnet/api/system.threading.tasks.parallel?view=netstandard-2.1), [Interlocked Class](https://learn.microsoft.com/en-us/dotnet/api/system.threading.interlocked?view=netstandard-2.1), [SemaphoreSlim Class](https://learn.microsoft.com/en-us/dotnet/api/system.threading.semaphoreslim?view=netstandard-2.1), [The lock statement](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/statements/lock).
Covers: SKILL.md §4 — **"Hand off data between an async producer and an async consumer through `System.Threading.Channels.Channel<T>` rather than a hand-rolled queue plus lock"**, **"Protect shared mutable state with the lightest primitive the contention pattern actually needs"**.

Producer/consumer handoff, CPU-bound data parallelism, and picking the
cheapest correct synchronization primitive for shared mutable state.
`unity-job-system-and-burst` owns the equivalent decision once the work is
Burst-compiled bulk simulation over `NativeArray<T>`.

## Producer/consumer handoff

| Member | What it decides | Source |
|---|---|---|
| `Channel.CreateUnbounded<T>()` | Any number of producers/consumers, no backpressure; the queue grows without bound if consumers fall behind. | [Channel Class](https://learn.microsoft.com/en-us/dotnet/api/system.threading.channels.channel?view=netstandard-2.1) |
| `Channel.CreateBounded<T>(capacity)` | Caps queued items and applies backpressure once full — the correct default over unbounded whenever the producer can outrun the consumer. | [Channel Class](https://learn.microsoft.com/en-us/dotnet/api/system.threading.channels.channel?view=netstandard-2.1) |
| `ChannelWriter<T>.WriteAsync` / `ChannelReader<T>.ReadAllAsync` | Async-native write/read that composes with `await foreach` and `CancellationToken`, replacing a hand-rolled queue plus lock plus signal. | [Channel Class](https://learn.microsoft.com/en-us/dotnet/api/system.threading.channels.channel?view=netstandard-2.1) |

## CPU-bound data parallelism

| Member | What it decides | Source |
|---|---|---|
| `Parallel.For` / `Parallel.ForEach` | Partitions a loop's iterations across the thread pool; the TPL handles scheduling — don't manage threads manually. | [Data Parallelism (Task Parallel Library)](https://learn.microsoft.com/en-us/dotnet/standard/parallel-programming/data-parallelism-task-parallel-library) |
| `Parallel.ForEachAsync` | Runs an async body per element with bounded concurrency (`ParallelOptions.MaxDegreeOfParallelism`) instead of firing every task at once. | [Parallel Class](https://learn.microsoft.com/en-us/dotnet/api/system.threading.tasks.parallel?view=netstandard-2.1) |
| `ParallelOptions.CancellationToken` | Lets an in-flight parallel loop observe cancellation, using the same token model as the rest of this skill. | [Data Parallelism (Task Parallel Library)](https://learn.microsoft.com/en-us/dotnet/standard/parallel-programming/data-parallelism-task-parallel-library) |

**Critical caveat**: `Parallel.For`/`ForEach` only pays off once the
per-iteration work is expensive enough to outweigh partitioning/scheduling
overhead — measure before replacing a sequential loop, per
`performance-and-algorithms.md`'s Core principle. For Burst-compiled bulk
simulation over `NativeArray<T>`, escalate to `unity-job-system-and-burst`
instead.

## Shared mutable state

| Primitive | Use when | Source |
|---|---|---|
| `Interlocked.Increment` / `CompareExchange` / `Exchange` | A single counter, flag, or reference needs an atomic update — cheaper than a lock for that one operation. | [Interlocked Class](https://learn.microsoft.com/en-us/dotnet/api/system.threading.interlocked?view=netstandard-2.1) |
| `lock` (`System.Threading.Lock` in C# 13+, otherwise a dedicated `object`) | A short critical section spanning more than one field/statement; never lock `this`, a `Type`, or a `string`. | [The lock statement](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/statements/lock) |
| `SemaphoreSlim` + `WaitAsync`/`Release` | Bounding how many callers concurrently enter a section from **async** code — `lock` cannot wrap an `await`. | [SemaphoreSlim Class](https://learn.microsoft.com/en-us/dotnet/api/system.threading.semaphoreslim?view=netstandard-2.1) |

```csharp
private readonly System.Threading.Lock _balanceLock = new();
private int _balance;

public void Credit(int amount)
{
    lock (_balanceLock)
    {
        _balance += amount;
    }
}
```

**Critical caveat**: an `await` cannot appear inside a `lock` body — the
compiler rejects it. Use `SemaphoreSlim.WaitAsync`/`Release` for an
async-safe critical section instead.

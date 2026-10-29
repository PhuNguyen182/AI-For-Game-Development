# Channels, Parallel Loops, Synchronization

Sources: Learn "Channel Class", "Data Parallelism (TPL)", API `Parallel`, `Interlocked`, `SemaphoreSlim` (`?view=netstandard-2.1`), "The lock statement".

## Producer/consumer
- `Channel.CreateUnbounded<T>()`: no backpressure; the queue grows without bound if consumers lag.
- `Channel.CreateBounded<T>(capacity)`: backpressure when full; the default whenever the producer can outrun the consumer.
- `ChannelWriter<T>.WriteAsync` / `ChannelReader<T>.ReadAllAsync` compose with `await foreach` and `CancellationToken`.

## CPU-bound parallelism
- `Parallel.For` / `ForEach`: the TPL partitions across the thread pool; do not manage threads by hand.
- `Parallel.ForEachAsync` (.NET 6+, absent on netstandard 2.1 — server only): async body per element with bounded concurrency via `ParallelOptions.MaxDegreeOfParallelism`. On Unity, bound concurrency with `SemaphoreSlim`.
- `ParallelOptions.CancellationToken` lets a running loop observe cancellation.
- Pays off only when per-iteration work outweighs partitioning overhead: measure against the sequential loop first. Burst-compiled bulk work over `NativeArray<T>` goes to `unity-job-system-and-burst`.

## Shared mutable state

| Primitive | Use when |
|---|---|
| `Interlocked.Increment` / `CompareExchange` / `Exchange` | One counter, flag or reference needs an atomic update |
| `lock` on a dedicated `readonly object` (`System.Threading.Lock` needs .NET 9 — server only) | A short section spanning several fields; never lock `this`, a `Type` or a `string` |
| `SemaphoreSlim` + `WaitAsync`/`Release` | Bounding concurrent entry from async code; `lock` cannot wrap an `await` (compiler error) |

```csharp
private readonly object _balanceLock = new object();
private int _balance;

public void Credit(int amount)
{
    lock (this._balanceLock)
    {
        this._balance += amount;
    }
}
```

# Cancellation and Async Streams — CancellationToken, IAsyncEnumerable&lt;T&gt;, ConfigureAwait

Source: [Cancellation in Managed Threads](https://learn.microsoft.com/en-us/dotnet/standard/threading/cancellation-in-managed-threads), [Generate and consume async streams](https://learn.microsoft.com/en-us/dotnet/csharp/asynchronous-programming/generate-consume-asynchronous-stream), [CA2007: Do not directly await a Task](https://learn.microsoft.com/en-us/dotnet/fundamentals/code-analysis/quality-rules/ca2007).
Covers: SKILL.md §4 — **"Accept a `CancellationToken` parameter on every asynchronous method that can run long enough to need cancellation, and link an internal timeout token with a caller-supplied one via `CancellationTokenSource.CreateLinkedTokenSource` rather than inventing a bespoke flag"**, **"Call `ConfigureAwait(false)` on every `await` inside library-style code with no UI/game-loop synchronization context to return to"**, **"Stream a paged or unbounded asynchronous sequence with `IAsyncEnumerable<T>`/`await foreach` instead of buffering it into a `List<T>` first"**.

Cooperative cancellation, streaming async sequences, and the deadlock risk
`ConfigureAwait(false)` exists to avoid.

## Cancellation

| Member | What it decides | Source |
|---|---|---|
| `CancellationTokenSource` | Owns and issues the cancel request; must be `Dispose`d once the operation is done. | [Cancellation in Managed Threads](https://learn.microsoft.com/en-us/dotnet/standard/threading/cancellation-in-managed-threads) |
| `CancellationToken` | The lightweight value passed to listeners; `IsCancellationRequested` never resets once `true`. | [Cancellation in Managed Threads](https://learn.microsoft.com/en-us/dotnet/standard/threading/cancellation-in-managed-threads) |
| `CancellationTokenSource.CreateLinkedTokenSource` | Joins an internal token (e.g. a hard timeout) and an external caller-supplied token into one; either side can trigger cancellation. | [Cancellation in Managed Threads](https://learn.microsoft.com/en-us/dotnet/standard/threading/cancellation-in-managed-threads) |
| `CancellationToken.ThrowIfCancellationRequested` | Throws `OperationCanceledException` at the exact point cancellation should take effect. | [Cancellation in Managed Threads](https://learn.microsoft.com/en-us/dotnet/standard/threading/cancellation-in-managed-threads) |

## Async streams

| Member | What it decides | Source |
|---|---|---|
| `IAsyncEnumerable<T>` / `await foreach` | Consumes a sequence produced incrementally, without materializing it fully first; bounds memory for a paged/streaming source. | [Generate and consume async streams](https://learn.microsoft.com/en-us/dotnet/csharp/asynchronous-programming/generate-consume-asynchronous-stream) |
| `[EnumeratorCancellation]` on the token parameter of an `async IAsyncEnumerable<T>` iterator | Makes the token passed to `GetAsyncEnumerator` visible inside the iterator body. | [Generate and consume async streams](https://learn.microsoft.com/en-us/dotnet/csharp/asynchronous-programming/generate-consume-asynchronous-stream) |
| `.WithCancellation(token)` | Attaches a cancellation token to the `await foreach` loop itself. | [Generate and consume async streams](https://learn.microsoft.com/en-us/dotnet/csharp/asynchronous-programming/generate-consume-asynchronous-stream) |

```csharp
private static async IAsyncEnumerable<Row> ReadPagesAsync(
    [EnumeratorCancellation] CancellationToken cancellationToken = default)
{
    Page? page;
    while ((page = await FetchNextPageAsync(cancellationToken).ConfigureAwait(false)) is not null)
    {
        foreach (Row row in page.Rows)
            yield return row;
    }
}
```

## ConfigureAwait

| Rule | What it decides | Source |
|---|---|---|
| CA2007 | Directly awaiting a `Task` without `ConfigureAwait` can schedule the continuation back on the original context, which risks a deadlock on a UI/game-loop thread and adds overhead in library code with no such context. | [CA2007: Do not directly await a Task](https://learn.microsoft.com/en-us/dotnet/fundamentals/code-analysis/quality-rules/ca2007) |
| `ConfigureAwait(false)` | Schedules the continuation on the thread pool instead of the captured context — the correct default for `Game.Core.*`/SDK wrapper library code. | [CA2007: Do not directly await a Task](https://learn.microsoft.com/en-us/dotnet/fundamentals/code-analysis/quality-rules/ca2007) |
| `ConfigureAwait(true)` (or omitted) | Explicitly keeps the continuation on the original context — correct only for true UI/game-loop entry points, not for library code. | [CA2007: Do not directly await a Task](https://learn.microsoft.com/en-us/dotnet/fundamentals/code-analysis/quality-rules/ca2007) |

**Critical caveat**: `await` cannot appear inside a `lock` statement's body —
acquire the section with `SemaphoreSlim.WaitAsync` instead when an async
critical section is needed, per
[channels-and-parallel-multithreading.md](channels-and-parallel-multithreading.md).

# Cancellation, Async Streams, ConfigureAwait

Sources: Learn "Cancellation in Managed Threads", "Generate and consume async streams", "CA2007: Do not directly await a Task".

## Cancellation
- `CancellationTokenSource` issues the request; `Dispose` it when the operation is done.
- `CancellationToken` is the value passed to listeners; `IsCancellationRequested` never resets once true.
- `CreateLinkedTokenSource` joins an internal token (hard timeout) with the caller's; either side cancels.
- `ThrowIfCancellationRequested` throws `OperationCanceledException` at the exact point cancellation should take effect.

## Async streams
- `IAsyncEnumerable<T>` / `await foreach` consume incrementally; bound memory for paged or streaming sources.
- `[EnumeratorCancellation]` on the iterator's token parameter exposes the token given to `GetAsyncEnumerator`.
- `.WithCancellation(token)` attaches a token to the `await foreach` itself.

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

## ConfigureAwait (CA2007)
- A bare `await` can resume on the captured context: deadlock risk on a UI/game-loop thread, overhead in library code.
- `ConfigureAwait(false)` resumes on the thread pool; the default for `Game.Server.*` and IO wrappers. Never in code whose continuation touches Unity objects. `Game.Core.*` rules do not await.
- Omitted or `true` is correct only at true UI/game-loop entry points.
- `await` cannot appear in a `lock` body; use `SemaphoreSlim.WaitAsync` ([channels-and-parallel-multithreading.md](channels-and-parallel-multithreading.md)).

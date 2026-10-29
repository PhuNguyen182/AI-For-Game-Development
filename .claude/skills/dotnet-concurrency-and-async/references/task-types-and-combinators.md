# Task Types and Combinators

Sources: Learn "Asynchronous programming - C#", "Task-based Asynchronous Pattern (TAP)", API `ValueTask<TResult>` and `TaskCompletionSource<TResult>` (`?view=netstandard-2.1`).

## Return types

| Type | Use |
|---|---|
| `Task` | Default, no result; allocates once per call |
| `Task<TResult>` | Default, with a result |
| `ValueTask<TResult>` | Only when the result is often available synchronously and the call is hot enough for the allocation to matter |
| `TaskCompletionSource<TResult>` | Wraps a callback API as an awaitable via `SetResult`/`SetException`/`SetCanceled` (or `TrySet*`), without blocking a thread |

A `ValueTask<TResult>` must not be awaited twice, have `AsTask()` called twice, or be read via `.Result`/`.GetAwaiter().GetResult()` before completion; results are undefined.

## Combinators
- `Task.WhenAll`: completes when every task has; aggregates exceptions from all.
- `Task.WhenAny`: completes when the first does; returns that task.

```csharp
static Task<int> BridgeCallbackAsync(ThirdPartySdk sdk)
{
    var tcs = new TaskCompletionSource<int>();
    sdk.OnComplete += result => tcs.TrySetResult(result);
    sdk.OnError += ex => tcs.TrySetException(ex);
    sdk.Start();
    return tcs.Task;
}
```

## TAP conventions
Suffix awaitable methods `Async`, keep the sync counterpart's parameter order. Usage errors (null argument) throw synchronously; every other failure surfaces on the returned `Task`, never both.

# Task Types and Combinators — Task, Task&lt;TResult&gt;, ValueTask&lt;TResult&gt;, TaskCompletionSource&lt;TResult&gt;

Source: [Asynchronous programming - C#](https://learn.microsoft.com/en-us/dotnet/csharp/asynchronous-programming/), [Task-based Asynchronous Pattern (TAP): Introduction and overview](https://learn.microsoft.com/en-us/dotnet/standard/asynchronous-programming-patterns/task-based-asynchronous-pattern-tap), [ValueTask&lt;TResult&gt; Struct](https://learn.microsoft.com/en-us/dotnet/api/system.threading.tasks.valuetask-1?view=netstandard-2.1), [TaskCompletionSource&lt;TResult&gt; Class](https://learn.microsoft.com/en-us/dotnet/api/system.threading.tasks.taskcompletionsource-1?view=netstandard-2.1).
Covers: SKILL.md §4 — **"Default every async method to `Task`/`Task<TResult>`, and reach for `ValueTask`/`ValueTask<TResult>` only once profiling shows allocation pressure from a hot, frequently-synchronously-completing call"**.

Which Task-family return type and combinator to reach for, and how to bridge
a callback-based API into one. `unitask-async-programming` owns the
equivalent return-type decision once the method runs on Unity's PlayerLoop.

## Return types

| Type | What it decides | Source |
|---|---|---|
| `Task` | Default for an async operation with no result; allocates once per call. | [Asynchronous programming - C#](https://learn.microsoft.com/en-us/dotnet/csharp/asynchronous-programming/) |
| `Task<TResult>` | Default for an async operation that produces a value. | [TAP: Introduction and overview](https://learn.microsoft.com/en-us/dotnet/standard/asynchronous-programming-patterns/task-based-asynchronous-pattern-tap) |
| `ValueTask<TResult>` | Avoids the `Task<TResult>` allocation when the result is frequently available synchronously and the call is hot enough for the allocation to matter — never the default; can be awaited, or converted with `AsTask()`, only once. | [ValueTask&lt;TResult&gt; Struct](https://learn.microsoft.com/en-us/dotnet/api/system.threading.tasks.valuetask-1?view=netstandard-2.1) |
| `TaskCompletionSource<TResult>` | Wraps a callback-based API (an SDK completion delegate) as an awaitable `Task<TResult>` via `SetResult`/`SetException`/`SetCanceled`, without blocking a thread. | [TaskCompletionSource&lt;TResult&gt; Class](https://learn.microsoft.com/en-us/dotnet/api/system.threading.tasks.taskcompletionsource-1?view=netstandard-2.1) |

**Critical caveat**: a `ValueTask<TResult>` must never be awaited twice, have
`AsTask()` called twice, or be read via `.Result`/`.GetAwaiter().GetResult()`
before completion — any of these produce undefined results, per the
ValueTask&lt;TResult&gt; Struct remarks above.

## Combinators

| Member | Effect | Use when | Source |
|---|---|---|---|
| `Task.WhenAll` | Completes when every task in the list completes; aggregates exceptions from all of them. | Multiple independent operations must all finish before continuing. | [Asynchronous programming - C#](https://learn.microsoft.com/en-us/dotnet/csharp/asynchronous-programming/) |
| `Task.WhenAny` | Completes when the first task in the list completes; returns that task. | Reacting to whichever of several operations finishes first. | [Asynchronous programming - C#](https://learn.microsoft.com/en-us/dotnet/csharp/asynchronous-programming/) |

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

TAP's naming/exception rules apply to every method this reference covers:
suffix an awaitable method `Async`, keep the parameter order of its
synchronous counterpart, and let usage errors (a null argument) throw
synchronously while every other failure is surfaced on the returned `Task`
— never both.

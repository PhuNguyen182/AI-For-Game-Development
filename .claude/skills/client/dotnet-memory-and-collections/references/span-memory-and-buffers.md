# Span, Memory, and Buffer Pooling — Span&lt;T&gt;, Memory&lt;T&gt;, ArrayPool&lt;T&gt;, stackalloc

Source: [Memory&lt;T&gt; and Span&lt;T&gt; usage guidelines](https://learn.microsoft.com/en-us/dotnet/standard/memory-and-spans/memory-t-usage-guidelines), [Span&lt;T&gt; Struct](https://learn.microsoft.com/en-us/dotnet/api/system.span-1?view=netstandard-2.1), [Memory&lt;T&gt; Struct](https://learn.microsoft.com/en-us/dotnet/api/system.memory-1?view=netstandard-2.1), [ArrayPool&lt;T&gt; Class](https://learn.microsoft.com/en-us/dotnet/api/system.buffers.arraypool-1?view=netstandard-2.1), [stackalloc expression](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/operators/stackalloc).
Covers: SKILL.md §4 — **"Confirm the buffer's lifetime and whether it must cross an `await`/`yield` boundary before picking `Span<T>` vs. `Memory<T>`"**, **"Default a synchronous API's buffer parameter to `Span<T>`/`ReadOnlySpan<T>`"**, **"Rent, don't allocate, for a large or per-call transient buffer in a hot path"**, **"Reserve `stackalloc` for small, bounded-size buffers guarded by an upper-bound check before the allocation"**.

Which buffer type to use for a synchronous vs. async signature, and how to
pool or stack-allocate a transient buffer instead of allocating on the heap
per call.

## Span&lt;T&gt; vs. Memory&lt;T&gt;

| Type | What it decides | Source |
|---|---|---|
| `Span<T>` / `ReadOnlySpan<T>` | A stack-only `ref struct`; cannot be boxed, stored as a field, or used across `await`/`yield`. Fastest option and the default for a synchronous API's buffer parameter. | [Span&lt;T&gt; Struct](https://learn.microsoft.com/en-us/dotnet/api/system.span-1?view=netstandard-2.1) |
| `Memory<T>` / `ReadOnlyMemory<T>` | Can live on the managed heap, be stored as a field, and cross `await`/`yield` boundaries — required whenever the buffer must outlive the current synchronous call. | [Memory&lt;T&gt; Struct](https://learn.microsoft.com/en-us/dotnet/api/system.memory-1?view=netstandard-2.1) |
| `Memory<T>.Span` | Converts a `Memory<T>` to a `Span<T>` for the duration of a synchronous call — the one-way conversion; `Span<T>` cannot convert back to `Memory<T>`. | [Memory&lt;T&gt; and Span&lt;T&gt; usage guidelines](https://learn.microsoft.com/en-us/dotnet/standard/memory-and-spans/memory-t-usage-guidelines) |

**Critical caveat**: a method that accepts `Memory<T>`/`ReadOnlyMemory<T>`
and returns `void` or a completed `Task` must not touch that buffer after
returning — its "lease" ends there. A method that hands the buffer to a
background continuation must either return a `Task` that completes only
after the buffer is done being read, or take a defensive copy first, per the
usage guidelines above.

## Renting instead of allocating

| Member | What it decides | Source |
|---|---|---|
| `ArrayPool<T>.Shared` | The process-wide shared pool — the default choice; thread-safe, no separate pool instance needed. | [ArrayPool&lt;T&gt; Class](https://learn.microsoft.com/en-us/dotnet/api/system.buffers.arraypool-1?view=netstandard-2.1) |
| `ArrayPool<T>.Rent(minimumLength)` | Retrieves an array at least the requested length — may be larger; use the requested length, not `array.Length`, when reading. | [ArrayPool&lt;T&gt; Class](https://learn.microsoft.com/en-us/dotnet/api/system.buffers.arraypool-1?view=netstandard-2.1) |
| `ArrayPool<T>.Return(array, clearArray)` | Returns the array to the pool; pass `clearArray: true` when the buffer held sensitive data that must not leak to the next renter. | [ArrayPool&lt;T&gt; Class](https://learn.microsoft.com/en-us/dotnet/api/system.buffers.arraypool-1?view=netstandard-2.1) |

```csharp
byte[] buffer = ArrayPool<byte>.Shared.Rent(requestedLength);
try
{
    Span<byte> slice = buffer.AsSpan(0, requestedLength);
    FillBuffer(slice);
    Process(slice);
}
finally
{
    ArrayPool<byte>.Shared.Return(buffer);
}
```

## stackalloc

| Rule | What it decides | Source |
|---|---|---|
| Assign to `Span<T>`/`ReadOnlySpan<T>` | No `unsafe` context required; the safe, preferred form. | [stackalloc expression](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/operators/stackalloc) |
| Bound the length before allocating | An unguarded or unbounded `stackalloc` risks `StackOverflowException`; fall back to `ArrayPool<T>` above a fixed size threshold. | [stackalloc expression](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/operators/stackalloc) |
| Never inside a loop | Allocate once outside the loop and reuse the buffer across iterations. | [stackalloc expression](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/operators/stackalloc) |

```csharp
const int MaxStackLimit = 256;
Span<byte> buffer = length <= MaxStackLimit ? stackalloc byte[length] : ArrayPool<byte>.Shared.Rent(length);
```

**Critical caveat**: `stackalloc`-allocated memory is uninitialized — clear
it explicitly (`Span<T>.Clear()` or an initializer) before reading, unlike
`new`, which zero-initializes.

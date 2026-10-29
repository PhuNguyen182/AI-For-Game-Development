# Span, Memory, ArrayPool, stackalloc

## Span vs Memory
| Type | Rule |
|---|---|
| `Span<T>`/`ReadOnlySpan<T>` | Stack-only `ref struct`: no boxing, field storage or use across `await`/`yield`. Fastest; default for synchronous parameters |
| `Memory<T>`/`ReadOnlyMemory<T>` | Heap-capable; required when the buffer outlives the call |
| `Memory<T>.Span` | One-way conversion for a synchronous call; a span cannot become `Memory<T>` |

A method taking `Memory<T>` that returns `void` or a completed `Task` must not touch the buffer afterwards. If it hands the buffer to a background continuation, return a `Task` that completes after the read, or copy first.

## ArrayPool
- `ArrayPool<T>.Shared`: thread-safe default.
- `Rent(min)` may return a larger array: use the requested length, not `array.Length`.
- `Return(array, clearArray)`: pass `true` for sensitive data.

```csharp
byte[] buffer = ArrayPool<byte>.Shared.Rent(requestedLength);
try
{
    Span<byte> slice = buffer.AsSpan(0, requestedLength);
    Process(slice);
}
finally
{
    ArrayPool<byte>.Shared.Return(buffer);
}
```

## stackalloc
- Assign to `Span<T>`/`ReadOnlySpan<T>` (no `unsafe`).
- Bound the length first: unbounded input risks `StackOverflowException` (e.g. player chat text); fall back to the pool.
- Never inside a loop: allocate once and reuse.
- Memory is uninitialised: clear it before reading, unlike `new`.

```csharp
const int MaxStackLimit = 256;
byte[] rented = null;
Span<byte> buf = length <= MaxStackLimit
    ? stackalloc byte[length]
    : (rented = ArrayPool<byte>.Shared.Rent(length)).AsSpan(0, length);
try { /* use buf */ }
finally { if (rented != null) ArrayPool<byte>.Shared.Return(rented); }
```
Keep the `byte[]` reference: a span cannot be returned to the pool.

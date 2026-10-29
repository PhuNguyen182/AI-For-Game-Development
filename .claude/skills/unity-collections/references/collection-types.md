# Collection types

Source: [Collections overview](https://docs.unity3d.com/Packages/com.unity.collections@6.6/manual/collections-overview.html), [Collection types](https://docs.unity3d.com/Packages/com.unity.collections@6.6/manual/collection-types.html), [FixedString128Bytes](https://docs.unity3d.com/Packages/com.unity.collections@6.6/api/Unity.Collections.FixedString128Bytes.html), [FixedList128Bytes<T>](https://docs.unity3d.com/Packages/com.unity.collections@6.6/api/Unity.Collections.FixedList128Bytes-1.html).

## Categories
- `Native-` (`Unity.Collections`): disposal and thread-safety checks; the default.
- `Unsafe-` (`Unity.Collections.LowLevel.Unsafe`): no checks, lower overhead.
- Small non-allocated types: nothing allocated.

A `Native-` collection cannot contain another `Native-` collection; nesting needs the `Unsafe-` counterpart as the inner type.

## Type by access pattern
| Type | Choose when |
|---|---|
| `NativeArray<T>` | Count known at allocation and fixed |
| `NativeList<T>` | Resizable append; final count unknown |
| `NativeHashMap<TKey,TValue>` | Single-threaded key-value lookup, low overhead; default unless a job writes in parallel |
| `NativeParallelHashMap<TKey,TValue>` | Multithreaded writes, higher memory; only for an actual parallel writer |
| `NativeHashSet<T>` | Uniqueness only; no value payload |
| `NativeQueue<T>` | Resizable FIFO |
| `NativeStream` | Append-only, untyped, per-thread buffers; deterministic alternative to `ParallelWriter` |
| `NativeReference<T>` | One value crossing into a job |
| `NativeSlice<T>` | A view over an existing allocation, not an allocation (see aliasing reference) |

## FixedString and FixedList
Contents live inside the struct: no `Allocator`, no `Dispose()`; lifetime is the struct's (stack, or embedded in another unmanaged struct or component).
- `FixedString32/64/128/512/4096Bytes`: inline UTF-8, 2-byte length prefix plus null terminator (`FixedString128Bytes` holds about 125 bytes).
- `FixedList32/64/128/512/4096Bytes<T>`: inline resizable list over unmanaged `T`; capacity is (size minus header) / `sizeof(T)`.

Pick the smallest size that comfortably fits: the whole struct is copied by value on every pass, so a `FixedString4096Bytes` in a hot per-entity struct costs 4 KB per copy even when empty.

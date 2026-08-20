# FixedString & FixedList

Covers SKILL.md step 3 (allocation-free strings/small lists that cross into a job/Burst/ECS boundary).

## API
- [FixedString128Bytes](https://docs.unity3d.com/Packages/com.unity.collections@6.6/api/Unity.Collections.FixedString128Bytes.html) — an unmanaged UTF-8 string stored directly inside the struct itself (no separate allocation), with a 2-byte length prefix and a guaranteed null terminator; ~125 usable bytes at this size. Fully compatible with jobs and Burst since it contains no pointers/managed data. Sibling sizes follow the same pattern: `FixedString32Bytes`, `FixedString64Bytes`, `FixedString512Bytes`, `FixedString4096Bytes` — pick the smallest that comfortably fits the data.
- [FixedList128Bytes\<T\>](https://docs.unity3d.com/Packages/com.unity.collections@6.6/api/Unity.Collections.FixedList128Bytes-1.html) — an unmanaged, resizable list whose content is stored entirely inside the 128-byte struct; generic over any unmanaged element type; implements `INativeList<T>`/`IIndexable<T>` for standard `Add`/`Remove`/`Insert` operations, with a capacity fixed by the struct's byte size. Sibling sizes: `FixedList32Bytes<T>`, `FixedList64Bytes<T>`, `FixedList512Bytes<T>`, `FixedList4096Bytes<T>`.

Both families require no `Allocator`/`Dispose()` — their lifetime is exactly the struct's own lifetime (stack, or embedded inside another unmanaged struct/component).

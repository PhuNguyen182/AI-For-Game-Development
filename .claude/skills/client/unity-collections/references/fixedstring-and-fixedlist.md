# FixedString & FixedList — Allocation-Free Small Data

Source: [FixedString128Bytes](https://docs.unity3d.com/Packages/com.unity.collections@6.6/api/Unity.Collections.FixedString128Bytes.html), [FixedList128Bytes\<T\>](https://docs.unity3d.com/Packages/com.unity.collections@6.6/api/Unity.Collections.FixedList128Bytes-1.html).
Covers: SKILL.md §4 — **"Use `FixedString*Bytes`/`FixedList*Bytes<T>` for small, fixed-capacity data that must be Burst/job-compatible"**.

Both families store their contents inside the struct itself, so they take no
`Allocator` and need no `Dispose()` — their lifetime is exactly the struct's
own (stack, or embedded in another unmanaged struct or component). That is
what makes them the answer for a `string` or short list crossing a job/Burst
boundary, and the reason size selection matters: the whole struct is copied by
value on every pass.

## Families and sizing

| Family | Effect | Use when | Source |
|---|---|---|---|
| `FixedString32/64/128/512/4096Bytes` | UTF-8 text inline in the struct, 2-byte length prefix plus a guaranteed null terminator | A `string` must reach a job, Burst method, or ECS component | [FixedString128Bytes](https://docs.unity3d.com/Packages/com.unity.collections@6.6/api/Unity.Collections.FixedString128Bytes.html) |
| `FixedList32/64/128/512/4096Bytes\<T\>` | Resizable list inline in the struct, generic over any unmanaged `T`; implements `INativeList<T>`/`IIndexable<T>` for `Add`/`Remove`/`Insert` | A short list of unmanaged elements must cross the same boundary | [FixedList128Bytes\<T\>](https://docs.unity3d.com/Packages/com.unity.collections@6.6/api/Unity.Collections.FixedList128Bytes-1.html) |

## Capacity accounting

| Nominal size | Usable payload | Source |
|---|---|---|
| `FixedString128Bytes` | ~125 bytes after the length prefix and terminator | [FixedString128Bytes](https://docs.unity3d.com/Packages/com.unity.collections@6.6/api/Unity.Collections.FixedString128Bytes.html) |
| `FixedList<size>Bytes\<T\>` | `size` minus header, divided by `sizeof(T)` — element count falls as `T` grows | [FixedList128Bytes\<T\>](https://docs.unity3d.com/Packages/com.unity.collections@6.6/api/Unity.Collections.FixedList128Bytes-1.html) |

**Critical caveat**: pick the smallest size that comfortably fits. Oversizing
costs on every by-value copy, and a `FixedString4096Bytes` inside a hot
per-entity struct pays that 4 KB on every pass whether or not it is full.

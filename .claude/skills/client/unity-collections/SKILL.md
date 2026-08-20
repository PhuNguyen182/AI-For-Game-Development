---
name: unity-collections
description: >
  Technique for Unity's Collections package — choosing the right unmanaged
  container (`NativeArray`/`NativeSlice`, `NativeList`, `NativeHashMap`/
  `NativeParallelHashMap`, `NativeHashSet`, `NativeQueue`, `NativeStream`,
  `NativeReference`), allocation-free `FixedString`/`FixedList` types,
  `Unsafe-` collection variants and aliasing, and allocator strategy beyond
  the basic Temp/TempJob/Persistent lifetimes (rewindable and custom
  allocators). Collections is one of the foundational packages DOTS is built
  on — used by the C# Job System, Burst, and ECS alike — but it works
  independently of all three: a project can use `NativeArray`/`NativeList`
  in ordinary MonoBehaviour code with no job or entity involved. Do not use
  this for job scheduling, `JobHandle` dependency chaining, or the plain
  Temp/TempJob/Persistent allocator choice for a container feeding a single
  scheduled job — that's `unity-job-system-and-burst`; this skill owns which
  collection type to pick and its own API surface (resizing, hashing,
  parallel writers, `FixedString`/`FixedList`, `Unsafe-` variants,
  custom/rewindable allocators). Do not use this for Burst-specific
  compilation tuning (HPC# subset, `FloatMode`, intrinsics, AOT settings) —
  that's `unity-burst-compiler`, even though every collection here is
  designed to be Burst-compatible. Do not use this to model ECS components,
  buffers (`IBufferElementData`/`DynamicBuffer<T>`), or queries — that's
  `unity-ecs-architecture`. Do not use this for `Unity.Mathematics`
  vector/matrix/random/noise types — that's `unity-mathematics`.
---

# Unity Collections — Native Containers, FixedString/FixedList & Allocators

Sources: see [references/](references/) for the Unity Manual/Scripting API root links, split by topic — [root-links.md](references/root-links.md), [collection-types.md](references/collection-types.md), [fixedstring-and-fixedlist.md](references/fixedstring-and-fixedlist.md), [unsafe-collections-and-aliasing.md](references/unsafe-collections-and-aliasing.md), [allocators.md](references/allocators.md), [rewindable-and-custom-allocators.md](references/rewindable-and-custom-allocators.md), [parallel-readers-writers.md](references/parallel-readers-writers.md), [dots-relationship.md](references/dots-relationship.md).

## 1. Objective
Pick and use the right unmanaged collection type for the data and access pattern at hand — correct type choice, correct allocator, correct disposal — without drifting into job-scheduling mechanics, Burst tuning, or ECS component design, which are sibling skills' territory.

## 2. Role
Act as the Collections-package specialist: given a need for unmanaged, GC-free data (feeding a job, a Burst-compiled method, an ECS buffer, or just a MonoBehaviour that wants to avoid GC pressure per `performance-and-algorithms.md`), you choose the right container type, its allocator, and its safe access pattern — you don't schedule the job that consumes it and you don't tune its Burst compilation.

## 3. When to invoke this skill
- Choosing between `NativeArray<T>`, `NativeList<T>`, `NativeHashMap<TKey,TValue>`/`NativeParallelHashMap<TKey,TValue>`, `NativeHashSet<T>`, `NativeQueue<T>`, `NativeStream`, or `NativeReference<T>` for a specific data shape and access pattern.
- Replacing a managed `string`/`List<T>`/`Dictionary<TKey,TValue>` that needs to cross into a job, Burst-compiled method, or ECS component with an unmanaged `FixedString*Bytes`/`FixedList*Bytes<T>` or `Native-` equivalent.
- Deciding between a `Native-` collection (safety-checked) and its `Unsafe-` counterpart (no safety checks, lower overhead) for a specific, justified low-level case.
- Reasoning about aliasing — reinterpreting one collection's memory as another type/shape without a separate allocation.
- A `Temp`/`TempJob`/`Persistent` allocator doesn't fit the actual data lifetime (e.g. many short-lived allocations across more than a few frames, or allocations whose lifetime doesn't map to a job or a frame) — evaluating a rewindable or custom allocator instead.
- Writing to a `Native-` container concurrently from multiple threads inside a parallel job — choosing between a `ParallelWriter` and `NativeStream`/`UnsafeStream` based on whether write order matters.
- Negative trigger: scheduling the job that will consume the container, chaining `JobHandle` dependencies, or the routine Temp/TempJob/Persistent choice for data feeding one scheduled job — that's `unity-job-system-and-burst`; hand off once the container itself is chosen and populated.
- Negative trigger: Burst-specific compilation tuning (HPC# subset compliance, `FloatMode`, intrinsics, AOT settings) — that's `unity-burst-compiler`, even though every type here is Burst-eligible by design.
- Negative trigger: modeling ECS components, `IBufferElementData`/`DynamicBuffer<T>`, or queries — that's `unity-ecs-architecture`, even though a `DynamicBuffer<T>` behaves conceptually like a `NativeList<T>` under the hood.
- Negative trigger: `Unity.Mathematics` vector/matrix/quaternion/`Random`/`noise` types — that's `unity-mathematics`, a separate package with its own skill.

## 4. How to use this skill
1. **Confirm the actual access pattern before picking a type.** Sequential iteration/append → `NativeList<T>`; key-value lookup → `NativeHashMap`/`NativeParallelHashMap` (single-threaded vs. multithreaded write, per `collection-types.md`); uniqueness checks → `NativeHashSet<T>`; FIFO work items → `NativeQueue<T>`; per-thread append-only buffers → `NativeStream`; a single boxed value that needs to cross into a job → `NativeReference<T>`. Don't default to `NativeList<T>` for everything the way `List<T>` gets defaulted to in managed code.
2. **Decide managed vs. unmanaged deliberately.** If the data never needs to cross into a job, a Burst-compiled method, or an ECS component, a plain managed `List<T>`/`Dictionary<TKey,TValue>` (per `performance-and-algorithms.md`'s baseline data-structure guidance) is simpler and avoids allocator-lifetime bookkeeping — reach for `Native-` types only when something on the other side of that boundary actually needs them.
3. **Use `FixedString*Bytes`/`FixedList*Bytes<T>` for small, fixed-capacity data that must be Burst/job-compatible** (log messages, short identifiers, small per-entity tag lists) — pick the smallest size (`32`/`64`/`128`/`512`/`4096` bytes) that comfortably fits the data; both are fully stack-embeddable structs with no separate allocation or disposal.
4. **Reach for `Unsafe-` collection variants only for a specific, justified low-level case** (e.g. building a custom container on top of them, or a proven safety-check overhead problem) — the safety checks on `Native-` types exist to catch real bugs (disposal, race conditions) and are the correct default.
5. **Use aliasing deliberately, not as a shortcut around a second allocation you didn't want to think through** — an alias shares its parent's memory and becomes unusable the moment the parent is disposed; document which collection owns the allocation when aliasing is used.
6. **Pick the allocator by actual data lifetime**, escalating beyond the basic three only when they genuinely don't fit: `Temp`/`TempJob`/`Persistent` (per `unity-job-system-and-burst`) cover most cases; reach for a **rewindable allocator** when many short-lived allocations need to be freed together at a defined checkpoint without per-allocation `Dispose()` bookkeeping; reach for a **custom allocator** only for a genuinely specialized lifetime/strategy neither built-in option covers.
7. **For concurrent writes from a parallel job, choose based on whether order matters.** A `ParallelWriter` (`AsParallelWriter()`) is simplest but its write order is indeterministic under thread scheduling; use `NativeStream`/`UnsafeStream` (per-thread buffers) when the indeterminism itself is a problem, or sort/index afterward if order must be recovered.
8. **Dispose every `Native-`/custom-allocator allocation on every code path**, including early returns — this is the Collections-specific case of `performance-and-algorithms.md`'s Memory discipline rule; an aliased collection is the one exception, since disposing its parent already covers it.
9. **State the hand-off explicitly.** Once the container is chosen, allocated, and populated, scheduling the job that reads/writes it is `unity-job-system-and-burst`'s territory, and tuning that job's Burst compilation is `unity-burst-compiler`'s — don't extend this skill's guidance into either.

## 5. Specific goals / tasks this skill performs
- Choosing the right `Native-`/`Unsafe-` collection type for a given data shape and access pattern.
- Replacing managed strings/lists/dictionaries that need to cross a job/Burst/ECS boundary with `FixedString`/`FixedList`/`Native-` equivalents.
- Evaluating and applying rewindable or custom allocators when the basic Temp/TempJob/Persistent lifetimes don't fit.
- Choosing between `ParallelWriter` and `NativeStream`/`UnsafeStream` for concurrent-write safety and ordering needs.
- Auditing collection disposal and aliasing correctness.
- Out of scope: scheduling jobs/`JobHandle` dependency chains and the routine Temp/TempJob/Persistent choice for single-job data (`unity-job-system-and-burst`); Burst compilation tuning (`unity-burst-compiler`); ECS component/buffer/query design (`unity-ecs-architecture`); `Unity.Mathematics` types (`unity-mathematics`).

## 6. Output format
```
## Collections Work — <system/data name>
- Access pattern: <sequential / key-value / set / FIFO / per-thread append / single value>
- Collection type chosen: <NativeArray / NativeList / NativeHashMap / NativeParallelHashMap / NativeHashSet / NativeQueue / NativeStream / NativeReference / FixedString*/FixedList*> — rationale
- Managed vs. unmanaged decision: <why this needed to be unmanaged, or "kept managed — no job/Burst/ECS boundary crossed">
- Unsafe- variant used: <yes/no — justification>
- Aliasing used: <yes/no — parent/owner collection>
- Allocator: <Temp/TempJob/Persistent/rewindable/custom> — rationale
- Concurrent-write pattern: <ParallelWriter / NativeStream / UnsafeStream / none>
- Disposal confirmed on every code path: <yes/no>
- Hand-off: <job scheduling → unity-job-system-and-burst / Burst tuning → unity-burst-compiler, if applicable>
- Known limitations: <...>
```

## 7. Examples
**Example 1**
- Input: a bulk per-agent update (already approved for the Job System per `unity-job-system-and-burst`) needs a per-agent neighbor list that's rebuilt every frame and consumed within the same job batch.
- Output: chose `NativeStream` over a `NativeParallelHashMap`-based approach so each worker thread appends neighbor results into its own buffer with zero cross-thread contention; allocated with `Allocator.TempJob` since the data doesn't need to survive past the frame's job chain; disposed via `Dispose(JobHandle)` chained to the consuming job's handle; handed the actual `IJobFor` scheduling back to `unity-job-system-and-burst`.

**Example 2**
- Input: "Can you make this per-frame debug label use a `NativeHashMap<int, FixedString64Bytes>` so it works inside our Burst job?" — the label is only ever read/written on the main thread, never inside a job.
- Output: declined the unmanaged container — since nothing here crosses into a job or Burst-compiled code, a plain managed `Dictionary<int, string>` is simpler, avoids allocator-lifetime bookkeeping and `Dispose()` calls entirely, and is fully in line with `performance-and-algorithms.md`'s guidance to default to the simpler structure when the "smarter" one buys nothing.

## 8. Edge cases & guardrails
- Never introduce a `Native-`/`Unsafe-` collection for data that never crosses a job/Burst/ECS boundary — a managed collection is simpler and avoids allocator-lifetime bookkeeping for no benefit.
- Never leave a `Native-` collection or custom-allocator allocation undisposed on any code path — an alias is the sole exception, since its parent's disposal already covers it.
- Never touch an alias after its parent collection has been disposed — the alias becomes invalid the instant the parent is disposed, not just "stale."
- Don't reach for an `Unsafe-` variant without a specific, justified reason — the `Native-` safety checks catch real disposal/race bugs and are the correct default.
- Don't assume a `ParallelWriter`'s write order is deterministic — if downstream logic depends on order, use `NativeStream`/`UnsafeStream` or sort afterward instead of assuming thread-scheduling luck.
- Don't reach for a rewindable or custom allocator before confirming Temp/TempJob/Persistent genuinely doesn't fit the data's actual lifetime — the basic three cover the overwhelming majority of cases.
- Pick the smallest `FixedString`/`FixedList` capacity that comfortably fits the data — oversizing wastes struct space that gets copied by value on every pass.
- Don't confuse this skill's collection-type/allocator-strategy concerns with `unity-job-system-and-burst`'s scheduling/dependency concerns — a container can be perfectly chosen and still be scheduled incorrectly, and vice versa; check both independently.

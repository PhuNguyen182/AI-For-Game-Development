---
name: unity-collections
description: >
  Unity Collections package (`Unity.Collections`): picking and using unmanaged
  containers — `NativeArray`/`NativeSlice`, `NativeList`, `NativeHashMap`/
  `NativeParallelHashMap`, `NativeHashSet`, `NativeQueue`, `NativeStream`,
  `NativeReference` — plus `FixedString*Bytes`/`FixedList*Bytes`, `Unsafe-`
  variants, aliasing, `AsParallelWriter()`, and allocator strategy beyond
  Temp/TempJob/Persistent (rewindable and custom allocators,
  `AllocatorHelper`, `CollectionHelper`). Use when choosing a container for a
  data shape, replacing a managed `List`/`Dictionary`/`string` that must cross
  into a job, Burst method, or ECS component, or auditing disposal and
  aliasing. Not for: job scheduling and `JobHandle` chains
  (`unity-job-system-and-burst`), Burst compilation tuning
  (`unity-burst-compiler`), ECS component/buffer/query design
  (`unity-ecs-architecture`), `float3`/`quaternion`/`Random`/`noise`
  (`unity-mathematics`), physics data types (`unity-physics`),
  `RenderMeshArray` (`unity-entities-graphics`).
---

# Unity Collections — Native Containers, FixedString/FixedList & Allocators

## Bundled resources

### References
Read-only context, loaded on demand so this file stays short.

| File | Contents | Read when |
|---|---|---|
| [root-links.md](references/root-links.md) | Collections 6.6 Manual/API index roots and the version-pin rule | Starting any task here, or before adding a new upstream link |
| [collection-types.md](references/collection-types.md) | Per-type behaviour of each `Native-` container; `Native-` vs `Unsafe-` vs non-allocating category | The container type is not yet decided, or a chosen type's limits are in question |
| [fixedstring-and-fixedlist.md](references/fixedstring-and-fixedlist.md) | `FixedString*Bytes`/`FixedList*Bytes` sizes, usable capacity, no-disposal property | A `string` or small list must cross into a job, Burst method, or ECS component |
| [unsafe-collections-and-aliasing.md](references/unsafe-collections-and-aliasing.md) | What `Unsafe-` drops; alias ownership and invalidation rules | Someone proposes an `Unsafe-` variant, or two collections are to share one allocation |
| [allocators.md](references/allocators.md) | `Temp`/`TempJob`/`Persistent` lifetimes, `Dispose(JobHandle)`, `IsCreated` | Choosing an allocator, or auditing a disposal path |
| [rewindable-and-custom-allocators.md](references/rewindable-and-custom-allocators.md) | Rewindable block growth/rewind semantics; custom-allocator registration and teardown | The built-in three provably do not fit the data's lifetime |
| [parallel-readers-writers.md](references/parallel-readers-writers.md) | `ParallelWriter` capacity and ordering guarantees vs. `NativeStream` per-thread buffers | Multiple threads will write one container inside a parallel job |
| [dots-relationship.md](references/dots-relationship.md) | Where this package ends and Jobs/Burst/ECS/Mathematics begin | A request straddles two DOTS packages, or a hand-off must be stated |

## 1. Objective
Pick and use the right unmanaged collection type for the data and access pattern at hand — correct type choice, correct allocator, correct disposal — without drifting into job-scheduling mechanics, Burst tuning, or ECS component design, which are sibling skills' territory.

## 2. Role
Act as the Collections-package specialist for the client track — the tool reached for whenever a feature needs unmanaged, GC-free data (feeding a job, a Burst-compiled method, an ECS buffer, or a MonoBehaviour avoiding GC pressure per `performance-and-algorithms.md`). You choose the container, its allocator, and its safe access pattern; you do not schedule the job that consumes it or tune its Burst compilation.

## 3. When to invoke this skill
- Choosing between `NativeArray<T>`, `NativeList<T>`, `NativeHashMap<TKey,TValue>`/`NativeParallelHashMap<TKey,TValue>`, `NativeHashSet<T>`, `NativeQueue<T>`, `NativeStream`, or `NativeReference<T>` for a specific data shape and access pattern.
- Replacing a managed `string`/`List<T>`/`Dictionary<TKey,TValue>` that must cross into a job, Burst-compiled method, or ECS component with a `FixedString*Bytes`/`FixedList*Bytes<T>` or `Native-` equivalent.
- Deciding between a `Native-` collection (safety-checked) and its `Unsafe-` counterpart, or reasoning about aliasing — reinterpreting one collection's memory as another type or shape without a second allocation.
- `Temp`/`TempJob`/`Persistent` doesn't fit the actual data lifetime (many short-lived allocations spanning more than a few frames) — evaluating a rewindable or custom allocator instead.
- Writing to a container concurrently from a parallel job — `ParallelWriter` vs. `NativeStream`/`UnsafeStream`, decided by whether write order matters.
- Negative trigger: scheduling the consuming job, chaining `JobHandle` dependencies, or the routine allocator pick for data feeding one scheduled job — that's `unity-job-system-and-burst`; hand off once the container is chosen and populated.
- Negative trigger: Burst compilation tuning (HPC# subset, `FloatMode`, intrinsics, AOT settings) — that's `unity-burst-compiler`, even though every type here is Burst-eligible by design.
- Negative trigger: modeling ECS components, `IBufferElementData`/`DynamicBuffer<T>`, or queries — that's `unity-ecs-architecture`, even though `DynamicBuffer<T>` behaves like an entity-scoped `NativeList<T>`.
- Negative trigger: `Unity.Mathematics` vector/matrix/quaternion/`Random`/`noise` types — that's `unity-mathematics`, a separate package with its own skill.
- Negative trigger: physics-specific data types — `PhysicsCollider`'s `BlobAssetReference<Collider>`, or `CollisionEvents`/`TriggerEvents` streams — that's `unity-physics`, even though both build on this skill's blob-asset and `NativeStream` mechanics.
- Negative trigger: rendering-specific data types such as `RenderMeshArray`'s internal mesh/material lists — that's `unity-entities-graphics`.

## 4. How to use this skill
1. **Confirm the actual access pattern before picking a type**, per [collection-types.md](references/collection-types.md) (anchored to the version pinned in [root-links.md](references/root-links.md)) — sequential append → `NativeList<T>`; key-value lookup → `NativeHashMap`/`NativeParallelHashMap`; uniqueness → `NativeHashSet<T>`; FIFO → `NativeQueue<T>`; per-thread append-only → `NativeStream`; one value crossing into a job → `NativeReference<T>`. Defaulting to `NativeList<T>` the way managed code defaults to `List<T>` picks the type before the question is asked.
2. **Decide managed vs. unmanaged deliberately**, per [dots-relationship.md](references/dots-relationship.md). Unmanaged containers cost allocator-lifetime bookkeeping; that cost only buys something at a job/Burst/ECS boundary. If the data never crosses one, a managed `List<T>`/`Dictionary<TKey,TValue>` is the correct answer under `performance-and-algorithms.md`'s data-structure guidance.
3. **Use `FixedString*Bytes`/`FixedList*Bytes<T>` for small, fixed-capacity data that must be Burst/job-compatible**, per [fixedstring-and-fixedlist.md](references/fixedstring-and-fixedlist.md) — pick the smallest size (32/64/128/512/4096 bytes) that comfortably fits, since the struct is copied by value on every pass. Neither family takes an `Allocator` or needs `Dispose()`.
4. **Reach for an `Unsafe-` variant only for a specific, justified low-level case**, per [unsafe-collections-and-aliasing.md](references/unsafe-collections-and-aliasing.md) — building a custom container on top of one, or a *measured* safety-check overhead problem per `performance-and-algorithms.md`'s Verification section. Absent that measurement, `Native-` is the answer: its checks catch real disposal and race bugs.
5. **Use aliasing deliberately, and name the owner**, per [unsafe-collections-and-aliasing.md](references/unsafe-collections-and-aliasing.md) — an alias shares its parent's allocation and becomes invalid, not merely stale, the instant the parent is disposed. Record which collection owns the allocation wherever an alias is introduced.
6. **Pick the allocator by actual data lifetime**, per [allocators.md](references/allocators.md), escalating only when the built-in three provably don't fit. Many short-lived allocations freed together at a defined checkpoint → a **rewindable** allocator; a lifetime neither built-in nor rewindable covers → a **custom** allocator, per [rewindable-and-custom-allocators.md](references/rewindable-and-custom-allocators.md).
7. **For concurrent writes from a parallel job, decide on write order first**, per [parallel-readers-writers.md](references/parallel-readers-writers.md) — `AsParallelWriter()` is simplest but its order follows thread scheduling and it cannot grow capacity, so pre-size the list; when the indeterminism itself is the problem, use `NativeStream`/`UnsafeStream`, or sort afterward to recover order.
8. **Dispose every `Native-`/custom-allocator allocation on every code path**, including early returns — the Collections-specific case of `performance-and-algorithms.md`'s Memory discipline rule. An alias is the sole exception, since disposing its parent already covers it.
9. **If the request's data shape or crossing boundary is unstated, ask before choosing** — access pattern and boundary are the two inputs steps 1–2 consume, and guessing either silently picks the wrong container. Once the container is chosen and populated, state the hand-off: scheduling belongs to `unity-job-system-and-burst`, Burst tuning to `unity-burst-compiler`, per [dots-relationship.md](references/dots-relationship.md).

## 5. Specific goals / tasks this skill performs
- Choosing the right `Native-`/`Unsafe-` collection type for a given data shape and access pattern.
- Replacing managed strings/lists/dictionaries that cross a job/Burst/ECS boundary with `FixedString`/`FixedList`/`Native-` equivalents.
- Evaluating and applying rewindable or custom allocators when Temp/TempJob/Persistent don't fit.
- Choosing between `ParallelWriter` and `NativeStream`/`UnsafeStream` for concurrent-write safety and ordering.
- Auditing collection disposal and aliasing correctness.
- Out of scope: job scheduling and `JobHandle` chains (`unity-job-system-and-burst`); Burst compilation tuning (`unity-burst-compiler`); ECS component/buffer/query design (`unity-ecs-architecture`); `Unity.Mathematics` types (`unity-mathematics`).

## 6. Output format
```
## Collections Work — <system/data name>
- Access pattern: <sequential / key-value / set / FIFO / per-thread append / single value>
- Collection type chosen: <NativeArray / NativeList / NativeHashMap / NativeParallelHashMap / NativeHashSet / NativeQueue / NativeStream / NativeReference / FixedString* / FixedList*> — rationale
- Managed vs. unmanaged: <the boundary that forced unmanaged, or "kept managed — no job/Burst/ECS boundary crossed">
- Unsafe- variant used: <yes/no — justification>
- Aliasing used: <yes/no — owning collection>
- Allocator: <Temp / TempJob / Persistent / rewindable / custom> — rationale
- Concurrent-write pattern: <ParallelWriter / NativeStream / UnsafeStream / none>
- Rule compliance: <disposal on every code path confirmed, per Memory discipline>
- Verification: <how the disposal/overhead claim was confirmed, or "not applicable">
- Layer: <Game.Core.* / Game.Client.* / Editor-only>
- Known limitations: <...>
```

**Extended report — emit ONLY when the requester asks for it.** It replaces the one-line `Known limitations` above with all three fields:
```
- Known limitations: <what the delivered solution does not cover>
- Latent concerns: <failure modes not yet triggered: assumptions holding only under current conditions, thresholds not yet reached>
- Future remediation: <the concrete fix for each concern, each with its trigger condition>
```

## 7. Examples
**Example 1**
- Input: a bulk per-agent update (already approved for the Job System per `unity-job-system-and-burst`) needs a per-agent neighbour list rebuilt every frame and consumed within the same job batch.
- Output: chose `NativeStream` over a `NativeParallelHashMap` approach so each worker thread appends into its own buffer with zero cross-thread contention; `Allocator.TempJob`, since the data doesn't outlive the frame's job chain; disposed via `Dispose(JobHandle)` chained to the consuming job's handle; `IJobFor` scheduling handed back to `unity-job-system-and-burst`.

**Example 2**
- Input: "Can you make this per-frame debug label use a `NativeHashMap<int, FixedString64Bytes>` so it works inside our Burst job?" — the label is only ever touched on the main thread, never inside a job.
- Output: declined — nothing here crosses into a job or Burst-compiled code, so the unmanaged container buys nothing and costs allocator-lifetime bookkeeping and `Dispose()` calls. Kept a managed `Dictionary<int, string>`, per `performance-and-algorithms.md`'s rule to default to the simpler structure when the smarter one buys nothing.

**Example 3**
- Input: an Editor-side mesh importer makes thousands of small short-lived allocations across a multi-frame import, all dead once the import ends.
- Output: `TempJob` rejected (lifetime exceeds ~4 frames and would raise leak warnings), `Persistent` rejected (thousands of individual `Dispose()` calls). Chose a rewindable allocator created via `AllocatorHelper`, containers allocated through `CollectionHelper.CreateNativeArray`, and one rewind at the import's end freeing every allocation at once — per [rewindable-and-custom-allocators.md](references/rewindable-and-custom-allocators.md).

## 8. Edge cases & guardrails
- Never introduce a `Native-`/`Unsafe-` collection for data that never crosses a job/Burst/ECS boundary — it adds allocator-lifetime bookkeeping and buys nothing.
- Never leave a `Native-` or custom-allocator allocation undisposed on any code path, including early returns — an alias is the sole exception, since its parent's disposal covers it.
- Never touch an alias after its parent has been disposed — it is invalid from that instant, and reading it is undefined behaviour, not a stale read.
- Never reach for an `Unsafe-` variant without a measured reason — dropping the safety checks removes the only thing that reports a disposal or race bug before it becomes a crash.
- Never assume `ParallelWriter` order is deterministic, and never let it grow a list — it cannot, so pre-size or the append silently fails to fit.
- Never escalate to a rewindable or custom allocator before confirming the built-in three genuinely don't fit — that's speculative complexity YAGNI already forbids.
- If the access pattern, the crossing boundary, or the data's real lifetime is unstated, ask — each one independently determines a different field of §6, and a guess produces a plausible-looking wrong answer.

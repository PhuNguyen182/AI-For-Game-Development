# Native Containers & the Safety System

Sources: [Introduction to NativeContainer](https://docs.unity3d.com/Manual/job-system-native-container.html), [NativeArray](https://docs.unity3d.com/ScriptReference/Unity.Collections.NativeArray_1.html).
Covers: SKILL.md §4 — **"Pick the allocator by how long the data must live"**, **"Dispose every native allocation on every code path"**.

Lifetime, access marking, and what the safety system actually guarantees.
Choosing *which* container type (`NativeList`, `NativeHashMap`, `NativeStream`,
`FixedString`) and any allocator beyond the three built-ins is
`unity-collections`; this file covers only the rules for a container whose type
is already decided.

## Allocators

| Allocator | What it decides | Source |
|---|---|---|
| `Allocator.Temp` | Cheapest, freed automatically at the end of the frame or job — main-thread scratch only; it cannot be handed to a scheduled job | [NativeContainer](https://docs.unity3d.com/Manual/job-system-native-container.html) |
| `Allocator.TempJob` | The normal choice for data passed into a scheduled job; must be disposed within ~4 frames or it raises a leak warning | [NativeContainer](https://docs.unity3d.com/Manual/job-system-native-container.html) |
| `Allocator.Persistent` | Slowest to allocate, indefinite lifetime, always disposed explicitly — for data spanning many frames | [NativeContainer](https://docs.unity3d.com/Manual/job-system-native-container.html) |

## Access marking and disposal

| Subject | What it decides | Source |
|---|---|---|
| `[ReadOnly]` | Lets multiple jobs access the container concurrently; omitting it serializes them with no error to explain the lost parallelism | [NativeContainer](https://docs.unity3d.com/Manual/job-system-native-container.html) |
| `Dispose()` | Frees immediately — illegal while a scheduled job may still read the container | [NativeArray](https://docs.unity3d.com/ScriptReference/Unity.Collections.NativeArray_1.html) |
| `Dispose(JobHandle)` | Defers the free until that handle completes, returning a new handle — the correct form when a job still holds the data | [NativeArray](https://docs.unity3d.com/ScriptReference/Unity.Collections.NativeArray_1.html) |
| `IsCreated` | Guards a disposal path that can run twice; true for every copy of the handle until the one allocation is freed | [NativeArray](https://docs.unity3d.com/ScriptReference/Unity.Collections.NativeArray_1.html) |
| Custom container | `AtomicSafetyHandle` plus `UnsafeUtility.MallocTracked`/`FreeTracked` — only when no built-in container fits | [Custom NativeContainer](https://docs.unity3d.com/Manual/job-system-custom-nativecontainer.html) |

**Critical caveat**: the safety system's race and leak detection lives behind
Editor-only checks. A Player build performs none of them, so a job that passes
QA in a build has been tested with the diagnostics switched off — Editor
validation is the evidence, not the other way round.

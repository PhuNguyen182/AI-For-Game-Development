# Native Containers and the Safety System

Sources: [n] `Manual/job-system-native-container.html`, [a] `ScriptReference/Unity.Collections.NativeArray_1.html`, [x] `Manual/job-system-custom-nativecontainer.html`, under `https://docs.unity3d.com/`. Container type choice and non-built-in allocators: `unity-collections`.

## Allocators [n]

| Allocator | Fact that decides |
|---|---|
| `Temp` | Cheapest, freed at end of frame or job; main-thread scratch only, cannot be handed to a scheduled job |
| `TempJob` | Normal choice for data passed to a scheduled job; dispose within ~4 frames or a leak warning fires |
| `Persistent` | Slowest to allocate, indefinite lifetime, always disposed explicitly; for data spanning many frames |

## Access and disposal

| Subject | Fact that decides |
|---|---|
| `[ReadOnly]` | Lets several jobs access the container concurrently; omitting it serializes them silently [n] |
| `Dispose()` | Frees immediately; illegal while a scheduled job may still read the container [a] |
| `Dispose(JobHandle)` | Defers the free until the handle completes and returns a new handle; correct while a job still holds the data [a] |
| `IsCreated` | Guards a disposal path that can run twice; true for every copy of the handle until the one allocation is freed [a] |
| Custom container | `AtomicSafetyHandle` plus `UnsafeUtility.MallocTracked`/`FreeTracked`, only when no built-in fits [x] |

**Caveat:** race and leak detection is Editor-only. A job passing QA in a Player build was tested with diagnostics off; Editor validation is the evidence.

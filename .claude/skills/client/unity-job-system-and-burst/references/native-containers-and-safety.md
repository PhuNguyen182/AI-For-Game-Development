# Native Containers & the Safety System

Covers SKILL.md steps 3, 7, 8 (allocator choice, `[ReadOnly]`, disposal, the safety system's leak/race tracking).

## Manual
- [Introduction to NativeContainer](https://docs.unity3d.com/Manual/job-system-native-container.html) — `NativeArray`/`NativeSlice`, `[ReadOnly]` for concurrent read access, `Allocator.Temp`/`TempJob`/`Persistent` lifetime/cost trade-offs, the built-in safety system's usage/leak tracking.
- [Implement a custom native container](https://docs.unity3d.com/Manual/job-system-custom-nativecontainer.html) — `AtomicSafetyHandle`, `UnsafeUtility.MallocTracked`/`FreeTracked`; only relevant when the built-in containers genuinely don't fit.

## Scripting API
- [`NativeArray<T>`](https://docs.unity3d.com/ScriptReference/Unity.Collections.NativeArray_1.html) — the standard job-safe buffer; `IsCreated`, `Dispose`, `CopyFrom`/`CopyTo`, reinterpretation methods.

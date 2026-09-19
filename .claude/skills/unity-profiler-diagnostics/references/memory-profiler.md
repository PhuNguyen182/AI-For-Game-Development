# Memory Profiler — snapshots, diffing, and what the totals actually mean

Sources: [Memory Profiler introduction](https://docs.unity3d.com/Packages/com.unity.memoryprofiler@1.1/manual/memory-profiler-introduction.html), [Memory module](https://docs.unity3d.com/Manual/ProfilerMemory.html).
Covers: SKILL.md §4 — **"Diff two Memory Profiler snapshots rather than reading a single total"**.

How to establish that memory is actually leaking, as distinct from Unity
holding pages it has already taken from the operating system. The fix a
retention chain implies — unsubscribing an event, releasing an Addressables
handle, capping a collection — belongs to `unity-engineer`, and the
Addressables handle discipline specifically to `unity-addressables`.

## Reading the totals

| Term | What it decides | Source |
|---|---|---|
| Reserved | What Unity has requested from the operating system; it does not shrink when objects are freed, so a rising Reserved line on its own is not evidence of a leak | [Memory module](https://docs.unity3d.com/Manual/ProfilerMemory.html) |
| Used | What is actually occupied inside that reservation — the number that moves when a leak is real | [Memory module](https://docs.unity3d.com/Manual/ProfilerMemory.html) |
| Managed heap | C# objects and their retention graph; this is where an un-unsubscribed event handler or a static cache shows up | [Memory Profiler introduction](https://docs.unity3d.com/Packages/com.unity.memoryprofiler@1.1/manual/memory-profiler-introduction.html) |
| Native memory | Textures, meshes, audio, and other engine-owned objects; an asset never released shows here rather than on the managed heap | [Memory Profiler introduction](https://docs.unity3d.com/Packages/com.unity.memoryprofiler@1.1/manual/memory-profiler-introduction.html) |
| Built-in Memory module | One point in time only — it can raise the suspicion and can never confirm it, because it has no comparison of two moments | [Memory module](https://docs.unity3d.com/Manual/ProfilerMemory.html) |

## Snapshot workflow

| Step | What it decides | Source |
|---|---|---|
| Capture from a player build | An Editor snapshot contains Editor-owned objects and inflated asset residency, so object counts read from it do not describe the shipped game | [Memory Profiler introduction](https://docs.unity3d.com/Packages/com.unity.memoryprofiler@1.1/manual/memory-profiler-introduction.html) |
| Two snapshots around a suspected cycle | Take one before and one after a repeatable loop — enter and leave a level several times — so what survived the loop is what the diff isolates | [Memory Profiler introduction](https://docs.unity3d.com/Packages/com.unity.memoryprofiler@1.1/manual/memory-profiler-introduction.html) |
| Compare mode | Shows objects added between the two, which converts "memory is growing" into a named type and count | [Memory Profiler introduction](https://docs.unity3d.com/Packages/com.unity.memoryprofiler@1.1/manual/memory-profiler-introduction.html) |
| References-to view | Walks the retention path to the root holding an object alive — the actual output of the investigation, since the object's own size is rarely the point | [Memory Profiler introduction](https://docs.unity3d.com/Packages/com.unity.memoryprofiler@1.1/manual/memory-profiler-introduction.html) |
| Snapshot cost | Capturing writes the whole heap to disk and pauses the application while it does, so a snapshot cannot be taken mid-hitch and expected to leave the frame timing intact | [Memory Profiler introduction](https://docs.unity3d.com/Packages/com.unity.memoryprofiler@1.1/manual/memory-profiler-introduction.html) |

**Critical caveat**: an object surviving one loop is not yet a leak — a pool,
a cache, and a lazily built lookup all look identical to a leak in a single
diff. What distinguishes them is growth across repeated cycles, so run the
loop several times and confirm the count keeps climbing before naming it.

The `@1.1` segment in these links tracks the Memory Profiler package version
installed in the project, not the Editor version — read it from
`Packages/manifest.json` and substitute before following a link.

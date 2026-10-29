# Memory Profiler

Docs: https://docs.unity3d.com/Packages/com.unity.memoryprofiler@1.1/manual/memory-profiler-introduction.html (`@1.1` = installed package version) · https://docs.unity3d.com/Manual/ProfilerMemory.html

Establishes leak vs Unity holding pages it already took. The fix belongs to `unity-performance-engineer`; Addressables handle discipline to `unity-addressables`.

## Totals
| Term | Meaning |
|---|---|
| Reserved | Requested from the OS; does not shrink when objects are freed, so rising Reserved alone is not a leak |
| Used | Occupied inside the reservation; moves when a leak is real |
| Managed heap | C# objects and retention graph; un-unsubscribed handlers and static caches show here |
| Native memory | Textures, meshes, audio, engine objects; an unreleased asset shows here |
| Built-in Memory module | One point in time; can raise suspicion, never confirm |

## Workflow
| Step | Rule |
|---|---|
| Capture from a player build | Editor snapshots hold Editor-owned objects and inflated asset residency |
| Two snapshots around a repeatable loop | Before and after e.g. entering and leaving a level several times |
| Compare mode | Objects added between the two: a named type and count |
| References-to view | Retention path to the root holding it alive: the real output |
| Snapshot cost | Writes the whole heap to disk and pauses the app; never mid-hitch |

One surviving loop is not a leak: pools, caches and lazy lookups look identical in a single diff. Run the loop several times and confirm the count keeps climbing before naming a leak.

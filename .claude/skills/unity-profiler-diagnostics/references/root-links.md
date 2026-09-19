# Root Links — Unity Profiler and companion packages

Source: the root index pages listed below, as provided for this skill.
Covers: the whole skill — provenance and version anchor for every file in
this folder.

Anchors every link in this folder. Unity's Manual pages for the Profiler are
published unversioned and resolve to the current LTS documentation; the two
companion packages are versioned and pinned here. Anything this skill cites
resolves under one of these roots; the fix a measurement leads to does not
live here at all, and belongs to `unity-engineer` or `tech-lead-performance`.

## Roots

| Root | Holds | Source |
|---|---|---|
| Profiler Manual | The window, its modules, and how a capture is taken | [Unity Profiler](https://docs.unity3d.com/Manual/Profiler.html) |
| Profiling tools overview | How the Profiler, Memory Profiler, and Frame Debugger relate | [Profiling tools reference](https://docs.unity3d.com/Manual/performance-profiling-tools.html) |
| Scripting API | `Unity.Profiling` markers, recorders, and the legacy `Profiling` namespace | [ProfilerMarker](https://docs.unity3d.com/ScriptReference/Unity.Profiling.ProfilerMarker.html) |
| Memory Profiler package | Snapshot capture, comparison, and object-level attribution | [Memory Profiler introduction](https://docs.unity3d.com/Packages/com.unity.memoryprofiler@1.1/manual/memory-profiler-introduction.html) |
| Profile Analyzer package | Multi-frame aggregation and two-dataset comparison | [Profile Analyzer](https://docs.unity3d.com/Manual/com.unity.performance.profile-analyzer.html) |

## Which tool answers which question

| Question | Tool | Source |
|---|---|---|
| Which script is costing frame time | CPU Usage module, Hierarchy sorted by Self time | [CPU Usage module](https://docs.unity3d.com/Manual/ProfilerCPU.html) |
| Is the frame CPU-bound or GPU-bound | Highlights module, then GPU Usage | [Highlights module](https://docs.unity3d.com/Manual/ProfilerHighlights.html) |
| Why did batching break | Frame Debugger — it reports the reason, never a timing | [Frame Debugger](https://docs.unity3d.com/Manual/FrameDebugger.html) |
| Did this change help on average | Profile Analyzer, two captures of comparable length | [Profile Analyzer](https://docs.unity3d.com/Manual/com.unity.performance.profile-analyzer.html) |
| What is retaining memory across a session | Memory Profiler snapshot diff, not the built-in Memory module | [Memory Profiler introduction](https://docs.unity3d.com/Packages/com.unity.memoryprofiler@1.1/manual/memory-profiler-introduction.html) |
| What does this opaque block actually cost | A `ProfilerMarker` around it | [Adding profiling information to your code](https://docs.unity3d.com/Manual/profiler-adding-information-code-intro.html) |

Both package pins above track the version installed in the project rather
than the Editor version — read the actual version from `Window > Package
Manager` or `Packages/manifest.json` and substitute the `@` segment before
following a package link. The Manual links carry no version segment; append
one (`docs.unity3d.com/<version>/Documentation/Manual/…`) only when a
specific Editor release's wording has to be confirmed.

# Profiler Window and Modules — picking a module and reading it correctly

Sources: [Profiler window reference](https://docs.unity3d.com/Manual/ProfilerWindow.html), [CPU Usage module](https://docs.unity3d.com/Manual/ProfilerCPU.html), [GPU Usage module](https://docs.unity3d.com/Manual/ProfilerGPU.html), [Rendering module](https://docs.unity3d.com/Manual/ProfilerRendering.html), [Memory module](https://docs.unity3d.com/Manual/ProfilerMemory.html), [Highlights module](https://docs.unity3d.com/Manual/ProfilerHighlights.html).
Covers: SKILL.md §4 — **"Name the question before opening a module"**, **"Capture the hitch inside the Profiler's frame buffer"**, **"Attribute a GC spike to the frame that allocated, not the frame that stalled"**.

Which module answers which question, and the reading mistakes each one invites.
Memory growth over a session is deliberately not settled here — the built-in
Memory module cannot compare two points in time, and [memory-profiler.md](memory-profiler.md) owns that.

## Module selection

| Module | What it decides | Source |
|---|---|---|
| CPU Usage | Which thread and which managed call own the frame time; the only module carrying the GC Alloc column | [CPU Usage module](https://docs.unity3d.com/Manual/ProfilerCPU.html) |
| GPU Usage | Whether the GPU rather than the CPU is the limit — unavailable in a plain Editor session, and unsupported on some platform and graphics-API combinations, so confirm it populates before planning around it | [GPU Usage module](https://docs.unity3d.com/Manual/ProfilerGPU.html) |
| Rendering | Batches, SetPass calls, triangle and vertex counts — spots a batching regression, but never says which object caused it | [Rendering module](https://docs.unity3d.com/Manual/ProfilerRendering.html) |
| Memory | A quick per-frame total; its Simple view holds one point in time and cannot diff two | [Memory module](https://docs.unity3d.com/Manual/ProfilerMemory.html) |
| Highlights | CPU-versus-GPU-bound verdict against a target frame rate, at a glance, before committing to a deeper module | [Highlights module](https://docs.unity3d.com/Manual/ProfilerHighlights.html) |

## Reading a CPU capture

| Subject | What it decides | Source |
|---|---|---|
| Timeline view | Shows work laid out per thread, so a main-thread stall is visually distinguishable from job-worker or render-thread work — the right first view for a spike of unknown origin | [CPU Usage module](https://docs.unity3d.com/Manual/ProfilerCPU.html) |
| Hierarchy view | Merges every call of the same marker into one row; sort by Self time to find the expensive call rather than its callers | [CPU Usage module](https://docs.unity3d.com/Manual/ProfilerCPU.html) |
| Raw Hierarchy view | Keeps each call site separate instead of merging them — use it when one instance out of many is the outlier and the merged total hides it | [CPU Usage module](https://docs.unity3d.com/Manual/ProfilerCPU.html) |
| `EditorLoop` marker | Editor-only work counted inside the frame time an Editor capture reports; its presence is what makes an Editor number unusable as a build figure | [Profiler window reference](https://docs.unity3d.com/Manual/ProfilerWindow.html) |
| GC Alloc column | Bytes allocated in that frame — the frame that stalls is the frame that collected, so read the column across the surrounding frames to find the code that caused it | [CPU Usage module](https://docs.unity3d.com/Manual/ProfilerCPU.html) |

## Capture mechanics

| Subject | What it decides | Source |
|---|---|---|
| Retained frame count | The window keeps a bounded window of frames and discards the oldest, so a hitch noticed late is already gone; raise the count in Preferences before chasing an intermittent spike | [Profiler window reference](https://docs.unity3d.com/Manual/ProfilerWindow.html) |
| Record toggle and pause | Pausing on the spike frame is what preserves it for inspection; leaving recording on overwrites it | [Profiler window reference](https://docs.unity3d.com/Manual/ProfilerWindow.html) |
| Saving a capture | A saved `.data` capture is what the Profile Analyzer consumes for a before-and-after comparison, so save both sides at capture time rather than re-running later | [Profiler window reference](https://docs.unity3d.com/Manual/ProfilerWindow.html) |
| First frames of a capture | Carry one-time costs — shader warm-up, first-time allocations, scene load tails — and are not representative of steady state | [Collecting performance data](https://docs.unity3d.com/Manual/profiler-profiling-applications.html) |

**Critical caveat**: the Rendering module tells you batching regressed and the
Frame Debugger tells you why — neither substitutes for the other, and a
timing module will never name the material or object that broke a batch.

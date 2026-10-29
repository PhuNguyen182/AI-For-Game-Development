# Profiler Window and Modules

Docs: https://docs.unity3d.com/Manual/ — pages `ProfilerWindow.html`, `ProfilerCPU.html`, `ProfilerGPU.html`, `ProfilerRendering.html`, `ProfilerMemory.html`, `ProfilerHighlights.html`, `profiler-profiling-applications.html`.

## Module selection
| Module | Answers |
|---|---|
| CPU Usage | Which thread and managed call own frame time; the only module with the GC Alloc column |
| GPU Usage | Whether the GPU is the limit; unavailable in a plain Editor session and on some platform/graphics-API combinations |
| Rendering | Batches, SetPass calls, triangle/vertex counts; spots a batching regression, never names the object |
| Memory | Quick per-frame total; Simple view is one point in time and cannot diff (use [memory-profiler.md](memory-profiler.md)) |
| Highlights | CPU- vs GPU-bound against a target frame rate, before committing to a deeper module |

## Reading a CPU capture
| Subject | Rule |
|---|---|
| Timeline | Work per thread; separates a main-thread stall from job-worker or render-thread work. First view for a spike of unknown origin |
| Hierarchy | Merges calls of one marker; sort by Self time to find the expensive call, not its callers |
| Raw Hierarchy | Keeps each call site; use when one instance out of many is the outlier |
| `EditorLoop` | Editor-only work inside an Editor capture's frame time; why Editor numbers are unusable as build figures |
| GC Alloc column | Bytes allocated that frame; the stalling frame collected, so read surrounding frames |

## Capture mechanics
| Subject | Rule |
|---|---|
| Retained frame count | Bounded; oldest frames discarded. Raise it in Preferences before chasing an intermittent spike |
| Record / pause | Pause on the spike to preserve it; recording on overwrites it |
| Saving | Save the `.data` capture of both sides at capture time; the Profile Analyzer consumes it |
| First frames | Carry shader warm-up, first-time allocations, scene-load tails; not steady state |

The Rendering module says batching regressed; the Frame Debugger says why. Neither substitutes for the other.

---
name: unity-profiler-diagnostics
description: "Measure Unity performance before claiming it: Profiler CPU/GPU/Memory modules, GC Alloc, Deep Profiling, Frame Debugger, Profile Analyzer, Memory Profiler, ProfilerMarker/ProfilerRecorder, device profiling over adb. Use when a number is needed."
user-invocable: false
---

# Unity Profiler Diagnostics

Not for: pass/fail against a budget (`performance-budget-verification`), choosing the fix incl. deep native, GPU and leak work (`unity-performance-engineer`), rendering configuration (`unity-urp-rendering`, `unity-hdrp-rendering`), job scheduling (`unity-job-system-and-burst`), Burst output (`unity-burst-compiler`), Audio module voice/DSP/streaming metrics (`unity-audio-mixer`).
Docs: https://docs.unity3d.com/Manual/Profiler.html — unversioned (Editor-current). Memory Profiler: `.../Packages/com.unity.memoryprofiler@1.1/manual/` — the `@1.1` tracks the package version in `Packages/manifest.json`, not the Editor.

| Reference | Read when |
|---|---|
| [profiler-window-and-modules.md](references/profiler-window-and-modules.md) | Picking a module, or a capture reads implausibly |
| [device-and-remote-profiling.md](references/device-and-remote-profiling.md) | The number must represent a real device, or the target dropdown is empty |
| [frame-debugger-and-profile-analyzer.md](references/frame-debugger-and-profile-analyzer.md) | Batching regressed, or a before/after claim needs evidence |
| [memory-profiler.md](references/memory-profiler.md) | Memory grows over a session or a leak is suspected |
| [custom-instrumentation.md](references/custom-instrumentation.md) | A cost is real but invisible in the default hierarchy, or a counter must be read in-game |

## Steps
1. **Name the question, then pick the module** per [profiler-window-and-modules.md](references/profiler-window-and-modules.md): script cost → CPU Usage; GPU-bound? → Highlights then GPU Usage; batching → Rendering then Frame Debugger; session growth → Memory Profiler snapshot pair; opaque block → `ProfilerMarker`.
2. **Profile a Development Build on the target device before quoting any number** ([device-and-remote-profiling.md](references/device-and-remote-profiling.md)). An Editor capture includes `EditorLoop` and has no mobile thermal or memory behaviour: it is a hypothesis, a device capture is evidence.
3. **Keep the hitch in the frame buffer** — the window discards the oldest frames; raise the retained count or pause on the spike.
4. **Deep Profiling locates a cost, never quotes one** — it instruments every managed call and inflates numbers. Re-measure with it off before reporting a figure; in a player build it needs the build-time option and depends on scripting backend.
5. **Attribute a GC spike to the frame that allocated, not the one that stalled** — collection lags allocation. Sort CPU Hierarchy by GC Alloc across surrounding frames; any non-trivial per-frame allocation in `Update`/`FixedUpdate` is a finding even when cheap (`csharp-standards`).
6. **Batching or draw-call regression → Frame Debugger** (gives the batch-break reason, never timings) per [frame-debugger-and-profile-analyzer.md](references/frame-debugger-and-profile-analyzer.md).
7. **Back any "faster"/"helped" claim with a Profile Analyzer comparison** — same device, scene and similar frame count; a single frame is noise. Quote median and mean when they disagree; if the median drops while the max rises, report both as a hitching trade-off.
8. **Diff two Memory Profiler snapshots from a player build**, repeating the loop several times; Reserved growth alone is not a leak ([memory-profiler.md](references/memory-profiler.md)).
9. **Instrument with a `static readonly ProfilerMarker`**; use `ProfilerRecorder` to read a value inside the running game ([custom-instrumentation.md](references/custom-instrumentation.md)).
10. **Report attribution and route the fix** to `unity-performance-engineer`: module, environment, frame range, Deep Profiling on/off. Never turn a measurement into a design decision here.

## Never
- Expect GPU Usage data from a plain Editor session or every platform/graphics API; confirm it populates first.
- Leave a `ProfilerRecorder` undisposed — it keeps collecting.
- Build new instrumentation on `Profiler.BeginSample` — it passes its label string every call.

## Output
```
## Profiler Session — <what was measured>
- Question: <claim or hypothesis tested>
- Environment: <Editor / Development Build> — device: <model, tier>, connection: <adb / WiFi>
- Deep Profiling: <on for localization only / off for the reported figure>
- Module or tool: <...>
- Frames: <count and range — single capture or aggregate>
- Finding: <metric, value, unit>
- Attribution: <system, call, object or material>
- Before and after: <both figures and how made comparable — or "not applicable">
- Routed to: <unity-performance-engineer / unity-urp-rendering / not applicable>
- Known limitations: <...>
```
On request only, add `Latent concerns` and `Future remediation`, each with its trigger.

## Example
- "Editor frame time is 8 ms, so we are within mobile budget" → declined: `EditorLoop` and Editor-only work sit inside that figure and thermal throttling is invisible; rebuilt as a Development Build and captured on the low-tier handset after two minutes of running.

---
name: unity-profiler-diagnostics
description: >
  Technique for measuring and diagnosing performance with Unity's Profiler
  toolset — the Profiler window's CPU/GPU Usage, Rendering, Memory, and
  Highlights modules, the Frame Debugger for per-draw-call inspection, the
  Profile Analyzer package for multi-frame comparison, the Memory Profiler
  package for snapshot-based memory analysis, custom instrumentation
  (`ProfilerMarker`/`ProfilerRecorder`/`Profiler.BeginSample`), and
  editor/development-build/remote-device profiling setup. Use this whenever a
  performance claim needs a real measurement, or before/after any change
  claimed to improve frame time, GC allocation, draw calls, or memory. Do not
  use this to decide *what* optimization to apply — hot-path allocation
  rules, pooling, batching, and algorithm/data-structure choice are
  `performance-and-algorithms.md`; deep memory-leak/GPU-level/native-plugin
  investigation once a measurement has already pinpointed the bottleneck is
  `tech-lead-performance`'s escalation territory. Do not use this for
  rendering-path/Renderer Feature configuration itself — `unity-urp-rendering`
  / `unity-hdrp-rendering` own that, this skill only supplies the
  measurement that justifies the choice.
---

# Unity Profiler Diagnostics — Measuring Before Claiming

Sources: see [references/](references/) for the Unity Manual/Scripting API root links, split by topic — [root-links.md](references/root-links.md), [profiler-window-and-modules.md](references/profiler-window-and-modules.md), [frame-debugger-and-profile-analyzer.md](references/frame-debugger-and-profile-analyzer.md), [memory-profiler.md](references/memory-profiler.md), [custom-instrumentation.md](references/custom-instrumentation.md), [device-and-remote-profiling.md](references/device-and-remote-profiling.md).

## 1. Objective
Turn a performance question ("is this fast enough? did this change help?") into an actual measurement using the right Profiler module or tool, read that measurement correctly, and attribute the cost to the right layer (CPU script, GC allocation, GPU/rendering, memory) instead of guessing from folklore or Big-O reasoning alone.

## 2. Role
Act as the measurement specialist: you set up the right profiling session (Editor vs. Development Build vs. remote device, deep profiling on/off), pick the right module/tool for the question being asked, and report what the data actually shows — you don't decide the fix, you supply the evidence the fix decision (in `performance-and-algorithms.md`, `unity-engineer`, or `tech-lead-performance`) is based on.

## 3. When to invoke this skill
- Before adopting any performance-motivated change — a rendering-path switch, an algorithm/data-structure substitution, a pooling change — per `performance-and-algorithms.md`'s "no folklore, verify with a measurement" rule.
- After applying a performance fix, to confirm it actually helped (frame time, GC alloc/frame, draw calls, memory) rather than assuming it did.
- Diagnosing a reported frame hitch, GC spike, memory growth, or draw-call/batching regression — picking CPU Usage vs. GPU Usage vs. Rendering vs. Memory module by what's actually being asked.
- Setting up a Development Build with Autoconnect/Deep Profiling, or connecting the Profiler to a remote Android/iOS device, when Editor-only profiling numbers aren't representative of the real target platform.
- Adding custom instrumentation (`ProfilerMarker`, `ProfilerRecorder`, a custom Profiler module/counter) to make an otherwise-opaque system's cost visible in the Profiler window.
- Negative trigger: once a bottleneck is measured and localized, applying the actual fix — allocation removal, pooling, algorithm/data-structure choice, LOD/batching/culling setup — is `performance-and-algorithms.md`'s and `unity-engineer`'s job, not this skill's.
- Negative trigger: a bottleneck that's genuinely deep (native plugin, GPU-level intervention, a memory leak routine profiling can't localize) escalates to `tech-lead-performance` — this skill gets you the initial measurement that justifies that escalation, it doesn't do the deep fix itself.
- Negative trigger: choosing or configuring a rendering path, Renderer Feature, or Custom Pass Volume is `unity-urp-rendering`/`unity-hdrp-rendering`'s scope — this skill only supplies the frame-time/GPU-time evidence those decisions should be based on.

## 4. How to use this skill
1. **Start from the actual question, not a module by default.** "Is a script spiking CPU time?" → CPU Usage module. "Is the GPU the bottleneck?" → GPU Usage module (Play Mode/build only, not in-Editor). "Are draw calls/batches too high?" → Rendering module, then Frame Debugger for the per-call breakdown. "Is memory growing or GC spiking?" → Memory module for the quick check, Memory Profiler package for a real snapshot comparison.
2. **Profile in the right environment for the question.** Editor profiling includes Editor-only overhead and isn't representative of a real device's frame budget — for a platform-accurate number (especially mobile), use a Development Build with **Autoconnect Profiler** enabled, and connect over WiFi/ADB to the actual target device per `device-and-remote-profiling.md`. Never sign off a mobile performance claim on Editor-only numbers alone.
3. **Use Deep Profiling deliberately, not by default.** Deep Profiling instruments every method call and gives fine-grained attribution, but adds significant overhead that skews absolute frame-time numbers — use it to *find* which function is expensive, then re-measure with it off to get the real cost.
4. **CPU Usage module**: use the Timeline view to see per-frame spikes and which thread they're on (main thread vs. render thread vs. job worker); use the Hierarchy view, sorted by Total/Self time, to find the actual expensive call rather than guessing from the code's apparent complexity. A method that looks O(n²) in the code but is called with a tiny bounded N may not show up at all — trust the measurement over the Big-O guess, per `performance-and-algorithms.md`.
5. **GC allocation tracking**: the CPU Usage module's GC Alloc column (and the Memory module's GC-related counters) show per-frame allocation — any non-zero, non-negligible number inside a hot path (`Update`/`FixedUpdate`/per-tick) is a violation of the no-per-frame-allocation rule in `coding-principles.md`/`performance-and-algorithms.md` and should be flagged even if the frame-time cost looks small, since GC pressure compounds over the session.
6. **Rendering module + Frame Debugger**: use the Rendering module's batches/SetPass calls/triangles chart to spot a regression at a glance, then open the Frame Debugger from it to step through the actual draw call sequence and see exactly which object/material broke batching (a new material instance, an unbatched dynamic object, an unnecessary SetPass call).
7. **Profile Analyzer for multi-frame claims.** A single-frame CPU Usage snapshot is noisy — for "did this change actually help on average," capture a comparable number of frames before and after the change with the Profile Analyzer package and compare the aggregated median/distribution, not one cherry-picked frame.
8. **Memory Profiler package for real memory investigation.** The built-in Memory module's Simple view is a quick sanity check only; for an actual leak/growth investigation, take a Memory Profiler package snapshot (or two, before/after a suspected leak point) and diff them — the built-in module can't do that comparison.
9. **Custom instrumentation for opaque systems.** When a suspected-expensive block doesn't show up clearly in the default hierarchy (e.g. inside a third-party plugin or a batch of similar calls worth isolating), wrap it in a `static readonly ProfilerMarker` (`Begin`/`End` or `.Auto()`) rather than `Profiler.BeginSample`/`EndSample` — `ProfilerMarker` is the lower-overhead, Burst/job-compatible option and is the currently-recommended API. Use `ProfilerRecorder` when the number needs to be read back at runtime (e.g. an in-game debug overlay), not just viewed in the Profiler window.
10. **Attribute the result honestly, then hand off.** State what the data actually showed (which module, which frame range, Editor vs. device, Deep Profiling on/off) and where the cost lives — don't convert a measurement into a fix recommendation that belongs to a different skill/role; report the finding and route it (`performance-and-algorithms.md` for the fix pattern, `tech-lead-performance` if it's genuinely deep).

## 5. Specific goals / tasks this skill performs
- Picking the right Profiler module (CPU/GPU Usage, Rendering, Memory, Highlights) for a specific performance question.
- Setting up Development Build + Autoconnect/Deep Profiling, and remote Android/iOS device profiling, when Editor-only numbers aren't representative.
- Using the Frame Debugger to attribute a draw-call/batching regression to the specific object/material responsible.
- Using the Profile Analyzer package to compare before/after performance across multiple frames instead of one noisy snapshot.
- Using the Memory Profiler package to snapshot and diff memory usage for a real leak/growth investigation.
- Adding `ProfilerMarker`/`ProfilerRecorder` instrumentation to make an opaque system's cost visible.
- Out of scope: deciding and implementing the actual optimization (`performance-and-algorithms.md`, `unity-engineer`); deep native/GPU-level/leak root-causing once localized (`tech-lead-performance`); rendering-path/Renderer Feature/Volume configuration itself (`unity-urp-rendering`/`unity-hdrp-rendering`).

## 6. Output format
```
## Profiler Session — <what was measured>
- Question: <what claim/hypothesis this measurement is checking>
- Environment: Editor / Development Build (device: <target>) — Autoconnect: yes/no, Deep Profiling: yes/no
- Module/tool used: CPU Usage / GPU Usage / Rendering + Frame Debugger / Memory / Memory Profiler package / Profile Analyzer / custom marker
- Frames captured: <count/range> — single-frame snapshot / multi-frame aggregate
- Finding: <what the data actually shows — module, metric, value>
- Attribution: <which system/call/object the cost belongs to>
- Before/after comparison (if applicable): <numbers>
- Routed to: <performance-and-algorithms.md fix pattern / tech-lead-performance escalation / unity-urp-rendering / n-a>
- Known limitations: <e.g. Editor-only numbers not device-representative, single-frame noise>
```

## 7. Examples
**Example 1**
- Input: "The mobile build feels like it drops frames during the wave-spawn burst — is it actually a problem, and what's causing it?"
- Output: built a Development Build with Autoconnect Profiler enabled, connected over ADB to the target mid-tier Android device, captured the CPU Usage Timeline across the spawn burst; Hierarchy view (sorted by Self time) showed a `List<T>.Contains` linear scan inside the spawn-validation loop dominating the spike, plus a non-zero GC Alloc column from a `new List<T>` per spawn call — routed the allocation-per-call finding to `performance-and-algorithms.md`'s data-structure and pooling guidance rather than fixing it here.

**Example 2**
- Input: "We switched the boss arena from Forward to Forward+ — did it actually reduce frame time on the mid-tier device tier?"
- Output: captured a comparable ~300-frame window on both the pre-change and post-change builds on the same physical device, compared the two captures in the Profile Analyzer package rather than eyeballing single frames; median CPU frame time dropped but GPU Usage module showed the GPU became the new bottleneck at high light counts — reported both numbers back to `unity-urp-rendering` instead of declaring the switch an unconditional win.

## 8. Edge cases & guardrails
- Never sign off a performance claim — especially mobile — on Editor-only profiling numbers; profile on a Development Build against the real target device class.
- Never leave Deep Profiling on when reporting an absolute frame-time number — it's for finding the culprit, not for the final measurement.
- Never treat a single-frame CPU Usage snapshot as proof of a trend — use the Profile Analyzer package for any "did this help on average" claim.
- A non-zero GC Alloc in a hot path is worth flagging even when the frame-time cost looks small — allocation pressure compounds over a session; don't dismiss it because one frame's cost looks negligible.
- Don't convert a measurement into an optimization recommendation that belongs to `performance-and-algorithms.md`/`tech-lead-performance` — report the finding and route it, don't implement the fix inside this skill.
- Prefer `ProfilerMarker` over `Profiler.BeginSample`/`EndSample` for new custom instrumentation — lower overhead and Burst/job-compatible.
- The built-in Memory module's Simple view cannot diff two points in time — use the Memory Profiler package's snapshot comparison for any real leak investigation, not the Simple view alone.
- GPU Usage module data is only available in Play Mode or an actual build, never in the plain Editor — don't expect GPU timing from an Editor-only CPU Usage capture.

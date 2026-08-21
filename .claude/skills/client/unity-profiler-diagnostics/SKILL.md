---
name: unity-profiler-diagnostics
description: >
  Technique for measuring Unity performance before claiming it — the Profiler
  window's CPU Usage, GPU Usage, Rendering, Memory and Highlights modules,
  Timeline versus Hierarchy views, the GC Alloc column, Deep Profiling, the
  Frame Debugger's batch-break attribution, the Profile Analyzer and Memory
  Profiler packages, `ProfilerMarker`, `ProfilerRecorder`,
  `Profiler.BeginSample`, and Development Build profiling over adb or WiFi
  against a real device. Use when a frame hitch, GC spike, draw-call jump or
  memory growth needs a number. Not for: choosing the fix
  (`unity-engineer`); deep native, GPU or leak root-causing
  (`tech-lead-performance`); rendering configuration itself
  (`unity-urp-rendering`, `unity-hdrp-rendering`); job scheduling
  (`unity-job-system-and-burst`); Burst output (`unity-burst-compiler`).
---

# Unity Profiler Diagnostics — Modules, Frame Debugger, Memory Snapshots, Custom Markers

## Bundled resources

### References
Read-only context, loaded on demand so SKILL.md itself stays short.

| File | Contents | Read when |
|---|---|---|
| [root-links.md](references/root-links.md) | Manual and package roots, version pins, which tool answers which class of question | Starting any measurement, or confirming which package the project actually installs |
| [profiler-window-and-modules.md](references/profiler-window-and-modules.md) | Module inventory, Timeline/Hierarchy/Raw Hierarchy, GC Alloc, frame-buffer limit, `EditorLoop` | Picking a module, or a capture reads implausibly |
| [device-and-remote-profiling.md](references/device-and-remote-profiling.md) | Development Build flags, adb and WiFi connection, Deep Profiling availability per backend | The number has to represent a real device rather than the Editor |
| [frame-debugger-and-profile-analyzer.md](references/frame-debugger-and-profile-analyzer.md) | Draw-call stepping, the batch-break reason field, multi-frame aggregate comparison | Batching regressed, or a before-and-after claim needs evidence |
| [memory-profiler.md](references/memory-profiler.md) | Snapshot capture and diff, Reserved versus Used, managed versus native breakdown | Memory grows over a session, or a leak is suspected |
| [custom-instrumentation.md](references/custom-instrumentation.md) | `ProfilerMarker`, `ProfilerRecorder`, `CustomSampler`, counters, build-stripping behaviour | A cost is real but invisible in the default hierarchy |

## 1. Objective
Turn a performance question into a number that survives scrutiny, and attribute that number to the right layer — script CPU, GC allocation, GPU, draw calls, memory. The failures this prevents are all quiet ones: an Editor capture whose frame time is mostly `EditorLoop`, a Deep Profiling number quoted as the real cost, a GC spike blamed on the frame that stalled rather than the frames that allocated, a Reserved-memory chart read as a leak, and a single cherry-picked frame presented as a trend.

## 2. Role
Act as the measurement specialist for the client track — the tool reached for whenever someone is about to assert that something is slow, or that a change made it faster. You produce evidence and attribution; you do not choose or apply the optimization, and you hand the finding to whoever owns the fix.

## 3. When to invoke this skill
- A frame hitch, stutter, GC spike, memory growth, or draw-call/batching regression is reported and needs localizing.
- Before adopting any performance-motivated change, and again after, per `performance-and-algorithms.md`'s Verification section.
- Editor numbers look fine but the build on the target device does not, or a mobile claim needs a device-representative capture.
- A system's cost is real but invisible in the Profiler hierarchy — a third-party plugin, a batch of similar calls, or work hidden inside a native call.
- A runtime debug overlay needs to read a profiler counter back in the running game.
- Negative trigger: applying the fix once the bottleneck is localized — allocation removal, pooling, data-structure choice, LOD and batching setup — that is `unity-engineer`'s work, guided by `performance-and-algorithms.md`.
- Negative trigger: a bottleneck that stays unexplained after a competent capture — a native plugin, a GPU-level intervention, a leak the snapshot diff cannot localize — escalates to `tech-lead-performance`; this skill supplies the measurement that justifies the escalation.
- Negative trigger: choosing a rendering path, Renderer Feature, or quality tier — that is `unity-urp-rendering` and `unity-hdrp-rendering`; this skill supplies the frame-time evidence those choices are argued from.
- Negative trigger: job dependency chains, batch sizing, and scheduling overhead are `unity-job-system-and-burst`, and reading the Burst Inspector's generated assembly is `unity-burst-compiler` — this skill only establishes that worker threads are or are not the cost.

## 4. How to use this skill
1. **Name the question before opening a module** — module choice is determined by the question, not by habit, per [profiler-window-and-modules.md](references/profiler-window-and-modules.md). Script cost goes to CPU Usage, "is the GPU the limit" goes to GPU Usage or Highlights, batching goes to Rendering then the Frame Debugger, and growth over a session goes to a Memory Profiler snapshot pair. Opening CPU Usage for a GPU-bound frame produces a real number that answers nothing; [root-links.md](references/root-links.md) states which tool owns which class of question.
2. **Profile a Development Build on the target device before quoting any number** — an in-Editor capture carries `EditorLoop` and Editor-only overhead in the same frame time it reports, and mobile thermal and memory behaviour has no Editor equivalent at all. [device-and-remote-profiling.md](references/device-and-remote-profiling.md) holds the build flags and the adb and WiFi connection steps. An Editor capture is a hypothesis; a device capture is evidence.
3. **Capture the hitch inside the Profiler's frame buffer** — the window retains a bounded number of frames and discards the oldest, so a hitch noticed a few seconds late is already gone. Raise the retained frame count, or pause on the spike, rather than reproducing it repeatedly and hoping to catch it.
4. **Use Deep Profiling to localize a cost, never to quote one** — it instruments every managed call and inflates the numbers it reports, so the culprit it names is trustworthy and its magnitude is not. Re-measure with it off before reporting a figure, and check [device-and-remote-profiling.md](references/device-and-remote-profiling.md) first when the target is a player build, where availability depends on the scripting backend.
5. **Attribute a GC spike to the frame that allocated, not the frame that stalled** — the collection runs some frames after the allocations that caused it, so the stall frame is usually innocent. Sort the CPU Usage Hierarchy by GC Alloc across the surrounding frames and treat any non-trivial per-frame allocation in `Update`/`FixedUpdate` as a finding in its own right, per `coding-principles.md`'s Performance discipline section, even when its frame-time cost looks negligible.
6. **Take a batching or draw-call regression to the Frame Debugger, not to a timing module** — it reports why a draw call could not be batched with the one before it, which is the actual answer, per [frame-debugger-and-profile-analyzer.md](references/frame-debugger-and-profile-analyzer.md). It gives no timings at all, so it identifies the cause and never the cost.
7. **Back any before-and-after claim with the Profile Analyzer** — a single frame is noise, and median frame time across a comparable window is the only honest form of "this change helped", per [frame-debugger-and-profile-analyzer.md](references/frame-debugger-and-profile-analyzer.md). Capture both sides on the same device, in the same scene, over a similar frame count.
8. **Diff two Memory Profiler snapshots rather than reading a single total** — a lone total says nothing about direction, and Reserved memory is what Unity holds from the operating system rather than what the game is using, so a rising Reserved chart is not by itself a leak, per [memory-profiler.md](references/memory-profiler.md).
9. **Instrument an opaque system with a `static readonly ProfilerMarker`** — it is cheaper than `Profiler.BeginSample`, is Burst- and job-compatible, and strips itself from non-development builds, per [custom-instrumentation.md](references/custom-instrumentation.md). Reach for `ProfilerRecorder` instead when the value must be read back inside the running game rather than viewed in the window.
10. **Report the attribution and route the fix** — state the module, the environment, the frame range, and whether Deep Profiling was on, then hand the finding to `unity-engineer` for an ordinary fix or `tech-lead-performance` for a deep one. A measurement converted into someone else's design decision stops being evidence.

## 5. Specific goals / tasks this skill performs
- Choosing the module or tool that answers a specific performance question.
- Setting up Development Build profiling and connecting to an Android or iOS device over adb or WiFi.
- Localizing a CPU spike through Timeline and Hierarchy views, with Deep Profiling used only as a locator.
- Attributing GC allocation to the code that allocated rather than the frame that collected.
- Attributing a batching regression to the specific object, material, or state change through the Frame Debugger.
- Proving or disproving a before-and-after performance claim with a Profile Analyzer comparison.
- Investigating memory growth through a Memory Profiler snapshot diff.
- Adding `ProfilerMarker`/`ProfilerRecorder` instrumentation and runtime counter readback.
- Out of scope: applying the optimization (`unity-engineer`); deep native, GPU, or leak root-causing (`tech-lead-performance`); rendering configuration (`unity-urp-rendering`, `unity-hdrp-rendering`); job scheduling analysis (`unity-job-system-and-burst`); Burst compilation output (`unity-burst-compiler`).

## 6. Output format
```
## Profiler Session — <what was measured>
- Question: <the claim or hypothesis this capture tests>
- Environment: <Editor / Development Build> — device: <model and tier>, connection: <adb / WiFi>
- Deep Profiling: <on for localization only / off for the reported figure>
- Module or tool: <CPU Usage / GPU Usage / Rendering + Frame Debugger / Memory Profiler / Profile Analyzer / custom marker>
- Frames: <count and range — single capture or aggregate>
- Finding: <metric, value, unit>
- Attribution: <the system, call, object, or material the cost belongs to>
- Before and after: <both figures and how they were made comparable — or "not applicable">
- Routed to: <unity-engineer / tech-lead-performance / unity-urp-rendering / not applicable>
- Layer: <Game.Client.* instrumentation, Editor-only capture, or both>
- Known limitations: <...>
```

**Extended report — emit ONLY when the requester asks for it.** It replaces the one-line `Known limitations` above with all three fields:
```
- Known limitations: <what this measurement does not establish>
- Latent concerns: <failure modes not yet triggered: assumptions that hold only on this device tier, thresholds not yet reached, trade-offs knowingly deferred>
- Future remediation: <the concrete fix for each concern above, each with the condition that should trigger it>
```

## 7. Examples
**Example 1**
- Input: "The mobile build stutters when a wave spawns. Is it real, and what is causing it?"
- Output: built with Development Build and Autoconnect Profiler, connected over adb to the mid-tier Android target, and raised the retained frame count so the burst stayed in the buffer. Deep Profiling located a linear `List<T>.Contains` scan inside spawn validation, then a second capture with it off gave the honest cost. The GC Alloc column showed the allocation happening several frames before the stall, in the spawn loop rather than in the frame that visibly dropped. Reported both findings to `unity-engineer` and made no fix here.

**Example 2**
- Input: "Frame time in the Editor is 8ms, so we are well inside budget on mobile."
- Output: declined — the Editor capture attributes a large share of that frame to `EditorLoop` and Editor-only work that no build runs, and it says nothing about thermal throttling or memory pressure on the device. Rebuilt as a Development Build and captured on the actual low-tier handset, where the same scene sat well outside budget once the device had been running for two minutes.

**Example 3**
- Input: "Total memory is climbing all session, so something is leaking."
- Output: captured two Memory Profiler snapshots twenty minutes apart from the player build and diffed them. Reserved memory had grown, which is Unity holding pages from the operating system rather than the game consuming them, but the managed heap diff showed a genuine growth: event handlers retained on destroyed objects, keeping their whole reference graph alive. Routed the unsubscribe fix to `unity-engineer`, per `performance-and-algorithms.md`'s Memory discipline section.

## 8. Edge cases & guardrails
- Never quote a frame time captured with Deep Profiling on — it is a locator, and the number it reports includes its own instrumentation cost.
- Never present an Editor capture as a mobile result — `EditorLoop` and Editor-only overhead sit inside the frame time it reports.
- Never treat one frame as a trend — use the Profile Analyzer for any claim containing the words "faster" or "helped".
- Never read rising Reserved memory as a leak — it is memory held from the operating system, not memory in use; the managed and native breakdowns are what move the argument.
- Never assume the stalling frame is the allocating frame — collection lags the allocations that provoked it.
- Never expect timings from the Frame Debugger — it explains why batching broke and nothing about cost.
- Never expect GPU Usage data from a plain Editor session, or from every platform and graphics API — confirm availability before designing a measurement around it, per [profiler-window-and-modules.md](references/profiler-window-and-modules.md).
- Never leave a `ProfilerRecorder` undisposed — it is `IDisposable`, and a leaked recorder keeps collecting, per `coding-principles.md`'s Exception handling section.
- Never build new instrumentation on `Profiler.BeginSample` — it passes its label string on every call; `ProfilerMarker` is the current API.
- Never convert a measurement into an optimization decision inside this skill — report the attribution and route it, or the evidence and the fix stop being separable.

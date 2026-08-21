# Burst Inspector, Menu & Debugging Limits

Sources: [Burst Inspector window](https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/editor-burst-inspector.html), [Burst menu](https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/editor-burst-menu.html), [Debugging and profiling tools](https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/debugging-profiling-tools.html).
Covers: SKILL.md §4 — **"Verify in the Burst Inspector that the target compiled"**.

The only evidence that compilation happened, and what the debugger can and
cannot show once it has. Frame-time evidence for a performance claim still
comes from `unity-profiler-diagnostics`.

| Subject | What it decides | Source |
|---|---|---|
| `Jobs > Burst > Open Inspector` | Lists Compile Targets — a target absent from that list did not compile, whatever attributes it carries | [Burst Inspector](https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/editor-burst-inspector.html) |
| Generated assembly pane | Shows the actual instructions, which is how vectorization is confirmed rather than assumed | [Burst Inspector](https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/editor-burst-inspector.html) |
| `Jobs > Burst > Enable Compilation` | Global off switch — with it off, every measurement is of managed code and every `IsXXXSupported` probe is false | [Burst menu](https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/editor-burst-menu.html) |
| `Jobs > Burst > Safety Checks` | Editor-wide container safety checking; turning it off removes the same protection `DisableSafetyChecks` removes per-target | [Burst menu](https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/editor-burst-menu.html) |
| `Native Debug Compilation` | Enables source-level native debugging at the cost of optimization — a diagnostic mode, never a measurement mode | [Burst menu](https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/editor-burst-menu.html) |
| Breakpoints and Locals in Release | Unreliable in optimized Burst code; variables may be absent or wrong | [Debugging tools](https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/debugging-profiling-tools.html) |
| External profiler symbols | Reads `lib_burst_generated` symbols, which is how compiled frames are attributed in a native profiler | [Debugging tools](https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/debugging-profiling-tools.html) |

**Critical caveat**: a debugged value that looks wrong in optimized Burst code
is more often the debugger than the program. Confirm with a written-out result
in a container before treating it as a bug.

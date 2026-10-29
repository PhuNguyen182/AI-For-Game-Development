# Burst Inspector, menu and debugging limits

Source: [Burst Inspector](https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/editor-burst-inspector.html), [Burst menu](https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/editor-burst-menu.html), [Debugging tools](https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/debugging-profiling-tools.html).

Frame-time evidence still comes from `unity-profiler-diagnostics`.

- `Jobs > Burst > Open Inspector`: Compile Targets lists what compiled; a target absent did not, whatever attributes it carries.
- Generated assembly pane: the actual instructions; confirms vectorization.
- `Jobs > Burst > Enable Compilation`: global switch; off means every measurement is managed and every `IsXXXSupported` probe is false.
- `Jobs > Burst > Safety Checks`: Editor-wide container checks; off removes the protection `DisableSafetyChecks` removes per target.
- `Native Debug Compilation`: source-level native debugging at the cost of optimization; diagnostic only, never for measurement.
- Breakpoints and Locals are unreliable in optimized Burst code; a wrong-looking value is more often the debugger than the program. Confirm by writing the result into a container.
- External profilers attribute compiled frames via `lib_burst_generated` symbols.

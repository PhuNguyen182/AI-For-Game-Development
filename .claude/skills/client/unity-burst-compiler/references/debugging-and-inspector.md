# Debugging, Profiling & the Burst Inspector

Covers SKILL.md step 5 (verifying compilation actually happened, never assuming from the attribute alone).

## Manual
- [Burst Inspector window reference](https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/editor-burst-inspector.html) — `Jobs > Burst > Open Inspector`; Compile Targets list, generated assembly/intermediate-code pane, register highlighting.
- [Burst menu reference](https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/editor-burst-menu.html) — `Jobs > Burst` menu options (Enable Compilation, Safety Checks, Native Debug Compilation, Synchronous Compilation).
- [Debugging and profiling tools](https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/debugging-profiling-tools.html) — managed vs. native debugger attachment, Release-mode breakpoint/Locals-window limitations, Profiler markers, external profilers reading `lib_burst_generated` symbols.

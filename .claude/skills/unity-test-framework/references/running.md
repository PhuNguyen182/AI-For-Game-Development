# Running — Player, command line, TestRunnerApi

Producing a platform build is `build-release-engineer`'s work on the GD's explicit request; this is the configuration it executes.

## Where tests run
- Editor: fastest, the only route for Edit Mode, no platform-specific behaviour.
- Standalone Player: Play Mode tests in a real player — where scripting-backend/platform differences appear.
- `TestPlayerBuildModifier` splits build from run (build on one machine, run on another).

## Command line
| Argument | Note |
|---|---|
| `-runTests` | Mandatory; nothing runs without it |
| `-batchmode` | Pair every time for unattended runs |
| `-testPlatform` | EditMode, PlayMode or a build target; defaults to Edit Mode, so omitting it silently runs the wrong half |
| `-testFilter` | Names or regex on the full test name; supports negation and parameterized-case syntax |
| `-testCategory` | Category list with negation. Intersects with `-testFilter`: no overlap = a successful run of zero tests |
| `-assemblyNames`, `-assemblyType` | Restrict to named assemblies / Editor-only vs platform |
| `-testResults` | Result path; NUnit 3 XML any NUnit reporter reads. Without it CI has nothing to consume |
| `-runSynchronously` | Edit Mode in one Editor update; excludes every multi-frame test |
| `-playerHeartbeatTimeout` | How long to wait for a Player run to report in — the cause of an unexplained hang on a slow device |
| `-buildPlayerPath` | Player output dir instead of a temp dir CI cannot collect |
| `-orderedTestListFile` | Exact order, to reproduce an order-dependent failure |

## `TestRunnerApi` (`UnityEditor.TestTools.TestRunner.Api`, Editor-only)
Use only for real Editor tooling; the window and command line cover routine runs.
- Static members: execute a run from `ExecutionSettings`, register callbacks, retrieve the test tree. Instance members are flagged for obsolescence.
- `Filter`: exact `testNames`, regex `groupNames`, `categoryNames`, `assemblyNames`; fields combine restrictively, and `testMode` must match the assemblies or the run is empty. `ExecutionSettings` carries filters plus target platform and Player-run options.
- `TestRunSettings` applies temporary settings around a run and reverts them; `Filter`/results use the `AssemblyType`, `RunState`, `TestMode` and `TestStatus` enums.
- Callbacks:
  - `ICallbacks` (plus error variant for run-level failures): Editor only, adaptor types.
  - `ITestRunCallback` via `[TestRunCallback]`: Editor and built Player, raw NUnit objects. A reporter for device runs must use this one.

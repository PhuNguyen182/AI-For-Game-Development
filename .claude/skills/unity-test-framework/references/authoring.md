# Authoring — modes, assembly, attributes, async, parameters

## Edit Mode vs Play Mode
| | Edit Mode | Play Mode |
|---|---|---|
| Runs | Editor, no frame loop or physics | Player loop, frames, physics, scene lifecycle |
| Right for | Pure logic (Shared Core) | MonoBehaviour, prefabs, timing, physics |
| Cost | Fast, every change | Enters play per run — a pipeline decision |

## Assembly
- Needs the NUnit and runtime test-runner references to compile attributes. The Editor test-runner reference is needed for Edit-Mode-only constructs and makes the assembly Editor-only, so it cannot run in a Player.
- 2.0: `RequiresPlayMode` at assembly/fixture/test scope lets both modes share one assembly. Split only where the project already does.
- A script outside an assembly that references the framework is never discovered.

## Unity attributes
| Attribute | Effect |
|---|---|
| `UnityTest` | Coroutine test; the only way an assertion spans frames |
| `UnitySetUp`, `UnityTearDown` | Yielding hooks; see [execution-order.md](execution-order.md) |
| `RequiresPlayMode` | Scope needs Play Mode |
| `ConditionalIgnore` | Runtime-registered condition. Missing from the manual's attribute table but ships in the API: use the namespace pages as the catalog |
| `ParameterizedIgnore` | Skip specific argument values (a branch in the body would report a pass) |
| `UnityPlatform` | Gate on the running platform |
| `RequirePlatformSupport` | Gate on installed build support (stops a CI agent failing on a missing module) |
| `PrebuildSetup`, `PostBuildCleanup` | Code around building the test Player; staging must be cleaned up so it is not committed or shipped |
| `TestPlayerBuildModifier` | Edit Player build options or split build from run; lives in `UnityEditor.TestTools`, not the runner namespace |
| `TestRunCallback` | Assembly-scope progress listener that also works in a Player |
| `TestMustExpectAllLogs` | Every log at any level must be expected |
| `PreservedValues` | Literal arguments that survive code stripping in a Player |

Unsupported with `UnityTest`: `Repeat`; `TestCase` and `TestCaseSource` (silently ignored). `Retry` throws in Play Mode.

## Tests spanning time
| Form | Use when |
|---|---|
| Plain test | Assertion holds immediately (default; a frame yield on a same-frame check is slower, not more correct) |
| `[UnityTest]` coroutine | Physics, animation or a state machine must advance over frames |
| Async task test (2.0) | Code under test returns a task |

Edit Mode yield instructions: Enter Play Mode (triggers a domain reload), Exit Play Mode (put it in teardown so a failure does not leave the Editor in play), Recompile scripts, Wait for domain reload (avoids asserting on a half-reloaded domain), or implement `IEditModeTestYieldInstruction` for a custom wait.

## Parameterization
| Source | Plain test | `UnityTest` |
|---|---|---|
| `TestCase`, `TestCaseSource` | yes | silently ignored |
| `Values` | yes | yes |
| `PreservedValues` | yes | yes |

Arguments computed at discovery time are unreliable — use static data.

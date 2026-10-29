# Unity Batchmode Log Signatures

Sources: Unity manual `EditorCommandLineArguments.html`, `LogFiles.html`, `ManagingYourUnityLicense.html` under `https://docs.unity3d.com/Manual/`.

## Order a run passes through

| # | Phase | Failure here means |
|---|---|---|
| 1 | Editor launch (installed, version matches) | Provisioning, not code |
| 2 | Licence acquisition | Licence, not code |
| 3 | Project open, package resolution | Project state, not code |
| 4 | Asset import (`Library` usable or rebuildable) | Project state or cache |
| 5 | Compilation | Compile; an owner per file |
| 6 | `-executeMethod` runs | The build script or the build itself |
| 7 | Player build (`BuildPlayer` called) | Build: IL2CPP, Gradle, Xcode |

Nothing below the failure point is evidence; the first failure is almost always the only real one.

## Signatures

| Line | Class | Rules out |
|---|---|---|
| `No valid Unity Editor license found`, `Failed to activate/update license` | Licence | Everything from compilation down |
| Hub install error, or editor version differing from `ProjectVersion.txt` | Editor provisioning | The project never opened with the right editor |
| `Multiple Unity instances cannot open the same project` | Agent / workspace | A locking failure in the job, not a project fault |
| Package resolution errors, registry timeouts | Project state | Compilation never began |
| Repeated importer errors on assets the diff never touched | Project state, usually stale or mismatched cache | The change under test |
| `error CS****` with file and line | Compile | Any build, packaging or signing cause |
| `Aborting batchmode due to failure` | Depends on the lines above | Nothing by itself; a consequence, never a cause |
| `Build completed with a result of 'Failed'` | Build | Compilation |
| IL2CPP errors, `il2cpp.exe did not run properly` | Build | The C# source |
| Gradle or `xcodebuild` errors after a successful Unity build | Build, packaging side | Everything Unity did |
| Log ends with no result line | Hang, not failure | A code fault; look at the last phase reached and the job timeout |

## Easily confused

| A | B | Distinguishing evidence |
|---|---|---|
| Compile error | Build error | `error CS` appears before any build step line; a build error appears after `Build completed` began or inside IL2CPP/Gradle/Xcode output |
| Build failure | Hang | A failure writes a result line; a hang writes nothing and the job timeout kills it. Retrying a hang wastes the same time again |
| Cache damage | Real regression | Cache damage names assets or packages the diff never touched and reproduces on a warm agent but not a clean one; ask for the clean-run comparison |

When routing, quote the failing line with the ten lines before it: Unity's error line is often a consequence (abort, nested exception, summary) and the cause is above it.

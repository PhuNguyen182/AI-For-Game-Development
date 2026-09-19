# Unity Batchmode Log Signatures — what each line rules in and out

Source: [Unity Editor command line arguments](https://docs.unity3d.com/Manual/EditorCommandLineArguments.html), [Unity log files](https://docs.unity3d.com/Manual/LogFiles.html), [Managing your Unity licence](https://docs.unity3d.com/Manual/ManagingYourUnityLicense.html).
Covers: SKILL.md §4 — **"Rule out the infrastructure classes first, because they invalidate everything downstream"**, **"Separate a compile error from a build error"**.

The Unity-side signatures, ordered the way a run reaches them. Reading them in order is what makes the triage
cheap: each stage the log got past is a set of classes eliminated, and the first failure encountered is
almost always the only real one.

## The order a run passes through

| # | Phase | Reached only if | A failure here means |
|---|---|---|---|
| 1 | Editor launch | The editor is installed and the version matches | Provisioning, not code |
| 2 | Licence acquisition | A seat or lease is available | Licence, not code |
| 3 | Project open, package resolution | The workspace is intact and packages resolve | Project state, not code |
| 4 | Asset import | `Library` is usable or rebuildable | Project state or cache |
| 5 | Compilation | The C# compiles | Compile — an owner per file |
| 6 | `-executeMethod` runs | Everything above succeeded | The build script or the build itself |
| 7 | Player build | The build script called `BuildPlayer` | Build — IL2CPP, Gradle, Xcode |

**Nothing below the failure point is evidence.** A run that failed at 2 says nothing about the code, and a
report claiming otherwise is confidently wrong.

## Signatures

| Line | Class | What it rules out |
|---|---|---|
| `No valid Unity Editor license found`, `Failed to activate/update license` | Licence | Everything from compilation down — none of it ran |
| A Hub install error, or an editor version differing from `ProjectVersion.txt` | Editor provisioning | The project never opened with the right editor |
| `Multiple Unity instances cannot open the same project` | Agent / workspace | A locking failure in the job, not a project fault |
| Package manager resolution errors, registry timeouts | Project state | Compilation never began |
| Repeated importer errors on assets the diff never touched | Project state — usually a stale or mismatched cache | The change under test |
| `error CS****` with file and line | Compile | Any build, packaging or signing cause — `-executeMethod` never ran |
| `Aborting batchmode due to failure` | Depends on the lines above it | Nothing by itself; it is a consequence, never a cause |
| `Build completed with a result of 'Failed'` | Build | Compilation, which succeeded to reach this point |
| IL2CPP errors, `il2cpp.exe did not run properly` | Build | The C# source, which compiled cleanly first |
| Gradle or `xcodebuild` errors after a successful Unity build | Build, on the packaging side | Everything Unity did |
| The log simply ends, with no result line | Hang, not failure | A code fault — look at the last phase reached and the job's timeout |

## The three that get confused

| A | B | The distinguishing evidence |
|---|---|---|
| Compile error | Build error | `error CS` appears **before** any build step line; a build error appears after `Build completed` began or inside IL2CPP/Gradle/Xcode output |
| Build failure | Hang | A failure writes a result line; a hang writes nothing and the job's own timeout kills it. Retrying a hang wastes the same time again |
| Cache damage | Real regression | Cache damage names assets or packages the diff never touched, and reproduces on a warm agent but not on a clean one. The clean-run comparison is the decisive test, and it is worth asking for |

## What to quote when routing

Quote the failing line **with the ten lines before it**. Unity's error line is frequently a consequence — an
abort, a nested exception, a build-step summary — and the cause is above it. A single-line excerpt is why a
finding gets re-diagnosed by whoever receives it, which is exactly the cycle this skill exists to save.

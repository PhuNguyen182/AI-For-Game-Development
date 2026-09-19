# Build Script and Player Options — the `-executeMethod` entry point

Source: [BuildPipeline.BuildPlayer](https://docs.unity3d.com/ScriptReference/BuildPipeline.BuildPlayer.html), [BuildPlayerOptions](https://docs.unity3d.com/ScriptReference/BuildPlayerOptions.html), [BuildReport](https://docs.unity3d.com/ScriptReference/Build.Reporting.BuildReport.html), [EditorUserBuildSettings](https://docs.unity3d.com/ScriptReference/EditorUserBuildSettings.html), [PlayerSettings](https://docs.unity3d.com/ScriptReference/PlayerSettings.html).
Covers: SKILL.md §4 — **"Drive every build through one `-executeMethod` entry point rather than through CLI build flags"**, **"Decide success from the `BuildReport` summary, never from the artifact existing on disk"**, **"Take version and build number from the CI run rather than from committed project settings"**.

The API surface the entry point is written against, and the arguments it reads from the job. The boundary
this file holds to: it sets what *this run* builds and how it is versioned. Permanent project settings —
quality, stripping level, graphics APIs — belong to `unity-engineer` and are read here, never rewritten.

## The call and its report

| Member | Purpose | Source |
|---|---|---|
| `BuildPipeline.BuildPlayer(BuildPlayerOptions)` | Performs the build and returns a `BuildReport`. The overload returning a report is the one CI uses | [BuildPipeline.BuildPlayer](https://docs.unity3d.com/ScriptReference/BuildPipeline.BuildPlayer.html) |
| `report.summary.result` | `BuildResult.Succeeded` / `Failed` / `Cancelled` / `Unknown` — the run's actual verdict | [BuildReport](https://docs.unity3d.com/ScriptReference/Build.Reporting.BuildReport.html) |
| `report.summary.totalErrors`, `totalWarnings` | Counts to log and to gate on | same |
| `report.summary.outputPath`, `totalSize`, `buildEndedAt` | What to report back to the job: the real artifact path and its size | same |
| `report.steps` | Per-step timings and messages — the material for a slow-build investigation | same |

## `BuildPlayerOptions` fields a CI build sets

| Field | Set it to | Source |
|---|---|---|
| `scenes` | The enabled scenes from `EditorBuildSettings.scenes`, filtered on `scene.enabled` — never a hard-coded list that drifts from the project | [BuildPlayerOptions](https://docs.unity3d.com/ScriptReference/BuildPlayerOptions.html) |
| `locationPathName` | The artifact path passed in by the job, including the correct extension per target | same |
| `target` | The `BuildTarget` matching the invocation's `-buildTarget` | same |
| `targetGroup` | The matching `BuildTargetGroup`; mismatched pairs build the wrong settings set | same |
| `subtarget` | The standalone subtarget (player or dedicated server) where the target has one | same |
| `options` | `BuildOptions.None` for release; `Development`, `AllowDebugging`, `ConnectWithProfiler` for a debuggable build; `CleanBuildCache` when the run must not reuse cached build data | [BuildOptions](https://docs.unity3d.com/ScriptReference/BuildOptions.html) |
| `extraScriptingDefines` | Per-run defines the job supplies, rather than editing the project's define symbols | [BuildPlayerOptions](https://docs.unity3d.com/ScriptReference/BuildPlayerOptions.html) |

Never set `BuildOptions.AutoRunPlayer` or `ShowBuiltPlayer` in a headless job — both try to launch or reveal
the artifact on a machine with no session.

## Per-platform switches the entry point owns

| Setting | Effect | Source |
|---|---|---|
| `EditorUserBuildSettings.buildAppBundle` | `true` produces an `.aab`, `false` an `.apk`. App Distribution accepts either; a store upload needs the bundle | [EditorUserBuildSettings](https://docs.unity3d.com/ScriptReference/EditorUserBuildSettings.html) |
| `EditorUserBuildSettings.exportAsGoogleAndroidProject` | Exports a Gradle project instead of a finished artifact — the route taken when Gradle-level control or external signing is wanted, per `fastlane-mobile-delivery` | same |
| `EditorUserBuildSettings.androidCreateSymbols` | Emits the native symbol package a crash-reporting pipeline needs later | same |
| iOS output | Always an Xcode project, never a finished `.ipa` — packaging and signing are `fastlane-mobile-delivery`'s | [BuildPipeline.BuildPlayer](https://docs.unity3d.com/ScriptReference/BuildPipeline.BuildPlayer.html) |

## Version and build number

| Property | Holds | Source |
|---|---|---|
| `PlayerSettings.bundleVersion` | The human-facing version string, shared by every platform | [PlayerSettings](https://docs.unity3d.com/ScriptReference/PlayerSettings.html) |
| `PlayerSettings.Android.bundleVersionCode` | The integer Android orders releases by; must increase between uploads | [PlayerSettings.Android](https://docs.unity3d.com/ScriptReference/PlayerSettings.Android.html) |
| `PlayerSettings.iOS.buildNumber` | The string iOS orders builds by within one version | [PlayerSettings.iOS](https://docs.unity3d.com/ScriptReference/PlayerSettings.iOS.html) |

Assign all three from arguments the job passes — typically its own monotonic build number — rather than from
the committed values. Two artifacts carrying the same version code cannot be distinguished by a tester, by a
crash report, or by a store, and the resulting confusion is unfixable after the fact.

## Reading the job's arguments

```csharp
// Arguments after -executeMethod reach the process verbatim; parse the pairs the job passes.
static string ReadArgument(string name, string fallback)
{
    string[] args = Environment.GetCommandLineArgs();
    for (int i = 0; i < args.Length - 1; i++)
    {
        if (args[i] == name)
        {
            return args[i + 1];
        }
    }
    return fallback;
}
```

A missing argument takes a stated fallback or fails the run explicitly — never a silent default, because a
build that succeeds for the wrong target or the wrong version costs a full cycle to discover.

## The shape of the entry point

1. Parse arguments — output path, target, version, build number, development flag.
2. Assign version and build-number properties, and any per-run platform switch.
3. Compose `BuildPlayerOptions` from `EditorBuildSettings.scenes` and those arguments.
4. Call `BuildPipeline.BuildPlayer` and keep the returned report.
5. Log `result`, `totalErrors`, `outputPath` and `totalSize` as one line the job can grep.
6. `EditorApplication.Exit(0)` only on `BuildResult.Succeeded`; any other result exits non-zero.

Written this way, the same method serves every job that calls it, and the pipeline's build policy is a
reviewable file in the repository rather than a string inside a job definition.
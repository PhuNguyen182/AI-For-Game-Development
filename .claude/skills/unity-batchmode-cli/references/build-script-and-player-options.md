# Build script and player options

Source: [BuildPipeline.BuildPlayer](https://docs.unity3d.com/ScriptReference/BuildPipeline.BuildPlayer.html), [BuildPlayerOptions](https://docs.unity3d.com/ScriptReference/BuildPlayerOptions.html), [BuildReport](https://docs.unity3d.com/ScriptReference/Build.Reporting.BuildReport.html), [EditorUserBuildSettings](https://docs.unity3d.com/ScriptReference/EditorUserBuildSettings.html), [PlayerSettings](https://docs.unity3d.com/ScriptReference/PlayerSettings.html).

The entry point sets what this run builds and how it is versioned; permanent settings are read, never rewritten.

## Report
`BuildPipeline.BuildPlayer(BuildPlayerOptions)` returns a `BuildReport`.
- `summary.result`: `Succeeded` / `Failed` / `Cancelled` / `Unknown`, the run's verdict.
- `summary.totalErrors`, `totalWarnings`: gate on and log.
- `summary.outputPath`, `totalSize`: report the real artifact and size.
- `steps`: per-step timings for slow-build work.

## `BuildPlayerOptions`
| Field | Set to |
|---|---|
| `scenes` | `EditorBuildSettings.scenes` filtered on `enabled`, not a hard-coded list |
| `locationPathName` | Job-supplied path with the right extension per target |
| `target` / `targetGroup` | Matching pair, equal to `-buildTarget`; a mismatch builds the wrong settings set |
| `subtarget` | Standalone player or dedicated server |
| `options` | `None` for release; `Development`, `AllowDebugging`, `ConnectWithProfiler` for debug; `CleanBuildCache` to skip cached build data |
| `extraScriptingDefines` | Per-run defines, instead of editing project defines |

Never set `AutoRunPlayer` or `ShowBuiltPlayer` headless.

## Platform switches
- `EditorUserBuildSettings.buildAppBundle`: `true` gives `.aab`, `false` `.apk`; a store upload needs the bundle.
- `exportAsGoogleAndroidProject`: Gradle project instead of an artifact, for Gradle control or external signing (`fastlane-mobile-delivery`).
- `androidCreateSymbols`: native symbol package for later crash reporting.
- iOS output is always an Xcode project, never an `.ipa`.

## Version
- `PlayerSettings.bundleVersion`: version string, all platforms.
- `PlayerSettings.Android.bundleVersionCode`: integer, must increase between uploads.
- `PlayerSettings.iOS.buildNumber`: string ordering builds within a version.

Assign all three from job arguments (typically the monotonic build number).

## Entry-point shape
```csharp
static string ReadArgument(string name, string fallback)
{
    string[] args = Environment.GetCommandLineArgs();
    for (int i = 0; i < args.Length - 1; i++)
        if (args[i] == name) return args[i + 1];
    return fallback;
}
```
1. Parse output path, target, version, build number, development flag. A missing argument takes a stated fallback or fails the run.
2. Assign version properties and platform switches.
3. Compose `BuildPlayerOptions`, call `BuildPlayer`, keep the report.
4. Log `result`, `totalErrors`, `outputPath`, `totalSize` as one greppable line.
5. `EditorApplication.Exit(0)` only on `Succeeded`, else non-zero.

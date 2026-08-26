# Batchmode Flags and Exit Codes — the command line a runner executes

Source: [Unity Editor command line arguments](https://docs.unity3d.com/Manual/EditorCommandLineArguments.html), [EditorApplication.Exit](https://docs.unity3d.com/ScriptReference/EditorApplication.Exit.html), [Log files](https://docs.unity3d.com/Manual/LogFiles.html).
Covers: SKILL.md §4 — **"Set the process exit code explicitly with `EditorApplication.Exit` instead of relying on `-quit`"**, **"Write the log to a file and to stdout, and assert on its content rather than on the absence of an error"**.

The flags a CI invocation actually uses, and the one thing a runner reads afterwards. The distinction this
file exists to make: `-quit` describes *when the editor stops*, and the exit code describes *what the build
concluded* — they are unrelated, and conflating them is how a pipeline reports green while shipping nothing.

## Flags a headless build uses

| Flag | What it changes | Source |
|---|---|---|
| `-batchmode` | Runs with no GUI and no interactive dialogs. It suppresses the dialog, it does not answer the question behind it — code that waits on a prompt blocks until the job's timeout | [Command line arguments](https://docs.unity3d.com/Manual/EditorCommandLineArguments.html) |
| `-nographics` | Does not initialise the graphics device. Correct for most build work; anything needing a real GPU fails in ways that read as unrelated | same |
| `-quit` | Quits after the commands finish, **with whatever code the editor felt like** — never combine with `-runTests`, which needs the editor alive to report | same |
| `-projectPath <path>` | The project to open. Always absolute, always the job's workspace | same |
| `-buildTarget <name>` | Switches the active target before load: `Android`, `iOS`, `StandaloneWindows64`, `StandaloneLinux64`, `StandaloneOSX`, `WebGL` | same |
| `-standaloneBuildSubtarget <Player\|Server>` | Selects the dedicated-server subtarget for a standalone build | same |
| `-executeMethod <Type.Method>` | Runs a `static` method in an Editor assembly after load. Requires the project to compile — a compile error means the method never runs | same |
| `-logFile <path\|->` | `-` streams to stdout, which the runner captures; a path also survives workspace cleanup. Without it the editor writes to its per-user default | [Log files](https://docs.unity3d.com/Manual/LogFiles.html) |
| `-accept-apiupdate` | Runs the API updater non-interactively. Without it, a project needing the updater can stall in batchmode | [Command line arguments](https://docs.unity3d.com/Manual/EditorCommandLineArguments.html) |
| `-disable-assembly-updater` | Skips assembly updating entirely — the stricter choice when the pipeline must fail rather than rewrite code | same |
| `-silent-crashes` | Suppresses the crash dialog on a crashed player launch; relevant when a job launches what it built | same |
| `-stackTraceLogType <type>` | Controls stack-trace verbosity in the log the job will parse | same |
| `-cacheServerEndpoint <host:port>` | Points the import cache at an Accelerator; see [caching-and-log-parsing.md](caching-and-log-parsing.md) | [Unity Accelerator](https://docs.unity3d.com/Manual/UnityAccelerator.html) |

## Default log locations, when `-logFile` is absent

| Platform | Path | Source |
|---|---|---|
| Linux | `~/.config/unity3d/Editor.log` | [Log files](https://docs.unity3d.com/Manual/LogFiles.html) |
| macOS | `~/Library/Logs/Unity/Editor.log` | same |
| Windows | `%LOCALAPPDATA%\Unity\Editor\Editor.log` | same |

An ephemeral agent destroys all three with the machine, which is why a CI invocation always passes `-logFile`
explicitly rather than collecting one of these afterwards.

## What the exit code is worth

| Statement | Status |
|---|---|
| `0` means the editor process ended without an internal failure | Reliable |
| Non-zero means something went wrong at the process level | Reliable |
| A specific non-zero value identifies *which* failure | **Not reliable across versions.** Values differ by editor version and by whether `-runTests` was used; `unity-test-framework` documents the codes that surface belongs to |
| `0` means the build succeeded | **False.** With `-quit`, a method that caught its own failure still exits 0 |

The contract a pipeline can actually rely on is the one the build script writes itself:

```csharp
// In the -executeMethod entry point, after BuildPipeline.BuildPlayer returned a report.
EditorApplication.Exit(report.summary.result == BuildResult.Succeeded ? 0 : 1);
```

`EditorApplication.Exit(code)` ends the process immediately with that code, which makes the exit status a
statement the build script authored rather than a side effect of `-quit`. With it in place, `-quit` is
redundant on a build invocation and is omitted.

## Log lines worth asserting on

| Line | Means | Source |
|---|---|---|
| `Build completed with a result of 'Succeeded'` | The player build finished; still confirm the `BuildReport` summary | [Command line arguments](https://docs.unity3d.com/Manual/EditorCommandLineArguments.html) |
| `Build completed with a result of 'Failed'` | The build failed even if the process exits 0 under `-quit` | same |
| `error CS****` | A compile error — `-executeMethod` never ran, so nothing downstream is meaningful | same |
| `Multiple Unity instances cannot open the same project` | Two runs collided on one workspace; a locking problem, not a build problem | same |
| `Failed to activate/update license` | The run never reached compilation; see [licensing-and-editor-provisioning.md](licensing-and-editor-provisioning.md) | [Managing your Unity licence](https://docs.unity3d.com/Manual/ManagingYourUnityLicense.html) |

Assert on the presence of a success line, never on the absence of an error line — a run killed by a timeout
produces neither, and "no error found" reads identically to "no run happened".
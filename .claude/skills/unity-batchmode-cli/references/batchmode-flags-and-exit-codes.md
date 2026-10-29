# Batchmode flags and exit codes

Source: [Command line arguments](https://docs.unity3d.com/Manual/EditorCommandLineArguments.html), [Log files](https://docs.unity3d.com/Manual/LogFiles.html).

`-quit` says when the editor stops; the exit code should say what the build concluded. They are unrelated.

| Flag | Effect |
|---|---|
| `-batchmode` | No GUI or dialogs; does not answer the question behind a dialog, so code awaiting a prompt blocks until the job timeout |
| `-nographics` | No graphics device; fine for most builds |
| `-quit` | Quits after the commands finish with whatever code; never with `-runTests` |
| `-projectPath <path>` | Absolute path to the job workspace |
| `-buildTarget <name>` | Active target before load: `Android`, `iOS`, `StandaloneWindows64`, `StandaloneLinux64`, `StandaloneOSX`, `WebGL` |
| `-standaloneBuildSubtarget <Player\|Server>` | Dedicated-server subtarget |
| `-executeMethod <Type.Method>` | Static Editor method after load; a compile error means it never runs |
| `-logFile <path\|->` | `-` streams to stdout, a path survives workspace cleanup; absent, the per-user default below is used |
| `-accept-apiupdate` | Runs the API updater non-interactively; without it the run can stall |
| `-disable-assembly-updater` | Skips updating; use when the pipeline must fail rather than rewrite code |
| `-silent-crashes` | No crash dialog when the job launches a crashed player |
| `-stackTraceLogType <type>` | Stack-trace verbosity in the parsed log |

Default log (absent `-logFile`; destroyed with an ephemeral agent, so always pass `-logFile`): Linux `~/.config/unity3d/Editor.log`, macOS `~/Library/Logs/Unity/Editor.log`, Windows `%LOCALAPPDATA%\Unity\Editor\Editor.log`.

## Exit code reliability
- `0`: editor ended without internal failure. Non-zero: process-level failure.
- A specific non-zero value does not reliably identify the failure; it varies by editor version and `-runTests` use.
- `0` does not mean the build succeeded: with `-quit`, a method that caught its own failure still exits 0.

Author the contract in the entry point, after `BuildPlayer` returned a report:
```csharp
EditorApplication.Exit(report.summary.result == BuildResult.Succeeded ? 0 : 1);
```

## Log lines
| Line | Means |
|---|---|
| `Build completed with a result of 'Succeeded'` | Build finished; still confirm the `BuildReport` |
| `Build completed with a result of 'Failed'` | Failed even if the process exited 0 |
| `error CS****` | Compile error; `-executeMethod` never ran |
| `Multiple Unity instances cannot open the same project` | Two runs collided on one workspace |
| `Failed to activate/update license` | Run stopped before compilation; see licensing reference |

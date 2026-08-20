# Platform, Build & Command Line

Source: [`UnityPlatformAttribute`](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEngine.TestTools.UnityPlatformAttribute.html), [`RequirePlatformSupportAttribute`](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEditor.TestTools.RequirePlatformSupportAttribute.html), [`RequiresPlayModeAttribute`](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEngine.TestTools.RequiresPlayModeAttribute.html), [`TestPlayerBuildModifierAttribute`](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEditor.TestTools.TestPlayerBuildModifierAttribute.html), [`ITestPlayerBuildModifier`](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEditor.TestTools.ITestPlayerBuildModifier.html), [Running Play Mode tests in a player](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/workflow-run-playmode-test-standalone.html), [Command line arguments](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/reference-command-line.html).

**Project role boundary — read this first.** Everything in this file that builds or launches a real Player (`-buildPlayerPath`, `-androidAppBundle`, "On Player" run location, `TestPlayerBuildModifier`) documents what the framework itself is capable of. Per this project's team structure, only `build-run-engineer` produces real platform builds, and only when the GD explicitly asks for one in the current conversation. `qa-automation-engineer` runs tests inside a single Unity Editor instance and never triggers a build. Use this file as reference material for a Complex-tier Tech Spec that genuinely requires on-device test verification (handed to `build-run-engineer`), not as routine QA workflow.

## `[UnityPlatform]` — restrict which platforms a test runs on

`UnityEngine.TestTools.UnityPlatformAttribute` — declares the specific platform(s) a test should (or should not) run on, independent of which assembly it lives in.

## `[RequirePlatformSupport]` — require Player build support

`UnityEditor.TestTools.RequirePlatformSupportAttribute` — requires that Player build support for the named platform(s) actually be installed for the test to run at all; without that build support installed, the test is skipped rather than failing.

## `[RequiresPlayMode]`

Covered fully in [getting-started-and-workflows.md](getting-started-and-workflows.md) and [attributes-reference.md](attributes-reference.md) — decides whether a test runs in the Editor's Play Mode or Edit Mode, independent of the assembly's own platform targeting.

## `TestPlayerBuildModifierAttribute` / `ITestPlayerBuildModifier`

**Namespace: `UnityEditor.TestTools`** — note this is a sibling of `UnityEditor.TestTools.TestRunner.Api`, **not** a member of it; a documentation/lookup mistake worth guarding against.

Lets you customize the `BuildPlayerOptions` used to build the Play Mode test Player, or split the build step from the run step across machines (e.g. a CI build agent that builds, and a separate device farm that runs).

```csharp
using UnityEditor;
using UnityEditor.TestTools;

[assembly: TestPlayerBuildModifier(typeof(BuildModifier))]

public class BuildModifier : ITestPlayerBuildModifier
{
    public BuildPlayerOptions ModifyOptions(BuildPlayerOptions playerOptions)
    {
        if (playerOptions.target == BuildTarget.iOS)
        {
            playerOptions.options |= BuildOptions.SymlinkLibraries;
        }

        playerOptions.options |= BuildOptions.AllowDebugging;
        return playerOptions;
    }
}
```

Documented use cases: enabling a platform-specific `BuildOptions` flag (e.g. `SymlinkLibraries` for iOS), preventing auto-launch (clearing `BuildOptions.AutoRunPlayer`), or redirecting the build's output path via `playerOptions.locationPathName`. Applied at assembly level; only usable from Editor code (references `UnityEditor`); affects the whole test-Player build regardless of which test filter is active. Can be combined with `[PostBuildCleanup]` (see [execution-order-and-setup-cleanup.md](execution-order-and-setup-cleanup.md)).

## Running Play Mode tests in a standalone Player

See [getting-started-and-workflows.md](getting-started-and-workflows.md)'s corresponding section for the Test Runner window's **On Player** run-location workflow, its same-network requirement, and the `Application.Quit`-doesn't-always-shut-down caveat.

## Command line arguments — full reference

Required flag: **`-runTests`** — no tests run without it.

| Argument | Description |
|---|---|
| `-forgetProjectPath` | Don't save the current Project into the Unity launcher/hub history. |
| `-runTests` | Runs tests in the Project. **Required** to run any tests at all. |
| `-testCategory` | Semicolon-separated list of test categories to include, e.g. `-testCategory "firstCategory;secondCategory"`. Supports `!` negation to exclude a category. Combined with `-testFilter`, only tests matching **both** run. |
| `-testFilter` | Semicolon-separated list of test names, or a regex against the full test name, e.g. `-testFilter "Low;Medium"`. Supports negation and parameterized-test syntax such as `"ClassName\.MethodName\(Param1,Param2\)"`. |
| `-testPlatform` | `EditMode`, `PlayMode`, or any `BuildTarget` enum value. Defaults to Edit Mode if unspecified. |
| `-requiresPlayMode` | `true`/`false` — filters by whether tests are tagged `[RequiresPlayMode]`; omit to run regardless. |
| `-assemblyType` | `EditorOnly` or `EditorAndPlatforms`. |
| `-assemblyNames` | Semicolon-separated list of test assemblies to include, e.g. `-assemblyNames "firstAssembly;secondAssembly"`. |
| `-testNames` | Semicolon-separated full test names (`FixtureName.TestName`), including parameterized forms like `MyTestClass2.MyTestWithMultipleValues(1)`. |
| `-testResults` | Output path for the NUnit-XML results file. |
| `-playerHeartbeatTimeout` | Seconds the Editor waits for heartbeats after starting a test run on a Player. Defaults to 10 minutes. |
| `-runSynchronously` | Runs Edit Mode tests synchronously within a single Editor update call; excludes multi-frame tests from the run. |
| `-buildPlayerPath` | Output directory for the built test Player (a temp folder by default). |
| `-testSettingsFile` | Path to a `TestSettings.json` for extra run configuration. |
| `-androidAppBundle` | Boolean — build an Android App Bundle (AAB) instead of an APK. |
| `-orderedTestListFile` | Path to a `.txt` file listing full test names, run in that exact order. |

**Canonical batchmode CI invocation:**
```
Unity.exe -runTests -batchmode -projectPath PATH_TO_YOUR_PROJECT -testResults C:\temp\results.xml -testPlatform PS4
```

**Note (verbatim):** "Use the `-batchmode` option when running tests on the command line to remove the need for manual user inputs." Always pair `-runTests` with `-batchmode` for any unattended/CI invocation.

The `-testResults` file is written in [NUnit's Test-Result XML Format](https://docs.nunit.org/articles/nunit/technical-notes/usage/Test-Result-XML-Format.html) — parse/consume it as standard NUnit XML, not a Unity-specific schema.

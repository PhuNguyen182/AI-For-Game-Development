---
name: unity-batchmode-cli
description: "Classic headless Editor: -batchmode -executeMethod, EditorApplication.Exit codes, BuildPipeline.BuildPlayer/BuildReport, -returnlicense, Hub CLI install, Library cache, log reading. Use when the Unity CLI cannot run the operation."
user-invocable: false
---

# Unity Batchmode CLI

Not for: the CI job calling it (`jenkins-pipeline-authoring`), the Addressables content build the entry point must run before `BuildPlayer` (`unity-addressables`), signing and packaging (`fastlane-mobile-delivery`), `-runTests` (`unity-test-framework`), diagnosing a red run (`ci-pipeline-failure-triage`), project player/quality/stripping settings (`gameplay-engineer`). `unity:unity-cli` is tried first per `core.md`; its no-`-batchmode`/`-quit` rule applies to that CLI only.
Docs: https://docs.unity3d.com/Manual/EditorCommandLineArguments.html — unversioned root serves the current release; confirm a flag against `Unity -help` or the versioned page before a job depends on it.

| Reference | Read when |
|---|---|
| [batchmode-flags-and-exit-codes.md](references/batchmode-flags-and-exit-codes.md) | Composing the command line, or judging an exit code or log line |
| [build-script-and-player-options.md](references/build-script-and-player-options.md) | Writing the `-executeMethod` entry point |
| [licensing-and-editor-provisioning.md](references/licensing-and-editor-provisioning.md) | The agent must install an editor or obtain/return a licence |
| [caching-and-log-parsing.md](references/caching-and-log-parsing.md) | Deciding what a job caches, or extracting a verdict from the log |

## Steps
1. **Pin the editor from `ProjectSettings/ProjectVersion.txt`** (`m_EditorVersion`, `m_EditorVersionWithRevision`); any other version upgrades the project on open. Read it from the checkout, not a job parameter. Install per [licensing-and-editor-provisioning.md](references/licensing-and-editor-provisioning.md).
2. **Drive every build through one `-executeMethod` entry point**, not CLI build flags: artifact path, scenes, options and version live in reviewable C#, per [build-script-and-player-options.md](references/build-script-and-player-options.md).
3. **Exit explicitly with `EditorApplication.Exit`** and omit `-quit`: `-quit` exits 0 after a method that failed. Exit non-zero on any result but `BuildResult.Succeeded`.
4. **Decide success from `BuildReport.summary`**, never from the artifact existing: a previous run's file at the same path looks identical.
5. **Take version and build number from the CI run** (`bundleVersion`, `Android.bundleVersionCode`, `iOS.buildNumber`); equal codes cannot be told apart by testers or stores.
6. **Licence is its own stage that always returns**: activate before the build, `-returnlicense` in the job's always-run `post` block.
7. **Keep `Library/` warm but never required**; a release candidate starts from a clean import, per [caching-and-log-parsing.md](references/caching-and-log-parsing.md).
8. **Log to a file and stdout (`-logFile`) and assert on a positive success line**, not on the absence of errors.
9. **Name every assumed input** (editor version, target, artifact path, version scheme) in the output; a guessed one builds the wrong thing successfully.

## Never
- Open two editors on one project path (`Library/` lock); serialisation is the CI job's lock (`jenkins-pipeline-authoring`).
- Use `-nographics` for work needing a GPU (baking, some imports); the failure reads as unrelated.
- Write a credential, keystore path or password into a build script or command line; take them from the job's credential binding.
- Edit committed project settings to make a build pass; assign only what the run needs.

## Output
```
## Batchmode Invocation — <platform and purpose>
- Editor version: <from ProjectVersion.txt, how obtained>
- Command line: <exact invocation, flags in order>
- Entry point: <path, static method, arguments read>
- Exit contract: <what exits non-zero, on which BuildResult>
- Licence handling: <activation stage, where the return happens>
- Cache policy: <what persists, what forces a clean import>
- Log: <destination, lines a run is judged on>
- Known limitations: <...>
```

## Example
- "`-quit` plus a file-exists check is enough" → declined: `-quit` exits 0 after a failed method and the file may be the previous run's; replaced with a `BuildReport.summary.result` check and `EditorApplication.Exit(1)`.

---
name: unity-batchmode-cli
description: >
  Technique for driving the Unity Editor headlessly from a CI host —
  `-batchmode -quit -nographics -projectPath -buildTarget -executeMethod
  -logFile -`, the exit codes a runner reads, `BuildPipeline.BuildPlayer`,
  `BuildPlayerOptions`, `BuildReport`, `EditorUserBuildSettings`,
  `EditorApplication.Exit`, `PlayerSettings.bundleVersion`,
  `Android.bundleVersionCode`, `iOS.buildNumber`, licence activation and
  `-returnlicense`, Unity Hub CLI editor installs from `ProjectVersion.txt`,
  and `Library/` cache reuse. Use when a build must run with no human at the
  keyboard. Not for: the CI job that calls it (`jenkins-pipeline-authoring`);
  signing and packaging (`fastlane-mobile-delivery`); the `-runTests` surface
  (`unity-test-framework`); diagnosing a red run (`ci-pipeline-failure-triage`).
---

# Unity Batchmode CLI — headless builds, exit codes, licensing

## Bundled resources

### References
Read-only context, loaded on demand so SKILL.md itself stays short.

| File | Contents | Read when |
|---|---|---|
| [root-links.md](references/root-links.md) | Manual and Scripting API roots, and why no URL here is version-pinned | Starting any task here, or a documentation page fails to resolve |
| [batchmode-flags-and-exit-codes.md](references/batchmode-flags-and-exit-codes.md) | Every flag a CI invocation uses, what each changes, and what the process exit code does and does not tell you | Composing or changing the command line a job runs |
| [build-script-and-player-options.md](references/build-script-and-player-options.md) | `BuildPlayerOptions`, `BuildReport`, target and subtarget selection, version and build-number assignment | Writing or changing the `-executeMethod` entry point |
| [licensing-and-editor-provisioning.md](references/licensing-and-editor-provisioning.md) | Activation and return on an ephemeral agent, floating vs seat licences, Hub CLI editor installs, module names | The agent must obtain an editor or a licence before it can build |
| [caching-and-log-parsing.md](references/caching-and-log-parsing.md) | `Library/` reuse, the Accelerator, workspace hygiene, and the log lines worth asserting on | Deciding what a job caches, or extracting a verdict from a batchmode log |

## 1. Objective
Produce a headless invocation that fails loudly and for the right reason. The failures this prevents are the ones that quietly waste a CI cycle: a build that reports exit code 0 while `BuildReport` says `Failed`, a `-quit` that never fires because a dialog opened behind `-batchmode`, an activation that silently consumes the project's last licence seat because nothing returned it, a job that appears to build the wrong branch because `Library/` was reused across incompatible editor versions, and a diagnosis attempted from a console that was never written to a file.

## 2. Role
Act as the headless-Unity specialist for the devops track, on behalf of `ci-cd-engineer`. You own the command line and the `-executeMethod` entry point it calls; the job that schedules it, the signing that follows it, and the tests it may run belong to neighbouring skills.

## 3. When to invoke this skill
- A build must run on a machine with no human, no GUI session, and no Editor window.
- An `Assets/Editor/**` build script is being written or changed.
- A batchmode run exits 0 but produces no artifact, or hangs until the job times out.
- The CI agent is ephemeral and must obtain an editor version and a licence before it can build.
- Version, build number, or build target must come from the CI run rather than from the committed project settings.
- Negative trigger: the `Jenkinsfile`, the agent label, credential binding, or the lock that keeps two runs off one project — that is `jenkins-pipeline-authoring`.
- Negative trigger: signing, packaging, `.aab`/`.ipa` production and keychain handling — that is `fastlane-mobile-delivery`.
- Negative trigger: `-runTests`, `-testPlatform`, `-testResults` and the NUnit XML they produce — that surface belongs to `unity-test-framework`; this skill only positions the test stage in the invocation order.
- Negative trigger: deciding what a red run means and who owns it — that is `ci-pipeline-failure-triage`.
- Negative trigger: player settings, quality settings and stripping level as project decisions — those are `unity-engineer`'s, even when a build script reads them.

## 4. How to use this skill
1. **Pin the editor version from `ProjectVersion.txt` before writing anything else** — the file names the exact editor the project opens with, and an agent that installs anything else either upgrades the project in place or fails after the slowest step. Provision that version through the Hub CLI, per [licensing-and-editor-provisioning.md](references/licensing-and-editor-provisioning.md), and resolve its documentation against the version note in [root-links.md](references/root-links.md) — flag names move between editor versions.
2. **Drive every build through one `-executeMethod` entry point rather than through CLI build flags** — `-buildTarget` selects the platform, but the artifact path, scene list, options and version belong in a static C# method where they are reviewable and testable, per [build-script-and-player-options.md](references/build-script-and-player-options.md). A command line that encodes build policy cannot be reviewed and is duplicated in every job that calls it.
3. **Set the process exit code explicitly with `EditorApplication.Exit` instead of relying on `-quit`** — `-quit` exits after the method returns, whatever the method concluded, so a failed build can exit 0 and a green pipeline can ship nothing. Exit non-zero on any outcome that is not `BuildResult.Succeeded`, per [batchmode-flags-and-exit-codes.md](references/batchmode-flags-and-exit-codes.md).
4. **Decide success from the `BuildReport` summary, never from the artifact existing on disk** — a previous run's artifact at the same path is indistinguishable from a fresh one, and `summary.result` plus `summary.totalErrors` is the only statement the editor makes about this run, per [build-script-and-player-options.md](references/build-script-and-player-options.md).
5. **Take version and build number from the CI run rather than from committed project settings** — assign `PlayerSettings.bundleVersion`, `PlayerSettings.Android.bundleVersionCode` and `PlayerSettings.iOS.buildNumber` from arguments the job passes in, per [build-script-and-player-options.md](references/build-script-and-player-options.md). Two builds carrying the same version code cannot be told apart by a tester or by a store.
6. **Treat the licence as its own stage that always releases** — activate before the build, return with `-returnlicence` in the job's `post` block whatever the outcome, and never leave the return conditional on success; a seat consumed by a crashed agent stays consumed until someone finds it by hand.
7. **Keep `Library/` warm without letting correctness depend on it** — a reused import cache is the difference between a two-minute and a twenty-minute run, but it is keyed to the editor version and the platform, per [caching-and-log-parsing.md](references/caching-and-log-parsing.md). Any run that must be trusted absolutely — a release candidate — starts from a clean import.
8. **Write the log to a file and to stdout, and assert on its content rather than on the absence of an error** — `-logFile -` streams to the console the runner captures, and a copy on disk survives the workspace being cleaned. A batchmode failure explains itself only there, and only a positive success line proves a run happened at all, per [caching-and-log-parsing.md](references/caching-and-log-parsing.md).
9. **State every input you had to assume rather than defaulting one** — a guessed build target, artifact path, or version scheme produces a run that succeeds and delivers the wrong thing. Name the assumption in the output, per `ci-cd-engineer`'s reporting envelope.

## 5. Specific goals / tasks this skill performs
- Composing a headless invocation with the correct flags, log destination, and target for the platform.
- Writing an `Assets/Editor/**` build entry point that reads its arguments and returns a real exit code.
- Assigning version, build number and output path from the CI run rather than from the project.
- Provisioning an editor version and a licence on an ephemeral agent, and returning the licence afterwards.
- Deciding what a job caches between runs and when a clean import is mandatory.
- Extracting a verdict and the surrounding evidence from a batchmode log.
- Out of scope: the CI job definition (`jenkins-pipeline-authoring`); signing and packaging (`fastlane-mobile-delivery`); test authoring and the `-runTests` surface (`unity-test-framework`); uploading the artifact (`firebase-app-distribution`); failure routing (`ci-pipeline-failure-triage`).

## 6. Output format
```
## Batchmode Invocation — <platform and purpose>
- Editor version: <from ProjectVersion.txt, and how the agent obtains it>
- Command line: <the exact invocation, flags in order>
- Entry point: <path and static method, and the arguments it reads>
- Exit contract: <what exits non-zero, and on which BuildResult>
- Licence handling: <activation stage, and where the return happens>
- Cache policy: <what persists between runs, and what forces a clean import>
- Log: <destination, and the lines a run is judged on>
- Layer: Editor-only
- Known limitations: <...>
```

**Extended report — emit ONLY when the requester asks for it.** It replaces the one-line `Known limitations` above with all three fields:
```
- Known limitations: <what this invocation does not cover>
- Latent concerns: <what holds only under current conditions — a cache key that is right today, a licence pool with one spare seat>
- Future remediation: <the concrete fix for each concern above, each with the condition that should trigger it>
```

## 7. Examples
**Example 1**
- Input: an Android nightly build must run on a Linux CI agent that is destroyed after every run.
- Output: Hub CLI installs the exact `ProjectVersion.txt` editor with the Android module; a licence stage activates before the build and returns it in `post`; the invocation is `-batchmode -nographics -projectPath <ws> -buildTarget Android -executeMethod BuildEntry.Android -logFile -` with no `-quit`, because `BuildEntry.Android` ends in `EditorApplication.Exit`; version and `bundleVersionCode` come from the job's build number; `Library/` is cached against the editor version and platform.

**Example 2**
- Input: "The build script has `-quit` and checks the file exists afterwards — that's enough to know it worked."
- Output: declined. `-quit` exits successfully after a method that failed, and the file check passes against the *previous* run's artifact still sitting at that path — together they produce a pipeline that reports green while shipping a stale build. Replaced with a `BuildReport.summary.result` check and `EditorApplication.Exit(1)` on anything but `Succeeded`, per §4 steps 3 and 4.

**Example 3**
- Input: a run hangs until the job's 60-minute timeout with the last log line reading `Refreshing native plugins`.
- Output: reported as a batchmode hang rather than a slow build. `-batchmode` suppresses dialogs but does not answer the code that raised them, and an API-updater or import prompt blocks with no console error. Diagnosis continues in `ci-pipeline-failure-triage`; the fix here is a job-level timeout plus `-accept-apiupdate` so the decision is made rather than waited on.

## 8. Edge cases & guardrails
- Never open two editors on one project path — the `Library/` lock makes the second fail or corrupt the first's import; serialisation is the CI job's, through `jenkins-pipeline-authoring`'s lock.
- Never leave a licence return conditional on the build succeeding — a crashed agent holds the seat until a human reclaims it.
- Never trust the process exit code alone as a build verdict, and never trust an artifact's existence at all.
- Never use `-nographics` for work that genuinely needs a GPU device — some baking and graphics-dependent import paths fail only under it, and the failure reads as unrelated.
- Never write a credential, keystore path or password into a build script or a command line — those come from the job's credential binding, per `jenkins-pipeline-authoring`.
- Never let a build script edit project settings permanently to make a build pass; assign what the run needs and leave the committed settings to `unity-engineer`.
- If the editor version, build target, or artifact path is missing from the request, state the assumption in the output rather than defaulting it silently — a build that succeeds for the wrong platform costs a full cycle to discover.
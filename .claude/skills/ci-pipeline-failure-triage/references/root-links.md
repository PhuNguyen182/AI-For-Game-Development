# Root Links — where the evidence lives, and where this triage stops

Sources: [Unity log files](https://docs.unity3d.com/Manual/LogFiles.html), [Jenkins Pipeline](https://www.jenkins.io/doc/book/pipeline/), [fastlane docs](https://docs.fastlane.tools/), [Firebase CLI](https://firebase.google.com/docs/cli).
Covers: SKILL.md §4 — **"Classify the failure into exactly one class before naming a cause"**.

A triage is only as good as the artifact it reads. This file names, per class, the evidence that settles it —
and the boundary where a failure stops being a pipeline failure and becomes somebody else's investigation.

## Evidence per class

| Class | Read | Where it comes from |
|---|---|---|
| Agent / workspace | The job's own console output before the stage's first command | Jenkins run log |
| Licence | The Unity log's first fifteen seconds | The `-logFile` output the stage captured |
| Editor provisioning | The Hub install step's output, and `ProjectVersion.txt` in the checked-out workspace | Job log plus repository |
| Project state | Package-manager and importer lines in the Unity log; the job's cache-restore step | Unity log, job log |
| Compile | `error CS****` lines with file and line | Unity log |
| Test | The NUnit XML the run produced, and the publisher's summary | Test results artifact |
| Test-run | Whether the XML exists at all, and the test stage's exit status | Job log, artifact list |
| Build | IL2CPP, Gradle or Xcode output, and `BuildResult` from the build script's own line | Unity log, Gradle or `xcodebuild` output |
| Signing | The Fastlane action's output and the keychain state it reported | Lane log |
| Distribution | The upload command's output and whether it returned a release link | Lane or CLI log |

**Collect the log as an artifact on every run, including green ones.** A comparison against the last passing
run is the fastest instrument in this skill, and it exists only if somebody kept it.

## Where this triage ends

| The failure is | Owner | Why not here |
|---|---|---|
| A built, signed artifact that misbehaves once installed — stripping, AOT, a missing native library | `build-fault-triage` | The pipeline did its job; the fault is in what it produced, and it needs the artifact and a device, not the run log |
| A crash reported from a released store build through telemetry | `crash-anr-investigator` | Production telemetry, a different evidence source and a different urgency |
| A test that ran and failed because it asserts the wrong thing | `qa-automation-engineer` | You establish that it ran and failed; whether the assertion is right is not a CI question |
| A pipeline that needs changing once the class is known | `ci-cd-engineer` | This skill reads and routes; it never edits |

The first row is the one that gets confused in practice. The dividing question is simple and always
answerable: **did the pipeline produce a correct artifact?** If it never produced one, the failure is here. If
it produced one that then misbehaves, it is `build-fault-triage`'s, and the run log has little to say about
it.

## Reading a Jenkins run

| Signal | Meaning |
|---|---|
| Stage view — which stage is red | Where to start, never the answer |
| `UNSTABLE` rather than `FAILURE` | A test publisher found failing tests; no step exited non-zero |
| `ABORTED` | A timeout, a manual stop, or an unanswered `input` — not a build failure |
| A stage skipped by `when` | Skipped is not passed; a report must say which |
| The same agent across failures | Points at that agent's state rather than at the change under test |

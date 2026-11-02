---
name: ci-pipeline-failure-triage
description: "Red Unity CI run triage: licence, editor version, Library damage, flakes, signing. Use when a CI run fails."
user-invocable: false
---

# CI Pipeline Failure Triage

- **Not for:** faults in an artifact that built and signed fine (`build-fault-triage`); dividing question: did the pipeline produce a correct artifact? if it never did, the failure is here.
- **Not for:** authoring or fixing the pipeline (`jenkins-pipeline-authoring`, `unity-batchmode-cli`).
- **Not for:** released-build crashes (`crash-anr-investigator`).
- **Not for:** whether a failing test asserts the right thing (`qa-automation-engineer`); this skill establishes only that it ran and failed.
- **Docs:** https://docs.unity3d.com/Manual/LogFiles.html (Unity log), https://www.jenkins.io/doc/book/pipeline/, https://docs.fastlane.tools/, https://firebase.google.com/docs/cli.

## References
- **[unity-batchmode-log-signatures.md](references/unity-batchmode-log-signatures.md):** the failure is inside a Unity stage.
- **[signing-and-distribution-failures.md](references/signing-and-distribution-failures.md):** the failure is after the build, in signing or delivery.
- **[flake-vs-real-failure.md](references/flake-vs-real-failure.md):** the failure did not reproduce, or someone wants a re-run or retry.

## Steps
1. **Establish what ran before the failing stage, before reading any error:** which stages passed, on which agent and commit, and whether this pipeline ever succeeded on that agent.
   - **Evidence:** stages before the failure are evidence; stages after it are not.
2. **Rule out infrastructure classes first:** agent, workspace, licence, editor provisioning, per [unity-batchmode-log-signatures.md](references/unity-batchmode-log-signatures.md).
   - **Why:** a run that never obtained a licence compiled no code, so nothing it says about code is evidence.
3. **Classify into exactly one class before naming a cause:** using the table under Classes; the class decides the owner.
4. **Separate a test that failed from a test run that never happened:** a crashed stage, a missing NUnit XML or a publisher tolerating empty results.
   - **Why:** they all read as pass or fail depending on configuration (`jenkins-pipeline-authoring`'s reporting rules).
5. **Separate a compile error from a build error:** `error CS****` means `-executeMethod` never ran; an IL2CPP, Gradle or Xcode error means the code compiled. Different owners.
6. **Attribute signing and distribution failures to configuration, not code:** per [signing-and-distribution-failures.md](references/signing-and-distribution-failures.md); the question is which configuration and who owns it.
7. **Establish whether it reproduces and state how many runs you looked at:** one red run is a data point, and a green re-run clears nothing, per [flake-vs-real-failure.md](references/flake-vs-real-failure.md).
   - **Intermittent:** report it as intermittent with its rate (`qa-standards`).
8. **Route by the evidenced class:** with the log excerpt (with surrounding lines), stage, agent and commit, as `qa-standards` "A finding has" requires.
9. **Return inconclusive when the log does not settle it:** name the missing artifact and which stage to re-run with what added.
   - **Bad log:** if the log is missing, truncated or from another run, say so and stop.

## Classes

| Class | Signature | Evidence lives in | Owner |
|---|---|---|---|
| Agent / workspace | Node offline, disk full, checkout or LFS failure, network timeout, `Multiple Unity instances cannot open the same project` | Jenkins console before the stage's first command | `ci-cd-engineer` for the job's assumptions; `gd` for the host |
| Licence | `Failed to activate/update license`, no seat | First 15 s of the Unity `-logFile` | `gd` (a seat is a purchase) |
| Editor provisioning | Version mismatch against `ProjectVersion.txt`, missing platform module | Hub install output, workspace `ProjectVersion.txt` | `ci-cd-engineer` |
| Project state | Package resolution failure, `Library` damage, import errors on untouched assets | Unity log, cache-restore step | `ci-cd-engineer` for the cache key; `gameplay-engineer` for the project |
| Compile | `error CS****` with file and line | Unity log | The agent owning that file |
| Test | A test ran and failed | NUnit XML, publisher summary | Owner of the code under test; `qa-automation-engineer` if the test is wrong |
| Test-run | Stage crashed, no results, empty set published | Whether the XML exists; test stage exit status | `ci-cd-engineer` |
| Build | IL2CPP, Gradle, Xcode, or `BuildResult.Failed` after a clean compile | Unity log, Gradle/`xcodebuild` output | `gameplay-engineer`; `ci-cd-engineer` where the build script is at fault |
| Signing | Keychain, certificate, profile, keystore, fingerprint mismatch | Lane log | `sdk-platform-engineer` for the identity; `ci-cd-engineer` for the wiring |
| Distribution | Upload auth, app id, artifact rejected | Lane or CLI log | `ci-cd-engineer`; `sdk-platform-engineer` for the Firebase project |

## Reading a Jenkins run
- **Red stage:** where to start, never the answer.
- **`UNSTABLE`:** a test publisher found failures with no non-zero exit.
- **`ABORTED`:** a timeout, manual stop or unanswered `input`, not a build failure.
- **Skipped by `when`:** not passed; say which.
- **Same agent across failures:** points at that agent's state.
- **Retained logs:** `Next:` keep logs as artifacts on every run, green ones too; the comparison against the last passing run is the fastest instrument here.

## Never
- **Unsupported cause:** naming a cause the log does not carry, or routing on the stage that went red.
- **Acting on the pipeline:** re-running a job to see what happens, or editing the pipeline, project or code; this skill reads. `Next:` the re-run, naming what it would establish.
- **Misfiling:** filing a signing, licence or infrastructure failure against the feature that happened to be merging.
- **Secrets in quotes:** quoting a log line containing a secret; report its identity and mask the value (`jenkins-pipeline-authoring` secret rules).

## Output
```
## CI Failure Triage — <job, run number, stage>
- Run: <job, build number, agent, commit, branch>
- Stages passed before the failure: <what is therefore known to work>
- Symptom: <what the run did>
- Evidence: <log excerpt with surrounding lines, and source>
- Class: <class from the table>
- What this rules out: <classes excluded, and why>
- Reproduction: <runs examined, how many reproduced, or first sighting>
- Decision: <class established / inconclusive — and what would settle it>
- Routed to: <agent-id | gd>
- Not covered: <stages, platforms and runs not examined>
```

## Example
- **"Failed twice, passed on the third run, add `retry(3)`":** declined as a diagnosis — a retry hides a one-in-three failure and the pipeline's record now says it passed.
  - **Done instead:** reported as intermittent (2 of 3), quoted the symptom both failed runs share, and established the class from what they have in common.

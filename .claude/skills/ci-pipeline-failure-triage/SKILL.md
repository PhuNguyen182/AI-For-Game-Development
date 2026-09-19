---
name: ci-pipeline-failure-triage
description: >
  Decision procedure for a red CI run on a Unity project — separating agent
  and workspace faults, Unity licence activation failures, editor version
  mismatches, `Library` and package-resolution damage, C# compile errors,
  genuine test failures against a test run that never happened, IL2CPP and
  Gradle or Xcode build errors, code-signing and provisioning faults, and
  distribution authentication faults — then routing each to its owner with
  the log excerpt that proves it. Not for: runtime faults in an artifact that
  built fine (`build-fault-triage`); authoring the pipeline
  (`jenkins-pipeline-authoring`); the Unity command line
  (`unity-batchmode-cli`); released-build crashes (`crash-anr-investigator`).
---

# CI Pipeline Failure Triage — what a red run actually means

## Bundled resources

### References
Read-only context, loaded on demand so SKILL.md itself stays short.

| File | Contents | Read when |
|---|---|---|
| [root-links.md](references/root-links.md) | Where each evidence source lives, and the boundary against the QA-side triage skill | Starting any triage, or deciding whether this skill owns the failure at all |
| [unity-batchmode-log-signatures.md](references/unity-batchmode-log-signatures.md) | The log lines that identify each Unity-side class, and what each rules out | The failure is inside a Unity stage |
| [signing-and-distribution-failures.md](references/signing-and-distribution-failures.md) | Keychain, certificate, profile, keystore and upload-auth signatures, and their owners | The failure is after the build, in signing or delivery |
| [flake-vs-real-failure.md](references/flake-vs-real-failure.md) | Reproduction discipline, what counts as intermittent, and why a retry is not a diagnosis | The failure did not reproduce, or somebody wants to re-run it |

## 1. Objective
Name the cause of a red run correctly on the first reading, and route it to the one agent who can fix it. The failures this prevents are all misattributions, and each costs a full cycle: a licence failure filed against the feature that happened to be merging, a stale cache reported as a code regression, a test-stage crash recorded as a test failure, a signing fault sent to a gameplay engineer, and a genuinely intermittent failure closed as fixed because the second run was green.

## 2. Role
Act as the CI diagnosis specialist for the devops track, on behalf of `ci-cd-engineer`. You read logs and decide what a failure is; you do not change the pipeline, the project, or the code, and you never re-run a job to see what happens.

## 3. When to invoke this skill
- A CI run failed and the cause is not already established by evidence.
- A run failed at a stage that has always worked, with no relevant change in the diff.
- A pipeline is red intermittently, and someone is about to add a retry.
- A failure needs an owner, and naming the wrong one would cost a cycle.
- A run reported success and something downstream proves it should not have.
- Negative trigger: an artifact that built and signed correctly but misbehaves once installed — IL2CPP stripping at runtime, a missing native library, an `ExecutionEngineException` — that is `build-fault-triage`, on the QA side.
- Negative trigger: writing or fixing the pipeline once the cause is known — that is `jenkins-pipeline-authoring` and `unity-batchmode-cli`.
- Negative trigger: crashes reported from a released build through production telemetry — that is `crash-anr-investigator`.
- Negative trigger: deciding whether a failing test is asserting the right thing — that is `qa-automation-engineer`; you establish only that the test ran and failed.

## 4. How to use this skill
1. **Establish what ran before the failing stage, before reading a single error** — which stages passed, on which agent, with which commit, and whether this pipeline succeeded on that agent before. A failure at stage four means stages one to three are evidence, and half of all misattributions come from reading the error first and the context never.
2. **Rule out the infrastructure classes first, because they invalidate everything downstream** — agent, workspace, licence and editor provisioning, per [unity-batchmode-log-signatures.md](references/unity-batchmode-log-signatures.md). A run that never obtained a licence compiled no code, so nothing it says about code is evidence, and a report that skips this check indicts the wrong change with total confidence.
3. **Classify the failure into exactly one class before naming a cause** — the class table below decides the owner, and a cause named before the class is a guess dressed as a finding.
4. **Separate a test that failed from a test run that never happened** — a crashed test stage, a missing NUnit XML, or a publisher tolerating empty results all read as "tests passed" or "tests failed" depending on the pipeline's configuration, and neither is what occurred, per `jenkins-pipeline-authoring`'s reporting rules.
5. **Separate a compile error from a build error** — `error CS****` means `-executeMethod` never ran and no build was attempted; an IL2CPP, Gradle or Xcode error means the code compiled and the packaging stage failed. They have different owners, and the log states which plainly, per [unity-batchmode-log-signatures.md](references/unity-batchmode-log-signatures.md).
6. **Attribute a signing or distribution failure to configuration rather than to code** — certificates, profiles, keystores and service accounts fail for reasons no gameplay change can cause, per [signing-and-distribution-failures.md](references/signing-and-distribution-failures.md). The only question worth asking is which configuration, and who owns it.
7. **Establish whether the failure reproduces, and state how many runs you looked at** — one red run is a data point, not a pattern, and a green re-run does not clear it, per [flake-vs-real-failure.md](references/flake-vs-real-failure.md). Report an intermittent failure as intermittent, with its rate, per `defect-reporting.md`'s reproduction rules.
8. **Route by the evidenced class and hand over the log excerpt that proves it** — with its surrounding lines, the stage, the agent and the commit, per `defect-reporting.md`'s five required elements. A routed finding without its evidence is re-diagnosed by whoever receives it.
9. **Return the class as inconclusive when the log does not settle it, and say what would** — the specific artifact missing, and which stage would have to be re-run with what added. An inconclusive triage stated as such is useful; a confident wrong class costs the cycle it was meant to save.

The classes step 3 chooses between, and the owner each one implies. Where the evidence for a class lives is listed in [root-links.md](references/root-links.md).

| Class | Signature | Owner |
|---|---|---|
| Agent / workspace | Node offline, disk full, checkout or LFS failure, network timeout | `ci-cd-engineer` for the job's assumptions; `gd` for the host itself |
| Licence | `Failed to activate/update license`, no seat available | `gd` — a seat is a purchase, not a fix |
| Editor provisioning | Version mismatch against `ProjectVersion.txt`, missing platform module | `ci-cd-engineer` |
| Project state | Package resolution failure, `Library` damage, import errors on untouched assets | `ci-cd-engineer` for the cache key; `unity-engineer` for the project |
| Compile | `error CS****` with a file and line | The agent owning that file |
| Test | A test ran and failed | The agent owning the code under test; `qa-automation-engineer` if the test itself is wrong |
| Test-run | The stage crashed, produced no results, or published an empty set | `ci-cd-engineer` |
| Build | IL2CPP, Gradle, Xcode, or `BuildResult.Failed` after a clean compile | `unity-engineer`; `ci-cd-engineer` where the build script is at fault |
| Signing | Keychain, certificate, profile, keystore, fingerprint mismatch | `tech-lead-sdk-platform` for the identity; `ci-cd-engineer` for the wiring |
| Distribution | Upload auth, app id, artifact rejected | `ci-cd-engineer`; `tech-lead-sdk-platform` for the Firebase project's own configuration |

## 5. Specific goals / tasks this skill performs
- Reconstructing what a run did before it failed, from its own log and stage history.
- Assigning a failure to exactly one class, with the evidence that distinguishes it from its neighbours.
- Telling a genuine test failure apart from a test run that never produced results.
- Telling a compile failure apart from a build failure, and both apart from a runtime fault.
- Establishing a reproduction rate rather than accepting a green re-run as a clearance.
- Routing each finding to its owner with a quoted log excerpt.
- Out of scope: fixing anything (`ci-cd-engineer` and the routed owner); runtime faults in a built artifact (`build-fault-triage`); released-build telemetry (`crash-anr-investigator`); judging a test's assertions (`qa-automation-engineer`).

## 6. Output format
```
## CI Failure Triage — <job, run number, stage>
- Run: <job, build number, agent, commit, branch>
- Stages passed before the failure: <what is therefore known to work>
- Symptom: <what the run did, as observed>
- Evidence: <the log excerpt with its surrounding lines, and where it came from>
- Class: <agent / licence / editor provisioning / project state / compile / test / test-run / build / signing / distribution>
- What this rules out: <the classes the evidence excludes, and why>
- Reproduction: <runs examined, how many reproduced, or first sighting>
- Decision: <class established / inconclusive — and what would settle it>
- Routed to: <agent-id | gd>
- Not covered: <stages, platforms and runs this triage did not examine>
```

**Extended report — emit ONLY when the requester asks for it.** It adds all three fields below the decision:
```
- Known limitations: <what this triage could not establish — one run only, no agent access, log truncated>
- Latent concerns: <conditions that will produce this again — a cache key that is right today, a certificate expiring, one macOS agent>
- Future remediation: <the concrete fix for each concern above, each with the condition that should trigger it>
```

## 7. Examples
**Example 1**
- Input: the nightly went red at "Build Android" the morning after a combat feature merged; the team assumes the merge broke it.
- Output: class **licence**, not compile. The log's last meaningful line is `Failed to activate/update license`, twelve seconds into a stage that normally takes eleven minutes — the project never compiled, so the merge is untouched by this evidence. Routed to `gd` with the excerpt, and noted that the previous night's run returned no licence because it was aborted, which is what exhausted the seat.

**Example 2**
- Input: "It failed twice and passed on the third run. Add `retry(3)` to the stage and move on."
- Output: declined as a diagnosis. A retry that hides a one-in-three failure ships the same defect with less evidence, and the pipeline's own record now says it passed. Reported as an intermittent failure with its rate (2 of 3), the shared symptom in both failed runs quoted, and the class established from what the two have in common — per §4 step 7.

**Example 3**
- Input: the test stage is green but the artifact is missing, and the job reports success.
- Output: class **test-run**, not test. The NUnit XML was never written — the stage crashed after Unity exited and the publisher was configured to tolerate empty results, so "green" means "nothing was measured". Routed to `ci-cd-engineer` to fail on empty results and to check the batchmode exit contract, with the note that every green run since that configuration landed is unproven, not passed.

## 8. Edge cases & guardrails
- Never name a cause the log does not carry, and never route on the stage that went red — a stage fails for reasons owned by several different agents.
- Never re-run a job to see whether it passes; that is an action, and this skill only reads. Ask for the re-run and say what it would establish.
- Never treat a green re-run as a clearance — an intermittent failure that disappears is still an open finding, per `verification-standards.md`.
- Never report a test failure without confirming the tests actually ran, and never report a compile error as a build failure or the reverse.
- Never file a signing, licence or infrastructure failure against the feature that happened to be merging; the timing is coincidence, and the cost of that mistake is a full cycle.
- Never quote a log excerpt containing a secret; report the line's identity and mask the value, per `jenkins-pipeline-authoring`'s secret rules.
- Never edit the pipeline, the project, or the code here — establish the class, route it, and stop.
- If the log is missing, truncated, or from a different run than the one reported, say so and stop; a triage from the wrong evidence is worse than none.

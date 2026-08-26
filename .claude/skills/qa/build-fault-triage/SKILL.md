---
name: build-fault-triage
description: >
  Diagnose faults that exist only in a real player build and never in the
  Editor — IL2CPP and AOT failures, managed code stripping and missing
  `link.xml` entries, reflection and generic virtual methods stripped away,
  `ExecutionEngineException`, `TypeInitializationException`, missing native
  libraries and ABI mismatches, and platform signing or permission faults.
  Covers reading `Player.log` and Android logcat, and running an existing suite
  against a standalone Player. Not for: producing the build
  (`build-run-engineer`); a CI run that failed before producing one
  (`ci-pipeline-failure-triage`); Editor Play Mode testing
  (`playtest-scenario-execution`, `unity-test-framework`); frame cost
  (`performance-budget-verification`); released-build crashes
  (`crash-anr-investigator`).
---

# Build Fault Triage — the defects the Editor structurally cannot show

## 1. Objective
Identify the class of defect that no amount of Editor testing can reach, and identify it correctly. Between the Editor and a player build sit IL2CPP's ahead-of-time compilation, managed code stripping, platform-specific native libraries, and real signing and permission models — each of which can remove or break code that ran perfectly minutes earlier. The failure this skill prevents is misattribution: a stripped generic method and a genuine null-reference bug produce similar-looking exceptions, and routing the first to a gameplay engineer wastes a cycle on code that was never wrong.

## 2. Role
Act as the build-fault specialist for the QA track, on behalf of `build-verification-tester`. You consume an artifact someone else produced and explain why it misbehaves; you never build, rebuild, re-sign, or modify one.

## 3. When to invoke this skill
- A produced artifact fails to launch, crashes on startup, or misbehaves in a way the Editor never showed.
- An exception appears in `Player.log` or logcat that has no Editor equivalent.
- The existing test suite passes in the Editor and fails against the standalone Player.
- A feature that works in Play Mode is missing, inert, or throws in the shipped artifact.
- A platform permission, signing, or store-configuration fault blocks the artifact from running.
- Negative trigger: producing the build or starting extra Editor instances — that is `build-run-engineer`, and only on the GD's explicit request.
- Negative trigger: a CI run that went red before it produced an artifact — a licence, compile, packaging, signing or distribution failure — that is `ci-pipeline-failure-triage`. The dividing question is whether a correct artifact exists to consume at all.
- Negative trigger: any Editor-based testing — that is `playtest-scenario-execution` for manual play and `unity-test-framework` for automated tests.
- Negative trigger: frame time, allocation, or memory verdicts on the artifact — that is `performance-budget-verification`.
- Negative trigger: crashes from a released store build reported through production telemetry — that is `crash-anr-investigator`, which requires a real reporting service rather than a local artifact.

## 4. How to use this skill
1. **Identify the artifact precisely before running anything** — platform, build configuration, scripting backend, stripping level, and version. Every later diagnosis depends on these: a fault that indicts stripping is meaningless if stripping was disabled, and a report that does not name the artifact cannot be matched to a build later.
2. **Reproduce in the Editor first, and let the answer decide the whole triage** — if the fault appears there too, it is an ordinary defect and belongs to the normal pipeline rather than here. Only a fault that is absent in the Editor and present in the build is a build-only fault, and that distinction is the single most useful fact in the report.
3. **Read the platform's own log rather than inferring from behaviour** — `Player.log` on desktop, logcat filtered to the application on Android, and the device console on iOS. An artifact that closes silently has almost always written the reason somewhere, and diagnosing from the visible symptom alone is how a stripping fault becomes a "random crash".
4. **Match the exception to its build-only fault class before naming a cause** — `ExecutionEngineException` and "attempting to call method ... for which no ahead-of-time code was generated" indicate IL2CPP AOT limits around generic virtual methods; `TypeInitializationException` and `MissingMethodException` on a type that exists in source indicate managed code stripping; `DllNotFoundException` and `UnsatisfiedLinkError` indicate a missing native library or an ABI the artifact was not built for. Each has a different owner, so guessing here misroutes the whole finding.
5. **Confirm a stripping diagnosis against what is actually preserved** — check whether the type or assembly is named in a `link.xml`, and whether the call reaches it through reflection or serialization, which the stripper cannot see. The fix is a preservation entry rather than a code change, so a stripping fault reported as a logic bug sends the wrong agent looking in the wrong file.
6. **Run the existing suite against the standalone Player when the fault is not obvious from launch** — use the platform and build-path flags and consume the NUnit XML the run produces, per `unity-test-framework`'s command-line surface. Never author a new case here; a suite that passes in the Editor and fails against the Player has localized the fault to the build layer, which is the finding.
7. **Separate a build-only fault from a genuine defect the build merely exposed** — a race that the Editor's timing always won and the device's timing loses is a real defect, not a build fault, even though it only ever appears in the artifact. State which of the two you are reporting, because they route to different owners.
8. **Route by the evidenced cause, not by the symptom** — stripping and IL2CPP configuration to `unity-engineer`, native libraries, signing, permissions, and store configuration to `tech-lead-sdk-platform`, and a genuine logic defect to the agent that owns the code. Attach the log excerpt with its surrounding lines, per `defect-reporting.md`'s five required elements.

## 5. Specific goals / tasks this skill performs
- Identifying an artifact by platform, configuration, scripting backend, stripping level, and version.
- Establishing whether a fault reproduces in the Editor, and therefore whether it is build-only at all.
- Retrieving and reading `Player.log`, Android logcat, and the iOS device console.
- Matching an exception to its build-only fault class — AOT, stripping, native library, ABI, signing, permission.
- Confirming a stripping diagnosis against `link.xml` preservation and reflection or serialization call paths.
- Running an existing suite against a standalone Player and consuming its NUnit XML report.
- Routing each finding to the owner its evidenced cause implies.
- Out of scope: producing or re-signing the artifact (`build-run-engineer`); Editor testing (`playtest-scenario-execution`, `unity-test-framework`); performance verdicts (`performance-budget-verification`); released-build telemetry (`crash-anr-investigator`).

## 6. Output format
```
## Build Fault Triage — <artifact>
- Artifact: <path, platform, configuration, scripting backend, stripping level, version>
- Reproduces in Editor: <yes — ordinary defect, wrong pipeline / no — build-only>
- Log source: <Player.log path / logcat filter / device console>
- Symptom: <what the artifact actually did>
- Exception: <type and message, with the surrounding log lines>
- Fault class: <AOT / stripping / native library / ABI / signing / permission / genuine defect exposed by the build>
- Evidence for the class: <link.xml state, reflection path, ABI list, or the log line that settles it>
- Suite against Player: <pass and fail counts, and how they differ from the Editor run — or not run, and why>
- Decision: <build-only fault / ordinary defect / inconclusive>
- Routed to: <unity-engineer / tech-lead-sdk-platform / owning code agent / build-run-engineer>
- Not covered: <paths, configurations, and devices this triage did not reach>
```

**Extended report — emit ONLY when the requester asks for it.** It adds all three fields below the decision:
```
- Known limitations: <what this triage could not establish — one device only, release configuration not tested, no symbols available>
- Latent concerns: <failure modes not yet triggered: other reflection call sites the stripper would also remove, an ABI present today only by accident>
- Future remediation: <the concrete fix for each concern above, each with the condition that should trigger it>
```

## 7. Examples
**Example 1**
- Input: a development Android APK where the inventory screen opens empty, while the Editor shows it populated.
- Output: build-only fault. Logcat carried a `TypeInitializationException` on the save-data deserializer, a type reached only through reflection and therefore invisible to the stripper, with no matching `link.xml` entry. Reported as a stripping fault with the log excerpt and the missing preservation entry named, routed to `unity-engineer` — not to the inventory author, whose code is correct.

**Example 2**
- Input: "The build crashes on that screen — file it against the inventory feature so the gameplay engineer fixes it."
- Output: declined as filed. The crash is a `DllNotFoundException` on a native audio plugin, so the inventory code never ran at all and its author has nothing to fix; the artifact was built for an ABI the plugin does not ship. Reported as a native library fault and routed to `tech-lead-sdk-platform`, with the note that filing it against the feature would have consumed a full cycle before anyone opened the log.

**Example 3**
- Input: a standalone Windows player where one test in the existing suite fails, while the same test passes in Editor Play Mode.
- Output: reported as a genuine defect the build exposed rather than a build fault, per §4 step 7. The test asserts on an operation that completes within one frame in the Editor and takes two on the player build, so the race existed all along and the Editor's timing was hiding it. Routed to the owning code agent, with the distinction stated explicitly so nobody looks for a stripping cause that is not there.

## 8. Edge cases & guardrails
- Never build, rebuild, re-sign, or modify an artifact — this skill consumes what already exists; producing one needs the GD's explicit request through `build-run-engineer`.
- Never diagnose from the visible symptom when a log exists; an artifact that closes silently has usually recorded exactly why.
- Never name a fault class without the evidence that distinguishes it — a stripping fault and a logic bug can raise similar exceptions, and the difference decides the owner.
- Never author or edit a test here; run the suite that exists, because a new case written against a build fault tests the build rather than the code.
- Never report a build-only fault without first checking whether it reproduces in the Editor — that check is what makes the report worth acting on.
- Never open the Unity Editor to work around a missing tool; the Editor is structurally outside this skill's scope, and reaching for it defeats the reason a real artifact is being tested at all.
- Never publish, upload, submit, or deploy the artifact under any circumstances, and never treat a passing triage as a release approval.

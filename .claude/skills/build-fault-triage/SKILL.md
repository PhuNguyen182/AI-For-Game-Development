---
name: build-fault-triage
description: "Player-build-only faults: IL2CPP/AOT, link.xml stripping, ABI, logcat. Use when a build fails but the Editor works."
user-invocable: false
---

# Build Fault Triage

- **Not for:** producing, rebuilding or re-signing the build (`build-release-engineer`, only on the GD's explicit request).
- **Not for:** a CI run that failed before producing an artifact (`ci-pipeline-failure-triage`); dividing question: does a correct artifact exist to consume.
- **Not for:** Editor testing (`playtest-scenario-execution`, `unity-test-framework`), frame/alloc/memory verdicts (`performance-budget-verification`).
- **Not for:** released-build crashes from telemetry (`crash-anr-investigator`).
- **Consumer only:** this skill consumes an existing artifact; it never builds, modifies, publishes, uploads, submits or deploys it, and a passing triage is not release approval.

## Steps
1. **Identify the artifact first:** path, platform, configuration, scripting backend, stripping level, version.
   - **Why:** a stripping diagnosis is meaningless if stripping was off.
2. **Reproduce in the Editor:** if it reproduces there, it is an ordinary defect for the normal pipeline. Only absent-in-Editor, present-in-build is build-only.
   - **No workaround:** do not open the Editor to work around a missing tool.
3. **Read the platform log, not the symptom:** `Player.log` (desktop), logcat filtered to the app (Android), device console (iOS). A silent close usually wrote its reason.
4. **Match the exception to a fault class before naming a cause:**
   - **IL2CPP AOT:** `ExecutionEngineException`, "attempting to call method ... for which no ahead-of-time code was generated" (generic virtual methods).
   - **Managed code stripping:** `TypeInitializationException`, `MissingMethodException` on a type that exists in source.
   - **Native library or ABI:** `DllNotFoundException`, `UnsatisfiedLinkError` (missing native library or unbuilt ABI).
5. **Confirm a stripping diagnosis:** is the type/assembly named in `link.xml`, and does the call reach it via reflection or serialization (invisible to the stripper)?
   - **Fix:** a preservation entry, not a code change.
6. **Fault not obvious from launch → run the existing suite against the standalone Player:** platform and build-path flags, consume the NUnit XML, per `unity-test-framework`.
   - **No authoring:** never author or edit a case; Editor-pass/Player-fail localizes the fault to the build layer.
7. **Separate a build-only fault from a genuine defect the build exposed:** e.g. a race the Editor's timing always won; state which you report, since owners differ.
8. **Route by evidenced cause:**
   - **Stripping and IL2CPP config:** `gameplay-engineer`.
   - **Native libraries, signing, permissions, store config:** `sdk-platform-engineer`.
   - **Logic defect:** the owning code agent.
   - **Evidence:** attach the log excerpt with surrounding lines, per `qa-standards` finding format.

## Output
```
## Build Fault Triage — <artifact>
- Artifact: <path, platform, configuration, backend, stripping level, version>
- Reproduces in Editor: <yes — ordinary defect, wrong pipeline / no — build-only>
- Log source: <Player.log path / logcat filter / device console>
- Exception: <type and message with surrounding log lines>
- Fault class: <AOT / stripping / native library / ABI / signing / permission / genuine defect exposed by the build>
- Evidence: <link.xml state, reflection path, ABI list, or the settling log line>
- Suite against Player: <pass/fail counts vs Editor, or not run and why>
- Decision: <build-only fault / ordinary defect / inconclusive>
- Routed to: <agent>
- Not covered: <paths, configurations, devices not reached>
```

## Example
- **"Crash on that screen: file it against the inventory feature":** declined as filed — a `DllNotFoundException` on a native audio plugin means the inventory code never ran.
  - **Done instead:** reported as native-library/ABI fault, routed to `sdk-platform-engineer`.

---
name: device-test-walkthrough
description: >
  Walk a supplied test-case list (risk-based-test-planning's format) against
  an already-installed build running on a real Android or iOS device —
  install and launch the artifact, drive it via the bundled device_playtest.py
  primitives (tap, swipe, text, keyevent), capture a screenshot and log
  evidence at each checkpoint, and classify every finding as Defect / Design
  flaw / As designed. Covers real-device input injection (adb on Android,
  idb on iOS) and pulling crash/ANR-relevant logs mid-walkthrough. Not for:
  Editor Play Mode scenarios (`playtest-scenario-execution`); build-only fault
  diagnosis (`build-fault-triage`); authoring or running the automated NUnit
  suite (`unity-test-framework`); deciding which test cases are owed
  (`risk-based-test-planning`); root-causing a crash once one occurs
  (`crash-anr-investigator`'s `/investigate-device-crash` convention).
---

# Device Test Walkthrough — running supplied test cases on a real device build

## 1. Objective
Close the one gap none of the Editor-based QA skills can reach: whether a
build actually behaves correctly on a real device, judged case by case
against a test plan someone already wrote, rather than by ad-hoc exploration.
A test case whose steps are prose ("tap the attack button twice") cannot be
executed by a script — only an agent looking at a screenshot can resolve that
into an actual tap. This skill fixes the two failures that make a device
walkthrough untrustworthy: skipping evidence because "it obviously worked",
and letting the walkthrough's own tooling silently decide a result is
correct when only a human-equivalent judgment can.

## 2. Role
Act as the hands-on device tester for the QA track, on behalf of
`build-verification-tester`. You install, launch, drive input, and capture
evidence on the real artifact; you never build, rebuild, re-sign, or modify
it, and you never author a test case — you execute the ones you were given.

## 3. When to invoke this skill
- `build-verification-tester` was handed a test-case list (the
  `plan-test-coverage`/`risk-based-test-planning` per-case format) alongside
  a produced build artifact and a reachable device.
- A case's `Observe via` field names `build/device` rather than Editor Play
  Mode or an automated assertion.
- A defect reported from the Editor needs confirming — or ruling out — on
  the real artifact before it is routed.
- Negative trigger: the case can be observed in Editor Play Mode — that is
  `playtest-scenario-execution`.
- Negative trigger: diagnosing *why* a build-only fault occurs (AOT,
  stripping, native library, signing) — that is `build-fault-triage`, invoked
  by the same caller alongside this skill.
- Negative trigger: authoring or running the automated NUnit suite — that is
  `unity-test-framework`.
- Negative trigger: deciding which test cases are owed in the first place —
  that is `risk-based-test-planning`, owned by `qa-lead`.
- Negative trigger: a crash or ANR already occurred and needs root-causing —
  stop the walkthrough, preserve the logs this skill already pulled, and hand
  off per `/investigate-device-crash`'s convention rather than re-diagnosing
  here.

## 4. How to use this skill
1. **Confirm the device before touching the artifact** — run
   `device_playtest.py devices`, then `doctor --platform <platform>`. No
   device, or a missing `idb`/`idb_companion`/WebDriverAgent on the iOS host,
   is `Status: Blocked`, per `verification-standards.md`'s "Blocked is a
   valid result" — never guess a device is ready.
2. **Install and launch, then confirm with a screenshot, not an exit code** —
   `install <path>` and `launch <app_id>` can both exit 0 while the app then
   crashes instantly; the script cannot tell you that. Take a screenshot
   immediately after launch and read it yourself before starting any case.
3. **Walk one supplied case at a time, in the order given** — restate its
   `Starting state`, `Actions`, and `Expected` verbatim from the input; a case
   you cannot resolve into concrete taps/swipes is reported `Ambiguous`, never
   guessed at.
4. **Capture the screenshot at the moment each case's expectation is
   evaluated, not afterwards** — the intermediate state is usually the
   finding. Use `screenshot` right when the checkpoint in `Expected` should be
   true.
5. **Drive input only through the primitives this skill wraps** — `tap`,
   `swipe`, `text`, `keyevent`. Never invent a coordinate the screenshot does
   not support; if the target isn't visible, that is itself the finding
   (`Result: Fail` or `Ambiguous`, not a guess).
6. **Pull logs whenever a case's actual result deviates from expected, and
   always after a crash** — `pull-logs` reuses the same log sources
   `/investigate-device-crash` already reads (logcat crash buffer, FATAL
   EXCEPTION / ANR greps on Android; `idevicecrashreport`/`idevicesyslog` on
   iOS). A crash mid-walkthrough stops that case's path immediately; do not
   attempt to relaunch and continue past it silently.
7. **Classify before routing, using `defect-reporting.md`'s three-way split**
   — a Defect when the build does not do what the case says it should, a
   Design flaw when it does exactly that and the case's own expectation is
   wrong, and As designed when the behaviour is correct and the case's
   expectation was mistaken. A Design flaw routes to `gd` immediately, never
   downgraded to stay in the routine cycle.
8. **Assign severity from `defect-reporting.md`'s impact-if-shipped table,
   not from the case's own stated risk** — a case's `Impact if this breaks`
   field is planning-time context, not a substitute for judging the actual
   observed impact.
9. **State a reproduction rate for anything timing-dependent** — repeat it if
   there's reason to suspect intermittency, and report attempts against
   reproductions, never as reliable on a single run.
10. **Report every case you did not reach** — a device that stopped
    responding, a case blocked by an earlier one, or time not spent on a
    lower-priority case all belong under `Not played`, per
    `verification-standards.md`'s coverage-claimed-is-coverage-owed rule.

## 5. Specific goals / tasks this skill performs
- Confirming device and tooling readiness before any device action.
- Installing, launching, stopping, and uninstalling a build artifact on a
  real Android or iOS device.
- Resolving a prose test-case step into concrete tap/swipe/text/keyevent
  input, screenshot by screenshot.
- Capturing screenshot and log evidence at the moment each case's
  expectation is evaluated.
- Classifying each finding as Defect / Design flaw / As designed and
  assigning severity.
- Reporting reproduction rate for intermittent findings and every case not
  reached.
- Out of scope: producing the artifact (`build-run-engineer`); diagnosing
  *why* a build-only fault occurs (`build-fault-triage`); Editor-based
  testing (`playtest-scenario-execution`, `unity-test-framework`); deciding
  which cases are owed (`risk-based-test-planning`); root-causing a crash
  once one occurs (`/investigate-device-crash`).

## 6. Output format
```
## Device Test Walkthrough — <artifact>
- Artifact: <path, platform, configuration>
- Device: <model/serial or UDID, OS version, how detected>
- Installed & launched: <commands run, confirmation the app was actually running>
- Test cases: <source, count run / count supplied>
- [N] <name> — Result: Pass | Fail | Blocked | Ambiguous
  - Starting state / Actions / Expected: <as supplied, verbatim>
  - Actual: <observed>
  - Evidence: <screenshot path(s) + timestamp, log excerpt>
  - Reproduction: <attempts vs. reproduced, for any finding worth repeating>
  - Classification: <Defect | Design flaw | As designed — only when Result != Pass>
  - Severity: <Critical | High | Medium | Low, per defect-reporting.md>
- Crash/ANR encountered: <yes/no — if yes, which case, pull-logs output path, and that this routes to /investigate-device-crash rather than being re-diagnosed here>
- Routed to: <agent-id per failing case, gd for any design flaw>
- Not played: <cases not reached, and why>
```

## 7. Examples
**Example 1**
- Input: build-verification-tester hands over a development Android APK, a
  connected device, and case `[3] Normal — inventory opens with the last
  equipped item selected`.
- Output: installed and launched, screenshot confirmed the main menu; walked
  the case's `Actions` (open inventory), captured a screenshot at the moment
  `Expected` should hold. The last-equipped item was not selected — a
  different item was. Reported `Result: Fail`, `Classification: Defect`,
  `Severity: Medium`, evidence attached, routed to `unity-engineer`.

**Example 2**
- Input: case `[7] Edge — rapid double-tap on the attack button does not
  double-cast the ability`.
- Output: the build double-casts on 4 of 5 attempts. Reported
  `Reproduction: 4/5`, `Result: Fail`, `Classification: Defect`, not marked
  reliable and not dropped because one attempt looked clean.

**Example 3**
- Input: mid-walkthrough, the app crashes on case `[9]`.
- Output: that case marked `Result: Blocked`, `pull-logs` run immediately and
  its output path recorded as evidence, remaining unreached cases listed
  under `Not played`, and the report states the crash routes to
  `/investigate-device-crash` rather than being diagnosed here.

## 8. Edge cases & guardrails
- Never report a finding without the screenshot or log excerpt that
  evidences it — per `defect-reporting.md`, a recollection is not evidence.
- Never guess a tap/swipe coordinate the current screenshot does not
  support; report the case `Ambiguous` instead.
- Never continue a walkthrough past a crash by relaunching silently — stop
  that case's path, pull logs, and hand off per `/investigate-device-crash`.
- Never fake iOS coverage from Android tooling, or vice versa, when the
  required binary or device is missing — report `Status: Blocked` and name
  exactly what's missing (see `references/ios-idb-setup.md` for the iOS
  prerequisites).
- Never downgrade a Design flaw into a Defect to keep it in the routine
  cycle — it routes to `gd` immediately, per `defect-reporting.md`.
- Never report an intermittent finding as reliable, and never drop it
  because a later attempt looked clean; state the rate.
- Never build, rebuild, re-sign, publish, or deploy the artifact — this
  skill only drives an artifact that already exists.
- The caller (`build-verification-tester`) owns which cases are "current"
  and any retry counts; this skill cannot hold state across invocations.

## Prerequisites
- Android: `adb` on `PATH`, USB debugging enabled, device authorized. No
  further setup.
- iOS: `idevice_id`/`idevicecrashreport`/`idevicesyslog` (`libimobiledevice`)
  plus `idb` and `idb_companion` (Facebook's iOS Debug Bridge) — **macOS
  host only**, `idb_companion` cannot run on Linux. Real-device `idb ui *`
  input additionally requires WebDriverAgent built, signed, installed, and
  running on the device, and the device paired/trusted with the host. See
  `references/ios-idb-setup.md` for the one-time setup and its recurring
  signing-expiry cost.

## Bundled resources
- `scripts/device_playtest.py` — the CLI this skill drives. Run
  `python3 scripts/device_playtest.py <command> --help` for exact flags.
- `references/cli-reference.md` — every subcommand, its per-platform command
  mapping, and exit-code conventions.
- `references/ios-idb-setup.md` — idb/idb_companion/WebDriverAgent host
  setup, pairing, and signing-expiry maintenance.

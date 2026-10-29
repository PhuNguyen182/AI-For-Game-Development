---
name: device-test-walkthrough
description: "Walk a test-case list on an installed build on a real Android/iOS device: install, launch, tap/swipe/type via bundled primitives, screenshot, logcat, per-case verdict. Use when cases must run on a physical device."
user-invocable: false
---

# Device Test Walkthrough

Not for: Editor Play Mode (`playtest-scenario-execution`), why a build-only fault happens (`build-fault-triage`), the NUnit suite (`unity-test-framework`), choosing cases (`risk-based-test-planning`), root-causing a crash (`investigate-device-crash`).

Judge a real build case by case from screenshots — supplied cases, or an Editor-reported defect to confirm on the device build; the script acts, only you judge.

| Reference | Read when |
|---|---|
| [cli-reference.md](references/cli-reference.md) | Picking a command's args, launch mode, keyevent code or pull-logs output |
| [ios-idb-setup.md](references/ios-idb-setup.md) | Target is iOS and `doctor` or an `idb ui *` call fails |

| Script | Run |
|---|---|
| [device_playtest.py](scripts/device_playtest.py) | `python .claude/skills/device-test-walkthrough/scripts/device_playtest.py <command> [args]` → device action, screenshot file or log dir |

Each command echoes its literal command to stderr — paste it as evidence. Exit 1 = missing binary or adb/idb failed; exit 0 says nothing about the app. Flags: `<cmd> --help`.

## Steps
1. **Confirm the device** — `devices`, then `doctor --platform <p>`. No device or a missing tool → `Status: Blocked`, naming what is missing.
2. **Install, launch, screenshot** — read the screenshot before any case; only it shows the app is running.
3. **Walk the supplied cases one at a time, in order** — restate `Starting state`, `Actions`, `Expected` verbatim; turn each action into `tap`/`swipe`/`text`/`keyevent` from the current screenshot. A target the screenshot does not show, or a step too vague to turn into input → `Ambiguous` (or `Fail` if it should be there); never an invented coordinate.
4. **Screenshot at the moment `Expected` should hold**, not after — the intermediate state is usually the finding.
5. **Actual ≠ expected → `pull-logs`.** Crash → stop the walkthrough and `pull-logs`; never relaunch and continue silently.
6. **Classify (Defect / Design flaw / As designed) and grade severity per `qa-standards`** — from observed impact, not the case's `Impact if this breaks`. Design flaw → `gd` at once.
7. **Timing-dependent finding → repeat it and state attempts vs reproductions** — never reliable from one run, never dropped because a later run looked clean.
8. **Every case not reached → `Not played`**, with why (device stopped, blocked by an earlier case, time).

## Never
- Report a finding without the screenshot or log excerpt that evidences it.
- Fake iOS coverage with Android tools, or the reverse — report `Blocked` naming the missing binary or device.
- Build, rebuild, re-sign, publish or deploy the artifact.
- Keep state across invocations — the caller (`build-release-engineer`) owns which cases are current and retry counts.
- Share the device — one physical device, one agent at a time.
- Put secrets or PII (tokens, player data) in screenshot or logcat evidence — redact, or cite the path only.

## Output
```
## Device Test Walkthrough — <artifact>
- Artifact: <path, platform, configuration>
- Device: <model/serial or UDID, OS version, how detected>
- Installed & launched: <commands run, screenshot showing the app running>
- Test cases: <source, run / supplied>
- [N] <name> — Result: Pass | Fail | Blocked | Ambiguous
  - Starting state / Actions / Expected: <verbatim>
  - Actual: <observed>
  - Evidence: <screenshot path(s) + timestamp, log excerpt>
  - Reproduction: <attempts vs reproduced>
  - Classification: <Defect | Design flaw | As designed — only when Result != Pass>
  - Severity: <Critical | High | Medium | Low>
- Crash/ANR: <no | case, pull-logs dir, routed to investigate-device-crash>
- Routed to: <agent per failing case; gd for a design flaw>
- Not played: <case — why>
```

## Example
- App crashes on case [9] → `Result: Blocked`, `pull-logs` dir as evidence, remaining cases under `Not played`, crash routed to `investigate-device-crash`, not diagnosed here.

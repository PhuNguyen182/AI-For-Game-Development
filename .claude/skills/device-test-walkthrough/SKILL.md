---
name: device-test-walkthrough
description: "Test cases on a real Android/iOS device: install, input, screenshot, logcat. Use when cases need a physical device."
user-invocable: false
---

# Device Test Walkthrough

- **Not for:** Editor Play Mode (`playtest-scenario-execution`), why a build-only fault happens (`build-fault-triage`), the NUnit suite (`unity-test-framework`).
- **Not for:** choosing cases (`risk-based-test-planning`), root-causing a crash (`investigate-device-crash`).
- **Judging:** judge a real build case by case from screenshots — supplied cases, or an Editor-reported defect to confirm on the device build; the script acts, only you judge.

## References
- **[cli-reference.md](references/cli-reference.md):** picking a command's args, launch mode, keyevent code or pull-logs output.
- **[ios-idb-setup.md](references/ios-idb-setup.md):** target is iOS and `doctor` or an `idb ui *` call fails.

## Scripts
- **[device_playtest.py](scripts/device_playtest.py):** run `python "${CLAUDE_SKILL_DIR}/scripts/device_playtest.py" <command> [args]` → device action, screenshot file or log dir.
- **Echo:** each command echoes its literal command to stderr; paste it as evidence.
- **Exit codes:** exit 1 = missing binary or adb/idb failed; exit 0 says nothing about the app.
- **Flags:** `<cmd> --help`.

## Steps
1. **Confirm the device:** `devices`, then `doctor --platform <p>`.
   - **Missing:** no device or a missing tool → `Status: Blocked`, naming what is missing.
2. **Install, launch, screenshot:** read the screenshot before any case; only it shows the app is running.
3. **Walk the supplied cases one at a time, in order:** restate `Starting state`, `Actions`, `Expected` verbatim; turn each action into `tap`/`swipe`/`text`/`keyevent` from the current screenshot.
   - **Unreachable target:** a target the screenshot does not show, or a step too vague to turn into input → `Ambiguous` (or `Fail` if it should be there); never an invented coordinate.
4. **Screenshot at the moment `Expected` should hold:** not after; the intermediate state is usually the finding.
5. **Actual ≠ expected → `pull-logs --package <app id>`:** app-only lines; `--full-buffer` only when the app's lines cannot explain it.
   - **Crash:** stop the walkthrough and `pull-logs`; never relaunch and continue silently.
6. **Classify (Defect / Design flaw / As designed) and grade severity per `qa-standards`:** from observed impact, not the case's `Impact if this breaks`.
   - **Design flaw:** `gd` at once.
7. **Timing-dependent finding → repeat it and state attempts vs reproductions:** never reliable from one run, never dropped because a later run looked clean.
8. **Every case not reached → `Not played`:** with why (device stopped, blocked by an earlier case, time).

## Never
- **Unevidenced finding:** reporting a finding without the screenshot or log excerpt that evidences it.
- **Faked coverage:** faking iOS coverage with Android tools, or the reverse; report `Blocked` naming the missing binary or device.
- **Touching the artifact:** building, rebuilding, re-signing, publishing or deploying it.
- **Kept state:** keeping state across invocations; the caller (`build-release-engineer`) owns which cases are current and retry counts.
- **Shared device:** one physical device, one agent at a time.
- **Raw dumps and PII:** committing a raw dump (logcat, syslog, `.ips`/`.crash`) or putting secrets or PII (tokens, player data) in a report or screenshot.
  - **Instead:** dumps stay local (gitignored; pre-commit refuses them) and the report cites the path or a redacted excerpt.

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
  - Evidence: <screenshot path(s) + timestamp, redacted log excerpt + local dump path>
  - Reproduction: <attempts vs reproduced>
  - Classification: <Defect | Design flaw | As designed — only when Result != Pass>
  - Severity: <Critical | High | Medium | Low>
- Crash/ANR: <no | case, pull-logs dir, routed to investigate-device-crash>
- Routed to: <agent per failing case; gd for a design flaw>
- Not played: <case — why>
```

## Example
- **App crashes on case [9]:** `Result: Blocked`, `pull-logs` dir as evidence, remaining cases under `Not played`, crash routed to `investigate-device-crash`, not diagnosed here.

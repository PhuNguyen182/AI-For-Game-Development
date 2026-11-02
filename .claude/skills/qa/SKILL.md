---
name: qa
description: "QA pipeline ending in qa-lead sign-off. Use after review on M/L work, or for tests or evidence on existing work."
argument-hint: "<feature slug, or what to test>"
---

# /qa

## 1. Plan — `qa-lead` (Plan)
- **Timing:** may run while `/review` is in progress; execution waits for review approval when review was chosen.
- **Review declined:** execute; each executor brief states that no correctness gate stands behind the code.
- **Brief:** `Feature: .workflow/features/<slug>.md`, acceptance criteria, this feature's open bugs, platforms, profile default QA (`routing.md`), multiplayer on/off.
- **Missing build:** device or perf coverage needs a build that does not exist → `AskUserQuestion` now.
  - **Build yes:** dispatch `build-release-engineer` with that build request (dev config, no version bump — never `/release`).
  - **Build no:** that coverage is a gap from the start.
- **Multi-client cases:** cases that need MPPM virtual players (extra Editor instances, `playtest-tester`) or a multi-instance build (`build-release-engineer`) → `AskUserQuestion` now.
  - **Answer:** record the answer in each brief.
  - **Multi-client no:** gap from the start.

## 2. Execute — serial on the Editor, serial on the device
- **Order:** the list below, only the agents the plan names.
- **Executor briefs:** every executor brief carries `Feature: .workflow/features/<slug>.md`.

1. **`qa-automation-engineer`:** extends the feature's `Tests/EditMode` and `Tests/PlayMode` suites with edge cases, never rewrites them; netcode cases when multiplayer.
2. **`playtest-tester`:** GDD scenarios in Play Mode.
3. **`performance-qa-engineer`:** budget per device tier (profile's lowest device first).
4. **`build-release-engineer`:** device cases on a real build.

- **New test code:** new test code → `code-reviewer` once before its results count, brief marked `Mode: test-code` (not a review round).
- **Test-code findings:** only findings that weaken what a test proves block; style findings are fixed without another round.
- **Bug re-runs:** a brief that re-runs a fixed bug carries `Verify: BUG-####` (one per bug) — this run is `/fix` step 6's verification.
- **Returns:** read every return's body: `Done` with defects is a finished run.

## 3. File
- **Defects:** each defect → `/fix` step 1 (record).
- **Design flaw:** a design flaw → GD now.
- **Stated gaps:** every gap a run states → feature file `Known limitations` candidate.

## 4. Sign-off — `qa-lead` (Sign-off)
- **Brief:** `Feature:` line, the plan verbatim, every report, review verdicts, the bugs whose Feature is this slug.
- **`Not signed off`:** the hook counts +1 `QA` and `rework` (never write it); fix the gaps (`/fix`), re-run only the affected cases, sign off again.
- **Cap:** a cap reached → stop rule (`routing.md`).

## 5. Report
- **Per acceptance criterion:** evidence | gap.
- **Bugs:** bugs by status.
- **Not run:** what did not run, and why.

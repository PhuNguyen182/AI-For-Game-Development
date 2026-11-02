---
name: qa
description: "QA a feature or existing work: qa-lead plans coverage, then automation, playtest, performance and device runs in order, bugs filed, qa-lead signs off. Use after review on M/L work, or when the GD asks for tests or evidence."
argument-hint: "<feature slug, or what to test>"
---

# /qa

## 1. Plan — `qa-lead` (Plan)
- May run while `/review` is in progress; execution waits for review approval when review was chosen. Review declined → execute; each executor brief states that no correctness gate stands behind the code.
- Brief: `Feature: .workflow/features/<slug>.md`, acceptance criteria, this feature's open bugs, platforms, profile default QA (`routing.md`), multiplayer on/off.
- Device or perf coverage needs a build that does not exist → ask the GD now; yes → dispatch `build-release-engineer` with that request (dev config, no version bump — never `/release`); no → that coverage is a gap from the start.
- Multi-client cases need MPPM virtual players (extra Editor instances, `playtest-tester`) or a multi-instance build (`build-release-engineer`) → ask the GD now; record the answer in each brief. No → gap from the start.

## 2. Execute — serial on the Editor, serial on the device
Order, only the agents the plan names; every executor brief carries `Feature: .workflow/features/<slug>.md`:
1. `qa-automation-engineer` — extends the feature's `Tests/EditMode` and `Tests/PlayMode` suites with edge cases, never rewrites them; netcode cases when multiplayer.
2. `playtest-tester` — GDD scenarios in Play Mode.
3. `performance-qa-engineer` — budget per device tier (profile's lowest device first).
4. `build-release-engineer` — device cases on a real build.

- New test code → `code-reviewer` once before its results count, brief marked `Mode: test-code` (not a review round). Only findings that weaken what a test proves block; style findings are fixed without another round.
- A brief that re-runs a fixed bug carries `Verify: BUG-####` (one per bug) — this run is `/fix` step 6's verification.
- Read every return's body: `Done` with defects is a finished run.

## 3. File
- Each defect → `/fix` step 1 (record). A design flaw → GD now.
- Every gap a run states → feature file `Known limitations` candidate.

## 4. Sign-off — `qa-lead` (Sign-off)
- Brief: `Feature:` line, the plan verbatim, every report, review verdicts, the bugs whose Feature is this slug.
- `Not signed off` → the hook counts +1 `QA` and `rework` (never write it); fix the gaps (`/fix`), re-run only the affected cases, sign off again. A cap reached → stop rule (`routing.md`).

## 5. Report
Per acceptance criterion: evidence | gap. Bugs by status. What did not run, and why.

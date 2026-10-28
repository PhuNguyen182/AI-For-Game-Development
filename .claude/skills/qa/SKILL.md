---
name: qa
description: "QA a feature or existing work: qa-lead plans coverage, then automation, playtest, performance and device runs in order, bugs filed, qa-lead signs off. Use after review on M/L work, or when the GD asks for tests or evidence."
argument-hint: "<feature slug, or what to test>"
---

# /qa

## 1. Plan — `qa-lead` (Plan)
- May run while `/review` is in progress; execution waits for review approval.
- Brief: acceptance criteria, open bugs, platforms, profile default QA (`routing.md`), multiplayer on/off.
- Device or perf coverage needs a build that does not exist → ask the GD now (`/release` builds); no → that coverage is a gap from the start.

## 2. Execute — serial on the Editor, serial on the device
Order, only the agents the plan names:
1. `qa-automation-engineer` — Edit/Play Mode suites; netcode cases when multiplayer.
2. `playtest-tester` — GDD scenarios in Play Mode.
3. `performance-qa-engineer` — budget per device tier (profile's lowest device first).
4. `build-release-engineer` — device cases on a real build.

- New test code → `code-reviewer` once before its results count. Only findings that weaken what a test proves block; style findings are fixed without another round.
- Read every return's body: `Done` with defects is a finished run.

## 3. File
- Each defect → `/fix` step 1 (record). A design flaw → GD now.
- Every gap a run states → feature file `Known limitations` candidate.

## 4. Sign-off — `qa-lead` (Sign-off)
- Brief: the plan verbatim, every report, review verdicts, bug list.
- `Not signed off` → fix the gaps (`/fix`), re-run only the affected cases, sign off again. Stop rule applies.

## 5. Report
Per acceptance criterion: evidence | gap. Bugs by status. What did not run, and why.

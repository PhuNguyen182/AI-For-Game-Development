---
name: fix
description: "Fix a bug end to end: record it, reproduce, root-cause, fix with the owning agent, add a regression test that fails before and passes after, verify, update the bug. Use for any defect, from QA or the GD."
argument-hint: "<bug id, or the symptom in the GD's words>"
---

# /fix

Main session is the only writer of `.workflow/bugs.md`. Finding format: skill `qa-standards`; statuses: `.claude/skills/qa-standards/references/bug-lifecycle.md`.

## 1. Record
- New bug → next `BUG-####` in `.workflow/bugs.md` (create from `references/bugs-template.md`): title, severity, feature, repro, owner, `Open`.
- Matches an existing bug → add evidence to it; a `Closed` one → `Reopened`, +1 `Fix rounds` (and the feature's `rework`).
- Every brief names the bug id; hook `round-cap.ps1` blocks it past the cap.
- On a feature with a file → also add it to that file's `Bugs` table. A closed feature stays `Closed`.

## 2. Reproduce
- Steps from a known state until it fails reliably, or the hit rate is stated. Tools: Play Mode (`playtest-tester`), a test, device (`/investigate-device-crash` for a device crash).
- Cannot reproduce → report that, with what was tried; ask the GD via `AskUserQuestion` (more info / keep open / close).

## 3. Root cause
- The owning agent finds the cause in code, not the symptom. Spec itself wrong → design flaw → GD now.
- Debugging approach: skill `superpowers:systematic-debugging` if installed.

## 4. Regression test — mandatory
- `qa-automation-engineer` writes a test that **fails on the current code**. Show the failing run.
- Untestable (no seam) → owner adds the seam in the fix; truly untestable (visual, device-only) → a written repro case in the bug, and say so.

## 5. Fix
- Owner fixes it, `Fixes: BUG-####` in its return. Compile check as in `/feature` step 4.
- Risk flag on the touched code, or Core touched → offer `/review` on the diff (`routing.md` → Gates).

## 6. Verify
- The regression test passes; the original repro no longer fails; nearby tests still pass. Ran → `Fixed`. Still failing → +1 `Fix rounds` (and the feature's `rework`), back to step 3; a cap reached → stop rule.
- Offer a QA verification run (`AskUserQuestion`): yes → a QA agent re-runs the repro and returns its `Repro:` line (hook `round-cap.ps1` counts `reproduces`) → `Closed`, or `Reopened` and the stop rule applies · no → stays `Fixed`, listed at CP4 or in the reply.

## 7. Report
Reply: cause, fix, test name, what was verified and what was not.

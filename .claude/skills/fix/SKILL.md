---
name: fix
description: "Bug fix pipeline with a mandatory regression test. Use for any defect, from QA, the GD or production telemetry."
argument-hint: "<bug id, or the symptom in the GD's words>"
---

# /fix

- **Writer:** main session is the only writer of `.workflow/bugs.md`.
- **Finding format:** skill `qa-standards`.
- **Statuses:** `.claude/skills/qa-standards/references/bug-lifecycle.md`.
- **Any size:** `/fix` runs at any size; the size of what the fix touches sets the attempt budget and the gate offer (`routing.md`).

## 1. Record
- **New bug:** next `BUG-####` in `.workflow/bugs.md` (create from `references/bugs-template.md`): title, severity, feature, repro, owner, `Open`.
- **Existing bug:** matches an existing bug → add evidence to it; a `Closed` one → `Reopened`.
- **Reopen by the GD:** a reopen the GD reports → +1 `Fix rounds` in the record (and the feature's `rework`).
- **Reopen by a run:** a reopen found by a `Verify:` run is counted by the hook — never write it.
- **Brief markers:** every brief carries `Bug: BUG-####` (one bug) and, when the bug belongs to a feature, `Feature: .workflow/features/<slug>.md`.
- **Hook charge:** hook `round-cap.ps1` charges only the `Bug:` and `Feature:` lines and blocks past a cap.
- **Feature file:** on a feature with a file → also add the bug to that file's `Bugs` table.
- **Closed feature:** a closed feature stays `Closed`.

## 2. Reproduce
- **Method:** steps from a known state until it fails reliably, or the hit rate is stated.
- **Tools:** Play Mode (`playtest-tester`), a test, device (`/investigate-device-crash` for a device crash).
- **Reproduce briefs:** briefs for this step never carry `Verify:`.
- **Production telemetry:** a `crash-anr-investigator` return with `Stages: pass` and an evidenced `Root cause:` is the repro; its `Impact:` is the hit rate.
- **Cannot reproduce:** report that, with what was tried; ask the GD via `AskUserQuestion` (more info / keep open / close).

## 3. Root cause
- **Cause:** the owning agent finds the cause in code, not the symptom.
- **Spec flaw:** spec itself wrong → design flaw → GD now.
- **Debugging approach:** skill `superpowers:systematic-debugging` if installed.

## 4. Regression test — mandatory
- **Failing test:** `qa-automation-engineer` writes a test that **fails on the current code**. Show the failing run.
- **Test brief:** the regression-test brief never carries `Verify:`.
- **No seam:** untestable (no seam) → owner adds the seam in the fix.
- **Truly untestable:** truly untestable (visual, device-only) → a written repro case in the bug, and say so.

## 5. Fix
- **Owner:** owner fixes it, `Fixes: BUG-####` in its return.
- **Compile check:** as in `/feature` step 4; commands in `feature` → build-checks.md.
- **Failing check:** a failing compile or regression test → same owner, next attempt (not a fix round).
- **Review offer:** risk flag on the touched code, or a Core assembly touched → offer `/review` on the diff (`routing.md` → Gates).
- **Rounds without a feature:** without a feature, its rounds count on the bug's `Review rounds:` (cap 3).

## 6. Verify
- **Passing state:** the regression test passes; the original repro no longer fails; nearby tests still pass. Ran → `Fixed`.
- **Verification run:** a QA executor brief with `Verify: BUG-####` re-runs the repro (a written repro: its written steps) and returns its `Repro:` line:
  - **`gone`:** → `Closed`, cited in History.
  - **`reproduces`:** → `Reopened` (the hook counts the fix round), back to step 3; a cap reached → stop rule.
  - **Inside `/qa`:** the `/qa` re-run of the affected cases is this run; no offer.
  - **Within a feature, QA declined:** no offer; CP4 lists the `Fixed` bug for the GD (accept unverified → `Accepted`, or verify).
  - **No feature:** `AskUserQuestion` — verify now (Khuyến nghị) / accept unverified (→ `Accepted`, the GD's call). A `Fixed` bug is never left without one of these.
  - **Needs a device build that does not exist (a production crash):** verified by the device run on the next release candidate (`/release` step 4), or accepted by the GD at `/release` step 1.

## 7. Report
- **Reply:** cause, fix, test name, what was verified and what was not.

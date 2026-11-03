---
name: fix
description: "Bug fix pipeline with a mandatory regression test. Use for any defect, from QA, the GD or production telemetry."
argument-hint: "<bug id, or the symptom in the GD's words>"
---

# /fix

- **Writer:** main session is the only writer of bug records, through `bugs.py` (skill `bugs`).
- **Finding format:** skill `qa-standards`.
- **Statuses:** `.claude/skills/qa-standards/references/bug-lifecycle.md`.
- **Any size:** `/fix` runs at any size; the size of what the fix touches sets the attempt budget and the gate offer (`routing.md`).

## 1. Record
- **Check first:** `bugs.py search "<words>"` before filing.
- **New bug:** `bugs.py add` prints the next `BUG-####`, status `Request`: title, description, priority, feature slug, repro, expected, actual, evidence, owner.
- **Existing bug:** matches an existing bug → add evidence with `update`; a terminal one → `Reopen`.
- **Reopen by the GD:** a reopen the GD reports → `Reopen`, then `round <id> fix +1 --note <why>` (and the feature's `rework`).
- **Still broken while `Resolved`:** the GD reports it → `Resolved` → `Review` → `Reopen`; a direct `Resolved` → `Reopen` is refused.
- **Reopen by a run:** a reopen found by a `Verify:` run is counted by the hook — never write it.
- **Brief markers:** every brief carries `Bug: BUG-####` (one bug) and, when the bug belongs to a feature, `Feature: .workflow/features/<slug>.md`.
- **Hook charge:** hook `round-cap.ps1` charges only the `Bug:` and `Feature:` lines and blocks past a cap.
- **Feature file:** on a feature with a file → also add the bug's ID, title and priority to that file's `Bugs` table; status stays in the CLI.
- **Closed feature:** a closed feature stays `Closed`.

## 2. Reproduce
- **Method:** steps from a known state until it fails reliably, or the hit rate is stated.
- **Tools:** Play Mode (`playtest-tester`), a test, device (`/investigate-device-crash` for a device crash).
- **Reproduce briefs:** briefs for this step never carry `Verify:`.
- **Production telemetry:** a `crash-anr-investigator` return with `Stages: pass` and an evidenced `Root cause:` is the repro; its `Impact:` is the hit rate.
- **Cannot reproduce:** report that, with what was tried; ask the GD via `AskUserQuestion` (more info / keep open / close as `Won't fix`, `--by GD`).

## 3. Root cause
- **Dispatch status:** dispatching the owner from `Request` or `Reopen`, here or at step 5 → `Processing`.
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
- **No fix delivered:** a `Failed` or `Blocked` attempt with no fix → `Request`; the next dispatch → `Processing`.
- **Review offer:** risk flag on the touched code, or a Core assembly touched → offer `/review` on the diff (`routing.md` → Gates).
- **Rounds without a feature:** without a feature, a workflow review round the hook cannot see → `round <id> review +1 --note <why>` (cap 3).
- **Extra round:** the GD's order → `extra-round <id> fix|review +n --note <the order>`.
- **Stop rule:** fired → `stop-rule <id> fix|review --extra-dispatch unused`; dispatch spent → `used`.

## 6. Verify
- **Passing state:** the regression test passes; the original repro no longer fails; nearby tests still pass.
- **Fix reached:** `com.unity.testtools.codecoverage` installed → run the regression test alone with coverage (`unity-test-framework` → code-coverage.md).
  - **Fix's lines not executed:** the test does not guard this fix → back to step 4, even when green; the bug stays `Processing`.
  - **Not runnable:** package absent or Editor open → say so; not a blocker.
- **Checks passed:** with the owner's `Fixes:` and `Fix reached` passed or not runnable → `Resolved`.
- **Verification run:** dispatching a QA executor brief with `Verify: BUG-####` → `Review`; it re-runs the repro (a written repro: its written steps) and returns its `Repro:` line:
  - **`gone`:** → `Complete`, cited in the status note.
  - **`reproduces`:** → `Reopen` (the hook counts the fix round), back to step 3; a cap reached → stop rule.
  - **No `Repro:` line:** → back to `Resolved`; the run settled nothing.
  - **Inside `/qa`:** the `/qa` re-run of the affected cases is this run; no offer.
  - **Within a feature, QA declined:** no offer; CP4 lists the `Resolved` bug for the GD (accept unverified → `Accepted`, or verify).
  - **No feature:** `AskUserQuestion` — verify now (Khuyến nghị) / accept unverified (→ `Accepted`, `--by GD`). A `Resolved` bug is never left without one of these.
  - **Needs a device build that does not exist (a production crash):** verified by the device run on the next release candidate (`/release` step 4), or accepted by the GD at `/release` step 1.

## 7. Report
- **Reply:** cause, fix, test name, what was verified and what was not.
- **No feature:** add "journal uncommitted": `.workflow/bugs.jsonl` waits for the GD's commit order.

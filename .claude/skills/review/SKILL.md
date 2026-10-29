---
name: review
description: "Review a diff, feature or path: code-reviewer and security-reviewer in parallel, findings merged and sent back to the author until both clear. Use for every M/L or risk-flagged submission, or an audit of existing code."
argument-hint: "<diff range, feature slug or path>"
---

# /review

## 1. Scope
- Diff range (`<base>...HEAD`, or the feature's `Log` paths), plus its spec or acceptance criteria; both gates read the diff themselves. An audit has no spec — say so in the brief; `code-reviewer` runs audit mode.
- Third-party content in the diff → `security-reviewer` clears it before anything else.

## 2. Gates — parallel, read-only
- `code-reviewer` and `security-reviewer` in one message. Neither waits for the other.
- Many modules or a whole-project audit → workflow `/review-gate` (see `.claude/workflows/review-gate.js`).

## 3. Merge
- Decide on `Verdict:`, never on `Status:`. Both `Approve` + `Clear` → done; Low findings go to the author once, with no re-review.
- `Needs-decision` from `code-reviewer` → settle it with its `Next:` (`technical-architect`, or the GD for a spec flaw) before the author's round.
- Drop duplicates; keep each finding's `path:line`, issue, fix and severity.
- `Needs Confirmation` → ask the author, then the GD (`AskUserQuestion`): only they know whether a real key exists. Unanswered → treated as a secret.

## 4. Return to the author
- Both finding sets together, in one brief. The fix is a new attempt for the same author.
- Round 2+: the brief carries the previous findings and the head commit they were made on; `code-reviewer` checks those and the lines changed since. `security-reviewer` re-runs only if the fix touched secrets, network, IAP, saves or imports.
- New findings on unchanged code in round 2+ block only at Critical/High; the rest go to `DEBT.md`.
- Each `Request changes` → +1 `review` and `rework` on the feature's `Rounds:` line. Repeated findings, or a cap reached → stop rule (`routing.md`).

## 5. Report
- Audit: findings by severity; no author, no rework loop unless the GD asks.
- Submission: verdicts, findings fixed, findings accepted by the GD (cost stated).

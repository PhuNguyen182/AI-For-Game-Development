---
name: review
description: "Review a diff, feature or path: code-reviewer and security-reviewer in parallel, findings merged and sent back to the author until both clear. Use for every M/L or risk-flagged submission, or an audit of existing code."
argument-hint: "<diff range, feature slug or path>"
---

# /review

## 1. Scope
- Diff (`git diff <base>...HEAD`, or the feature's `Log` paths), plus its spec or acceptance criteria. An audit has no spec — say so in the brief.
- Third-party content in the diff → `security-reviewer` clears it before anything else.

## 2. Gates — parallel, read-only
- `code-reviewer` and `security-reviewer` in one message. Neither waits for the other.
- Many modules or a whole-project audit → workflow `/review-gate` (see `.claude/workflows/review-gate.js`).

## 3. Merge
- Decide on `Verdict:`, never on `Status:`. Both `Approve` + `Clear` → done.
- Drop duplicates; keep each finding's `path:line`, issue, fix and severity.
- `Needs Confirmation` → ask the author, then the GD (`AskUserQuestion`): only they know whether a real key exists. Unanswered → treated as a secret.

## 4. Return to the author
- Both finding sets together, in one brief. The fix is a new attempt for the same author.
- Round 2+: the brief carries the previous findings; `code-reviewer` checks those and the changed lines only. `security-reviewer` re-runs only if the fix touched secrets, network, IAP, saves or imports.
- New findings on unchanged code in round 2+ block only at Critical/High; the rest go to `DEBT.md`.
- Repeated findings, or round 4 → stop rule (`routing.md`).

## 5. Report
- Audit: findings by severity; no author, no rework loop unless the GD asks.
- Submission: verdicts, findings fixed, findings accepted by the GD (cost stated).

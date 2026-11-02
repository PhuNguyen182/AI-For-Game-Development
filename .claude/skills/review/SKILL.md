---
name: review
description: "Review a diff, feature or path: code-reviewer and security-reviewer in parallel, findings merged and sent back to the author until both clear. Use for every M/L or risk-flagged submission, or an audit of existing code."
argument-hint: "<diff range, feature slug or path>"
---

# /review

## 1. Scope
- The reviewed state is the working tree, not `HEAD`: `git diff --merge-base <base>` (`<base>` = the feature's `Base:`; no feature → the branch the work was cut from; a feature's review first checks `git branch --show-current` equals its `Branch:`, else stop, `Needs GD`) plus untracked files (`git ls-files --others --exclude-standard`), plus its spec or acceptance criteria; both gates read the diff themselves. An audit has no spec — say so in the brief; `code-reviewer` runs audit mode.
- Every gate brief carries, each on its own line: `Round: <n>` — continuous across runs and rework, never restarting at 1: n = the target's file count (`Rounds:` / `Review rounds:`) + the hook's count for its key in `.workflow/rounds.json` (`feature:<slug>`, `bug:<id>`, `target:<path>`) + 1; the target — `Feature: .workflow/features/<slug>.md`, else `Bug: BUG-####`, else `Target: <path or base>`; an audit also `Mode: audit`. The round-cap hook reads only these lines.
- Every gate brief records the tree under review: `Tree: <sha>` = output of `git stash create`, or `git rev-parse HEAD` when the tree is clean. It is also the hook's dedupe key: the round's id is `round-<n>-<first 12 chars of Tree>`. Round 2+ adds `Previous tree: <sha>` — the `Tree:` the previous findings were made on.
- Third-party content in the diff → `security-reviewer` clears it before anything else.

## 2. Gates — parallel, read-only
- `code-reviewer` and `security-reviewer` in one message. Neither waits for the other.
- Large diff → workflow `review-gate` (`.claude/workflows/review-gate.js`); pass `args.feature` (or `args.bug` / `args.target`), `args.round`, `args.previous` (`{ findings, tree }`, the last result's `tree`). Pass `args.base` from the feature's `Base:`, and `args.spec` (the feature file, the bug's Expected, or the S acceptance criteria); `args.audit: true` only for an audit. Its gate briefs carry `Mode: workflow`, so the hook never counts them; it only blocks a launch past the cap. The main session records each round the returned verdicts fail (after the skeptic): +1 on the feature's `Rounds:` review and rework, or the bug's `Review rounds:`; a `Target:` has no file line → add the result's `roundId` to `.workflow/rounds.json` under `target:<path, lower-cased, / separators>` → `review`. A result `incomplete`, `no result` for a gate, or `nothing to review` on a non-empty change → re-run only the missing gate with `args.gates` (`['code']` or `['security']`; both when no gate ran), the same `args.round` and an unchanged tree (same `git rev-parse <tree>^{tree}` — the `stash create` sha itself changes); record the round once, from the combined verdicts, under the first result's `roundId`; incomplete twice → stop rule.
- Whole-project or path audit → workflow `project-audit` (`.claude/workflows/project-audit.js`).

## 3. Merge
- Decide on `Verdict:`, never on `Status:`. Both `Approve` + `Clear` → done; Low findings go to the author once, with no re-review.
- `Needs-decision` from `code-reviewer` → settle it with its `Next:` (`technical-architect`, or the GD for a spec flaw) before the author's round; with a Critical/High/Medium finding it counts as a failed round.
- `Needs-decision` with `Next: cto` from `security-reviewer` (secret possibly in git history) → stop the round, route to `cto` (`core.md` → Security). The review cannot close until `cto` settles it.
- Drop duplicates; keep each finding's `path:line`, issue, fix and severity.
- `Needs Confirmation` → ask the author, then the GD (`AskUserQuestion`): only they know whether a real key exists. Unanswered → a `Blocked` Leaked Secret finding: the author moves the value to a secret store or credential id, `security-reviewer` re-runs; record "Needs Confirmation unanswered — treated as secret" under the feature's `GD decisions`.

## 4. Return to the author
- Both finding sets together, in one brief. The fix is a new attempt for the same author.
- Round 2+: each gate brief carries `Round: <n>`, the current `Tree:`, the previous findings and `Previous tree: <sha>`; `code-reviewer` checks those and `git diff <previous sha>` plus untracked files. `security-reviewer` re-runs when its previous verdict was not `Clear`, or the fix touched secrets, network, IAP, saves or imports.
- New findings on unchanged code in round 2+ block only at Critical/High; the rest go to `DEBT.md`.
- A round in which either gate fails (`Request changes`, security `Blocked`) → +1 `review` (and the feature's `rework`), counted by the hook from the brief's marker lines — the main session writes only failed workflow rounds. Repeated findings, or a cap reached → stop rule (`routing.md`).

## 5. Report
- Audit: findings by severity; no author, no rework loop unless the GD asks.
- Submission: verdicts, findings fixed, findings accepted by the GD (cost stated).

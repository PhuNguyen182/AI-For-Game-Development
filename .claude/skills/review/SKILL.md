---
name: review
description: "Review gate by code-reviewer and security-reviewer. Use for M/L or risk-flagged work, or audits of existing code."
argument-hint: "<diff range, feature slug or path>"
---

# /review

## 1. Scope
- **Reviewed state:** the working tree, not `HEAD`: `git diff --merge-base <base>` plus untracked files (`git ls-files --others --exclude-standard`), plus its spec or acceptance criteria.
  - **`<base>`:** the feature's `Base:`; no feature → the branch the work was cut from.
  - **Branch check:** a feature's review first checks `git branch --show-current` equals its `Branch:`, else stop, `Needs GD`.
  - **Diff reading:** both gates read the diff themselves.
- **Audit scope:** an audit has no spec — say so in the brief; `code-reviewer` runs audit mode.
- **Marker lines:** every gate brief carries these, each on its own line:
  - **Round line:** `Round: <n>` — continuous across runs and rework, never restarting at 1.
  - **Round number:** n = the target's count (`Rounds:` / `bugs.py counters <id>`) + the hook's count for its key in `.workflow/rounds.json` (`feature:<slug>`, `bug:<id>`, `target:<path>`) + 1.
  - **Target line:** `Feature: .workflow/features/<slug>.md`, else `Bug: BUG-####`, else `Target: <path or base>`.
  - **Audit line:** an audit also `Mode: audit`.
  - **Hook reading:** the round-cap hook reads only these marker lines.
- **Tree line:** every gate brief records the tree under review: `Tree: <sha>` = output of `git stash create`, or `git rev-parse HEAD` when the tree is clean.
  - **Dedupe key:** `Tree:` is also the hook's dedupe key: the round's id is `round-<n>-<first 12 chars of Tree>`.
  - **Previous tree line:** round 2+ adds `Previous tree: <sha>` — the `Tree:` the previous findings were made on.
- **Third-party content:** third-party content in the diff → `security-reviewer` clears it before anything else.

## 2. Gates — parallel, read-only
- **Dispatch:** `code-reviewer` and `security-reviewer` in one message. Neither waits for the other.
- **Large diff:** large diff → workflow `review-gate` (`.claude/workflows/review-gate.js`).
  - **Round args:** pass `args.feature` (or `args.bug` / `args.target`), `args.round`, `args.previous` (`{ findings, tree }`, the last result's `tree`).
  - **Scope args:** pass `args.base` from the feature's `Base:`, and `args.spec` (the feature file, the bug's Expected, or the S acceptance criteria).
  - **Audit arg:** `args.audit: true` only for an audit.
  - **Hook counting:** its gate briefs carry `Mode: workflow`, so the hook never counts them; it only blocks a launch past the cap.
  - **Recording a failed round:** the main session records each round the verdicts fail (after the skeptic): +1 on the feature's `Rounds:` review and rework, or `bugs.py round <id> review +1`.
  - **Target record:** a `Target:` has no file line → add the result's `roundId` to `.workflow/rounds.json` under `target:<path, lower-cased, / separators>` → `review`.
  - **Missing result:** a result `incomplete`, `no result` for a gate, or `nothing to review` on a non-empty change → re-run only the missing gate.
    - **Re-run args:** `args.gates` (`['code']` or `['security']`; both when no gate ran), the same `args.round` and an unchanged tree.
    - **Unchanged tree:** same `git rev-parse <tree>^{tree}` — the `stash create` sha itself changes.
    - **Re-run record:** record the round once, from the combined verdicts, under the first result's `roundId`.
    - **Incomplete twice:** incomplete twice → stop rule.
- **Whole-project or path audit:** workflow `project-audit` (`.claude/workflows/project-audit.js`).

## 3. Merge
- **Deciding field:** decide on `Verdict:`, never on `Status:`.
- **Pass:** both `Approve` + `Clear` → done; Low findings go to the author once, with no re-review.
- **`Needs-decision` from `code-reviewer`:** settle it with its `Next:` (`technical-architect`, or the GD for a spec flaw) before the author's round.
  - **Failed round:** with a Critical/High/Medium finding it counts as a failed round.
- **`Needs-decision` with `Next: cto` from `security-reviewer`:** (secret possibly in git history) → stop the round, route to `cto` (`core.md` → Security).
  - **Closure:** the review cannot close until `cto` settles it.
- **Duplicates:** drop duplicates; keep each finding's `path:line`, issue, fix and severity.
- **`Needs Confirmation`:** re-dispatch the author with the question, then the GD (`AskUserQuestion`): only they know whether a real key exists.
  - **Unanswered:** a `Blocked` Leaked Secret finding: the author moves the value to a secret store or credential id, `security-reviewer` re-runs.
  - **Unanswered record:** record "Needs Confirmation unanswered — treated as secret" under the feature's `GD decisions`.

## 4. Return to the author
- **Findings:** both finding sets together, in one brief.
- **New attempt:** the fix is a new attempt for the same author.
- **Round 2+ briefs:** each gate brief carries `Round: <n>`, the current `Tree:`, the previous findings and `Previous tree: <sha>`.
- **Round 2+ `code-reviewer`:** checks the previous findings and `git diff <previous sha>` plus untracked files.
- **Round 2+ `security-reviewer`:** re-runs when its previous verdict was not `Clear`, or the fix touched secrets, network, IAP, saves or imports.
- **New findings:** new findings on unchanged code in round 2+ block only at Critical/High; the rest go to `DEBT.md`.
- **Failed round count:** a round in which either gate fails (`Request changes`, security `Blocked`) → +1 `review` (and the feature's `rework`), counted by the hook from the brief's marker lines.
- **Main session writes:** the main session writes only failed workflow rounds.
- **Stopping:** repeated findings, or a cap reached → stop rule (`routing.md`).

## 5. Report
- **Audit:** findings by severity; no author, no rework loop unless the GD asks.
- **Submission:** verdicts, findings fixed, findings accepted by the GD (cost stated).

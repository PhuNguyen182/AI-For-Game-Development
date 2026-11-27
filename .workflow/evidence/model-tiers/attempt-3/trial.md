# model-tiers QA evidence refresh — attempt 3 (HEAD 847844f), 2026-11-25/26

Main session. Counts, pass/fail, model ids and case names only.

## Commit stability (QA plan run 2)
- `git diff 2c898cd..HEAD --stat -- .claude/agents .claude/rules .claude/workflows`: empty.
- `git diff 0d170dc..HEAD --stat -- .claude/agents/technical-architect.md`: empty.
- `git diff afc5907..HEAD --stat -- .claude/workflows/review-gate.js`: empty.
- `code-reviewer.md` and `security-reviewer.md`: `model: opus`.

## AC1 (verify.ps1 at HEAD)
- exit 0, `verify-layer: OK (21 warning(s))`. Diff against the pre-feature baseline (OK, 20): new `log-triage.md: 64 lines > 50 recommended (soft)`; `always-loaded rules 130 lines` became `132 lines` (same warning, +2 lines from C2). No FAIL. Untracked `.claude/DEBT.csv` present; result unchanged.

## AC7
- `routing.md` lines 60-62: the `model:` default bullet, then the C2 Fable bullet, then the C2 log-triage bullet, worded as C2.
- `git diff -U0 develop..HEAD -- .claude/agents/`: files `ci-cd-engineer.md` (C4 Run log line) and new `log-triage.md`; the only `model:` line is `+model: haiku` in `log-triage.md`.

## AC11 / AC12 (hook suite at 847844f, main-session run)
- pwsh: 1704 PASS / 0 FAIL / 0 SKIP. Windows PowerShell 5.1: 1699 / 0 / 0. `hooks: all tests passed` on both.
- log-triage-scan PASS lines, same on both shells (27): H1 x2, H2, H3 x2, H4 x3, H5 x2, H6 x2, H7 x2, H7b x2, H7c x2, H8, H9, H9b, H10 x2, H10b, H11, H12, unexpected-error case.

## AC6 token method
- Totals in attempt-1/2 tables: input, output, cache-creation and cache-read tokens summed over assistant transcript lines, deduplicated by `message.id`.

## AC10 live dispatch at HEAD
- `log-triage` on the synthetic fixture, brief with no `Feature:`/`Bug:`/`Target:` line: claude-haiku-5-5, not blocked by round-cap, `Done`; first blocking line 3001 `Bar.cs:12`; counts one per pattern (2 / 1 / 0 / 0 / 0); 5 planted lines quoted masked; log path masked; hook blocks observed 0.

## Live probe of log-triage-scan (LIM-005)
- `log-triage` asked to return an AWS-key-shaped fake unmasked: the fake reached the main session in the SubagentHandback report; the transcript holds no hook block after the handback tool call. A SubagentStop hook runs after the handback is delivered, so it cannot withhold it. Result: C5 does not protect the SubagentHandback path. Main GD: Change 1 (PreToolUse on SubagentHandback).

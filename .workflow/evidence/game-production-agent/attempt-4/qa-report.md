# QA report: game-production-agent, sign-off round 2 evidence run (attempt 4)

Feature: `.workflow/features/game-production-agent.md`
Scope: evidence run only. No product or test code edited, no commit. Raw logs stay local (scratchpad), not committed.
Review status of the code under test: not stated in the brief; this run is a re-run of existing suites, so no correctness gate stands behind it beyond the suites' own assertions.

## 1. Revision

| Item | Value |
|---|---|
| `git rev-parse HEAD` | `a327b4b84f4903cc9efc376463b9c0ec7ed2449b` (branch `feature/game-production-agent`) |
| `git status --porcelain` (before and after all runs, identical) | ` M .workflow/bugs.jsonl` · `?? .memory/notes/feedback/main-gd-term.md` · `?? .workflow/evidence/game-production-agent/` · `?? .workflow/features/game-production-agent.md` · `?? docs/` |
| `git diff --stat 5997a35 a327b4b` | `.claude/hooks/tests/run.ps1 | 1 +` — 1 file changed, 1 insertion. Matches the expectation (only `run.ps1`). |

The runs left the tracked tree unchanged (status identical after).

## 2. Versions

| Tool | Version |
|---|---|
| Python (`python -I`) | 3.14.7 |
| Windows PowerShell (hooks suite host) | 5.1.26100.9711 |
| PowerShell 7 (`pwsh`, used for `verify.ps1`) | 7.6.9 |

## 3. Results (run one after the other, never in parallel; each twice)

### Hooks suite: `powershell -NoProfile -ExecutionPolicy Bypass -File .claude/hooks/tests/run.ps1` (Windows PowerShell 5.1)

| Run | Exit | PASS | FAIL | OBS | Duration | Last line |
|---|---|---|---|---|---|---|
| 1 | 0 | 1461 | 0 | 15 | 841 s | `hooks: all tests passed` |
| 2 | 0 | 1461 | 0 | 15 | 823 s | `hooks: all tests passed` |

- Both logs are 1478 lines. The only line differences between run 1 and run 2 are 8 `gate form` PASS lines that print the per-run temp folder name (`hooktest-d3997acc` vs `hooktest-87087310`); every result is identical.
- The 15 OBS lines are observations (not asserted pass/fail) and are identical in both runs:
  - pre-commit label variants: `(open bracket)Measured: r.csv]` -> 2, `(open bracket)MEASURED: r.csv]` -> 2, `(open bracket)measured : r.csv]` -> 0, `(open bracket) measured: r.csv]` -> 0, `(measured: r.csv)` -> 0, `measured: r.csv` -> 0
  - pre-commit marker variants: `<!--advisory:begin-->` -> 0, `<!-- ADVISORY:BEGIN -->` -> 2, `<!--  advisory:begin  -->` -> 0, `<!-- advisory:begin --> trailing text` -> 0
  - pre-commit: CRLF-marked block plus bare figure -> 0; staged deletion of a committed store file -> 2; exempt file renamed to a scanned path -> 0
  - round-cap: extra round under a level-3 heading -> 0; under a lower-case heading -> 2
- The two exempt-file PASS lines for `.claude/hooks/tests/run.ps1` (the file changed by `a327b4b`) are present in both runs: `pre-commit: ... and for a marker line: x/.claude/hooks/tests/run.ps1` and `pre-commit: the exact exempt file may define the label and the marker: .claude/hooks/tests/run.ps1`.
- Count method: lines starting `PASS`, `FAIL`, `OBS` after trimming; FAIL count is 0 in both logs.

### Python suites: `python -I <file>` (exit codes all 0)

| Suite | Run 1 | Run 2 |
|---|---|---|
| `.claude/skills/mem/scripts/test_adv.py` | exit 0, Ran 42, OK | exit 0, Ran 42, OK |
| `.claude/skills/mem/scripts/test_mem.py` | exit 0, Ran 63, OK | exit 0, Ran 63, OK |
| `.claude/skills/monetization-modeling/scripts/test_simulate.py` | exit 0, Ran 31, OK | exit 0, Ran 31, OK |
| `.claude/skills/advisory-protocol/scripts/test_check_pack.py` | exit 0, Ran 48, last line `data pack: OK` | exit 0, Ran 48, last line `data pack: OK` |
| `.claude/skills/bugs/scripts/test_bugs.py` | exit 0, Ran 275, OK (114 s) | exit 0, Ran 275, OK (152 s) |

Python total per run: 459 tests, 0 failures, 0 errors, same counts in both runs.

### Layer check: `.claude/skills/verify-layer/scripts/verify.ps1` (run under `pwsh` 7.6.9)

| Run | Exit | Result |
|---|---|---|
| 1 | 0 | `verify-layer: OK (21 warning(s))` |
| 2 | 0 | `verify-layer: OK (21 warning(s))` |

Output of the two runs is identical: no FAIL lines; 21 soft WARN lines (agent files over 50 lines x 18, `CLAUDE.md` 40 lines > 30, always-loaded rules 130 lines > 100, plus 3 aggregate size WARNs: list items > 200 chars (8 files), body > 8000 chars (5 files), description + when_to_use > 120 chars (4 files)). The warnings are soft limits the script itself treats as OK.

## 4. Checklist

- Review status stated: pass — stated above; unreviewed by this run.
- Fails first: n/a — no regression test added.
- Tests executed: pass — every run executed more than zero tests; counts above.
- Seed and clock injected: n/a — no Core test run.
- Runners agree: n/a — no `dotnet test` mirror adopted.
- Suite extended, not weakened: pass — no test file touched; `git status` unchanged by the run.
- Network cases: n/a — multiplayer off.
- Code coverage read: n/a — Unity Code Coverage package not applicable (no Unity code in this layer).

## 5. Not covered

| Gap | Owner |
|---|---|
| `verify.ps1` was run under `pwsh` 7.6.9 only; the brief did not name a host. The hooks suite itself exercises `verify.ps1` under Windows PowerShell 5.1 (the `verify ...` PASS lines in both hooks runs), but a direct 5.1 run of the whole-layer check was not made. | `qa-automation-engineer` |
| The 15 OBS lines record behaviour (e.g. lower-case `ADVISORY:BEGIN` marker blocked, spaced `<!--advisory:begin-->` and `(open bracket)measured : r.csv]` variants not blocked, lower-case "extra round" heading rejected) but assert nothing; whether those outcomes are intended is not decided by this run. | `technical-architect` |
| Python suites were run on Python 3.14.7 only; no other interpreter version. | `qa-automation-engineer` |
| Hooks suite ran on one machine (Windows 11); no CI or other OS run. | `ci-cd-engineer` |
| Each suite was run twice; spread across two runs showed identical results, durations varied (test_bugs 114 s vs 152 s; hooks 841 s vs 823 s). No timing budget was given, so durations are not judged. | none (informational) |
| Behaviour outside the suites (the game-production-agent flow in a live session, agent prompts' real-world behaviour) is not exercised by any of these suites. | `qa-lead` |

<!-- Label syntax is written as "(open bracket)measured:" here: pre-commit blocks the literal label outside the framework's own files. -->

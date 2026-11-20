# C3 suite re-run (QA round 1 of 2, gaps G1/G3)

Feature: workflow-state-stores. Repo: AI-For-Game-Development (framework, `.claude/` layer; no Unity).
Date: 2026-11-20. Runner: qa-lead test engineer. Suites ran strictly one at a time.

## Preconditions
| Check | Result |
|---|---|
| `git rev-parse --short HEAD` | `29a5cbd` (matches the brief) |
| `git status --short .claude` | empty (clean) |
| `python3 --version` | Python 3.14.7 |
| `pwsh --version` | PowerShell 7.7.0 |
| `powershell.exe` `$PSVersionTable.PSVersion` | 5.1.26100.9818 |

## 1. Python suites (`python3 -I`)
| Command | Result |
|---|---|
| `python3 -I .claude/skills/records/scripts/test_records.py` | `Ran 88 tests in 31.557s` / `OK` / exit 0 |
| `python3 -I .claude/skills/bugs/scripts/test_bugs.py` | `Ran 281 tests in 79.063s` / `OK` / exit 0 |

## 2. verify-layer
`pwsh -NoProfile -File .claude/skills/verify-layer/scripts/verify.ps1` -> exit 0, final line: `verify-layer: OK (21 warning(s))` (soft size warnings only, no FAIL).

## 3. Hook suite, pwsh 7.7.0
Command: `pwsh -NoProfile -File .claude/hooks/tests/run.ps1`. Raw output (local, not in repo): `C:\Users\Admin\AppData\Local\Temp\claude\8db747868b6de3cf\9cb5f018-855b-469c-bbce-45f36723e29e\scratchpad\hooks-pwsh7.txt` (1567 lines).
Exit code 0. Final line: `hooks: all tests passed`.

| PASS | FAIL | OBS | SKIP |
|---|---|---|---|
| 1550 | 0 | 15 | 0 |

## 4. Hook suite, Windows PowerShell 5.1.26100.9818
Command: `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .claude/hooks/tests/run.ps1`. Raw output (local): `...\scratchpad\hooks-ps51.txt` (1562 lines).
Exit code 0. Final line: `hooks: all tests passed`.

| PASS | FAIL | OBS | SKIP |
|---|---|---|---|
| 1545 | 0 | 15 | 0 |

## Quoted SKIP and FAIL lines
- FAIL lines: none in either run (both: `^\s*FAIL` count 0).
- SKIP lines: none in either run (both: `^\s*SKIP` count 0). A case-insensitive search for "skip" matches only PASS test names (`pre-push allows: git push -o ci.skip origin main`, `session-start skips closed features`, `session-start: a feature branch skips the purge`, `session-start: a dirty journal skips the purge, and the line says so`, `session-start: git failing at a real checkout names the skipped purge`); none is a SKIP result.
- None of the five SKIP sites in run.ps1 fired in either run: lines 1637 (code page 437 set succeeded), 1765 (round-cap Python/git simulation), 2209 (Git Bash found), 2345 (csc.exe found), 2608 (`$pwsh` resolved: on 5.1 it comes from `Get-Command pwsh`, and pwsh 7 is installed, so the line fires only on a machine without pwsh 7).

## OBS lines (15, identical text and values in both runs)
Observation probes, not assertions; the hook's current verdict is printed (0 = passes, 2 = blocked):
`label variant` x6 (the title-case and upper-case measured-label forms -> 2 each, four others -> 0), `marker variant` x4 (only `<!-- ADVISORY:BEGIN -->` -> 2), CRLF-marked block + bare figure -> 0, staged deletion of a committed store file -> 2, exempt-file rename -> 0, `round-cap` extra round under a level-3 heading -> 0, under a lower-case heading -> 2. Values are the same on pwsh 7 and 5.1.

## Why PASS differs by 5 (1550 vs 1545), with no SKIP on either side
Compared the sorted PASS-line sets of both runs. Differences:
1. Per-run temp folder names in gate-form lines (`hooktest-b28fd67b` vs `hooktest-64a7ffb9`): 8 lines per side, same checks, text differs only by the random folder name. Net 0.
2. `bugs stdin`: pwsh 7 prints `the default pipe of pwsh 7 is already byte-exact`; 5.1 prints `why the rule exists: the 5.1 default pipe writes ? and exits 0`. One PASS each. Net 0.
3. The real difference: 5 `gate form, allow, PowerShell` lines exist only on pwsh 7. Counts of `PASS  gate form, allow, PowerShell`: pwsh 7 = 75, 5.1 = 70. The missing 5 are the follow-up checks (`... and the commit lands`, `... with nothing left staged`, `... and the push reaches the remote`) for the commands containing `&&`:
   - `cd <path> && git commit -m x` (2 lines: commit lands, nothing left staged)
   - `later statements with no second commit (&&)` (2 lines: commit lands, nothing left staged)
   - `cd <path> && git push` (1 line: push reaches the remote)
   Cause: `GfRunnable` (run.ps1 lines 2231-2234) returns false for a PowerShell command containing `&&` when `$PSVersionTable.PSVersion.Major -lt 7`; the comment at 2230 says Windows PowerShell has no `&&`, so the command is a parse error and runs nothing, and only the gate verdict is checked (the plain `gate form, allow, PowerShell: <label>` line still passes on both). This is a deliberate branch, not a SKIP: no SKIP line is printed, and the 5 checks are not run on 5.1, not counted as passed.
   Total: 5 = 1550 - 1545. Bash allow lines are 76 on both.

Note: the 5.1 run's session-start line shifts from output line 1399 to 1394, consistent with those 5 absent lines.

## Secret / session-token check of the raw output
Searched both raw files for private-key headers, `AKIA...`, `ghp_...`, `sk-...`, JWT-like `eyJ...` and `Library\` / `UserSettings` content. The only hit is the PASS test name `pre-commit blocks Editor session data: UserSettings/EditorUserSettings.asset` (a test label, no content). Word matches for secret/token/password are hook test names (`secret-scan blocks a key shape`, ...). No secret or session token found; no Temp/Library/Logs/UserSettings content copied. The raw files hold only temp-folder paths under `AppData\Local\Temp\hooktest-*`; they stay in the scratchpad and are not committed.

## Repo state after the runs
`git rev-parse --short HEAD` = `29a5cbd`; `git status --short .claude` empty. Only this report was written to the repo.

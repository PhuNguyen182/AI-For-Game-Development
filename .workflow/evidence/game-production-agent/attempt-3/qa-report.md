# QA verification report - game-production-agent, attempt 3

Scope: `Verify: BUG-0009..BUG-0012` against HEAD, then every suite twice. No product or test code edited, nothing committed.

## Environment
- HEAD: `5997a357466a5ce19fc0bf8257c9be97fdb46a2e` (branch `feature/game-production-agent`)
- `git status --porcelain` before and after the runs (identical):
  ```
   M .workflow/bugs.jsonl
  ?? .memory/notes/feedback/main-gd-term.md
  ?? .workflow/evidence/game-production-agent/
  ?? .workflow/features/game-production-agent.md
  ?? docs/
  ```
- Python 3.14.7 (`python -I`), PowerShell 7.6.9 (pwsh), Windows PowerShell 5.1.26100.9711, git 2.56.0.windows.2, Windows 11 10.0.26300.
- Review status of the code under test: reviewed (test-code review round 2 Approve, per the brief). No correctness gate was re-run here.
- Raw logs (local, not committed): `C:\Users\Admin\AppData\Local\Temp\claude\c--Users-Admin-Projects-AI-For-Game-AI-For-Game-Development\6a67d61d-3392-4299-96b5-9196129da6d6\scratchpad\logs\run{1,2}-*.txt`, `summary.txt`.
- Repro helpers: `...\scratchpad\repro_0009_0010.py`, `repro_0012.ps1`, `diag.ps1` (same scratchpad).

## Repro results
Repro: BUG-0009 gone
Repro: BUG-0010 gone
Repro: BUG-0011 gone
Repro: BUG-0012 gone

| Bug | Command | Observed |
|---|---|---|
| BUG-0009 | temp git repo; transcript line holds assistant text `Before\r\n<!-- advisory:begin -->\r\nARPDAU 0.083\r\n<!-- advisory:end -->\r\nAfter`; `python -I mem.py --root <tmp> capture --transcript t.jsonl --session abcd1234-0`; read the trace | capture exit 0, 1 trace file. Trace text is `Before\r\n[advisory: adv q]\nAfter`. Figure `ARPDAU 0.083` in trace: False. `After` kept. LF control: figure False too. |
| BUG-0010 | temp git repo with `.memory/advisory/` ignored; `python -I adv.py --root <tmp> ingest` with stdin `[1,2]`, `null`, `7`, `{"agent":"x","return":7}` | all four exit 2, no traceback. stderr: `refused: ingest needs a JSON object, got list` / `NoneType` / `int`; `refused: ingest field return must be a string`. stdout empty. `.memory/advisory` not created, nothing stored. |
| BUG-0011 | Grep of `.claude/**/*.md` for bare `gd` (not part of a longer word or hyphenated name); Grep for `Routed to: gd` / `Next: gd`; `verify.ps1` | `Routed to: gd` and `Next: gd`: 0 hits. Bare `gd`: one hit, `git-recovery/references/reflog-and-unreachable-objects.md:10`, which is git's `%gd` format token, not a route (the fix exempts it). `verify.ps1` on the real layer: exit 0, `verify-layer: OK (21 warning(s))`. A planted skill with `Routed to: <agent \| gd>` makes verify fail: `FAIL ... retired route 'gd' (use main-gd)`, exit 1 (diag.ps1). |
| BUG-0012 | temp project (`CLAUDE_PROJECT_DIR`), feature file `review 4/5` with both headings; `round-cap.ps1 -Mode dispatch` under Windows PowerShell | A: extra round only under the second heading (`## Main GD decisions`), exit 0. B: extra round only under the second heading (`## GD decisions`), exit 0. Control C: both headings, no extra round: exit 2, "past the round cap ... default 3 applies". |

## Suite results (HEAD, run 1 then run 2, strictly sequential)
| Suite | Runner | Run 1 | Run 2 |
|---|---|---|---|
| `.claude/hooks/tests/run.ps1` | Windows PowerShell 5.1, `-File` | exit 1, 1459 PASS, 2 FAIL, 15 OBS (815 s) | exit 1, 1459 PASS, 2 FAIL, 15 OBS (879 s) |
| `test_adv.py` | `python -I` | exit 0, 42 tests OK | exit 0, 42 tests OK |
| `test_mem.py` | `python -I` | exit 0, 63 tests OK | exit 0, 63 tests OK |
| `test_simulate.py` | `python -I` | exit 0, 31 tests OK | exit 0, 31 tests OK |
| `test_check_pack.py` | `python -I` | exit 0, 48 tests OK | exit 0, 48 tests OK |
| `test_bugs.py` | `python -I` | exit 0, 275 tests OK (143 s) | exit 0, 275 tests OK (147 s) |
| `verify.ps1` | pwsh, whole layer | exit 0, `verify-layer: OK (21 warning(s))` | exit 0, same |

Python suites: no skips, no expected failures left in the counts (all `OK`). Run 1 and run 2 hook output is identical apart from the temp folder names in the `gate form` lines.

### The two run.ps1 failures (deterministic, both runs)
```
FAIL  soft: exit 0 on a whole-layer run, no FAIL, no per-file form (got False, expected True)
FAIL  verify: the whole-layer failure count is the plants and nothing else (got False, expected True)
```
- Location: `.claude/hooks/tests/run.ps1:2519` and `:2628`.
- Cause (read in `run.ps1`, reproduced in `diag.ps1`): commit 5997a35 added `VSkill 'route-gd'` (run.ps1:2446), a skill that is meant to fail verify with the retired route `gd`. It is planted in the shared `VerifyLayer` sandbox and never removed, unlike `backtick-run` (removed at :2575). Every later whole-layer `Verify` call therefore sees one extra `FAIL ... retired route 'gd'`. Line 2519 expects exit 0 and no `FAIL`; line 2628 expects `plants + longRefs + 5` failures and gets one more.
- It is a test-fixture ordering defect, not a product defect: the product check works (BUG-0011 row above). The per-file checks at :2447-2450 pass.
- The fix commit's own claim "1446/0" no longer holds at HEAD: 1459 PASS / 2 FAIL.
- Owner: `qa-automation-engineer` (test code in `run.ps1`); the plant needs removing after its per-file checks, or the two whole-layer expectations need the extra plant counted. I changed nothing.

## Checklist
- Review status stated: pass - reviewed per brief; no correctness gate re-run here.
- Fails first: n/a - no regression test added in this run.
- Tests executed: pass - every run executed more than zero tests (counts above).
- Seed and clock injected: n/a - no Core test.
- Runners agree: n/a - no `dotnet test` mirror.
- Suite extended, not weakened: n/a - no test file touched in this run.
- Network cases: n/a - multiplayer off.
- Code coverage read: n/a - not a Unity project run; package not applicable.

## Not covered
- Hook suite outcome under pwsh 7: only Windows PowerShell 5.1 was run, as the brief states. Owner: `qa-automation-engineer`.
- `verify.ps1` was run under pwsh only, not Windows PowerShell 5.1 (it runs under 5.1 inside run.ps1's sandbox, which is where the two failures arise). Owner: `qa-automation-engineer`.
- The BUG-0009 repro covers a CRLF block through `mem.py capture`; the unterminated-begin CRLF form is covered only by `test_an_unterminated_begin_with_windows_line_endings_still_strips` in `test_mem.py` (passes), not by hand. Owner: main session.
- The BUG-0012 hand repro used the `Agent` dispatch path only; the `Workflow` launch path is covered by existing `run.ps1` checks (pass) and was not repeated by hand. Owner: main session.
- Bug records still say "Review"; this report does not change a bug status.

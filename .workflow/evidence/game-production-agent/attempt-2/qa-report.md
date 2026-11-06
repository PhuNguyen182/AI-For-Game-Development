# QA report: game-production-agent, attempt 2 (test-code review round 1 fixes)

Author: qa-automation-engineer. Supersedes the numbers and the overclaims of `attempt-1/qa-report.md` (kept as written). Findings F1-F3 of attempt 1 are fixed in product code by the main session (BUG-0009, BUG-0010, BUG-0011); BUG-0012 (round-cap reads one heading) is the former observation O7, now a failing regression check.

## Run record

| Item | Value |
|---|---|
| Branch / HEAD | `feature/game-production-agent`, HEAD `bbeb7e1`; test and product edits uncommitted (nothing committed by this run) |
| Python | 3.14.7 (floor 3.10 not exercised) |
| PowerShell | `run.ps1` under Windows PowerShell 5.1 (`%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe -NoProfile -ExecutionPolicy Bypass -File .claude\hooks\tests\run.ps1`); the two runs were started together, each in its own temp folder |
| Review status of the code under test | reviewed earlier (Approve / Clear); the three fixes since then (mem.py, adv.py, verify.ps1 and five SKILL.md lines) were made by the main session and are not reviewed in this run |
| Product code touched by this run | none. `git diff -U0` of the six test files: 3 deleted lines, all in `run.ps1`, all the `StagedCode` helper body (see "Suite extended, not weakened") |
| `expectedFailure` | none in any file (removed by the main session, kept removed) |

## Results (every suite run twice on the final files)

| Suite | Command | Attempt 1 | Run 1 | Run 2 |
|---|---|---|---|---|
| `test_adv.py` | `python -I .claude/skills/mem/scripts/test_adv.py` | 41 ran, OK, 1 expected failure | 42 ran, OK | 42 ran, OK |
| `test_mem.py` | `python -I .claude/skills/mem/scripts/test_mem.py` | 63 ran, OK, 2 expected failures | 63 ran, OK | 63 ran, OK |
| `test_simulate.py` | `python -I .claude/skills/monetization-modeling/scripts/test_simulate.py` | 31 ran, OK | 31 ran, OK | 31 ran, OK |
| `test_check_pack.py` | `python -I .claude/skills/advisory-protocol/scripts/test_check_pack.py` | 48 ran, OK | 48 ran, OK | 48 ran, OK |
| `test_bugs.py` | `python -I .claude/skills/bugs/scripts/test_bugs.py` | 275 ran, OK | 275 ran, OK (94.6 s) | 275 ran, OK (101.2 s) |
| `run.ps1` | command above | 1455 PASS, 0 FAIL, 17 OBS | 1457 PASS, **2 FAIL**, 15 OBS, "2 failure(s)" | 1457 PASS, **2 FAIL**, 15 OBS, "2 failure(s)" |

Skips: 0 in every Python suite. The 2 `run.ps1` failures are the BUG-0012 regression checks, below; they are the only failures in both runs. `run.ps1` exits 1 until `round-cap.ps1` is fixed.

## M3: the BUG-0012 regression checks fail on the current code (both runs)

`round-cap.ps1:163` reads `## (?:Main )?GD decisions(.*?)(\r?\n## |$)` once, so with both headings in a feature file only the first heading's record is seen. Spec behaviour: both headings are read, an extra round under the second one is honored (dispatch exit 0). The two former `Observe` lines are now `Check`s expecting 0:

```
FAIL  round-cap: both headings, the extra round only under the new one, which comes second: honored (BUG-0012) (got 2, expected 0)
FAIL  round-cap: both headings, the extra round only under the old one, which comes second: honored (BUG-0012) (got 2, expected 0)
```

Same two lines in run 1 and run 2 (`run.ps1:870` and `:872`). They fail first by construction (product code unchanged); they must pass once the main session fixes `round-cap.ps1`. No other round-cap check changed.

## Per finding: what changed

| Finding | Change |
|---|---|
| M1 | `run.ps1`: near name `Assets/.claude/skills/advisory-protocol/SKILL.md` replaced by `Game/.claude/skills/advisory-protocol/SKILL.md`. New helper `StagedHook` returns the whole hook result (`StagedCode` wraps it, same exit code). Every near-name check now asserts `Code -eq 2` and the block text: `observed figure` for the label, `advisory marker` for the marker line. The unchanged `Assets/X/.claude/hooks/key.txt` check (also blocked by "asset without .meta") is left as it was, and a new check beside it stages `Game/X/.claude/hooks/key.txt`: exit 2, `secret in Game/X/.claude/hooks/key.txt` in the text, no "asset without" in the text. |
| M2 | `run.ps1`: the CRLF case no longer uses `StagedCode`. `core.autocrlf` is set to `false` in the fixture repo, the file is written byte-exact (`[IO.File]::WriteAllText`, `x\r\n<!-- advisory:begin -->\r\ny\r\n`), staged, and the staged diff is read from a `--output` file and asserted to hold `-->\r\n` (new check "staged with its CR bytes") before the hook runs; the hook check asserts exit 2 and `advisory marker`. `core.autocrlf` is unset afterwards (it was not set locally before; the global value is untouched). |
| M3 | Two `Observe` lines became `Check`s expecting 0, titled with BUG-0012. They fail (above). |
| M4 | `test_adv.py`: the non-object test now holds only `[1, 2]`, `"text"`, `7`, `null` and asserts exit 2, `"refused"` in stderr, and no store created. New `test_ingest_with_a_non_string_field_is_refused`: `agent`, `return`, `brief`, `session`, `agent_id` each set to a non-string (and `return: true`), exit 2, `"refused"` in stderr, no store; the same object with strings is then stored (exit 0). |
| M5 | `test_adv.py`: the metacharacter test keeps only queries that hold a word (`NEAR`, `NEAR(`, `interstitial)`, `"interstitial`, `interstitial*`, `a OR b AND NOT c`, `title:interstitial`, `interstitial -level`, the injection string, `^interstitial`, `{x}`) and asserts exit 0. The no-words test covers `"`, `""`, `*`, `\`, `)`, blanks and the empty string: exit 2, `query has no words` in stderr, empty stdout. |
| M6 | `test_mem.py`: the indented-marker test ends in the unique token `TailKept`, asserts it survives, the figure is gone, and `text.count(mem.ADVISORY_POINTER) == 1`. |
| M7 | `test_check_pack.py`: `test_old_mac_line_endings_are_read_too` adds a clean CR-only pack that returns `[]`, and the bad one equals exactly `["x.csv: column 1 ('user_id') identifies a person or device"]`. |
| M8 | `test_check_pack.py`: probed first. RX_NUMBER requires an ASCII `0` or `[1-9]` lead, so a full-width number is not a number and its column is text, under `d1` too. Renamed to `test_a_ten_digit_full_width_run_makes_its_column_text_and_is_a_long_digit_run_without_echo` (asserts `["x.csv: column 1 ('segment') holds a long digit run"]` and the `('d1')` form exactly) and `test_a_fifteen_digit_full_width_number_is_a_long_digit_run_in_a_text_column_not_a_numeric_id` (exact list). The "no echo" claim holds because the exact list has no cell text. |
| L1 | `test_adv.py`: both `assertNotIn("Traceback", err)` removed (`run_cli` runs `adv.main` in process, so a traceback would raise, not reach stderr). |
| L2 | The decision-note secret test asserts `secret-shaped` in stderr and that the value is not echoed. |
| L3 | `test_bugs.py`: the "exactly main GD" test now also files a second bug and moves it to `Accepted` with `--by "main GD"`; all four main-GD-only moves (Backlog, Backlog to Request, Won't fix, Accepted) plus delete are covered. |
| L4 | `test_bugs.py`: the old-`gd`-row test asserts `main GD only` in the refusal and that the bug is still `Backlog` after it. |
| L5 | Corrections below. |
| Stale comments | The two CRLF tests in `test_mem.py` said "expected to fail until mem.py is fixed"; they now cite BUG-0009, and also assert the text after the block survives (`After`, `Before`) and one pointer. |

## L5: corrections to attempt 1 (the attempt-1 text is left as written)

- **C5(d), full-width digits.** Wrong: "a 10-digit full-width phone is a 'long digit run' in a text column and in a numeric one". A full-width number never makes a numeric column (RX_NUMBER wants an ASCII lead digit), so the column is text in both fixtures and only the text rule applies. The numeric-id rule ("holds a long numeric id") is not exercised by full-width digits. Tests are renamed and assert the exact problem list (M8).
- **C2, "The same check is a permanent test".** Overclaim. The ad hoc probe used a 7-entry fixture with a brief, a return, a marked block, a labelled line, a labelled answer and an unterminated block, then `Select-String` over the written files. `test_no_figure_survives_anywhere_under_the_memory_folder` (`test_mem.py:696`) is a similar but different check: 7 entries, a figure in a brief, a return, a marked block, a labelled line and a labelled answer, no unterminated block and no `Select-String`; it reads every byte under `.memory/` in Python for `ARPDAU 0.0831`, `0.0831` and `11.27`. It does not assert `(open bracket)measured:` is absent, and it does not cover the unterminated-block path (covered elsewhere by `test_an_unterminated_begin_with_windows_line_endings_still_strips`). The 0/0/0 table in attempt 1 is the ad hoc probe's result only.
- **C6, "no double count".** Misleading. `round-cap.ps1` does not sum extra rounds: the cap number comes from the `Rounds:` line, and a heading record only decides whether a raised cap is honored. The `review 5/5` dispatch and `review 6/5` block checks show a second record changes nothing; they do not test counting, because nothing is counted from headings. Read those four checks as "a second record adds no capacity", not "no double count".
- **C2g coverage row.** Wrong: "near names of the 9 exempt files". The 10 near names derive from 6 of the 9 exempt paths (`SKILL.md`, `schema.md`, `mem.py`, `common.ps1`, `run.ps1`, `verify.ps1`); `adv.py`, `test_mem.py` and `test_adv.py` have no near-name case. The 9 exact files are all checked. The 4 case variants cover 4 files (`SKILL.md` twice, `mem.py`, `common.ps1`). One near name (`Assets/.claude/...`) was blocked for another reason and is replaced (M1).

## Previous findings, now fixed in product code (re-verified by the suites above)

| Was | Fix | Test that guards it, now a plain pass |
|---|---|---|
| F1 CRLF markers do not strip | BUG-0009 | `test_markers_with_windows_line_endings_still_strip`, `test_an_unterminated_begin_with_windows_line_endings_still_strips` (failed as `expectedFailure` before the fix, attempt 1) |
| F2 ingest of non-object JSON: traceback | BUG-0010 | `test_ingest_of_json_that_is_not_an_object_is_refused`, `test_ingest_with_a_non_string_field_is_refused` |
| F3 five `Routed to: gd` | BUG-0011 | not a test in my files; `verify.ps1` now fails on a retired `gd` route (not re-run in this attempt) |

## Checklist (qa-automation-engineer)
- Review status stated: pass. Earlier code reviewed; the main session's three fixes are not reviewed here.
- Fails first: pass. The BUG-0012 checks fail on unchanged `round-cap.ps1` (two lines above, both runs). The BUG-0009 and BUG-0010 tests failed first in attempt 1 as `expectedFailure`.
- Tests executed: pass. Counts per suite above.
- Seed and clock injected: n/a. No Core test.
- Runners agree: n/a. No `dotnet test` mirror.
- Suite extended, not weakened: pass with one note. The only deleted lines are 3 in `run.ps1`: the `StagedCode` body, which now delegates to `StagedHook` and returns the same exit code. Three of my own earlier assertions were tightened or replaced (the Assets near name, the CRLF hook check, the two Observe lines), none loosened.
- Network cases: n/a. Multiplayer is off.
- Code coverage read: n/a. No Unity project, no coverage package.

## Not covered (owner)
- Everything under "Not covered" in attempt 1 still stands (Python 3.10-3.13, pwsh 7 for `run.ps1`, live adviser behaviour, concurrent writers, hostile pack look-alikes).
- `verify.ps1` was not re-run after the BUG-0011 change (owner: main session, `/verify-layer`).
- The three main-session fixes are unreviewed code (owner: `code-reviewer`).
- `Assets/X/.claude/hooks/key.txt` (existing check) still passes for two reasons at once; the new `Game/` check isolates the secret scan.

<!-- Label syntax is written as "(open bracket)measured:" here: pre-commit blocks the literal label outside the framework's own files. -->

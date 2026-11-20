# workflow-state-stores: QA static checks C4, C5

Commit `29a5cbd`, branch `feature/workflow-state-stores`, base `develop` (c1eb56e). Read-only checks, nothing executed beyond `git grep`, `git diff`, Grep.
C6 (Python 3.10 probe) is out of scope per the main session's course correction and is not part of this report.
File name kept as briefed (c4-c6); it holds C4 and C5 only.

## C4: stale-reference grep (criterion 8): PASS

Scope: `.claude/`, `README.md`, `docs/`, `CLAUDE.md`. Patterns: `framework-backlog\.md`, `rounds\.json`, `\.workflow/DEBT\.md`, `\.workflow/backlog\.md`, `DEBT\.md`, `NOTES\.md`, `- Rounds:`, `templates/framework-backlog`.
Commands: Grep per scope (head_limit 0) and `git grep -n -E <same pattern> -- .claude README.md docs CLAUDE.md` (cross-check: 104 tracked hits in 11 files, same set as Grep). `README.md` and `CLAUDE.md`: 0 hits.
Result: 0 live references. Every hit is migration code, the md fallback (D1), a fixture, or a historical note.

| path:line | pattern | class |
|---|---|---|
| `.claude/hooks/round-cap.ps1:20`, `:176`, `:196`, `:412`, `:413` | `- Rounds:` | md fallback (D1: un-migrated feature file counters; 412-413 is the message for a file with no `- Rounds:` line and no registry record) |
| `.claude/hooks/session-start.ps1:123` | `framework-backlog.md`, `backlog.md`, `DEBT.md`, `rounds.json` | migration code (lists md stores still to be converted) |
| `.claude/hooks/tests/run.ps1:709,710,1784,1798` | `templates/framework-backlog`, `framework-backlog.md` | fixture (retired template placed by the test; asserts it is not copied) |
| `.claude/hooks/tests/run.ps1:810,829,873,963,976,1790,1806,1810` | `- Rounds:` | fixture (un-migrated feature md for the md fallback) |
| `.claude/hooks/tests/run.ps1:1163,1233,1335-1343` | `rounds.json` | fixture (un-migrated `rounds.json` read, never written) |
| `.claude/hooks/tests/run.ps1:1508` | `framework-backlog.md`, `backlog.md`, `DEBT.md`, `rounds.json` | fixture (list of retired md stores the test checks are absent) |
| `.claude/skills/bugs/scripts/test_bugs.py:626` | `rounds.json` | fixture/test (`assertNotIn("rounds.json", bugs.py source)`, a negative assertion) |
| `.claude/skills/verify-layer/scripts/verify.ps1:65` | `- Rounds:` | md fallback (layer guard that `schema.md` still documents the line `round-cap.ps1` reads) |
| `.claude/skills/review/SKILL.md:18` | `- Rounds:` | md fallback ("a legacy file: its `- Rounds:` line") |
| `.claude/skills/records/SKILL.md:50`, `:104` | `rounds.json`, `framework-backlog.md`, `backlog.md`, `DEBT.md`, `NOTES.md` | migration doc (import table; `Migrate from markdown` sources) |
| `.claude/skills/records/references/schema.md:120,121,122,128,129,133` | md store names, `rounds.json` | migration doc (source-to-store mapping, rename rule) |
| `.claude/skills/records/references/schema.md:131` | `- Rounds:` | md fallback ("Until migrated" round-cap reading) |
| `.claude/skills/records/references/schema.md:145,147,148,158` | `rounds.json` | migration doc (ledger reads and imports an un-migrated `rounds.json`) |
| `.claude/skills/records/scripts/records.py:1137,1145,1226,1231,1285,1349,1358,1366` | `rounds.json` | migration code (ledger import / `ledger migrate`) |
| `.claude/skills/records/scripts/records.py:2188,2232,2280,2480-2533,2589,2773,2912` | `framework-backlog.md`, `backlog.md`, `DEBT.md`, `NOTES.md`, `rounds.json` | migration code (`migrate --from-md` readers, parser docstring, CLI help) |
| `.claude/skills/records/scripts/records.py:2724` | `- Rounds:` | md fallback (`legacy_counters`, mirrors the hook's md read) |
| `.claude/skills/records/scripts/test_records.py:570,574,575,582,583,1266,1351,1355` | `rounds.json` | fixture |
| `.claude/skills/records/scripts/test_records.py:870,871,1083-1086,1109-1116,1183-1193,1234,1245,1248,1250,1260-1275` | md store names | fixture (md inputs for the migrate tests) |
| `.claude/skills/records/scripts/test_records.py:958,1049,1494` | `- Rounds:` | fixture |
| `docs/superpowers/specs/2026-11-05-product-advisory-team-design.md:86,91,151` | `DEBT.md`, `.workflow/backlog.md`, `.workflow/DEBT.md` | historical note (approved design spec dated 2026-11-05) |

Supporting checks:
- `.claude/templates/framework-backlog.md`: directory `.claude/templates` does not exist; `git ls-files .claude/templates` is empty. The retired template is gone.
- Ignore rules (outside the searched scope, noted for completeness): `.gitignore:117-121` (`rounds.*` patterns), `.gitignore:164-168` (`framework-backlog.md/.jsonl/.migrated-*.md`).

Observation (not a finding, no severity): the 2026-11-05 design spec carries no "superseded by workflow-state-stores" marker, so a reader of lines 91 and 151 could take `.workflow/backlog.md` and `.workflow/DEBT.md` as current. It is a dated approved spec, so it stays a historical note under the plan's rules.

## C5: removed test lines since develop (criterion 1): PASS

Command: `git diff develop...HEAD -U0 -- .claude/skills/bugs/scripts/test_bugs.py` (stat: 156 insertions, 11 deletions). The 11 removed `-` lines:

| # | removed line (test_bugs.py, develop side) | class |
|---|---|---|
| 1 | `def test_uncommitted_reports_name_the_no_feature_debt_file(self):` | rename only (re-added as `..._no_feature_debt_journal`, same body shape) |
| 2 | `self.assertIn("`.workflow/DEBT.md`", line)` | doc-contract assertion on an old md path; replaced by `` `.workflow/debt.jsonl` `` on the same `line` |
| 3 | `def test_known_debt_is_read_from_the_no_feature_file_too(self):` | rename only (re-added as `..._no_feature_store_too`) |
| 4 | `self.assertIn("`.workflow/DEBT.md`", line)` | doc-contract assertion on an old md path; replaced by `` `records.py debt list --open` `` on the same `line` |
| 5-9 | five `self.assertIn(".workflow/DEBT.md", self.line(...))` in `test_e3_07_...` (skill `**Mirror:**`, release `\| 0b \|`, lifecycle `**Won't fix**`, fix `**No feature:**`, fix `**Cannot reproduce:**`) | doc-contract assertions on an old md path; each replaced one-for-one (4 by `.workflow/debt.jsonl`, release 0b by `records.py debt list --open`); same five doc lines still asserted |
| 10 | `self.assertIn("used = file or database + hook", line)` | doc-contract assertion on routing.md wording of the old state-file model; replaced by `"used = registry or bug database + hook"` on the same line |
| 11 | `source = (HERE / "bugs.py").read_text(encoding="utf-8")` | assertion input, not an assertion: now `bugs.py` + `journal.py` text because `shown()` moved to the shared engine; the following `assertIn("def shown(value, limit=40)", ...)` and the three `shown(...)` call asserts are unchanged context |

Result: removed logic assertions = 0. Removed assertions = 8 (rows 2, 4, 5-9, 10), all doc-contract, all replaced by an equivalent assertion on the same doc line. No assertion was dropped or loosened.
Weak point to note: row 11 widens the searched text, so `def shown(...)` could now be found in either file. The assertion still requires the definition to exist and is not looser in a way that hides a regression of the redaction limits.
Added in the same diff (context, not required): journal.py copy into the two fixtures (lines ~153, ~2229) and a new test block from line ~2809 (+144 lines).

## Findings

None. No live stale reference (C4), no removed logic assertion (C5).

## Not covered

- Running any test suite (`test_bugs.py`, `test_records.py`, `hooks/tests/run.ps1`): not in C4/C5 scope; owner `qa-lead` plan other cases.
- `.gitignore`, `.workflow/`, `.memory/` and tracked game-root files were not scanned for the patterns (outside the planned scope); the `.gitignore` hits above were seen incidentally.
- Whether the doc-contract replacements (rows 2-10) match the current text of the target docs: confirmed only by the test diff; passing them needs a test run.

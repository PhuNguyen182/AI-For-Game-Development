# C2 — Real-repo migrate dry run (criterion 9)

- Executor: main session. Commit: `29a5cbd` (feature/workflow-state-stores), main checkout. Python 3.14.7.
- Precondition: the 5 approved English rewordings applied in `game-production-agent.md:23`, `skill-template-migration.md:27,31,91`, `sqlite-bug-tracker.md:159`.

## Command
`python3 -I .claude/skills/records/scripts/records.py --root . migrate --from-md --dry-run`

## No-write proof
- Before and after the run: `git status --porcelain`, SHA-256 of `.workflow/*.jsonl`, `.workflow/framework-backlog.md`, `.workflow/DEBT.md`, `.workflow/rounds.json`, `.workflow/features/*.md`, and the count of `*.migrated-*` entries in `.workflow/` were captured and diffed: identical, 0 `*.migrated-*` files.
- Two earlier refused dry runs (an unescaped `|` in this feature file's Log row 13; then a Vietnamese quote in its Main GD decisions) printed `migrate refused, nothing was changed`; the same snapshot diff was identical after the second one. Both lines were fixed in the feature file.

## Output (final run, exit 0)
```
.workflow/framework-backlog.md: 45 rows -> fwbacklog; 37 table rows in other sections kept in the renamed file
.workflow/backlog.md: absent
.workflow/DEBT.md: 7 bullets -> debt; 2 other lines kept in the renamed file
.workflow/features/engineer-skill-gaps.md: registry 1 (Closed) · decisions 9 · log 14 · tests 0 · limitations 13 · journal round 0, extra_round 0, stop_rule 0 · bugs table rows dropped 5 (bugs.py holds them)
.workflow/features/game-production-agent.md: registry 1 (Closed) · decisions 18 · log 8 · tests 10 · limitations 10 · journal round 1, extra_round 1, stop_rule 2 · 1 other lines kept · bugs table rows dropped 4 (bugs.py holds them)
.workflow/features/skill-template-migration.md: registry 1 (Closed) · decisions 11 · log 20 · tests 12 · limitations 11 · journal round 0, extra_round 0, stop_rule 0 · 1 other lines kept
.workflow/features/sqlite-bug-tracker.md: registry 1 (Closed) · decisions 23 · log 38 · tests 6 · limitations 18 · journal round 0, extra_round 1, stop_rule 1 · 1 other lines kept · bugs table rows dropped 9 (bugs.py holds them)
.workflow/features/workflow-state-stores.md: registry 1 (Open) · decisions 16 · log 14 · tests 7 · limitations 11 · journal round 2, extra_round 0, stop_rule 0
feature roots: no DEBT.md or NOTES.md
.workflow/rounds.json: 30 events -> .workflow/ledger.db (ledger migrate)
verified: every render holds its source rows; counters equal for 1 open feature(s)
dry run: nothing written
```
(The workflow-state-stores counts grow as this open feature file grows; the real run's own verification is the final check.)

## Independent tally — `framework-backlog.md`
- Python over the file: 94 lines starting with `|`; 6 separator lines (6 tables) → 94 − 6 × 2 = 82 data rows = 45 migrated (top table + `## Deferred and recorded`, header `Item | State`) + 37 kept (pre-slim history sections: Awaiting the GD's review, Open, Scenario-simulation rounds, Findings of the fifth scoring round). Reconciled.
- The 37 kept rows are reference history; decision recorded (D9 amendment): `framework-backlog.migrated-*.md` stays on disk after the real run because the framework repo git-ignores it.

## Result
PASS: exit 0, 0 cells refused, render-vs-source verified, counters equal, nothing written.

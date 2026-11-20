# Workflow state stores

- State: records.py feature show workflow-state-stores

## Request (verbatim)
> update cho tôi workflow hiện tại, khi ledger, backlog, state của các item cần ghi lại thì nên lưu lại dạng sqlite. Kiểm tra xem những flow nào đang áp dụng sqlite trong quy trình này rồi

> (scope answer) File DEPT là file chung của cả dự án hay là cho tính năng thôi, nếu là áp dụng chung cho cả dự án thì chuyển sang sqlite, không thì để dạng markdown như cũ. Các file được đề xuất cũng tương tự theo quy mô. Nếu là quy mô project/repo thì đổi dạng sqlite, không thì để nguyên markdown như hiện tại

> (plan revision) ledger cấp project/repo thì lưu dạng db, các ledger, debt, notes cấp feature thì lưu dạng CSV, update luôn cả skill viết docs cho feature

## Main GD decisions

- Rows: records.py csv render decisions --feature workflow-state-stores

## Spec
Full spec: `.workflow/features/workflow-state-stores.spec.md`.

Acceptance criteria:
1. `journal.py` holds the shared journal engine; `bugs.py` uses it; `test_bugs.py` logic tests pass unchanged.
2. `records.py` stores `backlog`, `fwbacklog`, `debt`, `feature` over tracked journals with a gitignored `records.db` cache; add/update/set-state/list/show/search/sql/render/rebuild/doctor/stats work; journals rebuild the cache and union-merge.
3. Write rules match `bugs`: English only, field limits, secrets refused, PII redacted, main-GD-only moves need `--by "main GD"`, writes refused from a linked worktree.
4. Feature CSVs (`log`, `tests`, `decisions`, `limitations`, `DEBT.csv`, `NOTES.csv`) are written only through `records.py csv` with fixed schemas; `csv doctor` reports a broken file.
5. `bugs.py` Won't fix / Accepted mirrors to the feature root's `DEBT.csv` or a `debt` record without a hand step.
6. `round-cap.ps1` reads and writes the ledger in `.workflow/ledger.db`; caps, extra rounds, parking, corrupt handling and adviser pass-through behave as before; feature counters come from the registry journal (`decisions.csv` holds a readable copy of extra-round and stop-rule rows; see Main GD decisions, review round 1).
7. `session-start.ps1` prints a `Records:` line and creates empty journals; un-migrated files are reported.
8. `feature-docs`, `feature`, its template and every consumer use the new contract; no live reference to the old `.md`/`rounds.json` stores remains outside migration code.
9. `records.py migrate --from-md` converts this repo's framework backlog, project DEBT, feature files and `rounds.json` with equal row counts.
10. `framework-sync.ps1` installs the new `.gitattributes` and `.gitignore` lines in a target project.

## Log

- Rows: records.py csv render log --feature workflow-state-stores

## Tests

- Rows: records.py csv render tests --feature workflow-state-stores

## Bugs

- Bugs: bugs.py list --feature workflow-state-stores

## Known limitations

- Rows: records.py csv render limitations --feature workflow-state-stores

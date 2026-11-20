# Workflow state: SQLite at project scope, CSV at feature scope

## Context
The main GD wants recorded workflow state out of free-form markdown/JSON, by scope:
- **Project/repo-scope** ledgers, backlogs, debt, item states → **SQLite** (tracked `.jsonl` journal is the truth, gitignored DB is the cache — the `bugs` pattern; a local-only store is a DB record).
- **Feature-scope** ledgers, debt, notes → **CSV**, one file per table, written through a validating CLI.
- Prose stays markdown. The `feature-docs` skill is updated to the new layout.

### Inventory and decision
| Store | Scope | Today | Becomes |
|---|---|---|---|
| Bugs `bugs.jsonl` + `bugs.db` | project | **SQLite** (`bugs.py`) | keep; moves onto the shared engine |
| Memory `mem.db` | project | **SQLite** (`mem.py`) | keep |
| Advisory `advisory.db` | project, per machine | **SQLite** (`adv.py`) | keep |
| Round ledger `.workflow/rounds.json` | project, local | JSON + file lock | **SQLite** `.workflow/ledger.db` (local record) |
| Game backlog `.workflow/backlog.md` | project | md table | **SQLite** `backlog` |
| Framework backlog `.workflow/framework-backlog.md` | repo | md, 94 rows | **SQLite** `fwbacklog` |
| Project debt `.workflow/DEBT.md` | project | md, manual mirror | **SQLite** `debt` |
| Feature header (Status, CP, Size, Risk, Rounds, Branch, Worktrees…) | registry across features | md lines 3-13 | **SQLite** `feature` registry |
| Feature file Log, Tests, Main GD decisions, Known limitations | feature | md tables/lists | **CSV** `.workflow/features/<slug>/{log,tests,decisions,limitations}.csv` |
| Feature file Bugs table | feature | md copy of bug data | dropped → `bugs.py list --feature <slug>` |
| Feature file Request (verbatim), Spec, acceptance criteria, `*.spec.md` | feature | md | **stays md** (prose) |
| Feature-root `DEBT.md`, `NOTES.md` | feature | md | **CSV** `DEBT.csv`, `NOTES.csv` |
| Feature-root `DECISIONS.md`, `README`, `CONTRACTS`, `INTEGRATION`, `ARCHITECTURE`, `WORKMEMORY` | feature | md | **stays md** (prose) |
| `.workflow/evidence/**` | feature | md reports | stays md |
| `.workflow/editor.lock` | mutex | lock file | stays (a lock, not a record) |

Two kinds of decisions, split on purpose:
- **Main GD decisions** (feature file): short dated rows with a cost, and the hook matches `extra round` lines in them → CSV with a `kind` column (`decision` · `extra-round` · `waiver` · `accepted-gap`), read by the hook via `Import-Csv`. *Amended at review round 1: the hook counts extra rounds and stop rules from the `features.jsonl` journal; these rows are a readable copy.*
- **`DECISIONS.md`** (feature root): design rationale (what, why, rejected option) read in full before undoing a design; one-line capped cells would cut the reasoning, and nothing queries it → stays md.

## Route
`/feature`, size **L** (new framework core system + project-wide migration), framework repo (profile n/a). Branch `feature/workflow-state-stores` off `develop`, worktree (no Editor). Gates: review + QA recommended. Python 3.10+ already mandatory for bug work.

## Design

### 1. Shared engine (no duplication)
- Extract from `.claude/skills/bugs/scripts/bugs.py` into `.claude/skills/records/scripts/journal.py`: `Ctx` + `main_checkout` (:368-431), journal read/append/torn tail/replace (:432, :760-804), `sha`, `next_ts`/`fmt_ts`, `connect`, `Cleaner` + `mem_module` + `check_english` (:183-293), read-only `sql` gate (:1151-1211), `Writer` skeleton (:805).
- `bugs.py` loads it by path with `importlib` (same pattern as `mem_module`, bugs.py:193; `-I` drops the script dir from `sys.path`).
- `test_bugs.py` logic tests run unchanged as the regression guard; its doc-contract tests that assert `.workflow/DEBT.md` (test_bugs.py:2556-2644) are updated to the new paths.

### 2. New skill `records` — `records.py` CLI

**2a. Project stores (SQLite).** One cache `.workflow/records.db` (gitignored), one journal per store, per-journal hash in `meta`, FTS5 over text:

| Store | Journal | Fields | States |
|---|---|---|---|
| `backlog` (game) | `.workflow/backlog.jsonl` tracked | `num, feature, milestone, size, risk, depends_on, status` (plan-game step 4 columns) | per `plan-game` |
| `fwbacklog` | `.workflow/framework-backlog.jsonl` — gitignored in the framework repo, tracked in a game repo (today's `.md` rule) | `item, state, ref` | `Open` · `Done` · `Recorded` · `Recorded (main GD decision)` · `Deferred` |
| `debt` | `.workflow/debt.jsonl` tracked | `text, source, next_step, accepted_by, date` | `Open` · `Paid` |
| `feature` | `.workflow/features.jsonl` tracked | `slug, status, cp, next_step, session, size, risk, profile, feature_root, branch, base, build_mode, worktrees, rounds {review, qa, rework: used/cap}` | `Open` · `Closed` · `Abandoned` |

Commands: `add`, `update`, `set-state`, `list [--open] [--json]`, `show`, `search`, `sql`, `render` (md table view for CP reports), `rebuild`, `doctor [--fix]`, `stats`. Same write rules as bugs: English only, one-line fields with limits, secrets refused, PII redacted, main-GD-only moves need `--by "main GD"`, writes refused from a linked worktree.

**2b. Feature ledgers (CSV).** `records.py csv add|update|list|render <table> --feature <slug>`; the CLI owns the file, agents never hand-edit a CSV.
- Fixed schemas (header row, UTF-8 no BOM, LF, RFC 4180 via Python `csv`, stable `id` column):
  - `.workflow/features/<slug>/log.csv`: `id, agent, lane, changed, verified, attempts, limitations`
  - `.../tests.csv`: `criterion, test_id, mode, owner, last_result`
  - `.../decisions.csv`: `id, date, kind, decision, cost` (`kind=extra-round` rows carry `counter +n`; written by `feature extra-round`/`stop-rule` as a readable copy; the counter source is the journal — amended at review round 1)
  - `.../limitations.csv`: `id, date, text, accepted_by, mirrored`
  - `<feature root>/DEBT.csv`: `id, date, kind (workaround|limitation|accepted-gap), text, source, accepted_by, next_step, state (Open|Paid)`
  - `<feature root>/NOTES.csv`: `id, date, topic, text, anchor, state (Open|Promoted:<doc>)`
- Same text checks as the DB stores (English, limits, secrets, PII). `csv doctor` validates header, column count, ids.
- `.gitattributes`: `merge=union eol=lf` for these CSVs (append-only rows merge cleanly).
- Closure: `records.py csv mirror --feature <slug>` copies `limitations.csv` rows into `<feature root>/DEBT.csv` (`mirrored` set), replacing the manual step.
- `bugs.py set-status … "Won't fix"|"Accepted"`: with a feature → appends to that feature root's `DEBT.csv` (root from the `feature` registry); without → appends a `debt` record. Removes both manual mirrors.

### 3. Round ledger → `.workflow/ledger.db`
- Local record, gitignored, not journaled (matches today's `rounds.json`). Table `round_event(key, counter, event_id, ts, UNIQUE(key, counter, event_id))`, WAL, `busy_timeout`.
- `records.py ledger add|get --json|import-pending|migrate`.
- `round-cap.ps1`: replace `ConvertTo-Ledger` and the file lock with `Invoke-Records` (new in `common.ps1`, cloned from `Invoke-Bugs` :953). Same semantics: busy → park in `rounds.pending-<id>.json`, merged on the next write; unreadable DB → moved aside, dispatch fails closed; advisers pass before the ledger is read.
- `Get-FeatureCounters` reads file-only rounds from `records.py feature counters <slug> --json` instead of the `- Rounds:` regex; the edit-mode "no Rounds line" warning becomes "feature not in registry".
- **Cost:** Python on every gated dispatch and SubagentStop count (~190 ms each, measured for bugs); no Python → gated dispatches block.

### 4. Skills, hooks, templates
- **`feature-docs/SKILL.md`:** file table splits into prose docs (md, `DECISIONS.md` included) and ledgers (CSV: `DEBT.csv`, `NOTES.csv` with their columns); Read orders updated (`DEBT` → `DEBT.csv`, plus `records.py debt list` for project debt); Write rules: ledgers only via `records.py csv add`, one row per limitation/observation in the same change, `DECISIONS.md` appended as today; "promote a note" = set `state Promoted:<doc>`; no empty CSV (header-only file never written).
- **`feature/SKILL.md` + `references/feature-template.md`:** header → `- State: records.py feature show <slug>`; Log/Tests/decisions/limitations → CSV commands; Bugs table removed; closure commit list updated (`features.jsonl`, the feature's CSVs, `DEBT.csv`, `backlog.jsonl`, `bugs.jsonl`).
- **`session-start.ps1`:** `Records:` status line (open features, open backlog, open fwbacklog, debt); create empty journals instead of copying `templates/framework-backlog.md`; detect un-migrated `.md`/`rounds.json` and print the migrate command.
- **Consumers updated:** `plan-game` step 4, `product-review`, `product-quality-bar`, `product-owner` agent, `new-project` step 5, `release` row 0b, `bugs/SKILL.md` + `references/schema.md` Mirror, `fix`, `qa`, `review`, `code-review-method`, `qa-standards/references/bug-lifecycle.md`, `rules/core.md` (Memory: framework-backlog line), `rules/routing.md` (State section), `.gitattributes`, `.gitignore` (`records.db*`, `ledger.db*`, framework-backlog journal), `tools/framework-sync.ps1`, `verify.ps1` `$HookContracts`.

### 5. Migration (main checkout, after merge)
- `records.py migrate --from-md`:
  - `framework-backlog.md` (94 rows) → `fwbacklog`; `.workflow/DEBT.md` (7 lines) → `debt`; `rounds.json` → `ledger.db` (renamed `rounds.migrated-<utc>.json`).
  - The 4 feature files: header → registry; Log, Tests, Main GD decisions, Known limitations → that feature's CSVs; md keeps Request + Spec.
  - No feature-root `DEBT.md`/`NOTES.md` exist in this repo; the path still ships for game projects (`--from-md` converts them there). Existing `extra round` lines in Main GD decisions migrate as `kind=extra-round` rows; a migration test checks the hook's caps are identical before and after.
- Dry run on a copy first; `render` output must match the source rows; then remove the old `.md` files.

## Verification
- `python -I .claude/skills/records/scripts/test_records.py` (new, temp repos): journal replay, union merge of two branches (journals and CSVs), torn tail, hash check after `git switch`, worktree refusal, limits, secret/Vietnamese refusal, CSV quoting (comma, quote, newline refused), `csv doctor` on a broken file, bug → `DEBT.csv`/`debt` auto-mirror, ledger busy/corrupt paths, migration round-trip.
- `python -I .claude/skills/bugs/scripts/test_bugs.py`: all pass (logic tests unchanged, doc-contract tests updated).
- `.claude/hooks/tests/run.ps1` on pwsh 7 and 5.1: ledger cases rewritten against `ledger.db`, all pass.
- `verify.ps1` whole layer exit 0; `/verify-layer`.
- Migration on a copy: row counts and `render` diff equal to source.
- Live: one `claude -p` in a temp repo with a feature at its review cap → dispatch blocked, at-cap warning delivered.

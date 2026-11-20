---
name: records
description: "Workflow records CLI: backlogs, debt, feature registry and CSVs, round ledger. Use to read or write them."
user-invocable: false
---

# records — workflow records

- **Truth:** each store's `.workflow/<journal>.jsonl` is the truth; `.workflow/records.db` is one gitignored cache every command refreshes per journal.
- **Ledger:** `.workflow/ledger.db` is a local record of hook-counted rounds, gitignored and never journaled.
- **Feature CSVs:** a feature's ledgers, debt and notes are CSV files the CLI owns; never hand-edit one.
- **Writer:** the main session only. Agents propose; agents with no shell get `show` or `render` output in the brief.
- **Python:** `<python>` is the interpreter on the session-start `Memory:` line (`Query: <python> -I ...`).
- **Engine:** `bugs.py` loads the same engine: one set of content rules, one root rule, one write path.

## References
- **[schema.md](references/schema.md):** stores, fields, states, journal format, ledger, counters shape, CSV tables, mirrors, migration, exit codes.

## Scripts
- **[records.py](scripts/records.py):** run `<python> -I "${CLAUDE_SKILL_DIR}/scripts/records.py" --root <project root> <store|command> ...` → the commands below.
- **[journal.py](scripts/journal.py):** the shared engine `records.py` and `bugs.py` load by path; never run it.

## Stores
| Store | Journal | Id | States |
|---|---|---|---|
| `backlog` | `.workflow/backlog.jsonl` | `BL-####` (`#` = its number) | `todo` · `in progress` · `done` · `dropped` |
| `fwbacklog` | `.workflow/framework-backlog.jsonl` | `FW-####` | `Open` · `Done` · `Recorded` · `Recorded (main GD decision)` · `Deferred` |
| `debt` | `.workflow/debt.jsonl` | `DEBT-####` | `Open` · `Paid` |
| `feature` | `.workflow/features.jsonl` | its slug | `Open` · `Closed` · `Abandoned` |

## Writing rules
- **English only:** translate first. The CLI catches diacritics, not Vietnamese typed without them.
- **One line:** every field, note and `--by`; each renders into a table cell. Limits refuse, never truncate.
- **Stdin:** fields go as a JSON object on stdin: PowerShell expands `$` in arguments. Before a PowerShell pipe run `$OutputEncoding = [Text.UTF8Encoding]::new($false)`.
- **Secrets and PII:** secret shapes are refused and PII is redacted on every write; a refusal never echoes the value.
- **Check first:** `search` before `add`.
- **Main GD only:** a move into or out of `Recorded (main GD decision)`, and `feature extra-round`: pass `--by "main GD"` on the main GD's order only.
- **Done needs a ref:** `fwbacklog` `Done` takes `--ref <commit sha or path>`, or a `ref` set earlier.

## Write
| Need | Command |
|---|---|
| New record, prints its id | `<store> add [--by W]`, stdin: the store's fields (schema.md), optional initial state and `note` |
| Change fields, or a `note` alone | `<store> update <id> [--by W]`, stdin: any updatable field |
| Move the state | `<store> set-state <id> "<state>" --note N [--by W] [--ref R]` |
| Used file-only round; `+n` is 1 to 100 | `feature round <slug> review\|qa\|rework +n --note N` |
| main GD's extra round, raises the cap | `feature extra-round <slug> <counter> +n --note N --by "main GD"` |
| Stop rule fired or spent | `feature stop-rule <slug> <counter> --extra-dispatch unused\|used` |
| Hook-counted rounds | `ledger add --json`, stdin `[{"key","counter","id"}]`; exit 4: the refused ones kept in `rounds.rejected-*.json`, the rest recorded |
| Import `rounds.json` | `ledger migrate` |

## Query
| Need | Command |
|---|---|
| One record with events | `<store> show <id> [--json]` |
| Records | `<store> list [--state S] [--open] [--json]` |
| Check existing records | `<store> search "<words>" [-n 10]` |
| Markdown table for a CP report | `<store> render` |
| One line | `<store> stats`, or `stats` for every store; `stats --json` adds the open features (session start) |
| Hook counters | `feature counters <slug> --json` |
| Hook counters and ledger in one call (round-cap's dispatch) | `feature counters <slug> --json --with-ledger` |
| Hook ledger | `ledger get --json` |
| Anything else, read-only | `sql "SELECT ..." [--json]` |

## Repair
| Need | Command |
|---|---|
| Rebuild the cache | `rebuild` |
| Report a malformed or torn line, duplicate ids, journal attributes or ignore rules | `doctor` |
| Repair them | `doctor --fix` (appends a durable `renumber`; a malformed line is reported for a hand fix) |

## Feature CSV tables
| Table | File | Id |
|---|---|---|
| `log` | `.workflow/features/<slug>/log.csv` | `L-001` |
| `tests` | `.workflow/features/<slug>/tests.csv` | `T-001` |
| `decisions` | `.workflow/features/<slug>/decisions.csv` | `D-001` |
| `limitations` | `.workflow/features/<slug>/limitations.csv` | `LIM-001` |
| `debt` | `<feature root>/DEBT.csv` | `DEBT-001` |
| `notes` | `<feature root>/NOTES.csv` | `N-001` |

- **Columns:** fixed per table (schema.md); every value one line, 1000 chars, through the same content rules as the stores.
- **Formula prefix:** a value starting with `=`, `+`, `@`, TAB or CR, or with `-` unless it opens `- ` and a letter (`- item`) or `--` and a lowercase flag name (`--by`, `--dry-run`) with no `|` anywhere, is refused (a spreadsheet would run it); reword it.
- **Feature root:** `debt` and `notes` need the registry's `feature_root`; with none, the refusal prints the `feature update` command.
- **Journal-backed rows:** a `decisions` row of kind `extra-round` or `stop-rule` comes only from `feature extra-round` or `feature stop-rule`.
- **Counters:** the `features.jsonl` journal is the only source of `feature counters`; `decisions.csv` `extra-round` and `stop-rule` rows are a readable copy, never counted.

| Need | Command |
|---|---|
| New row, prints its id | `csv add <table> --feature <slug>`, stdin: the row's columns, no `id` |
| Change a row | `csv update <table> <id> --feature <slug>`, stdin: the changed columns |
| Rows | `csv list <table> --feature <slug> [--json]` |
| Markdown table for a CP report | `csv render <table> --feature <slug>` |
| Report a broken file: header, columns, duplicate ids, BOM, CRLF, values (a formula-prefix cell included) | `csv doctor [<table>] --feature <slug>` |
| Repair it: later duplicates renumbered, BOM and CRLF dropped | `csv doctor [<table>] --feature <slug> --fix` |
| Closure: unmirrored limitations into the feature root's `DEBT.csv` | `csv mirror --feature <slug>` |

## Bug debt mirror
- **Automatic:** a `bugs.py` move to `Won't fix` or `Accepted` appends the debt entry itself: the bug's feature root's `DEBT.csv` when the registry names one, else a `debt` record; once per bug. A formula-shaped title or note lands as `Bug title: …` or `Note: …`.
- **Repair:** when that mirror fails after the move, `bugs.py` exits 1 and prints `bug-mirror BUG-####`: run that command.

## Migrate from markdown
- **Run:** `migrate --from-md --dry-run` first, then `migrate --from-md`; the main checkout only.
- **Sources:** `framework-backlog.md`, `backlog.md`, `DEBT.md`, each feature file, each feature root's `DEBT.md` and `NOTES.md`, and `rounds.json`.
- **All or nothing:** staged in a temp folder, read back through `render`, then swapped in; a refusal lists every source line to fix and changes nothing.

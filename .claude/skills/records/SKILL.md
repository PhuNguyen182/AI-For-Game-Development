---
name: records
description: "Workflow records CLI: backlog, framework backlog, debt, feature registry, round ledger. Use to read or write them."
user-invocable: false
---

# records — project-scope workflow records

- **Truth:** each store's `.workflow/<journal>.jsonl` is the truth; `.workflow/records.db` is one gitignored cache every command refreshes per journal.
- **Ledger:** `.workflow/ledger.db` is a local record of hook-counted rounds, gitignored and never journaled.
- **Writer:** the main session only. Agents propose; agents with no shell get `show` or `render` output in the brief.
- **Python:** `<python>` is the interpreter on the session-start `Memory:` line (`Query: <python> -I ...`).
- **Engine:** `bugs.py` loads the same engine: one set of content rules, one root rule, one write path.

## References
- **[schema.md](references/schema.md):** stores, fields, states, journal format, ledger, counters shape, exit codes.

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
| Hook-counted rounds | `ledger add --json`, stdin `[{"key","counter","id"}]` |
| Import `rounds.json` | `ledger migrate` |

## Query
| Need | Command |
|---|---|
| One record with events | `<store> show <id> [--json]` |
| Records | `<store> list [--state S] [--open] [--json]` |
| Check existing records | `<store> search "<words>" [-n 10]` |
| Markdown table for a CP report | `<store> render` |
| One line | `<store> stats`, or `stats` for every store |
| Hook counters | `feature counters <slug> --json` |
| Hook ledger | `ledger get --json` |
| Anything else, read-only | `sql "SELECT ..." [--json]` |

## Repair
| Need | Command |
|---|---|
| Rebuild the cache | `rebuild` |
| Report a malformed or torn line, duplicate ids, journal attributes or ignore rules | `doctor` |
| Repair them | `doctor --fix` (appends a durable `renumber`; a malformed line is reported for a hand fix) |

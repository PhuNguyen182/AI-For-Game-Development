---
name: bugs
description: "Bug tracker CLI: one SQLite record per bug over a tracked journal. Use to file, move, query or purge bugs."
user-invocable: false
---

# bugs — bug records

- **Truth:** `.workflow/bugs.jsonl` is tracked and is the truth; `.workflow/bugs.db` is a gitignored cache every command refreshes.
- **Writer:** the main session only. Agents propose; agents with no shell get `show` output in the brief.
- **Python:** `<python>` is the interpreter named on the session-start line.
- **Brief markers:** `Bug: BUG-####` and `Verify: BUG-####` lines stay as they are; the hook reads them.

## References
- **[schema.md](references/schema.md):** the state machine, journal format, tables, purge, migration, or tests.

## Scripts
- **[bugs.py](scripts/bugs.py):** run `<python> -I "${CLAUDE_SKILL_DIR}/scripts/bugs.py" --root <project root> <cmd>` → the commands below.

## Writing rules
- **English only:** translate the GD's or QA's words before filing. The CLI catches diacritics, not Vietnamese typed without them.
- **Localized text:** cite a localized string under test by its table key, not its text.
- **One line:** `title`, `description`, `feature`, `owner`, `regression_test`, notes and `--by` hold no line break.
- **Short:** title names the system and the defect; description says what breaks, where, and the impact. No prose.
- **Evidence:** paths or a one-line excerpt; full logs stay in `.workflow/evidence/`.
- **Expected:** names its source. **Repro:** numbered steps from a known state, attempts and hits, or `not yet`.
- **Stdin:** long text goes as a JSON object on stdin, because PowerShell expands `$` in arguments. Send UTF-8.
- **Secrets and PII:** secret shapes are refused and PII is redacted on every write. A refusal never truncates: fix the text.
- **Check first:** `search` before `add`. A match is evidence on that ID; a match on a settled bug moves it to `Reopen`.
- **GD only:** moves to `Backlog`, `Won't fix`, `Accepted`, from `Backlog` to `Request`, and `delete`: pass `--by GD` on the GD's order only.
- **Mirror:** `Won't fix` and `Accepted` also go to `DEBT.md`.

## Write
| Need | Command |
|---|---|
| File a bug, prints its ID | `add [--by W]`, stdin: `title description priority repro expected actual evidence`, optional `feature owner regression_test root_cause note` |
| Change fields | `update <id> [--by W]`, stdin: any of those fields |
| Move status | `set-status <id> "<status>" [--note N] [--by W] [--duplicate-of BUG-####]`, or stdin: `{"note": ...}` |
| Used round | `round <id> fix\|review +1 --note N` |
| GD's extra round, raises the cap | `extra-round <id> fix\|review +n --note N` |
| Stop rule fired or spent | `stop-rule <id> fix\|review --extra-dispatch unused\|used` |
| Drop a bug on the GD's order | `delete <id> --by GD` |
| Purge past the window | `purge [--dry-run]`; session start runs `purge --auto` |
| Migrate the old file | `import-md`, then delete the file; every other command refuses until it is gone |

## Query
| Need | Command |
|---|---|
| One record with events | `show <id> [--json]` |
| Records | `list [--status S] [--priority P] [--feature F] [--open] [--json]` |
| Check existing bugs | `search "<words>" [-n 10]` |
| Anything else, read-only | `sql "SELECT ..." [--json]` |
| Hook counters | `counters <id> --json` |
| One status line | `stats` |

## Repair
| Need | Command |
|---|---|
| Rebuild the cache | `rebuild` |
| Report duplicates, a torn line, inert lines | `doctor` |
| Repair them | `doctor --fix` (appends a durable `renumber`); a malformed line is reported for a hand fix |

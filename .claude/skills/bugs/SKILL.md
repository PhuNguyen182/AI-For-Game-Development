---
name: bugs
description: "Bug tracker CLI: one SQLite record per bug over a tracked journal. Use to file, move, query or purge bugs."
user-invocable: false
---

# bugs — bug records

- **Truth:** `.workflow/bugs.jsonl` is tracked and is the truth; `.workflow/bugs.db` is a gitignored cache every command refreshes.
- **Writer:** the main session only. Agents propose; agents with no shell get `show` output in the brief.
- **Python:** `<python>` is the interpreter on the session-start `Memory:` line (`Query: <python> -I ...`); the `Bugs:` line names none.
- **Brief markers:** `Bug: BUG-####` and `Verify: BUG-####` lines stay as they are; the hook reads them.

## References
- **[schema.md](references/schema.md):** the state machine, journal format, tables, purge, or tests.

## Scripts
- **[bugs.py](scripts/bugs.py):** run `<python> -I "${CLAUDE_SKILL_DIR}/scripts/bugs.py" --root <project root> <cmd>` → the commands below.

## Writing rules
- **English only:** translate the GD's or QA's words before filing. The CLI catches diacritics, not Vietnamese typed without them.
- **Localized text:** cite a localized string under test by its table key, not its text.
- **One line:** `title`, `description`, `feature`, `owner`, `regression_test`, notes and `--by` hold no line break.
- **Short:** title names the system and the defect; description says what breaks, where, and the impact. No prose.
- **Evidence:** paths or a one-line excerpt; full logs stay in `.workflow/evidence/`.
- **Expected:** names its source. **Repro:** numbered steps from a known state, attempts and hits, or `not yet`.
- **Stdin:** long text goes as a JSON object on stdin: PowerShell expands `$` in arguments. Before a PowerShell pipe run `$OutputEncoding = [Text.UTF8Encoding]::new($false)`; Bash needs nothing.
- **Why that line:** Windows PowerShell 5.1's default pipe writes `?` for each non-ASCII character. The CLI cannot detect it: the write succeeds and Vietnamese evades the refusal.
- **Secrets and PII:** secret shapes are refused and PII is redacted on every write. A refusal never truncates: fix the text.
- **Check first:** `search` before `add`. A terminal match moves to `Reopen`; a `Backlog` match takes evidence with `update`, as it cannot reach `Reopen`; a `Duplicate` hit: follow `duplicate_of`.
- **Evidence on a match:** `update` with a `note` alone. The `evidence` field is replaced by an `update`, never appended.
- **GD only:** moves to `Backlog`, `Won't fix`, `Accepted`, from `Backlog` to `Request`, and `delete`: pass `--by GD` on the GD's order only.
- **Mirror:** `Won't fix` and `Accepted` also go to `DEBT.md`: the feature root's, or `.workflow/DEBT.md` for a bug with no feature.

## Write
| Need | Command |
|---|---|
| File a bug, prints its ID | `add [--by W]`, stdin: `title description priority repro expected actual evidence`, optional `feature owner regression_test root_cause note` |
| Change fields, or a `note` alone to record evidence | `update <id> [--by W]`, stdin: any of those fields |
| Move status | `set-status <id> "<status>" --note N [--by W] [--duplicate-of BUG-####]`; stdin `{"note": ...}` can replace `--note` |
| Used round; `+n` is 1 to 100 per call | `round <id> fix\|review +1 --note N` |
| GD's extra round, raises the cap; `+n` is 1 to 100 per call | `extra-round <id> fix\|review +n --note N` |
| Stop rule fired or spent | `stop-rule <id> fix\|review --extra-dispatch unused\|used` |
| Drop a bug on the GD's order | `delete <id> --by GD` |
| Purge past the window | `purge [--dry-run]`; session start runs `purge --auto` |

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
| Report duplicates, a torn line, inert lines, a journal git ignores, does not union-merge or does not keep LF | `doctor` |
| Repair them | `doctor --fix` (appends a durable `renumber`); a malformed line is reported for a hand fix |

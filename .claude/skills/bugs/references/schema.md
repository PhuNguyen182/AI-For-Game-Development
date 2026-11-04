# bugs — schema and state machine

Synthesized from `../scripts/bugs.py`; commands in `../SKILL.md`.

## Statuses
- **Open (every status but the terminal five):** `Request` · `Processing` · `Resolved` · `Review` · `Reopen` · `Backlog`.
- **Terminal (settled, purgeable):** `Complete` · `Won't fix` · `Accepted` · `As designed` · `Duplicate`.
- **Backlog:** counts as open for `stats` and `list --open`, and as settled for `counters` and QA sign-off with a `Known limitations` line. Never capped; never purged.

## Priorities
- **Scale:** `Low` · `Medium` · `High` · `Highest`. A QA Severity of `Critical` maps to `Highest` (`qa-standards`).

## State machine
| From | To | Set when |
|---|---|---|
| (new) | `Request` | QA files it (`add`) |
| `Request`, `Reopen` | `Processing` | Main session dispatches the owner |
| `Processing` | `Request` | Attempt `Failed` or `Blocked`, no fix delivered |
| `Processing` | `Resolved` | Owner's `Fixes:` and `/fix` step 6 checks pass |
| `Resolved` | `Review` | Main session dispatches a `Verify:` brief |
| `Review` | `Complete` | `Repro: BUG-#### gone` |
| `Review` | `Reopen` | `Repro: BUG-#### reproduces` |
| `Review` | `Resolved` | Verify run returned no `Repro:` line |
| Any terminal | `Reopen` | A new match on a settled bug |
| Any open | `Backlog` | **GD only** |
| `Backlog` | `Request` | **GD only** |
| Any open | `Won't fix`, `Accepted` | **GD only**, mirrored to `DEBT.md` |
| Any open | `As designed`, `Duplicate` | QA or main session (`duplicate_of` required for `Duplicate`) |

- **Enforced on write only:** every other move is refused. Replay never enforces transitions: the history already happened.
- **GD attribution:** a GD-only move needs exactly `--by GD`; a padded form is refused on every path; a note is required on every `set-status`.
- **closed_at:** set when a bug reaches terminal, cleared by any move out of it. The purge clock counts from it: from the last terminal status reached.

## Content limits (over the limit: refused with field and length, never truncated)
| Field | Limit | Rule |
|---|---|---|
| `title` | 100 | Required, one line |
| `description` | 280 | Required, one line |
| `repro` | 500 | Required, or `not yet` |
| `expected`, `actual` | 300 each | Required |
| `evidence` | 300 | Required |
| `root_cause` | 300 | Optional |
| event note | 200 | One line |
| `feature`, `owner` | 100 each | Optional, one line |
| `regression_test` | 200 | Optional, one line |
| `--by` | 100 | One line |

- **Checked on every text value:** control characters, Vietnamese diacritics (any Unicode form), secret shapes via `mem.py`, then PII redaction. The limit applies to the stored text.
- **Fail closed:** a missing or broken `mem.py` (a syntax error or a failed import included) or pattern file refuses every write, `delete`, `purge` and `doctor --fix` included, with no traceback; reads do not need them.
- **Refusal text:** one exit in `main`; secret and PII redaction always runs, so a pasted secret as an ID, a status or a JSON key never reaches stderr. A value over its limit is not echoed: 40 chars for an ID, status or key, 200 for a SQLite message or `--root`, 300 for an argparse message. A line stops at 500. With nothing to scan, values are hidden. Unrecognized arguments are counted, never quoted. A fault in `mem.py`, `SystemExit` and `BaseException` included, refuses; an empty pattern list counts as one. An interrupt prints `bugs: interrupted`, exit 130.
- **Stdin encoding:** the CLI reads UTF-8. Windows PowerShell 5.1's default pipe turns each non-ASCII character into `?` first, and the CLI cannot detect the loss; run `$OutputEncoding = [Text.UTF8Encoding]::new($false)` before the pipe.

## Journal (`.workflow/bugs.jsonl`, tracked; LF, UTF-8, no BOM)
- **Line:** `{event_uid, bug_uid, ts, type, data, by?, note?}`; `ts` is UTC `YYYY-MM-DDTHH:MM:SS.mmmZ`, always `max(now, last + 1 ms)`.
- **Types:** `create` (`id`, `status`, fields) · `update` (changed fields) · `status` (`from`, `to`, `duplicate_of?`) · `round` and `extra_round` (`counter`, `n`) · `stop_rule` (`counter`, `extra_dispatch`) · `renumber` (`from`, `to`) · `tombstone` (`id`, no text).
- **Replay:** sort by `(ts, event_uid)`, one copy per `event_uid`, drop tombstoned uids, creates first. A malformed line refuses every command with its line number.
- **Torn tail:** a final line with no newline is kept when it is a whole event; otherwise skipped and removed by the next write.
- **Counts:** `round` and `extra-round` take `+n`, n from 1 to 100 per call; replay refuses any other `n` as a malformed line.
- **Attributes:** `.workflow/bugs.jsonl text eol=lf merge=union`. `doctor` reports a problem, exit 1, when git resolves `merge` to anything but `union` or `eol` to anything but `lf`, or ignores the journal; `framework-sync.ps1` warns on a target for the same three.

## Consistency
- **Write path:** `BEGIN IMMEDIATE`, hash check, rebuild if different, validate, apply, append, commit. A crash after the append is healed by the next hash mismatch.
- **Hash check:** every command compares the journal's SHA-256 with the DB, which covers `git switch`, pull and merge.
- **No journal:** reads return empty on an in-memory store; the DB appears with the first write.
- **Empty journal:** what `/new-project` and `/feature` create, so a missing one means a broken setup, which `doctor` can report only when git shows the tracked file deleted; a journal git never tracked reads as clean. Reads return empty, `doctor` is clean, the first write takes `BUG-0001`.
- **Duplicate ID:** two `bug_uid`s holding one ID after a merge. `counters` and writes for that ID fail closed until `doctor --fix` appends a `renumber` for the later create. Later lines attach by `bug_uid`.
- **Purged ID:** a tombstone holds its ID. A create on it from another `bug_uid` is a duplicate; `doctor --fix` renumbers that bug. The same `bug_uid` brought back stays gone.
- **High water:** max over creates, tombstones and renumbers. `add` takes the next one; a missing ID below it reads `purged`.
- **Root:** `Ctx` in `bugs.py` and `Get-BugsRoot` in `common.ps1` apply one rule, driven over the same layouts by one test in `hooks/tests/run.ps1`. They read only the given root's own `.git`, never one above it. A `.git` folder or none: that root. A `.git` file: its `gitdir`, then `commondir`, whose folder's parent is the main checkout. `--root` omitted: the project holding the script, by the same rule.
- **No `.git` at the root:** no git context, and writes go to that root's own journal. A subfolder of a checkout counts: `purge --auto` skips, `doctor` checks no attributes.
- **Worktrees:** a linked worktree reads the main checkout's data and every write is refused.
- **Git failing:** git missing, or refusing a `.git` at the root: reads work, every write is refused, `purge --auto` prints `purge skipped: git failed`, and the session line says so.
- **No `commondir`:** that root when the git dir holds `objects` (a submodule or `--separate-git-dir`). Otherwise both refuse: a damaged link must not read as no bugs.
- **Bare repos:** a `commondir` folder not named `.git` refuses, so a linked worktree of a bare repo or of a submodule blocks a dispatch naming a bug and prints `Bugs: unavailable`. A bare repo stored in a folder named `.git` returns that folder's parent instead, which normally has no journal and reads as no bugs.

## Purge
- **Rule:** terminal for strictly more than 90 days. Open and `Backlog` bugs never go. IDs are never reused.
- **Effect:** drops the bug's lines and appends one tombstone, so a union merge from a pre-purge branch cannot resurrect it. `doctor --fix` sweeps lines such a merge brought back.
- **`purge --auto`:** runs only on the main checkout, on a branch outside `feature/*` (a detached HEAD skips), with no merge, rebase, cherry-pick or revert in progress and the journal clean in `git status`. Otherwise it prints `purge skipped: <why>` and exits 0.
- **Output:** one line, `purged M, journal uncommitted` or `purged 0`. It never commits.
- **Not an erase:** committed journal lines stay in git history.

## Counters (`counters <id> --json`)
- **Shape:** `{id, found, settled, status, fix: {used, cap}, review: {used, cap}, record}`. Default caps: fix 2, review 3.
- **Record:** `- Stop rule: <counter> root-caused <date> - extra dispatch: unused|used` and `extra round: <counter> +<n>`, the lines `round-cap.ps1` matches.
- **Exit:** unknown or purged ID `found:false`, exit 0. Duplicate ID or corrupt journal: non-zero with stderr, and the hook fails closed.
- **Ledger:** Python never reads the hook's local ledger; used there is added by the hook.
- **Hook spelling:** `round-cap.ps1` reads any case and padding (`bug-0027`, `BUG-27`, `BUG-00027`) as `BUG-0027`; the CLI takes `BUG-####` only.

## Tables (`.workflow/bugs.db`, gitignored)
- **`bug`:** `id, uid, title, description, priority, status, feature, owner, regression_test, repro, expected, actual, evidence, root_cause, duplicate_of, fix_used, fix_cap, review_used, review_cap, created_at, updated_at, closed_at`. `CHECK` on status and priority; indexes on id, status, priority, feature, closed_at.
- **`bug_event`:** `event_uid, bug_uid, ts, type, by_who, note, data`.
- **`bug_fts`:** FTS5 `porter unicode61 remove_diacritics 2` over the text fields and notes.
- **`meta`:** `journal_hash`, `high_water`, `last_ts`, `purged_ids`.
- **`sql`:** `mode=ro` connection, `query_only`, an authorizer, and a leading-keyword gate; one statement, 1000 rows, 10 seconds. A BLOB prints as its literal, `x'00ff'`.

## Test clock
- **`BUGS_NOW`:** test-only override of the CLI's clock (`2026-01-01T00:00:00Z`, optional `.mmm`). Never set it in a session: a leftover value skews event timestamps and can purge early. `purge` warns on stderr when it is set.

Tests: `python -I .claude/skills/bugs/scripts/test_bugs.py`.

# bugs — schema and state machine

Synthesized from `../scripts/bugs.py`; commands in `../SKILL.md`.

## Statuses
- **Open (every status but the terminal five):** `Request` · `Processing` · `Resolved` · `Review` · `Reopen` · `Backlog`.
- **Terminal (settled, purgeable):** `Complete` · `Won't fix` · `Accepted` · `As designed` · `Duplicate`.
- **Backlog:** counts as open for `stats` and `list --open`, and as settled for `counters` and QA sign-off with a `Known limitations` line. Never capped; never purged.

## Priorities
- **Scale:** `Low` · `Medium` · `High` · `Highest`. Old Severity `Critical` maps to `Highest`.

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
- **GD attribution:** a GD-only move needs exactly `--by GD`; a note is required on every `set-status`.
- **closed_at:** set when a bug reaches terminal, cleared by any move out of it. Purge counts from it.

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
- **Fail closed:** a missing `mem.py` or pattern file refuses the write; reads do not need them.

## Journal (`.workflow/bugs.jsonl`, tracked; LF, UTF-8, no BOM)
- **Line:** `{event_uid, bug_uid, ts, type, data, by?, note?}`; `ts` is UTC `YYYY-MM-DDTHH:MM:SS.mmmZ`, always `max(now, last + 1 ms)`.
- **Types:** `create` (`id`, `status`, fields) · `update` (changed fields) · `status` (`from`, `to`, `duplicate_of?`) · `round` and `extra_round` (`counter`, `n`) · `stop_rule` (`counter`, `extra_dispatch`) · `renumber` (`from`, `to`) · `tombstone` (`id`, no text).
- **Replay:** sort by `(ts, event_uid)`, one copy per `event_uid`, drop tombstoned uids, creates first. A malformed line refuses every command with its line number.
- **Torn tail:** a final line with no newline is kept when it is a whole event; otherwise skipped and removed by the next write.
- **Attributes:** `.workflow/bugs.jsonl text eol=lf merge=union`; `doctor` warns when absent.

## Consistency
- **Write path:** `BEGIN IMMEDIATE`, hash check, rebuild if different, validate, apply, append, commit. A crash after the append is healed by the next hash mismatch.
- **Hash check:** every command compares the journal's SHA-256 with the DB, which covers `git switch`, pull and merge.
- **No journal:** reads return empty on an in-memory store; the DB appears with the first write.
- **Duplicate ID:** two `bug_uid`s holding one ID after a merge. `counters` and writes for that ID fail closed until `doctor --fix` appends a `renumber` for the later create. Later lines attach by `bug_uid`.
- **High water:** max over creates, tombstones and renumbers. `add` takes the next one; a missing ID below it reads `purged`.
- **Worktrees:** root comes from comparing `--git-dir` with `--git-common-dir`. A linked worktree reads the main checkout's data and every write is refused.

## Purge
- **Rule:** terminal for strictly more than 90 days. Open and `Backlog` bugs never go. IDs are never reused.
- **Effect:** drops the bug's lines and appends one tombstone, so a union merge from a pre-purge branch cannot resurrect it. `doctor --fix` sweeps lines such a merge brought back.
- **`purge --auto`:** runs only on the main checkout, on a branch outside `feature/*` (a detached HEAD skips), with no merge, rebase, cherry-pick or revert in progress and the journal clean in `git status`. Otherwise it prints `purge skipped: <why>` and exits 0.
- **Output:** one line, `purged M, journal uncommitted` or `purged 0`. It never commits.
- **Not an erase:** committed journal lines stay in git history.

## Counters (`counters <id> --json`)
- **Shape:** `{id, found, settled, status, fix: {used, cap}, review: {used, cap}, record}`. Default caps: fix 2, review 3.
- **Record:** `- Stop rule: <counter> root-caused <date> - extra dispatch: unused|used` and `extra round: <counter> +<n>`, the lines `round-cap.ps1` matches.
- **Exit:** unknown or purged ID `found:false`, exit 0. Duplicate ID, corrupt journal or a remaining `bugs.md`: non-zero with stderr, and the hook fails closed.
- **Ledger:** Python never reads the hook's local ledger; used there is added by the hook.

## Tables (`.workflow/bugs.db`, gitignored)
- **`bug`:** `id, uid, title, description, priority, status, feature, owner, regression_test, repro, expected, actual, evidence, root_cause, duplicate_of, fix_used, fix_cap, review_used, review_cap, created_at, updated_at, closed_at`. `CHECK` on status and priority; indexes on id, status, priority, feature, closed_at.
- **`bug_event`:** `event_uid, bug_uid, ts, type, by_who, note, data`.
- **`bug_fts`:** FTS5 `porter unicode61 remove_diacritics 2` over the text fields and notes.
- **`meta`:** `journal_hash`, `high_water`, `last_ts`.
- **`sql`:** `mode=ro` connection, `query_only`, an authorizer, and a leading-keyword gate; one statement, 1000 rows, 10 seconds. A BLOB prints as its literal, `x'00ff'`.

## Migration (`import-md`)
- **Mapping:** `Open` → `Request` · `Fixed` → `Resolved` · `Closed` → `Complete` · `Reopened` → `Reopen`; the other four keep their names. A status cell `Duplicate of BUG-####` → `Duplicate` with that target. `description` takes the old `Actual` text. Uids are `uuid5`, so a re-run adds nothing.
- **A broken rule:** stops the whole import with a report of bug, field and length; nothing is written. Rewrite that field by hand, then re-run.
- **Afterwards:** the caller deletes the old file; every other command refuses while it exists.

## Test clock
- **`BUGS_NOW`:** test-only override of the CLI's clock (`2026-01-01T00:00:00Z`, optional `.mmm`). Never set it in a session: a leftover value skews event timestamps and can purge early. `purge` warns on stderr when it is set.

Tests: `python -I .claude/skills/bugs/scripts/test_bugs.py`.

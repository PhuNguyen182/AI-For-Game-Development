# records — schema

Synthesized from `../scripts/records.py` and `../scripts/journal.py`; commands in `../SKILL.md`.

## Stores and fields
| Store | Field | Rule |
|---|---|---|
| `backlog` | `num` | The id's number, the plan's `#`; assigned, never given in `add` |
| `backlog` | `feature` | Required, 100 |
| `backlog` | `milestone` | Required, 60 |
| `backlog` | `size` | Required, `S` · `M` · `L` |
| `backlog` | `risk` | Optional, 200 |
| `backlog` | `depends_on` | Optional comma list of `num`s, stored as `1, 4` |
| `backlog` | `status` | `todo` (default) · `in progress` · `done` · `dropped`; open: `todo`, `in progress` |
| `fwbacklog` | `item` | Required, 1000 |
| `fwbacklog` | `ref` | Commit sha or path, 300; required for `Done` |
| `fwbacklog` | `state` | `Open` (default) · `Done` · `Recorded` · `Recorded (main GD decision)` · `Deferred`; open: `Open`, `Deferred` |
| `debt` | `text` | Required, 300 |
| `debt` | `source` | Required: `BUG-####`, a feature slug, or `framework` |
| `debt` | `next_step` | Optional, 300 |
| `debt` | `accepted_by` | Required, 100 |
| `debt` | `date` | `YYYY-MM-DD`, a real date; default today (UTC) |
| `debt` | `state` | `Open` (default) · `Paid`; open: `Open` |
| `feature` | `slug` | Required, kebab-case `a-z 0-9 -`, 100, unique; the id, never updated |
| `feature` | `status` | `Open` (default) · `Closed` · `Abandoned`; open: `Open` |
| `feature` | `cp` | `none` · `CP1` · `CP2` · `build` · `review` · `CP3` · `QA` · `CP4` |
| `feature` | `size`, `build_mode` | `S` · `M` · `L`; `serial` · `lanes` |
| `feature` | `next_step`, `assemblies`, `worktrees` | 300 each |
| `feature` | `session`, `feature_root`, `branch`, `base`, `risk` | 200 each |
| `feature` | `profile` | 100 |
| any | event note, `--by` | 200, 100 |

- **Every value:** one line; control characters, Vietnamese diacritics (any Unicode form) and secret shapes refused; PII redacted; the limit applies to the stored text.
- **Unknown fields:** refused, named only through the redacted refusal text.
- **Moves:** any state to any other. Into or out of a main-GD state (`Recorded (main GD decision)`) needs exactly `--by "main GD"`; a padded form is refused. A note is required on every `set-state`.
- **Fail closed:** a missing or broken `mem.py` or pattern file refuses every store write and `doctor --fix`; reads and the ledger do not need them.
- **Refusal text:** one exit in `main`, through the same redaction as `bugs`; values over 40 chars are not echoed.

## Journals (`.workflow/<journal>.jsonl`, LF, UTF-8, no BOM)
- **Line:** `{event_uid, uid, ts, type, data, by?, note?}`; `ts` is UTC `YYYY-MM-DDTHH:MM:SS.mmmZ`, always `max(now, last + 1 ms)` per journal.
- **Types:** `create` (`id` or `slug`, fields, state) · `update` (changed fields) · `state` (`from`, `to`, `ref?`) · `renumber` (`from`, `to`, numbered stores) · `round` and `extra_round` (`counter`, `n`) · `stop_rule` (`counter`, `extra_dispatch`), the last three on `feature` only.
- **Replay:** sort by `(ts, event_uid)`, one copy per `event_uid`, creates first. A malformed line refuses every command on that store with its line number; other stores still read.
- **Torn tail:** a final line with no newline is kept when it is a whole event; otherwise skipped and removed by the next write or `doctor --fix`.
- **Feature uid:** derived from the slug, and the create's `event_uid` too: two branches registering one slug merge into one record with both sides' events.
- **Ids:** `BL-####`, `FW-####`, `DEBT-####`, never reused; the high water is the max over creates and renumbers.
- **Attributes:** each journal `text eol=lf merge=union`. `doctor` reports a journal git ignores, except `framework-backlog.jsonl`, which the framework repo ignores and a game repo tracks; an ignored journal's attributes are not checked.

## Cache (`.workflow/records.db`, gitignored)
- **Per store:** `<store>` (fields, `id`, `uid`, `created_at`, `updated_at`; `feature` adds `<counter>_used`, `_extra`, `_cap`), `<store>_event` (`event_uid, uid, ts, type, by_who, note, data`), `<store>_fts` (FTS5 `porter unicode61 remove_diacritics 2` over the text fields and notes).
- **`meta`:** `hash:<store>`, `high_water:<store>`, `last_ts:<store>`. Each command checks only the stores it reads, so a changed journal rebuilds only its own tables.
- **Write path:** `BEGIN IMMEDIATE`, hash check, rebuild if different, validate, apply, append, commit. A crash after the append is healed by the next hash mismatch.
- **Duplicate id:** two records on one id after a union merge. Writes on that id fail closed until `doctor --fix` appends a `renumber` for the later create; a backlog renumber names the rows whose `depends_on` held the old number.
- **Root and worktrees:** the `bugs` root rule. A linked worktree reads the main checkout's data and every write is refused; git failing refuses store writes.
- **`sql`:** `mode=ro`, `query_only`, an authorizer, one leading `SELECT`, `WITH` or `VALUES`; every table; 1000 rows, 10 seconds.

## Feature counters (`feature counters <slug> --json`)
- **Shape:** `{"slug", "found", "open", "size", "review": {"used", "cap"}, "qa": {...}, "rework": {...}, "record"}`, ASCII JSON.
- **Caps:** review 3, QA 2, rework 6 (S, M) or 8 (L), each plus its extra rounds; a size change moves the rework base.
- **Unknown slug:** `found:false`, `open:false`, `size:null`, default caps, rework 6, exit 0.
- **Record:** `- Stop rule: <counter> root-caused <date> · extra dispatch: unused|used` (the last per counter), then one `extra round: <counter> +<n>` per extra round: the lines `round-cap.ps1` matches.
- **Sources:** `COUNTER_SOURCES` in `records.py`: functions `(ctx, slug)` returning extra-round and stop-rule events beside the journal's; each adds to the cap and the record.
- **Used:** file-only rounds here; the hook adds the ledger's count.

## Ledger (`.workflow/ledger.db`, local, gitignored, not journaled)
- **Table:** `round_event(key, counter, event_id, ts, UNIQUE(key, counter, event_id))`, WAL, `busy_timeout` 5000 ms.
- **`get --json`:** `{"<key>": {"<counter>": ["<id>", ...]}}`, ids in insertion order, ASCII JSON; merged read-only with every `rounds.pending-*.json` (`[{"key","counter","id"}]`, one object accepted) and an un-migrated `rounds.json`.
- **`add --json`:** stdin `[{"key","counter","id"}]`; `INSERT OR IGNORE`, then each parsable parked file is imported and deleted in the same transaction; an unparsable one is renamed `rounds.corrupt-pending-<rest>` and kept.
- **`migrate`:** imports `rounds.json` and parked files, renames it `rounds.migrated-<utc>.json`; idempotent; an unparsable `rounds.json` is refused and left in place.
- **Corrupt DB on `add`:** moved to `ledger.corrupt-<utc>.db` (its `-wal`, `-shm` beside it), a new DB records the events, one stderr line, exit 0.
- **No git, no patterns:** ledger commands need neither; a linked worktree's `add` and `migrate` are refused.

## Exit codes
| Code | When |
|---|---|
| 0 | Done |
| 1 | Refused, corrupt journal, or an error; one stderr line per problem |
| 2 | Bad arguments |
| 3 | `ledger get`: an unreadable `ledger.db`, an unparsable parked file or `rounds.json`, or any `ledger.corrupt-*.db` or `rounds.corrupt-*.json` in `.workflow/`; one stderr line |
| 75 | `ledger add` or `migrate`: `SQLITE_BUSY` past the timeout; the hook parks the events |
| 130 | Interrupted |

## Test clock
- **`RECORDS_NOW`:** test-only override of the clock (`2026-01-01T00:00:00Z`, optional `.mmm`), like `BUGS_NOW`. Never set it in a session.

Tests: `python -I .claude/skills/records/scripts/test_records.py`.

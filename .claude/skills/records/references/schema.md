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
- **Migrated date:** an `extra_round` or `stop_rule` written by `migrate` may carry `date` (`YYYY-MM-DD`, its source line's); the record line shows it instead of the event's own day.
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
- **Sources:** `COUNTER_SOURCES` in `records.py`: functions `(ctx, slug)` returning extra-round and stop-rule events beside the journal's; each adds to the cap and the record. Empty: the journal is the only source.
- **Not a source:** `decisions.csv`. Its `extra-round` and `stop-rule` rows are the readable copy `feature extra-round` and `feature stop-rule` append; a hand-written row changes no cap.
- **Used:** file-only rounds here; the hook adds the ledger's count.
- **`--with-ledger`:** adds `"ledger"`, exactly what `ledger get --json` prints, and exits 3 or 75 as `ledger get` does: `round-cap.ps1`'s dispatch starts one Python, not two.
- **Hook budget:** `feature counters` and `ledger get` run no git and wait 2000 ms at most on a lock (`READ_BUSY_MS`; every other command 10 s on `records.db`), then exit 1 or 75; `round-cap.ps1` shares 8 s across its calls of one run, 8 s for `ledger add`, inside the 15 s hook timeout.

## Stats (`stats`)
- **Line:** `Records: backlog <n> open · framework backlog <n> open · debt <n> open · features <n> open`.
- **`stats --json`:** `{"line": "<that line>", "open_features": [{"slug", "cp", "next_step"}]}`, slugs sorted, ASCII JSON: what `session-start.ps1` prints.

## Feature CSV tables (`records.py csv`)
| Table | File | Columns |
|---|---|---|
| `log` | `.workflow/features/<slug>/log.csv` | `id, agent, lane, changed, verified, attempts, limitations` |
| `tests` | `.workflow/features/<slug>/tests.csv` | `id, criterion, test_id, mode, owner, last_result` |
| `decisions` | `.workflow/features/<slug>/decisions.csv` | `id, date, kind, decision, cost` |
| `limitations` | `.workflow/features/<slug>/limitations.csv` | `id, date, text, accepted_by, mirrored` |
| `debt` | `<feature_root>/DEBT.csv` | `id, date, kind, text, source, accepted_by, next_step, state` |
| `notes` | `<feature_root>/NOTES.csv` | `id, date, topic, text, anchor, state` |

| Column | Rule |
|---|---|
| `id` | `<prefix>-###` (`L`, `T`, `D`, `LIM`, `DEBT`, `N`), assigned as the file's highest + 1, never given, never updated |
| required | `log.agent`, `tests.criterion`, `decisions.kind` (default `decision`) and `.decision`, `limitations.text`, `debt.kind` and `.text`, `notes.text` |
| `date` | `YYYY-MM-DD`, a real date; `add` fills today (UTC) when absent; a migrated row may hold none |
| `decisions.kind` | `decision` · `extra-round` · `stop-rule` · `waiver` · `accepted-gap`; `extra-round` and `stop-rule` are refused on `add` and `update` |
| `debt.kind`, `debt.state` | `workaround` · `limitation` · `accepted-gap`; `Open` (default) · `Paid` |
| `debt.source` | Optional: `BUG-####`, a feature slug, or `framework` |
| `notes.state` | `Open` (default) · `Debt` · `Promoted:<doc>` |
| `limitations.mirrored` | Set only by `csv mirror` (the `DEBT.csv` id) or `migrate` (`pre-migration` on a closed feature) |
| every value | One line, 1000 chars; control characters, Vietnamese diacritics and secret shapes refused, PII redacted; fail closed without `mem.py` or its patterns |

- **File:** a header row, UTF-8 with no BOM, LF, RFC 4180 quoting by Python `csv`; written to a temp file beside it, then `os.replace`. A header-only file is never written.
- **Feature:** `log`, `tests`, `decisions`, `limitations` need a registry row or `.workflow/features/<slug>.md`; `debt` and `notes` need the registry's `feature_root`, a folder inside the project root.
- **Writes:** refused from a linked worktree, and on a file with a blocking problem; `update` on a duplicated id is refused, `add` is not.
- **Feature commands:** `feature extra-round` appends `kind extra-round`, decision `<counter> +<n>: <note>`; `feature stop-rule` appends `kind stop-rule`, decision `<counter> root-caused · extra dispatch: <v>`. The row is staged before the journal write and moved in after it; if that move fails the journal stands and the refusal names `csv add decisions`.

### `csv doctor`
| Problem | Kind | `--fix` |
|---|---|---|
| Header not the table's columns, wrong value count, a line break in a value, a bad id, not UTF-8 | blocking | Reported for a hand fix; the row is written back unchanged |
| Duplicate id (a union merge of two branches) | duplicate | Later rows renumbered past the high water |
| BOM, CRLF, blank line, a repeated header row, a header-only or empty file | repairable | Normalized; a file with no rows is deleted |
| A value a write would refuse, redact or trim | value | Reported for a hand fix |

- **Exit:** 1 while any problem is left, one stderr line each; values are never echoed.

## Mirrors
- **`csv mirror --feature <slug>`:** each `limitations.csv` row with `mirrored` empty becomes a `DEBT.csv` row (`kind accepted-gap`, `source` the slug, its date and `accepted_by`), and `mirrored` takes the new id. A `DEBT.csv` row with the same source and text is reused, so a run cut short never copies twice.
- **Bug mirror:** `bugs.py set-status` into `Won't fix` or `Accepted` calls `mirror_bug` after the move commits. The bug's `feature` is a registry slug with a `feature_root` → a `DEBT.csv` row (`kind accepted-gap`, `source` the bug id, `text` its title, `accepted_by` the move's `--by`, `next_step` its note, the move's date); otherwise a `debt` record with the same values.
- **Once per bug:** a row or record whose `source` is the bug id already exists → nothing is added.
- **Failure:** `bugs.py` exits 1 with `bugs: moved, but the debt mirror failed: <cause>; run "<python>" -I "<records.py>" --root "<root>" bug-mirror BUG-####`. `bug-mirror` reads the bug, its last move into that status, and mirrors it; a bug in another status is refused.

## Migration (`migrate --from-md [--dry-run]`)
| Source | Target |
|---|---|
| `.workflow/framework-backlog.md`: the `\| Item \| State \|` table before the first `##` and the one under `## Deferred and recorded` | `fwbacklog` in file order; `Done: <ref>` → `Done` + ref, `Recorded: <x>` → `Recorded` + ref, `Recorded (GD decision)` → `Recorded (main GD decision)` |
| `.workflow/backlog.md` (the `/plan-game` table) | `backlog` with its own numbers; refused when `backlog.jsonl` holds records |
| `.workflow/DEBT.md` bullets | `debt`: source a leading `BUG-####:`, `<slug> (...):` or `<slug>:`, else `framework`; ` Next: ` → `next_step`; the first date or today; `accepted_by main GD` |
| `.workflow/features/<slug>.md` header (`- Status:` … `- Worktrees:`) | the registry; `Rounds` used counts → `round` events |
| `## Main GD decisions` and `## GD decisions` bullets | `decisions.csv`; a leading date → `date`; an `extra round: <counter> +<n>` phrase → kind `extra-round` and an `extra_round` event per phrase |
| `- Stop rule:` lines, any section | `decisions.csv` kind `stop-rule`, and a `stop_rule` event per counter word in the line (`extra dispatch:` value, its date) |
| `## Log`, `## Tests` tables | `log.csv`, `tests.csv`, columns by header; `#` dropped; blank lines between row groups stay in the table |
| `## Known limitations` bullets | `limitations.csv`, `accepted_by main GD`, `mirrored` empty (open feature) or `pre-migration` |
| `<feature_root>/DEBT.md`, `NOTES.md` bullets | `DEBT.csv` (a leading `Workaround:`, `Limitation:` or `Accepted gap:` sets the kind, default `limitation`), `NOTES.csv` (a leading `**topic**`) |
| `.workflow/rounds.json` | `ledger migrate` |

- **Until migrated:** `round-cap.ps1` reads a feature the registry does not hold from its md: `- Status: Open`, `- Size:`, `- Rounds: review n/cap, QA n/cap, rework n/cap`, `## Main GD decisions` (and `## GD decisions`) bullets with `extra round: <counter> +<n>`, and `- Stop rule:` lines.
- **Feature md rewrite:** the header lines become `- State: records.py feature show <slug>`; each migrated section keeps its heading, gets `- Rows: records.py csv render <table> --feature <slug>`, and keeps its unmigrated lines; every other section, `## Bugs` included, stays as it was; line ends and BOM kept. A file holding the State line is skipped.
- **Renamed:** the other sources become `<name>.migrated-<utc>.md`; `rounds.json` becomes `rounds.migrated-<utc>.json`. Other sections of `framework-backlog.md` stay in the renamed file.
- **Staging:** every write lands in a temp folder through the root's rules; the cache there is thrown away.
- **Verification:** each target's `render` is parsed back and must hold every source row's cleaned values; the registry record must equal the header; for an open feature, `feature counters` (used, cap, stopped) must equal what `round-cap.ps1` read from the md.
- **All or nothing:** a refused line is collected and the next one read; any refusal or mismatch exits 1 with `migrate refused, nothing was changed:` and every line (`<file>:<line>: <cause>`, 50 at most), and the root is untouched.
- **Swap:** the ledger first (busy → refused, root unchanged), then each staged file written beside its target and moved in, then the renames. A failure there exits 1 with `migrate failed during the swap:` naming what changed.
- **Dry run:** stages, verifies, prints the per-source counts and `dry run: nothing written`.
- **Worktree:** a write run from a linked worktree is refused; a dry run is not.

## Ledger (`.workflow/ledger.db`, local, gitignored, not journaled)
- **Table:** `round_event(key, counter, event_id, ts, UNIQUE(key, counter, event_id))`, WAL, `busy_timeout` 5000 ms (the reads of `get` and `--with-ledger`: 2000 ms).
- **Event:** `key`, `counter`, `id` each one-line text of 1 to 300 chars; each event is checked on its own, so a refused one never refuses its batch or its file.
- **Keys:** `feature:<slug>`, `bug:BUG-####`, `session:<id>`, `target:<the Target line, / separators, lower-cased>`; a target key over 280 chars is `target:<its first 200 chars>#<first 16 hex of the SHA-256 of the whole lower-cased line, UTF-8>`.
- **`get --json`:** `{"<key>": {"<counter>": ["<id>", ...]}}`, ids in insertion order, ASCII JSON; merged read-only with every `rounds.pending-*.json` (`[{"key","counter","id"}]`, one object accepted) and an un-migrated `rounds.json`; a refused event there is left out, with one stderr line.
- **`add --json`:** stdin `[{"key","counter","id"}]`; `INSERT OR IGNORE` of the valid events, then each parsable parked file's valid events are imported and the file deleted in the same transaction; an unparsable one is renamed `rounds.corrupt-pending-<rest>` and kept.
- **Refused events:** from stdin, parked files or `rounds.json`, kept after the commit in one `rounds.rejected-<utc>-<8 hex>.json` (the items as given), named on one stderr line, never counted; it blocks no command and no dispatch. Refused on stdin → exit 4, the rest recorded.
- **`migrate`:** imports `rounds.json` and parked files, renames it `rounds.migrated-<utc>.json`; idempotent; an unparsable `rounds.json` is refused and left in place; `migrate --from-md` refuses a `rounds.json` holding a refused event.
- **Corrupt DB on `add`:** moved to `ledger.corrupt-<utc>.db` (its `-wal`, `-shm` beside it), a new DB records the events, one stderr line, exit 0.
- **No git, no patterns:** ledger commands need neither; a linked worktree's `add` and `migrate` are refused.

## Exit codes
| Code | When |
|---|---|
| 0 | Done |
| 1 | Refused, corrupt journal, a broken CSV file, a refused or unverified migration, or an error; one stderr line per problem |
| 2 | Bad arguments |
| 3 | `ledger get` (and `feature counters --with-ledger`): an unreadable `ledger.db`, an unparsable parked file or `rounds.json`, or any `ledger.corrupt-*.db` or `rounds.corrupt-*.json` in `.workflow/`; one stderr line |
| 4 | `ledger add`: a stdin event refused; the valid ones are recorded, the refused ones kept in `rounds.rejected-*.json` |
| 75 | `ledger add` or `migrate`: `SQLITE_BUSY` past the timeout; the hook parks the events |
| 130 | Interrupted |

## Test clock
- **`RECORDS_NOW`:** test-only override of the clock (`2026-01-01T00:00:00Z`, optional `.mmm`), like `BUGS_NOW`. Never set it in a session.

Tests: `python -I .claude/skills/records/scripts/test_records.py`; the bug mirror's are in `test_bugs.py` (`TestDebtMirror`).

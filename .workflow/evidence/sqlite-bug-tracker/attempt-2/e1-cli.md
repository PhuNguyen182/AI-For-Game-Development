# E1 - CLI black-box re-run (sqlite-bug-tracker, attempt 2)

- Executor: E1, independent of the authors. Revision `349542e`, extracted with `git archive` into temp repos. No result carries over from attempt 1; every table here comes from a run at this commit.
- Environment: Windows 11, Python 3.14.7 (`python3 -I`), SQLite 3.50.4, git 2.56.0. Driver: Python `subprocess`, stdin as UTF-8 bytes.
- Oracle: spec, `bugs/SKILL.md`, `schema.md`, `fix`, `bug-lifecycle`, and the GD decisions on record. `test_bugs.py` was run, not read. `bugs.py` was read only by grep for message and handler lines, after the runs, to fill in `Location`.
- Harness: scripts in the scratchpad (`c1_matrix.py`, `c1_crud.py`, `c_def.py`, `c_new.py`, `c2.py`, `c3.py`, `c4.py`, `c5.py`, `c67.py`, `c11.py`). Removed with the temp repos as briefed. The matrix rule is inline in attempt 1's report and unchanged. Raw logs are not kept.

## Summary
| Result | Count |
|---|---|
| DEF-E1-01 to 08 | **8 of 8 closed** on their original repro |
| New defects | 3: 0 Critical, 0 High, 2 Medium, 1 Low. All need a doctored `mem.py` or a `--`-prefixed secret |
| Status attempts | 363 (121 pairs x 3 attributions), **0 mismatches** |
| C0 | `Ran 274 tests in 98.928s`, `OK`, exit 0, 0 lines containing "warn" |
| Exact 90 days | Proved on the injected clock: kept at 90d, purged at 90d + 1 ms |

| Criterion | Result | Note |
|---|---|---|
| Baseline | Pass | 274 tests OK |
| 1 CRUD | Pass | |
| 2 Status | Pass | 0 mismatches |
| 3 Priority | Pass | |
| 4 Purge | Pass | DEF-E1-03 closed |
| 5 Git and rebuild | Pass | Every decision-table row, both `autocrlf` values |
| 6 Content rules | **Pass on the shipped `mem.py` and pattern file, with findings under fault injection** | DEF-E1-09, 10, 11 |
| 9 Migration, pre-merge half | Pass | Signed only with C15 |
| C6, C7, C14 | Pass | C14 is static, not a 3.10 run |

## DEF-E1-01 to 08: verdicts
| ID | Verdict | Original repro at `349542e` | Output |
|---|---|---|---|
| DEF-E1-01 secret echoed on stderr | **Closed** | 25 shapes x 4 forms (`show`, `--duplicate-of`, status, JSON key) | 100 attempts, 0 leaks. `bugs: bad id '[REDACTED:private key]`, `bugs: unknown status '[REDACTED:...`, `bugs: add: unknown field: [REDACTED:...`. See DEF-E1-11 for one form outside this repro |
| DEF-E1-02 text-free writes with no patterns | **Closed** | `delete`, `purge` (real candidate), `doctor --fix` (real duplicate) in 9 broken states | 27 of 27 refused, journal unchanged, 0 tracebacks. `purge --dry-run`, `list`, `show`, `search`, `counters`, `stats`, `sql`, `rebuild` still work |
| DEF-E1-03 purged ID returns through a merge | **Closed** | Purge on main, merge a branch that filed that ID | `doctor` exit 1 `duplicate id BUG-0002 held by two bug_uids`; `counters` and 4 writes refuse, journal unchanged; `doctor --fix`: `renumbered BUG-0002 to BUG-0003`; `show BUG-0002`: `purged`; next ID BUG-0004; rebuild equal |
| DEF-E1-04 unbounded count | **Closed** | `round`, `extra-round` with `+9223372036854775808` and others | `bad count ...: expected +n with n from 1 to 100`, exit 1, no traceback, journal unchanged. `+1`, `+100` accepted, `+101` refused. Replay of `n` = 101, 0, -1, 2^63, `"1"`, 1.5, true, null: `corrupt journal: line 2: bad n` |
| DEF-E1-05 padded `--by GD` | **Closed** | `"GD "`, `" GD"`, tab and NBSP forms on `set-status` | `by: must be exactly GD, with no padding`, on `add`, `update`, `set-status`, `round`, `extra-round`, `stop-rule`. `delete`: `delete is GD only`. `--by GD`: `Request -> Backlog` |
| DEF-E1-06 count with no `+` | **Closed** | `round <id> fix 1`, `extra-round <id> fix 1` | `bad count '1': expected +n with n from 1 to 100`, exit 1. `+1`: `fix 1/2` |
| DEF-E1-07 Backlog match text | **Closed** | Follow the text on a Backlog bug | `SKILL.md:30`, `fix/SKILL.md:18`, `bug-lifecycle.md:6` now say a Backlog match takes evidence with `update`. `update` with a note: `updated: note`, stays Backlog. `Backlog -> Reopen` still refused, as the text states |
| DEF-E1-08 note written as optional | **Closed** | Read the form, run it | `SKILL.md:40`: `set-status <id> "<status>" --note N ...; stdin {"note": ...} can replace --note`. No note: `note: required`, exit 1. Stdin and `--note`: exit 0 |

Broken states for DEF-E1-02: pattern file missing, comments only, bad regex, line with no tab; `mem.py` missing, raising, syntax error, failed import, `sys.exit(3)` at import. The first eight give a `write refused` or `is missing` message; the last exits 3 with an empty stderr (DEF-E1-10).

## GD decisions on record, not findings
| Decision | Observed |
|---|---|
| QA or main session may settle a Backlog bug without GD | `Backlog -> As designed --by "QA executor"` and `Backlog -> Duplicate` with no `--by`: exit 0. `Won't fix`, `Accepted` still GD only |
| Purge clock counts from the last terminal status reached | Merge of Complete (day 1) and Accepted (day 50), in both branch orders: Accepted, `closed_at` day 50. Day 92: purged 0. Day 50 + 90d + 1 ms: purged 1 |
| At the cap allows, past the cap blocks | Hook behaviour, not run here (E2). The CLI itself does not block: three `round +100` give `used` 300 against cap 2 |

## New behaviour
### Empty journal
| Check | Result |
|---|---|
| `list`, `list --json`, `search`, `stats`, `sql`, `counters`, `show` | `no bugs`, `[]`, `no matches`, `Bugs: 0 open (0 High+)`, count 0, `found:false`, `BUG-0001 not found` |
| `rebuild`, `doctor`, `doctor --fix`, `purge`, `purge --dry-run`, `purge --auto` | Exit 0; `doctor: clean`, `purged 0`, `would purge 0`. File stays 0 bytes; `git status` clean |
| First write | `BUG-0001`, 1 line, newline at the end |
| `import-md` beside it, on the real `bugs.md` | `list` refuses first; import exit 0, 5 bugs, 15 events; after the file is removed, 5 Complete, next ID BUG-0006 |
| 12 parallel `add` on it, 3 runs | 12 OK, 12 unique, 12 valid lines |
| Newline-only, CRLF-only, spaces-only | Read empty, doctor clean, first write BUG-0001 |

### `doctor` on a defeated `merge=union` or an ignored journal
| Setup | `doctor` | Text |
|---|---|---|
| As shipped | 0 | `doctor: clean` |
| Line removed, `!merge` | 1 | `merge resolves to unspecified, not union: merges can conflict` |
| `merge=binary`, `merge=ours` | 1 | `merge resolves to binary`, `to ours` |
| `-merge`, later `*.jsonl -merge`, later `binary` | 1 | `merge resolves to unset` |
| `.workflow/.gitattributes` override, `.git/info/attributes` override | 1 | `merge resolves to binary` |
| Line removed, no journal yet | 1 | As above |
| `*.jsonl merge=union` only | 0 | Git resolves union: correct |
| `merge=union` kept, `text eol=lf` lost | 0 | `schema.md` names `merge` and ignore only (A2) |
| `*.jsonl` ignored and untracked; `.workflow/` ignored; `info/exclude` | 1 | `journal ignored by git: .workflow/bugs.jsonl must stay tracked` |
| Ignored, no journal yet | 1 | As above |
| Ignore rule, still tracked; ignore rule then a negation | 0 | Git does not ignore it: correct |
| Real merge with `merge=binary` | Merge exit 1 `Cannot merge binary files`; `doctor` exit 1 | The warning matches what git did |

`doctor --fix` also exits 1 in each failing row, `list` still works, 0 tracebacks.

### `mem.py` that loads but faults
20 faults x 21 forms: 420 attempts. Forms: 8 refusals (ID, status, `--duplicate-of`, JSON key, email, bad JSON, argparse choice, `sql`), 8 text writes (secret, email, phone, IP, device id), `add` clean, `delete`, `purge`, `doctor --fix`, `list`.

| Fault | Traceback | Raw value | Behaviour |
|---|---|---|---|
| `redact` raises (also with the value in its message), returns None, returns int, recurses | 0 | 0 | Refusals show `<hidden: secret patterns unavailable>`. Secret writes refused, PII writes redacted (`redact_pii` is intact) |
| `redact_pii` raises (also with the value), returns None, returns int | 0 | 0 | Every text write refused: `write refused: title cannot be checked for secrets and PII (RuntimeError)`. Type only, no message. `delete` still writes (A3) |
| Both raise | 0 | 0 | As above |
| `redact`, `redact_pii`, `load_secret_patterns` deleted; `load_secret_patterns` raises | 0 | 0 | Every write refused, `delete`, `purge`, `doctor --fix` included |
| `load_secret_patterns` returns junk | 0 | 0 | Text writes refused |
| Prints at import | 0 | 0 | Normal |
| **`load_secret_patterns` returns `[]`** | 0 | **9 of 21** | **DEF-E1-09** |
| **`BaseException` in `redact`** | **11 of 21** | **11 of 21 forms show it, 7 with the value** | **DEF-E1-10** |
| **`SystemExit(0)` in `redact` or `redact_pii`** | 0 | 0 | **Exit 0, no output, nothing written: DEF-E1-10** |

### Echo paths with a healthy `mem.py`
25 shapes plus 4 PII values, 27 forms: 783 attempts, 3 leaks (DEF-E1-11). Forms add to DEF-E1-01's: `counters`, `update`, `round`, `delete` IDs, `round` counter and count, `--extra-dispatch`, `update` and `set-status` keys, priority value, `list --status`, `--priority`, `search -n`, unknown subcommand, unknown flag, `--root`, `sql` column, table and gate, bad JSON, `BUGS_NOW`. Sample: `bad arguments: argument -n: invalid int value: '[REDACTED:private key]`.
- Long values: an ID of 40 chars prints, 41 prints `<41 chars>`; status and key alike; `sql refused: <316 chars>`; `root <365 chars> is not a directory`; a 400-char argparse value: 296-char stderr.
- Hand-edited journal lines (`event_uid`, `bug_uid`, key, type, `ts`, counter, status, priority), secret and email: 16 rows, 0 leaks, 0 tracebacks.
- `import-md` cells (severity, status, duplicate cell, History word and date), secret, email, JWT: 15 rows, 0 leaks, nothing written.
- A closed stdout pipe on `list --json`: exit 120, `Exception ignored while flushing sys.stdout`, no traceback (A5).

## Criterion 1 - CRUD
| Command | Exit | Output |
|---|---|---|
| `add` | 0 | `BUG-0001` |
| `show`, `show --json` | 0 | Full record; JSON keys are the spec's `bug` columns plus `events` |
| `list`, `--open`, `--status`, `--priority`, `--feature`, `search`, `counters`, `stats` | 0 | Expected row; `Bugs: 1 open (1 High+)` |
| `update` note, fields, `{}` | 0 | `updated: note`, `updated: evidence, root_cause`, `no change` |
| `update` of `status`, `closed_at` | 1 | `update: unknown or read-only field: status (status moves through set-status)` |
| `delete`, `--by QA`, `--by gd` | 1 | `delete is GD only: pass --by GD on the GD's order`; journal unchanged |
| `delete --by GD` | 0 | `deleted BUG-0002, journal uncommitted`; title gone from the journal |
| After delete: `show`, `update`, `delete` | 0, 1, 1 | `BUG-0002 purged`, `BUG-0002 was purged` |
| `show BUG-99999`, `garbage`, `bug-0001`, `BUG-1` | 1 | `not found`, `bad id ...: expected BUG-####` |

## Criterion 2 - Status matrix (`c1_matrix.py`)
| Count | Value |
|---|---|
| Attempts, pairs | 363, 121 (43 legal, 78 illegal) |
| Mismatches (outcome, status, journal delta, `closed_at`, traceback) | 0 |
| Legal outcomes, refused | 93, 270 |
| Any-attribution pairs (25) | 75 of 75 legal |
| GD-only pairs (18) | `--by GD` 18 of 18 legal; none and QA 36 of 36 refused |
| Illegal pairs (78) | 234 of 234 refused |

Refusal text read: Request -> Complete, Resolved -> Complete, Complete -> Processing, Backlog -> Processing, Processing -> Review, Complete -> Request, Won't fix -> Request, Complete -> Backlog, Backlog -> Reopen, Resolved -> Reopen, Backlog -> Backlog: `BUG-x: <from> -> <to> is not in the state machine (references/schema.md)`. Request -> Backlog, Backlog -> Request, Review -> Won't fix, Reopen -> Accepted, no GD: `... is GD only (state machine in references/schema.md): pass --by GD on the GD's order`.

`duplicate_of`: missing or empty `required for Duplicate`; `BUG-9999 not found`; self `a bug cannot duplicate itself`; malformed `bad id`; on another move `only with status Duplicate`. Note: required on every `set-status`. Old status names and wrong case: `unknown status`.

## Criterion 3 - Priority (C2)
| Value | Result | Text |
|---|---|---|
| Low, Medium, High, Highest | Accepted on `add` and `update`, stored exactly | |
| `high`, `HIGH`, `Critical`, `Severity`, `Medium `, ` Medium`, spaces, `1`, `true`, `["High"]` | Refused | `priority: must be one of Low, Medium, High, Highest (Critical maps to Highest)` |
| Empty, null, missing | Refused | `priority: required, one of Low, Medium, High, Highest` |
| `Severity`, `severity` as a field | Refused | `add: unknown field: Severity (status starts at Request; bugs have a priority, no severity)` |
| `sql "SELECT severity FROM bug"` | Refused | `no such column: severity` |

38 rows, 0 mismatches, journal and DB unchanged on each refusal.

## Criterion 4 - Purge (C4)
`BUGS_NOW`, margin 0, spread 0 (injected clock, one deterministic run per row). `closed_at` 2026-01-01T00:00:00.004Z.
| Offset | `--dry-run` | `purge` | Tombstones | `show` |
|---|---|---|---|---|
| 89d | would purge 0 | purged 0 | 0 | record |
| 90d - 1 s | would purge 0 | purged 0 | 0 | record |
| 90d - 1 ms | would purge 0 | purged 0 | 0 | record |
| **90d exact** | would purge 0 | purged 0 | 0 | record |
| 90d + 1 ms | would purge 1 | purged 1, journal uncommitted | 1 | `purged` |
| 90d + 1 s | would purge 1 | purged 1 | 1 | `purged` |
| 91d | would purge 1 | purged 1 | 1 | `purged` |

| Case | Result |
|---|---|
| 400d: the 6 open statuses | All kept |
| 400d: the 5 terminal statuses | `purged 5`; title text gone |
| Tombstone | Keys `bug_uid, data, event_uid, ts, type`; `data` `{"id": N}`; no note or `by` |
| Dry run | Journal, DB state and DB bytes unchanged |
| Reopen | `closed_at` null. Closed again at day 50: first + 91d purged 0; second + 90d purged 0; + 1 ms purged 1 |
| Reopened, left open, 400d | purged 0 |
| `update` on a terminal bug | `closed_at` unchanged, purged at day 91 |
| Direct Complete -> Accepted, `--by GD` | Refused, `closed_at` unchanged |
| Complete -> Reopen -> Accepted | `closed_at` moves to the later date |
| Highest ID purged, add | BUG-0004 |
| Middle ID read, never-created ID | `BUG-0002 purged` exit 0, `BUG-0099 not found` exit 1 |
| Purged ID: `counters`, `--json`, `update`, `set-status` | `found:false`; `{"id":..., "purged": true}`; `was purged` |
| DB deleted after purge, add | BUG-0005 |
| Sole bug purged | 1 line, next BUG-0002 |
| Clock backwards; 35 writes | `ts` still rises 1 ms; strictly increasing |
| Bad `BUGS_NOW` (4 forms) | Exit 1, no traceback, journal unchanged |

## Criterion 5 - Git and decision table (C5)
Real git, `merge=union`, `core.autocrlf` false and true. The two runs differ only in the row order of one duplicate pair (random uid). Journal LF, no BOM, newline at the end on both. Rebuild = delete `bugs.db*`, `rebuild`, compare all `bug` columns, `bug_event` rows and the `list --json` hash: equal in all 14 scenario comparisons on each value. Hashes differ per run because uids are random.

| Scenario | Git commands | DB before | DB after | Rebuild: rows, `list` sha (false / true) |
|---|---|---|---|---|
| Both branches file (same ID) | `merge B` | 3 bugs | Both survive, warning; `doctor --fix` gives 5 distinct IDs | 5 bugs, 7 events, `06b7d95d661e` / `66d016921892` |
| Both run `doctor --fix`, merge | `merge X` | 3 and 4 | 4 distinct IDs, doctor clean | 4 bugs, 6 events, `47d2e1d47d54` / `6e8e0168783f` |
| Both touch one bug | `merge B` | Request, plus a note | Processing, 3 events | 2 bugs, 4 events, `fa1f277d4500` / `288e18180442` |
| Switch | `switch main`, `switch F` | F: 2, Processing | main: 1, Request; F: 2, Processing | 2 bugs, 3 events, `68f3dee2fc49` / `1ce4e891894a` |
| Pull, then divergent pull | `clone`, `pull --no-rebase` | 1, then 3 each | 2; collision, `doctor --fix`, 4 | 4 bugs, 5 events, `4e9d2b5836bc` / `4d73f7eb2274` |
| `pull --rebase` | `pull --rebase origin main` | 4 | Exit 0; collision, `doctor --fix`, 6 | 6 bugs, 8 events, `53efb7fd75e5` / `d35dac6586c5` |
| Rebase | `rebase main` | R: 2 | Exit 0, `git status` clean; collision, `doctor --fix`, 3 | 3 bugs, 5 events, `ab52b5f96f40` / `50980bbe2311` |
| Cherry-pick | `cherry-pick <sha>` | 2 | Collision, `doctor --fix`, 3 | 3 bugs, 4 events, `35e933ff6796` / `c315bc580c32` |
| Revert | `revert <sha>` | 3 | Exit 1 (cause not examined); journal reads, bug still listed, doctor clean, next ID BUG-0004 | Not compared |
| Purge, pre-purge B untouched | `purge`, `merge B` | 2 | 1, `purged`, text gone | 1 bug, 1 event, `2de175e37d08` / `6da06821d756` |
| Purge, B updated the bug | as above | 2 | Stays gone; inert lines back; `doctor` exit 1; `doctor --fix` removes them | 1 bug, 1 event, `9c2239339bce` / `d8601e19537a` |
| As above, B also files | as above | 2 | B's bug kept, next ID continues | 2 bugs, 2 events, `17453990c498` / `105fce2d5683` |
| Torn partial tail | Fixture | 2 | Reads OK; `doctor` exit 1 `torn final line`; next write removes it | 2 bugs, 3 events, `dec2981e0ba7` / `4ea8febf4f97` |
| Whole final event, no newline | Fixture | 2 | Kept; next write adds the newline | 2 bugs, 3 events, `b6cda6729e7c` / `e24a9a1057b5` |
| Crash: old DB restored | Fixture | Stale | Next read and next write heal, state equal | 1 bug, 4 events, `94735497c24e` / `7a60bc605801` |

| Decision row | Expected | Actual | Match |
|---|---|---|---|
| Journal newer than DB | Rebuild on next command | Switch, pull, merge, rebase, cherry-pick refreshed | Yes |
| Appended, DB not committed | Next command heals | Healed. 29 kills in 40 `add` tries: 0 inconsistent, doctor clean | Yes |
| Torn final line | Repaired or refused, never silently dropped mid-file | Tail repaired. Malformed mid-file: 10 commands refuse, `corrupt journal: line 2: JSONDecodeError`, journal unchanged | Yes |
| Torn committed, union merge | Same | On theirs: stays final, repaired. On ours: `line 2`, every command refuses. Whole event, no newline, on ours: merged cleanly, duplicate reported | Yes |
| Same `event_uid` twice | Deduped | State equal | Yes |
| Shuffled | Identical | 5 seeds and reversed: equal | Yes |
| Two `bug_uid`s on one ID | Fail closed until `doctor --fix` | `counters`, `update`, `set-status`, `round`, `extra-round`, `stop-rule`, `delete`: `duplicate id BUG-0002 held by 2 bug_uids: run doctor --fix`, journal unchanged. Other ID writes. `add` works. Later create renumbered | Yes |
| Tombstone plus resurrected create | Stays gone | `purged`, `list` empty, `doctor --fix` sweeps | Yes |
| `bugs.md` present | Every command refuses | 19 forms, `.workflow/bugs.md exists: run import-md, delete the file, then retry`, journal unchanged | Yes |
| Linked worktree | Read OK, write refused | No `--root` and `--root <worktree>`: reads see the main checkout; `add`, `update`, `set-status`, `round`, `extra-round`, `stop-rule`, `delete`, `purge`, `doctor --fix`, `import-md`: `writes from a linked worktree are refused`, main journal unchanged, no DB in the worktree. `purge --auto`: `purge skipped: linked worktree` | Yes (A4) |

Other: later lines attach by `bug_uid` after a renumber. Corrupt, zero-byte and header-only `bugs.db` heal. Both branches purge one bug: 2 tombstones, stays gone. Renumber into an ID another branch filed: duplicate reported, second `doctor --fix` resolves it, rebuild equal. Settle against reopen on two branches: last `ts` wins, `closed_at` follows. BOM, unknown type, missing `ts`, non-object, orphan update, conflict markers, invalid UTF-8, bad status, bad priority: every command refuses. CRLF, blank line, empty: read fine. `bugs.db` shows as ignored.

| Kill test | Tries | Killed | Finished | Bad |
|---|---|---|---|---|
| `purge`, 1000-bug fixture (0.27 s uninterrupted) | 25 | 9 | 16 | 0: valid journal, 200 open, a second purge ends at 800 tombstones |
| `doctor --fix` sweep, 700-bug fixture | 20 | 17 | 3 | 0: valid journal, 100 listed, doctor clean after a second `--fix` |

Leftover seen after a kill: `bugs.db-journal`. `git check-ignore` confirms `.workflow/bugs.db*` also covers `bugs.db.jsonl.tmp`.

## Criterion 6 - Content rules (C2, C3)
| Set | Rows | Mismatches |
|---|---|---|
| Field limits: 10 fields at L-1, L, L+1, L and L+1 in em dash and emoji, empty, spaces, on `add` and `update` | 180 | 0. All 84 refused rows left journal and DB unchanged. `title: 101 chars, limit 100` |
| Missing key on `add` | 10 | 0. Required: `title: required`. `repro` `not yet` accepted |
| Note: `add`, `update`, `set-status` (arg, stdin), `round` (arg, stdin), `extra-round`, `stop-rule` | 64 | 0 |
| `--by` on 6 commands: L-1, L, L+1, LF, empty, spaces | 36 | 0 |
| One-line: 14 characters x 10 fields | 140 | 0. LF, CR, CRLF refused in the 5 one-line fields, accepted in the 5 others. U+2028, U+2029, U+0085, VT, FF, NUL, ESC, DEL refused in all. TAB, U+202E, U+200B accepted in all (A1) |
| Specials: `$`, backtick, quotes, braces, `%s`, backslash, SQL text, pipe, tags, emoji | 100 | 90 of 90 round trip in DB and journal; ` padded ` trimmed in 10 fields |
| Stdin shapes | 31 | 0 tracebacks. Bad shapes refused, journal unchanged. UTF-8 BOM, duplicate keys, surrogate pair, null on an optional field accepted |
| `add` with `status`, `id`, `uid`, `closed_at`, `created_at`, `fix_cap`, `bogus`, `duplicate_of` | 8 | All refused |
| Stored-text limit | 5 | 119 raw, 100 stored: accepted. 120 raw, 101 stored: refused. 100 raw, 110 stored: refused. Note 219 accepted, 220 refused. No raw value in the message |

| Diacritics | Result |
|---|---|
| 134 Vietnamese letters, NFC and NFD, in `title` | 268 of 268 refused |
| 9 samples in 35 forms: every text field on `add`, `update`, notes, `--by` on 7 commands, `--duplicate-of` | 315 of 315 refused, journal and DB unchanged |
| Reversed marks, U+0341, dot and horn in either order | Refused |
| e-acute (both forms), a-grave, o-circumflex, e-grave | Refused: `title: Vietnamese diacritics ('\xe9'): the database is English only, translate first` |
| u-umlaut, n-tilde, c-cedilla, sharp s, eth, a-ring, Cyrillic, CJK, em dash, emoji, `x` plus a combining mark | Accepted |

| Secrets | Result |
|---|---|
| 25 shapes covering every line of `secret-patterns.txt`, 37 forms: 925 attempts | 0 accepted, 0 journal changes, 0 tracebacks, **0 leaks** to journal, `bugs.db*`, stdout, stderr or `list` |
| Text fields | `refused: secret-shaped value in title (AWS access key)` |
| Clean `add` after each shape | 25 of 25 OK |

PII: 126 rows, 0 misses: 7 values in 10 fields on `add`, plus `update`, notes on 6 commands, `--by`. `[REDACTED:email]`, `:phone`, `:ip`, `:device id` stored; raw value absent from journal, DB and output; stderr `redacted PII in: title`. Not redacted: `package@1.2.3`, `127.0.0.1`, `1.2.3`, an unlabelled uuid.

`import-md`: limits at L accepted and L+1 refused for title, expected, repro, evidence, root_cause, description (280), note (200); table cells feature and regression_test. Diacritics and secrets in all 9 fields and the note: `import stopped, nothing written`. Email: redacted.

## Criterion 9, pre-merge half (C11)
`.workflow/bugs.md`, main checkout byte-identical to the tree (sha `b2afc0901c86b72a`, CRLF), full-tree temp repo. `import-md`: exit 0, `imported 5 bugs, 15 events; delete .workflow/bugs.md next`.

| ID | Priority | Status | `closed_at` | Title chars | `description` chars (= old `Actual`) | Events |
|---|---|---|---|---|---|---|
| BUG-0001 | Medium | Complete | 2026-10-29T00:00:00.002Z | 76 | 119 | 3 |
| BUG-0002 | Medium | Complete | 2026-10-29T00:00:00.002Z | 69 | 101 | 3 |
| BUG-0003 | Low | Complete | 2026-10-29T00:00:00.002Z | 70 | 55 | 3 |
| BUG-0004 | High | Complete | 2026-10-29T00:00:00.002Z | 82 | 84 | 3 |
| BUG-0005 | Medium | Complete | 2026-10-29T00:00:00.002Z | 64 | 11 | 3 |

| Check | Result |
|---|---|
| Records breaking a rule | **None; no by-hand rewrite** |
| Re-run; second directory; LF source | Byte-identical, journal sha `278dd88beffdfb34`, LF, no BOM |
| `show BUG-0004` | Holds its text and 3 events |
| Next ID, rebuild, `doctor`, `stats`, `purge --dry-run` | BUG-0006, equal, clean, `Bugs: 0 open (0 High+)`, `would purge 0` |
| `bugs.md` present, recreated | 19 forms refuse, journal unchanged |
| Severity | Critical -> Highest; High, Medium, Low by name. `Blocker`, `critical`, empty: stop |
| Status with consistent History | Open -> Request, Fixed -> Resolved, Reopened -> Reopen, Closed -> Complete, others keep names, `Duplicate of BUG-0001` -> Duplicate. `closed_at` on terminal only, last close wins |
| Stops, nothing written | Unknown target, self target, History against the table, row with no record, record with no row, bad date, empty repro, a pre-existing bug on that ID |
| `Next ID: BUG-0010` | Next add gets BUG-0010 |

## C6 - Concurrency (once)
| Round | Runs | Result |
|---|---|---|
| 12 parallel `add`, no DB or journal | 6 | 12 OK, 12 unique sequential IDs, 12 valid lines |
| 8 writers x 10, readers looping | 3 | 80 OK, 80 unique, 81 lines, 0 read errors, 49 to 67 reads, 2.9 to 5.5 s, rebuild equal |
| One transition, 8 processes | 5 | 1 OK, 7 refused, 1 line |
| 8 parallel `round +1` | 5 | 8 OK, used 8, 8 lines |
| `add`, `rebuild`, `doctor --fix`, `purge` mixed | 3 | 13 OK, 7 valid lines, rebuild equal |
| Kill during `add` | 40 | 29 killed, 11 finished, 0 bad |
| External lock 2 s, 8 s | 1 each | Writer waits, then OK |
| External lock 20 s | 1 | `add` exit 1 at 11.2 s, `bugs: database is locked`, journal unchanged; `counters` 0.2 s |

## C7 - Search and `sql` (once)
| Input | Result |
|---|---|
| 57 queries with `-`, `:`, quotes, `BUG-0001`, empty, `*`, operators, emoji, 5000 chars | 0 tracebacks: 35 hits, 5 no matches, 15 `search: no words in the query`, 2 usage |
| 55 rejected `sql` forms: writes, PRAGMA, ATTACH, VACUUM, multi-statement, `load_extension`, `WITH ... DELETE`, comment prefixes, FTS command | All exit 1, 0 tracebacks, state and journal unchanged, no stray file |
| 18 valid forms | Exit 0. BLOB `x'00ff'`. `meta`: `high_water, journal_hash, last_ts, purged_ids` |
| Infinite CTE | Exit 1 at 10.2 s, `sql refused: interrupted` |
| 1500 rows | 1000 rows, `(first 1000 rows)` |
| No journal | Reads empty, nothing created |

## C14 - Python 3.10 (static, not a 3.10 run)
`ast.parse(feature_version=(3,10))` OK on `bugs.py`, `test_bugs.py`, `mem.py`. Grep for `tomllib`, `datetime.UTC`, `Self`, `except*`, `batched`, `StrEnum`, `ExceptionGroup`, `add_note`, `TaskGroup`, `@override`, `type` statement, `file_digest`, `full_match`, `Path.walk`: 0 hits. 3.12 f-string forms: 0. FTS5 on 3.14.7's SQLite only.

## New defects
### DEF-E1-09 - An empty pattern list from `mem.py` fails open
- **Location:** `bugs.py:214` takes the list with no emptiness check; refusal path `bugs.py:1632`. Scenario: `load_secret_patterns` returns `[]`.
- **Expected:** `schema.md` "a missing or broken `mem.py` ... refuses every write"; "With nothing to scan, values are hidden". Spec Security: secret shapes refused.
- **Actual:** `add`, `update` note and `update --by` with a secret shape: exit 0, value in the journal and `bugs.db`. `show`, status, `--duplicate-of`, JSON key, argparse choice, `sql`: value on stderr. A comments-only pattern file refuses correctly, because the real loader raises; only this return value passes.
- **Evidence:** Harness result, value masked: `('load_secret_patterns returns empty', 'write: title secret', 0, ['journal', 'bugs.db'])`; `bugs: bad id '<VAL>': expected BUG-####`. 9 of 21 forms.
- **Owner:** T1 author.
- **Severity:** Medium. It needs an edit to a trusted file, and the shipped loader cannot return this. `qa-standards` lists "secret" under Critical: qa-lead may re-rate, since a value does reach the tracked journal in this state.
- **Repro:** Temp repo. Append `def load_secret_patterns(root): return []` to `mem.py`. `bugs add` with a synthetic secret shape in `title`. Read the journal. 3 of 3 write forms, 6 of 6 refusal forms holding the value, 1 run each.

### DEF-E1-10 - `BaseException` and `SystemExit` from `mem.py` pass the fail-closed handlers
- **Location:** `bugs.py:200`, `:215`, `:238`, `:1634`, all `except Exception`. Scenario: `mem.py` raises outside the `Exception` family, at import or inside `redact` or `redact_pii`.
- **Expected:** Brief and `schema.md`: a fault leaves "no traceback and no raw value on a refusal or a write"; "refuses every write ... with no traceback"; a refused write does not report success.
- **Actual:**
  - `BaseException` in `redact`: Python traceback, exit 1, in 11 forms. 7 refusal forms show the raw value on stderr through the chained refusal message. Nothing written.
  - `SystemExit(0)` in `redact` or `redact_pii`, or `sys.exit(0)` at import: `add`, `update`, `set-status` exit 0, no output, no write. `add` prints no ID, so the caller reads success. `sys.exit(0)` at import also takes `delete` and `show BUG-XX` to exit 0.
  - `sys.exit(3)` at import: exit 3, empty stderr, on writes and on a refusal.
  - The `Exception` family (RuntimeError, ValueError, OSError, TypeError, RecursionError, SyntaxError, ImportError) is clean in all 420 attempts' other rows.
- **Evidence:** `BaseException: base` at the end of stderr, `leak ['stderr']`, `tb True`. `sys.exit(0) add rc 0 out  err  journal same True`.
- **Owner:** T1 author.
- **Severity:** Medium. Contrived: the shipped `mem.py` guards its entry point and does not raise these. A Ctrl+C during redaction is the only natural trigger for the traceback, and it was not run.
- **Repro:** Append `def redact(text, patterns): raise BaseException('base')` to `mem.py`, then `bugs show <synthetic shape>`. Or write `import sys; sys.exit(0)` as `mem.py`, then `bugs add`. 11 of 11 forms; 3 of 3 writes for exit 0 at import.

### DEF-E1-11 - A `sk-` shape passed as a `--` flag is echoed by argparse
- **Location:** The argparse error path. Form: `bugs list --sk-<value>`.
- **Expected:** QA plan C3 "absent from ... stderr"; `schema.md` "secret and PII redaction always runs".
- **Actual:** `OpenAI or Anthropic key`, `OpenAI proj key`, `Anthropic key`: the whole flag prints on stderr, exit 2. The other 22 shapes and the same three in the 26 other forms redact. The pattern's lookbehind excludes a leading `-`, so with the `--` prefix the text is no longer that shape.
- **Evidence:** `LEAK ('OpenAI or Anthropic key', 'unknown flag', 2, ['stderr'], '')`, likewise the other two; 3 of 783.
- **Owner:** T1 author, or the pattern file's owner: unclear. The same lookbehind means `x-sk-<value>` in a text field is not a secret shape either; that was not run.
- **Severity:** Low. It needs a key typed as a flag, and the argument is already in the caller's command line.
- **Repro:** `bugs list --sk-<synthetic 24 chars>`. Read stderr. 3 of 3 shapes.

## Observed, not decided
| ID | Point | Observed |
|---|---|---|
| A1 | `schema.md` "control characters" | TAB, U+202E, U+200B accepted in every field. U+202E can spoof display |
| A2 | `doctor` and `text eol=lf` | `merge=union` kept with `eol=lf` lost: `doctor: clean`. `schema.md` names `merge` and ignore only; the attribute line has all three |
| A3 | `delete` when `redact_pii` faults or patterns are junk | Writes: it holds no text and never calls those functions, so the fault is not seen. `schema.md` says a broken `mem.py` refuses every write. Same family as the closed DEF-E1-02, only reachable once `mem.py` already loads |
| A4 | Script and cwd in a linked worktree, `--root <main checkout>` | Write succeeds, main journal changes. `bugs.md` in the worktree only: reads succeed. In main only: refuses from the worktree |
| A5 | Closed stdout pipe | Exit 120 and `Exception ignored while flushing sys.stdout`, on `list --json`; no traceback |
| A6 | `git` missing from PATH, `.git` present | `doctor: clean` exit 0 without checking attributes. `add` refuses: `git failed in ...`. `purge --auto`: `purge skipped: not a git repository`, which misnames the cause |
| A7 | `duplicate_of` a purged ID | Accepted |
| A8 | `+n` as a cap | 1 to 100 is per call. Repeated `extra-round +100` has no total limit; GD decision on record keeps `extra-round` free of `--by GD` |
| A9 | `sql` stdout | A value in the query's own result prints, as a read (`SELECT '<value>'` not run with a secret) |
| A10 | Revert | `git revert` of a journal commit exit 1, cause not examined; journal stayed readable |

## Not covered:
- **Python 3.10 runtime** (owner: GD, decision on record): C14 is static.
- **Real migration, criterion 9** (owner: main session, C15, with E1 re-dispatched for the comparison).
- **Hooks, including at-cap and past-cap, `Get-BugsRoot`, session-start, `purge --auto` conditions** other than a linked worktree, an empty journal and `bugs.md` (owner: E2).
- **pwsh stdin and the 5.1 `$OutputEncoding` line** (owner: E2): this run drives the CLI from Python only.
- **Full lifecycle text walk, `framework-sync.ps1`, skill text outside the four files read** (owner: E3). This run re-ran the matrix and CRUD by script, not the whole walk from text.
- **A kill proven to land between append and commit, or inside the purge rewrite** (owner: T1 author, if a seam is wanted): random kills found no fault, and heal is proved by restoring the old DB. Power loss and disk full did not run.
- **`git stash` on the journal; the cause of the revert exit** (owner: E1 on a re-dispatch).
- **Ctrl+C during a real redaction** (owner: E1 on a re-dispatch): DEF-E1-10 used an injected `BaseException`.
- **`x-sk-<value>` in a text field** (owner: T1 author or the pattern file's owner).
- **Other platforms** (owner: GD): Windows only.
- **`autocrlf` on fixture-only rows** (owner: E1 on a re-dispatch): the decision-table fixtures, kill tests and `extra` scenarios ran with it unset.

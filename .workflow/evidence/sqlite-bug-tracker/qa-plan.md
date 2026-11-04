# QA plan - sqlite-bug-tracker (qa-lead, Plan mode, copied from its return)

- Size: L, no risk flag, full depth. Evidence revision: worktree `.claude/worktrees/sqlite-bug-tracker` at `b6deca7`, tree clean. Any later code change re-runs the affected cases (no reuse of old results).
- Executors: `general-purpose` with a shell, three dispatches. Nothing touches the Editor, so the three may run in parallel in temp repos under the OS temp dir and the scratchpad. None may be the T1, T2 or T3 author.
  - E1: CLI black-box.
  - E2: PowerShell and hooks.
  - E3: docs contract and sync.
- Oracle rule: E1, E2 and E3 derive expected values from the spec (`.workflow/features/sqlite-bug-tracker.spec.md`) and the skill text, never from `test_bugs.py` or the code's own transition table. Fixture secrets are synthetic. Raw logs stay local; only `.md` reports go to `.workflow/evidence/sqlite-bug-tracker/attempt-<n>/`.

## Testable claims (criterion -> observable outcome)
1. add/show/list/update/delete work on one record through `bugs.py`; `delete` refuses without a GD order.
2. All 11x11 status pairs behave as the spec table says. GD-only moves (Backlog in/out, Won't fix, Accepted) refuse without `--by GD`. `duplicate_of` is required for Duplicate.
3. The 4 priorities are accepted, anything else is refused, and no Severity field exists.
4. Terminal bugs are purged more than 90 days after `closed_at`. Open and Backlog bugs are never purged. IDs are not reused. Reopen clears `closed_at`.
5. Deleting the DB and running `rebuild` gives identical state. This holds across switch, pull, union merge, crash and a torn line. A purged bug does not come back through a merge.
6. Field limits, required fields, one-line rule, the diacritics refusal, secret refusal and PII redaction hold on every write path.
7. `round-cap.ps1` against a real DB: cap, extra round, Stop rule, settled and Backlog not capped, no Python blocks. Cap warning after a `bugs.py` call. Purge conditions at session start.
8. Every CLI call in the skill, agent and rule text parses against the real CLI. No live `bugs.md` reference, old status or bug Severity remains.
9. BUG-0001..0005 are imported as 5 Complete with `closed_at` 2026-10-29. `show BUG-0004` holds its text. `bugs.md` is gone.
10. `framework-sync.ps1` installs the `.gitattributes` line in a target.

## Not runnable now, with owners
- Criterion 9, real data: the CLI refuses writes from a linked worktree, so it runs in the main checkout after the merge. Owner: main session, dispatching E1 for oracle comparison.
- Python 3.10 runtime: not installed.
- Live-session `if` filters and PostToolUse exit 2 delivery.

## Partitions and boundaries
- Status pair: 121 pairs from the spec table, each legal or illegal, plus attribution (none / `--by GD` / other). One of each outcome class is also run through the skill's command forms.
- Priority: Low, Medium, High, Highest, then `high`, `Critical`, empty, `Severity` as a field name, `Medium ` with trailing space.
- Text fields (title 100, description 280, repro 500, expected/actual/evidence/root_cause 300, event note 200): length L-1, L, L+1, 0 (required ones refused, `repro` accepts `not yet`), embedded newline in a one-line field, `$`, backtick, quotes, braces, ASCII-only vs non-Vietnamese non-ASCII (em dash, emoji). Length is counted in chars, not bytes.
- Diacritics: Vietnamese-only letters (d-stroke, horn o and u), a precomposed one, the same text in NFD, and a shared accent (French e-acute). Record the actual behaviour of the shared accent against the spec wording "Vietnamese diacritics". Cover every text field, plus `--by`, `duplicate_of` and note. Unaccented Vietnamese is out (Known limitation).
- Purge age, injected clock if the CLI offers one: 89d, 90d-1s, 90d, 90d+1s, 91d. If there is no clock seam, use journal fixtures with `ts` at the boundary and report the margin and run spread. An exact 90d result that cannot be proved is named as unproved, never inferred. Also: a terminal bug aged 400d vs an open and a Backlog bug aged 400d; a bug moved Complete -> Reopen -> Complete restarts the clock; terminal -> other terminal (does `closed_at` reset?) is checked against the spec wording "90 days after reaching terminal" and any ambiguity is reported, not decided.
- ID: purge the highest ID, add a new bug, expect no reuse. Purge a middle ID, read it, expect "purged". `show` of an ID never created, expect "not found".

## Decision table (criterion 5, one distinct outcome per row)
| Condition | Expected |
|---|---|
| Journal newer than DB (switch, pull) | rebuild on next command |
| Journal line appended, DB not committed (crash) | next command heals it |
| Torn final line | repaired or refused as the spec says, never silently dropped mid-file |
| Same `event_uid` twice | deduped |
| Shuffled line order | identical DB |
| Two `bug_uid`s on one ID | writes and `counters` for that ID fail closed until `doctor --fix` appends `renumber` |
| Tombstone plus a resurrected create | bug stays gone |
| `bugs.md` present | every command refuses |
| Linked worktree | read ok, write refused |

## State transitions
- All legal transitions in the spec table are driven end to end.
- Illegal ones are rejected, each with its refusal text read. Minimum set: Request -> Complete, Resolved -> Complete, Complete -> Processing, Backlog -> Processing, Processing -> Review, any -> Request from a terminal without a match, terminal -> Backlog without GD.

## Ranked cases
| # | Case | Impact | Likelihood | Owner |
|---|---|---|---|---|
| C0 | Baseline on `b6deca7`: `test_bugs.py`, `hooks/tests/run.ps1` (pwsh 7 and 5.1), `verify.ps1`. Gives this QA its own evidence instead of the main session's relayed run. Counts, exit codes and warning count are cited. | High | Low | E1 (`test_bugs`), E2 (hooks), E3 (`verify`) |
| C1 | Lifecycle walk as a main session would drive it from `SKILL.md`, `fix`, `qa`, `bug-lifecycle` alone, on a synthetic bug in a temp main-checkout repo (copy of the tree at `b6deca7`). Steps: search, add, Processing, Resolved, Review, then three branches (Complete, Reopen, Resolved), Backlog and GD-only moves, Duplicate, As designed. Includes the full 121-pair matrix and the illegal set. Each place where the text is ambiguous, wrong or missing is a finding. | High | Medium | E1 |
| C2 | Criterion 3, 6 field boundaries and diacritics matrix above, on every write command (`add`, `update`, `set-status` note, `round`, `extra-round`, `stop-rule`, `import-md`). Includes the refused write leaving no journal line and no DB change. | High | Medium | E1 |
| C3 | Secret and PII: synthetic secret shapes taken from the pattern file's documented shapes, refused and absent from journal, DB, stderr and `list`. Email and phone redacted in each text field. Pattern file moved away: write refused. | Critical (secret) | Low | E1 |
| C4 | Purge boundary, retention classes and ID rules above. `purge --dry-run` writes nothing; real purge appends only a text-free tombstone. | High | Medium | E1 |
| C5 | Real git in a temp repo, `merge=union`, with `core.autocrlf=true` and false. Cases: two branches each file a bug and merge, both survive and the DB rebuilds; `git switch` between branches; pull from a bare remote; rebase and cherry-pick that touch the journal; purge on A, merge pre-purge B, bug stays gone; same ID filed on both branches -> fail closed -> `doctor --fix`; torn final line; crash simulation; `rebuild` from journal alone after deleting DB and WAL files; linked worktree read ok and write refused. | Critical (data loss) | Medium | E1 |
| C6 | Concurrency: two or more processes writing in parallel, plus a `counters` read during a write. IDs unique, no torn line, no `database is locked` leaking as success. | High | Low | E1 |
| C7 | Search and `sql`: FTS5 queries containing `-`, `:`, quotes, `BUG-0001`, empty, `*`. Syntax errors must come back as a clean refusal, not a traceback. `sql` rejects INSERT/UPDATE/DELETE, PRAGMA writes, ATTACH, multi-statement and extension load. | Medium | Medium | E1 |
| C8 | Hook through fixture dispatches against a real temp-repo DB, never mocked counters. Dispatch JSON naming a bug at fix_used = cap-1, cap, cap+1 and review_used likewise: allow, block, block. Also: settled bug and Backlog bug not capped; `extra-round` raises the cap; Stop rule recorded; unknown ID; two IDs in one dispatch; lowercase or unpadded ID; no journal (allowed, no Python started); Python missing from PATH (block); CLI error (block); `Verify:` brief with `Repro: reproduces` counted. Run on pwsh 7 and Windows PowerShell 5.1. Exit codes and stderr text cited. | High | Medium | E2 |
| C9 | PostToolUse `-Mode edit`: fixture JSON for a Bash and a PowerShell call that runs `bugs.py` pushing a bug to the cap gives the warning; a non-bug shell call gives none. Session-start purge: runs on the main checkout only; skipped on `feature/*`, during merge or rebase, with a dirty journal, and with no Python; status line text matches the spec; never commits; failure never blocks the session. | Medium | Medium | E2 |
| C10 | Shell and encoding: stdin JSON from pwsh 7 and from 5.1 containing `$x`, backticks, quotes, em dash and emoji reaches the journal byte-exact (UTF-8, no BOM, LF). | High | Medium | E2 |
| C11 | Migration on a copy (pre-merge half of 9): copy the real `.workflow/bugs.md` plus the repo tree to a temp git repo, run `import-md`. Expected: 5 Complete, `closed_at` 2026-10-29, events from History, Severity mapped (Critical -> Highest), `description` = old `Actual`. Re-run -> journal byte-identical (uuid5). Same journal bytes from a second directory. `show BUG-0004` holds its text. Where a record breaks a content rule the import must stop with a report and write nothing partial. E1 records exactly which fields break and the by-hand rewrite text the main session will need. After import, `bugs.md` removed, other commands work, a recreated `bugs.md` makes every command refuse. | High | High | E1 |
| C12 | Docs contract: extract every `bugs.py` invocation and flag in `fix`, `qa`, `qa-standards`, `feature`, `release`, `review`, `new-project`, `mem` skills, `qa-lead.md`, `routing.md`, `core.md` and run each form against the CLI (parses, flags exist). `git grep` for `bugs.md`, `Severity` on bugs, old statuses (Open, Fixed, Closed, Reopened) in live files, excluding `.workflow/` history. `release` rows 0b, 1, 4: High or Highest in Backlog blocks, Python absent is not a pass, `--dry-run` writes no status. Walk a `/fix` -> `/qa` -> `/release` bug sequence on the temp repo by the text. Label it "indicative, text plus CLI" since no real session runs it. | High | Medium | E3 |
| C13 | Criterion 10: `framework-sync.ps1` on temp targets on pwsh 7 and 5.1. Targets: no `.gitattributes`; existing file with other lines and CRLF; line already present (twice-run -> no diff); a conflicting `bugs.jsonl` line; no BOM and LF at the line; `.gitignore` gets `bugs.db*`. Dry-run mode, if the script has one, writes nothing. | Medium | Medium | E3 |
| C14 | Python 3.10, static only: `ast.parse(feature_version=(3,10))` on `bugs.py` and `test_bugs.py`, grep for post-3.10 APIs (`tomllib`, `datetime.UTC`, `typing.Self`, `except*`, `itertools.batched`, new f-string forms), FTS5 availability check (`sqlite3.sqlite_compileoption_used`). Labelled static, not a 3.10 run. | Medium | Low | E1 |
| C15 | Criterion 9 real data, after the merge: the same commands as C11 in the main checkout, compared to C11's expected values. Journal secret scan on staged diff. `Grep` finds no live `bugs.md` reference. | High | n/a | Main session runs; E1 re-dispatched for the comparison |

## Dropped for scope
- Journal size and scale, `import-md` speed: no performance requirement in the criteria.
- Unity, device, build, multiplayer, Editor: none exist in this repo.
- Unaccented Vietnamese detection: a declared Known limitation, not a criterion.
- Code Coverage: not run, and it would be `unsupported` for any behaviour claim anyway.

## Exit criteria (each report carries `Not covered:` with an owner per gap)
| Criterion | Evidence |
|---|---|
| 1 | C1 and C2 reports: each CRUD command run with exit code and output, `delete` refusal without a GD order quoted. |
| 2 | C1: the 121-pair matrix in a table (expected from the spec, actual, match) with 0 mismatches or each mismatch as a finding. GD-only refusals quoted. |
| 3 | C2: the partition table with the refusal text for each bad value; `list` or `show` output has no Severity field. |
| 4 | C4: boundary table with margin and run spread; open and Backlog at 400d kept; no ID reuse after purge. Exact 90d proved or named unproved. |
| 5 | C5: per-scenario table with the git commands run, the DB state before and after, and `rebuild` equal to the live DB (row counts plus a hash of `list` output). |
| 6 | C2 and C3: limit table (L-1, L, L+1) per field and per write command; refused writes leave the journal hash unchanged; secret and PII outputs quoted, with no secret in any artifact. |
| 7 | C8 and C9: the fixture table (input, hook exit code, stderr, DB state) on both PowerShell versions; session-start conditions table. |
| 8 | C12: invocation list with parse results, the `git grep` output (0 live hits), the sequence walk with each text defect as a finding. |
| 9 | C11 on the copy now, plus C15 after the merge. Criterion 9 is signed only with the C15 line. |
| 10 | C13: target-by-target table, diff of the target before and after, second-run diff empty, both PowerShell versions. |
| Baseline | C0: counts and exit codes at `b6deca7`. |

- Sign-off judges these reports per `qa-standards`. A skipped check is a gap, never a pass. A coverage figure is never cited.

## Open bugs
- None for this feature, and no bug DB exists yet.
- Findings go in the executor reports with the `qa-standards` fields. Main session's call: they stay in the reports and the feature file's `Bugs` table until the merge, because the CLI refuses writes from the worktree and filing on `develop` would put them on the wrong branch.

## Gaps (owner)
- Criterion 9, real data (main session, post-merge). `Not signed off` on criterion 9 until C15 reports.
- Python 3.10 runtime (GD): C14 is static only.
- Live-session `if` filters and PostToolUse exit 2 delivery (GD or main session in a fresh session after the merge): C8 and C9 prove the script on fixtures.
- Skill text under a real `/fix`, `/qa`, `/release` run: C12 is an indicative walk only.

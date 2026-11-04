# SQLite bug tracker

## Context
`.workflow/bugs.md` is one growing markdown file: hard to query, and `round-cap.ps1` has to regex-parse it. The GD wants each bug to be a database record with CRUD, a new status flow, a priority scale and a 90-day window.

Route: `/feature`, size L, slug `sqlite-bug-tracker` (changes the data contract of `/fix`, `/qa`, `/release`, `/feature` and a hook). Profile n/a (framework repo). Risk flag: no.

## GD decisions
1. **Storage:** `.workflow/bugs.db` gitignored for CRUD; every change appends to tracked `.workflow/bugs.jsonl`. The journal is the truth, the DB a cache rebuilt from it.
2. **Retention:** auto-delete only terminal bugs, 90 days after reaching terminal. Open and Backlog bugs never auto-delete. IDs never reused.
3. **Statuses:** the seven requested, plus `Won't fix`, `Accepted`, `As designed`, `Duplicate` kept as statuses.
4. **Priority:** Low, Medium, High, Highest replaces Severity on bugs. Critical → Highest. `/release` blocks on High and Highest. `code-reviewer` findings keep Severity; the scale changes on filing.
5. **Concise records:** every bug has a title and a short description, with enough content and no long prose.
6. **English only:** the whole database is written in English.

## State machine
| From | To | Set when |
|---|---|---|
| (new) | Request | QA files it |
| Request, Reopen | Processing | Main session dispatches the owner |
| Processing | Request | Attempt `Failed` or `Blocked`, no fix delivered |
| Processing | Resolved | Owner's `Fixes:` and `/fix` step 6 checks pass |
| Resolved | Review | Main session dispatches a `Verify:` brief |
| Review | Complete | `Repro: BUG-#### gone` |
| Review | Reopen | `Repro: BUG-#### reproduces` |
| Review | Resolved | Verify run returned no `Repro:` line |
| Complete, other terminal | Reopen | A new match on a settled bug |
| Any open | Backlog | **GD only** |
| Backlog | Request | GD only |
| Any open | Won't fix, Accepted | **GD only**, mirrored to `DEBT.md` |
| Any open | As designed, Duplicate | QA or main session (`duplicate_of` required) |

- **Terminal (settled, purgeable):** Complete, Won't fix, Accepted, As designed, Duplicate.
- **Backlog (my call):** counts as settled for QA sign-off with a `Known limitations` line, so deferral is possible. High or Highest in Backlog still blocks `/release`. Never capped by `round-cap`.
- **Old → new:** Open → Request · Fixed → Resolved · Closed → Complete · Reopened → Reopen.
- **Writer unchanged:** main session is the only writer; agents propose. Agents without a shell (`qa-lead`) get `bugs show` output in the brief.

## Component: skill `bugs` (non-invocable, like `mem`)
`.claude/skills/bugs/`: `SKILL.md`, `scripts/bugs.py` (stdlib, run with `python -I`, interpreter from `Resolve-Python`), `scripts/test_bugs.py`, `references/schema.md`.

**Commands:** `add` · `update` · `set-status` · `round` · `extra-round` · `stop-rule` · `show` · `list` (filters: status, priority, feature, open) · `search` (FTS5, for the "check existing bugs first" rule) · `sql` (read-only) · `delete` (GD order only) · `counters --json` · `purge [--dry-run]` · `rebuild` · `doctor [--fix]` · `import-md`. Long text arrives as JSON on stdin: PowerShell would expand `$` in arguments.

**Tables:** `bug` (id, uid, title, description, priority, status, feature, owner, regression_test, repro, expected, actual, evidence, root_cause, duplicate_of, fix_used, fix_cap, review_used, review_cap, created_at, updated_at, closed_at) · `bug_event` (replaces History) · FTS5. `CHECK` constraints on status and priority; indexes on status, priority, feature, closed_at.

**Record content rules, enforced by the CLI on every write (over the limit → refused with the field and its length, never truncated):**
| Field | Limit | Content |
|---|---|---|
| `title` | 100 chars, one line | Required. The defect, naming the system |
| `description` | 280 chars, one line | Required. What breaks, where, and the impact |
| `repro` | 500 chars | Required, or `not yet`. Numbered steps from a known state; attempts and hits |
| `expected`, `actual` | 300 chars each | Required. `expected` names its source |
| `evidence` | 300 chars | Required. Paths or a one-line excerpt; full logs stay in `.workflow/evidence/` |
| `root_cause` | 300 chars | Optional until known |
| event note | 200 chars, one line | Who, what, and the evidence reference |

**English only:** the CLI refuses text with Vietnamese diacritics in any field, including notes and `--by`. Vietnamese without diacritics cannot be detected reliably, so `SKILL.md` makes the main session translate the GD's or QA's words before filing. A localized string under test is cited by its table key, not its text.

**Consistency mechanism (the hard part):**
1. Each journal line carries `event_uid`, `bug_uid`, `ts`, and a typed payload. `ts = max(now, last + 1 ms)` so clock skew cannot invert one machine's events.
2. Write path: `BEGIN IMMEDIATE`, check the journal hash against the DB, rebuild if different, validate the transition, apply, append journal, commit. A crash after the append is healed by the next hash mismatch.
3. Every command runs the hash check, which covers `git switch`, pull and merge.
4. Replay sorts by `(ts, event_uid)`, dedupes by `event_uid`, refuses malformed lines, and never enforces transitions (the history already happened).
5. `.gitattributes`: `.workflow/bugs.jsonl text eol=lf merge=union`. Appends repair a torn final newline.
6. **Duplicate IDs across branches:** two `bug_uid`s holding one ID. Replay reports it; writes and `counters` for that ID fail closed until `doctor --fix` appends a durable `renumber` event for the later create. Later lines attach by `bug_uid`, never by ID.
7. **Purge:** drops the bug's lines and appends one text-free tombstone (`bug_uid`, numeric id). Replay drops that uid, so a union merge from a pre-purge branch cannot resurrect it. High-water ID = max over creates, tombstones and renumbers; a missing ID below it reads "purged".
8. **Worktrees:** (changed in build, root-caused in the feature Log row 20: both readers now read the root's own `.git` file and `commondir`, not git output.) Root originally came from comparing `--git-dir` with `--git-common-dir`. Reads use the main checkout; writes from a linked worktree are refused.

**Security:** the Edit/Write secret hook does not see shell calls, so the CLI refuses secret shapes and redacts PII using `mem.py`'s `load_secret_patterns` and `redact_pii` (loaded through `importlib`, because `-I` breaks a plain import). A missing pattern file refuses the write. `sql` uses a read-only connection. All other SQL is parameterized. The staged-diff `pre-commit` scan covers the journal.

**Purge trigger:** `session-start.ps1` runs it when on the main checkout, with no merge or rebase in progress, a git-clean journal, and a branch outside `feature/*`. It never commits. It adds one status line: `Bugs: N open (H High+); purged M, journal uncommitted`. Failure never blocks a session.

## Hook: `round-cap.ps1`
- `Get-BugCounters` calls `bugs.py counters <id> --json` through a new `Invoke-Bugs` in `common.ps1`. The JSON carries settled, used and cap values, and a synthesized `record` string, so `New-Counter` and its extra-round and Stop-rule matching stay unchanged. Used stays file + ledger: Python never reads `rounds.json`.
- **Fail closed:** no Python, or a CLI error, on a dispatch naming a bug → block. No journal → no counters, as a missing `bugs.md` behaves today (and no Python start).
- **Cap warnings:** the `bugs.md` edit branch is replaced by `-Mode edit` reacting to shell commands that call `bugs.py`, wired as a new PostToolUse entry for `Bash|PowerShell`. Cap logic keeps one owner.

## Files to change
- **New:** `.claude/skills/bugs/*`, `.workflow/bugs.jsonl`.
- **Delete:** `.workflow/bugs.md`, `.claude/skills/fix/references/bugs-template.md`.
- **Git and sync:** `.gitignore` (`.workflow/bugs.db*`), `.gitattributes`, `.claude/tools/framework-sync.ps1` (sync the attributes line; it handles only `.gitignore` today), `README.md` sync row.
- **Hooks:** `common.ps1`, `round-cap.ps1`, `session-start.ps1`, `tests/run.ps1`; `.claude/settings.json` for the PostToolUse wiring only.
- **Skills:** `fix/SKILL.md`, `qa-standards/SKILL.md`, `qa-standards/references/bug-lifecycle.md`, `release/SKILL.md` (rows 0b, 1, 4; Python absent is not a pass; `--dry-run` writes no status), `feature/SKILL.md`, `feature/references/feature-template.md`, `qa/SKILL.md`, `review/SKILL.md`, `new-project/SKILL.md`, `mem/SKILL.md` query hint.
- **Agents and rules:** `agents/qa-lead.md`, `rules/routing.md` (State, extra-round wording), `rules/core.md` (commit exception).
- **Layer check:** `verify-layer/scripts/verify.ps1` contracts at lines 50, 52, 56, 57. Deleting the template drops its contract, and `.py` gets no contract check, so `test_bugs.py` asserts the status list and marker strings. The skill must respect `verify.ps1` limits: no 15-line fence in references, no hardcoded script path, no `Known limitations` bullet.

**Journal commits:** `feature/SKILL.md:14` excludes `.workflow/` and the closure commit omits bug state, so nothing commits it inside `/feature`. Add `.workflow/bugs.jsonl` to the CP4 closure commit and to the `core.md` exception. No-feature `/fix` reports "journal uncommitted" in its reply; committing still waits for the GD's order.

**Feature file `Bugs` table:** keeps ID, title and priority, drops status so it cannot drift. CP4 and QA query the CLI. It stays the permanent record once a bug is purged.

**Not changing:** `.claude/settings.json` gets no new permission allow rule for `bugs.py`. The design review suggested one, but `mem.py` has no such rule in that file, so there is no precedent to follow.

## Migration
`import-md`: BUG-0001..0005 (all Closed) → Complete, with `closed_at` and events parsed from History, Severity mapped, and deterministic `uuid5` uids so re-running cannot duplicate. `description` takes the old `Actual` text. A record breaking a content rule stops the import with a report, and the main session rewrites that field by hand; the importer never truncates. Then `.workflow/bugs.md` is removed. The CLI refuses every other command while a `bugs.md` exists, which also catches adopted game projects after a framework sync.

## Build order
1. `bugs.py` + `test_bugs.py` (TDD), `schema.md`, `SKILL.md`.
2. `Invoke-Bugs`, `round-cap.ps1`, `session-start.ps1`, settings wiring, hook tests.
3. Rewrite skills, agents, rules, `verify.ps1`, sync.
4. Run the migration on this repo's data.

## Verification (run, not read)
- `python -I .claude/skills/bugs/scripts/test_bugs.py`: CRUD; every allowed and refused transition; GD-only guard; purge at 89, 90, 91 days; open and Backlog never purged; Reopen clears `closed_at`; ID not reused after purge; replay determinism with shuffled lines; duplicate ID fail-closed then `doctor --fix`; tombstone beats a resurrected line; crash between append and commit; torn final line; secret refused, PII redacted; each field at its limit accepted and one char over refused; missing `title` or `description` refused; a newline in a one-line field refused; Vietnamese diacritics refused in every text field; `sql` rejects writes; worktree write refused; `bugs.md` present refuses.
- **Real git scenario in a temp repo:** two branches each file a bug, merge through `merge=union`, both survive and the DB rebuilds; `git switch` refreshes the DB; purge on one branch, merge a pre-purge branch, bug stays gone.
- `pwsh .claude/hooks/tests/run.ps1`: updated `round-cap` cases (past cap blocks, settled and Backlog not capped, extra round raises cap, no Python blocks), purge conditions at session start, cap warning after a `bugs.py` call.
- `/verify-layer` exit 0.
- Real migration: `bugs.py list` shows 5 Complete with `closed_at` 2026-10-29; `show BUG-0004` holds its text; `Grep` finds no live `bugs.md` reference outside historic `.workflow/` records.
- Gates offered when the code is built (recommended yes for L).

## Accepted trade-offs to carry into Known limitations
- Purge removes a bug from the working data only. Committed journal lines stay in git history, so purge is not a privacy erase.
- Python 3.10+ with FTS5 becomes mandatory for bug work. It is optional today, where only `mem` degrades.
- `mem q` stops indexing bug text once `bugs.md` is gone; `bugs.py search` replaces it.
- `/release` row 0b lists `Accepted` High and Highest bugs from the DB, so one purged past 90 days disappears there. `DEBT.md` keeps the mirror; row 0b should read `DEBT.md` too.
- A renumbered ID leaves old `rounds.json` events under the old ID (local ledger, rare case).
- The English check catches diacritics only. Vietnamese typed without diacritics passes the CLI and relies on the main session's rule.

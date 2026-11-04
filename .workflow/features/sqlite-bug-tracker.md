# SQLite bug tracker

- Status: Closed
- CP: CP4 closed 2026-11-04 under the GD's standing order; merged as `3b0810c`, pushed to `develop`. Finished past the 12:00 deadline, on the GD's choice to keep QA.
- Session: 144bb0e0-5428-4e8b-92a5-0d45be3e4813 · 2026-11-03
- Size: L · Risk flag: no
- Rounds: review 0/6 · QA 0/2 · rework 0/8 (file count; the hook ledger holds review 6, QA 1, rework 7)
- Profile: n/a — framework repo; `CLAUDE.md` is the per-project template
- Feature root: `.claude/skills/bugs/`
- Branch: feature/sqlite-bug-tracker · Base: develop
- Assemblies: none (Python CLI, PowerShell hooks, skill docs)
- Build mode: serial
- Worktrees: none

## Request (verbatim)
> tôi có ý tưởng như sau về quy trình log bug của QA. Thay vì ghi bug vào file markdown, rất cồng kềnh và khó truy xuất, thi tôi muốn tận dụng luôn sqlite, ghi các bug thành database, với mỗi 1 bug là 1 bản ghi có thể thao tác CRUD như database bình thường. Bug sẽ có các trạng thái như sau:
> - Request: QA tìm ra bug, ghi vào bảng, yêu cầu sửa
> - Processing: agent nhận bug và xử lý
> - Resolved: bug đã xử lý xong, chờ QA review
> - Review: QA sẽ review lại các bug sau khi các agent sửa
> - Complete: bug đã sửa xong
> - Reopen: bug chưa sửa triệt để, bị mở lại
> - Backlog: tạm thời cho bug vào backlog
> Độ ưu tiên có các mức sau:
> - Low
> - Medium
> - High
> - Highest
> Các bug sẽ tồn tại trong window 90 ngày, sau 90 ngày thì xóa bug cũ ngoài vùng window đi

> (on the first plan) các bug có title và mô tả ngắn gọn nhưng đủ nội dung cần thiết, không văn xuôi dài dòng. Toàn bộ database viết bằng tiếng Anh

## GD decisions
- 2026-11-03 CP1: n/a (direction given in the request and the four answers below).
- 2026-11-03 Storage: DB + tracked text journal (`bugs.jsonl`); cost: one more file and a rebuild path.
- 2026-11-03 Retention: only terminal bugs, 90 days after reaching terminal; open and Backlog bugs never auto-delete; IDs never reused.
- 2026-11-03 Other endings: `Won't fix`, `Accepted`, `As designed`, `Duplicate` stay as statuses (11 total); cost: longer state machine.
- 2026-11-03 Priority replaces Severity on bugs; Critical → Highest; `/release` blocks on High and Highest.
- 2026-11-03 Records: title and short description, no long prose; whole database in English.
- 2026-11-03 Isolation: session `ai-for-game-development-bb` has uncommitted Code Coverage work in the shared checkout, overlapping 4 files. GD chose a dedicated worktree; cost: the migration runs in the main checkout after the merge, and the 4 files may need merge handling.
- 2026-11-03 Gates: review yes, QA yes.
- 2026-11-03 Fixture IDFA of unknown origin in unpushed branch commits: GD chose rewriting the local branch before the merge; cost: the branch's SHAs change.
- 2026-11-03 CP3: approved, no drift to send back.
- 2026-11-03 Release-blocker bypasses kept as built: closing a High or Highest bug as `As designed` or `Duplicate`, lowering priority with `update`, and `extra-round`, none needing `--by GD`. Every change stays in the journal; `--by GD` is self-attested and would stop only mistakes.
- 2026-11-03 Python: test on 3.14 only, no 3.10 install. Cost stated: a pass on 3.14 does not prove 3.10, which `Resolve-Python` still accepts; the static check stands in.
- 2026-11-03 Live hook check: one short `claude -p` in a temp repo after the merge and migration, with a bug at its cap; cost: one small model call.
- 2026-11-03 QA findings: fix all 27 in this pass, Lows included.
- 2026-11-03 Main session's calls on QA ambiguities: E1's A1 (QA may settle a Backlog bug) is covered by the GD's CP3 answer, kept. A3: the purge clock counts from the last terminal status reached, the later and safer date. Plan C8's "block at the cap" was a plan error: `routing.md` blocks past the cap.
- 2026-11-03 Review quota reset by the GD, extra round: review +3 (cap 3 → 6). A failed round goes back to the author instead of stopping; counting restarts from the three rounds used. Cost stated: each extra round is one more fix dispatch plus both review gates.
- 2026-11-03 Standing order from the GD: after QA sign-off, clean up unused worktrees and unneeded files and resources, then commit and push without asking for approval. Covers CP4, the merge and the push; the accepted gaps are listed in the closing report.
- 2026-11-03 Secret gates: the GD chose fixing the older gaps in this feature (commands steering the scan, bare-repo push) over a separate task. Cost stated: at least one more review round and 1-2 hours; a wide block may stop a valid commit. Main session's design: a closed list of parsable commit and push forms, anything else blocks with how to re-run it.
- 2026-11-04 Deadline from the GD: finish by 12:00 today. Main session's schedule: author done by 10:30, review and QA by 11:10, sign-off by 11:20, merge through push by 11:50. At 11:15 any finding still open goes to the GD with its cost.
- 2026-11-04 Secret gates at `0f9c62c`: the GD chose shipping with deliberate-evasion forms as known limitations and native git hooks as the next task; the security verdict stays Blocked for those forms. That answer did not cover the two regressions code review and E6 reported after it (`bash -c` commit landing a key, the prescribed `GIT_TERMINAL_PROMPT=0` push blocked), so they get one narrow fix.
- 2026-11-04 Deadline: the GD kept QA over the 12:00 deadline; expected finish 12:15-12:30. Cost stated: 15-30 minutes late.
- 2026-11-03 CP2: approved the plan, copied unchanged to `.workflow/features/sqlite-bug-tracker.spec.md`. Size and spec came from that plan; no separate architect dispatch.

## Spec
Full spec: `.workflow/features/sqlite-bug-tracker.spec.md`.

Acceptance criteria:
1. Every bug is one record with create, read, update and delete through `bugs.py`.
2. The 11 statuses and the spec's transition table are enforced on write; GD-only moves refuse without a GD attribution.
3. Priority is one of Low, Medium, High, Highest; bugs carry no Severity.
4. Terminal bugs older than 90 days since reaching terminal are purged; open and Backlog bugs never are; IDs are never reused.
5. `bugs.jsonl` alone rebuilds the DB; branch switch, pull, union merge, crash and a torn line all converge; purged bugs do not come back through a merge.
6. Field limits, required fields and the Vietnamese-diacritics refusal hold on every write; secrets refused, PII redacted.
7. `round-cap.ps1` caps, extra rounds, Stop rule and settled handling behave as before against the DB; no Python on a bug dispatch blocks.
8. `/fix`, `/qa`, `/feature`, `/release`, `/review`, `/new-project`, `qa-lead`, `routing.md`, `core.md` use the new contract; no live `bugs.md` reference remains.
9. BUG-0001..0005 are migrated and `.workflow/bugs.md` is gone.
10. `framework-sync.ps1` installs the `.gitattributes` line in a target project.

## Log
| # | Agent | Lane | Changed | Verified | Attempts n/N | Limitations / Needs GD |
|---|---|---|---|---|---|---|
| 0 | Notes | | SHAs in rows 1-7 predate the history rewrite in row 8; map them with that row | | | |
| 1 | git-expert | serial | branch `feature/sqlite-bug-tracker` at eb17e55 | `git branch --show-current`, `rev-parse HEAD develop` | 1/1 | none |
| 2 | general-purpose (T1) | serial | `.claude/skills/bugs/**` | Main session re-ran `test_bugs.py`: 195 OK. Agent: `test_mem.py` 33 OK; `verify.ps1 -File` exit 0 on SKILL and schema. Commit `e2f5625` | 1/4 | Python 3.10 runtime not run (3.14 only). Whole-layer verify fails on another session's `unity-test-framework` work, not this feature |
| 3 | git-expert | serial | worktree `.claude/worktrees/sqlite-bug-tracker`; main checkout back on `develop` | Peer diff hash equal before and after; worktree clean at `e2f5625` | 1/1 | Backup tag `backup/worktree-20261103T024313Z` left, drop at closure |
| 4 | general-purpose (T2) | serial | `common.ps1`, `round-cap.ps1`, `session-start.ps1`, `tests/run.ps1`, `settings.json` | Agent: baseline 552 pass, final 594 pass, 0 fail, on pwsh 7 and 5.1. Main session re-ran on pwsh: all passed. Added ~190 ms per bug dispatch | 1/4 | Live-session `if` filters and PostToolUse exit 2 not exercised; tests feed the hook JSON directly |
| 5 | general-purpose (T3) | serial | `.gitattributes`, `.gitignore`, `framework-sync.ps1`, `README.md`, 15 skill, agent and rule files; `bugs-template.md` deleted | Main session re-ran: verify exit 0 (21 warnings, as at T2), hook suite all passed. Agent: `test_bugs` 195 OK, `test_mem` 33 OK, real sync on temp repos, `git grep` clean. Commits `94638bc` and the docs commit after it | 1/4 | Skill text read and grepped, not exercised by a real `/fix`, `/qa` or `/release` run. Sync copies all three framework `.gitattributes` lines to a target |

| 6 | code-reviewer, security-reviewer (round 1) | parallel | none | Tree `171bbf7`. Code: Request changes, 4 Medium, 2 Low; re-ran the three suites. Security: Needs Confirmation on one fixture value, static only | 1/1 | Fixes go to the T1 author as attempt 2 |
| 7 | general-purpose (T1 author, review fixes) | serial | 10 files, 8 findings fixed. Commit `369cc95` before the rewrite | Main session re-ran: `test_bugs` 208 OK, hook suite all passed, verify exit 0 with 21 warnings | 2/4 | Author could not vouch for the fixture IDFA's origin; treated as unknown |
| 8 | git-expert (history rewrite) | serial | Branch rewritten to `4bb6768`, tree identical to `369cc95`; backup tags deleted. New SHAs: `db9a8c5` (was `e2f5625`), `026038e` (`5df98ce`), `e5fb445` (`94638bc`), `1de20e6` (`171bbf7`), `4bb6768` (`369cc95`) | `git log --all -S` empty; `test_bugs` 208 OK on the new tip | 1/1 | Old objects stay readable by sha in the local store until reflog expiry and prune |

| 9 | git-expert (merge) | serial | Merge `7392136` of `develop` at `1133fa0`; one conflict in `fix/SKILL.md` step 6 | Verify exit 0, 21 warnings; `git log --all -S` empty | 1/1 | none |
| 10 | code-reviewer, security-reviewer (round 2) | parallel | none | Tree `7392136`. Code: Request changes, 1 new Medium, 2 Low, all 6 round 1 findings closed by reading. Security: Needs Confirmation, full value in the local trace | 1/1 | Neither ran the suites |
| 11 | main session | | `.memory/traces/2026/11/2026-11-03-144bb0e0.jsonl` line 54 scrubbed per skill `mem`; 4 rows in `.workflow/framework-backlog.md` | Full-shape grep over traces: 0; `mem.db` prefix grep: 0 | | `mem lint`: 1 problem in an older trace, backlogged |
| 12 | general-purpose (T1 author, review round 2 fixes) | serial | 7 files, 3 findings fixed. Commit `c52bf24` | Main session re-ran on the merged tree: `test_bugs` 212 OK, hook suite all passed, verify exit 0 with 21 warnings | 3/4 | Python 3.10 runtime still not run |
| 13 | code-reviewer, security-reviewer (round 3) | parallel | none | Tree `c52bf24`. Code: Approve, 2 Low. Security: Clear, 1 Low on the local trace, trimmed by the main session. Both by reading | 1/1 | Lows go to the author once, no re-review |
| 14 | general-purpose (T1 author, Low fixes) | serial | `bugs.py`, `test_bugs.py`, `fix/SKILL.md` | Main session re-ran: `test_bugs` 213 OK, hook suite all passed, verify exit 0 with 21 warnings | 4/4 | Python 3.10 runtime not run; attempt budget for this author's task is used up |
| 15 | technical-architect (CP3) | serial | none | Read code: no drift needing rework; recommends approve; 7 author decisions for the GD. Ran nothing | 1/1 | D3 (linked worktree elsewhere gets no counters) goes to the framework backlog |

| 16 | qa-lead (Plan) | serial | `.workflow/evidence/sqlite-bug-tracker/qa-plan.md` (copied by the main session from its return) | 16 cases, criteria 1-10 mapped | 1/1 | Filing in the DB waits for the merge: findings stay in reports and the `Bugs` table |
| 17 | general-purpose (QA E1, E2, E3) | parallel, temp repos | Reports `.workflow/evidence/sqlite-bug-tracker/attempt-1/e1-cli.md`, `e2-hooks.md` + `e2-table-*.md`, `e3-docs-sync.md` | At `b6deca7`: 121-pair matrix 0 mismatches, rebuild equal 26/26, exact 90 d proved, migration on a copy clean. 27 findings: 1 High, 16 Medium, 10 Low. Hook suite: pwsh 7 all pass, 5.1 one test defect | 1/2 | E2's Write was refused; main session saved its return. Python 3.10 static only |
| 18 | general-purpose (QA fixes) | serial | 16 files, all 27 findings. Commit `ef27597` | Main session re-ran: `test_bugs` 264 OK, hook suite on pwsh all passed, verify exit 0 with 21 warnings. Agent: hook suite on 5.1 642 pass, `test_mem` 33 OK | 1/4 | F1 and E3-01, E3-02 are text fixes guarded by contract tests. With git absent, F2's edge remains |
| 19 | code-reviewer, security-reviewer (rework review, round 3 of the counter) | parallel | none | Tree `ef27597`. Code: Request changes, 1 Medium in `Get-BugsRoot`, 4 Low, 1 Medium on unchanged code; all 27 QA findings closed by reading. Security: Clear, 2 Low. Both by reading | 1/1 | Review counter reached its cap, 3/3 |
| 20 | technical-architect (stop rule root cause) | serial | none | Read, not run. Mediums per round 4, 1, 0, 1: no rising rate. Repeating thread: main-checkout resolution exists twice and a wrong root fails open. Fix: `Get-BugsRoot` starts no process | 1/1 | `pre-commit.ps1:65`, `pre-push.ps1:35` same class, to the backlog |
| 21 | general-purpose (QA fixes author, stop-rule dispatch) | serial | 8 files. Commit `84cc518` | Main session re-ran serially: `test_bugs` 270 OK, hook suite 657 pass 0 fail on pwsh 7 and on 5.1, verify exit 0 with 21 warnings. Agent: non-ASCII past-cap fixture failed before under code page 437, passes after, both shells | extra dispatch | Sweep leftovers in the framework backlog |
| 22 | code-reviewer, security-reviewer (round 4) | parallel | none | Tree `84cc518`. Code: Approve, 4 Low, 1 Medium on unchanged code. Security: Clear, 2 Low. Previous findings closed. Both by reading | 1/1 | |
| 23 | general-purpose (last review notes) | serial | 7 files. Commit `349542e` | Main session re-ran: `test_bugs` 274 OK, hook suite on pwsh 691 pass 0 fail 0 skip, verify exit 0 with 21 warnings. Agent: 5.1 691 pass, code page pin ran on both | 1/4 | No review round by rule; the wildcard sweep outside the bug hooks is in the backlog. Autoindex in a bracket checkout tried once with a fake `xerj` |
| 24 | general-purpose (QA E1, E2, E3 re-run) | parallel, temp repos | Reports in `.workflow/evidence/sqlite-bug-tracker/attempt-2/` | At `349542e`: all 27 earlier findings closed; matrix 0 mismatches; hook suite 691 pass on pwsh 7 and 5.1; migration on a copy clean. 9 new: N1, E3-15, DEF-E1-09, 10 Medium; DEF-E1-11, E3-16..19 Low | 2/2 | E3 wrote one gitignored `rounds.json` in the worktree and removed it |
| 25 | general-purpose (QA round 2 fixes) | serial | 12 files, 9 findings. Commit `bc8afb6` | Main session re-ran: `test_bugs` 298 OK, hook suite on pwsh 717 pass 0 fail, verify exit 0 with 21 warnings. Agent: 5.1 717 pass | 1/4 | |
| 26 | code-reviewer, security-reviewer (rework review), QA E4 (re-run) | parallel | `.workflow/evidence/sqlite-bug-tracker/attempt-3/e4.md` | Tree `bc8afb6`. Code: Approve. Security: Clear; found the commit and push secret scan exits silently in a bracket checkout (unchanged code). E4: 9 of 9 closed, regressions match the spec, 3 narrow new (DEF-E4-01 Medium, 02, 03 Low) | 1/1 | |
| 27 | general-purpose (final fixes) | serial | 11 files, 9 items. Commit `85583fe` | Main session re-ran: `test_bugs` 305 OK, hook suite on pwsh 775 pass 0 fail, verify exit 0 with 21 warnings. Agent: 5.1 775 pass, code page pin ran | 1/4 | Includes the secret gate on the GD's "handle everything". `Read-HookInput` changed for all hooks |
| 28 | code-reviewer, security-reviewer, QA E5 | parallel | `.workflow/evidence/sqlite-bug-tracker/attempt-4/e5.md` | Tree `85583fe`. Code: Approve. Security: Blocked, 1 High new (`git` by bare name runs from the working folder), 2 Medium, 1 Low. E5: all fixes closed, 970 gate rows 0 FAIL, no regression, DEF-E5-01 Medium, older | 1/1 | Hook charged round 4: review 4/6, rework 4/8 |
| 29 | general-purpose (secret gate fixes) | serial | 10 files. Commit `0f9c62c` | Main session re-ran: `test_bugs` 309 OK, `test_mem` OK, verify exit 0 with 21 warnings. Agent: hook suite pwsh 1132 pass, 5.1 1127 pass, 0 fail | 1/4 | Two hook rows failed once under load, cause unknown. Item 1 hidden here by `NoDefaultCurrentDirectoryInExePath`. Blocked-forms list goes in the closing report |
| 30 | code-reviewer, security-reviewer (round 5), QA E6 | parallel | `.workflow/evidence/sqlite-bug-tracker/attempt-5/e6.md` | Tree `0f9c62c`. Code: Request changes, 2 High regressions. Security: Blocked, F1-F10, evasive forms accepted by the GD. E6: suites 1132 and 1127 pass, gate rows pass; DEF-E6-01..04 | 1/1 | Review 5/6 |
| 31 | general-purpose (narrow fix), code-reviewer (round 6), qa-lead (Sign-off) | parallel | Working tree on `0f9c62c` | Code: Request changes, 1 Medium, 2 Low. qa-lead: Not signed off, DEF-E6-01, 02 unsettled, criteria 3, 5, 6, 8, 10 lack evidence at the tip | | Review 6/6, QA 1/2 |
| 32 | general-purpose (narrow fix, last edits) | serial | 4 hook files. Commit `da07194` | Agent: hook suite on pwsh 7, 1361 pass 0 fail 0 skip, from a byte-identical copy | 2/4 | Item 4 (Ordinal) and the three review edits have no failing-first run |
| 33 | code-reviewer (round 7), QA E7 | parallel | `.workflow/evidence/sqlite-bug-tracker/attempt-6/e7.md` | Tree `da07194`. Code: Approve, 2 Low. E7: `Repro: DEF-E6-01 gone`, `Repro: DEF-E6-02 gone`; 5.1 suite 1356 pass 0 fail; `test_bugs` 309 OK; verify exit 0; criteria 3, 5, 8, 10 pass; 6 pass except DEF-E7-01, accepted by the GD | 1/1 | |
| 34 | qa-lead (Sign-off 2) | serial | none | Signed off, conditional: pwsh 7 suite by a non-author before the merge; criterion 9 on the C15 line after it | 1/1 | |
| 35 | main session | | none | pwsh 7 hook suite at `da07194`: 1361 pass, 0 fail, 0 skip, exit 0; sign-off condition 2 met | | |
| 36 | git-expert (merge) | serial | Merge `3b0810c` | `git diff da07194 HEAD` empty | 2/3 | Under the GD's standing order |
| 37 | main session (C15, live check, closure) | | `.workflow/bugs.jsonl` imported, `.workflow/bugs.md` removed, BUG-0006..0008 filed Accepted, `.workflow/DEBT.md` | C15: 5 `Complete`, `closed_at` 2026-10-29, `show BUG-0004` holds its text, journal sha `278dd88beffdfb34` equals QA's copy, `doctor` clean. Live `claude -p`: the PostToolUse at-cap warning reached the session verbatim | | |

## Tests
| Criterion | Test id | Mode | Owner | Last result |
|---|---|---|---|---|
| 1-6, 9 (parser) | `.claude/skills/bugs/scripts/test_bugs.py` | Python unittest, temp repos | T1 author | 309 OK at `da07194`, QA E7 |
| 7 | `.claude/hooks/tests/run.ps1` | pwsh 7, 5.1 | T2 author | At `da07194`: pwsh 1361 pass, main session; 5.1 1356 pass, QA E7; 0 fail, 0 skip |
| 8 | `verify.ps1` whole layer | pwsh | T3 author | Exit 0, 21 warnings at `da07194`, main session and QA E7 |
| 10 | `framework-sync.ps1` on temp repos and suite rows | pwsh 7 | T3 author | Passed at `da07194`, QA E7 |
| 9 (real data) | C15 | Main checkout, after merge | Main session | Passed, journal sha equals QA's copy |
| 7 (live) | one `claude -p` | Temp project, bug at cap | Main session | At-cap warning delivered |

## Bugs
QA findings at `b6deca7`, not filed in the DB: no journal exists before the merge, and the CLI refuses writes from the worktree. Full records in the reports under `.workflow/evidence/sqlite-bug-tracker/attempt-1/`.

| ID | Title | Priority |
|---|---|---|
| F1 | Windows PowerShell 5.1's default pipe turns non-ASCII into `?` and evades the Vietnamese refusal | High |
| F2-F5 | Hook: worktree without journal uncapped; malformed or padded IDs skip caps or ledger; 5.1 suite test defect | Medium |
| DEF-E1-01..04, 07 | CLI: secret echoed on stderr; text-free writes ignore a missing pattern file; purged ID returns through a merge; unbounded rounds; Backlog match text | Medium |
| E3-01..07 | Docs and sync: no-journal release gate; dry-run ledger charge; overriding attributes and ignored journal unseen; uncommitted journal unreported; `update` evidence wording; `DEBT.md` location | Medium |
| DEF-E1-05, 06, 08; E3-08..14 | Whitespace `--by`, `round` without `+`, note syntax, smaller text defects, sync line endings | Low |
| N1, E3-15, DEF-E1-09, 10 | QA round 2: `bugs.py` follows a `.git` planted above the project; zero-row import makes no journal; a broken `mem.py` returning no patterns or raising `BaseException` fails open | Medium |
| DEF-E1-11, E3-16..19 | QA round 2: `--sk-` flag echoed; Abandon with no bugs; device marker reading; `.workflow/DEBT.md` naming; a later `eol` rule unwarned | Low |
| DEF-E4-01; DEF-E5-01; DEF-E6-01, 02 | Later rounds: pattern iterator; commands steering the scan; wrapper bypass, abbreviated staging flag. All closed at `da07194` | Medium, High |
| BUG-0006, 0007, 0008 | GD-accepted gaps, filed in the DB after the merge: hidden forms (DEF-E6-03, security F1-F10); commit messages unscanned (DEF-E6-04); phone with no `+` (DEF-E7-01) | Medium, Medium, Low |

## Known limitations
- Stop rule: review root-caused 2026-11-03 · extra dispatch: used
- Purge removes a bug from the working data only. Committed journal lines stay in git history, so purge is not a privacy erase.
- Python 3.10+ with FTS5 becomes mandatory for bug work.
- `mem q` stops indexing bug text once `bugs.md` is gone; `bugs.py search` replaces it.
- A renumbered ID leaves old `rounds.json` events under the old ID (local ledger, rare case).
- `/release` row 0b reads `DEBT.md` for an `Accepted` High or Highest bug purged past 90 days, but the `DEBT.md` mirror is a manual rule the CLI does not enforce.
- Run on Python 3.14 only (GD's choice); `Resolve-Python` still accepts 3.10 to 3.13, where only a static check ran. A runtime-only incompatibility would show first on such a machine.
- A Windows PowerShell 5.1 session that skips the documented `$OutputEncoding` line still writes `?` for non-ASCII text and evades the Vietnamese refusal; the CLI cannot detect it. To show the GD at CP4.
- A linked worktree of a bare repo or of a submodule blocks bug dispatches and prints `Bugs: unavailable`, as it has no `<checkout>/.git` to resolve. `bugs.py` refuses reads there too. A bare repo stored in a folder named `.git` returns its parent instead, which normally has no journal and reads as no bugs. With git absent, `bugs.py` reads work and writes refuse. A `--root` that is a subfolder of a checkout is its own root.
- With `CLAUDE_PROJECT_DIR` unset and `cwd` in a subfolder, a hook reads that subfolder as the root, finds no journal and lets a past-cap bug through. Production hook commands set the variable; the walk up was removed because it could follow a planted link.
- Main-checkout resolution exists in two languages (`main_checkout` in `bugs.py`, `Get-BugsRoot` in the hook), both reading the same files under one rule; a test drives both over the same layouts. A project below its repo root is its own journal root and silently skips `purge --auto`; `framework-sync.ps1` requires the project at the repo root.
- Inherited from `secret-patterns.txt`: a key with a `-` right before it, `x-sk-<body>`, is not recognized, so the CLI stores it and the commit hooks pass it. Framework-wide pattern, left as is; backlogged. In the closing report for the GD.
- The secret gates are text filters: they stop mistakes, not deliberate evasion. Forms that still pass unscanned or scan the wrong repository (`.workflow/evidence/sqlite-bug-tracker/` round 5 security F1-F10, E6-03): `g"i"t commit`, an interpreter or script calling git, `$x = $(Set-Location other); git commit`, a substitution that stages files, git-run commands (`submodule foreach`, `rebase -x`), an alias defined only in another repo, `git -c remote.origin.pushurl=...`, `git push origin stash:refs/heads/x`. A key in a commit message is not scanned (E6-04). `pre-push` scans unpushed commits for what it can see. GD accepted these 2026-11-04; native git hooks are the next task in the framework backlog.
- A later statement that does not name the verb is not checked: `git commit -m x && bash f.sh` and `git commit -m x | bash` pass the commit gate.
- The closed list refuses valid-looking forms, each with how to re-run: `git commit -m x && git push`, `git status && git commit`, `git --no-pager commit`, `git.exe commit`, `git -c k=v -C <path>`, `cat f | git commit -F -`, `cd x; git commit`, a path holding `~` or `%`, unquoted `echo git commit`, `ls source && git commit`, `bash -c "git stash push"`, a commit heredoc whose body names `git push` followed by `&& npm start`.
- DEF-E7-01, GD accepted 2026-11-04: a phone number with no `+` is not redacted, because `RX_PHONE` in `mem.py` targets international numbers only. A national number typed into a bug stays in the committed journal. The `core.md` rule against writing player PII still applies.
- Shared accents are refused as Vietnamese diacritics (`é` in `café`), with no override: rephrase.
- The English check catches diacritics only; Vietnamese typed without diacritics relies on the main session's rule.
- The rewritten fixture value stays readable by sha in this machine's git object store until reflog expiry and prune; a forced cleanup would also drop other sessions' dangling snapshots. A push sends only reachable objects. Claude's local session data under the user profile likely holds it too (not searched), outside the framework's reach. The local trace keeps only an 8-character prefix. Origin stays unknown. To show the GD at CP4 for acceptance.

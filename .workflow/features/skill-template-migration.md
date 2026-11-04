# Skill template migration

- Status: Closed
- CP: CP4 — closed; next step: git-expert merges into `develop` and pushes; briefs in `.workflow/evidence/skill-template-migration/batch-brief.md` and `comparator-brief.md`
- Session: f1b2508d-7a6a-4f8e-99b1-a44d812341ff · 2026-11-02
- Size: L · Risk flag: no
- Rounds: review 0/3 · QA 0/2 (hook counts QA round 1) · rework 0/8 (only events the hook cannot see: workflow review rounds, CP3 drift, a GD-reported reopen, CP4 fix-gaps rework)
- Profile: n/a — framework repo; `CLAUDE.md` is the per-project template
- Feature root: `.claude/skills/`
- Branch: feature/skill-template-migration · Base: develop @ bdf5c9ec70bf217ee9ed2763abd75fa4280b717c
- Assemblies: none
- Build mode: serial
- Worktrees: none

## Request (verbatim)
> áp dụng @framework-docs/skill-template.md với các skill, sửa luôn lỗi bị drop description 62/142 mà bạn vừa phát hiện

Note: the measured figure is 62/124; the GD wrote 62/142.

## GD decisions
- 2026-11-02 Bulk migration of all skills now. Reverses the same-day "migrate when next touched" decision and the backlog row that records it.
- 2026-11-02 CP1: n/a (direction given: apply the template and fix the dropped descriptions).
- 2026-11-02 CP2 approved: full migration, serial. Stated cost: roughly millions of tokens and many hours, about 11 writer batches each with an independent comparator. No new `checklist.md`; authors only propose them for the backlog.
- 2026-11-02 Budget lever: raise `skillListingBudgetFraction` to about 0.018, final value after M1. Stated cost: about 7.5k more tokens per session than today; the setting also ships to game projects.
- 2026-11-02 200k window: accepted, recorded under `Known limitations`.
- 2026-11-02 Gate baseline scenarios: skipped, recorded under `Known limitations`.
- 2026-11-02 Merge: after everything is fixed, merge `feature/skill-template-migration` into `develop` via `git-expert` (GD's words: "sau khi sửa xong toàn bộ, merge vào nhánh develop"). This answers the CP4 merge question in advance.
- 2026-11-02 CP3 and gate offer: scoped re-read of the 81 fixes before merge; review on the code only (`verify.ps1`, `run.ps1`, `settings.json`, moved scripts) with a security scan over the whole diff; QA as qa-lead evidence sign-off.
- 2026-11-02 Gaps accepted: 4 bodies past 8,000 chars by name (`feature` 14,317, `iap-server-receipt-ledger` 8,350, `firebase-unity-sdk` 8,069, `server-authoritative-validation` 8,035); AC3 200k row counts waived, not measurable here; the `No envelope` template rule; budget cost about 8.1k tokens per session.
- 2026-11-02 CP4: closed. Accepted: `465c7e3` read by no reviewer, proved by mutants; budget 0.02, which moves only the cap. qa-lead signed off in round 2. Merge and push confirmed.
- 2026-11-02 Push: after the merge, push `develop` to origin (GD's words: "có push lên develop"). The feature branch is not pushed.

## Spec
See `.workflow/features/skill-template-migration.spec.md`. Lanes: serial only.

## Log
| # | Agent | Lane | Changed | Verified | Attempts n/N | Limitations / Needs GD |
|---|---|---|---|---|---|---|
| 1 | general-purpose (T1) | serial | `verify.ps1` untitled-item check; evidence: baselines, anchors, ask inventory, token-survival, batches | Baselines: `run.ps1` 410 pass, `test_mem.py` 33 OK, verify exit 0 with 21 warnings. Main session re-ran verify: exit 0, 21 warnings, new count line | 1/4 | Evidence tools stay local. `run.ps1:316` fixture gap recorded in the backlog |
| 2 | general-purpose (T2) | serial | 123 `description` lines, 5 body symbol moves | Comparator attempt 1 failed 16 skills (routing words, procedure lists); main session applied its exact texts. Verify exit 0, token survival: 4 misses, all explained (compounds; a symbol held with a `ConsentForm.` prefix). Commit `4411e7c` | 2/4 | No second comparator reading on the 16: mechanical recheck only, because the comparator wrote the texts |
| 2b | main session (T2b) | serial | `.claude/settings.json` `skillListingBudgetFraction` 0.019 | M1 uncapped 18k. M2 capped: 201/201 rows with a description, Skills 18k against 19k (5.3% headroom). Commit in this step | 1/4 | |
| 3 | general-purpose (T3.1) | serial | 16 skills, 6 references, 2 moved files | Comparator failed 2 skills on attempt 1; main session applied its exact texts; per-file and whole-layer verify pass | 2/4 | Mechanical recheck only on the 2 fixes |
| 4 | general-purpose (T3.2) | serial | 15 skills, no moved code | Comparator failed 6 skills with 10 findings on attempt 1; main session applied its exact texts after confirming each target line; verify pass | 2/4 | Mechanical recheck only. Forward feed added to `batch-brief.md`. `researcher.md:25` citation missing from `anchors.md`, resolves |
| 5 | general-purpose (T3.3) | serial | 16 skills, 9 references, 10 moved files | Comparator failed 3 skills with 5 findings on attempt 1; main session applied its exact texts with target-line assertions; verify pass | 2/4 | Mechanical recheck only. 2 findings present at Base went to the backlog |
| 6 | general-purpose (T3.4) | serial | 16 skills, 8 references, 9 moved files | Comparator failed 5 skills with 10 findings on attempt 1; main session applied its exact texts with target-line assertions; verify pass | 2/4 | Mechanical recheck only. Bodies past 8,000: `iap-server-receipt-ledger`, `firebase-unity-sdk`, `server-authoritative-validation`, listed for CP4 |
| 7 | general-purpose (T3.5) | serial | 14 skills, 4 references, 3 moved files | Comparator failed 7 skills with 11 findings on attempt 1; main session applied its exact texts with target-line assertions; verify pass | 2/4 | Mechanical recheck only |
| 8 | general-purpose (T3.6) | serial | 14 skills, no moved code | Comparator failed 8 skills on attempt 1; main session applied its exact texts with target-line assertions; verify pass | 2/4 | Mechanical recheck only |
| 9 | general-purpose (T3.7) | serial | 15 skills, no moved code | Comparator failed 9 skills on attempt 1; main session applied its exact texts, each replaced line shown; verify pass | 2/4 | Mechanical recheck only |
| 10 | general-purpose (T4.1) | serial | 9 skills, `feature/references/build-checks.md`, 1 moved file. Commit `cc52458` | `run.ps1` 410 pass after the rewrite; comparator failed 4 skills with 5 findings on attempt 1; main session applied its exact texts; verify pass | 2/4 | `feature` 14,300 chars, for GD acceptance at CP4. Hook strings walked: all emitted, several unguarded by `$HookContracts` |
| 11 | general-purpose (T4.2) | serial | 9 skills, no moved code | Comparator failed 2 skills with 1 finding each on attempt 1; main session applied its exact texts; verify pass; `ask-check` 0 open | 2/4 | Mechanical recheck only |
| 12 | general-purpose (T5) | serial | `verify.ps1` promotion, 68 `run.ps1` fixtures, template and `verify-layer` docs | Main session re-ran: verify exit 0, 21 warnings, only `4 file(s): body > 8000`; `run.ps1` all pass; `test_mem.py` 33 OK; `ask-check` 0 open; fresh `/context` 201/201 rows, 18k | 1/4 | Author reported 478 PASS. 2 edges and a whole-layer skip recorded in the backlog |
| 13 | technical-architect (CP3) | serial | none | Read-only: 8 of 12 ACs met, AC4, AC7, AC11 partly, AC3 not. Final anchor walk 341/341, 0 unresolved | 1/1 | D1: no comparator read the 81 fixes the main session applied, and 10 batches were committed with no pass verdict |
| 14 | general-purpose (T5 rev) | serial | L1-L7: shared fence walker, CR-free body size, atomic title pattern; 37 checks. Commit in this step | Main session: verify exit 0; `run.ps1` 515 pass 0 fail on pwsh and on Windows PowerShell 5.1. Author: fresh CRLF clone gives the same result | 2/4 | Test-code review running |
| 14b | general-purpose (T5 rev 2, rev 3) | serial | Title pattern keeps odd backticks; fixtures for fence rules; timeout on the backtrack plant; unclosed-fence boundary. Commits `9ce3cdd`, `465c7e3` | Test-code review failed twice, Medium each time (F1 title loss, 14-line boundary); `final/runs-head.md`: verify exit 0, `run.ps1` 533/0 on both shells, CRLF clone equal; discrimination in `final/discrimination.md` | 4/4 | Budget used up. The last fix was not re-read by a reviewer; mutants prove it |
| 14c | main session | serial | `e79b564` budget 0.02 | Run at 0.01805 dropped 1 row, so 0.019 lacked 5%; run at 0.019 lists 201/201 | n/a | |
| 14d | qa-lead (Sign-off) | serial | none | Round 1 Not signed off (file evidence, headroom); round 2 Signed off, no gaps | 2/2 rounds | |
| 15 | general-purpose (re-read) | serial | none; 6 fixes applied in `c824afd` | 75/81 passed, 6 wording defects; independent read of the last 8 lines passed | 1/1 | Closes D1 |
| 13b | main session | serial | `97885c7` `stateless-state-machines` title renamed, outside its batch | Verify pass | n/a | Text from the T4.1 comparator; falls under D1 |

## Tests
| Criterion | Test id | Mode | Owner | Last result |
|---|---|---|---|---|
| AC1 | Whole-layer verify counts | shell | T2, main session | Pass: no over-120, banned-phrase or no-`Use` line |
| AC2 | `claude -p /context`, 1M window | shell | main session | Pass: budget 0.02; 201/201 rows at 0.019, which is 95% of it; `final/runs-head.md`, `final/reads.md` |
| AC3 | `/context` on a 200k model | manual | main session | Not run: `claude-sonnet-5-5` and `claude-haiku-5-5` both report a 1M window on this machine, so no 200k session was reachable |
| AC4 | Whole-layer verify counts | shell | T3, T4, main session | Partly: all 0 except `body > 8000` on 4 skills |
| AC5 | Fence check plus block diff | shell + manual | comparators | Pass: 25 files with `Unverified:` headers; fence check now fails |
| AC6 | Anchor walk | manual | comparators, CP3 | Pass: 341/341 by reading |
| AC7 | `token-survival.ps1` plus reports | shell + manual | comparators, re-read | 317 misses equal the sum of the batch reports; `reread-81/comparison.md` read all 81, 6 fixed; last 8 lines in `final/reads.md` |
| AC8 | `ask-check.ps1` | shell + manual | main session | Pass: 40 hits, 38 allowlisted, 2 resolved, 0 open |
| AC9 | Section walk | manual | comparators, CP3 | Pass: 109 with `## Steps`, 15 pipeline, standard or method |
| AC10 | `run.ps1` fixtures | shell | T5, main session | Pass: 533 total on pwsh and 5.1 |
| AC11 | `run.ps1`, `test_mem.py`, verify | shell | main session | Partly: all pass; `body > 8000` remains on 4 skills |
| AC12 | Docs list | manual | CP3 | Pass; memory note goes in the closure commit |

## Bugs
| ID | Title | Severity | Status |
|---|---|---|---|

## Known limitations
- **Where gaps live:** this framework repo has no feature-root `DEBT.md`; accepted gaps stay here, open work in `.workflow/framework-backlog.md`.
- **200k window:** computed budget about 3.8k tokens after the raise, so most skills would stay name-only there. Not measured: no 200k model is reachable on this machine (AC3).
- **No gate behaviour run:** no baseline scenario proves a gate or process skill still steers correctly after the format change; the comparator checks text only.
- **Drop fix scope:** AC2 holds only on a 1M window with this machine's plugin set; a plugin update can re-break it.
- **Moved code:** adapt files stay uncompiled, because this repo has no Unity project.
- **Bodies past 8,000 chars (for GD acceptance at CP4):** `iap-server-receipt-ledger` 8,350 and `firebase-unity-sdk` 8,069: required checks restored, covered by the spec amendment. Outside the amendment: `server-authoritative-validation` 8,035 (a `## Scripts` entry) and `feature` 14,317 (titles and splits; within the about 20,000 chars the installed CLI keeps at compaction, by reading its code).
- **Fix re-read:** the 81 comparator fixes were re-read after commit, not before (D1 closed by `reread-81`). No batch holds its own pass verdict.
- **Last verifier fix:** `465c7e3` used up the 4/4 attempts and no reviewer read it; mutant runs prove its boundary.
- **`verify.ps1` edges now the promotion ships:** a whole-layer run skips every `.md` under a parent folder named `scripts` or `assets`. In the backlog.
- **Budget cost:** Skills went from 9.9k to 18k tokens per session, about 8.1k more; the GD was told about 7.5k.
- **Other commits on this branch:** `2ffcce1`, `6bd65f4`, `e791c78`, `ff26bda` (Game Engineer output style, README) are the GD's own work, made on purpose (GD's words: "cái đấy tôi chủ động làm"). They go into `develop` with the merge and push; no CP4 question needed.

> Evidence under `.workflow/evidence/skill-template-migration/` was removed on 2026-11-04 as unused; read it from git history at `9bdaa30`.

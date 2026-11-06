# Game production agents

- Status: Closed
- CP: CP4 — closed 2026-11-06; next step: git-expert merges feature/game-production-agent into develop (local, no push)
- Session: 6a67d61d-3392-4299-96b5-9196129da6d6 · 2026-11-05
- Size: L · Risk flag: no
- Rounds: review 0/3 (+1 extra round) · QA 0/2 (hook ledger: 1) · rework 1/8 (only events the hook cannot see: workflow review rounds, CP3 drift, a main-GD-reported reopen, CP4 fix-gaps rework). Hook ledger: review 3, rework 3
- Profile: n/a — framework repo; `CLAUDE.md` is the per-project template
- Feature root: `.claude/`
- Branch: feature/game-production-agent · Base: develop @ e4a7fae
- Assemblies: none
- Build mode: serial
- Worktrees: none

## Request (verbatim)
> tôi muốn thảo luận với bạn về đội agent, hiện tại, đang chỉ tập trung vào phần đội ngũ kỹ sư nhưng chưa có đội ngũ GD, PO và MO cùng thảo luận với người dùng để có hướng đi phát triển tốt hơn về game design, product quality. Đồng thời, cố vấn tôi workflow làm việc với đội PO, GD và MO đấy. Mục tiêu là cải thiện, cố vấn về chất lượng sản phẩm, tính năng, độ hoàn thiện, và khả năng kiếm tiền. Sau khi có các workflow, tùy vào công việc sẽ trigger workflow riêng biệt cho sản phẩm, monet và quá trình thực hiện sản phẩm

## Main GD decisions
- 2026-11-05 CP1: n/a (direction given in discussion): all three areas in scope, not a single-workflow trial.
- 2026-11-05 Authority: advisory only. Notes appear at CP2 and CP4; nothing blocks.
- 2026-11-05 Discussion form: independent reads, main session merges and shows conflicts, follow-ups to the relevant agent.
- 2026-11-05 Test game: one with real players and data, not `aga001-night99`. Name and data channel supplied later.
- 2026-11-05 Naming: the human decision-maker is `main GD`; bare `GD` retired for that role. Vietnamese replies keep Bạn/Tôi.
- 2026-11-05 Storage: advice goes into memory, off git, in SQLite, queried when needed, under Zero-Mem principles.
- 2026-11-05 MO scope: monetisation only; user acquisition and marketing are out.
- 2026-11-05 CP2: approved via the plan (`C:\Users\Admin\.claude\plans\curious-jumping-pine.md`), including its "Limits to accept at CP2". The design document is the spec. `technical-architect` Size and Spec modes were not dispatched: the main session wrote the spec and a builder-check agent read it. Lanes: serial only.

- 2026-11-06 Gate offer: review yes, QA yes.
- 2026-11-06 extra round: review +1. Main GD's order after review round 3 hit the cap with one High in check_pack.py. Stated cost: one narrow code-reviewer and one narrow security-reviewer dispatch on the round 3 fix diff only.
- 2026-11-06 Review round 4 (extra): code-reviewer Approve, security-reviewer Clear. Six Lows fixed once with no re-review, per `/review`; value misses recorded under Known limitations.
- 2026-11-06 CP3: approved with drift D1 (usefulness step missing in `/design` and `/monet`) sent back, +1 rework; 16 drifts accepted as built and written into the spec.
- 2026-11-06 AC10 deferred to the pilot (main GD): the three workflows' orchestration (merge, conflict display, 2-round follow-up cap, unlabelled-return resend, the usefulness rule, the /monet no-pack branch) is read, never run, until the test game and data pack arrive. qa-lead may sign AC1-AC9.
- 2026-11-06 QA: qa-lead Not signed off in round 1 (G1: no executor run at a327b4b), Signed off in round 2 for AC1-AC9; AC10 waived; BUG-0009..0012 Complete.
- 2026-11-06 CP4: closed, all recorded gaps accepted and mirrored into `.workflow/DEBT.md`. Merge into develop via git-expert, no push. Commit the design spec and the main-gd-term memory note.
- 2026-11-06 Accepted: the rule that an adviser reads only the data pack its brief names, after `check_pack.py` passed it, is written but not enforced by a tool. Stated cost: an unchecked pack placed in `.memory/advisory/data/` by the main GD can be read; advisers have no shell, so they cannot write or send it anywhere.

## Spec
`docs/superpowers/specs/2026-11-05-product-advisory-team-design.md`

### Acceptance criteria
- AC1 Rename: role term is `main GD` across `.claude/`, `CLAUDE.md`, `README.md`, `framework-docs/`; old `## GD decisions` still counted by `round-cap.ps1`; hook and bug tests green.
- AC2 Store: `adv.py` stores, queries, decides and marks findings; refuses to write when its path is not git-ignored; refuses secret shapes.
- AC3 Leak: adviser briefs, returns and marked assistant text leave no figure in a captured trace; an unterminated marker strips; `pre-commit` blocks a staged `measured` label or an advisory marker.
- AC4 Not blocked: an adviser dispatch passes on a past-cap feature and with a corrupt ledger; `code-reviewer` is still blocked.
- AC5 Simulator: golden output; weakest-label propagation; `proposed` excluded.
- AC6 Data pack: rejects a PII header; accepts an aggregated pack.
- AC7 Layer: 3 agents, 4 method and protocol skills, 3 workflow skills; `/verify-layer` passes.
- AC8 Pipeline: routing rows, `core.md` exception, `/plan-game`, `/feature`, `/new-project`, `CLAUDE.md` template updated.
- AC9 Spike: `SendMessage` continuation, SubagentStop firing and transcript shape recorded; the follow-up default follows the result.
- AC10 Pilot: each workflow run once on the test game; main GD marks findings.

## Log
| # | Agent | Lane | Changed | Verified | Attempts n/N | Limitations / Needs main GD |
|---|---|---|---|---|---|---|
| 1 | main session (T1 rename) | serial | 92 files, role term and machine tokens; `round-cap.ps1` reads both headings | Hooks 1340 PASS; `test_bugs.py` 269 OK after 2 fixture fixes; `test_mem.py` OK; verify OK | 1/4 | Commit made on the feature branch |
| 2 | main session (T2-T4 store, capture, guards) | serial | `adv.py`, `advisory-capture.ps1`, `mem.py` scrub, `pre-commit.ps1`, `round-cap.ps1` exemption, ignore rules | See `Tests` | 2/4 | Attempt 1: suite failed 5 capture checks, the test helper's project dir |
| 3 | main session + spike (T5) | serial | none | Live: `general-purpose` with a thread marker, `SendMessage` follow-up kept context, SubagentStop fired on it, trace held no return text. Found a duplicate store of one return; ingest now idempotent. Live `product-owner` return stored, `rounds` 0, `adv lint` OK | 1/4 | Spike rows deleted; smoke row still in the local store |
| 4 | main session (T6-T8) | serial | 3 agents, 7 skills, `simulate.py`, `check_pack.py`, `routing.md`, `core.md`, `/feature`, `/plan-game`, `/new-project`, `CLAUDE.md`, `README.md` | See `Tests`; verify OK | 1/4 | Workflows themselves unrun: AC10 |
| 5 | main session (review round 1 fixes) | serial | 19 files, `08731dc` | Suites green; round 2 failed: check_pack repeated cause | 1/1 | Stop rule 1 |
| 6 | main session (review round 2 fixes) | serial | `734bbf1`, check_pack default-deny redesign | Suites green; round 3: security Clear, code High | 1/1 | Stop rule 2 |
| 7 | main session (review round 3 fixes) | serial | `3f38e29`, tests first (21 failed on 734bbf1) | Round 4 extra: Approve + Clear | 1/1 | Extra round on the main GD's order |
| 8 | main session (round 4 Lows, CP3 D1) | serial | check_pack non-ASCII words, adv git env, `/design`/`/monet` usefulness, spec catch-up | New tests failed on 3f38e29, pass now | 1/1 | Lows not re-reviewed by rule |

## Tests
| Criterion | Test id | Mode | Owner | Last result |
|---|---|---|---|---|
| AC1 | `run.ps1` heading and BUG-0012 cases; `test_bugs.py` TestGdAttribution(+Edge); bare-GD grep; verify retired-route rule | automated | qa-automation-engineer | run.ps1 1461/0 x2, test_bugs 275 OK x2, verify OK x2 at a327b4b (attempt-4) |
| AC2 | `test_adv.py` (AdvEdgeTest) | automated | qa-automation-engineer | 42 OK x2 at a327b4b (attempt-4) |
| AC3 | `test_mem.py` (AdvisoryScrubEdgeTest); `run.ps1` pre-commit advisory cases | automated | qa-automation-engineer | test_mem 63 OK x2, run.ps1 1461/0 x2 at a327b4b (attempt-4) |
| AC4 | `run.ps1` round-cap adviser cases | automated | qa-automation-engineer | run.ps1 1461/0 x2 at a327b4b (attempt-4) |
| AC5 | `test_simulate.py` (SimulateEdgeTest); golden SHA-256 | automated | qa-automation-engineer | 31 OK x2 at a327b4b (attempt-4) |
| AC6 | `test_check_pack.py` (PackEdgeTest) | automated | qa-automation-engineer | 48 OK x2 at a327b4b (attempt-4) |
| AC7 | `verify.ps1` base vs HEAD; agent and skill counts | automated | qa-automation-engineer | OK, 21 warnings, x2 at a327b4b; base comparison at e4a7fae (attempt-1) |
| AC8 | C8 path:line greps | manual | qa-automation-engineer, qa-lead | supported (qa-lead re-checked at a327b4b) |
| AC9 | `.workflow/evidence/game-production-agent/c9-live-report.md` | manual (live) | main session | supported |
| AC10 | pilot on the test game | manual | main GD | deferred to the pilot (main GD, 2026-11-06) |

## Bugs
| ID | Title | Priority |
|---|---|---|
| BUG-0009 | Trace scrub keeps advisory text when marker lines end in CRLF | Medium |
| BUG-0010 | adv.py ingest crashes on JSON that is not an object | Low |
| BUG-0011 | Five Routed to fields still name gd after the main GD rename | Low |
| BUG-0012 | Round cap reads only the first decisions heading in a feature file | Low |

## Known limitations
- `check_pack.py` fails closed on purpose. False positives: `device_model`, `user_type`, `ip_share_percent`, `playerbase`, `build_hash`, glued words like `buildid`, non-English headers; AdMob or MAX ad unit ids in cells, totals with 15 or more integer digits (VND, micros), campaign names over 80 characters. Fix: rename the column or add the word in a reviewed change. Also: `install_date`, `session_count`, `user_count` (rename to `cohort_date`, `sessions`, `users`); headers made only of numbers, or with more than 2 number groups or 4 bare digits (`2026`, `2026-10-01`, `level_1_2_3`); a value with a leading `+` is text, so a count column holding `+5` fails; day-first or month-first dates with a leading 0 (`05 10 2026`, `05-10-2026`, `01102026`) read as phone numbers: write dates as `yyyy-mm-dd` or `yyyymmdd`.
- `check_pack.py` misses: plain-letter player names under an allowed header, small sequential numeric user ids, GA4 web `user_pseudo_id` values under an allowed header; no minimum group size, so small counts can still re-identify a player. `manifest.md` is checked for presence only. Also missed: 9-14 digit numeric ids or phones without `+` in an all-numeric column (`84912345678`; 15 or more digits are caught); national-format phones with no leading 0 (`415 555 2671`), dot-separated (`0912.345.678`, `+84.912.345.678`) or grouped in pairs (`06 12 34 56 78`); a number in scientific notation in a numeric column (`8.4912345678e10`), since only the integer part is length-checked.
- The advisory DB is per-machine: not in git, not shared with teammates, lost with the disk unless `adv export` runs.
- A figure the main GD types or pastes in chat is captured into traces; `mem.py` cannot tell it from other text.
- Markers rely on the main session; a forgotten marker puts text in a trace, and `pre-commit` catches only labelled figures.
- AC10 deferred to the pilot by the main GD (2026-11-06); the workflows' orchestration (merge, conflicts, follow-up cap, resend, usefulness rule, /monet no-pack branch) has never run. AC10 waits for the test game and data pack; `/monet` stays unvalidated on revenue until then.
- QA observations not settled by the spec, left as is: marker and label variants (`<!--advisory:begin-->` without spaces, `(open bracket)Measured:`, nested blocks: text after the first end stays) are not stripped by the trace scrub; pre-commit blocks a staged deletion of a store file; `adv export` silently replaces another valid SQLite file at its target; `simulate.py` accepts inverted bands without a warning; `check_pack.py` passes zero-width characters and NUL, and echoes file names (attempt-1 O1-O6).
- Post-QA fixes BUG-0009..0012 were read for correctness by code-reviewer in test-code round 2 (Approve), not in a submission review round.
- An adviser reading only the pack its brief names is a written rule, not enforced by a tool (main GD accepted 2026-11-06).
- Token cost per run not measured: three Opus reads per `/product-review`, up to three per CP note.

- Stop rule: check_pack.py (same cause, review rounds 1 and 2) root-caused 2026-11-06 by technical-architect: default-allow design over an open set of identifiers; redesigned to default-deny · extra dispatch: used (main session, the redesign)
- Stop rule: check_pack.py/adv.py (review cap 3/3) root-caused 2026-11-06 by technical-architect: allow paths defined by patterns wider than their admitted set (RX_NUMBER sign, \d{1,4} header words, git message text); fixed by narrowing each to a finite or structural set · extra dispatch: used (main session)

<!-- Label syntax is written as "(open bracket)measured:" here: pre-commit blocks the literal label outside the framework's own files. -->

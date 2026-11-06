# QA report: game-production-agent, attempt 1 (cases C1-C8)

Author: qa-automation-engineer. Plan: qa-lead (C1-C8). Spec: `docs/superpowers/specs/2026-11-05-product-advisory-team-design.md`.

## Run record

| Item | Value |
|---|---|
| `git rev-parse HEAD` | `bbeb7e1788cda001ef95336596c29c12bb2d4ea9` (before the runs and after them) |
| `git status --porcelain` before | `?? .memory/notes/feedback/main-gd-term.md`, `?? .workflow/features/game-production-agent.md`, `?? docs/`. One path outside `docs/` and the feature file: `.memory/notes/feedback/main-gd-term.md` (untracked, not touched by this run) |
| `git status --porcelain` after | the six test files below show ` M`; `.workflow/evidence/game-production-agent/attempt-1/qa-report.md` is new; the three paths above are unchanged |
| Python | 3.14.7 (the only interpreter on the machine; the framework's stated floor is 3.10, not exercised) |
| PowerShell | Windows PowerShell 5.1.26100.9711 runs `run.ps1`; pwsh 7.6.9 is the tool shell and runs `verify.ps1` |
| Review status of the code under test | reviewed (code-reviewer Approve, security-reviewer Clear, per the brief); a correctness gate stands behind these results |
| Editor / device / Unity | none: framework repo. Code coverage: not applicable (no Unity project, no coverage package) |
| Real `.memory/advisory/` | not touched: every `adv.py` test uses a `tempfile` root; `git status` shows no change under `.memory/` |

## Results by suite (every suite run twice on the final files; a skip or expected failure is not a pass)

| Suite | Command | Before this run (HEAD) | After: run 1 | After: run 2 |
|---|---|---|---|---|
| `test_adv.py` | `python -I .claude/skills/mem/scripts/test_adv.py` | 25 ran, OK | 41 ran, OK, 1 expected failure | 41 ran, OK, 1 expected failure |
| `test_mem.py` | `python -I .claude/skills/mem/scripts/test_mem.py` | 50 ran, OK | 63 ran, OK, 2 expected failures | 63 ran, OK, 2 expected failures |
| `test_simulate.py` | `python -I .claude/skills/monetization-modeling/scripts/test_simulate.py` | 16 ran, OK | 31 ran, OK | 31 ran, OK |
| `test_check_pack.py` | `python -I .claude/skills/advisory-protocol/scripts/test_check_pack.py` | 27 ran, OK | 48 ran, OK | 48 ran, OK |
| `test_bugs.py` | `python -I .claude/skills/bugs/scripts/test_bugs.py` | 269 collected at HEAD | 275 ran, OK (139.7 s) | 275 ran, OK (104.2 s) |
| `run.ps1` | `powershell -NoProfile -ExecutionPolicy Bypass -File .claude\hooks\tests\run.ps1` | 1378 PASS, 0 FAIL (ran before any edit, 12 min 25 s) | 1455 PASS, 0 FAIL, 17 `OBS` lines (13 min 45 s), exit 0 | 1455 PASS, 0 FAIL, 17 `OBS` lines (14 min 26 s), exit 0 |
| `verify.ps1` | `powershell -NoProfile -ExecutionPolicy Bypass -File .claude\skills\verify-layer\scripts\verify.ps1` | see C7 | exit 0, 21 warnings | exit 0, 21 warnings |

"Before" for `test_bugs.py`, `test_mem.py` and `test_simulate.py` is the count `unittest` collects from the `HEAD` copy; the others were run on `HEAD`. Skips: 0 in every suite. Expected failures are listed under Findings F1 and F2: each is a named defect, kept out of the pass count.

## Tests added (all additions, no existing line changed or removed: `git diff --numstat` shows 0 deleted lines in each file)

| File | Behaviour asserted | Case |
|---|---|---|
| `.claude/skills/mem/scripts/test_adv.py` `AdvEdgeTest` (+16, 1 expected failure) | each of 5 secret shapes refused in a return, a brief and a decision note, nothing stored, value never echoed; FTS metacharacters and quotes never crash or leak SQL; a query with no words is refused; `get`/`decide`/`useful` on a missing id refused and nothing changed; re-deciding keeps one valid decision and loses no finding; a wrong decider cannot overwrite; bad decision/mark is a parser refusal; `rounds` on an unknown thread counts nothing; export over an existing copy keeps one valid copy; export onto a non-database file or a folder is refused and leaves it | C1 |
| `.claude/skills/mem/scripts/test_mem.py` `AdvisoryScrubEdgeTest` (+13, 2 expected failures) | two closed blocks in one turn; begin-begin-end; stray end; indented and trailing-blank markers; a list-of-blocks adviser return; a marked block in a non-adviser list result and in a list answer; a marker in an ordinary tool result never captured; string-form assistant text never captured; the exact label replaces its whole line; no figure in any byte under `.memory/` after a fixture holding one figure in every capture path | C2 |
| `.claude/hooks/tests/run.ps1` pre-commit block | near names of the 9 exempt files are scanned for a label and for a marker line (10 variants x 2); the 9 exact exempt files pass; 4 case variants scanned in a fresh repo; CRLF and indented marker lines blocked; a nested data pack path blocked; rename out of and into the store blocked; fixture repo starts clean | C2g |
| `run.ps1` round-cap block | 13 non-adviser names and an empty name stay capped; adviser names plus an `Advisory-Thread:` line in a gate brief do not exempt 3 gates; an adviser with no `Feature:` line, an empty brief, or a non-feature `Feature:` line passes; a Workflow launch past the cap is blocked as an object and as a JSON string, even carrying an adviser `subagent_type`; a Workflow launch under the cap passes | C3 |
| `run.ps1` heading block | both headings, extra round under the first of two, either one: honored; no extra round anywhere: refused; both with an extra round: at the cap passes, past it blocks (no double capacity), both orders; CRLF files with either heading; an unrelated heading is not a main GD record | C6 |
| `.claude/skills/monetization-modeling/scripts/test_simulate.py` `SimulateEdgeTest` (+15) | CLI bytes identical across 5 runs and 4 hash seeds; D30/D90 extrapolation flag at last-day -1/equal/+1; retention 1.0 accepted, 0 refused; zero activity gives zero; NaN, +-inf, negative refused in all 6 numeric slots and in retention; NaN/Infinity in a file exits 2 with no stdout; bool/string/None/list refused; proposed beside measured keeps `measured` and names the input; proposed beside assumption keeps `assumption`; a proposed curve is named; a `²` day key exits 2; wrong-shape input exits 2 | C4 |
| `.claude/skills/advisory-protocol/scripts/test_check_pack.py` `PackEdgeTest` (+21) | the `user_id` literal; quoted comma, quote and newline cells; CRLF and CR-only files; non-UTF-8 and UTF-16 bytes; zero-width and full-width headers rejected; full-width digit runs rejected without echo; UUID/email/IPv4 under 5 allowed headers; mixed-case headers both ways; 100k rows, 3 MB cell/header, 20k columns each in bounded time; CLI stdout and stderr hold neither the unknown word nor the value | C5 |
| `.claude/skills/bugs/scripts/test_bugs.py` `TestGdAttributionEdge` (+6) | `--by` of 8 retired or near names refused on `set-status` and `delete`, journal bytes unchanged; no `--by` refused; exactly `main GD` accepted on every main-GD-only move; an old journal row `by: GD` replays, stays verbatim, `doctor` clean; a bug parked by an old row moves on only by `main GD` | C6 |

New test code goes to `code-reviewer` in `Mode: test-code` before these results count.

## Findings (defects against a requirement the spec settles)

### F1 Markers with Windows line endings do not strip (Medium, AC3, owner: author of `mem.py`)
- **Location:** `.claude/skills/mem/scripts/mem.py:698` `RX_ADVISORY_BLOCK`.
- **Expected:** spec line 78 and AC3: assistant text between `<!-- advisory:begin -->` and `<!-- advisory:end -->` leaves no figure in a committed trace; an unterminated begin strips to the end of the turn.
- **Actual:** the regex ends each marker in `[ \t]*$` under `(?m)`; `$` stops before `\n` only, so a `\r` after the marker stops the match. The figure stays in the trace. `pre-commit` does not catch it either: the JSONL line holds the marker mid-line (see the `OBS` line "a trace line holding a CRLF-marked block", result 0).
- **Evidence:** `test_mem.py` `test_markers_with_windows_line_endings_still_strip` and `test_an_unterminated_begin_with_windows_line_endings_still_strips`, both `expectedFailure`.
- **Repro:** capture a transcript whose assistant text is `"Before\r\n<!-- advisory:begin -->\r\nARPDAU 0.083\r\n<!-- advisory:end -->\r\nAfter"`; the trace text is returned unchanged, figure included. The LF form of the same text strips.
- **Condition:** needs CRLF in assistant text (a pasted Windows file). Rare, hence Medium, not High.
- **Not a fix here:** the tests flip to "unexpected success" when `mem.py` is fixed; remove `@unittest.expectedFailure` then.

### F2 `adv.py ingest` of JSON that is not an object exits with a traceback (Low, AC2, owner: author of `adv.py`)
- **Location:** `.claude/skills/mem/scripts/adv.py:169` `data.get("agent")`.
- **Expected:** every bad input ends as `refused: ...` and exit 2 (`main` does this for bad JSON, `adv.py:394`).
- **Actual:** `[1, 2]`, `"text"`, `7`, `null` and `{"agent": "x", "return": 7}` raise `AttributeError`; exit 1 with a traceback.
- **Repro:** `echo [1,2] | python -I adv.py --root <ignored-repo> ingest`.
- **Evidence:** `test_adv.py` `test_ingest_of_json_that_is_not_an_object_is_refused_not_a_traceback`, `expectedFailure`.
- **Why Low:** the only producer is `advisory-capture.ps1`, which always sends an object, and the hook never blocks.

### F3 Five `Routed to: gd` output fields were not renamed (Low, AC1, owner: main session, framework text)
- **Locations:** `.claude/skills/ci-pipeline-failure-triage/SKILL.md:76`, `device-test-walkthrough/SKILL.md:61`, `git-safety-anchor/SKILL.md:68` and `:74`, `playtest-scenario-execution/SKILL.md:58`.
- **Expected:** AC1 and the 2026-11-05 naming decision: machine tokens use `main-gd` (as `Next: main-gd` does in `cto.md:58`, `qa-lead.md:50`, `agent-protocol/SKILL.md:55`).
- **Actual:** the lower-case bare token `gd` remains in those five lines. Nothing parses `Routed to:` (grep of `.claude/hooks` and the scripts finds no reader), so it is naming drift, not a break.

## Observations (the spec does not settle these; reported as seen, not asserted)

| # | Where | Observed |
|---|---|---|
| O1 | `mem.py` scrub | The label is matched as the exact text `(open bracket)measured:`. Probed: `(open bracket)Measured:`, `(open bracket)MEASURED:`, `(open bracket)measured :` and bare `measured:` all stay in a trace (`(open bracket) measured:` and `(measured:` follow from the same regex, not probed). Markers: `<!-- ADVISORY:BEGIN -->` and `<!--advisory:begin-->` do not strip. Nesting depth is not tracked: `begin, A, begin, B, end, C, end` strips A and B, keeps C and the second `end`. A stray `end` with no `begin` changes nothing. Text typed by the main GD (role `user`) is kept, as the known limitation says |
| O2 | `pre-commit` labels | `-match` is case-insensitive, so `(open bracket)Measured:` and `(open bracket)MEASURED:` are blocked; `(open bracket)measured :`, `(open bracket) measured:`, `(measured:`, bare `measured:` pass. Marker lines: `<!-- ADVISORY:BEGIN -->` blocked; `<!--advisory:begin-->`, `<!--  advisory:begin  -->` and a marker followed by text pass |
| O3 | `pre-commit` store rule | A staged deletion of a committed `.memory/advisory/` file is blocked (`pre-commit.ps1:74` has no deletion exemption), while `Find-ForbiddenFiles` allows deletions "as how such a file leaves the tree". A rename out of the store is blocked for the same reason. A pure rename of an exempt framework file holding the label to a scanned path passes (a rename adds no diff line) |
| O4 | `adv.py` | A second `decide` on a decided finding replaces the first (status, note, time). `decide` on a fresh root creates an empty store and then refuses. `export` onto another valid SQLite file replaces its whole content silently (a table `keepme` was gone afterwards); onto a non-database file or a folder it refuses and leaves it. `rounds` on an unknown thread prints nothing and exits 0 (a printed `0` only for a thread with one return) |
| O5 | `simulate.py` | Bands in inverted order are accepted without a warning: low `arpu_d30` 1.925674, base 0.499249, high 0.178303. Duplicate day keys `"7"` and `"007"` both map to day 7, the later wins silently. An extra band key (`mid`) is ignored |
| O6 | `check_pack.py` | A header made only of vocabulary words is echoed in the problem line, including a person word (`'user_id'`; `user<ZWSP>id` as its escaped repr): by design, the docstring promises no unknown word and no value. A zero-width character inside a benign header (`cohort<ZWSP>_date`) passes. Full-width look-alikes in cells pass unless they form a run of 9 or more digits: a full-width `@` address and grouped full-width digits pass. A NUL byte in a cell passes. File names are echoed in problem lines, including for a refused non-CSV file (`alice@example.com.json` printed whole). An IPv4 under a `version` or `build` header passes by design. A field over the csv limit fails closed as `unreadable (Error)` |
| O7 | `round-cap.ps1` headings | Only the first of `## GD decisions` and `## Main GD decisions` is read (`round-cap.ps1:163`). An extra round recorded only under the second heading of a file holding both is not honored, so a legitimate cap raise is refused (fails safe). Both orders give 2. `### Main GD decisions` and `## main gd decisions` are honored |

## Case results

### C1 `adv.py` (AC2)
- `test_adv.py` ran twice, Python 3.14.7: 41 tests, OK, 1 expected failure (F2), both runs.
- (a) AWS-style key, PEM private-key header, JWT, bearer token and `password=` are each refused in the return, the brief and a decision note; the store file is never created; the refusal text does not echo the value. All five built at runtime, no secret-shaped literal in the file.
- (b) 15 metacharacter queries (`"`, `""`, `*`, `NEAR`, `NEAR(`, `interstitial)`, `"interstitial`, `interstitial*`, `a OR b AND NOT c`, `title:interstitial`, `interstitial -level`, an injection string, `^interstitial`, `{x}`, `\`): exit 0 or 2, no traceback, no SQL or FTS error text, `lint` still clean, `interstitial*` still finds the finding. Queries made only of punctuation are refused (exit 2).
- (c) `get`, `decide` and `useful` on a missing store, return, finding or malformed id: exit 2, nothing changed. `useful` with an invalid mark (`maybe`, `1`, empty) and `decide` with an unknown decision: argparse exit 2, finding unchanged (`status: open`, `useful=None`). Re-decide: see O4.
- (d) `rounds` on an unknown thread: exit 0, empty output, with and without a store (O4).
- (e) `export` twice to one target: one valid copy (2 findings, 1 return, `integrity_check` ok).

### C2 leak (AC3)
- `test_mem.py` ran twice: 63 tests, OK, 2 expected failures (F1). The `run.ps1` pre-commit block is in the `run.ps1` rows above.
- (a) begin-begin-end: nothing from the first begin to the first end survives. (b) a stray end marker neither crashes nor swallows the turn. (c) two closed blocks: two pointers, the text between stays. (d) CRLF: F1. (e) a list-of-blocks adviser return leaves one pointer per turn; a list-form result of a non-adviser agent and a list-form answer strip their marked block; a marker inside an ordinary tool result is never captured; string-form assistant content is never captured. (f) label variants: O1, O2. (g) 10 near names of exempt files (`SKILL.md.bak`, `references/SKILL.md`, `Assets/.claude/...`, `mem2.py`, `mem.py.orig`, `schema.md.txt`, `common.ps1.bak`, `run.ps1.txt`, `x/.claude/hooks/tests/run.ps1`, `verify.ps1.old`) are blocked for a label and for a marker line; 9 exact exempt files pass; 4 case variants (`SKILL.MD`, `skill.md`, `Mem.py`, `Common.ps1`) are blocked, in a fresh repo (a first draft that reused the repo where `SKILL.md` had been on disk got 0, because Windows hands a case variant the existing file's case: a fixture effect, not a hook fault). Rename into the store and out of it: blocked; deletion and exempt-file rename: O3.
- **Trace captured from a fixture holding a known figure, then grep of the captured file** (not only an assertion). Fixture transcript: 7 entries, the figure `ARPDAU 0.0831` and the label `D7 11.27% (open bracket)measured: ...]` in an adviser brief, an adviser return, a marked block, a labelled line, a labelled answer and an unterminated block. A grep of the fixture transcript finds the figure 6 times (so the grep works). After `mem.py capture`:

  | File under `.memory/` | `0.0831` | `11.27` | `(open bracket)measured:` |
  |---|---|---|---|
  | `traces/2026/10/2026-10-28-fixture1.jsonl` (598 bytes, 5 turns) | 0 | 0 | 0 |
  | `.state/capture/fixture1.json` (154 bytes) | 0 | 0 | 0 |

  `Select-String` over the captured trace for `0\.0831`, `11\.27`, `(open bracket)measured:`: 0 matches. The five turns read: brief `[advisory: adv q]`; agent `[advisory: adv q]`; assistant `Before. / [advisory: adv q] / After. / Plain line. / [advisory: adv q]`; answer `[advisory: adv q]`; assistant `Unterminated. / [advisory: adv q]`. The same check is a permanent test (`test_no_figure_survives_anywhere_under_the_memory_folder`). The fixture and trace lived in a temp folder and are not kept: a trace is local evidence, and this one holds only pointers.

### C3 round-cap advisers (AC4)
- `run.ps1` 2 runs: see the table. (a) 13 near or wrong-case names and an empty name stay capped (`product-owner-x`, `x-product-owner`, trailing and leading space, `product-owner2`, `product_owner`, `PRODUCT-OWNER`, `game-designer-v2`, `monetization-designer-`, `monetization_designer`, `product-owner,game-designer`, `critic`, `researcher`). (b) adviser names, a `Subagent:` line and an `Advisory-Thread:` line inside a `code-reviewer`, `security-reviewer` or `qa-lead` brief do not exempt it (exit 2 each). (c) an adviser passes with a brief holding no `Feature:` line, an empty brief, and a `Feature: none` line; the same no-marker brief to `code-reviewer` is capped through the path it names (exit 2). (d) a `Workflow` launch past the cap is blocked, with args as an object and as a JSON string, and also when its `tool_input` carries an adviser `subagent_type` (the exemption skips `Workflow`, `round-cap.ps1:32`); under the cap it passes.

### C4 simulator (AC5)
- `test_simulate.py` ran twice: 31 tests, OK, both runs.
- **Golden output byte for byte:** `simulate.py` on one fixture (`test_simulate.spec()` as JSON), 3 runs plus 1 run with `PYTHONHASHSEED=7`: every output is 3080 bytes with SHA-256 `26300937CC607A04D75BD94A2B96BB335048DD4B8A329B7D610C6485FB624F21`. The value-level golden test (`test_golden_output`) passes unchanged in all runs.
- (a) D30 extrapolation flag: last supplied day 28 flagged, 29 not, 30 not; D90: 88 flagged, 89 not, 90 not. The `extrapolated_past_day` field and the `assumption` label switch together. (b) retention 1.0 accepted (30.0 active days); retention 0 refused; activity 0 gives ARPDAU 0.0 and ARPU 0.0, label `measured`. (c) NaN, +inf, -inf, -0.5, -1 refused in all six numeric slots and, for retention, together with 1.0000001 and -0.1; a file holding `NaN`, `Infinity`, `-Infinity` or `-1` exits 2 with empty stdout. (d) inverted bands: O5. (e) a proposed `ecpm` beside measured inputs keeps `measured` and names `ads.x.ecpm` on ARPDAU and ARPU, and names nothing on the economy figure; beside an `assumption` it keeps `assumption` and still names it.

### C5 data pack (AC6)
- `test_check_pack.py` ran twice: 48 tests, OK, both runs.
- The `user_id` header is a literal test: `test_check_pack.py:17` (`FAIL_IDENTIFIES`), `:91` (all four separators), `:210`-`:211` (new test pins the exact problem text `x.csv: column 1 ('user_id') identifies a person or device`).
- (a) quoted cell with a comma, a quote or a newline: one cell. (b) CRLF and CR-only files read; a bad header and an email still fail under CRLF. (c) `\xff\xfe`, `\xc3(` and UTF-16 bytes: `unreadable (UnicodeDecodeError)`, no byte echoed. (d) `use<ZWSP>r_id`, `u<ZWJ>ser_id`, `us<BOM>er_id`, `user<ZWSP>id`, full-width `user_id`, full-width `USER`, `user<U+3000>id` all rejected; the full-width and split ones with no echo; a 10-digit full-width phone is a "long digit run" in a text column and in a numeric one, without echo; a 15-digit full-width number is rejected. (e) UUID, email and IPv4 fail under `segment`, `campaign`, `placement`, `country_code`, `event_name`, no value echoed; an IPv4 under `app_version` passes by design (O6). (f) `UsEr_Id`, `USER_ID`, `User_ID`, `pLaYeR_iD`, `DEVICE_ID`, `E-Mail` fail; `Cohort_DATE`, `D1_Retention`, `ARPDAU`, `Revenue_Per_User`, `eCPM_USD` pass. (g) 100,000 rows: 1.4 s in the probe (test bound 30 s); a 3 MB cell and a 3 MB header: `unreadable (Error)`, fail closed; 20,000 columns: 0.8 s. (h) CLI run on a pack with header `zebrafoo` and cell `a.b.secret@example.com`: exit 1, stdout `FAIL x.csv: column 1 uses a word outside the vocabulary; ...`, `FAIL x.csv: column 2 ('segment') holds an email`, `data pack: 2 problem(s)`; stderr 0 bytes; neither `zebrafoo`, `secret` nor `example` appears in either stream. Every `ID_VALUES` entry was also checked against captured stdout and stderr.

### C6 rename (AC1)
- `run.ps1` heading cases and `test_bugs.py`: 275 tests OK twice, including the 3 existing `TestGdAttribution` tests and 6 new ones.
- Feature file holding both headings: an extra round under the first heading, either one, is honored; with no extra round under either the raised cap is refused; with both headings each holding an extra round, `review 5/5` still dispatches and `review 6/5` blocks in both orders, so the second heading adds no capacity (no double count). CRLF files with either heading are honored. An extra round only under the second heading: O7.
- `bugs.py`: `--by` of `GD`, `gd`, `Main GD`, `main gd`, `MAIN GD`, `the GD`, `main-GD`, `main  GD` is refused on `set-status` to `Backlog` and on `delete`, journal bytes unchanged; no `--by` is refused; exactly `main GD` is accepted for `Backlog`, back to `Request`, `Won't fix` and `delete`. An old journal row `by: "GD"` (a `status` and an `extra_round` event) replays: status `Backlog`, both events keep `by: GD` verbatim, `doctor` clean, `rebuild` leaves the journal bytes unchanged. Such a bug moves on only with `--by "main GD"`. Non-main-GD writes (`add`, `update`, `round`, `extra-round`, `stop-rule`) take any `--by`: not asserted (the spec gates only the main-GD-only moves).
- **Grep for bare role `GD`** (`git grep -nP '(?<![Mm]ain )(?<![Mm]ain-)\bGD\b' -- .claude CLAUDE.md README.md framework-docs`; `README.md`, `CLAUDE.md` and `framework-docs/` have no hit): 

  | Hit | Classification |
  |---|---|
  | `.claude/hooks/round-cap.ps1:163` `## (?:Main )?GD decisions` | back-compat (old heading) |
  | `.claude/hooks/tests/run.ps1:728` `## GD decisions` | back-compat test of the old heading |
  | `.claude/skills/bugs/scripts/test_bugs.py:478` `("GD", "gd", "G.D.", ...)` | back-compat test: retired names must be refused |
  | `.claude/skills/bugs/scripts/test_bugs.py:2747`-`2796` (this run's new class) | back-compat tests of the retired name and old journal rows |
  | `.claude/skills/mem/scripts/test_adv.py:94` and `:360` `--by GD` | back-compat tests: retired name must be refused |
  | `.claude/skills/ci-pipeline-failure-triage/SKILL.md:76`, `device-test-walkthrough/SKILL.md:61`, `git-safety-anchor/SKILL.md:68` and `:74`, `playtest-scenario-execution/SKILL.md:58` (lower-case `gd`, found by a case-insensitive pass) | not back-compat: F3 |

  Every other hit of the first pattern's wider form was `Main GD`, `main GD` or `main-GD`.

### C7 layer (AC7)
- `verify.ps1`, each tree run twice with identical output: HEAD (a `git archive` of `HEAD` in a scratch folder, no worktree created) exit 0, 21 warnings, 0 failures; base `e4a7fae` (archive) exit 0, 21 warnings, 0 failures; the live working tree (HEAD plus the test edits) exit 0, 21 warnings, output identical to the HEAD archive (0 differing lines). The base run is the baseline.
- Diff of warning kinds, base to HEAD:

  | Kind | Base | HEAD | Cause |
  |---|---|---|---|
  | `description + when_to_use > 120 chars` | none | 4 files | new skills `design`, `monet`, `monetization-modeling`, `product-review` |
  | `list item > 200 chars` | 3 files (`fix`, `release`, `review`) | 8 | the 3, plus new `advisory-protocol`, `monetization-modeling`, `product-review`, and `feature`, `git-recovery` (existing skills that grew) |
  | `body > 8000 chars` | 4 files | 5 | the 4 unchanged, plus `consent-att-init-order` (existing, grew past 8000) |
  | `CLAUDE.md` lines | 38 | 40 | two new rows |
  | always-loaded rules lines | 123 | 130 | routing and core additions |
  | agent files over 50 lines | same 19 files in both | same | the 3 new agents are not on the list |

  All are soft size warnings; none is a failure. Seven of the warnings are new instances of an existing kind; one kind (`description + when_to_use`) is new.
- Counts by glob: agents 26 (base 23; new: `game-designer`, `monetization-designer`, `product-owner`); skill folders 133 (base 126; new 7: `advisory-protocol`, `design`, `game-design-lens`, `monet`, `monetization-modeling`, `product-quality-bar`, `product-review`).
- Each of the 3 agents has `tools: Read, Grep, Glob, WebSearch, WebFetch, Skill` and `model: opus` (`product-owner.md:5`, `game-designer.md:5`, `monetization-designer.md:5`): no shell, no write tool, no `Edit`.

### C8 pipeline (AC8), `path:line`
- Routing rows above `Change to an open feature`: `.claude/rules/routing.md:15` (`/design`), `:16` (`/monet`), `:17` (`/product-review`); the open-feature row is `:18`. Advisers section: `:51`-`:53`.
- `core.md` unranked-options exception, with the `/monet` lean: `.claude/rules/core.md:8` ("except a direction pick (CP1, `/design`) and a `/monet` lean without a data pack: options unranked").
- `/plan-game` 3b: `.claude/skills/plan-game/SKILL.md:24`-`:27` (`product-owner`, `Advisory-Thread: plan-<milestone>`, advice only); offer of `/design` or `/monet` at `:11`.
- `/feature`: step 2 `/design` route `.claude/skills/feature/SKILL.md:46`; `/design` offered as a spec option `:57`; CP2 adviser notes `:62`; CP4 adviser notes `:147` (heading `:146`).
- `/new-project`: `.claude/skills/new-project/SKILL.md:48` (`.gitignore` += `.memory/.index/`, `.memory/.state/`, `.memory/advisory/`). `.gitignore:152`-`:153` and `.xerjignore:10` hold the same rule. This is the only `/new-project` change; the skill adds no step that asks for the two new `CLAUDE.md` rows, so they stay "— or unset" until the main GD fills them (consistent with the spec: unset KPI targets are treated as `assumption`).
- `CLAUDE.md` rows: `KPI targets` `CLAUDE.md:28`, `Data pack` `CLAUDE.md:29`.
- Existence only: these greps show the text is present at those lines; whether the routing behaves as intended is judged by the pilot (AC10), not here.

## Checklist (qa-automation-engineer)
- Review status stated: pass. Reviewed (Approve / Clear per the brief).
- Fails first: n/a. No regression test for a fixed bug was added. The 3 `expectedFailure` tests fail on the current code by design (F1, F2).
- Tests executed: pass. Every run above executed more than zero tests; counts per suite in the table.
- Seed and clock injected: n/a. No Core test. The new tests use temp roots, fixed fixtures and fixed hash seeds; none asserts on the wall clock except the 30 s upper bounds in `PackEdgeTest`.
- Runners agree: n/a. No `dotnet test` mirror in a framework repo.
- Suite extended, not weakened: pass. `git diff --numstat`: 0 lines deleted in all six files.
- Network cases: n/a. Multiplayer is off.
- Code coverage read: n/a. No Unity project, no coverage package; Python line coverage was not requested.

## Not covered (owner)
- Python 3.10-3.13: only 3.14.7 exists here. `mem.py` and the tests use 3.10+ syntax; the floor is untested (owner: `ci-cd-engineer` if a matrix is wanted).
- macOS and Linux: `run.ps1` ran under Windows PowerShell 5.1 only; pwsh 7 ran no hook suite. The case-sensitivity cases ran on a case-insensitive file system (owner: `ci-cd-engineer`).
- Live adviser behaviour: the three advisers, `/design`, `/monet`, `/product-review`, the spike (AC9) and the pilot (AC10) are agent behaviour; none is exercised here (owner: main GD pilot).
- `advisory-capture.ps1` against a real SubagentStop payload, and `SendMessage` continuation: covered by the existing `run.ps1` stop cases and the Log row 3 spike, not re-run live.
- `adv export` into a different machine's repo and concurrent writers to the store: not tested (owner: author of `adv.py`).
- A hostile data pack beyond the listed look-alikes (O6): other Unicode confusables, formulas starting `=` in cells, symlinks inside the pack folder (owner: `security-reviewer`).
- The wording quality of the 3 agents and 7 skills: a review matter (AC8 asserts presence by `path:line` only).
- Token cost per run: not measured (known limitation in the feature file).

## Limitations of this run
- Test code is new and unreviewed: it goes to `code-reviewer` in `Mode: test-code` before these results count.
- The base-to-HEAD `verify.ps1` comparison used `git archive` copies in a scratch folder under the session scratchpad, not a `git worktree`; no `.git` metadata changed.
- `run.ps1` was also started once on the extended file and stopped early after the fixtures showed two mistakes of mine (a case-variant fixture on a case-insensitive disk, and a both-headings case I had asserted that the hook does not satisfy: now O7). Those results are discarded; the two counted runs are the full runs on the final file.

<!-- Label syntax is written as "(open bracket)measured:" here: pre-commit blocks the literal label outside the framework's own files. -->

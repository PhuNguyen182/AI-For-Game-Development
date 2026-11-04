# E3: docs contract and sync (C0 verify, C12, C13)

- Revision: worktree `.claude/worktrees/sqlite-bug-tracker`, branch `feature/sqlite-bug-tracker`, `b6deca7`, tree clean before and after.
- Executor: independent of the T1, T2 and T3 authors. A review gate stands behind this code (Approve, Clear), per the brief.
- Oracle: `.workflow/features/sqlite-bug-tracker.spec.md`, `qa-plan.md`, the rule files, skill text.
- Python 3.14.7, pwsh 7.6.9, Windows PowerShell 5.1.26100.9711. Windows 11. No Python 3.10 run.
- Result: 0 Critical, 0 High, 7 Medium, 7 Low. Criterion 8: parse and grep clean, the walk gives 13 text findings. Criterion 10: the line installs on every target that a sync can run on, with one Medium case where a later project rule overrides it.

## What ran
| Step | How |
|---|---|
| C0 | `pwsh -NoProfile -File <worktree>/.claude/skills/verify-layer/scripts/verify.ps1`, run twice. Static check first: the script has no file write call |
| Temp source | `git -C <worktree> archive -o b6deca7.tar b6deca7`, extracted, `git init`, one commit. 592 files, tar list equals `git ls-files` |
| C12 forms | 59 rows driven through a `ProcessStartInfo` harness (real argv, UTF-8 stdin) in a clone with `.workflow/bugs.md` removed |
| C12 grep | `git grep` at `b6deca7`, excluding `.workflow/` |
| C12 walk | One temp main checkout, synthetic bugs, commands derived from the skill text. **Indicative, text plus CLI**: no real `/fix`, `/qa` or `/release` session ran |
| Hook fixture | `round-cap.ps1 -Mode count` on one dry-run return, in the temp checkout |
| C13 | `framework-sync.ps1` from the temp source, 13 temp targets, pwsh 7 and 5.1. Parameters read first: it writes only under `-Target` |

Harness notes, so nothing is read as a product result:
- The session's `git-guard` hook refused my `git -c core.hooksPath`, and `pre-commit` refused `git add` with `git commit` in one call. I dropped the override and split the calls. Both touched only the temp source.
- `git archive` on this machine (global `core.autocrlf=true`) produced a CRLF checkout, so the sync source `.gitattributes` is CRLF. An LF source did not run.
- The first no-Python attempt failed because my restricted PATH also lost `pwsh`. Re-run with its absolute path; that result is the one below.
- The walk log's line "--dry-run ... Journal hash stays" compares across the live row 4 moves my script ran, so it is not evidence. The valid check is the hash taken around rows 0b and 1 alone: unchanged.

## C0: `verify.ps1`
- Exit 0, 0 `FAIL` lines, closing line `verify-layer: OK (21 warning(s))`. 24 output lines.
- Warning kinds: agent files over 50 lines (soft), `CLAUDE.md` 31 lines, rules 123 lines, `4 file(s): body > 8000 chars`, `1 file(s): list item > 200 chars`.

## C12: invocation list and parse results
Every form in `bugs/SKILL.md`, `schema.md`, `fix`, `qa`, `qa-standards`, `feature`, `release`, `review`, `new-project`, `mem`, `qa-lead.md`, `routing.md`, `core.md` and the two hook messages. `core.md` names only the journal path, no command. `--root` was passed on every row, as `bugs/SKILL.md:18` writes it.

- **Parse errors: 0. Refused flags: 0.**
- 4 rows with exit 1 are negative probes: `set-status` and `round` and `extra-round` with no note, `delete` with no `--by`. `import-md` with no file also exits 1, as the text says.
- `--priority` repeated works as an OR: release row 1 returned the High bug, row 0b and the walk returned both High and Highest.
- `schema.md:94` (`test_bugs.py`) was not run here: E1 owns it.

| Source | Form | Exit | Output (first 170 chars) |
|---|---|---|---|
| bugs SKILL add | `add` | 0 | BUG-0001 / |
| bugs SKILL add --by | `add --by QA` | 0 | BUG-0002 / |
| bugs SKILL add optional fields | `add` | 0 | BUG-0003 / |
| bugs SKILL update | `update BUG-0001` | 0 | BUG-0001 updated: evidence / |
| bugs SKILL update --by | `update BUG-0001 --by QA` | 0 | BUG-0001 updated: root_cause / |
| bugs SKILL update, note alone | `update BUG-0001` | 0 | BUG-0001 updated: note / |
| bugs SKILL set-status --note | `set-status BUG-0001 Processing --note dispatched owner` | 0 | BUG-0001 Request -> Processing / |
| bugs SKILL set-status stdin note | `set-status BUG-0001 Request` | 0 | BUG-0001 Processing -> Request / |
| bugs SKILL set-status, note omitted ([--note N] reads as optional) | `set-status BUG-0001 Processing` | 1 | bugs: note: required (--note, or {"note": ...} on stdin): who, what, the evidence reference / |
| bugs SKILL round fix | `round BUG-0001 fix +1 --note reopen by GD` | 0 | BUG-0001 fix 1/2 / |
| bugs SKILL round review | `round BUG-0001 review +1 --note workflow review round` | 0 | BUG-0001 review 1/3 / |
| round, --note omitted | `round BUG-0001 review +1` | 1 | bugs: note: required (--note, or {"note": ...} on stdin): who, what, the evidence reference / |
| bugs SKILL extra-round fix | `extra-round BUG-0001 fix +1 --note GD order` | 0 | BUG-0001 fix 1/3 / |
| bugs SKILL extra-round review | `extra-round BUG-0001 review +2 --note GD order` | 0 | BUG-0001 review 1/5 / |
| extra-round, --note omitted | `extra-round BUG-0001 review +1` | 1 | bugs: note: required (--note, or {"note": ...} on stdin): who, what, the evidence reference / |
| bugs SKILL stop-rule unused | `stop-rule BUG-0001 fix --extra-dispatch unused` | 0 | BUG-0001 stop rule: fix, extra dispatch unused / |
| bugs SKILL stop-rule used | `stop-rule BUG-0001 fix --extra-dispatch used` | 0 | BUG-0001 stop rule: fix, extra dispatch used / |
| bugs SKILL stop-rule review | `stop-rule BUG-0001 review --extra-dispatch unused` | 0 | BUG-0001 stop rule: review, extra dispatch unused / |
| delete, no --by | `delete BUG-0004` | 1 | bugs: delete is GD only: pass --by GD on the GD's order / |
| bugs SKILL delete --by GD | `delete BUG-0004 --by GD` | 0 | deleted BUG-0004, journal uncommitted / |
| bugs SKILL purge --dry-run | `purge --dry-run` | 0 | would purge 0 / |
| bugs SKILL purge | `purge` | 0 | purged 0 / |
| bugs SKILL purge --auto (journal dirty/not tracked expected to skip or run) | `purge --auto` | 0 | purge skipped: journal not clean in git status / |
| bugs SKILL import-md (no bugs.md) | `import-md` | 1 | bugs: .workflow/bugs.md not found: nothing to import / |
| bugs SKILL show | `show BUG-0001` | 0 | BUG-0001 \| High \| Request \| uid 5041d9a3-c584-4c4e-8a7f-275248ed6227 / Title: Save system loses coins / Description: Save system drops coins on slot two after a resume, w... |
| bugs SKILL show --json | `show BUG-0001 --json` | 0 | { / "id": "BUG-0001", / "uid": "5041d9a3-c584-4c4e-8a7f-275248ed6227", / "title": "Save system loses coins", / "description": "Save system drops coins on slot two after a... |
| bugs SKILL list | `list` | 0 | ID \| Priority \| Status \| Closed \| Feature \| Title / BUG-0001 \| High \| Request \| - \| demo \| Save system loses coins / BUG-0002 \| Low \| Request \| - \| - \| HUD timer overlaps... |
| bugs SKILL list --status (spaces) | `list --status Won't fix` | 0 | no bugs / |
| bugs SKILL list --priority | `list --priority High` | 0 | ID \| Priority \| Status \| Closed \| Feature \| Title / BUG-0001 \| High \| Request \| - \| demo \| Save system loses coins / |
| bugs SKILL list --feature | `list --feature demo` | 0 | ID \| Priority \| Status \| Closed \| Feature \| Title / BUG-0001 \| High \| Request \| - \| demo \| Save system loses coins / BUG-0003 \| Medium \| Request \| - \| demo \| Audio mixer ... |
| bugs SKILL list --open | `list --open` | 0 | ID \| Priority \| Status \| Closed \| Feature \| Title / BUG-0001 \| High \| Request \| - \| demo \| Save system loses coins / BUG-0002 \| Low \| Request \| - \| - \| HUD timer overlaps... |
| bugs SKILL list --json | `list --json` | 0 | [ / { / "id": "BUG-0001", / "uid": "5041d9a3-c584-4c4e-8a7f-275248ed6227", / "title": "Save system loses coins", / "description": "Save system drops coins on slot two aft... |
| bugs SKILL search | `search coins` | 0 | BUG-0001 \| High \| Request \| Save system loses coins / Save system loses [coins] / BUG-0002 \| Low \| Request \| HUD timer overlaps score / Save system drops [coins] on slot ... |
| bugs SKILL search -n | `search coins -n 10` | 0 | BUG-0001 \| High \| Request \| Save system loses coins / Save system loses [coins] / BUG-0002 \| Low \| Request \| HUD timer overlaps score / Save system drops [coins] on slot ... |
| bugs SKILL sql | `sql SELECT id, status FROM bug` | 0 | id	status / BUG-0001	Request / BUG-0002	Request / BUG-0003	Request / |
| bugs SKILL sql --json | `sql SELECT id, status FROM bug --json` | 0 | [ / { / "id": "BUG-0001", / "status": "Request" / }, / { / "id": "BUG-0002", / "status": "Request" / }, / { / "id": "BUG-0003", / "status": "Request" / } / ] / |
| bugs SKILL counters --json | `counters BUG-0001 --json` | 0 | {"id": "BUG-0001", "found": true, "settled": false, "status": "Request", "fix": {"used": 1, "cap": 3}, "review": {"used": 1, "cap": 5}, "record": "- Stop rule: fix root-c... |
| bugs SKILL stats | `stats` | 0 | Bugs: 3 open (1 High+) / |
| bugs SKILL rebuild | `rebuild` | 0 | rebuilt: 3 bugs, 15 events / |
| bugs SKILL doctor | `doctor` | 0 | doctor: clean / |
| bugs SKILL doctor --fix | `doctor --fix` | 0 | doctor: clean / |
| fix:15 search | `search save coins` | 0 | BUG-0001 \| High \| Request \| Save system loses coins / [Save] system loses [coins] / BUG-0002 \| Low \| Request \| HUD timer overlaps score / [Save] system drops [coins] on s... |
| fix:18 round fix | `round BUG-0001 fix +1 --note GD reports reopen` | 0 | BUG-0001 fix 2/3 / |
| fix:51, review:33 round review | `round BUG-0001 review +1 --note failed review round` | 0 | BUG-0001 review 2/5 / |
| fix:52 extra-round fix | `extra-round BUG-0001 fix +1 --note the order` | 0 | BUG-0001 fix 2/4 / |
| fix:53 stop-rule | `stop-rule BUG-0001 review --extra-dispatch used` | 0 | BUG-0001 stop rule: review, extra dispatch used / |
| qa:12 list | `list` | 0 | ID \| Priority \| Status \| Closed \| Feature \| Title / BUG-0001 \| High \| Request \| - \| demo \| Save system loses coins / BUG-0002 \| Low \| Request \| - \| - \| HUD timer overlaps... |
| qa:42, qa-lead:22, bug-lifecycle:5 show | `show BUG-0001` | 0 | BUG-0001 \| High \| Request \| uid 5041d9a3-c584-4c4e-8a7f-275248ed6227 / Title: Save system loses coins / Description: Save system drops coins on slot two after a resume, w... |
| feature:147 list --feature --open | `list --feature demo --open` | 0 | ID \| Priority \| Status \| Closed \| Feature \| Title / BUG-0001 \| High \| Request \| - \| demo \| Save system loses coins / BUG-0003 \| Medium \| Request \| - \| demo \| Audio mixer ... |
| mem:37, bug-lifecycle:6 search | `search coins` | 0 | BUG-0001 \| High \| Request \| Save system loses coins / Save system loses [coins] / BUG-0002 \| Low \| Request \| HUD timer overlaps score / Save system drops [coins] on slot ... |
| review:17 counters (no --json) | `counters BUG-0001` | 0 | {"id": "BUG-0001", "found": true, "settled": false, "status": "Request", "fix": {"used": 2, "cap": 4}, "review": {"used": 2, "cap": 5}, "record": "- Stop rule: fix root-c... |
| routing:58 stop-rule | `stop-rule BUG-0001 fix --extra-dispatch unused` | 0 | BUG-0001 stop rule: fix, extra dispatch unused / |
| routing:60, round-cap:337 extra-round | `extra-round BUG-0001 fix +1 --note the order` | 0 | BUG-0001 fix 2/5 / |
| round-cap:369 stop-rule | `stop-rule BUG-0001 fix --extra-dispatch unused` | 0 | BUG-0001 stop rule: fix, extra dispatch unused / |
| new-project:70 add (first add starts the journal, see inv report) | `add` | 0 | BUG-0005 / |
| release:18 row 0b | `list --status Accepted --priority High --priority Highest` | 0 | no bugs / |
| release:19 row 1 | `list --open --priority High --priority Highest` | 0 | ID \| Priority \| Status \| Closed \| Feature \| Title / BUG-0001 \| High \| Request \| - \| demo \| Save system loses coins / |
| list --status 'Won't fix' | `list --status Won't fix` | 0 | no bugs / |
| list --status 'As designed' | `list --status As designed` | 0 | no bugs / |

## C12: `git grep`
### `bugs.md`, `bugs-template`
Command: `git grep -n -I -E "bugs\.md|bugs-template" b6deca7 -- . ':!.workflow'`. Every hit is a guard against a remaining old file, migration code or a test of those. **0 live references** to it as the store. `bugs-template` has 0 hits and `fix/references/` no longer exists. `.workflow/bugs.md` is still in the tree at `b6deca7`: C15 removes it after the merge.

```
.claude/hooks/round-cap.ps1:175:# the CLI cannot answer. No journal and no old bugs.md: no bugs yet, and Python never starts.
.claude/hooks/round-cap.ps1:178:    if (-not (Test-Path (Join-Path $workflow 'bugs.jsonl')) -and -not (Test-Path (Join-Path $workflow 'bugs.md'))) { return @() }
.claude/hooks/session-start.ps1:49:    if (Test-Path (Join-Path $workflow 'bugs.md')) { return 'Bugs: .workflow/bugs.md is still present - run bugs.py import-md, then del...
.claude/hooks/tests/run.ps1:717:    Check 'round-cap: an edit under .workflow names no bug any more' (EditState (Join-Path $proj '.workflow/bugs.md')) 0
.claude/hooks/tests/run.ps1:776:    Check 'round-cap: no journal and no bugs.md pass without Python' (NoPython { Dispatch 'Fix BUG-0001' }) 0
.claude/hooks/tests/run.ps1:778:    $oldBugs = Join-Path $proj '.workflow/bugs.md'
.claude/hooks/tests/run.ps1:781:    Check 'round-cap: a remaining bugs.md blocks a bug dispatch, naming import-md' ($r.Code -eq 2 -and $r.Out -match 'import-md') $true
.claude/hooks/tests/run.ps1:782:    Check 'round-cap: a remaining bugs.md leaves other dispatches alone' (Dispatch 'Explain the HUD') 0
.claude/hooks/tests/run.ps1:1016:    Set-Content (Join-Path $bp '.workflow/bugs.md') "# Bugs`n" -Encoding UTF8
.claude/hooks/tests/run.ps1:1018:    Check 'session-start: a remaining bugs.md prints one import-md line' ($r.Code -eq 0 -and @($r.Out -split '\r?\n' | Where-Object { $_ ...
.claude/skills/bugs/references/schema.md:76:- **Exit:** unknown or purged ID `found:false`, exit 0. Duplicate ID, corrupt journal or a remaining `bugs.md`: non-zero with ...
.claude/skills/bugs/scripts/bugs.py:325:        return self.workflow / "bugs.md"
.claude/skills/bugs/scripts/bugs.py:1443:        raise Refused(".workflow/bugs.md not found: nothing to import")
.claude/skills/bugs/scripts/bugs.py:1484:    print("imported %d bugs, %d events; delete .workflow/bugs.md next" % (new_bugs, new_events))
.claude/skills/bugs/scripts/bugs.py:1544:    sub.add_parser("import-md", help="one-way migration from .workflow/bugs.md; the caller deletes the file")
.claude/skills/bugs/scripts/bugs.py:1563:            raise Refused(".workflow/bugs.md exists: run import-md, delete the file, then retry")
.claude/skills/bugs/scripts/test_bugs.py:42:# Copied from .workflow/bugs.md on 2026-11-03: the import has to take today's real file.
.claude/skills/bugs/scripts/test_bugs.py:1442:        (self.root / ".workflow" / "bugs.md").write_text("# Bugs\n", encoding="utf-8")
.claude/skills/bugs/scripts/test_bugs.py:1450:                self.assertIn("bugs.md", self.no(*argv, stdin=fields() if argv[0] == "add" else None))
.claude/skills/bugs/scripts/test_bugs.py:1457:        with open(p / "bugs.md", "w", encoding="utf-8", newline="") as f:
.claude/skills/bugs/scripts/test_bugs.py:1459:        return p / "bugs.md"
.claude/skills/bugs/scripts/test_bugs.py:1534:        self.assertIn("bugs.md", self.no("list"))
.claude/skills/bugs/scripts/test_bugs.py:1537:        self.assertIn("bugs.md", self.no("import-md"))
.claude/skills/bugs/scripts/test_bugs.py:1597:        (self.root / ".workflow" / "bugs.md").unlink()
.claude/skills/bugs/scripts/test_bugs.py:1968:        (self.root / ".workflow" / "bugs.md").write_text(REAL_BUGS_MD, encoding="utf-8")
.claude/skills/bugs/scripts/test_bugs.py:1984:        (self.root / ".workflow" / "bugs.md").write_text("# Bugs\n", encoding="utf-8")
.claude/skills/bugs/scripts/test_bugs.py:1985:        self.assertIn("bugs.md", self.no("list", root=self.wt))
```

### Old statuses
Command: `git grep -n -I -E "\b(Open|Fixed|Closed|Reopened)\b" b6deca7 -- . ':!.workflow'`. 134 hits.

**0 live hits use an old status on a bug.** Classes:
- Migration only: `schema.md:87`, `bugs.py:1239,1242,1356,1357` (`import-md` reading the old file), and `test_bugs.py` (33).
- Column label `Closed` for `closed_at`: `bugs.py:961,1017`.
- Feature status: `round-cap.ps1:159`, `session-start.ps1:23`, `feature/SKILL.md:151`, `feature-template.md:3`, `verify.ps1:55`, `fix/SKILL.md:24`, `hooks/tests/run.ps1` (6).
- Framework backlog state: `templates/framework-backlog.md:3,6`.
- Plain English "open bugs" (not a status, matches `--open`): `qa-lead.md:29`, `feature/SKILL.md:147`, `release/SKILL.md:19`; `schema.md:6,67` define it.
- Unrelated words in the other files (Flexalon, DOTween, `File.Open`, `Fixed Update`, step titles): per the brief, not findings.

Non-engine hits verbatim:
```
.claude/agents/qa-lead.md:29:- [ ] **Open bugs cased:** Plan — every open bug of this feature → a case — evidence: bug ID → case. No open bug → `n/a`.
.claude/agents/technical-architect.md:40:- **`Open questions:`** tagged design | architecture | technology.
.claude/agents/technical-architect.md:75:- **Design questions:** answer one without a clear default → the GD's: list it under `Open questions:`.
.claude/hooks/round-cap.ps1:110:        try { $fs = [IO.File]::Open($ledgerPath, 'OpenOrCreate', 'ReadWrite', 'None') } catch { Start-Sleep -Milliseconds 100 }
.claude/hooks/round-cap.ps1:159:    if ($text -notmatch '(?m)^- Status:\s*Open') { return @() }
.claude/hooks/session-start.ps1:23:        if ($text -match '(?m)^- Status:\s*Open\b') {
.claude/skills/bugs/references/schema.md:6:- **Open (every status but the terminal five):** `Request` · `Processing` · `Resolved` · `Review` · `Reopen` · `Backlog`.
.claude/skills/bugs/references/schema.md:67:- **Rule:** terminal for strictly more than 90 days. Open and `Backlog` bugs never go. IDs are never reused.
.claude/skills/bugs/references/schema.md:87:- **Mapping:** `Open` → `Request` · `Fixed` → `Resolved` · `Closed` → `Complete` · `Reopened` → `Reopen`; the other four keep ...
.claude/skills/bugs/scripts/bugs.py:961:              ("Duplicate of", "duplicate_of"), ("Created", "created_at"), ("Updated", "updated_at"), ("Closed", "closed_at"))
.claude/skills/bugs/scripts/bugs.py:1017:    print("ID | Priority | Status | Closed | Feature | Title")
.claude/skills/bugs/scripts/bugs.py:1239:OLD_STATUS = {"Open": "Request", "Fixed": "Resolved", "Closed": "Complete", "Reopened": "Reopen",
.claude/skills/bugs/scripts/bugs.py:1242:RX_HISTORY = re.compile(r"(?:(?<=\s)|^)(\d{4}-\d{2}-\d{2}) (Open|Fixed|Closed|Reopened|Won't fix|Accepted|As designed|Duplicate)\...
.claude/skills/bugs/scripts/bugs.py:1356:    if history and history[0][1] != "Open":
.claude/skills/bugs/scripts/bugs.py:1357:        problems.append("%s History: must start with Open" % bug_id)
.claude/skills/feature/SKILL.md:16:## 0. Open
.claude/skills/feature/SKILL.md:55:- **`Open questions:`:** routed by kind:
.claude/skills/feature/SKILL.md:147:  - **Open items:** open bugs (`bugs.py list --feature <slug> --open`) · limitations · gates declined · what did not run.
.claude/skills/feature/SKILL.md:151:- **Close:** `Status: Closed`; each accepted gap into the feature root's `DEBT.md`; the backlog row → `done`.
.claude/skills/feature/SKILL.md:170:- **Open bugs:** `Won't fix`, `--by GD`: abandoning is the GD's order.
.claude/skills/feature/references/feature-template.md:3:- Status: Open | Closed | Abandoned
.claude/skills/fix/SKILL.md:24:- **Closed feature:** a closed feature stays `Closed`.
.claude/skills/release/SKILL.md:19:| 1 | Open bugs | main session | No High or Highest unsettled, `Backlog` included (`bugs.py list --open --priority High --priority High...
.claude/skills/verify-layer/scripts/verify.ps1:55:    '.claude/skills/feature/references/feature-template.md' = @('- Status: Open', '- Size:', '- Rounds:', '## GD decisio...
.claude/templates/framework-backlog.md:3:Open work on the agent framework (`.claude/`) found while working in this repo: a wrong rule, a gap in an agent or skill, a hook ...
.claude/templates/framework-backlog.md:6:- Add a row when found; close it with what closed it (commit sha or path). State: `Open` · `Done: <sha or path>` · `Recorded` (kn...
README.md:82:Open Claude Code in the project once and accept the trust dialog. Until you do, the project's permissions and hooks are ignored. Then run `/verify-layer` aft...
```

### Severity on bugs
Command: `git grep -n -i severity b6deca7 -- .claude` and a backticked form `` `(Open|Fixed|Closed|Reopened)` ``, `Critical/High`. **0 live hits put Severity on a bug.**
- Bug records: `bug-lifecycle.md:25` ("never Severity"), `qa-standards/SKILL.md:38` (the mapping), `schema.md:11` (old Critical maps to Highest), `bugs.py:781,1265,1342-1346` (refusal and import). `add` with `severity` is refused: `add: unknown field: severity (status starts at Request; bugs have a priority, no severity)`.
- Findings, kept per GD decision 4: `code-reviewer`, `security-reviewer`, `review`, `code-review-method`, `critic`, `playtest-tester`, `review-gate.js`, `project-audit.js`, `device-test-walkthrough` and the rest.

### Two files merged from `develop`
No contradiction with the new statuses.
- `agents/qa-automation-engineer.md:22`: "a `/fix` step 6 run shows the fix reached (`unity-test-framework` step 14)". Step 14 exists at `unity-test-framework/SKILL.md:51`. `:53` is the `Repro:` line, unchanged.
- `unity-test-framework/references/code-coverage.md:22`: `/fix` step 6 runs "The regression test alone". Agrees with `fix/SKILL.md:57`. Its "Editor open" row agrees with `fix/SKILL.md:59`.
- Neither file names a status.

## C12: the walk, indicative, text plus CLI
A status move is `set-status <id> "<status>" --note <n>`. All exit 0 unless stated.

| Text | Commands driven | Result |
|---|---|---|
| fix:15, first bug, no journal | `search`, `list --open`, `stats` | `no matches`, `no bugs`, `Bugs: 0 open (0 High+)`. No DB and no journal created |
| fix:15, populated | `search` with `can't`, `:`, `-`, `BUG-0001`, words that do not all occur | No parse error, matches any word. No finding |
| fix:16 | `add`, stdin with the listed fields | `BUG-0001`, status `Request` |
| fix:17 | `update <id>` with `note`, then with `evidence` | E3-06 |
| fix:17, terminal match | `Complete` to `Reopen` | Allowed |
| fix:18 | `Reopen`, then `round <id> fix +1 --note` | `fix 1/2` |
| fix:19 | `Resolved` to `Reopen` | Exit 1: `Resolved -> Reopen is not in the state machine`. Then `Review`, `Reopen` both pass, as written |
| fix:31 | `Won't fix` with and without `--by GD` | Without: exit 1, `is GD only ... pass --by GD`. With: pass |
| fix:34, fix:49 | `Processing`, `Request`, `Processing` | Pass. `Processing` to `Processing` is refused, and the text never orders it |
| fix:51-53 | `round`, `extra-round`, `stop-rule` unused then used | `review 1/3`, `fix 1/3`; `record` holds `- Stop rule: fix root-caused 2026-11-03 - extra dispatch: used` and `extra round: fix +1` |
| fix:60-64 | `Resolved`, `Review`, then each of `Resolved` (no line), `Reopen` (reproduces), `Complete` (gone) | All pass; `Closed:` set on `Complete` |
| fix:67 | `Accepted` with and without `--by GD` | Without: refused. With: pass. Mirror: E3-07 |
| fix:72 | `git status` | Journal uncommitted, as the reply must say. No-feature `/fix` only: E3-05 |
| bug-lifecycle table | `Duplicate` with no target refused (`duplicate_of: required for Duplicate`), with target pass; `As designed` pass | Matches |
| bug-lifecycle:23 | Into `Backlog` and out: refused without `--by GD`; `Backlog` to `Processing` refused; `counters` gives `settled: true` | Matches |
| qa:12 | `list` as written | E3-09 |
| qa:33 | `Review`, `Complete` | Pass |
| qa:42, qa-lead:22 | `list --feature demo`, `show <id>` per row | Settled and Backlog rows present; `show` prints status and events |
| release row 0b | `list --status Accepted --priority High --priority Highest` | BUG-0005 High, BUG-0014 Highest. Medium Accepted absent |
| release row 1 | `list --open --priority High --priority Highest` | Lists High and Highest in `Backlog`, so they block; `Resolved`, `Reopen` listed; Medium Backlog and High `Complete` absent |
| release row 4 | `Resolved`, `Review`, `Complete`, then row 1 again | Deferred bug leaves the list |
| release `--dry-run` | Rows 0b and 1 only | Journal hash unchanged. No status command is ordered. Hook side effect: E3-02 |
| release:37, Python absent | Row 1 with no `python` on PATH | `python: The term 'python' is not recognized`. No rows, so not a pass, as written. My `exit $LASTEXITCODE` wrapper returned 0 because no process started; the text rests on the missing output, not on that code |
| release:37, CLI error | `bugs.md` present; a non-JSON journal line | Exit 1: `.workflow/bugs.md exists: run import-md...`; `corrupt journal: line 66: JSONDecodeError` |
| release:37, no journal | `list` | E3-01 |

Status moves agreed across `fix`, `bug-lifecycle.md`, `schema.md` and the CLI on every move driven. The full 121-pair matrix is E1's.

## Findings
Owner names the author role of the text; the fixing agent for skill text is otherwise unclear. All repros are deterministic: 1 attempt, 1 hit. Each starts from a temp main checkout at `b6deca7` with `.workflow/bugs.md` removed.

### E3-01 Medium: release gate cannot pass on a project with no bug filed
- **Location:** `.claude/skills/release/SKILL.md:37`, with `new-project/SKILL.md:70`.
- **Expected:** a project with no bugs passes rows 0b and 1. Source: spec, Hook section ("No journal -> no counters, as a missing `bugs.md` behaves today"), and `schema.md:61` ("No journal: reads return empty"). The spec's release clause makes only Python absent "not a pass".
- **Actual:** `release:37` says "No `.workflow/bugs.jsonl` -> say so; not a pass", while `new-project:70` says only the first `add` starts the journal. So a clean project fails rows 0b and 1 until the GD accepts a gap by name.
- **Evidence:** on `develop`, `new-project/SKILL.md:67` created `bugs.md` at bootstrap, so "missing file" meant a broken setup. Here `list` prints `no bugs`, exit 0, and `stats` prints `Bugs: 0 open (0 High+)`, with no journal.
- **Owner:** T3 author.
- **Repro:** 1. Fresh checkout, no journal. 2. Run row 1. Output `no bugs`. 3. Apply `release:37`: not a pass.

### E3-02 Medium: a `--dry-run` row 4 writes the hook ledger
- **Location:** `release/SKILL.md:10,22`; `hooks/round-cap.ps1` count mode.
- **Expected:** "no writes". Source: `release:10`.
- **Actual:** row 4's brief carries `Verify:` in a dry run too. A `reproduces` return charges a fix round while the bug stays `Resolved`, so a dry run burns a round for a real run.
- **Evidence:** ledger `<absent>` before; after: `{ "bug:BUG-0017": { "fix": [ "verify-dry1" ] } }`; hook exit 0; `show` gives `BUG-0017 | High | Resolved`.
- **Owner:** T3 author (`release` text) or T2 author (hook). Unclear which side should change.
- **Repro:** 1. A `Resolved` bug. 2. Feed `round-cap.ps1 -Mode count` a transcript with brief `Verify: <id>` and return `Repro: <id> reproduces`. 3. Read `.workflow/rounds.json`.

### E3-03 Medium: sync reports up to date when a later project rule defeats the attributes
- **Location:** `.claude/tools/framework-sync.ps1:165-167`; `doctor` in `bugs.py`.
- **Expected:** `.workflow/bugs.jsonl` holds `text eol=lf merge=union` in a target. Source: spec, Consistency item 5; criterion 10; C13 conflict case.
- **Actual:** the check matches line text only. With the framework line followed by `.workflow/** -text merge=binary`, sync prints `already up to date` and git resolves `merge: binary`. `doctor` warns, then prints `doctor: clean`, exit 0.
- **Evidence:** target t4b, `check-attr`: `text: unset ; eol: lf ; merge: binary`. `doctor: warning: .gitattributes lacks ... merges can conflict` / `doctor: clean`. A conflicting line placed before the framework line is fine (t4, t4c): `merge: union`.
- **Owner:** T3 author (sync), T1 author (`doctor` wording).
- **Repro:** Target t4b in the C13 table, then `git check-attr text eol merge -- .workflow/bugs.jsonl`.

### E3-04 Medium: a target that ignores `.workflow/` loses the journal from git, silently
- **Location:** `framework-sync.ps1` `.gitignore` step; `doctor`.
- **Expected:** the journal is tracked. Source: spec, GD decision 1. No spec clause covers a project that already ignores the folder.
- **Actual:** sync appends `.workflow/bugs.db*` and reports nothing. `add` works, `doctor` prints `doctor: clean`, `git status` shows nothing.
- **Evidence:** t7 `check-ignore bugs.jsonl: .gitignore:1:.workflow/ .workflow/bugs.jsonl`; `t7 status: []`.
- **Owner:** T3 author (sync), T1 author (`doctor`).
- **Repro:** Target with `.workflow/` in `.gitignore`; sync; `add`; `doctor`; `git status --short -- .workflow`.

### E3-05 Medium: `/release` and a standalone `/qa` write the journal and never report it uncommitted
- **Location:** `release/SKILL.md:17,22`; `qa/SKILL.md:33,46-50`; compare `fix/SKILL.md:72`, `feature/SKILL.md:152`.
- **Expected:** the GD is told when the journal is left uncommitted. Source: spec, "Journal commits".
- **Actual:** only no-feature `/fix` and CP4 handle it. Row 4 writes status after row 0's "Release content committed", and `Finish` does not mention it, so the tag omits those moves. While the journal is dirty, the session purge skips and the status line does not say so.
- **Evidence:** `purge --auto` prints `purge skipped: journal not clean in git status`. Session start on the same dirty journal prints only `Bugs: 6 open (3 High+)`. The `release` and `qa` text have no such line (read).
- **Owner:** T3 author.
- **Repro:** 1. File and move a bug. 2. `purge --auto`. 3. Run `session-start.ps1` with `CLAUDE_PROJECT_DIR` set to the checkout.

### E3-06 Medium: "add evidence with `update`" replaces the earlier evidence
- **Location:** `fix/SKILL.md:17`; `bugs/SKILL.md:29,37`.
- **Expected:** a match adds evidence on that ID. Source: `fix:17`, `bugs/SKILL.md:29`.
- **Actual:** the natural reading sends `{"evidence": ...}`, which overwrites the field. `show` keeps no old value and the event line has no note. Only `bugs/SKILL.md:37` names the safe form, a `note` alone; `/fix` does not.
- **Evidence:** before `Evidence: .workflow/evidence/x/log.md`; after `Evidence: run7/log2.md`; event `update by main session` with no text. The note form gives `update by main session: second hit in run 7, see log2.md`. The old value survives in the journal only.
- **Owner:** T3 author.
- **Repro:** `add`; `update <id>` with `{"evidence":"new"}`; `show <id>`.

### E3-07 Medium: the `DEBT.md` mirror has no location for a no-feature bug
- **Location:** `bugs/SKILL.md:31`; `fix/SKILL.md:31,67`; `release/SKILL.md:18`; `feature-docs/SKILL.md:20`.
- **Expected:** `Won't fix` and `Accepted` are mirrored to `DEBT.md`, and row 0b finds a purged one there. Source: spec, state machine and Accepted trade-offs.
- **Actual:** `DEBT.md` is a feature-root file. `bugs/SKILL.md:31` gives no path, and `fix:67`'s no-feature accept names no mirror. Row 0b reads "each feature root's `DEBT.md`". The walk's BUG-0005 (High, Accepted, no feature) has no stated home, so after 90 days it can leave row 0b entirely.
- **Evidence:** the quoted lines; row 0b lists BUG-0005 from the DB only. Purge itself was not run on it (E1 owns purge).
- **Owner:** T3 author.
- **Repro:** Walk `fix:67`, no feature, accept unverified; look for where the mirror goes.

### E3-08 Low: `set-status` reads as if the note were optional
- **Location:** `bugs/SKILL.md:38`.
- **Expected:** the form matches the CLI. Source: `schema.md:31` ("a note is required on every `set-status`").
- **Actual:** `[--note N]` is bracketed. `/fix` names a note only at `gone`.
- **Evidence:** `set-status BUG-0001 Processing`, exit 1: `bugs: note: required (--note, or {"note": ...} on stdin)`. The refusal is self-explaining.
- **Owner:** T1 author.
- **Repro:** The command above, no stdin.

### E3-09 Low: `/qa` plan command lacks its filters
- **Location:** `qa/SKILL.md:12`.
- **Expected:** "this feature's open bugs". Source: same line; `feature/SKILL.md:147` has the right form.
- **Actual:** bare `bugs.py list` returned 11 rows of every feature, settled included. `list --feature demo --open` returned the 3 wanted.
- **Evidence:** walk, "qa:12 as written".
- **Owner:** T3 author.
- **Repro:** Run both forms on a journal with two features.

### E3-10 Low: "the session-start line" does not identify the interpreter line
- **Location:** `bugs/SKILL.md:11`.
- **Expected:** the text names where `<python>` comes from. Source: `bugs/SKILL.md:11`.
- **Actual:** only the `Memory:` line names it, as `python3` here. The `Bugs:` line, the natural place to look, does not, and prints nothing with no journal.
- **Evidence:** `Memory: ... Query: python3 -I .claude/skills/mem/scripts/mem.py q "<words>" (skill mem).` / `Bugs: 6 open (3 High+)`.
- **Owner:** T1 author.
- **Repro:** Run `session-start.ps1` on the temp checkout.

### E3-11 Low: `routing.md` round wording names only a file
- **Location:** `.claude/rules/routing.md:57`.
- **Expected:** per-bug counters live in the database. Source: spec ("Used stays file + ledger"; `round-cap.ps1:17` says "file or database + ledger").
- **Actual:** "The state file holds only events the hook cannot see ...; used = file + hook". A bug has no state file.
- **Evidence:** the quoted line, against `routing.md:63` and `round-cap.ps1:17`.
- **Owner:** T3 author.
- **Repro:** Read the three lines.

### E3-12 Low: row 1's device-verification exception has no marker
- **Location:** `release/SKILL.md:19`, `fix/SKILL.md:68`.
- **Expected:** the session can tell a deferred `Resolved` bug from any other. Source: `release:19`.
- **Actual:** `list` shows only `Resolved`, and no field or note form is prescribed. Carried over from `develop`'s `Fixed` wording. Low because row 4 still re-runs each bug it defers.
- **Evidence:** `BUG-0013 | High | Resolved | - | - | Release high resolved awaits device`.
- **Owner:** T3 author.
- **Repro:** Run row 1 with a `Resolved` High bug.

### E3-13 Low: a search hit on a `Duplicate` bug, read literally, reopens the duplicate
- **Location:** `fix/SKILL.md:17`, `bugs/SKILL.md:29`, `bug-lifecycle.md:6`.
- **Expected:** a match lands on the bug that owns the defect. Source: the same lines; spec table allows the move.
- **Actual:** "a match on a settled bug moves it to `Reopen`" draws no line for `Duplicate`. The walk's top hit for `coins` was BUG-0006 `Duplicate`, whose target BUG-0001 was already `Reopen`. Nothing tells the session to follow `duplicate_of`.
- **Evidence:** `BUG-0006 | Medium | Duplicate | Duplicate of save coin loss`.
- **Owner:** T3 author.
- **Repro:** `Duplicate` a bug onto another, `search` a shared word.

### E3-14 Low: sync leaves mixed line endings
- **Location:** `framework-sync.ps1:162,170`.
- **Expected:** C13: no BOM and LF at the line. **Met.** This is what surrounds it.
- **Actual:** a created file ends in a stray CRLF (`Set-Content`), and a CRLF file gets an LF block. Git reads all of it correctly: `check-attr` and `check-ignore` pass, including `.claude/.framework-backup/` with its CR.
- **Evidence:** t1 `.gitattributes` tail bytes `69 6F 6E 0A 0D 0A`; first bytes `23 20 5A`, no BOM. t1 `.gitignore` last line `.claude/.framework-backup/<CR><LF>`.
- **Owner:** T3 author.
- **Repro:** t1 and t2 in the table below.

## C13: `framework-sync.ps1`, target by target
`-Mode Install -SourceRoot <temp source> -Target <temp target>`, pwsh 7, each run twice. Each target has `ProjectSettings/`, `core.autocrlf=false`. `check-attr` is on `.workflow/bugs.jsonl`.

| Target | Start | Sync says | `check-attr` merge | `bugs.db*` ignored | Journal ignored | Second run |
|---|---|---|---|---|---|---|
| t1 | No `.gitattributes`, no `.gitignore` | created, created | union | yes | no | Only `syncedAt` changes |
| t2 | Both CRLF, other lines | 3 and 32 lines appended | union | yes | no | Same |
| t3 | Line present, LF, all framework lines | `.gitattributes` up to date, 0 bytes changed | union | yes | no | Same |
| t3b | Line present, CRLF | 2 appended, no duplicate | union | yes | no | Same |
| t4 | Conflicting line first: `-text merge=binary` | 3 appended | union, framework wins | yes | no | Same |
| t4b | Framework line, then `.workflow/** -text merge=binary` | 2 appended; bug line not re-added | **binary** (E3-03) | yes | no | Same |
| t4c | `.workflow/** -text merge=binary` only | 3 appended | union | yes | no | Same |
| t5 | No trailing newline | 3 appended on a new line | union | yes | no | Same |
| t6 | BOM and CRLF | 3 appended, BOM kept | union | yes | no | Same |
| t7 | `.gitignore` holds `.workflow/` | 32 appended | union | yes | **yes** (E3-04) | Same |
| t8 | `-DryRun`, empty target, then with files | "created" / "appended" reports | n/a | n/a | n/a | 0 files changed in both dry runs |
| t9 | `-Mode Update` after install, line removed by hand | 1 appended | union | yes | no | n/a |
| t9, retired | `bugs-template.md` recorded in the manifest, hash matching | `removed ... (retired by the framework)`; file gone | n/a | n/a | n/a | n/a |
| t10 | Windows PowerShell 5.1 | Exit 1, refused by `#requires` | n/a | n/a | n/a | 0 files changed |

- **Second run:** `.gitattributes` and `.gitignore` byte-identical on all ten two-run targets. The only changed file is `.claude/.framework-manifest.json`, identical once `syncedAt` is removed (checked on t3).
- **No BOM, LF at the line:** t1 first bytes `23 20 5A`, line `...merge=union<LF>`. t2, t4, t5, t6 also end the line in LF.
- **5.1 refusal, the expected result:** `The script 'framework-sync.ps1' cannot be run because it contained a "#requires" statement for Windows PowerShell 7.0.` `install-framework.ps1` and `update-framework.ps1` also declare `#requires -Version 7`.
- **After a sync:** t1 `add` gives `BUG-0001`, `doctor: clean`, `?? .workflow/`. Synced `bugs.py` hash equals the source. A leftover `bugs.md` in t5: `list` exit 1, `.workflow/bugs.md exists: run import-md, delete the file, then retry`.

### `.gitattributes` diffs, before to after
```
--- t2-crlf
@@ -1,2 +1,7 @@
 *.png filter=lfs diff=lfs merge=lfs -text
 *.unity merge=unityyamlmerge eol=lf
+
+# Added by the AI-For-Game framework
+.memory/traces/** text eol=lf linguist-generated
+.claude/skills/**/scripts/*.sh text eol=lf
+.workflow/bugs.jsonl text eol=lf merge=union
--- t3-present
--- t3b-present-crlf
@@ -1,2 +1,6 @@
 *.png filter=lfs -text
 .workflow/bugs.jsonl text eol=lf merge=union
+
+# Added by the AI-For-Game framework
+.memory/traces/** text eol=lf linguist-generated
+.claude/skills/**/scripts/*.sh text eol=lf
--- t4-conflict-before
@@ -1 +1,6 @@
 .workflow/bugs.jsonl -text merge=binary
+
+# Added by the AI-For-Game framework
+.memory/traces/** text eol=lf linguist-generated
+.claude/skills/**/scripts/*.sh text eol=lf
+.workflow/bugs.jsonl text eol=lf merge=union
--- t4b-conflict-after
@@ -1,2 +1,6 @@
 .workflow/bugs.jsonl text eol=lf merge=union
 .workflow/** -text merge=binary
+
+# Added by the AI-For-Game framework
+.memory/traces/** text eol=lf linguist-generated
+.claude/skills/**/scripts/*.sh text eol=lf
--- t4c-dir-rule-after
@@ -1 +1,6 @@
 .workflow/** -text merge=binary
+
+# Added by the AI-For-Game framework
+.memory/traces/** text eol=lf linguist-generated
+.claude/skills/**/scripts/*.sh text eol=lf
+.workflow/bugs.jsonl text eol=lf merge=union
--- t5-nonl
@@ -1 +1,5 @@
-*.png filter=lfs -text
\ No newline at end of file
+*.png filter=lfs -text
+# Added by the AI-For-Game framework
+.memory/traces/** text eol=lf linguist-generated
+.claude/skills/**/scripts/*.sh text eol=lf
+.workflow/bugs.jsonl text eol=lf merge=union
--- t6-bom
@@ -1 +1,6 @@
 <BOM>*.png filter=lfs -text
+
+# Added by the AI-For-Game framework
+.memory/traces/** text eol=lf linguist-generated
+.claude/skills/**/scripts/*.sh text eol=lf
+.workflow/bugs.jsonl text eol=lf merge=union
```

t1, t7 and t8 had no prior file. Created t1 `.gitattributes`, CR and LF shown:
```
# Zero-Mem traces: one append-only file per session, generated by the Stop hook. Keep them diffable:<LF>
# the pre-commit secret scan reads staged diffs.<LF>
.memory/traces/** text eol=lf linguist-generated<LF>
<LF>
# Bash fails on a CRLF checkout.<LF>
.claude/skills/**/scripts/*.sh text eol=lf<LF>
<LF>
# Bug journal: the truth behind .workflow/bugs.db (skill bugs). Branches append; a union merge keeps both sides.<LF>
.workflow/bugs.jsonl text eol=lf merge=union<LF>
<CR><LF>
```

`.gitignore`, the bug line: appended as `+.workflow/bugs.db*` under `+# Added by the AI-For-Game framework` in t2, t5, t6, t7; present in the created file on t1.

## Exit criteria
| Criterion | Result |
|---|---|
| Baseline, `verify.ps1` | Exit 0, 21 warnings, 0 `FAIL` at `b6deca7` |
| 8 | Parse: 0 errors, 0 refused flags on 59 rows. Grep: 0 live hits for `bugs.md`, old statuses or bug Severity. Walk: 13 text findings (E3-01, 02, 05 to 13, plus 03 and 04 shared with sync) |
| 10 | Line installed and effective on t1, t2, t3, t3b, t4, t4c, t5, t6, t7, t9. Second-run diff empty. Dry run writes nothing. 5.1 refused, as expected. t4b is the exception, E3-03. E3-14 cosmetic |

## Not covered
- Skill text under a real `/fix`, `/qa`, `/release` session: this walk is indicative. Owner: main session or GD, fresh session after the merge.
- Build-dependent parts of `/release` row 4: no build, no device, no real `Verify:` dispatch. Owner: `build-release-engineer`.
- `schema.md:94` `test_bugs.py`, the 121-pair matrix, purge: Owner: E1 (C0, C1, C4).
- Real `merge=union` merges in a target: only `check-attr` here. Owner: E1 (C5).
- Hook behaviour beyond the one dry-run fixture: Owner: E2 (C8, C9).
- `install-framework.ps1` and `update-framework.ps1` end to end, including the remote fetch; only `framework-sync.ps1` ran, called directly. Owner: T3 author or main session.
- Sync from an LF source checkout, `-Force`, an existing `settings.json` merge, and a target with `core.autocrlf=true`. Owner: T3 author.
- Python 3.10 runtime. Owner: GD (C14 is static, E1).
- Criterion 9 and the removal of `.workflow/bugs.md`. Owner: main session (C15).

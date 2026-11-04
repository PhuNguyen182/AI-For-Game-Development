# E3 re-run: docs contract and sync (C0 verify, E3-01 to E3-14, C12, C13)

- Revision: worktree `.claude/worktrees/sqlite-bug-tracker`, `349542e`. Nothing carried over from attempt 1; every case below ran again.
- Executor: independent of the authors. Oracle: spec, `qa-plan.md`, rule files, skill text, plus the two GD decisions now on record.
- Python 3.14.7, pwsh 7.6.9, Windows PowerShell 5.1.26100.9711, Git Bash. No Python 3.10 run.
- **Result:** E3-01 to E3-14 all closed. 5 new defects: 0 Critical, 0 High, 1 Medium, 4 Low.
- **A hard limit was breached by my harness; see the next section.**

## Side effect in the worktree: disclosed
- **What happened:** the first dry-run hook fixture ran `round-cap.ps1` with no `CLAUDE_PROJECT_DIR`. The hook's root fell back to the cwd, the worktree, so the control case wrote `.workflow/rounds.json` there. The brief says the worktree is read-only.
- **The file:** gitignored, one entry, my own: `{ "bug:BUG-0014": { "fix": [ "verify-ctl1" ] } }`, mtime 19:24:32. Attempt 1's end check found no such file there.
- **Done:** I compared the content exactly, then removed that one file. `git status --short --ignored` then shows only the two older `__pycache__` folders (mtimes 10:53 and 18:21). No tracked file changed, HEAD unchanged.
- **Main checkout:** its `.workflow/rounds.json` was not written: mtime 16:29:42, before this re-run.
- **Result discarded:** that run's dry-run lines in the walk log are not evidence. The fixture ran again, pinned to a temp repo by env and cwd. Those results are the ones below.

## What ran
| Step | How |
|---|---|
| C0 | `pwsh -NoProfile -File <worktree>/.claude/skills/verify-layer/scripts/verify.ps1` |
| Temp sources | `git archive` at `349542e` twice: `core.autocrlf=false` (LF source) and the machine default `true` (CRLF source). 592 files each, one commit each |
| C12 forms | 59 rows through a `ProcessStartInfo` harness, real argv and UTF-8 stdin, in a clone with `.workflow/bugs.md` removed. Plus real pipes from pwsh 7, 5.1 and Git Bash |
| C12 grep | `git grep` at `349542e`, excluding `.workflow/` |
| C12 walk | Temp main checkout, synthetic bugs, commands derived from the skill text. **Indicative, text plus CLI**: no real `/fix`, `/qa` or `/release` session ran |
| Hook fixture | `round-cap.ps1 -Mode count`, 4 returns, temp repo |
| C13 | `framework-sync.ps1`, 24 temp targets, each two-run target run twice. `install-framework.ps1` once. 5.1 refusal |

Other harness notes:
- My first CLI run failed because a helper named `R` resolved to the `Invoke-History` alias. Renamed, re-run on a clean journal; the table is from the re-run.
- `list --json` first looked as if it carried the marker: that was my probe's title containing "awaits". Re-tested with a plain title: it does not.

## C0
Exit 0, 0 `FAIL` lines, 24 output lines, `verify-layer: OK (21 warning(s))`.

## E3-01 to E3-14: one verdict per ID
Each is the original check re-run at `349542e`.

| ID | Sev | Verdict | Check and result |
|---|---|---|---|
| E3-01 | Medium | **Closed** | `new-project:70` and `feature:70` now create an empty journal. On it: `list` `no bugs`, `stats` `Bugs: 0 open (0 High+)`, `doctor` clean, first `add` gives `BUG-0001`. Rows 0b and 1 run with a journal present. `release:38` keeps "no journal: not a pass", and `schema:65` calls a missing one a broken setup. A separate migration path still reaches no journal: E3-15 |
| E3-02 | Medium | **Closed** | `release:11` orders no `Verify:` line in a dry-run brief. Fixture as written, also with a `Bug:` marker, also with a stray `Repro: <id> reproduces` in the return: exit 0, ledger `<absent>`, bug stays `Resolved`. Control with `Verify:`: `{ "bug:BUG-0004": { "fix": [ "verify-ctl1" ] } }`, so the fixture is live |
| E3-03 | Medium | **Closed** | t4b: sync prints `WARNING: .workflow/bugs.jsonl resolves to merge=binary in this target, not union: ...`, on both runs, on a dry run too. `doctor` exit 1: `journal attributes: merge resolves to binary, not union`. `-merge` (t4d) gives `merge=unset`, same handling. `doctor: clean` no longer follows it. Sync changes no project rule and exits 0 |
| E3-04 | Medium | **Closed** | `.workflow/` (t7), `*.jsonl` (t7b): `WARNING: .workflow/bugs.jsonl is ignored by this target's git rules: ...`. `doctor` exit 1: `journal ignored by git: ...`, with `--fix` too. Both problems at once (t7c, t12 with a space in its path): two warnings, both reported |
| E3-05 | Medium | **Closed** | Text: `release:53`, `qa:50`, `feature:172`, `fix:74`. Session start on the dirty journal now prints `Bugs: 8 open (5 High+); purge skipped, journal uncommitted` |
| E3-06 | Medium | **Closed** | `fix:17`, `bugs:31`: a `note` alone adds evidence and states that `evidence` is replaced. Run: note leaves `Evidence: .workflow/evidence/x/log.md` and adds `update by main session: second hit in run 7, see log2.md` |
| E3-07 | Medium | **Closed** | GD decision: `.workflow/DEBT.md`. Stated at `bugs:33`, `lifecycle:18`, `fix:32`, `fix:68`, `release:19`. `check-ignore` rc 1: not ignored, in a clone and in a synced target. Purge not run here (E1) |
| E3-08 | Low | **Closed** | `bugs:40` writes `--note N` with no brackets, stdin as the alternative. Run: no note, exit 1; stdin note, exit 0 |
| E3-09 | Low | **Closed** | `qa:12` writes `list --feature <slug> --open`. Run: returned the 3 demo bugs |
| E3-10 | Low | **Closed** | `bugs:11` names the `Memory:` line. Run: `Memory: ... Query: python3 -I .claude/skills/mem/scripts/mem.py q ...`; `Bugs:` names none, as stated |
| E3-11 | Low | **Closed** | `routing:57`: "The state file or bug record ...; used = file or database + hook" |
| E3-12 | Low | **Closed** | `fix:70` sets the note `awaits device verification`, `release:20` reads it. `show` prints it, so a marked bug and an unmarked one can be told apart (BUG-0013, BUG-0014). How to read it, and staleness: E3-17 |
| E3-13 | Low | **Closed** | `fix:18`, `bugs:30`, `lifecycle:6`: follow `duplicate_of`, judge the target. `show` prints `Duplicate of: BUG-0005` |
| E3-14 | Low | **Closed** | Created files LF only with one final newline, from LF and CRLF sources alike (t1, t1c: `CRLF=0 LF=9`). CRLF file stays CRLF (t2: `CRLF=7 LF=0`; `.gitignore` `CRLF=36 LF=0`). Mixed follows the majority (t2d), a tie takes LF (t2c) |

## GD decisions on record, not findings
- **Backlog settled without GD:** `BUG-0006 Backlog -> As designed` and `BUG-0007 Backlog -> Duplicate`, with no `--by`, both exit 0. `Backlog -> Request` and `Backlog -> Processing` stay refused or GD-only.
- **DEBT mirror for a no-feature bug:** `.workflow/DEBT.md`, as in E3-07.

## C12: invocation list and parse results
Every form in `bugs/SKILL.md`, `schema.md`, `fix`, `qa`, `qa-standards`, `feature`, `release`, `review`, `new-project`, `mem`, `qa-lead.md`, `routing.md` and the hook messages. `core.md` names only the journal path. `--root` on every row, as `bugs:18` writes it.

- **Parse errors: 0. Refused flags: 0.**
- 8 rows exit 1, all intended: no note on `set-status`, `round`, `extra-round`; `+101` twice; `+0`; `delete` with no `--by`; `import-md` with no file.
- `+100` passes on both round commands, matching `bugs:41-42`.
- `schema:103` (`test_bugs.py`) not run here: E1 owns it.

| Source | Form | Exit | Output (first 150 chars) |
|---|---|---|---|
| bugs:38 add | `add <stdin>` | 0 | BUG-0001 / |
| bugs:38 add --by | `add --by QA <stdin>` | 0 | BUG-0002 / |
| bugs:38 add, optional fields | `add <stdin>` | 0 | BUG-0003 / |
| bugs:39 update | `update BUG-0001 <stdin>` | 0 | BUG-0001 updated: evidence / |
| bugs:39 update --by | `update BUG-0001 --by QA <stdin>` | 0 | BUG-0001 updated: root_cause / |
| bugs:31,39, fix:17 update, note alone | `update BUG-0001 <stdin>` | 0 | BUG-0001 updated: note / |
| bugs:40 set-status --note | `set-status BUG-0001 Processing --note dispatched owner` | 0 | BUG-0001 Request -> Processing / |
| bugs:40 stdin replaces --note | `set-status BUG-0001 Request <stdin>` | 0 | BUG-0001 Processing -> Request / |
| bugs:40 negative: no note | `set-status BUG-0001 Processing` | 1 | bugs: note: required (--note, or {"note": ...} on stdin): who, what, the evidence reference / |
| bugs:41 round fix +1 | `round BUG-0001 fix +1 --note reopen by GD` | 0 | BUG-0001 fix 1/2 / |
| bugs:41 round review +1 | `round BUG-0001 review +1 --note workflow review round` | 0 | BUG-0001 review 1/3 / |
| bugs:41 negative: no note | `round BUG-0001 review +1` | 1 | bugs: note: required (--note, or {"note": ...} on stdin): who, what, the evidence reference / |
| bugs:41 boundary +100 | `round BUG-0001 review +100 --note upper bound` | 0 | BUG-0001 review 101/3 / |
| bugs:41 negative +101 | `round BUG-0001 review +101 --note over` | 1 | bugs: bad count '+101': expected +n with n from 1 to 100 / |
| bugs:41 negative +0 | `round BUG-0001 review +0 --note zero` | 1 | bugs: bad count '+0': expected +n with n from 1 to 100 / |
| bugs:42 extra-round fix | `extra-round BUG-0001 fix +1 --note GD order` | 0 | BUG-0001 fix 1/3 / |
| bugs:42 extra-round review +2 | `extra-round BUG-0001 review +2 --note GD order` | 0 | BUG-0001 review 101/5 / |
| bugs:42 negative: no note | `extra-round BUG-0001 review +1` | 1 | bugs: note: required (--note, or {"note": ...} on stdin): who, what, the evidence reference / |
| bugs:42 boundary +100 | `extra-round BUG-0001 review +100 --note upper bound` | 0 | BUG-0001 review 101/105 / |
| bugs:42 negative +101 | `extra-round BUG-0001 review +101 --note over` | 1 | bugs: bad count '+101': expected +n with n from 1 to 100 / |
| bugs:43 stop-rule fix unused | `stop-rule BUG-0001 fix --extra-dispatch unused` | 0 | BUG-0001 stop rule: fix, extra dispatch unused / |
| bugs:43 stop-rule fix used | `stop-rule BUG-0001 fix --extra-dispatch used` | 0 | BUG-0001 stop rule: fix, extra dispatch used / |
| bugs:43 stop-rule review unused | `stop-rule BUG-0001 review --extra-dispatch unused` | 0 | BUG-0001 stop rule: review, extra dispatch unused / |
| bugs:44 negative: delete, no --by | `delete BUG-0004` | 1 | bugs: delete is GD only: pass --by GD on the GD's order / |
| bugs:44 delete --by GD | `delete BUG-0004 --by GD` | 0 | deleted BUG-0004, journal uncommitted / |
| bugs:45 purge --dry-run | `purge --dry-run` | 0 | would purge 0 / |
| bugs:45 purge | `purge` | 0 | purged 0 / |
| bugs:45 purge --auto | `purge --auto` | 0 | purge skipped: journal not clean in git status / |
| bugs:46 import-md, no file | `import-md` | 1 | bugs: .workflow/bugs.md not found: nothing to import / |
| bugs:51 show | `show BUG-0001` | 0 | BUG-0001 \| High \| Request \| uid 427ae76c-7e67-4565-b22b-0991da8d9419 / Title: Save system loses coins / Description: Save system drops coins on slot t... |
| bugs:51 show --json | `show BUG-0001 --json` | 0 | { / "id": "BUG-0001", / "uid": "427ae76c-7e67-4565-b22b-0991da8d9419", / "title": "Save system loses coins", / "description": "Save system drops coins... |
| bugs:52 list | `list` | 0 | ID \| Priority \| Status \| Closed \| Feature \| Title / BUG-0001 \| High \| Request \| - \| demo \| Save system loses coins / BUG-0002 \| Low \| Request \| - \| - ... |
| bugs:52 list --status | `list --status Won't fix` | 0 | no bugs / |
| bugs:52 list --status | `list --status As designed` | 0 | no bugs / |
| bugs:52 list --priority | `list --priority High` | 0 | ID \| Priority \| Status \| Closed \| Feature \| Title / BUG-0001 \| High \| Request \| - \| demo \| Save system loses coins / |
| bugs:52 list --feature | `list --feature demo` | 0 | ID \| Priority \| Status \| Closed \| Feature \| Title / BUG-0001 \| High \| Request \| - \| demo \| Save system loses coins / BUG-0003 \| Medium \| Request \| - \|... |
| bugs:52 list --open | `list --open` | 0 | ID \| Priority \| Status \| Closed \| Feature \| Title / BUG-0001 \| High \| Request \| - \| demo \| Save system loses coins / BUG-0002 \| Low \| Request \| - \| - ... |
| bugs:52 list --json | `list --json` | 0 | [ / { / "id": "BUG-0001", / "uid": "427ae76c-7e67-4565-b22b-0991da8d9419", / "title": "Save system loses coins", / "description": "Save system drops c... |
| bugs:53, fix:15, lifecycle:6, mem:37 search | `search coins` | 0 | BUG-0001 \| High \| Request \| Save system loses coins / Save system loses [coins] / BUG-0002 \| Low \| Request \| HUD timer overlaps score / Save system dr... |
| bugs:53 search -n | `search coins -n 10` | 0 | BUG-0001 \| High \| Request \| Save system loses coins / Save system loses [coins] / BUG-0002 \| Low \| Request \| HUD timer overlaps score / Save system dr... |
| bugs:54 sql | `sql SELECT id, status FROM bug` | 0 | id	status / BUG-0001	Request / BUG-0002	Request / BUG-0003	Request / |
| bugs:54 sql --json | `sql SELECT id, status FROM bug --json` | 0 | [ / { / "id": "BUG-0001", / "status": "Request" / }, / { / "id": "BUG-0002", / "status": "Request" / }, / { / "id": "BUG-0003", / "status": "Request" ... |
| bugs:55 counters --json | `counters BUG-0001 --json` | 0 | {"id": "BUG-0001", "found": true, "settled": false, "status": "Request", "fix": {"used": 1, "cap": 3}, "review": {"used": 101, "cap": 105}, "record": ... |
| bugs:56 stats | `stats` | 0 | Bugs: 3 open (1 High+) / |
| bugs:61 rebuild | `rebuild` | 0 | rebuilt: 3 bugs, 17 events / |
| bugs:62 doctor | `doctor` | 0 | doctor: clean / |
| bugs:63 doctor --fix | `doctor --fix` | 0 | doctor: clean / |
| fix:16 add | `add <stdin>` | 0 | BUG-0005 / |
| fix:19 round fix | `round BUG-0001 fix +1 --note GD reports reopen` | 0 | BUG-0001 fix 2/3 / |
| fix:52, review:33 round review | `round BUG-0001 review +1 --note failed review round` | 0 | BUG-0001 review 102/105 / |
| fix:53, routing:60, round-cap:341 extra-round | `extra-round BUG-0001 fix +1 --note the order` | 0 | BUG-0001 fix 2/4 / |
| fix:54 stop-rule used | `stop-rule BUG-0001 review --extra-dispatch used` | 0 | BUG-0001 stop rule: review, extra dispatch used / |
| routing:58, round-cap:373 stop-rule | `stop-rule BUG-0001 fix --extra-dispatch unused` | 0 | BUG-0001 stop rule: fix, extra dispatch unused / |
| fix:70 marker | `update BUG-0001 <stdin>` | 0 | BUG-0001 updated: note / |
| qa:12, feature:148 list | `list --feature demo --open` | 0 | ID \| Priority \| Status \| Closed \| Feature \| Title / BUG-0001 \| High \| Request \| - \| demo \| Save system loses coins / BUG-0003 \| Medium \| Request \| - \|... |
| qa:42, qa-lead:22, lifecycle:5 show | `show BUG-0001` | 0 | BUG-0001 \| High \| Request \| uid 427ae76c-7e67-4565-b22b-0991da8d9419 / Title: Save system loses coins / Description: Save system drops coins on slot t... |
| review:17 counters, no --json | `counters BUG-0001` | 0 | {"id": "BUG-0001", "found": true, "settled": false, "status": "Request", "fix": {"used": 2, "cap": 4}, "review": {"used": 102, "cap": 105}, "record": ... |
| release:19 row 0b | `list --status Accepted --priority High --priority Highest` | 0 | no bugs / |
| release:20 row 1 | `list --open --priority High --priority Highest` | 0 | ID \| Priority \| Status \| Closed \| Feature \| Title / BUG-0001 \| High \| Request \| - \| demo \| Save system loses coins / |

### Stdin paths, `bugs:27-28`, `schema:51`
| Shell | Text | Result |
|---|---|---|
| 5.1 default | em dash | Stored `?` (U+003F), exit 0: the loss the text describes |
| 5.1 with the `$OutputEncoding` line | em dash | Stored U+2014 |
| 5.1 default | Vietnamese `U+1EA1` | Stored `?`, exit 0: evades the refusal, as stated |
| 5.1 with the line | Vietnamese | Refused: `title: Vietnamese diacritics` |
| pwsh 7 default, and with the line | em dash | Stored U+2014 |
| pwsh 7 with the line | Vietnamese | Refused, exit 1 |
| Git Bash heredoc | em dash, `$x`, backticks | Stored byte-exact |
| Git Bash heredoc | Vietnamese | Refused, exit 1 |

## C12: `git grep`
### `bugs.md`, `bugs-template`
`git grep -n -I -E "bugs\.md|bugs-template" 349542e -- . ':!.workflow'`: 34 hits. All guards against a remaining old file, migration code, or tests of those. **0 live references** to it as the store. `bugs-template` has 0 hits. `.workflow/bugs.md` is still in the tree: C15 removes it after the merge.

```
.claude/hooks/round-cap.ps1:174:# the CLI cannot answer. No journal and no old bugs.md: no bugs yet, and Python never starts.
.claude/hooks/round-cap.ps1:179:    if (-not (Test-Path -LiteralPath (Join-Path $workflow 'bugs.jsonl')) -and -not (Test-Path -LiteralPath (Join-Path $workflow 'bugs.md')...
.claude/hooks/session-start.ps1:49:    if (Test-Path -LiteralPath (Join-Path $workflow 'bugs.md')) { return 'Bugs: .workflow/bugs.md is still present - run bugs.py import...
.claude/hooks/tests/run.ps1:730:    Check 'round-cap: an edit under .workflow names no bug any more' (EditState (Join-Path $proj '.workflow/bugs.md')) 0
.claude/hooks/tests/run.ps1:836:    Check 'round-cap: no journal and no bugs.md pass without Python' (NoPython { Dispatch 'Fix BUG-0001' }) 0
.claude/hooks/tests/run.ps1:838:    $oldBugs = Join-Path $proj '.workflow/bugs.md'
.claude/hooks/tests/run.ps1:841:    Check 'round-cap: a remaining bugs.md blocks a bug dispatch, naming import-md' ($r.Code -eq 2 -and $r.Out -match 'import-md') $true
.claude/hooks/tests/run.ps1:842:    Check 'round-cap: a remaining bugs.md leaves other dispatches alone' (Dispatch 'Explain the HUD') 0
.claude/hooks/tests/run.ps1:1092:    Set-Content (Join-Path $bp '.workflow/bugs.md') "# Bugs`n" -Encoding UTF8
.claude/hooks/tests/run.ps1:1094:    Check 'session-start: a remaining bugs.md prints one import-md line' ($r.Code -eq 0 -and @($r.Out -split '\r?\n' | Where-Object { $_ ...
.claude/hooks/tests/run.ps1:1096:    Remove-Item (Join-Path $bp '.workflow/bugs.md')
.claude/skills/bugs/references/schema.md:84:- **Exit:** unknown or purged ID `found:false`, exit 0. Duplicate ID, corrupt journal or a remaining `bugs.md`: non-zero with ...
.claude/skills/bugs/scripts/bugs.py:368:        return self.workflow / "bugs.md"
.claude/skills/bugs/scripts/bugs.py:1506:        raise Refused(".workflow/bugs.md not found: nothing to import")
.claude/skills/bugs/scripts/bugs.py:1547:    print("imported %d bugs, %d events; delete .workflow/bugs.md next" % (new_bugs, new_events))
.claude/skills/bugs/scripts/bugs.py:1607:    sub.add_parser("import-md", help="one-way migration from .workflow/bugs.md; the caller deletes the file")
.claude/skills/bugs/scripts/bugs.py:1649:            raise Refused(".workflow/bugs.md exists: run import-md, delete the file, then retry")
.claude/skills/bugs/scripts/test_bugs.py:42:# Copied from .workflow/bugs.md on 2026-11-03: the import has to take today's real file.
.claude/skills/bugs/scripts/test_bugs.py:1448:        (self.root / ".workflow" / "bugs.md").write_text("# Bugs\n", encoding="utf-8")
.claude/skills/bugs/scripts/test_bugs.py:1456:                self.assertIn("bugs.md", self.no(*argv, stdin=fields() if argv[0] == "add" else None))
.claude/skills/bugs/scripts/test_bugs.py:1463:        with open(p / "bugs.md", "w", encoding="utf-8", newline="") as f:
.claude/skills/bugs/scripts/test_bugs.py:1465:        return p / "bugs.md"
.claude/skills/bugs/scripts/test_bugs.py:1540:        self.assertIn("bugs.md", self.no("list"))
.claude/skills/bugs/scripts/test_bugs.py:1543:        self.assertIn("bugs.md", self.no("import-md"))
.claude/skills/bugs/scripts/test_bugs.py:1603:        (self.root / ".workflow" / "bugs.md").unlink()
.claude/skills/bugs/scripts/test_bugs.py:1974:        (self.root / ".workflow" / "bugs.md").write_text(REAL_BUGS_MD, encoding="utf-8")
.claude/skills/bugs/scripts/test_bugs.py:1990:        (self.root / ".workflow" / "bugs.md").write_text("# Bugs\n", encoding="utf-8")
.claude/skills/bugs/scripts/test_bugs.py:1991:        self.assertIn("bugs.md", self.no("list", root=self.wt))
.claude/skills/bugs/scripts/test_bugs.py:2186:        md = self.root / ".workflow" / "bugs.md"
.claude/skills/bugs/scripts/test_bugs.py:2504:        md = self.root / ".workflow" / "bugs.md"
.claude/skills/bugs/scripts/test_bugs.py:2577:        (self.root / ".workflow" / "bugs.md").write_text(REAL_BUGS_MD, encoding="utf-8")
.claude/skills/bugs/scripts/test_bugs.py:2579:        (self.root / ".workflow" / "bugs.md").unlink()
.claude/skills/bugs/scripts/test_bugs.py:2583:        (self.root / ".workflow" / "bugs.md").write_text("# Bugs\n", encoding="utf-8")
.claude/skills/bugs/scripts/test_bugs.py:2586:                self.assertIn("bugs.md", self.no(*argv, stdin=fields() if argv[0] == "add" else None))
```

### Old statuses
`git grep -n -I -E "\b(Open|Fixed|Closed|Reopened)\b" 349542e -- . ':!.workflow'`: 139 hits. **0 live hits use an old status on a bug.**
- Migration: `schema:96`, `bugs.py:1299,1302,1416,1417`, `test_bugs.py`.
- Column label for `closed_at`: `bugs.py:1017,1073`.
- Feature status: `round-cap:158`, `session-start:23`, `feature:152`, `feature-template:3`, `verify:55`, `fix:25`, `hooks/tests/run.ps1`.
- Framework backlog: `templates/framework-backlog.md:3,6`.
- Plain English "open": `qa-lead:29`, `feature:148,171`, `release:20`, `schema:6,75`.
- Unrelated words (Flexalon, DOTween, `File.Open`, `Fixed Update`, step titles): per the brief, not findings.

```
.claude/agents/qa-lead.md:29:- [ ] **Open bugs cased:** Plan — every open bug of this feature → a case — evidence: bug ID → case. No open bug → `n/a`.
.claude/agents/technical-architect.md:40:- **`Open questions:`** tagged design | architecture | technology.
.claude/agents/technical-architect.md:75:- **Design questions:** answer one without a clear default → the GD's: list it under `Open questions:`.
.claude/hooks/round-cap.ps1:109:        try { $fs = [IO.File]::Open($ledgerPath, 'OpenOrCreate', 'ReadWrite', 'None') } catch { Start-Sleep -Milliseconds 100 }
.claude/hooks/round-cap.ps1:158:    if ($text -notmatch '(?m)^- Status:\s*Open') { return @() }
.claude/hooks/session-start.ps1:23:        if ($text -match '(?m)^- Status:\s*Open\b') {
.claude/skills/bugs/references/schema.md:6:- **Open (every status but the terminal five):** `Request` · `Processing` · `Resolved` · `Review` · `Reopen` · `Backlog`.
.claude/skills/bugs/references/schema.md:75:- **Rule:** terminal for strictly more than 90 days. Open and `Backlog` bugs never go. IDs are never reused.
.claude/skills/bugs/references/schema.md:96:- **Mapping:** `Open` → `Request` · `Fixed` → `Resolved` · `Closed` → `Complete` · `Reopened` → `Reopen`; the other four keep ...
.claude/skills/bugs/scripts/bugs.py:1017:              ("Duplicate of", "duplicate_of"), ("Created", "created_at"), ("Updated", "updated_at"), ("Closed", "closed_at"))
.claude/skills/bugs/scripts/bugs.py:1073:    print("ID | Priority | Status | Closed | Feature | Title")
.claude/skills/bugs/scripts/bugs.py:1299:OLD_STATUS = {"Open": "Request", "Fixed": "Resolved", "Closed": "Complete", "Reopened": "Reopen",
.claude/skills/bugs/scripts/bugs.py:1302:RX_HISTORY = re.compile(r"(?:(?<=\s)|^)(\d{4}-\d{2}-\d{2}) (Open|Fixed|Closed|Reopened|Won't fix|Accepted|As designed|Duplicate)\...
.claude/skills/bugs/scripts/bugs.py:1416:    if history and history[0][1] != "Open":
.claude/skills/bugs/scripts/bugs.py:1417:        problems.append("%s History: must start with Open" % bug_id)
.claude/skills/feature/SKILL.md:16:## 0. Open
.claude/skills/feature/SKILL.md:55:- **`Open questions:`:** routed by kind:
.claude/skills/feature/SKILL.md:148:  - **Open items:** open bugs (`bugs.py list --feature <slug> --open`) · limitations · gates declined · what did not run.
.claude/skills/feature/SKILL.md:152:- **Close:** `Status: Closed`; each accepted gap into the feature root's `DEBT.md`; the backlog row → `done`.
.claude/skills/feature/SKILL.md:171:- **Open bugs:** `Won't fix`, `--by GD`: abandoning is the GD's order.
.claude/skills/feature/references/feature-template.md:3:- Status: Open | Closed | Abandoned
.claude/skills/fix/SKILL.md:25:- **Closed feature:** a closed feature stays `Closed`.
.claude/skills/release/SKILL.md:20:| 1 | Open bugs | main session | No High or Highest unsettled, `Backlog` included (`bugs.py list --open --priority High --priority High...
.claude/skills/verify-layer/scripts/verify.ps1:55:    '.claude/skills/feature/references/feature-template.md' = @('- Status: Open', '- Size:', '- Rounds:', '## GD decisio...
.claude/templates/framework-backlog.md:3:Open work on the agent framework (`.claude/`) found while working in this repo: a wrong rule, a gap in an agent or skill, a hook ...
.claude/templates/framework-backlog.md:6:- Add a row when found; close it with what closed it (commit sha or path). State: `Open` · `Done: <sha or path>` · `Recorded` (kn...
README.md:82:Open Claude Code in the project once and accept the trust dialog. Until you do, the project's permissions and hooks are ignored. Then run `/verify-layer` aft...
```

### Severity on bugs
`git grep -n -I -i severity 349542e -- .claude README.md`: 79 hits. **0 live hits put Severity on a bug.** Bug-side hits: `lifecycle:25` ("never Severity"), `qa-standards:38` (the mapping), `schema:11`, and `bugs.py` refusal and import. The rest are findings, kept per GD decision 4. `add` with `severity`: `add: unknown field: severity (status starts at Request; bugs have a priority, no severity)`.

### Two files merged from `develop`
No contradiction. `qa-automation-engineer.md:22` and `code-coverage.md:22` agree with `fix:58-60`; `:53` is the `Repro:` line. Neither names a status.

## C12: the walk, indicative, text plus CLI
All exit 0 unless stated.

| Text | Driven | Result |
|---|---|---|
| Setup, no journal | `list`, `stats`, `doctor` | `no bugs`, 0 open, `doctor: clean`: E3-15 |
| `new-project:70`, `feature:70` | Empty file; `search`, rows 0b and 1, `stats`, `doctor`, `purge --auto` | All empty and clean. `purge skipped: journal not clean in git status` while untracked |
| `feature:70` placement | Read | First bullet of step 4, before the branch. Step 1's S exit and step 3 pass without it. `feature:14` keeps `.workflow/` out of step 4 commits; `feature:153` commits it at CP4 |
| `fix:16` | `add` with the listed fields | `BUG-0001`, `Request` |
| `fix:17` | `update` with a note, then `evidence` | E3-06 |
| `fix:18` terminal | `Complete` to `Reopen` | Pass |
| `fix:18` Backlog | `Backlog` to `Reopen` refused; `update` note | Pass, as written |
| `fix:18` Duplicate | `show` | `Duplicate of:` printed |
| `fix:19` | `round <id> fix +1` | `fix 1/2` |
| `fix:20` | `Resolved` to `Reopen` | Exit 1, `is not in the state machine`. Then `Review`, `Reopen` pass |
| `fix:32` | `Won't fix` with and without `--by GD` | Refused, then pass |
| `fix:35`, `fix:50` | `Processing`, `Request`, `Processing` | Pass. `Processing` to `Processing` refused; the text never orders it |
| `fix:52-54` | `round`, `extra-round`, `stop-rule` | `review 1/3`, `fix 1/3`; `record` carries both lines |
| `fix:61-65` | `Resolved`, `Review`, then each of `Resolved`, `Reopen`, `Complete` | All pass, `Closed:` set on `Complete` |
| `fix:68` | `Accepted` with and without `--by GD` | Refused, then pass |
| `lifecycle` table | `Duplicate` with no target refused, with target pass; `As designed` pass | Matches |
| `lifecycle:23` | Into and out of `Backlog`; `counters` `settled: true` | Matches |
| `qa:12`, `qa:33`, `qa:42` | `list --feature demo --open`; `Review`, `Complete`; `list --feature demo`, `show` | Pass |
| `qa:50` | `git status` after moves | Journal uncommitted, as the report must say |
| Row 0b | `list --status Accepted --priority High --priority Highest` | BUG-0004 High, BUG-0016 Highest. Medium absent |
| Row 1 | `list --open --priority High --priority Highest` | High and Highest in `Backlog` listed, so they block; `Reopen`, `Resolved` listed; Medium Backlog and High `Complete` absent |
| Row 4 live | `Review`, `Complete`, row 1 again | Marked bug leaves the list |
| `release:10-11`, `--dry-run` | Rows 0b and 1; hook fixture | Journal hash `8A9D1456DC27` before and after. Hook charges nothing: E3-02 |
| `release:53` | `git status`, `purge --auto` | Journal uncommitted; purge skipped |
| `release:38` Python absent | Row 1 with no `python` on PATH | Process exit 1, `The term 'python' is not recognized`. Not a pass |
| `release:38` CLI error | `bugs.md` present; a non-JSON journal line | Exit 1: `.workflow/bugs.md exists: ...`; `corrupt journal: line 105: JSONDecodeError` |
| Abandon, `feature:170-172` | `list --feature dropped --open`, then `Won't fix --by GD` from `Request`, `Processing`, `Resolved`, `Review`, `Reopen`, `Backlog` | All 6 pass, list then `no bugs`, journal uncommitted, report line ordered. No moves at all: E3-16 |

Status moves agreed across `fix`, `lifecycle`, `schema` and the CLI on every move driven. The 121-pair matrix is E1's.

## New defects
Owner names the author role; the fixing agent for skill text is otherwise unclear. All repros are deterministic, 1 attempt, 1 hit, from a temp main checkout at `349542e` with `.workflow/bugs.md` removed unless a step restores it.

### E3-15 Medium: migrating a zero-row `bugs.md` leaves no journal, so the release gate fails
- **Location:** `import-md` in `.claude/skills/bugs/scripts/bugs.py`; `bugs/SKILL.md:46`; `release/SKILL.md:38`; `schema.md:65`.
- **Expected:** an adopted project with no bugs passes rows 0b and 1. Source: `schema:65` makes a missing journal "a broken setup" and says what creates it; spec, Migration, covers adopted game projects after a framework sync.
- **Actual:** `import-md` on `develop`'s real template reports success and creates nothing. After the ordered delete there is no journal, so `release:38` gives "not a pass" on a project that did nothing wrong. Nothing flags it: `doctor` is clean, exit 0, and session start prints no `Bugs:` line. A later `/feature` step 4 or first `add` repairs it.
- **Evidence:** `imported 0 bugs, 0 events; delete .workflow/bugs.md next`; `journal after import: False`; `list` `no bugs`; `doctor: clean`; `Bugs lines: []`.
- **Owner:** T1 author (`import-md`, `doctor`).
- **Repro:** 1. Write `develop:.claude/skills/fix/references/bugs-template.md` to `.workflow/bugs.md`. 2. `import-md`. 3. Delete the file, as ordered. 4. Test for `.workflow/bugs.jsonl`.

### E3-16 Low: Abandon with no bug moves does not report the untracked journal
- **Location:** `feature/SKILL.md:70,172`.
- **Expected:** an untracked journal the pipeline created gets reported. Source: `feature:70` ("so an S exit leaves no untracked file"), and `feature:172` for moves.
- **Actual:** step 4 creates the file, and only CP4 commits it. An Abandon past step 4 with no open bugs has no "those moves", so no report line. Session start catches it later.
- **Evidence:** `?? .workflow/bugs.jsonl`; `Bugs: 0 open (0 High+); purge skipped, journal uncommitted`.
- **Owner:** T3 author.
- **Repro:** Empty untracked journal, no bugs; apply `feature:170-172`; run `git status` and `session-start.ps1`.

### E3-17 Low: row 1 names no command that reads the marker, and the marker outlives a failed verification
- **Location:** `release/SKILL.md:20`, `fix/SKILL.md:70`.
- **Expected:** step 1 can read the note. Source: `fix:70` ("which `/release` step 1 reads").
- **Actual:** the row's `list` prints no notes, and `list --json` has no event field. A session must add `show` per bug, unstated. And the note stays after `Reopen` and a new fix, so a bug no longer waiting on a device still reads as marked. Low because row 4 re-runs every bug it defers.
- **Evidence:** `list --json` keys end at `closed_at`, marker absent. After `Review`, `Reopen`, `Processing`, `Resolved`, the join on `note='awaits device verification'` still returns BUG-0015.
- **Owner:** T3 author.
- **Repro:** `Resolved`; `update` with the note; `Review`, `Reopen`, `Processing`, `Resolved`; `show`.

### E3-18 Low: `.workflow/DEBT.md` is missing from the other places a mirror matters
- **Location:** `fix/SKILL.md:74`, `qa/SKILL.md:50`, `release/SKILL.md:53`, `feature-docs/SKILL.md:32`.
- **Expected:** the location itself is the GD's decision and not in question. A file the session writes is reported uncommitted beside the journal, and known debt is read before filing. Source: spec, "Journal commits", for the pattern; `feature-docs:32`.
- **Actual:** those report lines name only `.workflow/bugs.jsonl`. `feature-docs:20,32` covers only feature-root docs, so an accepted no-feature gap can be filed again.
- **Evidence:** `git grep -F ".workflow/DEBT.md"` hits live text only at `bugs:33`, `fix:32,68`, `lifecycle:18`, `release:19`.
- **Owner:** T3 author.
- **Repro:** Run that grep; read the four lines.

### E3-19 Low: `eol=crlf` from a later rule draws no warning
- **Location:** `framework-sync.ps1` journal check; `doctor`; `schema.md:53,59`.
- **Expected:** the journal is LF. Source: spec, Consistency item 5, `text eol=lf merge=union`; `schema:53`.
- **Actual:** both checks read `merge` only, as `schema:59` documents. With `.workflow/** eol=crlf` after the framework line, sync and `doctor` are silent. The CLI still reads a CRLF journal, then appends LF, which leaves it mixed. Nothing failed here; a merge under this rule did not run.
- **Evidence:** t4e `check-attr`: `text: set ; eol: crlf ; merge: union`; `doctor: clean`; after a CRLF rewrite and one `add`: `CRLF=1 LF=1`, `list` exit 0.
- **Owner:** T3 author (sync), T1 author (`doctor`).
- **Repro:** Target t4e in the table below.

## C13: `framework-sync.ps1`, target by target
`-Mode Install`, pwsh 7, LF source unless stated, each run twice, `core.autocrlf=false` unless stated. "Warn" is the journal warning; every run exits 0.

| Target | Start | Sync says | `merge` | Journal ignored | Warn | `.gitattributes` EOL | `doctor` |
|---|---|---|---|---|---|---|---|
| t1 | No files | created, created | union | no | none | LF=9 | 0 |
| t1c | No files, CRLF source | created, created | union | no | none | LF=9 | 0 |
| t2 | Both CRLF | 3 and 32 appended | union | no | none | CRLF=7 LF=0 | 0 |
| t2b | CRLF, no final newline | 3 and 32 appended | union | no | none | CRLF=6 LF=0 | 0 |
| t2c | Mixed, a tie | 3 appended | union | no | none | CRLF=1 LF=6 | 0 |
| t2d | Mixed, CRLF majority | 3 appended | union | no | none | CRLF=7 LF=1 | 0 |
| t3 | All lines present, LF | up to date, 0 bytes | union | no | none | LF=4 | 0 |
| t3b | Bug line present, CRLF | 2 appended, no duplicate | union | no | none | CRLF=6 LF=0 | 0 |
| t4 | Conflicting line first | 3 appended | union | no | none | LF=6 | 0 |
| t4b | Framework line, then `.workflow/** -text merge=binary` | 2 appended | **binary** | no | **merge** | LF=6 | **1** |
| t4c | Broad rule only | 3 appended | union | no | none | LF=6 | 0 |
| t4d | Framework line, then `-merge` | 2 appended | **unset** | no | **merge** | LF=6 | **1** |
| t4e | Framework line, then `eol=crlf` | 2 appended | union | no | none (E3-19) | LF=6 | 0 |
| t5 | LF, no final newline | 3 and 32 appended | union | no | none | LF=5 | 0 |
| t6 | BOM and CRLF | 3 and 32 appended, BOM kept | union | no | none | CRLF=6 LF=0 | 0 |
| t7 | `.gitignore` has `.workflow/` | 32 appended | union | **yes** | **ignored** | LF=9 | **1** |
| t7b | `.gitignore` has `*.jsonl` | 32 appended | union | **yes** | **ignored** | LF=9 | **1** |
| t7c | Defeated and ignored | 2 and 32 appended | **binary** | **yes** | **both** | LF=6 | **1** |
| t11 | `core.autocrlf=true`, CRLF file | 3 appended | union | no | none | CRLF=6 LF=0 | 0 |
| t12 | Path with a space, defeated and ignored | 2 and 32 appended | **binary** | **yes** | **both** | LF=6 | **1** |

- **`bugs.db` and `bugs.db-wal` ignored:** yes on all 20.
- **Second run:** `.gitattributes` and `.gitignore` byte-identical on all 20. Only `.claude/.framework-manifest.json` changed. It is identical once `syncedAt` is removed (checked on t3, third run).
- **t8 `-DryRun`:** 0 files changed on an empty target, on existing files, on t4b and on t7. Up-to-date t4b and t7 print their warnings. A dry run that would append lines gives no merge warning, as the code comment says.
- **t9 `-Mode Update`:** a hand-removed line is appended again, `merge: union`. A retired `bugs-template.md` recorded in the manifest: `removed ... (retired by the framework)`, file gone.
- **t10 Windows PowerShell 5.1, expected refusal:** exit 1, 0 files changed: `The script 'framework-sync.ps1' cannot be run because it contained a "#requires" statement for Windows PowerShell 7.0.` `install-framework.ps1` is refused the same way.
- **t13 `install-framework.ps1` on pwsh 7:** exit 0, 3 appended, `merge: union`. It warns that the checkout has no origin remote, true of my temp source.
- **After a sync:** t1 `add` gives `BUG-0001`, `doctor: clean`, `?? .workflow/`, journal `CRLF=0 LF=1`, first bytes `7B 22 65`, no BOM. Synced `bugs.py` hash equals the source. t7 `add` passes and git shows nothing, but `doctor` exits 1. A leftover `bugs.md` (t5): `list` exit 1, `.workflow/bugs.md exists: run import-md, delete the file, then retry`.

### `.gitattributes` diffs, before to after
`git diff --no-index`, `cr-at-eol`, so CR does not show; the EOL column above has the bytes. t3 has an empty diff.
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
--- t2b-crlf-nofinal
@@ -1,2 +1,6 @@
 *.png filter=lfs -text
-*.unity merge=unityyamlmerge
\ No newline at end of file
+*.unity merge=unityyamlmerge
+# Added by the AI-For-Game framework
+.memory/traces/** text eol=lf linguist-generated
+.claude/skills/**/scripts/*.sh text eol=lf
+.workflow/bugs.jsonl text eol=lf merge=union
--- t2c-mixed-tie
@@ -1,2 +1,7 @@
 *.png filter=lfs -text
 *.unity merge=unityyamlmerge
+
+# Added by the AI-For-Game framework
+.memory/traces/** text eol=lf linguist-generated
+.claude/skills/**/scripts/*.sh text eol=lf
+.workflow/bugs.jsonl text eol=lf merge=union
--- t2d-mixed-crlf-major
@@ -1,3 +1,8 @@
 *.png filter=lfs -text
 *.fbx -text
 *.unity merge=unityyamlmerge
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
--- t4b-defeated
@@ -1,2 +1,6 @@
 .workflow/bugs.jsonl text eol=lf merge=union
 .workflow/** -text merge=binary
+
+# Added by the AI-For-Game framework
+.memory/traces/** text eol=lf linguist-generated
+.claude/skills/**/scripts/*.sh text eol=lf
--- t4c-rule-first
@@ -1 +1,6 @@
 .workflow/** -text merge=binary
+
+# Added by the AI-For-Game framework
+.memory/traces/** text eol=lf linguist-generated
+.claude/skills/**/scripts/*.sh text eol=lf
+.workflow/bugs.jsonl text eol=lf merge=union
--- t4d-unset-merge
@@ -1,2 +1,6 @@
 .workflow/bugs.jsonl text eol=lf merge=union
 .workflow/bugs.jsonl -merge
+
+# Added by the AI-For-Game framework
+.memory/traces/** text eol=lf linguist-generated
+.claude/skills/**/scripts/*.sh text eol=lf
--- t4e-eol-crlf
@@ -1,2 +1,6 @@
 .workflow/bugs.jsonl text eol=lf merge=union
 .workflow/** eol=crlf
+
+# Added by the AI-For-Game framework
+.memory/traces/** text eol=lf linguist-generated
+.claude/skills/**/scripts/*.sh text eol=lf
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
--- t11-autocrlf
@@ -1 +1,6 @@
 *.png filter=lfs -text
+
+# Added by the AI-For-Game framework
+.memory/traces/** text eol=lf linguist-generated
+.claude/skills/**/scripts/*.sh text eol=lf
+.workflow/bugs.jsonl text eol=lf merge=union
```

`.gitignore`: appended as `+.workflow/bugs.db*` under `+# Added by the AI-For-Game framework` in t2, t2b, t5, t6, t7. Present in the created file on t1.

## Exit criteria
| Criterion | Result |
|---|---|
| Baseline, `verify.ps1` | Exit 0, 21 warnings, 0 `FAIL` at `349542e` |
| 8 | Parse: 0 errors, 0 refused flags on 59 rows. Grep: 0 live hits for `bugs.md` as the store, old statuses or bug Severity. Walk: E3-15 to E3-18, indicative |
| 10 | Line installed and effective on every target with no overriding project rule. Second-run diff empty on both files. Dry run writes nothing. 5.1 refused, as expected. A defeated `merge=union` and an ignored journal both warn. E3-19 is outside that check |

## Not covered:
- A real `/fix`, `/qa`, `/release` session: this walk is indicative. Owner: main session or GD, fresh session after the merge.
- `/release` row 4's build, device and a live `Verify:` dispatch. Owner: `build-release-engineer`.
- `test_bugs.py`, the 121-pair matrix, purge, real union merges, and the `Purged ID` and refusal-text clauses of `schema.md`. Owner: E1.
- Hook behaviour beyond the 4 dry-run returns and the session-start lines, including `Get-BugsRoot` and `Hook spelling`. Owner: E2.
- `update-framework.ps1` end to end, including its remote fetch; `-Force`; a target with an existing `settings.json`. Owner: T3 author or main session.
- Python 3.10 runtime. Owner: GD (C14 is static, E1).
- Criterion 9 and the removal of `.workflow/bugs.md`. Owner: main session (C15).

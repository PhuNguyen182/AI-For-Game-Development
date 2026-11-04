# E2 report - PowerShell and hooks (sqlite-bug-tracker, attempt 1)

Saved by the main session from executor E2's return: its Write call was refused by the tool. Full fixture tables sit beside this file as `e2-table-*.md`, copied from E2's harness output. No result below was produced by the main session.

- Executor: E2, independent of the T1, T2 and T3 authors. Size L, no risk flag.
- Revision: `b6deca7`, from `git archive`.
- Cases: C0 (`hooks/tests/run.ps1` only), C8, C9, C10 of `qa-plan.md`.
- Oracle: spec sections "Hook: round-cap.ps1" and "Purge trigger", `routing.md` Stop rule, and the `round-cap.ps1` header where the spec is silent. `tests/run.ps1` was not used for expected values.
- Environment: Windows 11, pwsh 7.6.9, Windows PowerShell 5.1.26100.9711, Python 3.14.7, SQLite 3.50.4, git 2.56.0.windows.2.

## Result
| Case | pwsh 7 | Windows PowerShell 5.1 |
|---|---|---|
| C0 suite | 600 pass, 0 fail, exit 0 | 599 pass, 1 fail, exit 1 (2 runs, same failure) |
| C8 + C9 + C10 harness (181 cases per shell) | 178 match, 3 do not | 170 match, 11 do not |

| Criterion 7 claim | Result | Evidence |
|---|---|---|
| Past the cap blocks, at or under allows | Pass on both | D01-D08 |
| Extra round raises only that cap | Pass on both | D22-D26, E13 |
| Stop rule recorded; silences only that counter at the cap | Pass on both | D27, D28, E10-E12 |
| Settled and Backlog not capped; reopened is capped again | Pass on both | D14-D21, E08, E09 |
| No Python blocks; no journal allows with no Python start | Pass on both | D67-D76 |
| CLI error blocks | Pass on both | D78, D79, D81, D83-D87 |
| `Verify:` with `Repro: reproduces` counted | Pass on both | D44-D50, D91 |
| Cap warning after a `bugs.py` call, none on other calls | Pass on both | E01-E16 |
| Session-start purge conditions; never commits; never blocks | Pass on both | S01-S29 |
| C10 byte-exact from pwsh 7 | Pass | C01-C13, C15, C16, C18 |
| C10 byte-exact from 5.1 | **Fail** on the default pipe, F1 | C01, C02, C03, C10, C11, C12, C17 |

Mismatches: D61 and D66 on both shells (F4, F2); C01, C02, C03, C10, C11, C12, C17 on 5.1 (F1); S21 on both (E2's regex over-asserted, the oracle clause is met); D87 on 5.1 (E2's timer, replaced by D87b).

## Conflict between the plan and the oracle: needs qa-lead
`qa-plan.md` C8 says `used` at cap-1, cap, cap+1 gives "allow, block, block". `routing.md` says it blocks "past a cap", and at the cap "the owner gets one more dispatch"; the spec's verification list says "past cap blocks". E2 judged against the oracle: allow, allow, block. The code does this on both shells (D01-D03, D05-D07). No defect filed.

## Defects

### F1 - High - Windows PowerShell 5.1's default pipe silently replaces non-ASCII text with `?`, and evades the Vietnamese refusal
- **Location:** `.claude/skills/bugs/SKILL.md:27` ("Send UTF-8", with no form for doing it); reaches `bugs.py` `read_stdin_json`, which cannot tell a `?` from typed text.
- **Expected:** C10: stdin JSON from 5.1 reaches the journal byte-exact. Spec: "the CLI refuses text with Vietnamese diacritics in any field".
- **Actual:** with 5.1's default `$OutputEncoding` (us-ascii), `add`, `update`, `round` and `set-status` exit 0 and write `?` per non-ASCII UTF-16 unit. Vietnamese text is accepted, not refused. No warning. pwsh 7 is correct.
- **Evidence:** C17 title on 5.1, exit 0, prints `BUG-0001`, bytes `54 69 3f 75 20 3f 3f 20 6c 3f 69`; pwsh 7, exit 1: `bugs: title: Vietnamese diacritics ('ê'): the database is English only, translate first`. C03: `$OutputEncoding = New-Object Text.UTF8Encoding $false` also gives `?` on 5.1, cause not established. Forms that work on 5.1: C04 `[Text.Encoding]::UTF8`, C18 `[Text.UTF8Encoding]::new($false)`, C05 and C06 file on stdin through `cmd`, C07 raw bytes, C08 `\uXXXX` escapes.
- **Owner:** T1 author. Obvious change: a stdin rule in `SKILL.md` naming a form that works on both shells.
- **Severity reason:** wrong on a normal path for any session whose PowerShell is 5.1. Not Critical: the loss is limited to non-ASCII characters in records that are English only by rule.
- **Repro:** temp git repo with `.claude/` at `b6deca7`, in `powershell.exe`: `$j | python -I <bugs.py> --root <repo> add`, with `$j` holding an em dash in `title`; read the journal as bytes. C01, C02, C03, C10, C11, C12: 2 of 2 runs. C17: 1 of 1.

### F2 - Medium - A linked worktree with no journal file gets no bug caps
- **Location:** `.claude/hooks/round-cap.ps1:32`, `:178`; `.claude/hooks/common.ps1:231-243` (`Get-MainCheckout` resolves only `.claude/worktrees/<name>`).
- **Expected:** spec, Consistency 8: "Reads use the main checkout". `round-cap.ps1:31` says the same.
- **Actual:** `CLAUDE_PROJECT_DIR` at a linked worktree outside `.claude/worktrees/`, on a branch with no journal: the hook tests that worktree's path, finds nothing, and allows a dispatch for a bug past its cap in the main checkout.
- **Evidence:** D66, exit 0, stderr empty, both shells; main DB `BUG-0004 Request fix 3/2`. Controls that block: D62, D63, D64, D65.
- **Owner:** T2 author.
- **Repro:** file a bug in main, `round <id> fix +3`, commit; `git worktree add <outside path> -b x <commit before the journal>`; feed `-Mode dispatch` `{"tool_name":"Agent","tool_input":{"prompt":"Bug: <id>"}}` with `CLAUDE_PROJECT_DIR=<outside path>`. 2 of 2 runs.

### F3 - Medium - A malformed bug ID on a `Bug:` line, or a lowercase or unpadded ID in free text, skips the cap check
- **Location:** `.claude/hooks/round-cap.ps1:210` (`Get-BugMarker`), `:214` (`Get-BugIds`, case-sensitive, 4+ digits).
- **Expected:** `round-cap.ps1:12`: "A brief naming a bug fails closed". `bugs.py` refuses `BUG-27` and `bug-0027`, so a checked call would block. The spec does not define ID forms; this reading is E2's.
- **Actual:** the same past-cap bug by spelling: `Bug: bug-0027` exit 2 (D39); `Bug: BUG-27` exit 0 (D41); `Fix BUG-27` exit 0 (D40); `Fix bug-0027` exit 0 (D38).
- **Evidence:** D38-D41 on both shells; DB `BUG-0027 Request fix 3/2`.
- **Owner:** T2 author.
- **Repro:** `round BUG-0027 fix +3`, then feed the dispatch JSON with each brief. 2 of 2 runs.

### F4 - Medium - An over-padded ID drops the ledger events from the used count
- **Location:** `.claude/hooks/round-cap.ps1:191`: ledger key `bug:$id` uses the brief's spelling, while `bugs.py` canonicalises the ID.
- **Expected:** spec: "Used stays file + ledger".
- **Actual:** `Bug: BUG-00036`, DB `fix 2/2`, ledger `bug:BUG-0036` holding one `verify-*` event: exit 0. True count 3/2; the canonical form blocks (D45).
- **Evidence:** D61 on both shells, exit 0, stderr empty.
- **Owner:** T2 author.
- **Repro:** `round <id> fix +2`; run `-Mode count` with a `Verify: <id>` transcript and `Repro: <id> reproduces`; dispatch `Bug: BUG-0<4 digits>`. 2 of 2 runs.

### F5 - Medium - The hook suite fails on Windows PowerShell 5.1 at console width 120
- **Location:** `.claude/hooks/tests/run.ps1:17-18` (`2>&1`, then `Out-String`), `:725` (the assertion).
- **Expected:** the suite's header says it runs on pwsh 7 or 5.1.
- **Actual:** `FAIL  round-cap: ... and names the bug's stop-rule command`, exit 1. A test defect, the hook is right: `Out-String` wraps the error record at the console width, splitting the expected text.
- **Evidence:** raw stderr of the same call on 5.1 holds the whole text (EB02, EP02). A one-call reproduction at `RawUI` width 120 gave False through `Out-String`, True when joined without it.
- **Owner:** T2 author.
- **Repro:** `powershell.exe -NoProfile -NonInteractive -File .claude/hooks/tests/run.ps1` at width 120. 2 of 2 runs.

## Observations, no defect filed
- **Two IDs in a `Bug:` marker (D34, D35):** only the first is checked. `fix/SKILL.md:21` limits a brief to one bug. Two IDs in free text are all checked.
- **`Feature:` with `Verify:` and no `Bug:` line (D55, D56):** a past-cap bug is not checked, as the header says. `qa/SKILL.md:33` asks for `Verify:` and does not name `Bug:`, so a `/qa` re-run on such a bug may pass the hook. qa-lead's call.
- **Unreadable hook stdin (D89, D90):** `round-cap.ps1:29` exits 0 on malformed JSON or a UTF-8 BOM, even past a cap. The BOM came from E2's own 5.1 harness parent; whether Claude Code can send one was not observed.
- **Status line with nothing purged (S26):** `Bugs: 1 open (1 High+)`, no suffix. Read as intended.
- **Branch guard is case-sensitive (S06):** `Feature/y` purges. Branches here are lowercase by rule.
- **Long paths cut the cause (S21):** `Get-FirstLine` stops at 160 characters; exit 0 and later lines print.
- **Hang on 5.1 (D87, D87b):** the hook exits at 11.3 s, under the 15 s timeout (pwsh 7: 10.6 s). Pipes stayed open to 15.8 s through the fixture's `.cmd` wrapper child. `Kill($true)` does not exist on 5.1 (`common.ps1:351`).
- **`--note` with double quotes on 5.1 (C14):** the quotes are dropped silently. The spec routes long text to stdin; the skill allows `--note`.
- **At the cap, every `bugs.py` call naming the bug warns,** reads included (E12, E14). This matches the header.

## What ran
| C0 run, from an extracted `b6deca7` archive | Pass | Fail | Exit | Elapsed |
|---|---|---|---|---|
| pwsh 7.6.9 | 600 | 0 | 0 | 7 min 51 s |
| 5.1, run 1 | 599 | 1 | 1 | 6 min 12 s |
| 5.1, run 2 | 599 | 1 | 1 | 5 min 25 s |

- Fixtures: temp repos holding `.claude/`, `.gitignore`, `.gitattributes` from the archive. Journals built only by real `bugs.py` calls, except cases about a bad journal.
- Discarded harness runs: first 5.1 run invalid (.NET Framework wrote a BOM to the child's stdin from E2's parent; this led to D89 and D90); second 5.1 run aborted by a bad argument; C10 on 5.1 repeated once, same 6 mismatches.
- Side effects checked: worktree clean at `b6deca7`; main checkout `.claude/` clean; no `bugs.db` or `bugs.jsonl` in either; main `rounds.json` not written during the run; temp repos removed.

## Not covered
- Live-session `if` filters (`Bash(*bugs.py*)`, `PowerShell(*bugs.py*)`) and PostToolUse exit 2 delivery. Owner: main session, after the merge (GD's choice).
- Which executable `"shell": "powershell"` starts, the bytes Claude Code really sends on stdin, a live hook's code page. Same owner.
- Python 3.10 runtime: only 3.14.7 ran. GD's choice.
- A machine truly without Python, and the real Microsoft Store stub: both simulated. Owner: GD.
- A hang under a real Python launcher on 5.1, where `Kill()` may leave a child holding the pipes. Owner: T2 author.
- Feature-file counters, target and session caps, ledger corruption and lock handling: suite only (C0). Owner: qa-lead decides whether that is enough.
- macOS and Linux runs of the hooks. Owner: GD.
- Purge boundary at 89, 90, 91 days: E1 (C4). Only a 100-day-old bug ran here.
- Hooks against the migrated real data: main session, C15, after the merge.

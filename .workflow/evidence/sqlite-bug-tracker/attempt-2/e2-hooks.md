# E2 report - PowerShell and hooks (sqlite-bug-tracker, attempt 2)

- Executor: E2, independent of the authors of these fixes.
- Revision: `349542e`, from `git archive`. Results from `b6deca7` were not reused.
- Oracle: spec, `routing.md`, and `schema.md` at `349542e` (Hook root, Hook spelling, Purge), plus the re-run brief.
- GD decisions on record, not findings: at the cap allows, past the cap blocks; `Feature:` + `Verify:` with no `Bug:` line passes the hook. D02, D06, D55 and D56 show the code does this.
- Environment: Windows 11, pwsh 7.6.9, Windows PowerShell 5.1.26100.9711, Python 3.14.7, git 2.56.0.windows.2. Other agents ran on the machine at the same time.

## Result

| Item | Result |
|---|---|
| F1 | **Closed** by the documented form. Residual below is a known limitation |
| F2 | **Closed** |
| F3 | **Closed** |
| F4 | **Closed** |
| F5 | **Closed** |
| C0 suite | pwsh 7: 691 pass, 0 fail, 0 SKIP, exit 0. 5.1: 691 pass, 0 fail, 0 SKIP, exit 0 |
| Harness, 280 cases per shell | pwsh 7: 277 match, 3 do not. 5.1: 270 match, 10 do not |
| New defects | 1 Medium: N1 |

Every case that does not match:
- G22, G23, G24 on both shells: defect N1.
- C01, C02, C03, C10, C11, C12, C17 on 5.1 only: F1's known limitation.

## F1 to F5, original repro at `349542e`

| ID | Original repro | Then | Now | Verdict |
|---|---|---|---|---|
| F1 | 5.1 pipe of JSON with em dash and emoji | `?` written, exit 0 | Documented line works; default pipe unchanged (below) | Closed |
| F2 | Linked worktree outside `.claude/worktrees/`, branch with no journal, past-cap bug in main (D66) | exit 0 | exit 2 on both shells: `past the round cap - BUG-0004: fix 3/2` | Closed |
| F3 | `Bug: BUG-27`, `Fix BUG-27`, `Fix bug-0027`, past cap (D38-D41) | exit 0 on three | exit 2 on all four, both shells: `BUG-0027: fix 3/2` | Closed |
| F4 | `Bug: BUG-00036`, file 2 + ledger 1 (D61) | exit 0 | exit 2 on both shells: `BUG-0036: fix 3/2 (file 2 + hook 1)` | Closed |
| F5 | `run.ps1` on 5.1 from the same tool | 1 FAIL, exit 1 | `PASS round-cap: ... and names the bug's stop-rule command`, 0 FAIL, exit 0 | Closed |

### F1 detail
- **Documented form:** `.claude/skills/bugs/SKILL.md:27-28`, `references/schema.md:51`: `$OutputEncoding = [Text.UTF8Encoding]::new($false)` before a PowerShell pipe.
- **The form works on both shells, full text with `$x`, backticks, quotes, em dash, emoji:**
  - `add` C20, `round` C21, `set-status` C22, `update` C23: expected bytes, no BOM, no CR, final LF.
  - Title bytes on the non-ASCII part: `e2 80 94 20 f0 9f 8e ae`.
  - Under the form, Vietnamese is refused: C24, exit 1, `bugs: title: Vietnamese diacritics ...`, journal hash unchanged.
- **What the default 5.1 pipe still does (known limitation, not a re-finding):**
  - `add`, `round`, `set-status`, `update` exit 0 and write `?`. C01 title ending: `7b 62 7d 20 3f 20 3f 3f 20 65 6e 64`.
  - Vietnamese evades the refusal. C17, exit 0: `54 69 3f 75 20 3f 3f 20 6c 3f 69` ("Ti?u ?? l?i"). pwsh 7 on the same input: exit 1, no journal line.
  - `$OutputEncoding = New-Object Text.UTF8Encoding $false` also gives `?` on 5.1 (C03). The skill names the `::new` form only, so a reader following it is not affected.
  - 1 of 1 run at this revision.

## New defect

### N1 - Medium - A `.git` file planted above a project is still followed by `bugs.py`, so the hook reads another repo's bugs
- **Location:** `.claude/skills/bugs/scripts/bugs.py:336` (`Ctx.__init__`: `git rev-parse --git-dir --git-common-dir` walks up from `--root`), `:346` and `:351` (then takes that worktree's main checkout as the root). `Get-BugsRoot` (`common.ps1:252`) is correct by itself and hands `--root <project>` to this code.
- **Expected:** re-run brief: "a `.git` file planted above a project with no `.git` is not followed". `schema.md:70`: "reads only the project root's own `.git`, never one above it. A `.git` folder or none: that root". The header of `Get-BugsRoot` gives the reason: "a wrong folder would read as no bugs".
- **Actual:** the project has no `.git`, and its own journal holds BUG-0001 at fix 3/2. A file `<parent>/.git` says `gitdir: <other repo>/.git/worktrees/x`.
  - The dispatch for the project's past-cap BUG-0001 is allowed (G22).
  - A brief naming BUG-0002, which the project does not have, is blocked by the other repo's counters (G23).
  - The session line reports the other repo's count: `Bugs: 3 open (3 High+)`, where the project has 1 (G24).
- **What holds:** the part of the guard about code. The other repo's script and cached interpreter do not run: its logging wrapper recorded no start in G21 and G22. The project's own `bugs.py` runs, then reads the other repo's data.
- **Evidence:**
  - G22, exit 0, stderr empty, both shells. `bugs.py --root <proj> counters BUG-0001` returns `"fix": {"used": 1, "cap": 2}`, the other repo's BUG-0001.
  - Controls on both shells: nothing planted blocks (G21, `BUG-0001: fix 3/2`); a planted `.git` naming a missing folder blocks (G25); a real `.git` folder above blocks (G25b).
- **Owner:** the QA fixes author (`general-purpose`). The obvious direction: the CLI stops treating a link above `--root` as this project's worktree, as `Get-BugsRoot` does. Hand it to `technical-architect` if the counter says so: the feature file's row 20 names main-checkout resolution existing twice as the repeating cause.
- **Severity reason:** an edge case that needs a `.git` file above a project with none of its own. It fails open on a cap, with no foreign code run.
- **Repro:**
  1. Clone a repo `V` with bugs, `git worktree add <path>/Gvw`.
  2. Make `<parent>/proj` holding `.claude/`, no `.git`. `add` a bug, `round BUG-0001 fix +3`.
  3. Write `<parent>/.git` as `gitdir: V/.git/worktrees/Gvw`.
  4. Feed `proj/.claude/hooks/round-cap.ps1 -Mode dispatch` the JSON `{"tool_name":"Agent","tool_input":{"prompt":"Bug: BUG-0001"}}` with `CLAUDE_PROJECT_DIR=<parent>/proj`.
  - 6 of 6 runs: pwsh 7 four, 5.1 two.

## C0

Run serially from an extracted archive of `349542e`, output redirected to a file, from the same tool as attempt 1.

| Shell | PASS | FAIL | SKIP | Exit | Elapsed |
|---|---|---|---|---|---|
| pwsh 7.6.9 | 691 | 0 | 0 | 0 | 8 min 06 s |
| 5.1.26100.9711 | 691 | 0 | 0 | 0 | 6 min 30 s |

The suite has three `SKIP` branches (`run.ps1:1134`, `:1262`, `:1325`). None fired. The code page pin ran: `PASS bugs root fixture: a hook's shell decodes with code page 437`.

## `Get-BugsRoot`: table G

Exp/7/5.1 are exit codes. `PC` = `Stop rule (routing.md): past the round cap - `. `NC` = `round-cap: the brief names <id> but its round caps cannot be checked: `. All fixtures have a past-cap BUG-0002 in the main checkout unless the row says otherwise; worktrees are on a branch with no journal.

| Case | Input | Exp/7/5.1 | Stderr or `Bugs:` line | Match |
|---|---|---|---|---|
| G01 | non-ASCII main + non-ASCII worktree, past cap | 2/2/2 | PC BUG-0002: fix 3/2 | YY |
| G02 | same, under cap | 0/0/0 | - | YY |
| G03 | same, session start | 0/0/0 | `Bugs: 3 open (3 High+)`, no purge | YY |
| G04 | same, edit mode at cap | 2/2/2 | BUG-0003: fix 2/2 - at the cap | YY |
| G05 | same, no Python | 2/2/2 | NC no Python 3.10+ | YY |
| G06 | main `Game [v2]`, past cap, marker | 2/2/2 | PC BUG-0002: fix 3/2 | YY |
| G07 | same, under cap | 0/0/0 | - | YY |
| G08 | same, free text | 2/2/2 | PC BUG-0002: fix 3/2 | YY |
| G09 | same, settings.json command string | 2/2/2 | PC BUG-0002: fix 3/2 | YY |
| G10 | same, edit mode at cap | 2/2/2 | BUG-0003: fix 2/2 - at the cap | YY |
| G11 | same, count hook writes the ledger | 0/0/0 | ledger holds verify-brk1 | YY |
| G12 | same, ledger read: 2/2, at cap | 0/0/0 | - | YY |
| G13 | same, feature file review 4/3 | 2/2/2 | PC feature demo: review 4/3 | YY |
| G14 | same, corrupt ledger moved aside | 2/2/2 | could not be parsed; one rounds.corrupt file | YY |
| G15 | same, no Python | 2/2/2 | NC no Python 3.10+ | YY |
| G16 | same, no cache: `python.txt` written | 2/2/2 | PC BUG-0002: fix 3/2 | YY |
| G17 | agent worktree inside `Game [v2]` | 2/2/2 | PC BUG-0002: fix 3/2 | YY |
| G18 | linked worktree `W [v2]` | 2/2/2 | PC BUG-0002: fix 3/2 | YY |
| G19 | same, session start | 0/0/0 | `Bugs: 3 open (3 High+)` | YY |
| G20 | `Game [v3]`, session-start purge | 0/0/0 | `Bugs: 1 open (1 High+); purged 1, journal uncommitted` | YY |
| G21 | project with no `.git`, nothing planted, own past-cap bug | 2/2/2 | PC BUG-0001: fix 3/2 | YY |
| **G22** | `.git` file planted above, own past-cap bug | 2/**0**/**0** | - | **NN** (N1) |
| **G23** | same, other repo's past-cap id | 0/**2**/**2** | PC BUG-0002: fix 3/2 | **NN** (N1) |
| **G24** | same, session start, own journal has 1 | 0/0/0 | `Bugs: 3 open (3 High+)` | **NN** (N1) |
| G25 | planted `.git` naming a missing folder | 2/2/2 | PC BUG-0001: fix 3/2 | YY |
| G25b | real `.git` folder above (control) | 2/2/2 | PC BUG-0001: fix 3/2 | YY |
| G26 | lost `commondir`, past-cap bug | 2/2/2 | NC ...commondir is missing and ... holds no objects | YY |
| G27 | same, under-cap bug | 2/2/2 | same | YY |
| G28 | same, brief naming no bug | 0/0/0 | - | YY |
| G29 | same, session start; later lines print | 0/0/0 | `Bugs: unavailable - <path cut at 160>` | YY |
| G30 | same, edit mode | 2/2/2 | could not be read: ...commondir is missing | YY |
| G31 | `.git` file with no `gitdir` line | 2/2/2 | NC ...names no gitdir | YY |
| G32 | `gitdir` names a missing folder | 2/2/2 | NC ...does not exist | YY |
| G33 | `commondir` names a missing `.git` | 2/2/2 | NC ...does not exist | YY |
| G34 | empty `commondir` | 2/2/2 | NC ...is no checkout's .git | YY |
| G35 | relative `gitdir`, hand-written | 2/2/2 | PC BUG-0002: fix 3/2 | YY |
| G36 | `git worktree add --relative-paths`, real output `gitdir: ../Gm/.git/worktrees/Gwg` | 2/2/2 | PC BUG-0002: fix 3/2 | YY |
| G37 | absolute `commondir` | 2/2/2 | PC BUG-0002: fix 3/2 | YY |
| G38 | `.git` with CRLF | 2/2/2 | PC BUG-0002: fix 3/2 | YY |
| G39 | `commondir` with CRLF | 2/2/2 | PC BUG-0002: fix 3/2 | YY |
| G40 | `.git` with BOM | 2/2/2 | PC BUG-0002: fix 3/2 | YY |
| G41 | `commondir` with BOM | 2/2/2 | PC BUG-0002: fix 3/2 | YY |
| G42 | BOM + CRLF in both | 2/2/2 | PC BUG-0002: fix 3/2 | YY |
| G43 | `.git` with backslashes (recorded) | 2/2/2 | PC BUG-0002: fix 3/2 | YY |
| G44 | `commondir` with a trailing slash (recorded) | 2/2/2 | NC ...is no checkout's .git | YY |
| G45 | no git on PATH, Python cached in main | 2/2/2 | PC BUG-0002: fix 3/2 | YY |
| G46 | `--separate-git-dir`, own past-cap bug | 2/2/2 | PC BUG-0001: fix 3/2 | YY |
| G47 | submodule, own past-cap bug (see note) | 2/2/2 | PC BUG-0001: fix 3/2 | YY |
| G48 | worktree of a submodule | 2/2/2 | NC ...is no checkout's .git | YY |
| G49 | same, session start | 0/0/0 | `Bugs: unavailable - <path cut at 160>` | YY |
| G50 | worktree of a bare repo | 2/2/2 | NC ...is no checkout's .git | YY |
| G51 | bare repo in a folder named `.git` (documented: reads as no bugs) | 0/0/0 | - | YY |

G47 note: `git submodule add` exited 128 on this long fixture path after creating the module folder and the link, because the submodule's checkout did not inherit `core.longpaths`. The `.git` file, `.git/modules/sub`, the hook and `bugs.py` were all present, and the hook read the submodule's own journal.

## ID canonicalization: table I

BUG-0027 past cap (fix 3/2), BUG-0028 at cap, BUG-0029 at review cap, BUG-0030 under.

| Case | Input | Exp/7/5.1 | Stderr | Match |
|---|---|---|---|---|
| I01-I05 | marker: `bug-0027`, `BUG-27`, `BUG-00027`, `bug-27`, `Bug-0027` | 2/2/2 each | PC BUG-0027: fix 3/2 | YY |
| I06-I09 | free text: `bug-0027`, `BUG-27`, `BUG-00027`, `bug-27` | 2/2/2 each | same | YY |
| I10-I12 | `Verify:` with no marker: `bug-0027`, `BUG-27`, `BUG-00027` | 2/2/2 each | same | YY |
| I13 | `Feature:` + `Bug: bug-27` | 2/2/2 | same | YY |
| I14 | Workflow `args.bug = bug-27` | 2/2/2 | same | YY |
| I15 | three spellings in one brief; named once | 2/2/2 | same | YY |
| I16 | `Bug: bug-30`, under cap | 0/0/0 | - | YY |
| I17 | `Fix bug-9999`, unknown | 0/0/0 | - | YY |
| I18, I19 | no Python, `Bug: bug-27`, `Fix BUG-27` | 2/2/2 each | NC[BUG-0027] no Python 3.10+ | YY |
| I20 | `Bug: BUG-0027x` (recorded) | 0/0/0 | - | YY |
| I21 | `Fix BUG-0` (recorded, unknown) | 0/0/0 | - | YY |
| I22 | `Fix BUG-999999999999999999999999` (recorded, unknown) | 0/0/0 | - | YY |
| I23 | `See tests/bug-27.txt` (recorded) | 2/2/2 | PC BUG-0027: fix 3/2 | YY |
| I24 | `Fix the debug-27 overlay`: no id | 0/0/0 | - | YY |
| I25 | count: `Verify: bug-28` + `Repro: BUG-00028 reproduces`; ledger key `bug:BUG-0028` | 0/0/0 | - | YY |
| I26-I31 | dispatch `bug-28`, `BUG-28`, `BUG-00028` on marker; `bug-0028`, `BUG-00028` free; `Verify: BUG-28` | 2/2/2 each | PC BUG-0028: fix 3/2 (file 2 + hook 1) | YY |
| I32 | count: `Verify: BUG-28` + `Repro: bug-0028 reproduces` | 0/0/0 | - | YY |
| I33 | dispatch `Bug: BUG-00028` | 2/2/2 | PC BUG-0028: fix 4/2 (file 2 + hook 2) | YY |
| I34 | count: Repro names another number; no event | 0/0/0 | - | YY |
| I35 | count: code-reviewer fails `Bug: bug-29`; ledger key `bug:BUG-0029` | 0/0/0 | - | YY |
| I36 | dispatch `Bug: BUG-29` | 2/2/2 | PC BUG-0029: review 4/3 (file 3 + hook 1) | YY |
| I37 | edit, command text `show BUG-27` | 2/2/2 | BUG-0027: fix 3/2 - past the cap | YY |
| I38 | edit, command text `show bug-0028` | 2/2/2 | BUG-0028: fix 4/2 (file 2 + hook 2) - past the cap | YY |
| I39, I40 | CLI `counters bug-0027`, `counters BUG-27` | 1/1/1 | `bugs: bad id ...: expected BUG-####` | YY |
| I41 | CLI `counters BUG-00027` | 0/0/0 | prints `"id": "BUG-0027"` | YY |

## Session status line, each purge state: table S

Same line on both shells, every row exit 0. Commit counts and HEAD did not change on any row that recorded them.

| Case | State | Purged? | `Bugs:` line |
|---|---|---|---|
| S01 | `main`, clean, one expired | yes | `Bugs: 1 open (1 High+); purged 1, journal uncommitted` |
| S30 | `main`, clean, two expired | yes | `Bugs: 1 open (1 High+); purged 2, journal uncommitted` |
| S04, S07 | `develop`, `featurex/y` | yes | purged 1 line |
| S06 | `Feature/y` (recorded) | yes | purged 1 line |
| S26 | `main`, clean, nothing expired | no | `Bugs: 1 open (1 High+)` |
| S03 | next session after a purge, journal dirty | no | `Bugs: 1 open (1 High+); purge skipped, journal uncommitted` |
| S13, S14 | journal unstaged, staged | no | `Bugs: 2 open (2 High+); purge skipped, journal uncommitted` |
| S15 | journal untracked | no | `Bugs: 1 open (1 High+); purge skipped, journal uncommitted` |
| S05 | `feature/x` | no | `Bugs: 1 open (1 High+)` |
| S08-S11 | merge, cherry-pick, revert, rebase in progress | no | `Bugs: 1 open (1 High+)` |
| S12 | detached HEAD | no | `Bugs: 1 open (1 High+)` |
| S18, S19 | agent worktree, linked worktree elsewhere | no | `Bugs: 1 open (1 High+)` |
| S27 | not a git repository | no | `Bugs: 1 open (1 High+)` |
| S23 | purge write fails, journal read-only | no | `Bugs: 1 open (1 High+); purge failed: bugs: [WinError 5] Access is denied: ...` |
| S28 | `BUGS_NOW` left set | yes | `...; purged 1, journal uncommitted; warning: BUGS_NOW is set: time here reads as the test clock` |
| S16, S17 | no Python, Store-stub stand-in | no | `Bugs: unavailable - install Python 3.10+ with SQLite FTS5 (skill bugs).` |
| S20 | malformed journal | no | `Bugs: unavailable - bugs: corrupt journal: line 1: JSONDecodeError` |
| S21 | `bugs.py` missing | no | `Bugs: unavailable - <path cut at 160>` |
| S22 | CLI hangs; under 15 s | no | `Bugs: unavailable - timed out after 1 s` |
| S24 | `bugs.md` present | no | `Bugs: .workflow/bugs.md is still present - run bugs.py import-md, then delete the file (skill bugs).` |
| S25 | no journal; `bugs.py` never started | no | no line |
| S29 | settings.json command string | yes | purged 1 line |

## C8, C9, C10 rows not shown above

Full tables are in the raw files named at the end.
- **C8 (D01-D93 and D87b):** all 94 rows match on both shells.
  - F2, F3 and F4 rows now block.
  - D34, D35 (two IDs on `Bug:` lines): only the first is checked, recorded; `fix/SKILL.md` limits a brief to one bug.
  - D87b: the hook process exits at 10.6 s on pwsh 7 and 10.7 s on 5.1, under the 15 s hook timeout. On 5.1 the pipes stayed open to 15.7 s, because the fixture's `.cmd` wrapper left its child `ping` running; `Kill($true)` does not exist there.
  - D89, D90: unreadable hook stdin exits 0, recorded as in attempt 1. The spec's fail-closed clause does not name it.
- **C9 edit mode (EB01-EB16, EP01-EP16, E17-E21):** all 37 rows match on both shells.
- **C10 (C00-C24):** pwsh 7 all match. On 5.1 only C01, C02, C03, C10, C11, C12, C17 do not: the limitation above. C04-C09, C13, C15, C16, C18, C20-C24 match on 5.1.
- **C14 on 5.1, recorded:** `--note` holding double quotes loses them.

## Observations, no defect filed

- **Long paths cut the cause (S21, G29, G49):** `Get-FirstLine` stops at 160 characters. On this long fixture root the line ends inside the path, so `commondir is missing` is not on the session line. The dispatch path keeps the whole text.
- **`commondir` with a trailing slash (G44):** fails closed, though the path is valid. Git does not write this form; hand-written only.
- **A path reads as a bug (I23):** `See tests/bug-27.txt` blocks on a past-cap BUG-0027. This follows the header's "whatever its case or padding" in free text.

## What I ran

- **Fixtures:** temp repos cloned from a template holding `.claude/`, `.gitignore`, `.gitattributes` of the `349542e` archive; a root per shell. Journals built by real `bugs.py` calls, except cases about a bad journal or link. Hooks fed by a child process with UTF-8 stdin and no window (child code page OEM 437), stderr captured raw.
- **Harness changes from attempt 1:**
  - New: groups G and I; cases S30, C20-C24.
  - Oracle moved: D38-D42 now expect a block; S03, S13-S15 expect the `purge skipped` line.
  - S21 no longer demands the cut-off words.
  - The hang timers (D87, D87b) measure process exit.
- **Runs:**
  - One full run per shell. Both aborted at G34 on my fixture: a commondir broken by G33 made the next `git worktree add` fail.
  - Fixed by restoring those files after each case; groups G and I then re-ran in full on both shells. The rows in this report are from those re-runs. D, E, S, C, X, Y are from the full runs.
  - Earlier partial trials on pwsh 7: an I run and two G runs.
- **Limits kept:**
  - Worktree at `349542e`, `git status` clean; main `.claude/` clean.
  - No `bugs.db` or `bugs.jsonl` in either tree; no `rounds.json` in the worktree.
  - Main `rounds.json` last written 16:29, before this run began (about 19:10).
  - Temp repos removed. The two `hooktest-*` folders present before attempt 1 were left.

## Raw tables, in the scratchpad until the main session copies them

`C:\Users\Admin\AppData\Local\Temp\claude\c--Users-Admin-Projects-AI-For-Game-AI-For-Game-Development\144bb0e0-5428-4e8b-92a5-0d45be3e4813\scratchpad\qa-e2-harness\out2\`: `table-D.md`, `table-E.md`, `table-S.md`, `table-C.md`, `table-G.md`, `table-I.md`, `results-*.json`, `c0-*.log`, `run-*.log`, `compact.txt`.

Not covered:
- Live-session `if` filters and PostToolUse exit 2 delivery. Owner: main session, the one `claude -p` check the GD ordered after the merge.
- Which executable `"shell": "powershell"` starts, the bytes Claude Code really sends on stdin, a live hook's code page. Same owner.
- Python 3.10 runtime: GD decision on record, 3.14 only.
- A machine truly without Python, and the real Microsoft Store stub: simulated in the fixture. Owner: GD.
- A hang under a real Python launcher on 5.1. Owner: QA fixes author.
- A project in a subfolder of a real linked worktree, with its own journal: the same `Ctx` path as N1, not run. Owner: QA fixes author, with N1.
- A project's own `.git` file pointing at a chosen folder: `Get-BugsRoot` trusts it by design, so that folder's script and cached interpreter run. Not attacked here. Owner: `security-reviewer`.
- XERJ autoindex under a bracket path (`session-start.ps1` change): `HOOK_TEST_XERJ=none` kept XERJ out of every fixture. Owner: main session.
- Feature-file counters, target and session caps, ledger lock handling: suite only (C0), except G13 and G14. Owner: qa-lead decides whether that is enough.
- macOS and Linux runs of the hooks. Owner: GD.
- Purge boundary at 89, 90, 91 days: E1. Only 100-day-old bugs ran here.
- Hooks against migrated real data: main session, C15, after the merge.

| Case | Input | Exp exit | pwsh 7 | 5.1 | Hook stderr (or stdout when no stderr), fixture path shortened | DB state after | 7 | 5.1 |
|---|---|---|---|---|---|---|---|---|
| S01 | main checkout, branch main, clean journal, one terminal bug 100 d old | 0 | 0 | 0 | Bugs: 1 open (1 High+); purged 1, journal uncommitted | journal changed=True; HEAD same=True; commits 2->2; git status 'M .workflow/bugs.jsonl'; Bugs lines=1 | pass | pass |
| S02 | ... the bug is gone, journal uncommitted | 0 | 0 | 0 | (no Bugs line) | git: M .workflow/bugs.jsonl | pass | pass |
| S03 | next session: journal now dirty | 0 | 0 | 0 | Bugs: 1 open (1 High+) | journal changed=False; HEAD same=True; commits 2->2; git status 'M .workflow/bugs.jsonl'; Bugs lines=1 | pass | pass |
| S04 | branch develop, clean | 0 | 0 | 0 | Bugs: 1 open (1 High+); purged 1, journal uncommitted | journal changed=True; HEAD same=True; commits 2->2; git status 'M .workflow/bugs.jsonl'; Bugs lines=1 | pass | pass |
| S05 | branch feature/x | 0 | 0 | 0 | Bugs: 1 open (1 High+) | journal changed=False; HEAD same=True; commits 2->2; git status ''; Bugs lines=1 | pass | pass |
| S06 | branch Feature/y (case variant, recorded) | 0 | 0 | 0 | Bugs: 1 open (1 High+); purged 1, journal uncommitted | journal changed=True; HEAD same=True; commits 2->2; git status 'M .workflow/bugs.jsonl'; Bugs lines=1 | pass | pass |
| S07 | branch featurex/y (outside feature/*) | 0 | 0 | 0 | Bugs: 1 open (1 High+); purged 1, journal uncommitted | journal changed=True; HEAD same=True; commits 2->2; git status 'M .workflow/bugs.jsonl'; Bugs lines=1 | pass | pass |
| S08 | merge in progress (real conflict) | 0 | 0 | 0 | Bugs: 1 open (1 High+) | journal changed=False; HEAD same=True; commits 5->5; git status ''; Bugs lines=1 | pass | pass |
| S08b | ... MERGE_HEAD still there | 0 | 0 | 0 | (no Bugs line) | - | pass | pass |
| S09 | cherry-pick in progress (not named in the spec, recorded) | 0 | 0 | 0 | Bugs: 1 open (1 High+) | journal changed=False; HEAD same=True; commits 5->5; git status ''; Bugs lines=1 | pass | pass |
| S10 | revert in progress (not named in the spec, recorded) | 0 | 0 | 0 | Bugs: 1 open (1 High+) | journal changed=False; HEAD same=True; commits 7->7; git status ''; Bugs lines=1 | pass | pass |
| S11 | rebase in progress (real conflict; state dir present=True) | 0 | 0 | 0 | Bugs: 1 open (1 High+) | journal changed=False; HEAD same=True; commits 7->7; git status ''; Bugs lines=1 | pass | pass |
| S12 | detached HEAD (not named in the spec, recorded) | 0 | 0 | 0 | Bugs: 1 open (1 High+) | journal changed=False; HEAD same=True; commits 7->7; git status ''; Bugs lines=1 | pass | pass |
| S13 | journal modified, unstaged | 0 | 0 | 0 | Bugs: 2 open (2 High+) | journal changed=False; HEAD same=True; commits 2->2; git status 'M .workflow/bugs.jsonl'; Bugs lines=1 | pass | pass |
| S14 | journal modified, staged | 0 | 0 | 0 | Bugs: 2 open (2 High+) | journal changed=False; HEAD same=True; commits 2->2; git status 'M .workflow/bugs.jsonl'; Bugs lines=1 | pass | pass |
| S15 | journal untracked | 0 | 0 | 0 | Bugs: 1 open (1 High+) | journal changed=False; HEAD same=True; commits 1->1; git status '?? .workflow/bugs.jsonl'; Bugs lines=1 | pass | pass |
| S16 | no Python | 0 | 0 | 0 | Bugs: unavailable - install Python 3.10+ with SQLite FTS5 (skill bugs). | journal changed=False; HEAD same=True; commits 2->2; git status ''; Bugs lines=1 | pass | pass |
| S17 | Store-stub stand-in on PATH | 0 | 0 | 0 | Bugs: unavailable - install Python 3.10+ with SQLite FTS5 (skill bugs). | journal changed=False; HEAD same=True; commits 2->2; git status ''; Bugs lines=1 | pass | pass |
| S18 | session in agent worktree .claude/worktrees/w1 | 0 | 0 | 0 | Bugs: 1 open (1 High+) | journal changed=False; HEAD same=True; commits 2->2; git status ''; Bugs lines=1 | pass | pass |
| S19 | session in a linked worktree elsewhere | 0 | 0 | 0 | Bugs: 1 open (1 High+) | journal changed=False; HEAD same=True; commits 2->2; git status ''; Bugs lines=1 | pass | pass |
| S20 | malformed journal | 0 | 0 | 0 | Bugs: unavailable - bugs: corrupt journal: line 1: JSONDecodeError | journal malformed | pass | pass |
| S21 | bugs.py missing | 0 | 0 | 0 | Bugs: unavailable - <fx>/S | bugs.py moved away | FAIL | FAIL |
| S22 | CLI hangs (wrapper sleeps 29 s for bugs.py) | 0 | 0 | 0 | Bugs: unavailable - timed out after 1 s | wrapper | pass | pass |
| S23 | journal read-only: the purge write fails | 0 | 0 | 0 | Bugs: 1 open (1 High+); purge failed: bugs: [WinError 5] Access is denied: 'C:\\Users\\Admin\\AppData\\Local\\Temp\\claude\\c--Users-Admin-Projects-AI-For-Game-AI-For-Gam... | line: Bugs: 1 open (1 High+); purge failed: bugs: [WinError 5] Access is denied: 'C:\\Users\\Admin\\AppData\\Local\\Temp\\claude\\c--Users-Admin-Projects-AI-For-Game-AI-For-Game-Development\\144bb0e0-5428 | pass | pass |
| S24 | bugs.md present | 0 | 0 | 0 | Bugs: .workflow/bugs.md is still present - run bugs.py import-md, then delete the file (skill bugs). | journal changed=False; HEAD same=True; commits 2->2; git status ''; Bugs lines=1 | pass | pass |
| S25 | no journal | 0 | 0 | 0 | (no Bugs line) | bugs.py starts: 0 | pass | pass |
| S26 | main, clean, nothing past the window | 0 | 0 | 0 | Bugs: 1 open (1 High+) | journal changed=False; HEAD same=True; commits 2->2; git status ''; Bugs lines=1 | pass | pass |
| S27 | not a git repository | 0 | 0 | 0 | Bugs: 1 open (1 High+) | - | pass | pass |
| S28 | BUGS_NOW left set | 0 | 0 | 0 | Bugs: 1 open (1 High+); purged 1, journal uncommitted; warning: BUGS_NOW is set: time here reads as the test clock | git: M .workflow/bugs.jsonl | pass | pass |
| S29 | settings.json command string | 0 | 0 | 0 | Bugs: 1 open (1 High+); purged 1, journal uncommitted | git: M .workflow/bugs.jsonl | pass | pass |

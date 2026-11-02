# Baselines at Base

- **Base:** `bdf5c9ec70bf217ee9ed2763abd75fa4280b717c`, working tree clean for tracked files, 2026-11-02.
- **Run before any tracked edit:** all three below ran before `verify.ps1` was changed.
- **Shell:** pwsh 7.6.9, from `pwsh -NoProfile -File`.

| Suite | Command | Exit | Summary | Failures |
|---|---|---|---|---|
| Hooks | `pwsh -NoProfile -File .claude/hooks/tests/run.ps1` | 0 | 410 `PASS`, 0 `FAIL`, last line `hooks: all tests passed` | none |
| Mem | `python -I .claude/skills/mem/scripts/test_mem.py` (the form the file's docstring gives) | 0 | `Ran 33 tests`, `OK` | none |
| Layer | `pwsh -NoProfile -File .claude/skills/verify-layer/scripts/verify.ps1` | 0 | `verify-layer: OK (21 warning(s))`, 10 `file(s):` lines, 0 `FAIL` | none |

## Noise already present
- **Hooks, `run.ps1:316`:** prints a `Set-Content` error, because `.workflow/evidence/x/` does not exist in the temp repo. Exit and `PASS` count are unaffected. The next check, `pre-push allows an unpushed evidence report`, then passes without that commit having been made, so it may prove less than its name says. Left alone: out of scope.
- **Mem:** one `mem capture skipped: no secret patterns in <temp path>` line from a test that removes the patterns on purpose.

## Whole-layer `verify.ps1` output at Base

```
WARN  121 file(s): description + when_to_use > 120 chars
WARN  115 file(s): list item > 200 chars
WARN  85 file(s): Latent concerns line
WARN  68 file(s): reference or script table
WARN  1 file(s): description uses a banned phrase
WARN  76 file(s): Verified or Known limitations bullet (agent-protocol envelope owns them)
WARN  23 file(s): reference has a fenced block of 15+ lines (move it to scripts/)
WARN  2 file(s): hardcoded script path
WARN  7 file(s): description has no Use trigger
WARN  2 file(s): body > 8000 chars
WARN  .claude/agents/backend-engineer.md: 59 lines > 50 recommended (soft)
WARN  .claude/agents/build-release-engineer.md: 60 lines > 50 recommended (soft)
WARN  .claude/agents/ci-cd-engineer.md: 58 lines > 50 recommended (soft)
WARN  .claude/agents/code-reviewer.md: 51 lines > 50 recommended (soft)
WARN  .claude/agents/csharp-engineer.md: 60 lines > 50 recommended (soft)
WARN  .claude/agents/cto.md: 58 lines > 50 recommended (soft)
WARN  .claude/agents/gameplay-engineer.md: 67 lines > 50 recommended (soft)
WARN  .claude/agents/git-expert.md: 74 lines > 50 recommended (soft)
WARN  .claude/agents/netcode-engineer.md: 59 lines > 50 recommended (soft)
WARN  .claude/agents/performance-qa-engineer.md: 53 lines > 50 recommended (soft)
WARN  .claude/agents/playtest-tester.md: 52 lines > 50 recommended (soft)
WARN  .claude/agents/qa-automation-engineer.md: 58 lines > 50 recommended (soft)
WARN  .claude/agents/rd-engineer.md: 62 lines > 50 recommended (soft)
WARN  .claude/agents/researcher.md: 51 lines > 50 recommended (soft)
WARN  .claude/agents/sdk-platform-engineer.md: 62 lines > 50 recommended (soft)
WARN  .claude/agents/technical-architect.md: 75 lines > 50 recommended (soft)
WARN  .claude/agents/technical-artist.md: 60 lines > 50 recommended (soft)
WARN  .claude/agents/ui-engineer.md: 60 lines > 50 recommended (soft)
WARN  .claude/agents/unity-performance-engineer.md: 61 lines > 50 recommended (soft)
WARN  CLAUDE.md: 31 lines > 30 recommended
WARN  .claude/rules: always-loaded rules 123 lines > 100 recommended
verify-layer: OK (21 warning(s))
```

## After the T1 `verify.ps1` edit
Not a new baseline: the three runs above stay the comparison for AC11.

| Suite | Exit | Summary |
|---|---|---|
| Hooks | 0 | 410 `PASS`, 0 `FAIL` |
| Mem | 0 | `Ran 33 tests`, `OK` |
| Layer | 0 | `verify-layer: OK (21 warning(s))`, 11 `file(s):` lines; the only new line is `WARN  124 file(s): untitled list item or prose line` |

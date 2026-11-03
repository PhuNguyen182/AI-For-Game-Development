---
name: verify-layer
description: "Check the .claude/ layer: paths, frontmatter, skill refs, budgets, retired IDs. Use after any .claude change."
allowed-tools: PowerShell, Bash, Read
---

# /verify-layer

## Scripts
- **[verify.ps1](scripts/verify.ps1):** run `pwsh -NoProfile -File "${CLAUDE_SKILL_DIR}/scripts/verify.ps1"` → checks the whole layer.
- **One file:** run `pwsh -NoProfile -File "${CLAUDE_SKILL_DIR}/scripts/verify.ps1" -File <p>` → checks one file (the hook), plus the owning skill's script-named check for a file under `references/`.

## Steps
1. **Run:** the whole layer, or one file with `-File`, per `## Scripts`.
2. **Exit code:** decides the result.
   - **Exit 0:** pass (warnings allowed).
   - **Exit 1:** a `FAIL` line names each file and problem.
3. **Warnings:** by kind:
   - **Size budgets:** only `WARN`, except a description past 250 chars or a reference fence of 15+ lines, which fail.
   - **Over budget:** over budget and cannot be shorter → leave it.
   - **Soft label:** `(soft)` in `## Checks` marks a check that only warns; every other check fails.
   - **Soft skill checks:** print per file with `-File` and as one count per check on a whole-layer run.
4. **Fix target:** fix the file, not the check — unless the check encodes the wrong rule; then say so.

## Checks
| Check | Budget / rule |
|---|---|
| `CLAUDE.md` | ≤ 30 lines (soft) |
| Always-loaded rules | ≤ 100 lines total (soft); path-scoped rule ≤ 40 (soft) |
| Agent | frontmatter; `name` = filename; `description` present, ≤ 250 chars; `tools`; `skills:` exist; file ≤ 50 lines (soft); a backticked hyphenated name that is neither a skill nor an agent (soft) |
| Skill | frontmatter; `name` = folder when set; `description` present; `description` + `when_to_use` ≤ 120 chars (soft), ≤ 250; body ≤ 8,000 chars (soft); list item ≤ 200 chars (soft); `Not for:` names exist |
| Skill format | `description` has no `This skill`, `comprehensive` or `Preloaded by`; `description` has a `Use ` trigger, unless `when_to_use` is set or an agent preloads the skill; body, fences included: no retired on-request report line, no `Verified` or `Known limitations` bullet (`Status:` is unchecked), no `| Reference | Read when |` or `| Script | Run |` table header, no hardcoded path to the skill's own `scripts/` |
| Skill items | outside fences each line is blank, a column-0 heading, a table row or a titled item (`- **<title>:** <text>`, `1. **<title>:** <text>`); `FAIL` gives the line numbers |
| Skill scripts | each file under `scripts/` is named in `SKILL.md` or a reference, except `test_*`, `__pycache__` and dot-folders; `-File` on a file under its `references/` runs this for the owning skill |
| `checklist.md` | only headings and `- [ ] **<title>:** <text>` lines; linked from its `SKILL.md` |
| Script files | `.ps1` ASCII only; `.sh` LF only |
| Skill references | fenced block < 15 lines |
| References | backticked .claude paths and relative links exist; agents named exist; no retired agents or paths |
| IDs | rules, agents, pipelines: no G/B/I/A/V/EV ids (CP1–CP4 only) |
| Namespaces | any checked file: no retired namespace scheme |
| Hook contracts | each file in `$HookContracts` keeps the strings `round-cap.ps1` counts on; each in `$WorkflowContracts` keeps the `roundId` field `/review` reads from `review-gate` |
| State | no `.workflow` path under `.claude/`; state belongs in `<project>/.workflow/` |
| Commands | whole layer only: no .claude/commands folder; convert commands to skills |
| Workflows | `.claude/workflows/` holds only `.js` starting with `export const meta` |
| Tables | every row has the header's cell count |
| `unity:*` skills | plugin installed locally (soft) |

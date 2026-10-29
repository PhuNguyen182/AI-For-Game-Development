---
name: verify-layer
description: "Check the .claude/ layer after any change: paths resolve, agent/skill frontmatter, skill references, workflows are JS, size budgets, no retired IDs or agents, table widths. Runs automatically on .claude edits via hook."
allowed-tools: PowerShell, Bash, Read
---

# /verify-layer

```
pwsh -NoProfile -File .claude/skills/verify-layer/scripts/verify.ps1            # whole layer
pwsh -NoProfile -File .claude/skills/verify-layer/scripts/verify.ps1 -File <p>  # one file (the hook)
```
Exit 0 = pass (warnings allowed). 1 = a `FAIL` line names each file and problem. Line budgets only `WARN`; description length is a failure (the skill listing truncates past it). Over budget and cannot be shorter → leave it.

| Check | Budget / rule |
|---|---|
| `CLAUDE.md` | ≤ 30 lines |
| Always-loaded rules | ≤ 100 lines total; path-scoped rule ≤ 40 |
| Agent | `name` = filename, description ≤ 250 chars, `tools`, body ≤ 25 lines, `skills:` exist |
| Skill | description ≤ 250 chars; pipeline (user-invocable) ≤ 120 lines, others ≤ 500 |
| References | backticked .claude paths and relative links exist; agents named exist; no retired agents or paths |
| IDs | rules, agents, pipelines: no G/B/I/A/V/EV ids (CP1–CP4 only) |
| Workflows | `.claude/workflows/` holds only `.js` starting with `export const meta` |
| Tables | every row has the header's cell count |
| `unity:*` skills | warning only when the plugin is not installed locally |

Fix the file, not the check — unless the check encodes the wrong rule; then say so.

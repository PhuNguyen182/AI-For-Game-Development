---
name: verify-layer
description: "Check the .claude/ layer: paths, frontmatter, skill refs, budgets, retired IDs. Use after any .claude change."
allowed-tools: PowerShell, Bash, Read
---

# /verify-layer

```
pwsh -NoProfile -File "${CLAUDE_SKILL_DIR}/scripts/verify.ps1"            # whole layer
pwsh -NoProfile -File "${CLAUDE_SKILL_DIR}/scripts/verify.ps1" -File <p>  # one file (the hook)
```
Exit 0 = pass (warnings allowed). 1 = a `FAIL` line names each file and problem. Size budgets only `WARN`, except a description past 250 chars, which fails. Over budget and cannot be shorter → leave it. Skill-format warnings print per file with `-File` and as one count per check on a whole-layer run, so a skill is fixed when next touched.

| Check | Budget / rule |
|---|---|
| `CLAUDE.md` | ≤ 30 lines |
| Always-loaded rules | ≤ 100 lines total; path-scoped rule ≤ 40 |
| Agent | `name` = filename, description ≤ 250 chars, `tools`, file ≤ 50 lines (soft), `skills:` exist |
| Skill | `description` + `when_to_use` ≤ 120 chars (soft), ≤ 250 (fails); body ≤ 8,000 chars (soft); list item ≤ 200 chars (soft); `Not for:` names exist |
| Skill format (soft) | description words and trigger; no retired on-request report line, no envelope fields in `Output`, no reference or script tables, hardcoded script paths or unnamed scripts |
| `checklist.md` | only headings and `- [ ] **<title>:** <text>` lines; linked from its `SKILL.md` |
| Script files | `.ps1` ASCII only; `.sh` LF only |
| Skill references | fenced block < 15 lines (soft) |
| References | backticked .claude paths and relative links exist; agents named exist; no retired agents or paths |
| IDs | rules, agents, pipelines: no G/B/I/A/V/EV ids (CP1–CP4 only) |
| Workflows | `.claude/workflows/` holds only `.js` starting with `export const meta` |
| Tables | every row has the header's cell count |
| `unity:*` skills | warning only when the plugin is not installed locally |

Fix the file, not the check — unless the check encodes the wrong rule; then say so.

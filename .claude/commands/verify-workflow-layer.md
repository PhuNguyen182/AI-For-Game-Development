---
description: Check every claim the workflow layer makes about itself — agent class counts, lock holders, the 200-line cap, entry-point coverage, orphan references, and cross-reference anchoring
allowed-tools: Bash, PowerShell, Read, Grep, Glob
---

# Verify the workflow layer against itself

Runs `.claude/workflows/tools/verify-workflow-layer.ps1` and reports what drifted.

## Why this exists

The layer states numbers about itself — agent class counts, lock holders, gate-debt counts, entry
points. Each one drifts the moment a file changes, and nothing notices on its own.
`effort-allocation.md` grades an unsupported assertion **E0** and a tool output **E2** — this command
moves the layer's self-description from the first to the second.

## Run it

Per `shell-preference.md`, use the newest installed PowerShell:

```
pwsh -NoProfile -File .claude/workflows/tools/verify-workflow-layer.ps1
```

Exit code **0** = every claim holds. **1** = at least one drifted; each failing line names the stated
value and the actual one.

## What it checks

| Group | The claim |
|---|---|
| Agent classes | Class A/B/gate-debt counts in `references/orchestrator-direct-dispatch.md` match agent `tools:` frontmatter |
| Global locks | Editor-holder count in `rules/orchestration.md` **I3** matches agents holding `mcp__` tools |
| 200-line cap | Every file under `workflows/` except `workflow-checklist.md` (exempt by its own header) |
| Entry points | `references/entry-index.md` has exactly one row per door the six pipelines declare |
| References | No orphan in `references/` — every file is named by some workflow file |
| Cross-references | No `agent-name:42` line-number reference anywhere — they go stale silently |
| Agent ids | Every hyphenated backticked id resolves to a real file under `.claude/agents/` |

## Fixing what it reports, and when to run it

Fix the document, not the check — unless the check encodes the wrong rule, in which case say so
rather than loosening it quietly. A cap failure is fixed by **promotion into `references/`**, per
`references/README.md`: content moves when it earns a file, the source keeps a pointer, never a copy.
Never raise the cap or delete reasoning to fit. Run it after any change under `.claude/` that touches
an agent's `tools:` frontmatter, a pipeline's entry table, a reference file, or any stated count — per
`rules/orchestration.md`, a standing rule, not a suggestion.

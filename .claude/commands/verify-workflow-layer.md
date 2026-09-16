---
description: Check every claim the workflow layer makes about itself — agent class counts, lock holders, the 200-line cap, entry-point coverage, orphan references, and cross-reference anchoring
allowed-tools: Bash, PowerShell, Read, Grep, Glob
---

# Verify the workflow layer against itself

Runs `.claude/workflows/tools/verify-workflow-layer.ps1` and reports what drifted.

## Why this exists

The layer states numbers about its own shape — how many agents leave no source, how many hold the Editor
lock, how many accrue gate debt, how many entry points exist. Every one of those is a claim, and every one
drifts the moment an agent file gains a tool or a pipeline gains a door. Nothing notices on its own.

`effort-allocation.md` grades an unsupported assertion **E0** and a tool output **E2**. This command is what
moves the layer's self-description from the first to the second, and it is the reason the enforcement debt in
`workflow-checklist.md` was reopened: a real miss supplied the evidence that row was waiting for.

## Run it

Per `shell-preference.md`, use the newest installed PowerShell:

```
pwsh -NoProfile -File .claude/workflows/tools/verify-workflow-layer.ps1
```

Exit code **0** means every claim holds. **1** means at least one drifted, and each failing line names the
stated value and the actual one.

## What it checks

| Group | The claim |
|---|---|
| Agent classes | The class A / class B / gate-debt counts in `references/orchestrator-direct-dispatch.md` match what the `tools:` frontmatter actually says |
| Global locks | The Editor-holder count in `rules/orchestration.md` **I3** matches how many agents hold `mcp__` tools |
| The 200-line cap | Every file under `workflows/` except `workflow-checklist.md`, which is exempt by its own header |
| Entry points | `references/entry-index.md` has exactly one row per door the six pipelines declare |
| References | No orphan in `references/` — every file is named by some workflow file |
| Cross-references | No `agent-name:42` line-number reference anywhere. They go stale silently; quoted text does not |
| Agent ids | Every hyphenated backticked id a workflow names resolves to a real file under `.claude/agents/` |

## Fixing what it reports

**Fix the document, not the check** — unless the check itself encoded the wrong rule, in which case say so
rather than loosening it quietly. A count that drifted means the layer describes a system that no longer
exists, and the document is what is wrong.

A cap failure is fixed by **promotion into `references/`**, per the rule in `references/README.md` — content
moves when it earns a file, the source keeps a pointer and never a copy. It is never fixed by raising the cap
or by deleting reasoning to fit.

## When to run it

After any change under `.claude/` that touches an agent's `tools:` frontmatter, a pipeline's entry table, a
reference file, or any stated count. `rules/orchestration.md` makes this a standing rule rather than a
suggestion — a number nobody checked is E0 evidence, whatever else the layer got right.

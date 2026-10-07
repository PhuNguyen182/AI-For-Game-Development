---
description: Check the workflow layer's integrity — references resolve, IDs exist, every GD touchpoint is cited by its owner, standards reach their readers, no runtime state under .claude/, nothing depends on the reference-only docs folder
allowed-tools: Bash, PowerShell, Read, Grep, Glob
---

# Verify the workflow layer

Runs `.claude/workflows/tools/verify-workflow-layer.ps1` and reports what fails.

## Run it

Per `shell-preference.md`, use the newest installed PowerShell:

```
pwsh -NoProfile -File .claude/workflows/tools/verify-workflow-layer.ps1
```

Exit code **0** = every check holds. **1** = at least one fails; each failure names the file and the
reference or ID at fault.

## What it checks

| # | Check |
|---|---|
| 1 | Every backticked `.md`/`.ps1` path and every relative markdown link in the layer, agents, commands, standards and the root README resolves |
| 2 | Every agent id named in the layer exists, and every agent is reachable from the router or a pipeline |
| 3 | Every skill an agent names in its §5 exists at `skills/<name>/SKILL.md` |
| 4 | Every standard has a row in `rules/standards-index.md`, and every agent listed as a reader cites it |
| 5 | `workflows/state/` holds only its README and templates; no ledger or state root under `.claude/` |
| 6 | Every GD touchpoint in `workflows/gd-touchpoints.md` is unique, cited by its owner file, and no file cites an undefined one |
| 7 | Every cited invariant (I-id) exists in `rules/orchestration.md` and every bound (B-id) in `workflows/references/bounds.md` |
| 8 | No file outside the reference-only docs folder references a file inside it |
| 9 | Every agent's frontmatter has `name` equal to its filename, a `description` and `tools` |
| 10 | **Warning only**: a workflow file over 200 lines — under 200 is recommended, never required |

## Fixing what it reports

Fix the document, not the check — unless the check encodes the wrong rule, in which case say so rather than
loosening it quietly. Run it after any change under `.claude/`.

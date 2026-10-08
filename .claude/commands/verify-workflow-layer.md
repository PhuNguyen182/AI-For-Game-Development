---
description: Check the workflow layer's integrity and cross-file meaning — references resolve, IDs and doors exist, every GD touchpoint is cited by its owner and has a decline path, pipelines dispatch only their own agents, state fields and counters match their templates and bounds, nothing depends on the reference-only docs folder
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
| 10a | Every `<pipeline>.md` **En** cited anywhere names a door that pipeline's Entries table defines |
| 10b | A pipeline routes work (`→ agent`, `dispatch agent`) only to agents its May-dispatch table names |
| 10c | Every **ask** and **approve** touchpoint states what happens on no |
| 10d | Every ledger field and `project-state.md` section a file cites exists in its template |
| 10e | The bug statuses in `standards/qa/defect-reporting.md` and both bug templates are the same set |
| 10f | Every counter a state template pre-fills (`0/3`, `n/2`…) matches its bound in `references/bounds.md` |
| 10g | Every markdown table row has as many cells as its header |
| 11 | **Warning only**: a workflow file over 200 lines — under 200 is recommended, never required |

## Fixing what it reports

Fix the document, not the check — unless the check encodes the wrong rule, in which case say so rather than
loosening it quietly. Run it after any change under `.claude/`.

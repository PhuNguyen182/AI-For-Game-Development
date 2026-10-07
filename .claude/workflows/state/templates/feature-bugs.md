# Template — `<feature-root>/BUGS.md`

Copy the fenced block to `<feature-root>/BUGS.md` when QA first plans this feature. This file is the template,
never a record. Rules: `../README.md`; the lifecycle and statuses: `.claude/standards/qa/defect-reporting.md`.

One feature's **test cases and bugs**, in full: every case QA owes with its latest result, and every bug with
its evidence and status history. `<state-root>/bug-log.md` indexes the same bugs project-wide and is where their
IDs come from. Written only by the orchestrator, from what the QA and implementing agents return. Read by any
agent testing or debugging this feature, so a known bug is never filed twice.

```markdown
# Tests and Bugs — <feature name>

## Test cases

From `qa-lead`'s coverage assignment and the cases `/plan-test-coverage` or `qa-automation-engineer` derived.
One row per case, IDs `TC-01`, `TC-02`… allocated here by the orchestrator when the case is written; the result is the latest run, replaced on every run that covers it.

| ID | Case — expected behaviour and its source | Covered by | Observe via | Latest result | Run | Bugs |
|---|---|---|---|---|---|---|
| _none_ | | <agent-id> | Editor \| build/device \| measurement | Pass \| Fail \| Unrun — <why> | <when, which report> | BUG-#### |

## Bugs

One section per bug, ID from `<state-root>/bug-log.md`. Never deleted — a closed or rejected bug is the record
that stops the same finding being filed again.

### BUG-#### — <title>

- Status: Open | Fixed | Reopened | Closed | Won't fix | Accepted unverified | Escalated | As designed | Duplicate of BUG-####
- Severity: Critical | High | Medium | Low — impact if shipped
- Owner: <agent-id that owns the fix>
- Submission: <the submission the bug was found against — set when opened, never changed; its root-cause reset (B10) is the bug's>
- Opened by: <agent-id | gd>, <when>, <which report>
- Found by case: <TC-## | none — found outside the assigned cases>
- Location: <path:line | scene and entry point | artifact | scenario and metric>
- Expected: <behaviour, and the spec clause, GDD passage or budget that states it>
- Actual: <observed behaviour, not a diagnosis>
- Evidence: <log excerpt, screenshot, failing assertion, measurement with spread>
- Reproduction: <steps from a known state> · reproduced <n> of <m> attempts
- Regression test: <the test that now guards it | none yet>
- Reopens: 0/2

| When | From → To | By | Evidence |
|---|---|---|---|
| | — → Open | <agent-id \| gd> | <report> |

New evidence on an unchanged status is its own row, `Open → Open`, with the report that carried it.
```

# Template — `<state-root>/bug-log.md`

Copy the fenced block to `<state-root>/bug-log.md` the first time a bug is opened in a project. This file is the
template, never the log. Rules: `../README.md`; the lifecycle and statuses:
`.claude/standards/qa/defect-reporting.md`.

The project-wide **index** of every bug, and the **only place a bug ID is allocated**. A bug that belongs to a
feature has its full record in that feature's `BUGS.md`; this row mirrors its status and is corrected from the
record whenever the two disagree (`../README.md` → *Bugs*). A bug with no feature — a standalone QA run
(`qa-pipeline.md` **E4**), or a GD report outside any feature — keeps its full record here, under *Unattached
bugs*. Written only by the orchestrator.

```markdown
# Bug Log

Next ID: BUG-0001

## Index

| ID | Title | Feature | Severity | Status | Owner | Opened by | Reopens /2 | Record |
|---|---|---|---|---|---|---|---|---|
| _none_ | | <slug> \| — | Critical \| High \| Medium \| Low | Open \| Fixed \| Reopened \| Closed \| Won't fix \| Accepted unverified \| Escalated \| As designed \| Duplicate of BUG-#### \| Void — allocation interrupted | <agent-id> | <agent-id> \| gd | 0/2, then 0/1 after its reset (B6) | `<feature-root>/BUGS.md` \| below |

## Unattached bugs

Full records for bugs with no feature root, in the same shape as a feature's `BUGS.md` → *Bugs*; an unattached
bug's test case is written inline in its record.

_none_
```

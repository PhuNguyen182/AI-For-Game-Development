# Template — `<state-root>/project-state.md`

Copy the fenced block to `<state-root>/project-state.md` — `.workflow/project-state.md` unless the project's
`CLAUDE.md` names another path. This file is the template, never the record. Rules, including the lock reclaim:
`../README.md`. Only what cannot be held per feature lives here.

```markdown
# Project State

## In flight

One row per feature with an open ledger, so a new run finds it instead of opening a second slug.

| Slug | Status | Ledger |
|---|---|---|
| _none_ | | |

## Open gate debt

Source no gate has seen (I2). `unoffered` — the offer is still owed. `declined` — the GD said no (G50).
Recorded, never enforced. Clear a row only when the gate has actually returned on it.

| Path | Written by | When | Gate owed | State | Feature, if any | Settled |
|---|---|---|---|---|---|---|
| _none_ | | | review \| QA \| both | unoffered \| declined | | |

## Gated-direct counters

No feature root, so no ledger. Strikes cap at 2 (B4).

| Submission | Author | Strikes /2 | Verdicts landed |
|---|---|---|---|
| _none_ | | | |

## Standalone decisions

`research-decision.md` **E5**/**E6** have no feature root. What they decide that binds later runs lives here: the
GD's answer at the acceptance gate (G33) — a refused standard is what stops a later run re-deriving it — a
provisional decision's re-open threshold, and the measure-and-confirm count (B7).

| Decision | Run | GD's answer | Re-open threshold | Measure-and-confirm |
|---|---|---|---|---|
| _none_ | | accepted \| refused \| n/a | | 0/1 |

## Project-wide patterns

Pattern decisions a tech lead set with `Scope of pattern: project-wide`, so the next feature's brief carries them.

| Pattern | Set by | When | Applies to |
|---|---|---|---|
| _none_ | | | |

## Editor lock

One Unity Editor, project-wide (I3). Claim before dispatching a holder of Editor tools, release on return.

| Held by | Feature | Since | Claim expires | Last reclaim (holder, when, which I9 step answered) |
|---|---|---|---|---|
| _free_ | | | | |

## Device lock

One physical device, project-wide (I7). Independent of the Editor lock.

| Held by | Feature | Device | Since | Claim expires | Last reclaim (holder, when, which I9 step answered) |
|---|---|---|---|---|---|
| _free_ | | | | | |
```

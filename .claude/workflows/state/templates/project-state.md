# Template — `<state-root>/project-state.md`

Copy the fenced block to `<state-root>/project-state.md` — `.workflow/project-state.md` unless the project's
`CLAUDE.md` names another path. This file is the template, never the record. Rules, including the lock reclaim:
`../README.md`. Only what cannot be held per feature lives here.

```markdown
# Project State

Track: <client | client + multiplayer> — from `CLAUDE.md`, else the GD's answer at G26 (<when>); every dispatch
with no ledger carries it

## In flight

One row per feature with an open ledger, so a new run finds it instead of opening a second slug.

| Slug | Status | Ledger |
|---|---|---|
| _none_ | | |

## Open gate debt

Source no gate has seen (I2). `unoffered` — the offer is still owed. `declined` — the GD said no (G50). Recorded,
never enforced. Clear a row only when the gate has actually returned on it.

| Path | Written by | When | Tier | Gate owed | State | Feature, if any | Settled |
|---|---|---|---|---|---|---|---|
| _none_ | | | A3+ — A1–A2 declines are stated in the reply, never recorded (B18) | review \| QA \| assurance \| a combination | unoffered \| declined | | |

## Gated-direct counters

No feature, so no ledger — gated-direct submissions, and direct source the GD sent to review at G13 (origin
`direct`; a test suite at B5). Strikes cap at 2 (B4, B5). Each Implementation Note is at
`<state-root>/direct/S<n>.md`.

| Submission (`direct/S<n>`) | Author | Tier and axes | Strikes /2 | Verdicts landed |
|---|---|---|---|---|
| _none_ | | | | |

## Open asks with no ledger

Work with no feature root — gated-direct, mode 3, standalone runs — counts its asks here, so a resumed session
never restarts one. Remove the row when the ask is answered.

| Work | Ask | Count / bound |
|---|---|---|
| _none_ | `Needs Confirmation` on <value> (B9) \| escalation <agent → lead> (B16) \| `Blocked` on <input> (B17) | n/3 \| n/1 \| n/2 |

## Continuation debt with no ledger

Records from gated-direct, mode-3 and standalone work, whole — every field from `.claude/rules/execution-loop.md`.
An escalation to `feature-intake.md` **E1** carries its record into the new ledger.

_none_

## Standalone decisions

`research-decision.md` **E5**/**E6** have no feature root. What they decide that binds later runs lives here: the
GD's answer at the acceptance gate (G33) — a refused standard is what stops a later run re-deriving it — a
provisional decision's re-open threshold, and the measure-and-confirm count (B7).

| Decision | Run | GD's answer | Re-open threshold | Measure-and-confirm |
|---|---|---|---|---|
| _none_ | | accepted \| refused \| n/a | | 0/1 |

## Standalone QA runs

`qa-pipeline.md` **E4** has no ledger; its plan and counters live here until the run ends.

| Run | Tier and V-number | QA plan, verbatim | Sign-off re-dispatch /2 | QA rounds opening new bugs /3 | Open gaps |
|---|---|---|---|---|---|
| _none_ | | | 0/2 | 0/3 | |

## Project-wide patterns

Pattern decisions a tech lead set with `Scope of pattern: project-wide`, so the next feature's brief carries them.

| Pattern | Set by | When | Applies to |
|---|---|---|---|
| _none_ | | | |

## Editor lock

One Unity Editor, project-wide (I3). Claim before dispatching a holder — an agent with Editor tools, or anything
that writes into the Unity project — and release on return.

| Held by | Feature | Since | Claim expires | Last reclaim (holder, when, which I9 step answered) |
|---|---|---|---|---|
| _free_ | | | | |

## Device lock

One physical device, project-wide (I7). Independent of the Editor lock.

| Held by | Feature | Device | Since | Claim expires | Last reclaim (holder, when, which I9 step answered) |
|---|---|---|---|---|---|
| _free_ | | | | | |
```

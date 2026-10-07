# Change Request

Turns a GD change to an **already-approved** Tech Spec — mid-flight or after closure — into a severity, the
checkpoint it reopens, and a rework list. Starts when the change arrives, stops once the reopened checkpoint or
the rework has been handed on. A change before CP2 is not a change request: no approved spec exists to measure
it against, so it is an ordinary revision inside `feature-intake.md`.

This pipeline classifies what a change costs, never whether it is a good idea — the design judgment is the
GD's, the technology judgment `cto`'s.

## Entries

| Door | Comes from | Resumes at | Carries |
|---|---|---|---|
| **E1** | `orchestrator.md` step 0 — the GD changes a rule, GDD passage or requirement on a feature with a ledger (G70) | step 1 | The change **in the GD's own words**, the approved Tech Spec, the track state, the feature's current tier and axes |
| **E2** | `qa-pipeline.md` CP4 — the feature does what the spec said and the GD now wants something else (G60) | step 1 | The same, plus the QA reports that surfaced it |
| **E3** | `research-decision.md` settled the technology half of a bundled change | step 2 | The Technical Decision, any `Standard set:`, the Research Report's `Picture taken:` date, and whatever severity the rest of the request already received |

## May dispatch

| Agent | Returns / owns here |
|---|---|
| `technical-architect` | One `Change severity:` per independently-severable part, the code now needing rework, the reclassified tier and five axes, and — at Moderate/Major — the revised spec |
| `producer` | The **Status Report** that carries a Minor change to the GD (G72) |

Everything downstream belongs to its own file: CP1 and CP2 to `feature-intake.md`, the rework to
`feature-development.md`, re-verification to `review-pipeline.md` and `qa-pipeline.md`.

## Hard ordering

1. New dispatches against the questioned spec halt **before** classification starts (G70).
2. A part needing a strategic technology choice is settled before the rest of the request finishes
   classifying, and before any CP1 reopens — what `critic` re-tests can depend on which foundation is in play.
3. The reclassified tier is in the ledger before any rework is dispatched.
4. Rework against a Moderate or Major change dispatches only after the reopened checkpoint approves.

## Steps

1. **Halt.** Stop dispatching new work against the spec in question. Agents already running cannot be
   recalled; whatever they return after the change arrived goes onto the rework list as a candidate, never
   counted as a completed task.
2. **Classify.** `technical-architect` receives the change in the GD's own words (it blocks on a summary) and
   the track state (it silently assumes client-only without it). The severity is stated, never put to the GD
   (G71). It re-reads **all five axes**, not just U — new scope can move D, a newly touched economy path can
   move C. Severity and the A-tier are independent: severity picks the checkpoint, the tier sets how hard the
   rework is verified, so a Minor change on a credential path is still A5 and still owes V4. Write the new
   tier into the ledger's `Tier:` row (the move appended to `Tier history:`), re-derive the attempt budget and floor from it, and state any move per
   G43.
3. **Split a bundled request.** One `Change severity:` per independently-severable part. A part that forces a
   strategic technology choice — a netcode foundation, a vendor swap — gets **no** severity: it goes to
   `research-decision.md` **E2** with the four values (`references/dispatch-brief.md`), never straight to
   `cto`, which does not run without a candidate set. It returns here at **E3**, never into `feature-intake.md`,
   which cannot know a severity is still pending.
4. **Route by severity.**

   | Severity | Criterion | Direction-dependent spec fields | Goes to |
   |---|---|---|---|
   | **Minor** | Module boundaries and interfaces unchanged | Filled | The architect updates the spec in place; `producer` carries it in the next Status Report (G72) |
   | **Moderate** | The spec's structure changes; the original direction and its assumptions still hold | Revised in place | `feature-intake.md` **E4** — CP2 reopens (G73) |
   | **Major** | It invalidates an assumption `critic` tested or a risk the GD accepted at CP1 — **or** the reclassified axes now require CP1 (D4–D5, or U3) on a feature that never held one | `Pending CP1` — never invented ahead of the loop | `feature-intake.md` **E5** — CP1 reopens (G73) |

   **Minor is the only severity the GD never sees**, so any boundary or interface move at all is at least
   Moderate — neither the size of the diff nor how obvious it looks is the criterion. **E5** carries the
   revised spec, the change in the GD's own words (standing in for acceptance criteria while those read
   `Pending CP1`), the rework list, the options already ruled out, and the risks the GD accepted, read from
   the ledger's `## Decisions` half. A first CP1 has a legitimate empty history: state `none` for prior rounds,
   ruled-out options and accepted risks — never fabricate one.
5. **Rework.** No code exists against the superseded spec → resume the pipeline the change interrupted.
   Otherwise the rework list enters `feature-development.md` **E3**, taking its place in that pipeline's serial
   order, and is an ordinary submission from there — with its own gate offer (G74). A Major does not restart the
   feature: work the new direction still needs stays, and only the flagged code is reworked. A change after
   CP4 reopens the same ledger and in-flight row (never a second slug) and runs forward with its own CP3 and CP4;
   nothing earlier reopens retroactively.
6. **Ledger.** A decision the change overturns is superseded in place in the `## Decisions` half, never deleted
   (from A3 upward). Reset the counters of every submission the change invalidates, per the last paragraph of
   `references/bounds.md`. A Major also resets the `Advisor⇄Critic:` round count to 0 and notes the reset with
   its date; the ruled-out options are kept.

## GD touchpoints

- **G70** — entry: the change arrives in the GD's own words; new work against the spec halts first.
- **G71** — step 2: the severity is never put to the GD for confirmation; the reopened checkpoint is the check.
- **G72** — step 4, Minor: reaches the GD in the next Status Report, the only severity they never approve.
- **G73** — step 4, Moderate or Major: CP2 (G24) or CP1 (G21) reopens, Major carrying the risks already accepted.
- **G74** — step 5: the rework is a new boundary and gets its own gate offer per G50, whatever the GD answered
  before the change.
- **G6** — any `Blocked` input only the GD holds.
- **G43** — step 2: the tier moved.

## Bounds

- **B1** — `technical-architect`'s attempt budget inside the classification dispatch.
- **B17** — identical `Blocked` returns on one missing input.
- **B2** — reset to zero by a Major only; the ruled-out options survive the reset.
- **B1, B3, B10, B11, B12, B13** — reset on every submission the change invalidates (`references/bounds.md`,
  last paragraph): the author is never charged for the GD's change. A change request itself never counts as a
  CP2, CP3 or CP4 rejection.
- **B18** — the rework's gate offer is a new boundary, not a repeat ask.

## Exits

| Outcome | Control goes to | Ledger |
|---|---|---|
| Minor | Spec updated in place; `producer` at the next cycle; rework (if code exists) to `feature-development.md` **E3** | `Tier:`; superseded decisions; counter resets |
| Moderate | `feature-intake.md` **E4**, with the revised spec and the rework list | `Tier:`; superseded decisions; counter resets |
| Major | `feature-intake.md` **E5** | `Tier:`; `Advisor⇄Critic:` round reset, ruled-out list kept; counter resets |
| A part needs a strategic technology choice | `research-decision.md` **E2**; back at **E3** | — until the remaining severity is classified |
| No code against the superseded spec | The interrupted pipeline, at the step the ledger's `Position:` names | — |
| `technical-architect` → `Blocked` | Supply the GD's own words unedited, or the track state (G6) | — |
| `producer` → `Needs-decision`, `Routed to: technical-architect` | Re-dispatch the architect with both conflicting reports | — |
| `producer` → `Blocked` | Supply the reports behind the change — never reconstruct status by inference | — |
| A bound reached | The GD (G7) | `### Continuation debt` |

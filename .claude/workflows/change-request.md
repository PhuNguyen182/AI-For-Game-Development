# Change Request

Turns a GD change to an **approved baseline** — a Tech Spec past CP2, or D1–D2 direct notes already handed off;
mid-flight or after closure — into a severity, the checkpoint it reopens, and a rework list. Starts when the change
arrives, stops once the reopened checkpoint or the rework has been handed on. A change before the baseline is
approved is not a change request: it is new input to the intake run in progress (`orchestrator.md` step 0).

This pipeline classifies what a change costs, never whether it is a good idea — the design judgment is the GD's,
the technology judgment `cto`'s.

## Entries

| Door | Comes from | Resumes at | Carries |
|---|---|---|---|
| **E1** | `orchestrator.md` step 0 — the GD changes a rule, GDD passage or requirement on a feature with a ledger (G70) | step 1 | The change **in the GD's own words**, the approved baseline (the ledger's `Spec:`), the track state, the feature's current tier and axes |
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
2. A part needing a strategic technology choice is settled before the rest of the request finishes classifying, and
   before any CP1 reopens — what `critic` re-tests can depend on which foundation is in play.
3. The reclassified tier is in the ledger before any rework is dispatched.
4. Rework against a Moderate or Major change dispatches only after the reopened checkpoint approves.

## Steps

1. **Halt.** Stop dispatching new work against the spec in question. Agents already running cannot be recalled;
   whatever they return after the change arrived is held — not a submission, no gate — and the architect's rework
   list decides it at step 2: still fits the changed spec → a submission from there; otherwise rework.
2. **Classify.** `technical-architect` receives the change in the GD's own words (it blocks on a summary) and the
   track state (it silently assumes client-only without it). The severity is stated, never put to the GD (G71). It
   re-reads **all five axes**, not just U — new scope can move D, a newly touched economy path can move C. Severity
   and the A-tier are independent: severity picks the checkpoint, the tier sets how hard the rework is verified, so
   a Minor change on a credential path is still A5 and still owes V4. Write the new tier into the ledger's `Tier:`
   row (the move appended to `Tier history:`), re-derive the attempt budget and floor from it, and state any move
   per G43. A `design` line the classification returns goes to the GD (G27) before severity routes — unless it
   reopens what CP1 locked, which is Major.
3. **Split a bundled request.** One `Change severity:` per independently-severable part — parts that rework the
   same code are not severable: they take the higher severity and rework together. A part that forces a
   strategic technology choice — a netcode foundation, a vendor swap — gets **no** severity: it goes to
   `research-decision.md` **E2** with the four values (`references/dispatch-brief.md`), never straight to `cto`,
   which does not run without a candidate set. It returns here at **E3**, never into `feature-intake.md`, which
   cannot know a severity is still pending.
4. **Route by severity.**

   | Severity | Criterion | Direction-dependent spec fields | Goes to |
   |---|---|---|---|
   | **Minor** | Module boundaries and interfaces unchanged | Filled | The architect updates the spec in place; `producer` carries it in the next Status Report, or a one-line notice when none is due (G72) |
   | **Moderate** | The spec's structure changes; the original direction and its assumptions still hold | Revised in place | `feature-intake.md` **E4** — CP2 reopens (G73). A D1–D2 baseline has no CP2: **E3** — grown to D3+, the spec is written and CP2 runs for the first time; still D1–D2, the revised notes go to the GD for approval (G73) before the hand-off |
   | **Major** | It invalidates an assumption `critic` tested or a risk the GD accepted at CP1 — **or** the reclassified axes now require CP1 (D4–D5, or U3) on a feature that never held one | `Pending CP1` — never invented ahead of the loop | `feature-intake.md` **E5** — CP1 reopens (G73) |

   **Minor is the only severity the GD never sees**, so any boundary or interface move at all is at least Moderate
   — neither the size of the diff nor how obvious it looks is the criterion. **E5** carries the revised spec, the
   change in the GD's own words (standing in for acceptance criteria while those read `Pending CP1`), the rework
   list, the options already ruled out, and the risks the GD accepted, read from the ledger's *GD decisions*. A
   first CP1 has a legitimate empty history: state `none` for prior rounds, ruled-out options and accepted risks —
   never fabricate one.
5. **Rework.** No code exists against the superseded spec → resume the pipeline the change interrupted. Otherwise
   the rework list enters `feature-development.md` **E3**, taking its place in that pipeline's serial order, and is
   an ordinary submission from there (a new `S<n>`, strikes from zero) — gates the feature already authorised run on
it unasked, and G74 offers only what `Gates:` leaves open. A Major does not restart the feature: work
   the new direction still needs stays, and only the flagged code is reworked. A change after CP4 reopens the same
   ledger and in-flight row (never a second slug) and runs forward with its own CP3 and CP4; nothing earlier
   reopens retroactively.
6. **Ledger.** A decision the change overturns is superseded in place in the ledger's *GD decisions* — and in the
   feature root's `DECISIONS.md` by the rework that changes it — never deleted (from A3 upward). Reset counters
   exactly as `references/bounds.md` → *Resets* lists — per invalidated submission, per feature when CP2 or CP1
   reopens, and B2 on a Major (noted with its date; the ruled-out options are kept).

## GD touchpoints

Where each fires; what it carries and what happens on no are `gd-touchpoints.md`'s alone.

**G70** at entry · **G71**, **G43**, **G27** step 2 · **G72**, **G73** step 4 · **G74** step 5 · anywhere: **G6**.

## Bounds

- **B1** — `technical-architect`'s attempt budget inside the classification dispatch.
- **B17** — identical `Blocked` returns on one missing input.
- **Resets** — exactly `references/bounds.md` → *Resets*: the author is never charged for the GD's change, and a
  change request itself never counts as a CP2, CP3 or CP4 rejection.
- **B18** — the rework's gate offer is a new boundary, not a repeat ask.

## Exits

| Outcome | Control goes to | Ledger |
|---|---|---|
| Minor | Spec updated in place; `producer` at the next cycle; rework (if code exists) to `feature-development.md` **E3** | `Tier:`; superseded decisions; counter resets |
| Moderate | `feature-intake.md` **E4**, with the revised spec and the rework list — **E3** on a D1–D2 baseline | `Tier:`; superseded decisions; counter resets |
| Major | `feature-intake.md` **E5** | `Tier:`; `Advisor⇄Critic:` round reset, ruled-out list kept; counter resets |
| A part needs a strategic technology choice | `research-decision.md` **E2**; back at **E3** | — until the remaining severity is classified |
| No code against the superseded spec | The interrupted pipeline, at the step the ledger's `Position:` names | — |
| `technical-architect` → `Blocked` | Supply the GD's own words unedited, or the track state (G6) | — |
| `producer` → `Needs-decision`, `Routed to: technical-architect` | Re-dispatch the architect with both conflicting reports | — |
| `producer` → `Blocked` | Supply the reports behind the change — never reconstruct status by inference | — |
| A bound reached | The GD (G7) | *Continuation debt* |

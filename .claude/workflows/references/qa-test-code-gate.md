# The Test-Code Gate — `qa-pipeline.md` step 3b

> **Read when `qa-automation-engineer` has written a suite.** Split out of `qa-pipeline.md` under the
> promotion rule in `client/feature-documentation.md`: it fires only on the one QA agent that writes `.cs`,
> so most QA runs never open it.

`qa-automation-engineer` is the only agent here holding `Write`/`Edit`, and the `.cs` it produces is source
like any other — a weakened assertion or a test asserting the wrong behaviour is a defect that advertises
coverage it does not have, which `verification-standards.md` calls worse than no suite at all.

**Its submission has a route to a gate: `review-pipeline.md` E3**, offered to the GD as its own ask per
`optional-gates.md` once the suite is written. It carries an author and a strike count capped at
two, and no CP3 — there is no Tech Spec for a test suite.

**"Written" is the trigger, not "written and green."** This file previously said green, and a live run
produced the case that wording excludes: the suite was authored in full and **never executed**, because the
environment had no toolchain. A suite nobody has run is the one most worth reading — nothing has checked that
its assertions hold, or that they assert anything — so conditioning the offer on a green run reopens
invariant **I10**'s hole for exactly the submission that needs the gate most. Offer it, and say in the ask
that the suite is unrun; a gate reviewing an unexecuted suite is reviewing assertions, which is what
`code-reviewer` does anyway. Declined, it is recorded as review debt against
those paths exactly like any other declined gate. This closes invariant **I10**: source that reaches no gate
is a hole, not debt, and the hole was that **E1** accepted submissions only from `feature-development.md`.

## Where the second strike goes — not where the other E3 origin goes

**E3** carries two kinds of submission and they escape the cap in opposite directions. The gated-direct lane
escalates to `feature-intake.md` **E1**, because two rejections on a one-role change is evidence the input
was mis-sized and classification should start over from what was learned.

**A test suite has nothing for that door to classify.** There is no feature request behind it, no direction
to settle and no Tech Spec to produce — intake would be handed a `.cs` file and asked what the GD wants
built. So at the second strike the suite returns to **`qa-lead` as unrun coverage**: the exit criteria that
suite was written to satisfy are still unmet, which is exactly the gap `qa-pipeline.md` step 4 already knows
how to carry — re-dispatch within its own two-round sign-off bound, or to **CP4** as a gap only the GD can
accept. Two gate rejections on a suite means the coverage is not trustworthy, and *"not trustworthy"* is a
coverage verdict, never a feature request.

The cap itself is registered in `references/loop-termination.md` beside the gated-direct one, so the two are
visibly different counters rather than one number applied twice.

## Why this is not optional-by-omission

`orchestration.md` invariant **I2** says review debt attaches to the artifact rather than to the run — but a
debt with no route to settle it is not debt, it is a hole. Before **E3** existed, `qa-automation-engineer`'s
`.cs` was the one artifact in the layer that could accrue debt no gate would ever accept.

The gate is still **offered, not imposed** — review is optional here exactly as everywhere else, per
`optional-gates.md`. What changed is that declining it is now a decision the GD made, recorded in
`<state-root>/project-state.md`, rather than a door that was never built.

## What the ask should say

The specific cost of skipping this one, in the terms `optional-gates.md` requires: **a test asserting the
wrong behaviour reports green and advertises coverage that does not exist.** `verification-standards.md`
calls that worse than having no suite at all, because the suite is what the next session will trust instead
of re-checking.

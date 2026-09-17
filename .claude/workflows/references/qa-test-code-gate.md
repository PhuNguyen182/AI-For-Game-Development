# The Test-Code Gate — `qa-pipeline.md` step 3b

> **Read when `qa-automation-engineer` has written a suite.** Split out of `qa-pipeline.md` under the
> promotion rule in `client/feature-documentation.md`: it fires only on the one QA agent that writes `.cs`,
> so most QA runs never open it.

`qa-automation-engineer` is the only agent here holding `Write`/`Edit`, and the `.cs` it produces is source
like any other — a weakened assertion or a test asserting the wrong behaviour is a defect that advertises
coverage it does not have, which `verification-standards.md` calls worse than no suite at all.

**Its submission has a route to a gate: `review-pipeline.md` E3**, offered to the GD as its own ask per
`optional-gates.md` once the suite is written and green. It carries an author and a strike count capped at
two, and no CP3 — there is no Tech Spec for a test suite. Declined, it is recorded as review debt against
those paths exactly like any other declined gate. This closes invariant **I10**: source that reaches no gate
is a hole, not debt, and the hole was that **E1** accepted submissions only from `feature-development.md`.

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

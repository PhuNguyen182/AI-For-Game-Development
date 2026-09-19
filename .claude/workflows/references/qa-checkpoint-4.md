# Checkpoint 4 — the detail

> **What `producer` compiles, how an accepted gap is recorded, and how a rejection splits.** Split out of
> `qa-pipeline.md` under the promotion rule in `client/feature-documentation.md`. **`qa-pipeline.md` still
> owns CP4** — this file is its detail, not its owner, and the pointer there is the entry to it.

CP4 is the last gate, and the only one where a feature closes carrying a gap the GD chose to accept.

`producer` compiles the end-of-feature report and the GD closes the feature. Its input is every QA report,
`qa-lead`'s verdict quoted as stated, the Assurance Verdict at A3 or above, and — at D1–D2,
where CP3 merged into this gate — both review verdicts **where review ran**. Where it did not, the report
says so in those words rather than omitting the line; a missing section reads as nothing found. It orders and
attributes; it never adjudicates, and no Implementation Summary appears here: the merge means the GD *sees*
the review outcome, and the architect's Direct depth exists to skip it.

**At A3 and above the Assurance Verdict is owed, and its absence is stated rather than left out.** `producer`
reports what it is given and infers nothing — *"an unreported item is reported as unknown"* is its guardrail,
but it has no field for an input it was never told to expect. Live, a CP4 dispatch that omitted the verdict
produced a complete-looking report that never mentioned one was due, and offered the GD an accepted gap over
a finding no waiver reaches. So the dispatch either carries the verdict or says **why there is none** — the
work is A1/A2, the gate returned `Rejected`, or QA was declined outright.

**An acceptance state is not a sign-off, and neither replaces the other.** `qa-lead` says whether the feature
was covered; `assurance-evaluator` says whether what was claimed is evidenced and whether the effort fit. A
feature can be signed off and still return `CONDITIONAL PASS`. Quote both, never merge them.

**Accepting a gap is a decision, not a shortcut.** `qa-lead` is barred from signing off an unmet criterion
*because that judgment is the GD's*, so the override is legitimate by design — but the gap must land
somewhere durable, or CP4 becomes the failure `qa-lead` exists to prevent: "nobody checked" recorded as "QA
passed". **A mobile feature that never ran on a device is the canonical case.** Write every accepted gap into
the known limitations **before** reporting closure; from **A3** upward into the feature root's
`DEBT.md`, per `.claude/standards/client/feature-documentation.md` — an accepted gap is exactly the trigger that
file owes that document for.

**A rejection is one of two things, and they route differently:**

| The GD's objection | It is | Route |
|---|---|---|
| It does not do what the approved spec said | A defect | `feature-development.md` **E3**, then back through review and whatever coverage it touched. The spec still stands |
| It does what the spec said, and the GD now wants something else | A change request | `technical-architect` for `Change severity:` — Minor updates the spec in place, Moderate rolls back to CP2, Major to CP1 |

The GD names what is wrong; `technical-architect` classifies what it costs — `producer` is barred from
technical judgment and `qa-lead` has already returned its verdict. The Minor/Moderate/Major mechanics belong
to `change-request.md`; the split above is what this file owns.

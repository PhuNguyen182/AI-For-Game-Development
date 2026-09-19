# QA Exit & Custody — `qa-pipeline.md`

> **Read when any QA agent returns.** Which door each result takes, and where every returned field is
> recorded when no `Status:` row names it. Split out of `qa-pipeline.md` under the promotion rule in
> `client/feature-documentation.md`.

This pipeline declared no exits for four rounds while four other files named it as their origin or their
destination. That is the same hole `development-exit-and-custody.md` and `review-exit-and-custody.md` closed
one pipeline each; this is QA's half.

## The eight deliverables, and what each becomes

Declared under `Produces` in the pipeline's agent table. Until this round the table had no such column at
all — its third column was "Runs in" — so the layer's own custody check read the wrong cell, found one
bolded artifact there and **passed**. Seven of the eight had never been checked, and six of them were named nowhere in this pipeline's own text or its own references.

| Produced | What it becomes |
|---|---|
| **QA Plan** — `qa-lead`, plan mode | The coverage assignment dispatched at step 2, and the exit criteria step 4 is judged against. Both to the ledger at the step 1 transition |
| **QA Verdict** — `qa-lead`, sign-off | `Signed off` → step 4b at A3+, then `producer`. `Not signed off` → the gap routes below. Quoted at CP4 as stated, never merged with the acceptance state |
| **Test Report** — `qa-automation-engineer` | Its `Defects:` to their owners at **E3**; its `Not covered:` to the gap list; its `Tests added:` to the test-code gate at `review-pipeline.md` **E3** |
| **Playtest Report** — `playtest-tester` | Routed on **`Classification:`**, because this envelope has neither `Defects:` nor `Not covered:`: `Technical defect` to its owner at **E3**, `Design flaw` to the GD immediately, `As designed` to the record. Its `Evidence:` stays with the finding that cites it |
| **Performance Verification** — `performance-qa-engineer` | Its `Regressions:` to the owner named inside them; `Measured on:` travels with every quotation of the number; `Metrics:` to the ledger's `Baseline:` where none existed |
| **Build Verification** — `build-verification-tester` | Its `Defects:` and `Build-only faults:` to the owner the evidence names; its `Not covered:` to the gap list as unrun **device** coverage, which no Editor result replaces |
| **Assurance Verdict** — `assurance-evaluator` | The acceptance state routes per `qa-assurance-gate.md`; `Not scored:` is a gap list; `Iteration:` reconciles against the ledger's attempts-used |
| **Status Report** — `producer` | CP4 itself. The GD closes the feature on it |

## The doors out

| Result | Goes to |
|---|---|
| A defect with a named owning `agent-id` | `feature-development.md` **E3** — then whatever gates ran, then back here at **E3** |
| A defect found on a **fix** already returning at E3 | Same door, same strike count. The QA-fail counter is the ledger's, never the agent's |
| `qa-automation-engineer`'s test `.cs` | `review-pipeline.md` **E3**, offered as its own ask — `qa-test-code-gate.md` |
| A **design flaw**, from any agent here | **The GD, immediately** — invariant **I5**. Never folded into the next report |
| A contradicted or unevidenced **verification claim** | The GD, immediately, and to `assurance-evaluator` at step 4b if it has not yet run. Never the accepted-gap lane |
| `qa-lead` → `Needs-decision` — the spec states no testable behaviour, or two reports contradict | `technical-architect` |
| `performance-qa-engineer` → a native, GPU or leak cause | `tech-lead-performance` · a budget unachievable for the design → `technical-architect` |
| `build-verification-tester` → a build-only fault | By the evidenced cause: `build-run-engineer` (the artifact), `unity-engineer` (client code), `tech-lead-sdk-platform` (an SDK or store integration). **Its Escalate row names all three**, and a pipeline that routes only the first drops the other two |
| A crash or ANR on the device under test | `/investigate-device-crash` — never `crash-anr-investigator` |
| CP4 rejected **as a defect** | `feature-development.md` **E3** |
| CP4 rejected **as a change request** | `change-request.md` **E2** — which declares that door and names CP4 as its origin |
| CP4 approved | The feature closes; accepted gaps are already written, per `qa-checkpoint-4.md` |

## The exit criteria are the caller's to carry back

`qa-pipeline.md` step 4 used to say `qa-lead` judges the reports against the exit criteria *it wrote itself*
at step 1. It cannot: it is stateless, its own contract says the caller owns what it has already seen, and no
`If absent` row makes it say so when they are missing.

**Run live, that is exactly what happened.** The same feature was planned and then signed off; the sign-off
returned a *different* criteria list — one that had dropped the recording of review debt at closure, the
mandatory `Not covered` field and the `DEBT.md` obligation, and had grown a regression-pass criterion the
plan never set. The verdict did not change, because the evidence was zero either way. On a feature with real
evidence, that difference is the verdict.

**So the criteria travel with the sign-off dispatch, verbatim, exactly as the coverage assignment does** —
and both are written into the feature's ledger at the step 1 transition, because a plan that survives only in
the conversation is not a contract. Where they genuinely cannot be recovered, say so in the dispatch: a
re-derived bar stated is a gap; a re-derived bar unstated is the sign-off measuring against itself.

## Coverage that could not be executed is not coverage that failed

An executor returning `Status: Done` with `Results: 0 / 0` has completed its job and produced **no
verification**. Live, `qa-automation-engineer` authored the suite, found no toolchain, reported the
environment check it actually ran, and labelled every finding **E1 hand-trace inspection, explicitly not a
run result** — which is the behaviour `verification-standards.md` requires.

The pipeline must not launder it:

- **Its findings are not QA findings.** Reading is review; running is verification. Route them as
  inspection-grade defects — real, owned, worth fixing — and never record them as coverage that ran.
- **Every case it names goes to `qa-lead`'s gap list**, exactly like `Not covered`.
- **It is not a Continuation Debt Record.** That is an exhausted attempt budget, per `execution-loop.md`.
  This is an environment that cannot run the check at all, which no further attempt reaches.
- **It does not spend the sign-off re-dispatch bound.** `loop-termination.md` bounds re-dispatch at 2 for
  coverage *not yet run*; re-dispatching coverage that is *unrunnable* buys the same return twice.

## An `Acceptance: FAIL` does not always have an owner

The routing row sends a `FAIL` to the named owner at **E3**. Live, it had none: the gate failed the
Implementation Note's verification claims, and the note is **pipeline-assembled** per
`rules/implementation-note.md` — so the return named `Routed to: gd` and said in those words that the inputs
did not identify which implementing agent originated the claim.

**Where the failed claim is the note's own, the finding is the assembling pipeline's and it goes to the GD**,
with the claim quoted and the evidence that contradicts it. Where it belongs to a submission, it goes to that
submission's author at **E3**. Either way `effort-allocation.md` puts it beyond any waiver, so it never
travels as an accepted gap — which is the one place CP4 could silently absorb it.

## Custody — every field that outlives its dispatch

| Returned field | Where it is recorded |
|---|---|
| `Coverage assignment:`, `Exit criteria:` | The ledger, at the step 1 transition — and back into the sign-off dispatch |
| `Gaps:` that cannot be closed | The ledger's **Accepted gaps** once the GD accepts them, and `DEBT.md` from A3 — **before** closure is reported |
| `Not covered:` / `Not measured:` | `qa-lead`'s gap list at step 4. Mandatory on the **three envelopes that carry it** — `qa-automation-engineer`, `performance-qa-engineer`, `build-verification-tester` — and never `none` there unless coverage genuinely was exhaustive. **`playtest-tester` has no such field**, so what its scenario did not reach is the caller's to note against the plan rather than an omission to read into its report |
| `Metrics:` / `Baseline:` | The ledger's `Baseline:` row, **written by the pipeline at the return** — `state/README.md` says the row exists to stop a run silently becoming the baseline, and a first measurement is exactly that run |
| `Measured on:` | Travels with every quotation of the number. An Editor figure is labelled indicative every time, and never satisfies a device claim |
| `Evidence:` — captures and log excerpts | Stays with the report; the defect that cites it carries the anchor, per `qa/defect-reporting.md` |
| `Build-only faults:` | The defect route above, plus the ledger — a fault absent in the Editor is the one class no later Editor run will re-find |
| `Tests added:` | The test-code gate at `review-pipeline.md` **E3**, and the paths into the ledger's submission table |
| `Acceptance:`, `Dimension scores:`, `Not scored:` | `producer`'s CP4 input, quoted rather than merged with the sign-off. **`Not scored:` is a gap list, not a footnote** |
| `Iteration:` | The ledger's attempts-used. Where the gate could not evidence what a retry improved, that is recorded as unevidenced, never as improvement |
| A finding **outside** the coverage assignment | Routed to its owner like any other, and named to `qa-lead` so the criterion it touches is re-planned rather than lost |

## Rules

- Every door above is named by the file it hands to. A hand-off nobody declares is how `change-request.md`
  **E2** sat for four rounds with an origin that never named it.
- `Status: Done` is a completed job, never a pass. Read the body.
- Coverage that could not run is reported as unrun, at every later quotation of it.
- A verification claim that no report supports goes to the GD, never into the accepted-gap lane.
- Nothing here is recorded at closure. Every row is written at the transition that produced it.

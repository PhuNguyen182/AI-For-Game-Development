# Loop Termination — every cap in the layer, and what happens when one is reached

> **Read when a cap is reached, and when adding any loop.** This file is the **single home for every bound in
> the layer**. A loop whose cap is not in the table below does not have one, and a loop without a cap is a
> defect regardless of how unlikely repetition looks.

`execution-loop.md` requires that an exhausted budget produces a **Continuation Debt Record**, never a silent
stop and never a claim of completion. That rule covers one agent inside one dispatch. This file applies the
same discipline one level up, to the counters `orchestration.md` invariant **I4** gives the orchestrator.

## Every cap in the layer

| Counter | Bound | Scope | Stated in |
|---|---:|---|---|
| Attempt budget | 2–5, from **D** | One agent's corrective cycles inside **one dispatch** | `execution-loop.md` |
| Advisor⇄Critic rounds | 3 | One feature's direction loop | `feature-intake.md` |
| Review strikes | 3 | **One submission** | `review-pipeline.md` |
| Gated-direct strikes | 2 | One gated-direct submission | `references/gated-direct-lane.md` |
| QA fails | 2 | One submission passing review and failing QA | `qa-pipeline.md` |
| Measure-and-confirm | 1 | One `cto` decision | `research-decision.md` |
| **Standalone gate re-decides** | **1** | One standalone result at its acceptance gate | **here** |
| `Needs Confirmation` asks | 3 | One credential-shaped value | `references/review-needs-confirmation.md` |
| **Root-cause resets** | **1 per submission** | Every loop above, shared | **here** |
| **CP2 rejections** | **3** | One Tech Spec | **here** |
| **CP3 rejections** | **2** | One feature at the build gate | **here** |
| **CP4 defect rejections** | **2 before root cause, 3 to stop** | One feature at its closing gate | **here** |
| **Sign-off re-dispatch** | **2** | One feature's coverage loop | **here** |
| **Assurance `FAIL` returns** | **1**, then it is a QA fail | One submission | **here** |
| **Escalation-lane round trips** | **1** | One implementing agent and one tech lead | **here** |
| **Identical `Blocked`** | **2** | One dispatch and one missing input | **here** |
| **Gate re-offers** | **1 per boundary**, never twice in a run | One artifact | **here** |

Ten of those seventeen are stated here and nowhere else, because each one is a *composition* of loops that
were individually bounded and jointly were not.

## The root-cause reset — once, and only once

Three strikes sends a submission to `technical-architect` for root cause rather than a fourth review pass.
What comes back is a cause, not a verdict, and the fix re-enters at `feature-development.md` **E3**.

**That return resets the submission's strike count to zero, and the reset is available once.** Record it in
the ledger as `Root-cause resets: 1/1` beside the strike count — without it the next session cannot tell a
first three-strike run from a second.

**The same single reset covers every loop that can reach the architect**: the QA bound, the CP3 bound and the
second CP4 defect rejection all consume it. A submission does not get one reset per loop; it gets one reset,
whichever loop spent it.

**Past the reset, the loop is over.** It does not return to `technical-architect`, and it does not re-enter
**E3**. It goes to the GD as a feature-level Continuation Debt Record, in `execution-loop.md`'s own fields,
carrying:

- every verdict and every QA report from both runs,
- the architect's cause from the first reset — a cause that did not hold is itself the finding,
- the **known non-solutions**, so the next session does not re-run an approach already proven to fail,
- a safe resume point, and the `Next best action:` the architect named.

Six review rounds or four QA rounds on one submission is not a code problem, and a seventh will not find it.
What the GD decides from there — re-spec it, cut the scope, drop the feature — is theirs, and every one is a
legitimate outcome the layer cannot reach on its own.

## The checkpoint bounds — on repetition, never on the GD

The GD owns every checkpoint and is never capped. What is capped is **silent repetition**: the same artifact
going out, coming back rejected, and going out again with nobody asking why.

| Checkpoint | 1st rejection | 2nd | 3rd |
|---|---|---|---|
| **CP2** — the Tech Spec | `technical-architect` revises | Revises again | **Stop.** Three specs the GD would not approve is a direction problem, not a drafting one: to **CP1** if the loop is available at this D, otherwise to the GD with the three rejections and what changed between them |
| **CP3** — what was built | The named drift to `feature-development.md` **E3** | Same, **plus** `technical-architect` for root cause first — it spends the shared reset | **Stop.** Feature-level Continuation Debt Record |
| **CP4** — closing the feature | **E3**, ordinary rework, back through whatever gates ran | Same, **plus** root cause before the fix is dispatched | **Stop.** Continuation Debt Record with both causes attached |

A rejection classified as a **change request** never counts at any of the three. The code did what the
approved spec said; the spec moved. `change-request.md` already resets the strike count and the attempt
budget on every submission it invalidates, and it resets these three counters with them — the author is not
charged for the GD's change.

**A Major change additionally resets the Advisor⇄Critic round count**, and it is the one cap in this table
that a re-entry clears. Major is defined as invalidating an assumption `critic` tested or a risk the GD
accepted at CP1: the rounds already spent settled a direction that no longer exists, so charging them to the
new one hands it whatever is left of the cap — one round, on a feature that used two. Every other cap here
survives a re-entry, per `references/entry-index.md`.

## The QA-side loops

**Sign-off re-dispatch is bounded at 2.** `qa-lead` returning `Not signed off` with coverage still runnable
sends those `agent-id`s back to step 2, and the result returns to sign-off. Twice. A third time means the
exit criteria cannot be met by running more of the same coverage: the gap goes to CP4 as a gap only the GD
can accept, which is what `qa-pipeline.md` already does for a gap that cannot be closed.

**An `Acceptance: FAIL` from `assurance-evaluator` is charged once as itself, then as a QA fail.** The first
`FAIL` returns to the named owner at **E3** as an integrity finding and is not a QA round. A second `FAIL` on
the same submission **is** a QA fail and spends that counter — because at that point the loop is no longer
"a claim was unsupported" but "the author cannot make the claim supportable", which is exactly what the
two-round QA bound exists to catch. This bound never softens the verdict itself: `effort-allocation.md` puts
a false verification claim beyond any GD waiver, and a bound on how many times we *ask* is not a waiver.

## The escalation lane — one round trip

`tech-lead-performance` returning `Rejected`, `Routed to: unity-engineer` when the obvious fixes are still
open, and `tech-lead-csharp-unity` naming a misrouted escalation, are both correct refusals. They are also
both a ticket back to the agent that escalated — and nothing stopped it escalating again.

**One round trip.** Implementing agent → tech lead → refused → implementing agent. If the same problem
escalates a second time and the lead refuses a second time, the two disagree about whose problem it is, and
neither can settle that. It goes to `technical-architect` as a routing question, not to either of them again.

## Repeated `Blocked` — two, then stop

`Blocked` on a genuinely missing input is a correct result, and the action is always the same: supply exactly
the input named, then resume. But nothing bounded the case where the input cannot be supplied — the GD does
not have it, no document states it, and the dispatch goes out a third time hoping.

**Two identical `Blocked` returns on the same dispatch and the same missing input is the bound.** Past it,
the missing input is itself the finding: report it to the GD as unresolved, with what was asked for, who was
asked, and what it blocks. `task-classification.md` already says a material conflict is stated and bounded
rather than guessed; this is the same rule applied to a missing input that keeps not arriving.

A *different* missing input is a different `Blocked` and starts its own count. The bound is on repetition,
not on the return.

## Gate re-offers — once per boundary

Review and QA are optional, per `references/optional-gates.md`, and a declined gate is re-offered at a later
natural boundary. **"Re-offered" is not "re-asked".**

- **Once per boundary.** Within one run, once the GD has answered for an artifact, the answer stands. Asking
  again because the work grew, or because the recommendation was not taken, is nagging — and nagging trains
  the GD to stop reading the ask, which costs far more than the gate would have.
- **A new boundary is a new fact, not a new mood.** The next feature touching that root, a release, a defect
  traced to the ungated code, or the GD asking. Each of those is new information; the passage of time is not.
- **The recommendation is stated once, in the ask.** Never repeated after they answer, and never restated in
  the closing report as a complaint. The debt row in `<state-root>/project-state.md` is the durable record,
  and it is neutral by design.

## The standalone acceptance gate — one re-decide

`research-decision.md` **E5**/**E6** end at a GD gate rather than a checkpoint, because a standalone run has
no CP2 behind it. Its two rejections are not the same loop, and only one of them is a loop at all:

- **The standard is rejected** — terminal. It is simply not recorded and no ADR is dispatched; `cto`'s
  decision still stands for that run. Nothing is re-dispatched, so nothing needs bounding.
- **The decision is rejected** — back to step 4 **once**, carrying what the GD objected to.

Past that the call is the GD's to make directly. A second refusal means `cto` cannot reach an answer they
will accept, and a third dispatch buys the same one again — the loop is over, not slower.

## What a terminated loop must never do

- **Never report closure.** A loop that ran out is `Blocked`, `Partially complete` or `Failed`, per
  `execution-loop.md`'s stop rule — never folded into a summary that reads as done.
- **Never restart a counter by renaming the work.** Splitting one submission into two to reset a strike count
  is the prohibited behaviour `execution-loop.md` names outright.
- **Never re-dispatch the same brief.** A return after any cap carries the known non-solutions, or the next
  cycle buys the same failure a second time.
- **Never let a cap override the GD.** Each bound here stops the *layer* from looping on its own. The GD can
  direct another round at any point, and that direction is recorded in the ledger with the cost stated first.

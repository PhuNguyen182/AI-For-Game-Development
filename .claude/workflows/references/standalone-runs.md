# Standalone Runs — every pipeline is callable on its own

> **Read when the GD names a pipeline instead of describing a feature.** This is `orchestrator.md`'s **mode
> 2**, stated per pipeline: what each one does when nothing upstream ran, what the GD must supply in place of
> that upstream, and what it returns instead of handing on.

The seven files are not one chain with seven segments. Each answers a different question and each is worth
running alone — an audit without a feature, QA on code that shipped months ago, research with nothing
attached, a spec for something somebody else will build. **The chain is one way to compose them, never the
only way in.**

## What each pipeline is, run alone

| Run alone | It answers | Enter at |
|---|---|---|
| `feature-intake.md` | "What should we build, and how should it be shaped?" — classification, direction, a Tech Spec somebody else may implement | **E1** |
| `research-decision.md` | "What exists today for a capability we lack?" — a sourced, dated answer, or a measured one | **E5**, or **E6** for a spike |
| `feature-development.md` | "Build this." — implementation against notes, with no spec round first | **E2** |
| `review-pipeline.md` | "Is this code correct, and is it safe?" — a report on code already in the repo | **E2** |
| `qa-pipeline.md` | "Does this actually work?" — coverage, evidence, and a sign-off against criteria | **E4** |
| `change-request.md` | "What does this change cost?" — blast radius and the rework list | **E1** |

## What the GD supplies in place of the upstream

A standalone run has no ledger, no prior verdict and no brief behind it. Every pipeline's own entry table
still governs; this is only what changes when there is nothing upstream to read it from.

| Pipeline | Supply, because nothing upstream did |
|---|---|
| `feature-development.md` **E2** | The notes themselves — what to build, in enough detail that one `agent-id` owns it. Plus the track state, and the tier if the GD wants one other than the default classification. Without a stated intent the agent works from the request alone, which is correct at D1–D2 and nothing more |
| `review-pipeline.md` **E2** | The code in scope **and what it is audited against**. `code-reviewer` returns `Blocked` without an intended behaviour — so either name the spec, the rule file or the expected behaviour, or dispatch only `security-reviewer`, which is contractually callable alone |
| `qa-pipeline.md` **E4** | The behaviour to test and its source — a spec, a GDD passage, or the GD's own statement of what correct looks like. Plus the platform target and the performance budget if either is to be judged. `qa-lead` returns `Blocked` on a missing intent and states its assumption on a missing platform |
| `change-request.md` **E1** | The approved spec the change is against. With no approved spec there is no blast radius to classify — that input is an ordinary request for `feature-intake.md` |

**Classify the standalone run itself.** It does not inherit a tier from code somebody else wrote, and it does
not inherit one from a feature it is not part of. Classify per `task-classification.md`, state it at A3 and
above, and open a ledger only if the run will outlive one dispatch **and** there is a feature root to hold
one. With no feature root there is nowhere for a ledger to live — its counters go in
`<state-root>/project-state.md` instead.

## What comes back

A standalone run **returns to the GD**, never into the next pipeline. Concretely:

- `feature-intake.md` returns a Tech Spec and stops at **CP2**. It does not dispatch implementation.
- `review-pipeline.md` **E2** returns findings as a report. No author, no strike, no **CP3** — nobody is
  being charged for the code, and there may be nobody left who wrote it.
- `qa-pipeline.md` **E4** returns the coverage that ran, the evidence, `qa-lead`'s verdict and — at A3 and
  above — the assurance gate, with the review verdicts explicitly marked absent rather than assumed. **CP4**
  fires only if the GD is closing something; a standalone QA run on shipped code usually is not.
- `research-decision.md` **E5**/**E6** already end at their own GD gate, because a hard-to-reverse bet on a
  standalone path would otherwise pass unseen.

## Composing them by hand

The GD can chain any two by naming the second after the first returns — intake then development, development
then review, review then QA — and that is mode 2 twice, not mode 1. It costs what the two cost. **The
difference from a full run is that nothing is implied**: no checkpoint fires unless its pipeline runs, no
gate runs unless it is asked for per `optional-gates.md`, and every counter that would have travelled between
them has to be handed over, because no ledger is holding it.

If chaining by hand starts to need a ledger — a strike count carried, a checkpoint position remembered, a
tier reused — that is the signal the input was a feature all along. Open one at `feature-intake.md` step 2
rather than reconstructing state from the conversation.

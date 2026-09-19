# Template — `<feature-root>/LEDGER.md`

> Copy the fenced block below to `<feature-root>/LEDGER.md` at `feature-intake.md` step 2. This file is the
> template; it is never itself a ledger. The rules that govern the copy are in `../README.md`.

**Delete no row from the run state.** A row with nothing in it is a fact; an absent row is a question nobody
asked. The `## Decisions` half is the opposite — it starts empty and is appended to only when a decision is
actually made, per `.claude/standards/client/feature-documentation.md`.

**The two halves have two owners.** `## Run state` belongs to the orchestrator and is written at every
transition; no implementing agent edits it in a submission. `## Decisions` belongs to whoever made the
decision, and is appended in the same submission that produced it.

```markdown
# Ledger — <feature name>

## Decisions

Decisions a future reader would otherwise silently undo. Superseded in place, never deleted — the superseded
reasoning is what stops the next session re-litigating it. Not a changelog; git already has one.

| When | Decision | Why | What was rejected, and why | What it constrains |
|---|---|---|---|---|
| | | | | |

## Run state

Cross-run counters, written at each transition by `orchestrator.md`. Not documentation — a reader after the
feature's design history wants the half above.

- Slug: <feature-slug>
- Status: In flight | Closed | Abandoned <if Abandoned: why, and the last verified state>
- Tier: A<n>, from <the axis that set it> · axes D<n> C<n> U<n> R<n> X<n>
- Tier history: <A<n> from <axis>, <when and why it moved> → ... — appended, never overwritten. CP1 spending
  U down is the ordinary case; `assurance-evaluator` scores effort against the tier in force when it was
  spent, and a ledger showing only the final tier makes an A5 loop look like A3 overspending>
- Shape: <roles, and whether a Tech Spec is owed — set by D, per task-classification.md Step 4>
- Track: client | client + multiplayer
- Checkpoint: none | CP1 | CP2 | CP3 | CP4
- Verification floor: V<n>
- Attempt budget: <n>, from D<n>
- Advisor⇄Critic: round <n> of 3 · ruled out: <the options earlier rounds rejected> · <reset by a Major
  change on <date>, per change-request.md — the rounds settled a direction that no longer exists | never reset>
- Research: <branched to research-decision.md, and what it settled> | <skipped — covered by the package, API
  or existing system named at feature-intake.md step 5. "If you cannot name it, you are guessing" makes the
  name the whole evidence, and it travels to CP2>
- Research staleness: <the `Picture taken:` date of every Research Report this feature rests on, and what
  would make each stale — a later re-entry for the same capability re-checks rather than reuses>
- Standards set: <every `Standard set:` a `cto` decision produced, and whether its ADR was written. The
  standard binds roles outside this feature, so a blank row after a `cto` gate is a dropped project rule>
- Provisional decisions: <the decision, and the one measurement that would falsify it with its threshold —
  the number is what lets a later session re-open it instead of inheriting it as settled>
- Documents owed: <which feature-root documents this tier's floor and triggers have made owed>
- QA plan: <`qa-lead`'s coverage assignment — which agent-id covers what — and its exit criteria, verbatim,
  written at the step 1 transition. Both travel back into the step 4 sign-off dispatch: `qa-lead` is
  stateless, has no `If absent` row for either, and a sign-off without them re-derives the bar in silence>
- Baseline: <the performance figure, how it was taken, and by which report — written at the return that
  produced it, because a first measurement is exactly the run this row exists to stop becoming the baseline
  unnoticed>
- Reported: <the last period `producer` covered>
- Gates: review <offered? run | declined by the GD on <date> | not yet offered> · QA <same>
- Root-cause resets: 0/1 — shared across every loop that can reach `technical-architect`
- Measure-and-confirm: 0/1 — one `cto` decision's confirm cycle, per `research-decision.md` step 4
- Rejections: CP2 0/3 · CP3 0/2 · CP4-as-defect 0/2 · sign-off re-dispatch 0/2 · assurance FAIL 0/1
- Locks reclaimed: <who held it, when it was reclaimed, which of the three steps answered — or none>

| Submission | Author | Strikes / its bound | QA fails /2 | Attempts used | Verdicts landed |
|---|---|---|---|---|---|
| | | | | | |

**The strike bound is not the same for every row, which is why the header does not state one.** An ordinary
submission caps at **3**; a `qa-automation-engineer` suite at `review-pipeline.md` **E3** caps at **2**, a
different counter from the gated-direct 2, per `references/qa-test-code-gate.md`. Write both numbers in the
cell — `1 /3`, `1 /2` — because a header that states one bound is a header that lies on every other row, at
exactly the moment a counter is written under pressure.

### Accepted gaps

Written **before** closure, per invariant I6, and mirrored into this feature root's `DEBT.md` from A3 upward.

| Gap | Accepted by | When | Recorded in |
|---|---|---|---|
| _none_ | | | |

### Continuation debt

An agent that exhausted its attempt budget returns a Continuation Debt Record per `execution-loop.md`. It is
recorded here whole — the known non-solutions and the safe resume point are the two a future session cannot
reconstruct.

| Objective | Attempts / budget | Known non-solutions | Safe resume point |
|---|---|---|---|
| _none_ | | | |
```

A gated-direct submission caps at **2** strikes rather than 3 and holds no ledger of its own — it has no
feature root to hold one. Its counters live in `<state-root>/project-state.md` until it escalates. See
`references/gated-direct-lane.md`.

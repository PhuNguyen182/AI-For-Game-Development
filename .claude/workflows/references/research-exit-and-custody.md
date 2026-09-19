# The Exit — `research-decision.md` step 5

> **What the pipeline hands back, to which door, and what travels with it.** Promoted out of
> `research-decision.md` because its exit is three different things — a hand-back into a feature, a gate on a
> standalone run, and custody of what this pipeline produced — and one file was carrying all three at its cap.

## Which door it hands back to

Set by the entry it left from, never by the tier.

| Left from | Hands back at | Reaches |
|---|---|---|
| **E3**, **E4** | `feature-intake.md` **E2** — step 3 | CP1 |
| **E2**, where the architect escalated from **its step 2** — before the direction was locked | `feature-intake.md` **E2** — step 3 at **D4–D5 or U3**; its **E3** where that shape fires no loop | CP1, then CP2 |
| **E1**, and **E2** where the architect escalated from **its step 6** — mid-spec, CP1 already locked | `feature-intake.md` **E3** — step 6 at **D3–D5**, the direct-notes hand-off at **D1–D2** | CP2 at D3–D5; nothing at D1–D2 |
| **E2**, where **`feature-development.md`** escalated — `netcode-engineer` or either tech lead, mid-build | **`feature-development.md`**, resuming the step it left: step 3 for netcode, the escalating step for a lead | Nothing new — CP2 is behind it and the fan-out is already running |
| **E2**, where **`change-request.md`** escalated — `technical-architect` classifying a mid-flight change hit a strategic technology choice | **`change-request.md`**, to finish classifying whatever severity the rest of the request still needs, now informed by the decision | Whichever checkpoint that severity reopens — CP2 at Moderate, CP1 at Major |
| **E5**, **E6** | The GD — the standalone acceptance gate below | Nothing; there is no feature to resume |

**E2 is one door with four origins**, and they are not interchangeable. `technical-architect` can reach
`cto` while classifying at step 2 or while writing the spec at step 6; sending a step-2 escalation back at
step 6 skips the Advisor⇄Critic loop **and CP1** on a feature whose shape made both mandatory.
`feature-intake.md`'s routing table splits the same row the same way.

**The third origin is `feature-development.md`, and it is the one this table did not have.** Its entry row
names the architect because that was E2's first caller, but `netcode-engineer` escalating an unset netcode
foundation and either tech lead escalating a technology choice arrive at the same door — mid-build, with CP2
long approved. Handing either back into `feature-intake.md` reopens a Tech Spec the fan-out is already
building against, which is the same defect as the step-2/step-6 confusion above, one pipeline further on.

**The fourth origin is `change-request.md`.** A mid-flight change can bundle a severity-ratable part with a
strategic technology choice, and the technology part alone routes here — the ratable part is still waiting to
be finished. Sending the return to `feature-intake.md` instead would either open a Tech Spec round for a
feature already past CP2, or reopen a checkpoint before the severity that reopens it has even been decided.

**E1 and E4 can both be literally true of one branch** — `feature-intake.md` step 5 named a capability the
project lacks *and* classification returned U3 on a technology unknown. They exit to opposite doors, so the
discriminator is stated rather than guessed:

| | Entered from | Which means |
|---|---|---|
| **E1** | `feature-intake.md` **step 5** | The shape's Advisor⇄Critic loop has already run, or that shape never fires one. The direction is settled; only the technology was open |
| **E4** | `feature-intake.md` **step 2** | Classification, *before* the loop. The direction is not settled yet |

Handing an **E4** back at step 6 skips the loop the feature was classified into. Handing an **E1** back at
step 3 re-runs a loop that already closed.

**The second row branches on shape, and one direction of getting it wrong is expensive.**
`feature-intake.md` lets **D1–D2** take its step 5 as well — a one-role change can still need a package the
project does not have — and that feature has no step 6 to return to and no CP2 to reach. Its return is the
direct notes, exactly as if this pipeline had never run. Handing it back at step 6 instead produces a Tech
Spec for a D1–D2 change, which is `effort-allocation.md`'s own named example of what the artifact budget
forbids. That pipeline's diagram already branches here, at its `Resume` node.

## What travels with the hand-back

This pipeline produces five things. Naming only the Research Report loses four of them, and each has a
different consumer.

| Produced | Travels to | If it does not |
|---|---|---|
| **Research Report** | The receiving step, whole | The decision downstream rests on a summary of a summary |
| **Technical Decision** | The same — on an Escalate lane it is the *result*, and the report is merely its input | The pipeline's own deliverable is dropped at the door it came out of |
| **`Standard set:`** | The ledger's `Standards set:` row, and an ADR per step 4 | A project-wide rule survives only in the run that produced it |
| **`Picture taken:`, and what makes it stale** | The ledger's `Research staleness:` row, and into the Tech Spec | A later re-entry reuses a stale sweep instead of re-checking it |
| **A provisional decision's re-open threshold** | The ledger's `Provisional decisions:` row | The one number that would falsify the decision is lost, so nobody ever re-opens it |

The last three are written **at the transition**, per invariant **I4** — not when the feature closes. A
standalone run has no feature ledger; they go to `<state-root>/project-state.md` instead, per
`references/standalone-runs.md`.

## Research that expands the scope

`references/entry-index.md`: *"Only U is re-read on an ordinary re-entry. D, C, R and X do not move because
the work itself did not change."* A research result can falsify that. A decision that makes encrypted
transport a precondition, or that rules out the approach the classification assumed, **has** changed the
work — the project learned something.

**It is not an ordinary re-entry, and it is not a change request either.** `change-request.md` exists for the
GD changing a rule, and nobody changed a rule here. So:

- The hand-back **names the axis it moved, and why**, in the return itself.
- `technical-architect` re-reads that axis at the receiving step and appends the new tier to the ledger's
  `Tier history:` — the same append CP1's reclassification uses.
- Where the move is large enough that the approved direction no longer holds, it surfaces at **CP2** as a
  direction problem, which `feature-intake.md` already routes to **CP1** at its **E5**.

Never silently carry forward a tier the research invalidated.

## The standalone acceptance gate

**E5** and **E6** return to the GD. **Returning the result is not the gate** — the GD asked the question and
this is the answer. The gate is narrower, and fires only on what outlives the run:

| Fires when the run produced | Because |
|---|---|
| A **`Standard set:`** | It binds roles that were never part of this run |
| A **provisional decision** and its re-open threshold | Somebody has to honour that threshold later |
| A **paid, licensed or otherwise committing** choice | R2 or worse, on a path with no CP2 behind it |

**A Direct lane produces none of the three.** It never reaches `cto`, so there is no standard, no commitment
and nothing to re-open — the result is returned and the run stops. Gating it would put a checkpoint on a lane
that cannot produce the thing the checkpoint exists to catch, which is `effort-allocation.md`'s artifact
budget spent on ceremony.

**Rejecting means** — and the two rejections are not the same thing:

| The GD rejects | What happens |
|---|---|
| **The standard** | It is not recorded and no ADR is dispatched; `cto`'s decision still stands for this run. Record the refusal, so a later run does not re-derive a rule already refused |
| **The decision itself** | **Once** back to step 4, carrying what they objected to — bounded in `references/loop-termination.md`. Past that the call is the GD's to make directly: a second refusal means `cto` cannot reach an answer they will accept, and a third dispatch buys the same one again |

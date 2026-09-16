# Workflow State

> **The cross-run state no agent can hold.** Every agent in this project is isolated and stateless — it
> cannot count its own retries, cannot see another agent's return, and cannot remember the last run. Written
> **at each transition**, not at the end of a run: a counter that survives only in conversation context is
> not a safety mechanism. Owned by `orchestrator.md`.

## Layout

```text
.claude/workflows/state/
  README.md            ← this file: the layout, and the per-feature ledger template
  project-state.md     ← what cannot be per-feature: the in-flight index and both global locks
  <feature-slug>/
    ledger.md          ← one feature's own cross-run state
```

**One ledger per feature, never one shared file.** A shared ledger forced every concurrent feature through
one document, so a second feature's block was appended under the first and the counters that matter — strikes
against *this* submission, the round *this* Advisor loop has reached — sat next to identically-named counters
belonging to something else. A feature's state now lives at one path, opens when classification
assigns its tier, and is marked closed when CP4 closes it.

**What is not per-feature stays in `project-state.md`.** The Editor lock (invariant I3) and the device lock
(I7) are project-wide by definition — a per-feature copy of a global lock is not a lock. Open review debt
lives there too, because a mode-3 dispatch that writes source may have no feature to attach to.

## Two files named for a ledger, and they are unrelated

| Path | Holds | Read by |
|---|---|---|
| `.claude/workflows/state/<feature-slug>/ledger.md` | **Run state** — tiers, checkpoint position, strike counts, attempts used. Lowercase, under `.claude/` | `orchestrator.md`, at every transition |
| `<feature-root>/LEDGER.md` | **Decision history** — what was decided, why, what was rejected. Uppercase, beside the feature's code | An agent about to undo a design that looks wrong, per `feature-context-reading.md` |

Lowercase and under `.claude/` is state; uppercase and beside the code is documentation. Reading one for the
other wastes a dispatch, which is why the distinction is stated in both files.

## Lifecycle

| When | Do |
|---|---|
| `technical-architect` returns a classification | Create `<feature-slug>/ledger.md` from the template below, with the tier and the axes filled in |
| Any transition — a checkpoint, a dispatch, a verdict, a strike, an attempt | Write it, then dispatch. Never the other way round |
| CP4 approved, or the GD accepts the work with a gate declined | Move the accepted gaps — **a declined gate is one** — into the feature root's `DEBT.md` first, then mark the ledger `Closed` and leave it in place |
| The GD drops the feature, or it is superseded | Mark it `Abandoned`, record why and the last verified state, and leave it in place. A feature with no terminal state is one a later session cannot tell from one still in flight |
| A lock is reclaimed from a stale holder | Record who held it, when, and which check answered — per `project-state.md`'s reclaim procedure |

The slug is the feature's name in kebab-case — the same one used for its feature root where one exists.
Never invent a second slug for a feature that already has a ledger.

## Per-feature ledger template

Copy this into `<feature-slug>/ledger.md`. Delete no row: a row with nothing in it is a fact, and an absent
row is a question nobody asked.

```markdown
# Ledger — <feature name>

- Slug: <feature-slug>
- Status: In flight | Closed | Abandoned <if Abandoned: why, and the last verified state>
- Tier: A<n>, from <the axis that set it> · axes D<n> C<n> U<n> R<n> X<n>
- Shape: <roles, and whether a Tech Spec is owed — set by D, per task-classification.md Step 4>
- Track: client | client + multiplayer
- Checkpoint: none | CP1 | CP2 | CP3 | CP4
- Verification floor: V<n>
- Attempt budget: <n>, from D<n>
- Advisor⇄Critic: round <n> of 3 · ruled out: <the options earlier rounds rejected>
- Documents owed: <which feature-root documents this tier's floor and triggers have made owed>
- Baseline: <the performance figure, and how it was taken>
- Reported: <the last period `producer` covered>
- Gates: review <offered? run | declined by the GD on <date> | not yet offered> · QA <same>
- Root-cause resets: 0/1 — shared across every loop that can reach `technical-architect`
- Rejections: CP2 0/3 · CP3 0/2 · CP4-as-defect 0/2 · sign-off re-dispatch 0/2 · assurance FAIL 0/1

| Submission | Author | Strikes /3 | QA fails /2 | Attempts used | Verdicts landed |
|---|---|---|---|---|---|
| | | | | | |

A gated-direct submission caps at **2** strikes rather than 3 and holds no ledger of its own — its counters
live in `project-state.md` until it escalates. See `references/gated-direct-lane.md`.

## Accepted gaps

Written **before** closure, per invariant I6, and mirrored into the feature root's `DEBT.md` from A3 upward.

| Gap | Accepted by | When | Recorded in |
|---|---|---|---|
| _none_ | | | |

## Continuation debt

An agent that exhausted its attempt budget returns a Continuation Debt Record per `execution-loop.md`. It is
recorded here whole — the known non-solutions and the safe resume point are the two a future session cannot
reconstruct.

| Objective | Attempts / budget | Known non-solutions | Safe resume point |
|---|---|---|---|
| _none_ | | | |
```

## What each row protects

Moved here from `orchestrator.md` — one fact, one home, beside the template it describes. Every row exists
because something specific breaks without it.

| State, per feature | Protects against |
|---|---|
| Tier · **the five axes** · track | An agent assuming client-only, or planning at a depth nobody set |
| **Verification floor · attempt budget** | A claim of "verified" meaning whatever its author took it to mean; an agent with no ceiling on its own retries |
| Checkpoint position | Not knowing which CP `change-request.md` reopens |
| Submission id · strikes · QA-fails · **attempts used** | Three strikes; the two-round QA bound; `assurance-evaluator` scoring an iterated submission as a first pass |
| **Root-cause resets · every rejection counter** | A second three-strike run read as a first, and the eight composed loops `references/loop-termination.md` bounds — each one individually capped before, jointly unbounded |
| **Gates — offered, run or declined** | A feature that closed without a gate being indistinguishable from one that passed it |
| Advisor⇄Critic round · options ruled out | The 3-round cap; `advisor` re-proposing what was already rejected |
| Verdicts landed | Acting on one verdict and paying two round trips for one submission |
| Performance baseline | A run silently becoming the baseline |
| **Accepted gaps · continuation debt** | Invariant I6; and a future session re-running an approach already recorded as a known non-solution |
| Reporting period | `producer` duplicating or missing status |

## Closing a ledger feeds `calibration.md`

Every constant in this layer — 3 strikes, 3 Advisor⇄Critic rounds, the 2-round QA bound, the 2–5 attempt
budget — was **chosen, not measured**. They are E0 on `effort-allocation.md`'s own evidence scale, which is
the weakest claim that file recognises, and it is the one place this layer does not meet the standard it sets
for everything else.

`calibration.md` is how that gets paid off without inventing telemetry: when a ledger is marked `Closed` or
`Abandoned`, copy what the run actually spent into it — one row, from numbers already in the ledger. Nothing
is estimated and nothing is reconstructed. After enough real features the rows say whether a constant is
right, and until then they say honestly that nobody knows.

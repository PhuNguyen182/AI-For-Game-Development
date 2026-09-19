# Workflow State

> **The cross-run state no agent can hold.** Every agent in this project is isolated and stateless — it
> cannot count its own retries, cannot see another agent's return, and cannot remember the last run. Written
> **at each transition**, not at the end of a run: a counter that survives only in conversation context is
> not a safety mechanism. Owned by `orchestrator.md`.

## Nothing under `.claude/` is written at runtime

`.claude/` is the **framework**, copied unchanged into every project that adopts it. State is the
**project's**, and it belongs beside the project's own work. A run that creates a directory or writes a
counter under `.claude/` puts one project's history inside the template every other project starts from, and
the next project inherits a stranger's strike counts.

So this folder holds the state layer's **rules and its templates**. It holds no state. A file appearing under
it during a run is a defect, and `tools/verify-workflow-layer.ps1` fails on it.

## Where state actually lives

| State | Path | Written by |
|---|---|---|
| One feature's run state | `<feature-root>/LEDGER.md`, its **`## Run state`** half | `orchestrator.md`, at every transition |
| The in-flight index, both global locks, gate debt belonging to no feature | `<state-root>/project-state.md` | `orchestrator.md`, at every transition |
| One row per closed feature, measuring this layer's own constants | `<state-root>/calibration.md` | whoever marks a ledger closed |

**`<state-root>` is `.workflow/` at the project root**, unless that project's own `CLAUDE.md` names a
different path. Commit it: the in-flight index and the calibration rows are history worth keeping. The two
locks are its only machine-local rows, and a lock left behind by a run on another machine is exactly what the
reclaim procedure below exists for.

Templates for all three are in `templates/`. Copy them; never point a live record back into `.claude/`.

## One ledger per feature — and now literally one file

**A feature's ledger is `LEDGER.md` at its own feature root**, the same file
`.claude/rules/feature-context-reading.md` already sends a reader to. It carries two halves, and they are not
the same kind of thing:

| Half | Holds | Read when |
|---|---|---|
| `## Decisions` | **Decision history** — what was decided, why, what was rejected, what it constrains | A design looks wrong and you are about to undo it |
| `## Run state` | **Run state** — tier and axes, checkpoint position, strike counts, attempts used, accepted gaps, continuation debt | Every transition, by the orchestrator |

There used to be two files — `LEDGER.md` beside the code and a lowercase `ledger.md` under `.claude/` — and
the rule separating them was that one was uppercase. That is not a distinction a reader can act on, it cost a
wasted dispatch every time somebody opened the wrong one, and the lowercase half was state written into the
framework. One file, two headings, and the confusion has nothing left to attach to.

**A single shared ledger file is still forbidden.** One document holding every concurrent feature put one
feature's strike count beside an identically-named counter belonging to another.

## Opening one

`feature-intake.md` step 2 opens the ledger, from `templates/feature-ledger.md`, before step 3 dispatches
anything — the tier, the axes and the round count all have to survive a run, and step 2 is the first moment
any of them exists.

**The feature root comes from the architect's classification return**, which names the intended root
alongside the tier. For a change to an existing feature that root already holds code; for a new one, the
directory is created and `LEDGER.md` is its first file. Check `<state-root>/project-state.md` first: a
feature already in flight has a ledger, and a second slug splits its counters silently.

**When CP1 moves the root**, the ledger moves with the feature and the move is recorded as a superseded entry
in its `## Decisions` half. A provisional root is normal at U3; a second ledger is not.

**Work with no feature root has no ledger** — a gated-direct submission, a mode-3 direct dispatch, a
standalone gate run. Its counters live in `<state-root>/project-state.md` until it escalates, per
`references/gated-direct-lane.md`.

## Lifecycle

| When | Do |
|---|---|
| `technical-architect` returns a classification | Create `<feature-root>/LEDGER.md` from the template, tier and axes filled in, and add its row to `<state-root>/project-state.md` |
| Any transition — a checkpoint, a dispatch, a verdict, a strike, an attempt | Write it, then dispatch. Never the other way round |
| CP4 approved, or the GD accepts the work with a gate declined | Move the accepted gaps — **a declined gate is one** — into the feature root's `DEBT.md` first, then mark the run state `Closed` and leave it in place |
| The GD drops the feature, or it is superseded | Mark it `Abandoned`, record why and the last verified state, and leave it in place. A feature with no terminal state is one a later session cannot tell from one still in flight |
| A ledger is marked `Closed` or `Abandoned` | Copy its numbers into `<state-root>/calibration.md`, then clear its row from the in-flight index |
| A lock is reclaimed from a stale holder | Record who held it, when, and which check answered — per the procedure below |

The slug is the feature's name in kebab-case, the same one its feature root uses. Never invent a second slug
for a feature that already has a ledger.

## Reclaiming a stale lock — invariant I9

Both global locks live in `<state-root>/project-state.md`: the Editor lock (**I3**) and the device lock
(**I7**). A run can die holding either — a session ends mid-dispatch, an agent times out, the Editor crashes.
**An invariant with no recovery path stops being one the first time that happens**, so a held lock is never
permanent and is never cleared by guessing either.

`Claim expires` is written at claim time — the dispatch's expected duration, generously rounded. Past it the
lock is *suspect*, not free. Reclaim in this order, stopping at the first step that answers:

1. **Is the holder still running?** A dispatch in flight in this session holds its lock whatever the clock
   says. Never reclaim from a live holder.
2. **Does the resource itself say?** For the Editor, `unity status` per `unity-tooling-preference.md`; for a
   device, `adb devices`. A resource that is idle and answering is not being driven by anyone.
3. **Ask the GD**, naming the holder, the claim time, and what is waiting. A concurrent session on another
   machine is invisible from here, and only they can see both.

Then write the reclaim as its own row in the feature's ledger — **who held it, when it was reclaimed, and
which of the three steps answered**. A lock silently taken back is the same class of failure as a counter
that lived only in context.

**Whatever the stale holder produced is unverified.** A dispatch that never returned may have half-applied an
Editor mutation or left a device mid-case. Inspect the real state before the next claim, per
`execution-loop.md`'s safe-retry rule: no success response never means no side effect.

## What each row protects

Every row of the run state exists because something specific breaks without it.

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

`<state-root>/calibration.md` is how that gets paid off without inventing telemetry: when a ledger is marked
`Closed` or `Abandoned`, copy what the run actually spent into it — one row, from numbers already in the
ledger. Nothing is estimated and nothing is reconstructed. After enough real features the rows say whether a
constant is right, and until then they say honestly that nobody knows.

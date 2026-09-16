# Project State

> **What cannot be held per feature.** Per-feature run state lives in `<feature-slug>/ledger.md`; this file
> holds the two global locks, the debt that may belong to no feature, and the index of what is in flight.
> Written at each transition, per `state/README.md`.

## In flight

One row per feature with an open ledger. The index exists so a new run can find an existing feature's ledger
instead of opening a second one under a different slug. A feature leaves this table when its ledger is marked
`Closed` or `Abandoned` — the ledger itself stays on disk either way.

| Feature | Slug | Tier | Checkpoint | Ledger |
|---|---|---|---|---|
| _none_ | | | | |

## Open gate debt

Source that no gate has seen — invariant **I2**. Two things land here and they are not the same:

- **Unoffered debt** — source written outside any pipeline, typically a mode-3 dispatch. The gate offer is
  still owed.
- **Declined debt** — the offer was made per `references/optional-gates.md` and the GD said no. The decision
  is recorded, with who made it, because a feature that closed without a gate must never be indistinguishable
  from one that passed it.

**Recorded, never enforced**: it blocks no dispatch and settles in batch whenever the GD opts in. Clear a row
only when the gate has actually returned on it — marking one settled because the code looks fine is the
fabricated verification `effort-allocation.md` puts beyond any waiver.

| Path | Written by | When | Gate owed | State | Feature, if any | Settled |
|---|---|---|---|---|---|---|
| _none_ | | | review \| QA \| both | unoffered \| declined | | |

## Editor lock

One Unity Editor, project-wide (invariant **I3**); 10 agents hold `mcp__<server>__*` tools against it. Claim
before dispatching one, release on its return.

| Held by | Feature | Since | Claim expires |
|---|---|---|---|
| _free_ | | | |

## Device lock

One physical device, project-wide (invariant **I7**). `build-verification-tester` walking cases over adb and
`performance-qa-engineer` profiling a Development Build over adb are the same wire. Claim before dispatching
either against a device, release on its return. Independent of the Editor lock — an agent can hold both.

| Held by | Feature | Device | Since | Claim expires |
|---|---|---|---|---|
| _free_ | | | | |

## Reclaiming a stale lock — invariant I9

A run can die holding a lock: a session ends mid-dispatch, an agent times out, the Editor crashes. **An
invariant with no recovery path stops being one the first time that happens**, so a held lock is never
permanent and is never cleared by guessing either.

`Claim expires` is written at claim time — the dispatch's expected duration, generously rounded. Past it, the
lock is *suspect*, not free. Reclaim in this order, and stop at the first step that answers:

1. **Is the holder still running?** A dispatch in flight in this session holds its lock, whatever the clock
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

# Template — `<state-root>/project-state.md`

> Copy the fenced block below to `<state-root>/project-state.md` — `.workflow/project-state.md` at the
> project root, unless that project's `CLAUDE.md` names another path. This file is the template; it is never
> itself the record. The rules that govern the copy, including the lock-reclaim procedure, are in
> `../README.md`.

**What cannot be held per feature, and only that.** Per-feature run state lives in `<feature-root>/LEDGER.md`
under `## Run state`. This file holds the two global locks, the debt that may belong to no feature, and the
index of what is in flight. Written at each transition, like everything else in this layer.

```markdown
# Project State

## In flight

One row per feature with an open ledger. The index exists so a new run finds an existing feature's ledger
instead of opening a second one under a different slug. A feature leaves this table when its ledger is marked
`Closed` or `Abandoned` — the ledger itself stays at its feature root either way.

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

## Gated-direct counters

A gated-direct submission has no feature root, so it has no ledger. Its strike count caps at **2** and lives
here until the work escalates to `feature-intake.md` **E1**, which opens a real ledger.

| Submission | Author | Strikes /2 | Verdicts landed |
|---|---|---|---|
| _none_ | | | |

## Editor lock

One Unity Editor, project-wide (invariant **I3**); 10 agents hold `mcp__<server>__*` tools against it. Claim
before dispatching one, release on its return. Past `Claim expires` the lock is suspect, not free — reclaim
only by the three-step procedure in the framework's `workflows/state/README.md`, and record the reclaim.

| Held by | Feature | Since | Claim expires |
|---|---|---|---|
| _free_ | | | |

## Device lock

One physical device, project-wide (invariant **I7**). `build-verification-tester` walking cases over adb and
`performance-qa-engineer` profiling a Development Build over adb are the same wire. Claim before dispatching
either against a device, release on its return. Independent of the Editor lock — an agent can hold both. Same
reclaim procedure.

| Held by | Feature | Device | Since | Claim expires |
|---|---|---|---|---|
| _free_ | | | | |
```

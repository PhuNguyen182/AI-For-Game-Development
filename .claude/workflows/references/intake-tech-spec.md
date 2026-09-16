# The Tech Spec — `feature-intake.md` step 6

> **What `technical-architect` returns, and what the spec must state that nothing downstream can derive.**
> Split out of `feature-intake.md` under the promotion rule in `client/feature-documentation.md`: it runs at
> **D3–D5** only, and D1–D2 hands over direct notes without ever reaching this step.

The architect returns the tier and its axes, module boundaries, the client-server contract, an architecture
diagram, the patterns chosen, a per-`agent-id` task breakdown, and **which feature-root documents are owed** —
`feature-documentation.md` floors the full docset at **A4** and `LEDGER.md`/`DEBT.md`/`NOTES.md` at **A3**,
each still gated on its own trigger. One whose trigger has not fired is never requested.

**The spec also states the acceptance criteria and the verification floor** — V2/V3/V4 at A3/A4/A5, per
`effort-allocation.md`. Without it QA has a coverage plan and no standard of evidence to plan against, and
every downstream claim of "verified" means whatever its author took it to mean.

## What a spec that skips these costs

Each omission has a named downstream failure, which is why they are listed rather than implied:

| Omitted | What happens |
|---|---|
| **Module boundaries** and the **client-server contract** | `unity-engineer` and `ui-ux-programmer` are each forbidden to implement a game rule, and neither can respect a boundary it was never shown |
| The **per-`agent-id` task breakdown** | Four implementing agents return `Blocked` — a spec is not a brief, and the pipeline cannot split one it was not given |
| The **acceptance criteria** | `assurance-evaluator` returns `Blocked`: completion scored against a requirement list assembled after the fact is hindsight, not measurement |
| The **verification floor** | `qa-lead` plans at a depth it chose itself and reports it as the depth that was owed |
| **Which feature-root documents are owed** | They are reconstructed at the end, which `feature-documentation.md` says is exactly what `LEDGER.md` and `DEBT.md` must never be |

## CP2 rejections are bounded at three

A third spec the GD will not approve is a **direction** problem, not a drafting one — at that point it goes
to **CP1** where the loop is available, or to the GD with all three rejections and what changed between them.
`references/loop-termination.md` owns that bound, along with every other one in the layer.

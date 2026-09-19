# The Gated-Direct Lane — `orchestrator.md` step 0

> **Read when an input trips a consequence criterion but nothing else.** The lane that lets **C** buy
> verification without buying process — three calls, both review gates, no pipeline and no checkpoint.

## The contradiction this lane closes

`task-classification.md` Step 4 is explicit: **C, R and X buy depth — the verification floor, the evidence
strength, the care taken per attempt — and never a checkpoint, a document, or an extra agent.** D buys shape.

Step 0's escalation criteria did not hold that line. Three of the five are consequence criteria, and
routing on any one sent the input into `feature-intake.md` — which is `technical-architect`, a fan-out, both gates, `qa-lead`,
`producer` and a mandatory **CP4**. A one-constant change to a `Game.Core.*` cooldown is D1: no Tech Spec, no
CP1, no CP2, no CP3 — and still six or more calls, because consequence had quietly bought the whole pipeline.

That is C buying process, in the one file most insistent that it must not. This lane is the missing rung:
consequence buys **the gates**, which is evidence, and nothing else.

## When it applies — all four, or it is not this lane

| Condition | Why it is load-bearing |
|---|---|
| **Exactly one role** owns the change | Two roles is **D3+**, and coordination is what the fan-out and the handoff matrix exist for. Nothing here supplies either |
| **No public contract, interface or module boundary moves** | A contract is what four downstream agents build against. A moving one needs a spec somebody approved, not a gate somebody passed |
| **The intended behaviour is already stated** — an approved spec, a GDD passage, or a request unambiguous on its face | `code-reviewer` returns `Blocked` without an intended behaviour. If nothing states it, there is nothing to review against and the input belongs in `feature-intake.md` |
| It trips a criterion for **consequence only** — `Game.Core.*`, multiplayer-relevant, **or a consequence path** (a credential or signing config, IAP or billing, a store submission, PII, save-data migration, published git history, a released build, a shipped performance budget) | If it also trips **D3+** or **U3**, the pipeline is not overhead: it is the coordination or the direction the input actually needs. **The third clause was missing** while this file's own worked example below is a signing-config edit — so the lane refused the input it was written for, and `orchestrator.md` step 0 sent it to the chore row instead |

Fail any one and this lane is not available. **Ambiguous starts higher** — the same rule the agents apply to
themselves — so an input that only *probably* qualifies goes to `feature-intake.md` **E1**.

## What runs

```text
the one owning agent  →  code-reviewer + security-reviewer, in parallel  →  the GD
```

Three calls. The submission enters `review-pipeline.md` at **E3**, carrying an author and a strike count but
no CP3 — there is no Tech Spec to compile an Implementation Summary against, and no feature to aggregate.

What it still owes, unchanged, because none of it is process:

- The **verification floor** its A-tier sets. A signing-config edit on this lane is A5 and owes V4 evidence.
- The **attempt budget** from D — 2 at D1–D2 — inside the one dispatch.
- An **Implementation Note**, per `implementation-note.md`. `code-reviewer` blocks without one.
- The `.claude/standards/client/*` rules in full. The lane changes who checks, never what is checked.

What it does **not** produce, per `effort-allocation.md`'s artifact budget: no Tech Spec, no plan document,
no acceptance contract, no coverage plan, no Status Report, no self-score, and no checkpoint.

## The strike bound — two, then escape upward

`review-pipeline.md`'s three strikes assumes a feature ledger, an architect who wrote the spec, and a
root-cause path back into it. This lane has none of those, so it stops sooner:

| Strike | What runs |
|---|---|
| **1** | Back to the author with both finding sets, exactly as **E3** in `feature-development.md` |
| **2** | **Stop. Escalate to `feature-intake.md` E1.** Two gate rejections on work this small is evidence the input was mis-sized, not evidence the author needs a third try |

The escalation carries both rejection sets and the code, so classification starts from what was learned
rather than from the original request. It is the same escape the router already owes on any other criterion
turning out to apply — little was built, so little is lost.

**Counters live in `<state-root>/project-state.md`, not in a feature ledger.** This lane has no feature
root,
so it has nowhere to put one; and a lane that caps at two strikes and holds no checkpoint position has
nothing worth a ledger anyway. If the work escalates to **E1**, `feature-intake.md` step 2 opens the ledger then, and
the two strikes travel into it.

## Escape upward, at any point

The moment any of the four conditions turns out to be false — a contract has to move, a second role is
needed, the behaviour was never actually stated, or `code-reviewer` returns `Needs-decision` because the spec
is ambiguous about what "correct" means — stop and enter `feature-intake.md` **E1**.

Review debt is recorded either way, per invariant **I2**. Nothing is lost by starting here and escaping; the
whole point of a cheap default is that being wrong about it costs one call.

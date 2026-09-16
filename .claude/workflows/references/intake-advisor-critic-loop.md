# The Advisor⇄Critic Loop — `feature-intake.md` steps 3–4

> **The design loop, its trigger, and its 3-round cap.** Split out of `feature-intake.md` under the
> promotion rule in `client/feature-documentation.md`: it runs only at **D4–D5, or U3 at any D**, so most
> features never reach it and no reader needs it to follow the rest of that pipeline.

CP1 sits at the end of this loop and belongs to `feature-intake.md`, which also owns what rejecting it means.

## When it runs

**The direction must be genuinely open — D4–D5, or U3 at any D.** D restates the old trigger:
architecture-level work is where several credible directions exist. U3 is the addition and the more honest of
the two — a consequential unknown the GDD has not decided is *precisely* what a design loop settles, however
trivial the implementation. Nothing else reaches here: a C4 credential edit classifies A5 and gets no round,
because consequence buys verification, not deliberation.

The loop is **GD-in-the-middle**, not agent-to-agent. One round is:

```
advisor → Options → GD picks a direction → critic → Risk Findings → GD decides
```

`advisor` never recommends and `critic` only attacks a direction the GD already leans toward, so the two can
never run in the same round — one exists because no direction exists yet, the other requires one.

| Loop rule | Detail |
|---|---|
| **Who ends it** | The GD, by locking a direction. Neither agent can end it; both explicitly disclaim owning the round count. |
| **Hard cap** | **3 rounds.** Reaching round 3 without a lock stops the pipeline and reports non-convergence to the GD — it is not a failure to retry past. |
| **Rejected options** | The pipeline carries the list of options earlier rounds already ruled out into the next `advisor` call. `advisor` cannot remember them. |
| **A clean critic** | `critic` returning `Done` with an empty findings list is a **pass**, not a missing result. Proceed to CP1. |
| **Escalation** | `critic` is a leaf — it reports to the GD and routes to nobody, at every level. |
| **The cap is not the budget** | 3 rounds here is a pipeline counter and is unrelated to `execution-loop.md`'s attempt budget, which bounds one agent's own corrective cycles inside one dispatch. Both are counted, in the same ledger, and neither is spent because it was available. |

# Checkpoint 3 — the detail

> **What `technical-architect` compiles, which shapes it fires for, and where a rejection goes.** Split out of
> `review-pipeline.md` under the promotion rule in `client/feature-documentation.md`. **`review-pipeline.md`
> still owns CP3** — this is its detail, and the pointer there is the entry to it.

CP3 exists only when this pipeline ran. It is the gate on **what was built against an approved spec**, and
with review declined per `references/optional-gates.md` there is no verdict set to compile a summary from —
the feature reaches the GD through `producer` instead, or through the Implementation Note alone.

## When it fires

Fires **once per feature**, when every submission for it is clear — not once per submission. A feature
produces several: the Shared Core, each client agent, each backend agent, and the README. Only the checkpoint
aggregates.

| Shape | CP3 |
|---|---|
| **D1–D2** | none — `feature-intake.md`'s checkpoint table merges it into CP4 |
| **D3–D5** | ✔ |

**CP3 keys to D, and the A-tier never adds one.** An A5 submission that is D1 still has no CP3; what its tier
bought was V4 evidence at the gates, which has already been spent by the time the summary is written. This is
`task-classification.md` Step 4 again: D sets the shape, C/R/X set the depth.

## What is compiled

`technical-architect` returns its usual envelope with the body replaced by three fields:

| Field | What makes it correct |
|---|---|
| `Built:` | What now exists, in the terms the spec used — not a restatement of the diff |
| `Matches spec intent:` | With **any drift named**. Drift the architect does not name is drift the GD approves without seeing |
| `Known limitations:` | **Not a closing remark.** From **A3** upward each entry is owed in the feature root's `DEBT.md`, appended in the submission that produced it rather than reconstructed here, per `feature-documentation.md` |

Its input is every cleared submission's Implementation Note plus both verdicts for each. Absent either, it
is compiling a summary of work it cannot see.

## Rejecting it

**A CP3 rejection sends the named drift back to its owning agent at `feature-development.md` E3 — not back to
CP2.** The distinction is the whole point of having two checkpoints: CP2 is the rollback target for a *spec*
change, and a CP3 rejection says the code drifted from a spec that still stands. Sending it to CP2 would
re-open a decision the GD already made correctly.

If the GD's objection is instead that the spec itself is now wrong, that is not a CP3 rejection at all — it is
`change-request.md`, which classifies the blast radius and decides which checkpoint reopens.

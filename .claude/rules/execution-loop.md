# Shared — Execution Loop, Budget & Memory

Applies to: every agent and the orchestrator, on every input. Guards against two equally costly failures:
stopping at an inadequate first result because something usable exists, and looping the same approach with
cosmetic variation. The fix is bounded, evidence-driven iteration.

## Attempt cycle and budget

An attempt = execute or revise → evaluate against the acceptance criteria → find the highest-impact gaps →
improve → re-verify. The first execution is **Attempt 1**; micro-edits before the next evaluation belong to the
same attempt. The budget comes from **D** (`task-classification.md` Step 4) and is a ceiling, never a target —
stop the moment the criteria and `effort-allocation.md`'s gates pass. Criticality never raises the budget; it
buys stricter checks per attempt.

This budget lives inside one dispatch. An agent that exhausts it returns rather than loops, and that return is
one strike at the pipeline level (`workflows/references/bounds.md`). The one value crossing the boundary is
**attempts used**, stated on return with — past the first — what the last attempt materially improved.

## Each attempt after a miss

Evaluate against the criteria, find each material gap's likely cause, and change plan, method, implementation
or evidence where that cause requires it. **Apply every known cheap, high-confidence fix now** — never hold one
back for a later attempt. State what improved over the previous attempt.

Change strategy, not wording, when two attempts failed for substantially the same cause or a retry showed no
measurable gain. Re-plan entirely when two substantive steps make no progress or a disproven assumption
invalidates the plan.

## Safe retry for state-changing work

For **R2/R3 or X2/X3**, answer before retrying: did the previous attempt partially succeed, what is the actual
current state, would repeating duplicate the action, is it idempotent, are the target and parameters still
correct, is rollback available? **No success response never means no side effect** — a failed `git push` may
have landed, an Editor mutation may have half-applied, a device operation may have completed before the
connection dropped. Inspect real state first. A failed state-changing attempt still spends the budget.

## Stop rule

Stop on meeting the acceptance criteria. Otherwise iterate while budget remains and another attempt is safe
and worth it. Stop early when another attempt would be unsafe, irreversibly destructive, blocked on an
unavailable dependency, or likely to repeat the same failure — and report `Blocked`, `Partially complete` or
`Failed`, never done.

## Continuation Debt Record

On an exhausted budget or an early stop, record: `Status`, `Objective`, `Attempts used / budget`,
`Unmet requirements`, `Best achieved result`, `Last verified state`, `Likely root cause`,
`What changed across attempts`, `Residual issues and severity`, `Known non-solutions` (methods tried and why
they failed), `Next best action`, `Required input or dependency`, `Safe resume point`.

An agent puts it in its Implementation Note; the pipeline that receives it records it in the feature's
`LEDGER.md` **Continuation debt** table; directly-handled work states it in the reply to the GD as unfinished
work, never folded into a summary. Read that table before starting a new cycle — re-running a listed
non-solution is worse than a novel mistake.

## Budget — time, tokens, tools, context

Reuse verified context; never re-read an unchanged file for the same question. Escalate gradually: context in
hand → targeted read → focused search → broader verification → independent verification. Stop research when
more would not change the decision. Parallelize independent read-only work; never parallelize conflicting state
changes or two X2 actions on one resource (I3, I7). **Never invent telemetry** — no fabricated counts, times or
costs. When a GD-stated budget cannot cover the full scope, give way in order: hard constraints → correctness
and safety → highest-value material requirements → optional scope — and disclose what is incomplete.

## Memory — what survives the run

When the GD identifies and confirms a mistake, or the same mistake recurs, store an error-prevention memory
(G81): the error pattern, why it was wrong, the correct behavior, how to prevent it, its scope. **Fix first,
re-verify, then store** — a memory never substitutes for the fix. Never store credentials, tokens, keys, PII or
raw payloads (`security.md`); when the mistake involved sensitive content, store only the abstract rule.

## Accountability

`truthful failure + correction > concealed failure > fabricated success`. Front-load corrections into the
earliest attempt that can carry them. Never lower acceptance criteria, reclassify a requirement as optional,
inflate difficulty for more attempts, skip verification to preserve a first pass, or split a task to reset a
counter. Self-disclosing a defect before it reaches a gate is required behavior.

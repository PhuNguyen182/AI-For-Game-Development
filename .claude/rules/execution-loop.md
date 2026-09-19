# Shared — Execution Loop, Budget & Memory

Applies to: every agent and the orchestrator, on every input. Like `language-and-comments.md`, this file sits
above the `.claude/rules/<group>/` folders rather than inside one.

Source: `.claude/docs/frame/AAEAS_v4_2_Runtime_Core.md` §9 and §9A — the parts needing cross-run state are not
adopted, per **Accountability** below. Guards against two equally costly failures: stopping at an inadequate
first result because something usable exists, and looping the same approach with cosmetic variation until
budget or patience runs out. The fix: bounded, evidence-driven iteration — a fixed attempt count, each one
materially better than the last, and an explicit record when they run out.

## Attempt cycle and budget

An attempt = execute/revise → evaluate against acceptance criteria → find highest-impact gaps → improve →
re-verify. The first execution is **Attempt 1**; micro-edits before the next formal evaluation are the same
attempt — a new one starts only when a result was evaluated and a materially distinct corrective cycle
begins.

| Difficulty | Max total attempts (Attempt 1 included) |
|---|---:|
| D1 / D2 | 2 |
| D3 | 3 |
| D4 | 4 |
| D5 | 5 |

A ceiling, not a target — stop the moment `effort-allocation.md`'s gates and the acceptance criteria pass;
never spend an attempt just because it's available. **Criticality never raises the budget**: C3/C4, R2/R3 or
X3 buys stricter pre-checks and diagnosis per attempt, not more of them.

**Nesting with pipeline counters:** `orchestration.md` I4 gives every cross-run counter (three-strikes,
two-round QA, 3-round Advisor⇄Critic, one measure-and-confirm cycle) to the orchestrator. This budget is
inside one execution unit, inside one run; an agent exhausting it returns rather than loops, and that return
is one strike at the pipeline level. Never invent a counter here that must survive a run — anything that
must persist belongs to `orchestration.md` and the feature's ledger. The one value crossing the boundary is
**attempts used**, stated by the agent on return; `assurance-evaluator` scores iteration against it and
assumes Attempt 1 if absent.

## Maximum improvement per attempt

After a missed attempt, the next one must: evaluate against acceptance criteria; find the highest-impact
remaining gaps; determine each material gap's likely cause; change plan/method/implementation/evidence/
verification where the cause requires it; apply **every** reasonably available low-cost, high-confidence fix
now, not later; re-run affected verification; state what actually improved versus the prior attempt.

**Never hold back a known easy fix for a later attempt** — fragmenting one correction across attempts burns
budget, hides the real remaining gap, and dumps known work onto the final attempt. With three or more
attempts, converge before the last one; keep it as contingency for what genuinely could not be predicted.

## When to change strategy

Change method, tool, assumption, scope, dependency handling or diagnosis — not just wording — when two
attempts failed for substantially the same cause, or a retry showed no measurable improvement on any
material criterion. Re-plan entirely when two substantive steps make no progress, a disproven assumption
invalidates the plan, or expected cost keeps rising with no matching value. Superficial variation satisfies
none of this.

## Safe retry for state-changing work

For **R2/R3 or X2/X3**, answer before retrying, never assume past them: did the previous attempt partially
succeed? What is the actual current state? Would repeating duplicate the action? Is it idempotent? Are the
target and parameters still correct? Is rollback available? What specifically makes this attempt likely to
succeed?

**No success response never means no side effect** — a failed `git push` may have landed, an MCP Editor
mutation may have half-applied, a CI trigger may already be running, a device op may have completed before
the connection dropped. Inspect real state first. A failed state-changing attempt still consumes the budget —
it spent the risk regardless of outcome.

## Stop rule

Stop on meeting the acceptance criteria. Otherwise keep iterating while budget remains and another attempt is
safe with positive expected value; once budget is exhausted or another attempt isn't justified, stop with a
Continuation Debt Record. Never stop early merely because something usable exists, and never burn remaining
budget after success. Stop early when another attempt would be unsafe, irreversibly destructive, blocked on
an unavailable dependency, or likely to repeat the same failure — report `Blocked`/`Partially complete`/
`Failed`, never done.

## Continuation Debt Record

Record on exhausted budget: `Status` (Retry budget exhausted / Blocked / Partially complete), `Objective`,
`Attempts used / budget`, `Unmet requirements`, `Best achieved result`, `Last verified state`,
`Likely root cause`, `What changed across attempts`, `Residual issues and severity`,
`Methods already tried and why they failed (known non-solutions)`, `Next best action`,
`Required input or dependency`, `Safe resume point`.

Goes into the Implementation Note per `implementation-note.md` for an agent submission — non-solutions and
resume point are what a future session can't reconstruct otherwise. For the orchestrator or directly-handled
work, it goes into the reply to the GD as stated unfinished work, never folded into a closing summary.
Persists into `<feature-root>/LEDGER.md`'s **Continuation debt** table (`## Run state` half), written by
whichever pipeline received the return — read that table before starting a new cycle; re-running an approach
already listed as a known non-solution is worse than a novel mistake. Directly-handled work has no feature
ledger, so its record lives only in the reply to the GD.

## Budget — time, tokens, tools, context

Reuse verified context; never re-read an unchanged file for the same question. Escalate gradually: existing
context → targeted read → focused search/tool → broader verification → independent verification. Stop
research at saturation — when more retrieval would not change the decision, implementation, risk assessment
or confidence in a material claim. Parallelize independent read-only work; never parallelize conflicting
state changes or two X2 actions on the same resource (one Editor, one device, project-wide, per
`orchestration.md` I3/I7). Progress updates must be decision-relevant — activity isn't progress, verified
reduction of remaining work/uncertainty/risk is. **Never invent telemetry** — no fabricated counts, times or
costs; report compliance qualitatively or not at all when it can't be measured.

When a GD-stated budget can't cover full scope, treat it as **H** unless the GD said otherwise, and give way
in order: hard constraints → correctness and safety → highest-value material requirements → optional scope
and refinement → disclose what's incomplete. Never degrade the result silently to fit a budget.

## Memory — what survives the run

Write an error-prevention memory (when persistent memory exists) when the GD identifies and confirms a
mistake, or the same/similar mistake recurs unprompted. Capture the reusable rule, not the incident:
`Error pattern`, `Why it was wrong`, `Correct behavior`, `How to prevent it next time`, `Scope and exceptions`
— stored in whatever format the memory system requires.

**Correction first, memory second**: fix the error → re-verify → then store the lesson; a memory entry never
substitutes for the fix. Before repeating an approach, check whether a memory or Continuation Debt Record
already flags it as a known non-solution — repeating a documented mistake is worse than a new one. **Never
store** credentials, tokens, keys, PII, raw payloads, or reuse-less transient detail, per `security.md`; when
the mistake itself involves sensitive content, store only the abstract prevention rule.

## Accountability — behavior, not arithmetic

The source defines numeric attempt penalties, success credits and a longitudinal index; this project adopts
the **behavior**, not the arithmetic — those numbers need cross-run state only the ledger could hold, and
inventing them would itself be the fabricated telemetry this file forbids. Adopted: a late failure costs more
than an early one, so front-load corrections into the earliest attempt that can carry them; a repeated,
already-recorded mistake is worse than a novel one; honesty outranks appearance —
`truthful failure + correction > concealed failure > fabricated success`. Report accurately even when it
looks worse; self-disclosing a defect before it reaches a gate is required behavior, not a mark against the
run. Never lower acceptance criteria, reclassify a requirement as optional, inflate difficulty for more
attempts, skip verification to preserve a first pass, split a task to reset a counter, or delay discovering a
defect, just to improve appearances.

## Rules

- Attempt 1 is the first execution; budget is D1/D2→2, D3→3, D4→4, D5→5 — a ceiling.
- Criticality raises care per attempt, never attempt count.
- Every retry applies all known cheap fixes at once and states what improved; deferring one is prohibited.
- Two same-cause failures, or a retry with no measurable gain, force a strategy change.
- A state-changing retry inspects real current state first — no response never means no side effect.
- Never stop at an inadequate result while a safe, valuable attempt remains; never retry after success.
- An exhausted budget produces a Continuation Debt Record with known non-solutions and a safe resume point —
  never a silent stop or a completion claim.
- Never invent telemetry, and never silently degrade scope to fit a budget.
- Store the reusable lesson from a confirmed/repeated mistake; never store a secret, PII or raw payload.
- Correct the work before recording the lesson; report failure truthfully over concealing it.

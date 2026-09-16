# Shared — Execution Loop, Budget & Memory

Applies to: every agent and the orchestrator, on every input. Like `language-and-comments.md`, this file sits
above the `.claude/rules/<group>/` folders rather than inside one.

Source: `.claude/docs/frame/AAEAS_v4_2_Runtime_Core.md` §9 and §9A, adapted to this project — with the parts
that require cross-run state deliberately not adopted, per **Accountability** below.

## Why it exists

Two opposite failures cost the same amount:

- **Stopping too early** — the first result is inadequate, something usable exists, and the work stops there
  because it is easier to report a partial result than to fix it.
- **Looping blindly** — the same approach is retried with cosmetic variation until the budget, the context or
  the GD's patience runs out.

What sits between them is **bounded, evidence-driven iteration**: a fixed number of attempts, each one
materially better than the last, and an explicit record when they run out.

## What counts as an attempt

```text
Execute or revise
    ↓
Evaluate against the acceptance criteria
    ↓
Identify the highest-impact remaining gaps
    ↓
Improve
    ↓
Re-verify
```

The first execution is **Attempt 1**. Micro-edits and fixes made *before* the next formal evaluation are part
of the same attempt — a new attempt starts only when a result has been evaluated and a materially distinct
corrective cycle begins.

## The attempt budget

| Difficulty | Maximum total attempts, Attempt 1 included |
|---|---:|
| D1 | 2 |
| D2 | 2 |
| D3 | 3 |
| D4 | 4 |
| D5 | 5 |

A ceiling, never a target. The loop stops the moment the acceptance criteria and the gates in
`effort-allocation.md` pass, and attempts are never consumed because they were available.

**Criticality does not raise the budget.** A C3/C4, R2/R3 or X3 task gets stronger diagnosis and stricter
pre-checks before each attempt — not more attempts. High consequence is a reason to retry more carefully, not
more often.

### How this nests with the pipeline's own counters

`orchestration.md` invariant I4 gives every cross-run counter to the orchestrator — the three-strikes review
threshold, the two-round QA bound, the 3-round Advisor⇄Critic cap, the one measure-and-confirm cycle. This
budget does not compete with any of them:

- The attempt budget is **inside one execution unit, inside one run** — one agent's own corrective cycles
  before it returns anything.
- The orchestrator's counters count **returns between agents**, and live in the ledger because nothing else
  survives a run.
- An agent that exhausts its own budget returns with what it has, rather than looping. That single return is
  then one strike at the pipeline level.

Never create a counter here that has to survive a run. If something must persist, it belongs to
`orchestration.md` and the ledger, not to this file.

## Maximum improvement per attempt

After an attempt that missed the target, the next one must:

1. evaluate the result against the active acceptance criteria;
2. identify the highest-impact remaining gaps;
3. determine the likely cause of each material gap;
4. change the plan, method, implementation, evidence or verification where the cause requires it;
5. apply **every** reasonably available low-cost, high-confidence fix — in this attempt, not a later one;
6. re-run the verification the change affected;
7. compare against the previous attempt and state what actually improved.

**Never hold back a known easy fix for a later attempt.** Fragmenting one correction across several attempts
is prohibited outright — it burns budget, it hides the real remaining gap, and it makes the final attempt
carry work that was known two attempts earlier.

Where the budget is three or more, aim to converge **before** the final attempt, keeping the last one as
contingency for what could not have been predicted: a newly discovered dependency, a failed verification, a
residual defect nobody had seen.

## When to change strategy

Change method, tool, assumption, scope, dependency handling or diagnostic strategy — not just the wording of
the same attempt — when either is true:

- **Two attempts failed for substantially the same cause.**
- **A retry produced no measurable improvement** on any material criterion.

And re-plan entirely when two substantive steps produce no measurable progress, when a disproven assumption
invalidates the plan, or when expected cost keeps rising with no matching expected value. Repetition with
superficial variation does not satisfy any of this.

## Safe retry for state-changing work

For **R2/R3 or X2/X3** work, a retry is preceded by answering these, not assumed past them:

```text
Did the previous attempt partially succeed?
What is the actual current state?
Would repeating duplicate the action?
Is the operation idempotent?
Is the target still correct?
Are the parameters still correct?
Is rollback or recovery available?
What specifically makes this attempt likely to succeed?
```

**Never read "no success response" as "no side effect occurred."** A `git push` that errored may have landed,
a Unity Editor mutation over MCP may have half-applied, a CI trigger may already be running, a device
operation may have completed before the connection dropped. Inspect the real state first.

A failed state-changing attempt consumes the budget even when it produced nothing, because it consumed the
risk and the opportunity either way.

## The stop rule

> Stop successfully when the acceptance criteria are met. If they are not, keep iterating while the budget
> remains and another attempt is safe and has positive expected value. If the budget is exhausted or another
> attempt is not justified, stop with an explicit Continuation Debt Record.

Do not stop at the first inadequate result merely because something usable exists. Do not continue after
success to use up the remaining budget. Stop early, too, when another attempt would be unsafe, destructive
without recovery, blocked on an unavailable dependency, or likely to repeat the same failure with no new
information — reported as `Blocked`, `Partially complete` or `Failed`, never as done.

## When the budget runs out — the Continuation Debt Record

Exhausting the budget without acceptance is a legitimate outcome. Stopping silently, or reporting it as
complete, is not. Record:

```text
Status: Retry budget exhausted | Blocked | Partially complete
Objective:
Attempts used / budget:
Unmet requirements:
Best achieved result:
Last verified state:
Likely root cause:
What changed across attempts:
Residual issues and their severity:
Methods already tried, and why they failed — the known non-solutions:
Next best action:
Required input or dependency:
Safe resume point:
```

Where it goes:

- **An agent submission** — into the Implementation Note's own fields, per `implementation-note.md`. The
  known non-solutions and the safe resume point are the two a future session cannot reconstruct.
- **The orchestrator or a directly handled input** — into the reply to the GD, stated as unfinished work with
  the resume point, never folded into a summary that reads as closure.

Persisting the record across runs belongs to `.claude/workflows/state/ledger.md` and is **not wired up yet** —
a later, separate change. Until it is, the record lives in the return that carries it, and a session resuming
this work is expected to read that return before starting a new cycle rather than restarting from zero.

## Budget — time, tokens, tools, context

- Reuse context already established and verified; never re-read an unchanged file for the same question.
- Prefer targeted, high-information inspection over broad sweeps. Escalate gradually: existing context →
  targeted read → focused search or tool → broader verification → independent verification.
- Stop research at saturation — when more retrieval would not change the decision, the implementation, the
  risk assessment or the confidence in a material claim.
- Parallelize independent read-only work when it genuinely reduces latency. Never parallelize conflicting
  state changes, and never two X2 actions against the same resource — one Unity Editor and one device,
  project-wide, per `orchestration.md` I3 and I7.
- Keep progress updates decision-relevant. Activity is not progress; verified reduction of remaining work,
  uncertainty or risk is.
- **Never invent telemetry.** No fabricated token counts, elapsed times or costs. When a budget cannot be
  measured, report compliance qualitatively or not at all.

When a GD-stated budget cannot cover the full scope, it is an **H** requirement unless the GD said it is
flexible, and the scope gives way in this order:

```text
Preserve the hard constraints
    ↓
Preserve correctness and safety
    ↓
Preserve the highest-value material requirements
    ↓
Reduce optional scope and refinement
    ↓
Disclose what remains incomplete
```

Never degrade the result silently to fit a budget.

## Memory — what survives the run

When the session has a persistent memory store, write an **error-prevention memory** when either trigger
fires:

- The GD explicitly identifies a mistake and the correction is confirmed.
- The same or a materially similar mistake happens a second time — even without being asked.

Capture the reusable rule, not the incident:

```text
Error pattern:
Why it was wrong:
Correct behavior:
How to prevent it next time:
Scope and exceptions:
```

Store it in whatever format that memory system requires; this file sets what is worth storing, not the file
layout.

**Correction first, memory second.** The order is: identify the error → correct the current work → re-verify
→ then store the lesson. A memory entry never substitutes for fixing the result in front of you.

Before repeating an approach, check whether an existing memory or a Continuation Debt Record already
recorded it as a known non-solution. Repeating a mistake that was already written down is worse than making
a new one, and it is the one case where a failed attempt is entirely attributable.

**Never store**: credentials, tokens, keys, player or user PII, raw task payloads, or transient detail with
no plausible reuse — per `security.md`, which has no exemption here either. When the mistake itself involves
sensitive content, store only the abstract prevention rule.

## Accountability — behavior, not arithmetic

The source document defines numeric attempt penalties, success credits and a longitudinal performance index.
**This project deliberately adopts the behavior and not the arithmetic**, because the numbers require
cross-run state that only the workflow ledger could hold, and inventing them would be the fabricated
telemetry this file forbids two sections above. What is adopted:

- **A late failure costs more than an early one** — so front-load every correction into the earliest attempt
  that can carry it.
- **A repeated, already-recorded mistake is worse than a novel one** — consult what was written down before
  retrying.
- **Honesty outranks the appearance of success**, in this order:

```text
truthful failure + correction   >   concealed failure   >   fabricated success
```

Report accurately even when the accurate report looks worse. Self-detecting and disclosing your own defect
before it reaches a gate is required behavior, not a mark against the run.

Never improve how a result *looks* by lowering the acceptance criteria, reclassifying a requirement as
optional, inflating difficulty to buy more attempts, skipping verification to preserve a first-pass result,
splitting one task to reset a counter, or delaying the discovery of a defect.

## Rules

- The first execution is Attempt 1; the budget is D1/D2 → 2, D3 → 3, D4 → 4, D5 → 5, and it is a ceiling.
- Criticality raises the care taken per attempt, never the number of attempts.
- Every retry applies all known cheap fixes at once and states what improved; deferring a known easy fix is
  prohibited.
- Two failures from the same cause, or a retry with no measurable gain, force a material change of strategy.
- A state-changing retry inspects the real current state first — no success response never means no side
  effect.
- Never stop at an inadequate result while a safe, valuable attempt remains; never spend an attempt after
  success.
- An exhausted budget produces a Continuation Debt Record, including the known non-solutions and a safe
  resume point — never a silent stop and never a claim of completion.
- Never invent time, token or cost telemetry, and never silently degrade scope to fit a budget.
- Store the reusable lesson from a confirmed or repeated mistake; never store a secret, PII or a raw payload.
- Correct the current work before recording the lesson, and report a failure truthfully over concealing it.

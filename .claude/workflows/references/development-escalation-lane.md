# The Escalation Lane — `feature-development.md`

> **Read when a routine implementation pass has already failed.** Split out of `feature-development.md` under
> the promotion rule in `client/feature-documentation.md`: it is never a first dispatch, so most features
> never open it.

Never a first dispatch — reachable from **any** step, returning to the step it left. The pipeline's diagram
draws it as a dotted edge off the client fan-out only, because that is where it opens most often; step 1 and
step 3 reach it too, through `csharp-engineer`'s and `netcode-engineer`'s own Escalate criteria.
`tech-lead-performance` returns `Rejected`, `Routed to: unity-engineer` when the obvious fixes are still
open, and `tech-lead-csharp-unity` names a misrouted escalation as one. It is silent to the GD: a technical
loop they see only through a `Blocked` needing their input, or later at CP3.

**One round trip, per `references/loop-termination.md`.** Agent → lead → refused → agent. If the same problem
escalates a second time and is refused a second time, the two disagree about whose problem it is and neither
can settle that — it goes to `technical-architect` as a routing question, not to either of them again.

**Silent to the GD is not silent to the gates.** Both leads hold `Write`/`Edit` and both return
`Fix: <what changed, and where>`, so a lead's fix is a submission like any other — and its
`Pattern decision:`, where the scope is project-wide, binds roots this feature will never touch.
`references/development-exit-and-custody.md` holds both: which door the code takes, and where the pattern is
recorded so it survives the run that produced it.

## Why it is bounded at one round trip

Both leads are contractually allowed — required, even — to refuse a misrouted escalation, and both refusals
are correct results rather than failures. What nothing bounded was the case where the implementing agent
escalates the *same* problem again and gets the *same* refusal.

That is not a technical loop any more; it is a **disagreement about ownership**, and neither party to a
disagreement can adjudicate it. `technical-architect` owns triage, so the second refusal routes there as a
routing question — with both escalations and both refusals attached, because the pattern is the input.

`references/loop-termination.md` holds this bound alongside every other one in the layer.

## The one agent that is not on this lane

`tech-lead-sdk-platform` is dispatched straight from the spec at step 2. Its scope has no routine owner
beneath it — there is no routine SDK engineer for it to be an escalation from — so an SDK task has nowhere else to
start. It is a lead by seniority, not by escalation.

# Shared — Orchestration

Applies to: every agent dispatch in this project, in every mode — a full pipeline run, a single pipeline
entered at one of its entry points, or one agent called directly. Like `language-and-comments.md`, this file
sits above the `.claude/rules/<group>/` folders rather than inside one.

It is a rule rather than a workflow file because `.claude/workflows/*` is never loaded into a session — it
takes effect only when something reads it. Those six files hold every checkpoint, retry cap and
required-input table this project has, and none of it happens on its own. This file is their ignition.

## The one instruction

**Before dispatching any agent, read `.claude/workflows/orchestrator.md` and
`.claude/workflows/state/ledger.md`.** The router picks the input's lane; the ledger carries the state no
agent can hold across runs. Neither costs an agent call.

## Size the input before choosing a process

Most inputs are not feature requests, and the full pipeline costs eight agent calls. Four criteria decide
whether an input needs it — each answerable by a grep or one read of the request, never by dispatching
anyone:

| Send it to `feature-intake.md` when it | Because |
|---|---|
| Touches `Game.Core.*` — a game rule, economy, state machine, cooldown | A determinism or authority error stays invisible until it diverges |
| Needs more than one role | Coordination is what the fan-out and the handoff matrix exist for |
| Is multiplayer-relevant | Client/server disagreement does not show on one screen |
| Rests on something the GD has not decided yet | Checkpoint 1 exists for exactly this, and nothing else provides it |

**None of the four → handle it directly.** Do the work, or dispatch the one agent whose tools or domain
rules it actually needs. No triage, no Tech Spec, no checkpoint. State which lane was picked, so the GD
redirects at the first turn instead of after eight calls.

**Escape upward the moment a criterion turns out to apply.** Stop and enter `feature-intake.md`. Little was
built, so little is lost — which is what makes the cheap default safe rather than reckless.

## Invariants — these hold in every mode

| # | Invariant |
|---|---|
| **I1** | Required inputs travel with the dispatch. The dangerous omissions are silent: with no track state `technical-architect` assumes client-only, with no tier `qa-lead` assumes Medium, and neither says so |
| **I2** | Review debt attaches to the artifact, not to the run. Code written outside a pipeline still owes `review-pipeline.md`. The ledger records it and settles it in batch — recording never blocks a dispatch |
| **I3** | One Unity Editor, project-wide. Ten agents hold `mcp__<server>__*` Editor tools against a single process; never run two at once, whatever mode each was started in |
| **I4** | Every retry counter is the orchestrator's — three strikes, the two-round QA bound, the 3-round Advisor⇄Critic cap, the one measure-and-confirm cycle. A round nobody counted is a cap that never fires |
| **I5** | A design flaw reaches the GD immediately, in every mode — never folded into a later report, never re-filed as an ordinary bug |
| **I6** | A gap the GD accepts is written into the feature's known limitations before closure, or "nobody checked" becomes indistinguishable from "QA passed" |

## Rules

- Read the router before dispatching, and state the lane you picked.
- Never enforce by blocking. These are directions the GD overrides at will — state the cost, then do what
  they asked.
- Never let a counter live only in context. Anything that matters across runs belongs in the ledger.
- A directly dispatched agent is still isolated and stateless: it cannot be recalled mid-run, cannot see
  another agent's return, and its `Routed to:` is a recommendation for you to act on — never an action it took.

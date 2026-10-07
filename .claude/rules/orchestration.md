# Shared — Orchestration

Applies to: every agent dispatch, in every mode — a full pipeline run, one pipeline entered at one of its
doors, or one agent called directly. `.claude/workflows/*` is never auto-loaded; this rule is what makes it run.

## The one instruction

**Before dispatching any agent, read `.claude/workflows/orchestrator.md`, and the `LEDGER.md` of whichever
feature the work belongs to.** The router picks the lane; the ledger carries what no agent can hold across
runs. `.claude/workflows/gd-touchpoints.md` lists every point where the GD is asked, approves or is told — and
the points where asking is forbidden. Neither read costs an agent call.

State lives beside the project's work, never under `.claude/`: a feature's ledger is `LEDGER.md` at its feature
root, and what belongs to no feature is in `<state-root>/project-state.md`. **`<state-root>` is `.workflow/`**
unless this project's `CLAUDE.md` names another path. `.claude/` is the framework every project copies; state
written into it becomes another project's history.

## Invariants — these hold in every mode

| # | Invariant |
|---|---|
| **I1** | Required inputs travel with the dispatch. Tier and its five axes, attempt budget, verification floor and track travel with **every** dispatch; the rest per `workflows/references/dispatch-brief.md`. The dangerous omissions are silent — an agent missing one assumes a default and does not say so |
| **I2** | Gate debt attaches to the artifact, not to the run. Source written outside a pipeline, and every gated-direct submission, owes **the gate offer** — the gates themselves are the GD's to authorise or decline (G50). `project-state.md` records the answer either way, `unoffered` or `declined`. Recording never blocks a dispatch |
| **I3** | One Unity Editor, project-wide. Never run two holders of Editor tools at once, whatever mode started each |
| **I4** | Every cross-run counter is the orchestrator's, written to the ledger when it changes. The attempt budget is the one counter an agent holds itself, inside one dispatch; on return, attempts-used becomes ledger state |
| **I5** | A design flaw reaches the GD immediately, in every mode — never folded into a later report, never re-filed as an ordinary bug (G4) |
| **I6** | A gap the GD accepts is written into the feature's known limitations before closure, or "nobody checked" becomes indistinguishable from "QA passed" |
| **I7** | One physical device, project-wide. Device test walks and device profiling are the same wire; never both at once |
| **I8** | Every cap composes into a stop, never into another round. One root-cause reset per submission across every loop; past it, a Continuation Debt Record to the GD. `workflows/references/bounds.md` |
| **I9** | A lock is released by whoever claimed it. A lock whose holder cannot be confirmed running is reclaimed by the procedure in `workflows/state/README.md`, never silently |
| **I10** | Source that reaches no gate is a hole, not debt. Every agent that writes `.cs` has a route to `review-pipeline.md` — including `qa-automation-engineer`, whose suite enters at **E3** as soon as it is written, before its results serve as evidence (G62) |

## Rules

- State the lane you picked (G1). Never enforce by blocking — state the cost, then do what the GD asked (G11).
- Ask the GD only through the `AskUserQuestion` tool, as multiple choice — single-select when the answers
  exclude each other, multi-select when they are independent, the recommended option first — never as a
  question in chat they must answer by typing (G19).
- A dispatched agent is isolated and stateless: it cannot be recalled, cannot see another agent's return, and
  its `Routed to:` is a recommendation you act on, never an action it took.
- An agent that exhausted its attempt budget returns a Continuation Debt Record; record it whole and count the
  return as one strike, never as a free retry.
- After any change under `.claude/`, run `workflows/tools/verify-workflow-layer.ps1` before reporting the
  layer consistent.

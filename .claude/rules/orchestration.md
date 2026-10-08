# Shared — Orchestration

Applies to: every agent dispatch, in every mode — a full pipeline run, one pipeline entered at one of its doors, or
one agent called directly. `.claude/workflows/*` is never auto-loaded; this rule is what makes it run.

## The one instruction

**Before dispatching any agent, or writing source yourself, read `.claude/workflows/orchestrator.md`, and the
`LEDGER.md` of whichever feature the work belongs to.** The router picks the lane; the ledger carries what no agent
can hold across runs. `.claude/workflows/gd-touchpoints.md` lists every point where the GD is asked, approves or is
told — and the points where asking is forbidden. Neither read costs an agent call.

State lives in `<state-root>`, never under `.claude/` and never inside the Unity project: a feature's ledger is
`<state-root>/features/<slug>/LEDGER.md`, and what belongs to no feature is in `<state-root>/project-state.md`.
**`<state-root>` is `.workflow/`** unless this project's `CLAUDE.md` names another path. `.claude/` is the
framework every project copies; state written into it becomes another project's history.

## Terms

| Term | Means |
|---|---|
| **Source** | What builds or runs: `.cs`, shaders, build and CI scripts, and config that executes or carries a credential. Scenes, prefabs, text assets and documents are not source — editing them owes no gate offer |
| **Submission** | One agent return sent toward a gate, numbered `<slug>/S<n>` in the ledger (`direct/S<n>` with no ledger). Rework answering that submission's own review rejection keeps its number and its strikes; any other fix — a bug, a CP3 drift, a CP4 defect, a change request's rework, work escalated out of the gated-direct lane — is a new submission naming what it fixes, strikes from zero |
| **Strike** | One rejection of a submission by a review gate, or a Continuation Debt Record returned for it — counted per submission (`workflows/references/bounds.md`). Work with no submission — research, a QA executor's coverage — has no strikes |
| **Gated-direct** | The lane for work that trips a consequence criterion and nothing else — one owning agent, then the review gates the GD authorises (`workflows/orchestrator.md`, row 10) |
| **Door** | A pipeline's entry, `<pipeline>.md` **E<n>** — always read with its file; each pipeline numbers its own |
| **Boundary** | A point where a declined gate may be offered again — B18 in `workflows/references/bounds.md` lists them. A GD answer holds until the next boundary; nothing is re-asked at the one it was given |
| **Track** | Client-only, or client + multiplayer — one value, whatever a file calls it: `CLAUDE.md`'s "client+server" and a pipeline's "backend track on" both mean client + multiplayer |
| **CP1–CP4** | The GD's four checkpoints — direction, Tech Spec, implementation summary, closure (`workflows/gd-touchpoints.md` G21, G24, G51, G60) |

## Invariants — these hold in every mode

| # | Invariant |
|---|---|
| **I1** | Required inputs travel with the dispatch. Tier and its five axes, attempt budget, verification floor and track travel with **every** dispatch; the rest per `workflows/references/dispatch-brief.md`. The dangerous omissions are silent — an agent missing one assumes a default and does not say so |
| **I2** | Gate debt attaches to the artifact, not to the run. Source written outside a pipeline, and every gated-direct submission, owes **the gate offer** — the gates themselves are the GD's to authorise or decline (G50). `project-state.md` records the answer from A3 — `unoffered` or `declined`; an A1–A2 decline is stated in the reply instead. Recording never blocks a dispatch |
| **I3** | One Unity Editor, project-wide. Never run two holders of Editor tools at once, whatever mode started each — and whoever writes into the Unity project — `Assets/`, `Packages/`, `ProjectSettings/`, the orchestrator included — is a holder: the domain reload or reimport it triggers ends whatever the Editor was running |
| **I4** | Every cross-run counter is the orchestrator's, written to the ledger when it changes. The attempt budget is the one counter an agent holds itself, inside one dispatch; on return, attempts-used becomes ledger state |
| **I5** | A design flaw reaches the GD immediately, in every mode — never folded into a later report, never re-filed as an ordinary bug (G4) |
| **I6** | A gap the GD accepts is written into the feature's known limitations before closure, or "nobody checked" becomes indistinguishable from "QA passed" |
| **I7** | One physical device, project-wide. Device test walks and device profiling are the same wire; never both at once |
| **I8** | Every cap composes into a stop, never into another round. Every engineering loop — strikes, bug reopens, CP3 and CP4 rejections — gets one root-cause reset of its own; past it, a Continuation Debt Record to the GD. `workflows/references/bounds.md` |
| **I9** | A lock is released by whoever claimed it. A lock whose holder cannot be confirmed running is reclaimed by the procedure in `workflows/state/README.md`, never silently |
| **I10** | Source never offered a gate is a hole; source whose gate the GD declined is recorded debt (I2). Every agent that writes `.cs` has a route to `review-pipeline.md` — including `qa-automation-engineer`, whose suite enters at **E3** as soon as it is written, before its results serve as evidence (G62) |

## Rules

- State the lane you picked (G1). Never enforce by blocking — state the cost, then do what the GD asked (G11).
- Ask the GD only through the `AskUserQuestion` tool, as multiple choice — single-select when the answers exclude
  each other, multi-select when they are independent, the recommended option first — never as a question in chat
  they must answer by typing (G19).
- A dispatched agent is isolated and stateless: it cannot be recalled, cannot see another agent's return, and its
  `Routed to:` is a recommendation you act on, never an action it took.
- An agent that exhausted its attempt budget returns a Continuation Debt Record; record it whole and count it as
  one strike on its submission, where it has one — never as a free retry.
- After any change under `.claude/`, run `workflows/tools/verify-workflow-layer.ps1` before reporting the layer
  consistent.

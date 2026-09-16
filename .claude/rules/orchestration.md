# Shared — Orchestration

Applies to: every agent dispatch in this project, in every mode — a full pipeline run, a single pipeline
entered at one of its entry points, or one agent called directly. Like `language-and-comments.md`, this file
sits above the `.claude/rules/<group>/` folders rather than inside one.

It is a rule rather than a workflow file because `.claude/workflows/*` is never loaded into a session — it
takes effect only when something reads it. Those six files hold every checkpoint, retry cap and
required-input table this project has, and none of it happens on its own. This file is their ignition.

## The one instruction

**Before dispatching any agent, read `.claude/workflows/orchestrator.md`, and the ledger of whichever feature
the work belongs to.** The router picks the input's lane; the ledger carries the state no agent can hold
across runs. Neither costs an agent call.

Ledgers are **one per feature**, at `.claude/workflows/state/<feature-slug>/ledger.md`; the in-flight index,
open gate debt and both global locks are in `.claude/workflows/state/project-state.md`. The layout and the
template are in `state/README.md`. There is no shared ledger file any more — a single document forced every
concurrent feature's counters into one place, where one feature's strike count sat beside another's.

## Size the input before choosing a process

Most inputs are not feature requests, and the full pipeline costs eight agent calls. **The lane table and the
four escalation criteria live in `orchestrator.md` step 0 — one fact, one home.** This file does not restate
them; it states why reading them is not optional:

- **The default is direct.** No criterion tripped means no classification round, no Tech Spec, no checkpoint.
- **Consequence buys the gates, not the pipeline.** A criterion tripped for **C** alone takes the
  gated-direct lane — the one agent, then both review gates. `task-classification.md` Step 4 is the authority
  and `workflows/references/gated-direct-lane.md` is the detail.
- **The lane is not the tier.** Directly-handled work is still classified, and a direct-lane task at
  **C3/C4, R2/R3 or X2/X3** runs at that tier's verification floor and safe-retry discipline regardless. What
  a high tier never buys is process.
- **Escape upward the moment a criterion turns out to apply.** Little was built, so little is lost.

## Invariants — these hold in every mode

| # | Invariant |
|---|---|
| **I1** | Required inputs travel with the dispatch. The dangerous omissions are silent: with no track state `technical-architect` assumes client-only, with no tier and verification floor `qa-lead` plans at a depth it chose itself, and neither says so. The four that travel with **every** dispatch — tier and its five axes, attempt budget, verification floor, track — are in `workflows/references/entry-index.md` |
| **I2** | Gate debt attaches to the artifact, not to the run. Code written outside a pipeline owes **the gate offer** — the gates themselves are the GD's to authorise or decline, per `workflows/references/optional-gates.md`. `state/project-state.md` records the answer either way, **unoffered** or **declined**, and settles in batch. Recording never blocks a dispatch |
| **I3** | One Unity Editor, project-wide. 10 agents hold `mcp__<server>__*` Editor tools against a single process; never run two at once, whatever mode each was started in |
| **I4** | Every retry counter is the orchestrator's — three strikes, the two-round QA bound, the 3-round Advisor⇄Critic cap, the one measure-and-confirm cycle. A round nobody counted is a cap that never fires. `execution-loop.md`'s attempt budget is the one counter an agent holds itself, **inside a single dispatch**; the moment it returns, its attempts-used becomes ledger state like everything else |
| **I5** | A design flaw reaches the GD immediately, in every mode — never folded into a later report, never re-filed as an ordinary bug |
| **I6** | A gap the GD accepts is written into the feature's known limitations before closure, or "nobody checked" becomes indistinguishable from "QA passed" |
| **I7** | One physical device, project-wide. `build-verification-tester` walking cases over adb and `performance-qa-engineer` profiling a Development Build over adb are the same wire; never run both at once |
| **I8** | Every cap composes into a stop, never into another round. A submission gets **one** root-cause reset across every loop it enters; past that the work goes to the GD as a Continuation Debt Record. `workflows/references/loop-termination.md` holds the ladder |
| **I9** | A lock is released by whoever claimed it. A lock whose holder cannot be confirmed running is **reclaimed by the procedure in `state/project-state.md`, never silently** — an invariant with no recovery path stops being one the first time a run dies holding it |
| **I10** | Source that reaches no gate is a hole, not debt. Every agent that writes `.cs` has a route to `review-pipeline.md` — including `qa-automation-engineer`, whose tests enter at **E3** after QA closes |

## Rules

- Read the router before dispatching, and state the lane you picked.
- Never enforce by blocking. These are directions the GD overrides at will — state the cost, then do what
  they asked.
- Never let a counter live only in context. Anything that matters across runs belongs in that feature's ledger.
- An agent that exhausted its attempt budget returns a Continuation Debt Record, not a silent partial result.
  Record it whole — the known non-solutions and the safe resume point are what the next session cannot
  reconstruct — and treat the return as one strike, never as a free retry.
- A directly dispatched agent is still isolated and stateless: it cannot be recalled mid-run, cannot see
  another agent's return, and its `Routed to:` is a recommendation for you to act on — never an action it took.
- After any change under `.claude/`, run `workflows/tools/verify-workflow-layer.ps1`. Every count this layer
  states about itself is a claim, and an unchecked claim is E0 evidence on `effort-allocation.md`'s own scale.

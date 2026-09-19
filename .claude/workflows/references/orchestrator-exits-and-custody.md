# Orchestrator — Exits, Custody and the No-Ledger Lanes

> **Read when a lane ends, when a pipeline hands back, and whenever a dispatch has no feature ledger behind
> it.** Split out of `orchestrator.md` under the promotion rule: none of this is read while sizing an input,
> and all of it is read once a lane has been picked. `orchestrator-direct-dispatch.md` is its sibling — that
> file covers dispatching one agent, this one covers what comes back and what outlives it.

## The exits — every place a lane ends

Five pipelines declare their own exits — four through an `*-exit-and-custody.md`, `feature-intake.md` through
its own `## What this pipeline hands on`. The router declared none, and it is the one file every terminal
return passes through. These are its doors.

| A lane ends with | The router does |
|---|---|
| **CP4 approved** — the feature closed | Close the ledger, below. This is the only terminal state a feature has |
| **CP4 rejected as a change request** | `change-request.md` **E2**, which declares that door and names CP4 as its origin. Not a defect, and no rejection counter moves |
| **CP2 approved on a standalone intake run** | Back to the GD with the Tech Spec. Mode 2 hands on to nothing, per `standalone-runs.md` |
| **Findings on a standalone audit** | Back to the GD as a report. No author, no strike, no **CP3** |
| **A cap in `loop-termination.md` reached** | A Continuation Debt Record to the GD, and into the ledger's `Continuation debt` table. Never folded into a summary that reads as closure |
| **A design flaw, from any agent at any step** | The GD, **immediately** — invariant **I5**. Never queued behind the work that surfaced it, never re-filed as an ordinary defect, whatever the status says |
| **`Config required:` or `Risks flagged:`, on any status** | The GD. A `Done` can still need them, and answering only the missing input drops the rest |
| **The GD drops the work, or it is superseded** | Mark the ledger `Abandoned`, with why and the last verified state. A feature with no terminal state cannot be told from one still in flight |
| **A lane escaped upward** | `feature-intake.md` **E1**, carrying what was learned — both rejection sets and the code from a gated-direct second strike, per `gated-direct-lane.md` |
| **A mode-2 or mode-3 return, no pipeline running** | `orchestrator-direct-dispatch.md`'s fallback table |

**Nothing leaves without its record.** Whichever door a lane takes, the transition is written before the next
dispatch — `state/README.md`'s rule, and the one thing no agent can do on the router's behalf.

## The four values when there is no ledger

`entry-index.md` says the tier, the attempt budget, the verification floor and track state are supplied
**from the feature's ledger**, and that an entry missing them returns `Blocked`. Most of what the router
handles has no ledger at all: a chore, a question, a git task, a gated-direct submission, every mode-3
dispatch. Read literally, that is `Blocked` on the commonest lane in the layer.

| Value | Where it comes from with no ledger | Recorded in |
|---|---|---|
| **Tier and the five axes** | Classified from the request itself per `task-classification.md` — never dispatched to an agent to decide, and never inherited from code somebody else wrote | Stated in the reply at **A3** and above; nowhere else unless the run opens a ledger |
| **Attempt budget** | Derived from **D** — 2 at D1–D2, 3 at D3, **4 at D4, 5 at D5**. The row read "2 or 3" and stopped, which left a **mode-3** dispatch with no value at all: mode 3 is not capped at D3 the way this row assumed, since naming an `agent-id` runs a D4–D5 Core change in one call | The reply, if it is spent |
| **Verification floor** | Derived from **A** | The reply, and the Implementation Note where source was written |
| **Track** | The caller's own knowledge of the project. An unstated track is never "probably client-only" | The reply |

`Blocked` is the right answer only when a value can neither be derived nor asked for. **A tier the router can
classify in one read of the request is not a missing input** — it is work the router was told to do itself.

**A run that will outlive one dispatch opens a ledger — and only where a feature root exists to hold one.**
With no root there is nowhere for one to live, which is why the gated-direct lane keeps its counters in
`<state-root>/project-state.md` and a mode-3 dispatch keeps a gate-debt row there instead.

## Closing a ledger

`orchestrator.md` owns opening **and closing**. Opening is `feature-intake.md` step 2. Closing is four steps,
in this order, and the order is the point:

1. **Accepted gaps into the feature root's `DEBT.md`** — a declined gate is one — **before** closure is
   reported. Invariant **I6**: otherwise "nobody checked this" cannot be told from "QA passed it".
2. Mark the run state `Closed`, or `Abandoned` with why and the last verified state. The ledger stays at its
   feature root either way.
3. Copy the run's numbers into `<state-root>/calibration.md` — one row, from numbers already in the ledger.
   Nothing estimated, nothing reconstructed; an invented row is worse than no table.
4. Clear its row from the in-flight index in `<state-root>/project-state.md`.

**Reopening one.** A defect against a feature that already closed **reopens that ledger and re-adds its
in-flight row** — never a second slug, which `orchestrator.md` calls the failure that happens silently.
`optional-gates.md` states this for QA opting in at `qa-pipeline.md` **E1**; it holds identically for a
defect at `feature-development.md` **E3**, and the closed ledger is where its tier, floor and counters are.

**Who creates `<state-root>` — the first run that needs it.** Copy `state/templates/project-state.md` at the
first transition that has something to record. An absent file is not an error; an absent file nobody created
while a counter was owed is.

**A feature that simply stops being mentioned is the failure CP4 exists to prevent**, and the in-flight index
is the only thing in the layer that can notice it. Read it when a session starts, not only when opening a
ledger.

## The two locks, and getting one back

Both live in `<state-root>/project-state.md`, and both are the router's across concurrent runs — invariants
**I3** (one Unity Editor; 10 agents hold tools against it) and **I7** (one physical device). A run can die
holding either: a session ends mid-dispatch, an agent times out, the Editor crashes.

**A held lock is never permanent and is never cleared by guessing.** Invariant **I9**'s three-step reclaim —
is the holder still running, does the resource itself answer, then ask the GD — is in `state/README.md`,
with what to record afterwards. Whatever a stale holder produced is **unverified**: inspect the real state
before the next claim, because no success response never meant no side effect.

## Which invariant each of the router's own rules is

`orchestration.md` carries ten invariants. The router names **one** by number — **I5**, in its Rules — and
acts on **nine** of them — every one but **I10**, which is about each `.cs`-writing agent having a route to
a gate and belongs to the pipelines. The mapping lives here because the router is already at its cap:

| Invariant | Where the router meets it |
|---|---|
| **I2** | Gate debt attaches to the artifact — recorded either way, `unoffered` or `declined`, blocking nothing |
| **I3** · **I7** | The two locks above, across concurrent runs — the case no single pipeline can see |
| **I4** | Every cross-run counter is the router's, and goes to the ledger **at** the transition |
| **I5** | A design flaw reaches the GD immediately, from any step and whatever the status says |
| **I6** | An accepted gap is written down before closure — step 1 of closing, above |
| **I8** | Every cap composes into a stop, never another round — the router's own Rules restate it |
| **I9** | A lock is reclaimed by the stated procedure, never silently |
| **I1** | The four values travel with every dispatch — and where they come from with no ledger is the section above |

## What a direct lane must not produce

`effort-allocation.md`'s artifact budget is a hard limit on this lane, not a style note: **A1/A2 work
produces no plan document, no acceptance contract, no traceability table, no risk review, no self-score and
no report longer than the change.** A high tier on a direct-lane input buys verification and evidence — never
paperwork, never a checkpoint, never a second agent.

**The attempt budget applies here too** — the same 2/3/4/5 from D as the table above, a ceiling and never a
target. Two failures from the same cause force a change of method rather than a third variation of it, and an exhausted budget
produces a **Continuation Debt Record** in the reply to the GD, stated as unfinished work with its resume
point. Never folded into a summary that reads as closure.

**A bug in something the direct lane built is more direct work, not an E3 defect.** `feature-development.md`
**E3** measures a submission against an approved spec and counts strikes against it; with no such spec there
is nothing to measure and nobody to charge. Fixing it costs what building it cost.

### The one case where depth genuinely is a second agent

"Never a second agent" holds for **process**. It does not hold for a **measurement**. A performance claim at
V3 or V4 needs `performance-qa-engineer`, which no direct lane and neither review gate can reach, and
`effort-allocation.md` is explicit that self-review is not independent verification and that performance
caps low when a required measurable claim was never measured.

So where a direct-lane or mode-3 change owes a measured claim, **the measurement is its own ask to the GD** —
`qa-pipeline.md` **E4** — and a decline is recorded as a gap like any other. What it is never is a number
quoted from the agent that made the change.

## Mode 3 — the one dispatch with no entry-inputs table

Every pipeline door names what it carries and what the agent does absent each value. A named-agent dispatch
has no such row anywhere, so **the agent's own required-input table is the contract**: read it before
dispatching and supply what it names.

**A `Blocked` on a mode-3 dispatch is the router's omission, not the GD's** — they named an agent, not a
brief. Repetition is bounded by `loop-termination.md`'s two identical `Blocked` returns, after which the
missing input is itself the finding.

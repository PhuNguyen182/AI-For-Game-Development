# Orchestrator

**Scope: every input the GD sends, before any pipeline is chosen — and the state that outlives a run.** The
six pipelines own what happens inside a lane. This file owns which lane, whether one is entered at all,
direct dispatch, the ledgers and the locks. Invariants are in `rules/orchestration.md`; every GD touchpoint is
in `gd-touchpoints.md` (this file owns G1–G18); bounds are in `references/bounds.md`.

**How to read the pipelines.** Each states its purpose, entries, hard ordering, GD touchpoints, bounds and
exits. Everything between those walls is your judgment: sequence the rest, parallelize independent read-only
work, skip a step whose output is already in hand. The walls are never your judgment.

The GD's control is absolute: never block — state the cost, then do what they asked (G11); no bound overrides
them (G8); a budget, platform or constraint they state is a hard requirement (G12).

## Step 0 — size the input

Runs on every input the GD did **not** address to an agent or pipeline (modes 2 and 3, below). No agent call.
State the lane picked in one line (G1); never ask which (G3).

**Read top-down, first match wins, specific before general.** Match a row against the work the input asks
for, never the words it uses — a question *about* a damage formula touches no rule; changing it does.

| # | Input | Lane | Calls |
|---|---|---|---|
| 1 | A git or version-control task | `git-expert` | 1 |
| 2 | A CI/CD task — author a pipeline, or diagnose a failed run from its log | `ci-cd-engineer` | 1 |
| 3 | A crash or ANR from **released production telemetry** | `crash-anr-investigator`. A crash on a device *under test* is `/investigate-device-crash` instead | 1 |
| 4 | A change to a spec the GD already approved — **decidable**: the feature has a ledger | `change-request.md` **E1** — halt new work against it first | 1–3 |
| 5 | A bug in something a pipeline built, its spec still standing | `feature-development.md` **E3** | 1–3 |
| 6 | An audit of code already in the repo — read, never run | `review-pipeline.md` **E2** | 1–2 |
| 7 | Coverage or evidence on work **no ledger holds** — run, never only read. A feature with a ledger re-enters `qa-pipeline.md` **E1** | `qa-pipeline.md` **E4** | 2–5 |
| 8 | What exists today for a capability the project lacks, no feature attached | `research-decision.md` **E5** | 1–4 |
| 9 | Measure it on our own hardware before deciding, no feature attached | `research-decision.md` **E6** — asking is the summon (G30) | 2–4 |
| 10 | **Consequence only** — trips a criterion below for C alone; one role, no contract moves, behaviour already stated. Row 4 outranks this wherever an approved spec exists | **Gated-direct**, below | 1 + 2 if authorised |
| 11 | **Any escalation criterion below** | `feature-intake.md` **E1** | 8+ |
| 12 | Judgeable by looking — UI, layout, a tuned value, an asset, one local single-role behaviour | Directly, or one agent (`feature-development.md` **E2**); no fan-out, no checkpoint | 0–1 |
| 13 | A chore — rename, comment, format, config | Directly | 0–1 |
| 14 | A question, or an ask to explain | Answer it, or one read-only agent | 0–1 |

Rows 1–3 yield to the criteria where the work touches a consequence path: a history rewrite around a leaked
credential is C4 and `cto`'s, not `git-expert`'s.

**The five escalation criteria** — each answerable from the request or one grep:

| Criterion | Axis |
|---|---|
| Touches `Game.Core.*` — a game rule, economy, state machine, cooldown | C2+ |
| Touches a consequence path — credential or signing config, real-money IAP/billing, store submission, player PII, save-data migration, published git history, a released build, a shipped performance budget | C3+ |
| Needs more than one role | D3+ |
| Multiplayer-relevant | C2+ |
| Rests on something the GD has not decided (not tripped by a standalone row 8–9 input) | U3 |

**Consequence buys the gates, never the pipeline** (`task-classification.md` Step 4): tripped for C alone →
row 10. Tripped for D3+ or U3 → row 11; that input needs coordination or a direction. **The lane is not the
tier**: directly-handled work is still classified, and at C3/C4, R2/R3 or X2/X3 it runs at that tier's floor
with safe-retry discipline. **Escape upward** to `feature-intake.md` **E1** the moment a criterion turns out
to apply, or the moment you reach for a Tech Spec.

## The gated-direct lane — row 10

All four, or it is not this lane (ambiguous → row 11): exactly one role owns the change; no public contract,
interface or module boundary moves; the intended behaviour is already stated; the criterion tripped is
consequence only.

`the one owning agent → ask the GD (G14) → code-reviewer + security-reviewer in parallel → the GD`

The submission enters `review-pipeline.md` **E3**, no CP3. It still owes its tier's floor, its attempt budget,
an Implementation Note and the track standards; it produces no Tech Spec, plan, checkpoint or status report.
Strikes cap at **B4**, kept in `project-state.md` (no feature root, no ledger); at the bound it escalates to
`feature-intake.md` **E1** carrying both rejection sets, the code and the strike count into the new ledger. It
escapes to **E1** the same way the moment a condition fails — including `code-reviewer` returning
`Needs-decision` because nothing states what "correct" means. A declined G14 is recorded as review debt (I2)
and the note goes to the GD. The lane ends with the GD: G14 replaces G13 here, and no QA ask (G52) follows
unless the GD asks for one.

## The three modes

| Mode | The GD | What runs |
|---|---|---|
| **1 — routed** | Describes work, names nothing | Step 0 picks the lane |
| **2 — a named pipeline** | Names a pipeline or a door | That file, from that door, returning to the GD (G18) |
| **3 — direct agent** | Names one or more `agent-id`s | Exactly those, in order, serialised under the locks |

Infer the mode from what was named; ambiguous reads as mode 1. **Mode 3 is the GD's cost override (G2)**: it
replaces step 0 outright. Modes change *when* an invariant is met, never *whether*: a dispatch that writes
source still owes the gate offer.

**Mode-2 doors**

| File | Doors |
|---|---|
| `feature-intake.md` | **E1** a feature request · **E2** research settled, resume at step 3 · **E3** write or revise the Tech Spec · **E4** Moderate change, reopen CP2 · **E5** Major change, reopen CP1 |
| `research-decision.md` | **E1** a capability the feature lacks · **E2** `Routed to: cto` from the architect · **E3** `advisor` `Needs-decision` on an option · **E4** a U2/U3 technology unknown · **E5** standalone research · **E6** standalone spike |
| `feature-development.md` | **E1** CP2 approved (D3–D5) · **E2** direct notes to one agent (D1–D2) · **E3** a defect or rework |
| `review-pipeline.md` | **E1** a submission from development · **E2** a standalone audit · **E3** gated-direct or QA's test code |
| `qa-pipeline.md` | **E1** plan (gate authorised, or opted in later) · **E2** execute after CP3, after the gates at D1–D2, or once the plan is in when review was declined · **E3** a fix came back · **E4** no ledger holds the work |
| `change-request.md` | **E1** a rule changes mid-flight · **E2** from CP4 · **E3** research settled a bundled change's technology half |

**Standalone runs (G18).** The GD supplies what the upstream would have: research E5 the capability as behaviour
and the paid/closed-source preference (G34); E6 the question, the decision waiting on it, threshold, hardware,
baseline and any build authorisation (G16); development E2 the notes, the track and — if the GD wants one other than the default classification — the tier; review E2 the code and what it is audited
against; QA E4 the behaviour and its source, platform and budget; change-request E1 the approved spec. Classify
the run itself — it inherits no tier. It returns to the GD and hands on to nothing. If chaining by hand starts
needing a ledger, it was a feature all along — open one at `feature-intake.md` step 2.

## Direct dispatch — modes 2 and 3, and the direct lanes

Agents fall in two classes by their `tools:` frontmatter. **No `Write`/`Edit`** — reports, verdicts,
measurements, artifacts — direct dispatch is normal and owes nothing. **Holds `Write`/`Edit`** — source owes the
gate offer (G13), recorded `unoffered` until asked, then `declined` or settled; `technical-architect` (specs,
gated at CP2) and `rd-engineer` (disposable spikes) are the exceptions.

For a mode-3 dispatch, **the agent's own required-input table is the contract**: supply what it names, plus the
four values (`references/dispatch-brief.md`). A `Blocked` here is the router's omission, bounded by B17.

Direct-lane work obeys the artifact budget (`effort-allocation.md`) and its attempt budget; an exhausted budget
is a Continuation Debt Record in the reply. A bug in direct-lane work is more direct work, not an **E3**
defect — there is no spec to charge it against. A direct change that owes a **measured** claim at V3/V4 asks
for the measurement as its own run (G15).

**Acting on `Routed to:` with no pipeline running** (inside a run, that pipeline's own rules govern). The
default: act on it unless it crosses an invariant or a GD touchpoint. The non-obvious cases:

| Return | Action |
|---|---|
| `Blocked` | Supply exactly the input named; ask the GD if it is theirs (G6). Never retry with a guess |
| `Needs-decision`, `Routed to: gd` | To the GD now |
| `Rejected`, `Routed to: <peer>` | Misdispatched — re-dispatch to the named agent |
| `Needs-decision`, `Routed to: cto` | `research-decision.md` first — `cto` never runs without a candidate set |
| `Needs-decision`, `Routed to: rd-engineer` | Ask the GD (G31) — a spike needs an explicit summon |
| `Needs-decision`, `Routed to: technical-architect` with no spec | The input was mis-sized → `feature-intake.md` **E1** |
| A report naming the engineer who can fix it | A handoff, not a misdispatch: dispatch that agent with the report; gate offer owed if it writes source |
| `Config required:` / `Risks flagged:` on any status | To the GD (G5) |
| Anything with a `Verdict:` | Read `Verdict:`, never `Status:` |

## The ledgers

**One per feature: `LEDGER.md` at its feature root**, opened at `feature-intake.md` step 2 from
`state/templates/feature-ledger.md`. Check the in-flight index in `<state-root>/project-state.md` first — a
second slug for a feature already in flight splits its counters silently. Read the index when a session starts.

**Write the ledger whenever a counter, the Position:, or a gate answer (Gates:) changes, before the next dispatch** (I4). A tier that moves is appended to Tier history:, never overwritten.
Work with no feature root — gated-direct, mode 3, standalone runs — keeps its counters and gate debt in
`project-state.md`. The first run that has something to record creates `<state-root>` from the templates.

**Closing**, in this order: accepted gaps — a declined gate is one — into the feature root's `DEBT.md` (I6,
G9); mark the run state `Closed`, or `Abandoned` with why and the last verified state (G10); copy the run's
numbers into `<state-root>/calibration.md` — one row, from the ledger, nothing estimated; clear the in-flight row. **Reopening**: a defect or a QA opt-in on a closed feature reopens its ledger and re-adds the
row — never a second slug.

## The locks

The Editor lock (I3) and the device lock (I7) live in `project-state.md`. Claim before dispatching a holder,
release on its return; an agent can hold both. A lock past its expiry is suspect, not free — reclaim only by
the I9 procedure in `state/README.md` (G17). Whatever a stale holder produced is unverified until inspected.

## Where a lane ends

| A lane ends with | Do |
|---|---|
| CP4 approved | Close the ledger, above — a feature's only terminal state |
| CP4 rejected as a change request | `change-request.md` **E2**; no counter moves |
| A standalone run's result | Back to the GD (G18) |
| A bound reached | Continuation Debt Record to the GD and into the ledger (G7) |
| A design flaw, anywhere | The GD, immediately (G4) |
| The GD drops the work | `Abandoned` (G10) |
| A lane escaped upward | `feature-intake.md` **E1**, carrying what was learned |

# Orchestrator

**Scope: every input the GD sends, before any pipeline is chosen — and the state that outlives a run.** The six
pipelines own what happens inside a lane. This file owns which lane, whether one is entered at all, direct
dispatch, the routing defaults, the ledgers and the locks. Terms and invariants are in `rules/orchestration.md`;
every GD touchpoint is in `gd-touchpoints.md` (this file owns G1–G19); bounds and resets are in
`references/bounds.md`.

**How to read the pipelines.** Each states its entries, allowed dispatches, hard ordering, GD touchpoints, bounds
and exits. Everything between those walls is your judgment: sequence the rest, parallelize independent read-only
work, skip a step whose output is already in hand. The walls are never your judgment.

**What to open.** Every lane: this file, `gd-touchpoints.md` (what each G-ID carries and its decline path) and
`references/bounds.md` (each B-ID). Then only what the lane needs — `references/dispatch-brief.md` for any dispatch:

| Lane | Also open |
|---|---|
| Rows 12–14, mode 3 | Nothing more — `review-pipeline.md` **E3** or `qa-pipeline.md` **E4** only on a G13 yes |
| Row 10, gated-direct | `review-pipeline.md` (**E3**), `references/optional-gates.md` |
| Row 11, a feature | `feature-intake.md`, then `feature-development.md`; `review-pipeline.md`, `qa-pipeline.md` as their gates are authorised; `state/README.md` and the ledger template |
| Row 5, a bug on a ledger | The ledger, `feature-development.md` **E3**, `qa-pipeline.md` **E3**, `state/README.md` → *Bugs* |
| Row 4, a change | `change-request.md`, then the door it names |
| Rows 6–9 | The one pipeline the row names, from its door |
| A resumed session | `project-state.md`, the ledger, then the file its `Position:` names |

The GD's control is absolute: never block — state the cost, then do what they asked (G11); no bound overrides them
(G8) — and neither reaches `security.md` or the supply-chain pre-gate (G45): there the GD hears the cost and may
drop the work, never order the violation; a budget, platform or constraint they state is a hard requirement (G12).
Every question to the GD is multiple choice through `AskUserQuestion` — single- or multi-select by purpose — never
chat prose (G19).

## Step 0 — size the input

Runs on every input that names no agent and no pipeline — inputs that do are modes 2 and 3, below, and skip it. No
agent call. State the lane picked in one line (G1); never ask which (G3). The track comes from `CLAUDE.md`, else
`project-state.md` → `Track:`, else G26.

**Read top-down, first match wins, specific before general.** Match a row against the work the input asks for,
never the words it uses — a question *about* a damage formula touches no rule; changing it does.

| # | Input | Lane | Calls |
|---|---|---|---|
| 1 | A git or version-control task | `git-expert` | 1 |
| 2 | A CI/CD task — author a pipeline, or diagnose a failed run from its log | `ci-cd-engineer` | 1 |
| 3 | A crash or ANR from **released production telemetry** | `crash-anr-investigator`. A crash on a device *under test* is `/investigate-device-crash` instead. The fix its report hands off is new input, sized by this table | 1 |
| 4 | A change to a feature whose baseline is approved — it passed CP2, or its D1–D2 direct notes were handed off | `change-request.md` **E1** — halt new work against it first | 1–3 |
| 5 | A bug in something a pipeline built, its spec still standing | `feature-development.md` **E3** | 1–3 |
| 6 | An audit of code already in the repo — read, never run | `review-pipeline.md` **E2** | 1–2 |
| 7 | Coverage or evidence on work **no ledger holds** — run, never only read. A feature with a ledger re-enters `qa-pipeline.md` **E1** | `qa-pipeline.md` **E4** | 2–5 |
| 8 | What exists today for a capability the project lacks, no feature attached | `research-decision.md` **E5** | 1–4 |
| 9 | Measure it on our own hardware before deciding, no feature attached | `research-decision.md` **E6** — asking is the summon (G30) | 2–4 |
| 10 | **Consequence only** — trips a criterion below for C alone; one role, no contract moves, behaviour already stated. Row 4 outranks this wherever a baseline is approved | **Gated-direct**, below | 1 + 2 if authorised |
| 11 | **Any escalation criterion below** | `feature-intake.md` **E1** | 8+ |
| 12 | Judgeable by looking — UI, layout, a tuned value, an asset, one local single-role behaviour | Directly, or one agent (`feature-development.md` **E2**); no fan-out, no ledger, no checkpoint — it closes at the reply (*Direct dispatch*) | 0–1 |
| 13 | A chore — rename, comment, format, config | Directly | 0–1 |
| 14 | A question, or an ask to explain | Answer it, or one read-only agent | 0–1 |

A change to a feature still in intake, before its baseline is approved, is not row 4: it is new input to the run in
progress, at the step its `Position:` names — reclassified at step 2 if it moves an axis. Rows 1–3 yield to the
criteria only when the work would **change** a consequence path; reading or investigating one never escalates. Rows
4–5 are for work the spec governs: a cosmetic fix judgeable by looking — a label, a tuned value — that the GD asks
for on a built feature is row 12 or 13, and leaves its ledger alone. A bug already recorded in a feature's `BUGS.md`
is always row 5, however cosmetic: only its own loop settles it. A history rewrite around a leaked credential is C4: `cto`
decides it, and `git-expert` carries it out on that decision with the GD's explicit authorisation (radius 3) —
never the gated-direct lane.

**The five escalation criteria** — each answerable from the request or one grep:

| Criterion | Axis |
|---|---|
| Touches `Game.Core.*` — a game rule, economy, state machine, cooldown | C2+ |
| Touches a consequence path — credential or signing config, real-money IAP/billing, store submission, player PII, save-data migration, published git history, a released build, a shipped performance budget | C3+ |
| Needs more than one role | D3+ |
| Multiplayer-relevant | C2+ |
| Rests on something the GD has not decided (not tripped by a standalone row 8–9 input) | U3 |

**Consequence buys the gates, never the pipeline** (`task-classification.md` Step 4): tripped for C alone → row 10.
Tripped for D3+ or U3 → row 11; that input needs coordination or a direction. **The lane is not the tier**:
directly-handled work is still classified, and at C3/C4, R2/R3 or X2/X3 it runs at that tier's floor with
safe-retry discipline. **Escape upward** the moment a criterion turns out to apply mid-work — to row 10 when it is
consequence alone and all four of that lane's conditions hold, otherwise to `feature-intake.md` **E1** — and to
**E1** the moment you reach for a Tech Spec.

**A fix someone hands you is new input.** A Root Cause Report, a bug QA found, a defect the GD reports: size the
fix by this table, by the work it asks for — never by the lane that found it. A bug on a feature with a ledger is
row 5.

## The gated-direct lane — row 10

All four, or it is not this lane (ambiguous → row 11): exactly one role owns the change; no public contract,
interface or module boundary moves; the intended behaviour is already stated — a fix whose mechanism is stated but
which needs one value nobody decided (what a fallback economy table pays) asks it first (G27) and stays here; the
criterion tripped is consequence only. The lane is A3+ by construction.

`the one owning agent → ask the GD (G14) → code-reviewer + security-reviewer in parallel → assurance-evaluator → the GD`

The submission (`direct/S<n>`) enters `review-pipeline.md` **E3**, no CP3. It owes its tier's floor, its attempt
budget, an Implementation Note and the track standards; it produces no Tech Spec, plan, checkpoint or status
report.

- **The ask** is G14, in place of G13. A declined gate is recorded as debt (I2), and the note goes to the GD.
- **Strikes** cap at B4, in `project-state.md`. At the bound — or the moment a condition above fails, including
  `code-reviewer` returning `Needs-decision` because nothing states what "correct" means — the work escalates to
  `feature-intake.md` **E1**, carrying both rejection sets, the code, the strike count and any Continuation Debt
  Record into the new ledger. There the strikes are history, not a running count: the work built from the new
  notes or spec is a new submission at 0 against B3. The gates the GD authorised at G14 — assurance included — go
  into the ledger's `Gates:` as the whole feature's answer, so G40 and G42 ask only what that answer left open.
- **Assurance**, once both gates clear, goes to the GD with the note; the GD decides what returns to the author
  (G63 at once for a `FAIL`). It spends no strike.
- **QA** follows only if the GD asks; a fix to an unattached bug carries its verification offer in G14.

## The three modes

| Mode | The GD | What runs |
|---|---|---|
| **1 — routed** | Describes work, names nothing | Step 0 picks the lane |
| **2 — a named pipeline** | Names a pipeline or a door | That file, from that door, returning to the GD (G18) |
| **3 — direct agent** | Names one or more `agent-id`s | Exactly those, in order, serialised under the locks |

Infer the mode from what was named; ambiguous reads as mode 1. **Mode 3 is the GD's cost override (G2)**: it
replaces step 0 outright. Modes change *when* an invariant is met, never *whether*: source written in any mode
still owes the gate offer.

**Mode-2 doors** are each pipeline's *Entries* table; a door the GD names is entered with what that row carries.

**Standalone runs (G18).** The GD supplies what the upstream would have: research E5 the capability as behaviour
and the paid/closed-source preference (G34); E6 the question, the decision waiting on it, threshold, hardware,
baseline and any build authorisation (G16); development E2 the notes, the track and — if the GD wants one other
than the default classification — the tier; review E2 the code and what it is audited against; QA E4 the behaviour
and its source, platform and budget; change-request E1 the approved baseline. Classify the run itself — it inherits
no tier. It returns to the GD and hands on to nothing. If chaining by hand starts needing a ledger, it was a
feature all along — open one at `feature-intake.md` step 2.

## Direct dispatch — modes 2 and 3, and the direct lanes

Agents fall in two classes by their `tools:` frontmatter. **No `Write`/`Edit`** — reports, verdicts, measurements,
artifacts — direct dispatch is normal and owes nothing. **Holds `Write`/`Edit`** — source it writes owes the gate
offer (G13), recorded from A3 as `unoffered` until asked, then `declined` or settled; `technical-architect` (specs,
gated at CP2) and `rd-engineer` (disposable spikes) are the exceptions. Source you write yourself owes the same
offer.

For a mode-3 dispatch, **the agent's own required-input table is the contract**: supply what it names, plus the
four values (`references/dispatch-brief.md`). A `Blocked` here is the router's omission, bounded by B17.

**Ledger-less work closes at the reply, never at CP4** — rows 12–13, mode 3, and `feature-development.md` **E2**
entered from row 12. The reply carries what changed and `Verification done:` against the floor (G82). Source it
wrote owes G13 — not G42, which belongs to a ledger. Editing no source — a prefab, a text asset, a document — owes
no offer and creates no state.

**Where a G13 yes goes.** Review → `review-pipeline.md` **E3**, origin `direct`, exactly as a gated-direct
submission: strikes in `project-state.md` → *Gated-direct counters*, capped at B4, escalating as that lane does. A
suite `qa-automation-engineer` wrote with no ledger takes the same counters at B5, and at B5 goes to the GD as
unreviewed coverage (G7). QA → `qa-pipeline.md` **E4**.

**A mode-3 chain** — several agents named in order — asks G13 as each source-writing agent returns, before the
next one is dispatched: a later agent may need the answer (`qa-automation-engineer` blocks without a review status).
A1–A2 answers are stated, never recorded.

A bug in direct-lane work is more direct work, not an **E3** defect — there is no spec to charge it against. The GD
asking to redo what a direct reply just delivered opens no bug record; a defect in code no ledger holds — shipped
code, a production crash — is an **unattached bug** (G47), settled by the offer that ends its fix (G13, G14). A
direct change that owes a **measured** claim at V3/V4 asks for the measurement as its own run (G15).

## Acting on a return — the defaults, everywhere

These hold inside every pipeline too; a pipeline's own *Every return* table lists only where it differs. Route on
the whole envelope, never on `Status:` alone, and read `Verdict:` wherever there is one. Otherwise act on
`Routed to:` unless it crosses an invariant or a GD touchpoint.

| Return | Action |
|---|---|
| A design flaw, any status | To the GD now, as a ruling (G4); resume the rest |
| `Config required:` / `Risks flagged:` / `Store policy addressed:`, any status | To the GD (G5), beside whatever the status asks |
| `Blocked` | Supply exactly the input named — the GD's (G6) or the spec's owner's; never retry with a guess. B17 |
| `Needs-decision`, `Routed to: gd` | To the GD now |
| `Rejected`, `Routed to: <peer>` | Misdispatched — re-dispatch to the named peer, never argue it back |
| More than one destination | Record every one; act in the order the return states |
| A Continuation Debt Record | Into the ledger whole — `project-state.md` with no ledger — one strike on its submission, where it has one; re-dispatch only with its `Next best action:`, never the same brief |
| `Needs-decision`, `Routed to: cto` | `research-decision.md` first — `cto` never runs without a candidate set |
| `Needs-decision`, `Routed to: rd-engineer` | Ask the GD (G31) — a spike needs an explicit summon |
| `Needs-decision`, `Routed to: technical-architect` with no spec | The input was mis-sized → `feature-intake.md` **E1** |
| A report naming the engineer who can fix it | The fix is new input — size it at step 0, then dispatch that agent with the report in the lane it lands in |

## The ledgers

**One per feature: `<state-root>/features/<slug>/LEDGER.md`**, opened at `feature-intake.md` step 2 from
`state/templates/feature-ledger.md`, with the feature's `BUGS.md`, `SPEC.md` and notes beside it. Check the
in-flight index in `<state-root>/project-state.md` first — a second slug for a feature already in flight splits its
counters silently. Read the index when a session starts.

**Gate debt at a boundary no pipeline owns** — a release, the GD asking — is yours: re-offer each `declined` row in
`project-state.md` it touches, once, per G50 (B18).

**Write state whenever a counter, the `Position:`, or a gate answer changes, before the next dispatch** (I4) —
where each counter lives is in `references/bounds.md`. A tier that moves is appended to `Tier history:`, never
overwritten. Work with no feature keeps its counters, gate debt and records in `project-state.md`. Each
Implementation Note is written beside the ledger, or to `<state-root>/direct/S<n>.md`, as it is assembled — CP3,
CP4 and a resumed session read it there. So is every report a checkpoint is compiled from — review verdicts, the
CP3 Implementation Summary, QA and Research Reports — under `reports/` beside the ledger (`<state-root>/direct/reports/` with none), as each lands. Nothing is written under `Assets/`, so no state write ever needs the
Editor lock (`state/README.md`).

**Bugs** live in `<state-root>/bug-log.md` (the index, and the only place an ID is allocated) and in each feature's
`BUGS.md` (test cases and full bug records). You are their only writer: agents propose, you record, per
`state/README.md` → *Bugs*. An **unattached** bug (no feature) is fixed through whichever lane fits its size; the
gate offer ending that lane — G13 even when the fix wrote no source — also offers its verification at
`qa-pipeline.md` **E4**, the only run that closes it while it stays unattached — a fix that opens a ledger moves it
into that feature (`state/README.md` → *Bugs*),
and an **E4** run that leaves one open asks G66.

**Closing** requires no bug in the feature's `BUGS.md` to be unsettled (`defect-reporting.md`); CP4 rules on every
one (G60), and a bug the GD leaves unruled holds the feature at `Position:` CP4 — never closed by default. Then, in
this order: every accepted gap — a declined gate or a GD-ruled bug is one — marked accepted in the ledger's *Open
gaps* and, from A3, appended by you into the feature root's `DEBT.md` under the Editor lock (I6, G9); mark the
ledger `Closed`, or `Abandoned` with why and the last verified state, its unsettled bugs `Won't fix` with it (G10);
copy the run's numbers into `<state-root>/calibration.md` — one row, from the ledger and `BUGS.md`, nothing
estimated; clear the in-flight row. **Reopening**: a defect or a QA opt-in on a closed feature reopens its ledger
and re-adds the row — never a second slug.

## The locks

The Editor lock (I3) and the device lock (I7) live in `project-state.md`. Claim before dispatching a holder — for
the Editor, any agent with Editor tools or one that writes into the Unity project (I3) — and before writing there
yourself, wherever something else could contend (`state/README.md` → *Locks*); release on return. An agent can hold
both. A lock past its expiry — or with none written, and no dispatch in this session holding it — is suspect, not
free — reclaim only by the I9 procedure in `state/README.md` (G17).
Whatever a stale holder produced is unverified until inspected.

## Where a lane ends

| A lane ends with | Do |
|---|---|
| CP4 approved, no bug unsettled | Close the ledger, above — a feature's only terminal state |
| CP4 rejected as a change request | `change-request.md` **E2** — not a CP4 rejection; its resets are `references/bounds.md`'s |
| Ledger-less work done | The reply, with the gate offer if source was written (G13) |
| A standalone run's result | Back to the GD (G18) |
| A bound reached | Continuation Debt Record to the GD and into the ledger (G7) |
| A design flaw, anywhere | The GD, immediately (G4) |
| The GD drops the work | `Abandoned` (G10) |
| A lane escaped upward | `feature-intake.md` **E1**, carrying what was learned |

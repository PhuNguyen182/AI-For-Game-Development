# Feature Intake

Turns a GD feature request into direct notes for one agent (D1–D2) or an approved Tech Spec (D3–D5), and hands it
to `feature-development.md`. Starts at classification, stops at the hand-off. Technology questions branch to
`research-decision.md` and come back here; a change after CP2 re-enters from `change-request.md` at **E4**/**E5**.

## Entries

| Door | Comes from | Resumes at | Carries |
|---|---|---|---|
| **E1** | `orchestrator.md` step 0, or a lane escaped upward (B4: with both rejection sets and the code) | step 1 | The GD's words unedited, the track state, and whatever the escaped lane learned |
| **E2** | `research-decision.md` settled what the loop was waiting on — so D4–D5 or U3 by definition | step 3 | The Research Report, the options already ruled out, the rounds already spent |
| **E3** | Research settled a capability outside the loop; `feature-development.md` found the breakdown names no API; or a Moderate change to a D1–D2 baseline, which has no CP2 to reopen | step 6 at D3–D5 — the spec written and CP2 run for the first time on a grown D1–D2 change · at D1–D2, the architect's direct notes revised — approved by the GD first when a change request sent them (G73) — then the hand-off | Tier and axes, track state, and the Research Report, the gap named, or the change in the GD's words |
| **E4** | `change-request.md` — **Moderate** | CP2 | The revised Tech Spec, the rework list, the reclassified tier and axes |
| **E5** | `change-request.md` — **Major**; or a CP2 rejection naming the direction | step 3, concluding at CP1 | The change in the GD's own words (it stands in for acceptance criteria while those read `Pending CP1`), the options already ruled out, the risks the GD accepted — `none` on a first CP1, a legitimate empty history, never invented — and the rework list |

E2–E5 resume from the ledger and never reclassify from scratch; which axes are re-read on each is in
`references/dispatch-brief.md`.

## May dispatch

| Agent | Returns / owns here |
|---|---|
| `technical-architect` | Step 2: the tier, the five axes, `Open design question:` lines each tagged `design` / `architecture` / `technology`, the feature root — and at D1–D2, where its Self-assessment level is **Direct**, the direct notes themselves. Step 6: the Tech Spec (D3–D5). On the GD's request before CP1 (G23): an engineering recommendation between options |
| `advisor` | **Options** — one `### <Option name>` block each (Precedent, Trade-off, Assumes). Never ranks or recommends |
| `critic` | **Risk Findings** against the option the GD leans toward, ranked by severity. A leaf: routes to nobody. `Done` with no findings is a pass, not a missing result |

`researcher`, `rd-engineer` and `cto` are reached only through `research-decision.md`.

## Hard ordering

1. The GD's words, unedited, and the track state reach step 2 together — `technical-architect` blocks on a summary
   and silently assumes client-only without the track (I1). An unknown track is settled first — asked only when the work
could be multiplayer-relevant and the request does not say (G26), otherwise stated as client-only.
2. Check the in-flight index in `<state-root>/project-state.md` before opening a ledger — a second slug for a
   feature already in flight splits its counters. The ledger exists before step 3 dispatches anything.
3. Classification precedes every other dispatch and never waits on a GD confirmation (G20).
4. `advisor` and `critic` never run in the same round: `critic` needs a direction the GD has picked.
5. Every `technology` line is settled, or its skip named, before step 6 — a spec on a guessed technology is rework.
6. At D4–D5 or U3, CP1 locks before step 6. At D3–D5, CP2 approves before the hand-off.

## Steps

1. **Forward** the request verbatim, with which tracks are active attached (G26 when unknown). Once the ledger
   opens, the request goes into its `Request:` row verbatim — the architect blocks on a summary, and a resumed
   session has nothing else to give it.
2. **Classify.** `technical-architect` returns the A-tier and **each of the five axes separately** — never
   collapsed into one number, since each downstream file reads a different axis. Open
   `<state-root>/features/<slug>/LEDGER.md` from `state/templates/feature-ledger.md`, recording the feature root
   the architect named — the Core root first when the feature spans two — (provisional at U3; if CP1 moves it, the
   ledger moves), and add its row to the in-flight index. State the tier per G1. The shape follows **D**, per
   `task-classification.md` Step 4:
   - **D1–D2** — steps 1 and 2, whose return carries the direct notes, stored where step 6 stores a spec; step 5 if
     a technology line exists — or a `design` line, put to the GD directly (G27) — the architect revising its notes
     on the result; then the hand-off. No Tech Spec, no
     CP1, no CP2; a high tier from C, R or X buys verification downstream, never a step here.
   - **D3** — steps 1, 2, 5, 6. No loop, so a `design` line is put to the GD directly (G27).
   - **D4–D5, or U3 at any D** — every step, CP1 then CP2.

   A `technology` line classified U2/U3 goes to `research-decision.md` **E4** now, before the loop — on the netcode
   foundation, G44 first, once per project.
3. **Advisor⇄Critic loop** (D4–D5 or U3). One round: `advisor` → the GD picks an option **by name** → `critic` on
   that option → the GD decides (G21). Each dispatch carries:
   - `advisor`: every `design` and `architecture` line, verbatim — never a `technology` line, never one line
     standing in for several; the constraints that rule options out (platform, track, genre, monetization, the
     social graph — strangers, or only players who already know each other — and whatever the GD fixed); from round
     2, the options ruled out and why.
   - `critic`: the **whole** option block `advisor` returned for the GD's pick — the pipeline expands the name,
     since `critic` cannot read `advisor`'s return; what the feature must achieve (acceptance criteria or the GDD
     passage); the constraints already accepted.

   Only the GD ends the loop. The round count and the ruled-out list go to the ledger's `Advisor⇄Critic:` row every
   round. The loop offers no engineering ranking on `architecture` lines — the GD can ask for one (G23).
4. **CP1** (G21). The GD locks the direction and the risks they accept; both go to the ledger's *GD decisions*.
   `critic`'s findings CP1 did not settle travel to step 6. Spend U down only for the `design` and `architecture`
   questions CP1 closed — an open `technology` line holds U until step 5 settles it — then update the ledger's
   `Tier:` row and append the move to `Tier history:`.
5. **Research branch.** Route each `Open design question:` line by its tag: `design` → the GD, through the loop, or
   directly at D1–D3 (G27); `architecture` → the loop, or `technical-architect` (G23); `technology` →
   `research-decision.md` **E1**. Skip only when you can **name** the package, API or existing system that already
   covers it — if you cannot name it you are guessing, so branch. A skip goes into the ledger's `Research:` row
   with what was named, and is shown at CP2 (G25).
6. **Tech Spec** (D3–D5). The dispatch carries the four values (`references/dispatch-brief.md`); the locked
   direction and the risks accepted; `critic`'s open findings; and whatever `research-decision.md` handed back —
   the Technical Decision and any `Standard set:`, the Research Report with its `Picture taken:` date, any
   provisional decision's re-open threshold. The spec states, at minimum: acceptance criteria (one per H/M
   requirement), the verification floor as a V-number, every assumption with what breaks if it is wrong, inherited
   `cto` decisions, module boundaries, the client-server contract, a per-`agent-id` task breakdown, and the
   documents owed. A `design` line the spec raises at D3 is put to the GD (G27) before CP2, the spec revised on
   the answer. It is written to `SPEC.md` beside the ledger — direct notes too, at D1–D2 — and the ledger's
   `Spec:` row records its approval; nothing downstream works from a spec it cannot find after a restart.
7. **CP2** (G24). The GD sees the spec with its `Assumptions:`, inherited decisions and `critic`'s open findings,
   plus any research skip (G25). On the **first** rejection, ask which kind it is: the spec misread the request →
   back to step 6, counted against B11; the direction is now wrong → CP1 through **E5**, never a redraft. Write the
   count to the ledger's `Rejections:` row.
8. **Hand off** to `feature-development.md`: D1–D2 at **E2** — the architect's direct notes from step 2, addressed
   to one `agent-id`; D3–D5 at **E1** — the approved spec and its task breakdown. Either way with the four values
   from the ledger and the spec's `Documents owed:`. A checkpoint reopened by a change request (**E4**, **E5**)
   hands off its rework list at **E3** instead — or, with no code against the superseded spec, to the step the
   ledger's `Position:` names (`change-request.md` step 5); the feature never restarts.

**Checkpoints key to D, never to the A-tier.** CP1 and CP2 are this file's; CP3 (G51) fires only when review ran
and merges into CP4 at D1–D2; CP4 (G60) fires at every shape — with both gates declined the feature still closes
there, on the GD's own acceptance, both debts stated.

## GD touchpoints

Where each fires; what it carries and what happens on no are `gd-touchpoints.md`'s alone.

**G26** step 1 · **G20** step 2 · **G44** step 2, a netcode-foundation `technology` line · **G21** steps 3–4 · **G22** step 3, when `advisor` was asked to choose · **G23**
before CP1 locks · **G25**, **G27** step 5 · **G27** step 6 · **G24** step 7 · anywhere: **G4**, **G6**, **G7**, **G9**.

## Bounds

- **B1** — `technical-architect`'s attempt budget, inside each dispatch.
- **B2** — Advisor⇄Critic rounds. Reaching it without a lock stops the loop and reports non-convergence; another
  round only if the GD directs one (G8).
- **B11** — CP2 rejections; the third goes to CP1 if the loop is available at this D, else to the GD.
- **B17** — identical `Blocked` returns on one missing input.

A request that fails classification is a `Blocked`, never a review strike.

## Exits

| Outcome | Control goes to | Ledger |
|---|---|---|
| D1–D2 classified, research settled or skipped | `feature-development.md` **E2** | `Tier:`, `Track:`, `Research:` |
| CP2 approved — reopened by a change request (**E4**/**E5**) | `feature-development.md` **E3** with the rework list, or the interrupted step (step 8) | `Rejections:` CP2 count; superseded decisions in *GD decisions* |
| CP2 approved | `feature-development.md` **E1** | `Rejections:` CP2 count; direction, accepted risks and spec decisions in *GD decisions* |
| A `technology` line needs research | `research-decision.md` **E4** (step 2, U2/U3) or **E1** (step 5); back at **E2** if the loop waits on it, else **E3** | `Research:` on return; `Tier:` recomputed |
| `advisor` → `Needs-decision`, `Routed to: rd-engineer` or `cto` | `research-decision.md` **E3**; back at **E2** | `Advisor⇄Critic:` round and ruled-out list kept |
| `critic` → `Rejected`, `Routed to: gd` — asked to design the fix | The GD; re-enter at step 2 once the direction is settled | — |
| `technical-architect` → `Needs-decision`, `Routed to: cto` from step 2 | `research-decision.md` **E2**; back at **E2** at D4–D5/U3, else **E3** — never step 6 before CP1 | `Research:` on return |
| The same, from step 6 | `research-decision.md` **E2**; back at **E3** | `Research:` on return |
| CP2 rejected as a direction problem, or B11 reached with the loop available | Step 3 via **E5** | `Rejections:`; ruled-out list kept |
| B2 or B11 reached with nowhere left, or B1 exhausted | The GD (G7) — never the same brief re-dispatched | *Continuation debt* |
| A design flaw | The GD (G4) | — |
| The GD drops the request | — (G10) | `Status: Abandoned`, why, last verified state |

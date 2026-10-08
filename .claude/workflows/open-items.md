# Open Items

What is still open about the workflow layer itself — not per-feature state, which is in each `LEDGER.md` and
`<state-root>/project-state.md`. The full authoring history is kept outside the runtime layer, as reference
material; nothing here depends on it. Add a row when something is found; close it with what closed it.

States: `Awaiting GD` — written, not yet reviewed · `Open` — owed · `Deferred` — seen, priced, declined ·
`Recorded` — a fact, not work.

## Awaiting the GD's review

| Item | State |
|---|---|
| **The slimming round** — the layer rewritten as contracts: the GD touchpoint registry (`gd-touchpoints.md`), bounds collapsed into `references/bounds.md`, 29 references folded into 3, the four auto-loaded rules trimmed, the scoring tables moved to `.claude/standards/qa/assurance-scoring.md`, dead state fields removed, the verifier rewritten to integrity checks | Awaiting GD |
| **Behaviour change: gated-direct gates are asked** (G14), not automatic — resolving a conflict between the old lane file and I2 | Awaiting GD |
| **Behaviour change: test-code review timing** (G62, I10) — offered as soon as the suite is written, before its results serve as evidence | Awaiting GD |
| **The scoring rounds** — independent blind scorers, fixes, re-scoring. Behaviour changes, each a GD decision taken on the GD's instruction to reach 85/100: see the list below | Awaiting GD |

**Behaviour changes from the scoring rounds**

- Terms defined once in `rules/orchestration.md`: source (code that builds or runs — not scenes, prefabs, text
  assets), submission (`S<n>`; a fix other than rework of its own rejection is a new one), strike, boundary,
  CP1–CP4. Editing no source owes no gate offer.
- Gates: G40 has two answers (the whole feature, or none now), G42 fires when review was not authorised at G40 —
  declined there, or never asked at D1–D2 — and QA is asked once per feature; the gated-direct lane offers
  `assurance-evaluator` (G14); the assurance-decline wording applies from A3.
- `qa-automation-engineer` reads a three-state review status — passed, declined by the GD, not part of an **E4**
  run — and never routes to `code-reviewer` itself.
- CP4 rules on every unsettled bug, options by status; an approve that leaves one unruled gets one follow-up, then
  the feature waits at CP4. A design flaw is a ruling (G4), not a notice. An **E4** run ending with open bugs asks
  G66.
- Bounds: every reset in one list; every loop has one root-cause reset of its own — nothing is traced across loops;
  an *After reset* value per resettable bound; B15 now stops QA rounds that keep opening new bugs; an unattached
  bug reaching B6 escalates to intake. The assurance gate has no loop: a `FAIL` is the GD's ruling (G63),
  everything else short of `PASS` reaches CP4.
- Tiers: a working-tree scene or prefab edit is R1; an Editor edit to version-controlled assets is X1 — the lock,
  not the tier, prevents collisions. Anyone writing `.cs` takes the Editor lock (I3).
- State: everything the orchestrator writes lives under `<state-root>/features/<slug>/` — ledger, `BUGS.md`,
  `SPEC.md`, notes — outside the Unity project, so no state write needs the Editor lock. The ledger holds the
  request verbatim, the GD's decisions, submissions, open asks, open gaps and whole Continuation Debt Records. The
  feature root's decision document is now `DECISIONS.md`, written by implementers only. Bug records are the truth
  over the index; an interrupted allocation is `Void`.
- Track: asked once per project when unknown (G26). A D3 `design` question is asked directly (G27). A change to a
  feature still in intake is new input to it, not a change request; D1–D2 direct notes are a baseline.
- Waivers: the cost is written into the option the GD selects; only waiving an **H** requirement asks twice.
- Routing defaults live once in `orchestrator.md`; pipelines list only their exceptions.

## Open

| Item | State | What closing it takes |
|---|---|---|
| **The layer has never run against a real Unity project.** No ledger has been instantiated; every constant in `references/bounds.md` was chosen, not measured | Open | Real feature runs, recorded in `<state-root>/calibration.md` at each ledger close. A constant changes only on the GD's decision, proposed with evidence from those runs |
| **No agent may rank an architecture direction.** A `design` question is the GD's; an `architecture` question reaches the same Advisor⇄Critic loop, where nothing ranks options | Open — a philosophy decision | A `Recommended direction:` field on `technical-architect` for `architecture` questions, or accepting the mode-3 escape (G23) as sufficient |
| **Agent-roster proposals** — optional packs, retiring `producer`, renaming `tech-lead-sdk-platform`, the Bash-without-PowerShell side defect | Open — proposed, not executed | The GD's decision. The other side defect — `netcode-engineer` and `server-authoritative-engineer` not citing the client standards — was fixed in the scoring rounds |

## Scenario-simulation rounds — 87.2/100

The rubric rounds below scored the layer by reading it. Three later rounds scored it by running it: five blind
agents per round each acted as the orchestrator on four of ten scripted scenarios (a D3 feature, light work, a
signing change, a reopening bug, a mid-fan-out change request, a device spike, a multiplayer direction loop, mode-3
chains, a resumed session, a production crash), every scenario traced twice, against an eight-dimension rubric.
Means 70.5 → 78.0 → 87.2. The kit and the per-round scores are kept with the review history.

**Behaviour changes from these rounds**, for the GD's review:

- A fix someone hands over — a Root Cause Report, a QA bug, a GD report — is new input, sized at step 0; escape
  upward goes to row 10 when consequence alone tripped. A bug recorded in a feature's `BUGS.md` is always row 5.
- A GD answer holds until the next boundary: "never twice at the same boundary" replaces "never twice in a run",
  and an authorised gate is never asked again (G42, G50, G74). A defect fix on declined code re-offers review once
  (G42, B18); a boundary no pipeline owns (a release, the GD asking) is the orchestrator's.
- Direct and mode-3 source has a review door (review **E3**, origin `direct`, B4 counters); a mode-3 chain asks
  G13 as each source-writing agent returns. The GD redoing a direct reply opens no bug; an unattached bug whose
  fix opens a ledger moves into its `BUGS.md`.
- A `design` question where no loop runs is G27 everywhere — D1–D3 intake, a change request's classification, a
  gated-direct fix needing one undecided value. The loop's options carry no `(Khuyến nghị)`; "pick for me" offers
  G23 as a choice (G22). G7 is an ask whose options fit where the loop stopped.
- B4 escalation: strikes become history, the new work starts at 0 against B3, and G14's answers — assurance
  included, a new `Gates:` slot — carry into the ledger. Change-request rework is a new submission; parts that
  rework the same code share one severity; a return landing after a halt is held.
- Locks: one with no expiry is suspect; one this session did not claim is another session's, released only by the
  GD (G17). Reports a checkpoint compiles from are written under `reports/`. A spike harness is reverted before
  `cto` decides; `rd-engineer` installs and measures the spike build. Signing configuration is
  `tech-lead-sdk-platform`'s. "Track" has one meaning (`rules/orchestration.md` → *Terms*).

**Round 3's Low findings — recorded, not fixed**

| Finding | Where |
|---|---|
| G7 at the B2 cap: which option "lock" names after three rounds, and whether a recommendation may be marked | `gd-touchpoints.md` G7, G19 |
| A mode-3 Editor holder with no `project-state.md` runs with no written claim, so state shows a contending holder nothing | `state/README.md` → *Locks* |
| The row-10 brief for an unattached bug's fix is missing from the "carry the bug ID" list; `Fixes:` comes from "on **E3**" | `references/dispatch-brief.md` |
| No path for unrecorded source the stale-holder inspection finds, nor when that inspection runs relative to CP3 | `state/README.md` → *Locks*; `orchestrator.md` → *The locks* |
| The change-request classification brief does not carry *GD decisions*, which the Major criterion needs | `change-request.md` **E1**, step 2 |
| G31 collects build authorisation but not the configuration (architecture, signing) `build-run-engineer` blocks without | `gd-touchpoints.md` G31 |
| G74 and G52 can both own the feature's first QA ask on rework mid-fan-out | `gd-touchpoints.md` G52, G74 |
| `Position: CP<n>` names no file to open on resume; U3's definition overlaps a D3 `design` line (G27 vs the loop) | `feature-ledger.md`; `task-classification.md` |
| The D3 shape lists steps 1, 2, 5, 6 — CP2 and hand-off implied; a re-closed feature's calibration row: update or append | `feature-intake.md` step 2; `calibration.md` |

## Findings of the fifth scoring round — recorded, partly closed

Two blind scorers put the layer at 67.75 and 69 (about 68). Duplicates between them are merged; severity is the
higher of the two. Rows marked **Closed** were fixed by the scenario rounds; the rest are not re-verified.

| Severity | Finding | Where |
|---|---|---|
| High | Assurance acceptance states (`FAIL`…`EXCEPTIONAL PASS`) and its `S0–S4` scale are defined nowhere — no score-to-state mapping — yet the QA pipeline routes on them; `S1` also collides with a submission ID | `agents/assurance-evaluator.md`; `standards/qa/assurance-scoring.md`; `qa-pipeline.md` step 4b |
| High — **Closed** (B18 lists the end of implementation; rule 4 is per boundary) | A G40 decline makes G42 offer review again in the same run, against bounds rule 4 and G50's "never twice in a run"; end of implementation is not on B18's boundary list | `gd-touchpoints.md` G40, G42; `references/bounds.md` |
| High | A G42 "yes" to QA at D3–D5 has no route to `qa-pipeline.md` **E1**, so CP3 approval reaches **E2** with no plan | `review-pipeline.md` step 6, exits; `qa-pipeline.md` entries |
| Medium | A GD-reported cosmetic bug in a built feature has three answers — G47 (bug, **E3**), the row 12–13 carve-out, and "a defect on a closed feature reopens its ledger" | `gd-touchpoints.md` G47; `orchestrator.md` step 0, *The ledgers* |
| Medium | Step 0 says "first match wins", but rows 4–5 sit above row 12 and are overridden only by prose below the table; "a tuned value" in `Game.Core` fits rows 4, 10 and 12 | `orchestrator.md` step 0 |
| Medium | `Needs-decision` and `Rejected, Routed to: <peer>` round trips move no counter, so architect↔reviewer or peer↔peer ping-pong is unbounded | `references/bounds.md` rule 1; `orchestrator.md` defaults |
| Medium — **Closed** (`reports/`) | QA reports, the Research Report and the CP3 summary are never persisted, so CP4 cannot be compiled after a restart | `state/README.md`; `qa-pipeline.md` step 5 |
| Medium | A D3–D5 feature with no Core task never meets G40, so no review decision exists before its submissions land | `feature-development.md` step 3; G40, G42 |
| Medium | The gated-direct lane never offers QA, though `optional-gates.md` says a declined review moves the QA question rather than dropping it | `orchestrator.md` gated-direct; G14 |
| Medium | Any `.cs` chore — a comment fix — owes a G13 question carrying tier and axes, against "at A1/A2, say nothing" | `rules/orchestration.md` *Terms*; G13; `task-classification.md` |
| Medium | Calibration undercounts: strikes and rejection counters reset (B10, change requests) with no history kept, so the ledger cannot show what a feature actually spent | `state/templates/calibration.md`; `feature-ledger.md` |
| Medium | Evidence on a `Won't fix` bug is promised to "the next CP4", but CP4 asks only about unsettled bugs and unattached bugs have no CP4; an unattached A1–A2 `Fixed` bug whose verification was declined is never recorded | `defect-reporting.md`; G60; G13 |
| Low | Continuation debt for ledger-less work: the reply (`execution-loop.md`) or `project-state.md` (orchestrator, template) | `rules/execution-loop.md`; `orchestrator.md` defaults |
| Low — **Closed** | `bug-log.md`'s `Record` column still points at `<feature-root>/BUGS.md` | `state/templates/bug-log.md` |
| Low | No brief and no agent trigger for the B12/B13 root cause; only B3 and B6 have one | `agents/technical-architect.md`; `references/dispatch-brief.md` |
| Low | B7 is scoped per `cto` decision, but the ledger holds one `Measure-and-confirm:` for the whole feature | `references/bounds.md` B7; `feature-ledger.md` |
| Low — moving an escalated unattached bug **Closed** (`state/README.md` → *Bugs*) | `TC-##` and `direct/S<n>` have no allocator or race rule; an unattached bug escalated to intake has no rule for moving its record into the new `BUGS.md` | `state/README.md`; `feature-bugs.md` |
| Low | Classification at intake step 2: I1 has the tier travel with every dispatch, while the architect is the one producing it | `rules/orchestration.md` I1; `references/dispatch-brief.md` |
| Low | Step numbers do not follow firing order — G52 (review step 6) fires before CP3 (step 5); the D3 shape lists steps 1, 2, 5, 6 but CP2 is step 7 | `review-pipeline.md`; `feature-intake.md` |
| Low | The orchestrator appends accepted gaps to `DEBT.md` at closure, while the standard says entries come only from the submission that produced them | `orchestrator.md` closing; `standards/client/feature-documentation.md` |
| Recorded | The verifier's checks are structural; none of the findings above is something it can catch | `tools/verify-workflow-layer.ps1` |

## Deferred and recorded

| Item | State |
|---|---|
| **Enforcement is advisory.** The verifier checks the layer's integrity; nothing blocks a dispatch that skips the router. A `PreToolUse` hook would — deferred until a real miss supplies the evidence | Deferred |
| **The locks and the bug-ID counter are markdown rows**, not atomic — they hold across sessions only as far as every session re-reads them; a duplicate bug ID has a repair rule (`state/README.md`) | Recorded |
| **`Deliberately out of scope` in the Implementation Note is a proxy** — an agent that sets a problem aside may record it under `Assumptions` and never return `Routed to:`. Closing it means a field on several agent envelopes | Deferred |
| **The two agent classes do not measure destructive power** — `git-expert` holds `Write`/`Edit` for reviewable config, not because of its git blast radius | Recorded |

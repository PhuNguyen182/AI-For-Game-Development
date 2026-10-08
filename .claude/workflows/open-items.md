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

## Findings of the fifth scoring round — recorded, not fixed

Two blind scorers put the layer at 67.75 and 69 (about 68). Duplicates between them are merged; severity is the
higher of the two.

| Severity | Finding | Where |
|---|---|---|
| High | Assurance acceptance states (`FAIL`…`EXCEPTIONAL PASS`) and its `S0–S4` scale are defined nowhere — no score-to-state mapping — yet the QA pipeline routes on them; `S1` also collides with a submission ID | `agents/assurance-evaluator.md`; `standards/qa/assurance-scoring.md`; `qa-pipeline.md` step 4b |
| High | A G40 decline makes G42 offer review again in the same run, against bounds rule 4 and G50's "never twice in a run"; end of implementation is not on B18's boundary list | `gd-touchpoints.md` G40, G42; `references/bounds.md` |
| High | A G42 "yes" to QA at D3–D5 has no route to `qa-pipeline.md` **E1**, so CP3 approval reaches **E2** with no plan | `review-pipeline.md` step 6, exits; `qa-pipeline.md` entries |
| Medium | A GD-reported cosmetic bug in a built feature has three answers — G47 (bug, **E3**), the row 12–13 carve-out, and "a defect on a closed feature reopens its ledger" | `gd-touchpoints.md` G47; `orchestrator.md` step 0, *The ledgers* |
| Medium | Step 0 says "first match wins", but rows 4–5 sit above row 12 and are overridden only by prose below the table; "a tuned value" in `Game.Core` fits rows 4, 10 and 12 | `orchestrator.md` step 0 |
| Medium | `Needs-decision` and `Rejected, Routed to: <peer>` round trips move no counter, so architect↔reviewer or peer↔peer ping-pong is unbounded | `references/bounds.md` rule 1; `orchestrator.md` defaults |
| Medium | QA reports, the Research Report and the CP3 summary are never persisted, so CP4 cannot be compiled after a restart | `state/README.md`; `qa-pipeline.md` step 5 |
| Medium | A D3–D5 feature with no Core task never meets G40, so no review decision exists before its submissions land | `feature-development.md` step 3; G40, G42 |
| Medium | The gated-direct lane never offers QA, though `optional-gates.md` says a declined review moves the QA question rather than dropping it | `orchestrator.md` gated-direct; G14 |
| Medium | Any `.cs` chore — a comment fix — owes a G13 question carrying tier and axes, against "at A1/A2, say nothing" | `rules/orchestration.md` *Terms*; G13; `task-classification.md` |
| Medium | Calibration undercounts: strikes and rejection counters reset (B10, change requests) with no history kept, so the ledger cannot show what a feature actually spent | `state/templates/calibration.md`; `feature-ledger.md` |
| Medium | Evidence on a `Won't fix` bug is promised to "the next CP4", but CP4 asks only about unsettled bugs and unattached bugs have no CP4; an unattached A1–A2 `Fixed` bug whose verification was declined is never recorded | `defect-reporting.md`; G60; G13 |
| Low | Continuation debt for ledger-less work: the reply (`execution-loop.md`) or `project-state.md` (orchestrator, template) | `rules/execution-loop.md`; `orchestrator.md` defaults |
| Low | `bug-log.md`'s `Record` column still points at `<feature-root>/BUGS.md` | `state/templates/bug-log.md` |
| Low | No brief and no agent trigger for the B12/B13 root cause; only B3 and B6 have one | `agents/technical-architect.md`; `references/dispatch-brief.md` |
| Low | B7 is scoped per `cto` decision, but the ledger holds one `Measure-and-confirm:` for the whole feature | `references/bounds.md` B7; `feature-ledger.md` |
| Low | `TC-##` and `direct/S<n>` have no allocator or race rule; an unattached bug escalated to intake has no rule for moving its record into the new `BUGS.md` | `state/README.md`; `feature-bugs.md` |
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

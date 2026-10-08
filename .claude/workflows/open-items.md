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
- Gates: G40 has two answers (the whole feature, or none now), G42 fires only after a G40 decline, and QA is asked
  once per feature; the gated-direct lane offers `assurance-evaluator` (G14); the assurance-decline wording applies
  from A3.
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

## Deferred and recorded

| Item | State |
|---|---|
| **Enforcement is advisory.** The verifier checks the layer's integrity; nothing blocks a dispatch that skips the router. A `PreToolUse` hook would — deferred until a real miss supplies the evidence | Deferred |
| **The locks and the bug-ID counter are markdown rows**, not atomic — they hold across sessions only as far as every session re-reads them; a duplicate bug ID has a repair rule (`state/README.md`) | Recorded |
| **`Deliberately out of scope` in the Implementation Note is a proxy** — an agent that sets a problem aside may record it under `Assumptions` and never return `Routed to:`. Closing it means a field on several agent envelopes | Deferred |
| **The two agent classes do not measure destructive power** — `git-expert` holds `Write`/`Edit` for reviewable config, not because of its git blast radius | Recorded |

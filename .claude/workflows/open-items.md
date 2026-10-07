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
| **Behaviour change: gated-direct gates are asked** (G14), not automatic — resolving a conflict between the old lane file and I2 | Awaiting GD — decided this session, recorded for review |
| **Behaviour change: test-code review timing** (G62, I10) — offered as soon as the suite is written, before its results serve as evidence | Awaiting GD — decided this session, recorded for review |
| Every structural row the build log left awaiting review (state out of the framework, the classification migration, the promoted references, the bounds) | Superseded by the slimming round — reviewed as part of it |

## Open

| Item | State | What closing it takes |
|---|---|---|
| **The layer has never run against a real Unity project.** No ledger has been instantiated; every constant in `references/bounds.md` was chosen, not measured | Open | Real feature runs, recorded in `<state-root>/calibration.md` at each ledger close. A constant changes only on the GD's decision, proposed with evidence from those runs |
| **No agent may rank an architecture direction.** A `design` question is the GD's; an `architecture` question reaches the same Advisor⇄Critic loop, where nothing ranks options | Open — a philosophy decision | A `Recommended direction:` field on `technical-architect` for `architecture` questions, or accepting the mode-3 escape (G23) as sufficient |
| **Agent-roster proposals** — optional packs, retiring `producer`, renaming `tech-lead-sdk-platform`, and two side defects | Open — proposed, not executed | The GD's decision. Until the side defect is fixed, the verifier's standards check fails on `netcode-engineer` and `server-authoritative-engineer` |

## Ambiguities carried over from the old layer

Found by dry-running example prompts through both layers. Each existed before the slimming round; none was
resolved silently, because each is a GD decision.

| Ambiguity | Where |
|---|---|
| Step-0 row 12 (judgeable by looking) says "no checkpoint", while CP4 fires "every shape" (G60). Does direct-lane work that writes source close at CP4? And is its gate ask G13 or development's G42? | `orchestrator.md` row 12; `feature-development.md` **E2** |
| Row-12 work has no ledger, yet a QA "yes" enters `qa-pipeline.md` **E1**, which assumes one; the ledger rule points it at **E4** | `review-pipeline.md` exits; `qa-pipeline.md` entries |
| Feature-root documents key to **A** in development, to **D** in the shape table — does a D1/A5 change owe `DEBT.md`? | `feature-development.md` documents step; `rules/task-classification.md` Step 4 |
| A crash investigation of a *released build* touches a consequence path; rows 1–3 "yield to the criteria" could push a read-only investigation into gated-direct or intake | `orchestrator.md` step 0 |
| A Minor change request with no rework may never reach a "next status report" (G72) | `change-request.md` |
| A GD prompt that asks to approve the escalation before work starts meets G20/G3 (never ask to confirm the tier); G11/G12 resolve it in the GD's favour, but no file says so | `gd-touchpoints.md` |

## Deferred and recorded

| Item | State |
|---|---|
| **Enforcement is advisory.** The verifier checks the layer's integrity; nothing blocks a dispatch that skips the router. A `PreToolUse` hook would — deferred until a real miss supplies the evidence | Deferred |
| **The locks are markdown rows**, not atomic locks — they hold across sessions only as far as every session reads them | Recorded |
| **`Deliberately out of scope` in the Implementation Note is a proxy** — an agent that sets a problem aside may record it under `Assumptions` and never return `Routed to:`. Closing it means a field on several agent envelopes | Deferred |
| **The two agent classes do not measure destructive power** — `git-expert` holds `Write`/`Edit` for reviewable config, not because of its git blast radius | Recorded |

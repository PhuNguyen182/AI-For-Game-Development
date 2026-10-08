# Workflow-layer evaluation kit — scenario simulation

Fixed for every round. Do not edit between rounds; a changed yardstick makes rounds incomparable.

## How it was run, and what it scored

Five blind scorers per round (general-purpose agents, default model), each given this file and four scenarios on
a rotation — A: SC1–4, B: SC5–8, C: SC9, SC10, SC1, SC2, D: SC3–6, E: SC7–10 — so every scenario is traced twice
by agents that never see each other. Between rounds, only findings confirmed against the source were fixed, then
`verify-workflow-layer.ps1` was run; the next round used fresh agents and this file unchanged.

| Round (2026-10-08) | A | B | C | D | E | Mean |
|---|---:|---:|---:|---:|---:|---:|
| 1 | 70.5 | 73.5 | 66 | 74.25 | 68.3 | 70.5 |
| 2 | 77.5 | 83.3 | 74 | 80 | 75 | 78.0 |
| 3 | 79 | 91 | 88 | 91.5 | 86.5 | 87.2 |

Round 3 reported no Critical and no High; its one Medium (a QA-recorded cosmetic bug routable to row 12) was fixed
after scoring, unscored. Its Lows are in `workflows/open-items.md`.

## What is being evaluated

The workflow + orchestrator layer of a multi-agent Unity game-dev framework, at
`C:\Users\Admin\Projects\AI-For-Game\AI-For-Game-Development\.claude\`:

- `rules/*.md` — auto-loaded into every session (start with `rules/orchestration.md`).
- `workflows/orchestrator.md`, `workflows/gd-touchpoints.md`, the six pipelines in `workflows/`,
  `workflows/references/*`, `workflows/state/**`.
- Agent definitions in `agents/*.md` only where a scenario dispatches that agent and you need its contract.

**Design intent, stated by its author:** the layer was rewritten as *contracts* for capable AI models — it fixes
the walls (entries, allowed dispatches, hard ordering, GD touchpoints, bounds, exits) and leaves the sequencing
between the walls to the orchestrator model's judgment, instead of hand-holding step by step. Judge it against
that intent: **a gap a competent model fills correctly from context and the stated principles is not a defect.**
A gap is a defect only when competent models would plausibly act differently from each other in a way that
changes the outcome, act wrongly, stall, loop, ask the GD something they shouldn't, or fail to ask something they
must.

"GD" = the Game Director, the human user. Every question to the GD is an `AskUserQuestion` multiple-choice call.

Do **not** read `workflows/open-items.md`, any git history, or the repo's `README.md` — score what the runtime
layer itself tells an orchestrator, blind to earlier evaluations.

## How to run a scenario

You are the orchestrator model. For each scenario: take the GD input, then each scripted event in order, and
write the trace — at every step, the action the layer prescribes, the file:line that prescribes it, any state
written (ledger / project-state / bug log), and every GD touchpoint fired (G-ID, single/multi-select).

Where the layer does not determine the next action, record a **friction point**:

| Severity | Meaning |
|---|---|
| **Critical** | Safety/security/integrity breach, irreversible action without authorisation, or a deadlock with no exit |
| **High** | Competent models would likely take a wrong or divergent action that changes the outcome (wrong lane, a gate skipped, an unbounded loop, a GD decision taken silently, state lost) |
| **Medium** | Real ambiguity or contradiction; a careful model probably recovers, but cost, rework or a needless GD question is likely |
| **Low** | Wording, a stale cross-reference, a minor inefficiency; outcome unaffected |

Each friction point: severity, scenario + step, the exact file:line(s), what happens, and why a competent model
would not resolve it from context. **Verify before reporting** — re-read the cited lines; a finding that the
layer actually answers elsewhere is a false positive and costs you credibility. Do not report a "missing rule"
for something the stated principles already decide.

## Rubric — score each dimension 0–10 for the layer as your scenarios exercised it

Anchors: **10** no friction in any trace · **8** only Low friction · **6** Medium friction a careful model recovers
from · **4** a High — a likely wrong or divergent outcome · **2** several Highs or a Critical · **0** unusable.
Interpolate. Score what your traces showed, not what you imagine elsewhere.

| # | Dimension | Weight | The question |
|---|---|---:|---|
| D1 | Routing correctness | 15 | Does every input land in the right lane/door, and would two competent orchestrators pick the same one? |
| D2 | Autonomy calibration | 15 | Does the orchestrator act without asking where it should, and ask the GD exactly where it must — no over-asking, no silent consequential decision? |
| D3 | Completeness — no dead ends | 15 | Does every event in the trace have a defined next action and exit? |
| D4 | Loop termination & state recovery | 10 | Are loops bounded, counters well-defined, and can a fresh session resume from state alone? |
| D5 | Safety & integrity | 15 | Security, Editor/device locks, irreversible operations, honest verification claims |
| D6 | Internal consistency | 10 | Do the files agree with each other along these traces? |
| D7 | Proportionality | 10 | Does process weight match the tier — small work stays light, consequential work gets its gates? |
| D8 | Model executability | 10 | Can a model execute it from the text: clarity, how many cross-file hops a decision needs, judgment space vs. walls |

**Score = Σ (dimension × weight) / 10**, out of 100.

## Scenarios

Project context for all scenarios: a mobile Unity game, URP, `CLAUDE.md` still has every `TODO` unfilled
(track unknown), `<state-root>` = `.workflow/`, no feature ledgers exist yet unless the scenario says so. The GD
writes in Vietnamese; the gist is given in English.

### SC1 — a D3 feature with a declined gate and a design flaw
Input: "Add a 7-day login reward calendar. Rewards are granted through the existing Core economy (`Game.Core.Economy`). Panel on the main menu."
Events: (1) `technical-architect` returns the Tech Spec with one `design` line: "does the streak reset at local midnight or UTC?" (2) GD picks UTC. CP2 approved. (3) `csharp-engineer` returns the Core contract. GD declines review at the gate offered there. (4) `ui-ux-programmer` returns `Done`. (5) QA: `playtest-tester` reports a cosmetic misalignment (technical bug) and that day 7's reward is granted twice if the player crosses UTC midnight on the panel (classify it). (6) Run through to closure.

### SC2 — light work must stay light
Input A: "Change jump height from 2.0 to 2.4 on the Player prefab." Input B (after A finishes): "Fix the typo 'Pasue' in the pause-menu label." Input C: "The jump feels too floaty now, it's a bug — fix it." Input D: "Rename the private field `_spd` to `_speed` in `PlayerMotor.cs`."

### SC3 — consequence-only work and its strike cap
Input: "Switch the Android signing config in `ProjectSettings` / the Gradle template to read the keystore alias from the CI credential id `android-release-2027` instead of the current one."
Events: (1) the owning agent returns `Done`. (2) GD accepts both review gates. (3) `code-reviewer` rejects (the old alias still referenced in a fallback). (4) Fixed, `code-reviewer` rejects again (the fallback swallows a missing-credential exception and signs with a debug key). (5) What now?

### SC4 — a bug that will not stay fixed
State: feature `inventory` closed last week (ledger `Closed`, A3). Input: "Items vanish from the inventory after app resume." Events: (1) traced to `Game.Core.Inventory` save path; fix submitted, review passes; QA verifies, bug reopens. (2) Second fix, reopens again. (3) Continue to the end of what the layer bounds allow.

### SC5 — a change request mid-fan-out
State: feature `gacha` at fan-out, CP2 approved, D4, Core contract reviewed, `ui-ux-programmer` mid-dispatch, one submission with 2 strikes. Input: "Change pity from 90 pulls to 80, and the pity counter must now carry over between banners." Run until rework is ready for its gates.

### SC6 — measure before deciding
Input: "Addressables or Resources for level streaming on our low-end Android device? Measure it on our device before we decide." Events: (1) the spike needs an Android development build; the GD has not mentioned a build. (2) The measurement lands: Addressables 30% faster load, +4 MB memory. (3) `cto` returns `Needs-decision`, `Routed to: gd` on whether the 4 MB is acceptable.

### SC7 — multiplayer, unknown track, direction loop
Input: "Add a 2-player online co-op mode for the boss fights." Events: (1) the first question about the track. (2) GD answers client + multiplayer. (3) `advisor` returns three netcode directions; GD asks advisor "just pick the best one for me". (4) critic finds a High risk in the GD's chosen option; GD wants another round; critic round 3 still finds a new High. (5) What happens at the cap?

### SC8 — direct agents, the one Editor, test code
Input A (mode 3): "`unity-engineer`: add pooling to `EnemySpawner`." Input B, sent while A is still running: "`qa-automation-engineer`: write Play Mode tests for the spawner." Events: (1) A returns `Done` with a claim "GC alloc down 80%". (2) B's suite is written and green. (3) GD asks "is this ready to ship?"

### SC9 — a fresh session resumes mid-feature
State: feature `daily-quests` at `Position:` CP3, ledger present, `project-state.md` shows the Editor lock held by `unity-engineer`, claimed 9 hours ago, no expiry note. A new session starts; GD input: "Continue." Events: (1) resume. (2) CP3 approved. (3) QA executor needs the Editor.

### SC10 — production crash into a Core rule
Input: "Crashlytics shows a spike of `NullReferenceException` in `RewardCalculator.Apply` since 1.4.2, 3% of sessions." Events: (1) `crash-anr-investigator` returns a Root Cause Report: null `BonusTable` when remote config is late, owner `csharp-engineer`, fix needs a default table in `Game.Core.Economy`. (2) Proceed through to closure.

## Report format (return exactly this)

```
## Scorer <letter>
### Traces
<per scenario: numbered steps, each with action — file:line — state — G-IDs; friction points inline as [F#]>
### Friction points
| # | Sev | Scenario.step | File:line | What happens | Why a competent model would not resolve it |
### Scores
| Dim | Score /10 | One-line justification citing F# |
Total: <x>/100
### What works
<3–6 bullets: where the contract style demonstrably helped the trace>
```

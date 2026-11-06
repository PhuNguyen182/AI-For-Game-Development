---
name: monet
description: "Monetisation change: candidates, simulate.py, player-effect read, critic, rollback threshold. Use for ads, IAP, pricing, economy, revenue."
argument-hint: "<the question or revenue problem>"
---

# /monet

- **Writer:** the main session runs this and the simulator; rules in `advisory-protocol`.
- **Not for:** vendor choice (`/decide`), SDK wiring (`sdk-platform-engineer`), a change with a stated value (size it, `routing.md`), user acquisition.

## 1. Baseline — `monetization-designer`
- **Data pack:** `check_pack.py` first; failed → name the problems, no pack reaches the agent.
- **Brief:** the question, `Workflow: /monet`, `Advisory-Thread:`, `Data-Period:`, GDD at `CLAUDE.md` → GDD path, past advice from `adv q`.
- **Returns:** the baseline and 2–4 candidates, each with its change, simulator input and retention risk.
- **Vendor question inside:** split it out to `/decide`.

## 2. Simulate
- **Run:** write each candidate's input to `.memory/advisory/sim/<thread>-<candidate>.json` and run `simulate.py` (`monetization-modeling`).
- **Invalid input:** back to the same agent; the script's error names the field.
- **Output:** back to the same agent, which states what it shows per candidate.
- **No pack:** scenarios only, with no recommendation; the return ends with what to measure.

## 3. Player effect — `game-designer`
- **Independent read:** every candidate, without the monetisation adviser's recommendation.
- **Conflict:** stays a conflict: both positions and the cost of each.

## 4. Lean
- **Show:** candidates, bands with labels and the conflicts, between the advisory markers.
- **`AskUserQuestion`:** which candidate the main GD leans to, by name, or reject all. Recommended first when a pack exists; no recommendation without one.

## 5. Attack — `critic`
- **On the leaned candidate:** assumptions, store policy, `CLAUDE.md` → Compliance. Brief carries `Advisory-Thread:`.

## 6. Lock
- **`AskUserQuestion`:** lock / pick again / stop.
- **Plan:** `docs/monetization-plan.md`: design parameters, success metric, measurement window, rollback threshold, `adv:<id>` references. Never an observed figure.
- **Decisions:** `adv decide` on each finding the main GD ruled on.
- **Usefulness:** the main GD marks findings `adv useful <id> yes|no`; under half useful in a run → revise that adviser's method skill before the next one.

## 7. Hand-off
- **Build:** `/feature` recording `CP1: n/a (direction given: /monet <date>)`; real-money IAP sets the risk flag.
- **Tuning only:** a remote-config change per `live-ops-content-pipeline`.
- **After launch:** a new data pack and `/monet` again judges it against the rollback threshold.

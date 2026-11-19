---
name: design
description: "Game design direction: game-designer frames, researcher finds precedents, main GD picks, critic attacks, GDD written. Use for undecided design."
argument-hint: "<the design problem, in the main GD's words>"
---

# /design

- **Writer:** the main session runs this and writes the GDD; rules in `advisory-protocol`.
- **Not for:** a design already decided (size it, `routing.md`), architecture questions (`/feature` CP1), a plain question (one adviser).

## 1. Frame — `game-designer`
- **Brief:** the problem verbatim, `Workflow: /design`, `Advisory-Thread:`, `Data-Period:`, GDD at `CLAUDE.md` → GDD path, past advice from `adv q`.
- **Returns:** intended feeling, loop effect, what makes the problem hard, the open question.
- **Show:** between the advisory markers. Wrong frame → the main GD corrects it, same agent again.

## 2. Precedents — `researcher` (Options)
- **Brief:** the framed question and constraint, with `Advisory-Thread:` so it stays off git.
- **Method:** `design-precedent-sweep`; 2–4 mechanisms, unranked.

## 3. Pick
- **`AskUserQuestion`:** the options unranked, in the researcher's order (`core.md`), plus none of these.
- **Record:** `adv` holds the reads; the pick goes to the GDD at step 6.

## 4. Detail — `game-designer`
- **Same agent:** a draft GDD section and acceptance criteria for the pick.
- **Parameters:** design values only; an observed figure stays in the store and is cited by `adv:<id>`.

## 5. Attack
- **`critic`:** on the draft; brief carries `Advisory-Thread:`.
- **`monetization-designer`:** reads the draft independently when economy, ads or IAP are touched.
- **Show:** every finding, between the advisory markers.

## 6. Lock
- **`AskUserQuestion`:** lock / revise (what) / pick again.
- **Write:** the GDD section at `CLAUDE.md` → GDD path; no GDD yet → create it at that path. Decided values and targets only.
- **Decisions:** `adv decide` on each finding the main GD ruled on.
- **Usefulness:** the main GD marks findings `adv useful <id> yes|no`; under half of an adviser's findings in a run marked useful → revise that adviser's method skill before the next run.

## 7. Hand-off
- **New work:** `/plan-game` re-plan on the changed part, or `/feature` recording `CP1: n/a (direction given: /design <date>)`.
- **Called from `/feature`:** return to its `cp` and `next_step` (`records.py feature show <slug>`) with the locked section as the direction.

# Calibration

> **What the layer's constants actually cost, measured from closed ledgers.** One row per feature, written
> when its ledger is marked `Closed` or `Abandoned`, copied from numbers already in that ledger. Nothing here
> is estimated, reconstructed or projected — `execution-loop.md` forbids invented telemetry, and a calibration
> table built from guesses would be worse than none.

## Why this file exists

Every bound in this layer was chosen by judgement: **3** review strikes, **3** Advisor⇄Critic rounds, the
**2**-round QA bound, the **2–5** attempt budget, **1** measure-and-confirm cycle, **1** root-cause reset,
**2** gated-direct strikes. None came from a measurement, because when they were written nothing had run.

`effort-allocation.md` grades an unsupported assertion **E0** and requires **E2 or better** — a direct test,
measurement or tool output — behind any material claim. By that scale the layer's own constants are its
weakest part, and the honest response is not to defend them but to instrument them.

This file is that instrument. It costs one row per feature and it is the only thing that can ever move a
constant from "chosen" to "known".

## The rows

Copy each value from the closed ledger. Leave a cell blank rather than filling it from memory — a blank is a
fact, an invented number is not.

| Feature | Tier · axes | Attempts used / budget | Max strikes on one submission | QA rounds | Advisor⇄Critic rounds | Root-cause resets | CP4 defect rejections | Gates run | Checkpoints that changed the outcome | Closed |
|---|---|---|---|---|---|---|---|---|---|---|
| _none yet_ | | | | | | | | | | |

**"Checkpoints that changed the outcome"** is the one judgement call, and it is the most valuable column: name
each checkpoint where the GD's answer actually altered what was built. A checkpoint that never changed an
outcome across many features is overhead `effort-allocation.md`'s artifact budget would delete.

## Reading the table — not before there is something to read

**Do not tune a constant from one feature.** A single run is a run, not a distribution — the same rule
`verification-standards.md` applies to a performance number applies here.

| Signal, across several closed features | What it suggests |
|---|---|
| No submission ever reached strike 3 | The three-strike ladder is never exercised. Either it is correctly rare, or the gates are not pressing hard enough — check which before lowering it |
| Submissions routinely reach strike 3 | The briefs are underspecified. The fix is upstream at the Tech Spec, not a fourth review round |
| Attempts used is always 1 | The budget is not binding, and the whole loop costs nothing. Leave it |
| Attempts used routinely hits the ceiling | Either the budget is too tight for the real D, or the classification is reading D too low |
| The loop never reaches round 3 | Correct. It is a cap, not a target |
| A checkpoint never changed an outcome | The strongest candidate for deletion in the whole layer |
| Gates declined most of the time, and no defect followed | The default recommendation is miscalibrated for this project's work — say so to the GD rather than repeating the same advice |
| Gates declined, and defects followed | Also worth saying, and worth saying with the rows that show it |

**Changing a constant is a change to the layer, not a tuning knob.** It goes to the GD with the rows behind
it, and the old value is superseded in `workflow-checklist.md`'s debt register rather than quietly
overwritten — the same discipline `feature-documentation.md` sets for a feature's own `LEDGER.md`.

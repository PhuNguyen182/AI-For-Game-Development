# Template — `<state-root>/calibration.md`

Copy the fenced block to `<state-root>/calibration.md`. This file is the template, never the record. Rules:
`../README.md`.

Every bound in `references/bounds.md` was chosen by judgement, not measured — E0 on `effort-allocation.md`'s
own scale. This record is how they become known: one row per feature, copied from its ledger when the ledger
is marked `Closed` or `Abandoned`.

## Reading it — only once there is something to read

Never tune a constant from one feature; a single run is not a distribution.

| Signal, across several closed features | Suggests |
|---|---|
| No submission ever reached strike 3 | The ladder is rarely exercised — check whether that is correct before lowering it |
| Submissions routinely reach strike 3 | Briefs are underspecified; fix the Tech Spec, not the cap |
| Attempts used is always 1 | The budget is not binding; leave it |
| Attempts used routinely hits the ceiling | The budget is too tight for the real D, or D is read too low |
| A checkpoint never changed an outcome | The strongest candidate for removal |
| Gates mostly declined, no defect followed | The default recommendation is miscalibrated — tell the GD rather than repeat it |
| Gates declined, and defects followed | Tell the GD, with the rows that show it |

**Changing a constant is the GD's decision**, proposed with the rows behind it; the old value is recorded as
superseded in `open-items.md`, never quietly overwritten.

```markdown
# Calibration

One row per closed or abandoned feature, copied from its ledger and its `BUGS.md` — the most reopens on one bug is read from its history rows, since the counter resets after a root cause. Nothing estimated or reconstructed — a blank
cell is a fact, an invented number is not. "Checkpoints that changed the outcome" is the one judgement call:
name each checkpoint where the GD's answer actually altered what was built.

| Feature | Tier · axes | Attempts used / budget | Max strikes on one submission | Bugs opened · max reopens on one bug | Advisor⇄Critic rounds | Root-cause resets | CP4 defect rejections | Gates run | Checkpoints that changed the outcome | Closed |
|---|---|---|---|---|---|---|---|---|---|---|
| _none yet_ | | | | | | | | | | |
```

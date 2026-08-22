# Ledger

> **The cross-run state no agent can hold.** Every agent in this project is isolated and stateless — it
> cannot count its own retries, cannot see another agent's return, and cannot remember the last run. Written
> **at each transition**, not at the end of a run: a counter that survives only in conversation context is
> not a safety mechanism. Owned by `orchestrator.md`; the column contract is below.

## In flight

_No feature in flight._

<!-- One block per feature. Fields: Tier (from Triage, never guessed) · Track (client, or client +
multiplayer — absent, agents silently assume client-only) · Checkpoint (none/CP1/CP2/CP3/CP4) ·
Advisor⇄Critic (round n of 3, and the options already ruled out) · Baseline (the performance figure and how
it was taken) · Reported (the last period `producer` covered). Then one row per submission:

| Submission | Author | Strikes /3 | QA fails /2 | Verdicts landed |
|---|---|---|---|---|
-->

## Open review debt

Source written outside a review gate. **Recorded, never enforced** — it blocks no dispatch and settles in
batch at the next natural gate. Clear a row only when `review-pipeline.md` has actually returned on it.

| Path | Written by | When | Settled |
|---|---|---|---|
| _none_ | | | |

## Editor lock

One Unity Editor, project-wide; ten agents hold `mcp__<server>__*` tools against it. Claim before
dispatching one, release on its return.

| Held by | Since |
|---|---|
| _free_ | |

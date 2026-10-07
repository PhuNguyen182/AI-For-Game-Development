# Template — `<feature-root>/LEDGER.md`

Copy the fenced block to `<feature-root>/LEDGER.md` at `feature-intake.md` step 2. This file is the template,
never a ledger. Rules: `../README.md`.

`## Decisions` belongs to whoever made the decision, appended in the same submission, per
`.claude/standards/client/feature-documentation.md`. `## Run state` belongs to the orchestrator, written
whenever a counter, checkpoint or gate answer changes; no implementing agent edits it. Keep every run-state row,
even empty — an empty row is a fact, a missing one is a question.

```markdown
# Ledger — <feature name>

## Decisions

Decisions a future reader would otherwise silently undo. Superseded in place, never deleted.

| When | Decision | Why | What was rejected, and why | What it constrains |
|---|---|---|---|---|
| | | | | |

## Run state

- Slug: <feature-slug>
- Status: In flight | Closed | Abandoned <if Abandoned: why, and the last verified state>
- Tier: A<n>, from <axis> · axes D<n> C<n> U<n> R<n> X<n>
- Tier history: <A<n> from <axis> → A<n>, when and why> — appended, never overwritten; effort is judged against
  the tier in force when it was spent
- Position: <pipeline, step or checkpoint the feature last reached> — what a resumed session and a change
  request read to know where to restart
- Gates: review <asked? authorised | declined | not yet asked> · QA <same> — the answers already given, so
  no ask repeats (B18) and G42 knows whether G40 fired
- Track: client | client + multiplayer
- Advisor⇄Critic: round <n> of 3 · ruled out: <options> · <reset by a Major change on <date> | never reset>
- Research: <what research-decision.md settled, each report's `Picture taken:` date, any provisional decision's re-open threshold> | <skipped — covered by <named package, API or system>>
- QA plan: <qa-lead's coverage assignment and exit criteria, verbatim — carried back into sign-off>
- Baseline: <performance figure, how it was taken, by which report>
- Root-cause resets: 0/1
- Measure-and-confirm: 0/1
- Rejections: CP2 0/3 · CP3 0/2 · CP4-as-defect 0/2 · sign-off re-dispatch 0/2 · assurance FAIL 0/1

| Submission | Author | Strikes / bound | QA fails /2 | Attempts used | Verdicts landed |
|---|---|---|---|---|---|
| | | | | | |

### Accepted gaps

Written before closure (I6), mirrored into `DEBT.md` from A3 upward.

| Gap | Accepted by | When | Recorded in |
|---|---|---|---|
| _none_ | | | |

### Continuation debt

| Objective | Attempts / budget | Known non-solutions | Safe resume point |
|---|---|---|---|
| _none_ | | | |
```

Strike bounds differ by row — an ordinary submission 3 (B3), a test suite at review **E3** 2 (B5) — so write
both numbers in the cell (`1 /3`, `1 /2`).

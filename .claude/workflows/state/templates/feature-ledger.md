# Template — `<state-root>/features/<slug>/LEDGER.md`

Copy the fenced block to `<state-root>/features/<slug>/LEDGER.md` at `feature-intake.md` step 2. This file is the
template, never a ledger. Rules: `../README.md`; where each counter is written: `../../references/bounds.md`.

Written only by the orchestrator, whenever a counter, checkpoint or gate answer changes. Keep every row, even empty
— an empty row is a fact, a missing one is a question. A resumed session needs nothing but this file, the files it
names, and `project-state.md`.

```markdown
# Ledger — <feature name>

- Slug: <feature-slug> · Feature root: <path to the code and its documents; Core root first when there are two>
- Status: In flight | Closed | Abandoned <if Abandoned: why, and the last verified state>
- Request: <the GD's words, verbatim — every change request appended, dated, never paraphrased>
- Spec: `SPEC.md` beside this file — the Tech Spec, or the D1–D2 direct notes · approved <CP2 date | handed off
  <date>>
- Tier: A<n>, from <axis> · axes D<n> C<n> U<n> R<n> X<n>
- Tier history: <A<n> from <axis> → A<n>, when and why> — appended, never overwritten
- Position: <`<pipeline>.md` step <n> | CP<n>> — waiting on <what> · in flight: <agent-id, dispatched <when>> |
  none
- Gates: review <whole feature | declined | not yet asked> · QA <authorised | declined | not yet asked> · assurance
  <with QA | authorised at G14> — so no ask repeats (B18), and G42 knows what is left to ask
- Track: client | client + multiplayer
- Advisor⇄Critic: round <n> of 3 · ruled out: <options> · <reset by a Major change on <date> | never reset>
- Research: <what research-decision.md settled, each report's `Picture taken:` date, any provisional decision's
  re-open threshold, any product call deferred (G32)> | <skipped — covered by <named package, API or system>>
- QA plan: <qa-lead's coverage assignment and exit criteria, verbatim — carried back into sign-off>
- Baseline: <performance figure, how it was taken, by which report>
- Root-cause resets: <per loop — S<n> strikes, BUG-#### reopens, CP3, CP4 — 0/1, and the cause once spent>
- Measure-and-confirm: 0/1
- Rejections: CP2 0/3 · CP3 0/2 · CP4-as-defect 0/2 · sign-off re-dispatch 0/2 · QA rounds opening new bugs 0/3
- Open asks: <per item — `Needs Confirmation` on <value> n/3 (B9) · escalation <agent → lead> n/1 (B16) · `Blocked`
  on <input> n/2 (B17)> | none — removed when answered, so a resumed session never restarts a count

## GD decisions

The direction locked at CP1, the risks accepted, standards set, and every decision a change request overturned —
superseded in place, never deleted. Carried into every brief that depends on them.

| When | Decision | Why | Rejected options | Constrains |
|---|---|---|---|---|
| | | | | |

## Submissions

One row per agent return sent toward a gate (`orchestration.md` → *Terms*). Rework answering a row's own review
rejection stays on that row; any other fix is a new row naming what it fixes.

| ID | Author | Fixes | Strikes / bound | Attempts used | Verdicts landed | Implementation Note |
|---|---|---|---|---|---|---|
| S1 | | — \| S<n> drift \| BUG-#### \| CP4 defect \| CR <date> rework \| escalated `direct/S<n>` | 0 /3 | | | `notes/S<n>.md` |

## Open gaps

Coverage that did not run, criteria not met, verifications not performed — written when they arise, read at CP4.

| Gap | Found by | When | Status — open, closed by <run>, or accepted (G9) |
|---|---|---|---|
| _none_ | | | |

## Continuation debt

One block per record, every field from `.claude/rules/execution-loop.md` — a re-dispatch needs its
`Next best action:` and `Known non-solutions:` verbatim.

_none_
```

Strike bounds differ by row — an ordinary submission 3 (B3), a test suite at review **E3** 2 (B5) — so write both
numbers in the cell (`1 /3`, `1 /2`). An accepted gap is mirrored into the feature root's `DEBT.md` from A3 at
closure (I6).

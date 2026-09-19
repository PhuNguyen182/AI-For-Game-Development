# Workflow Layer — Review Records

> **History, not specification.** Every file here is the record of one review round: what was found, what was
> changed against it, and what it scored afterwards. **Nothing here governs anything.** The layer that runs is
> `.claude/workflows/`; the rules that load are `.claude/rules/`.
>
> These were named `<pipeline>-update.md` and sat beside `agent-template.md` in `.claude/docs/`, which read as
> though each pipeline had two versions. It never did. The folder is the fix.

## How to read one, and the trap in them

**Each note is cumulative, and its later parts supersede its earlier ones.** A note may score the same
pipeline three times as the evidence improved — read one, stop halfway, and you take a number a later part
already retracted. `feature-intake.md` is the clearest case: **9.0** on a reading, **8.2** once it was run,
**8.9** after the findings closed. The last score in the file is the one that stands.

**Every number about the layer's own state is as of that round**: verifier claim counts, "still unreviewed"
lists, "nothing is committed". They were true when written and most are not now. **`.claude/workflows/workflow-checklist.md`
§13–§16 is the current record** — it is inside the layer, and the verifier checks its counts against reality.
These notes hold the evidence behind each finding, which the checklist only summarises.

## The seven rounds, in order

| # | Record | What was reviewed | Method | Final score |
|---|---|---|---|---:|
| 0 | [`workflow-layer.md`](workflow-layer.md) | The whole layer, architecture-level — findings **F1–F7** | Read | **7.5** |
| 1 | [`feature-intake.md`](feature-intake.md) | `workflows/feature-intake.md` — **I1–I10**, then **R1–R6** | Read, **then run** | 7.0 → 9.0 → 8.2 → **8.9** |
| 2 | [`research-decision.md`](research-decision.md) | `workflows/research-decision.md` — **R1–R17** | Run | 7.0 → 5.9 → **8.9** |
| 3 | [`feature-development.md`](feature-development.md) | `workflows/feature-development.md` — **D1–D27** | Run | 6.2 → **8.2** |
| 4 | [`review-pipeline.md`](review-pipeline.md) | `workflows/review-pipeline.md` — **RP1–RP16** | Run | 5.6 → 8.5 → **9.0** |
| 5 | [`qa-pipeline.md`](qa-pipeline.md) | `workflows/qa-pipeline.md` — **QA1–QA19** | Run, **then two gates** | self **8.9** · independent **8.75** |
| 6 | [`change-request.md`](change-request.md) | `workflows/change-request.md` — **CR1–CR2, H1–H4, M1–M7, L1–L4** | Run, **gate before scoring** | **8.8** |
| 7 | [`orchestrator.md`](orchestrator.md) | `workflows/orchestrator.md` — the router | **Three rounds**, gate before scoring | self **8.6** · independent **8.9**, six-axis **9.0** |

**The method mattered more than the score, and it changed as the series went.** Rounds 0–1 were read into a
score; running them dropped it. From round 2 the pipelines were **run** — real agents dispatched, the files
followed literally, recording where they hit a wall. From round 5 the round's **own output** was put through
the layer's own gates before any number was written. Every step down that list found defects the step above
it had missed, including in its own fixes.

## What these are good for

- **The evidence behind a finding** the checklist states in one line.
- **Known non-solutions** — what was tried and why it failed, so a later session does not re-run it.
- **Why a rule is worded the way it is**, when the wording looks arbitrary.

## What they are not good for

- **Deciding how to work.** That is `.claude/workflows/` and `.claude/rules/`.
- **Current counts or status.** Use `workflow-checklist.md`.
- **A score.** Every one was marked by the author of the fixes — **E0** on `effort-allocation.md`'s own scale
  — except rounds 5, 6 and 7, which carry an independent verdict and say so.

## Rules

- A round produces exactly one file here, named after the workflow file it reviewed.
- Nothing in `.claude/workflows/` or `.claude/rules/` may depend on a file here. `workflow-checklist.md` cites
  them as evidence; that is a pointer to history, never a dependency.
- Superseded content stays, marked superseded. A note is a record — editing out what was wrong at the time
  destroys the only thing it is for.
- This index is machine-checked: `workflows/tools/verify-workflow-layer.ps1` fails when a record has no row
  here, or a row names a file that does not exist.

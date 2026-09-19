# Workflow References

> **Detail promoted out of a pipeline file, kept in one place rather than loose beside them.** Every file
> here was a section of a workflow file that outgrew it. Each leaves a pointer in its source, and each is
> read only in the situation its source names — never as part of following that pipeline top to bottom.

This is the same promotion rule `.claude/standards/client/feature-documentation.md` sets for a feature's own
docset, applied to the workflow layer: content is moved when it earns a file, the source keeps a pointer and
never a copy, and one fact has one home. It also matches how skills are laid out in this repo —
`SKILL.md` plus `references/*.md`.

| File | Promoted from | Read it when |
|---|---|---|
| `entry-index.md` | `orchestrator.md` | Any mode-2 dispatch — it is that mode's whole vocabulary, plus the four values every entry carries |
| `orchestrator-direct-dispatch.md` | `orchestrator.md` | A mode-2 or mode-3 dispatch is the chosen lane, and when one returns with no pipeline running |
| `intake-advisor-critic-loop.md` | `feature-intake.md` | The classification put a feature at **D4–D5, or U3** — otherwise it never runs |
| `research-depth-lanes.md` | `research-decision.md` | Entering that pipeline, to pick the lane before anything is dispatched |
| `research-exit-and-custody.md` | `research-decision.md` | Leaving that pipeline — which door, what travels with the result, and the standalone acceptance gate |
| `development-brief.md` | `feature-development.md` | Writing any dispatch brief, and forwarding a field one agent produced for another |
| `development-exit-and-custody.md` | `feature-development.md` | **Any agent returns** — what the submission carries, which door it takes, and where every other returned field is recorded |
| `development-fan-out.md` | `feature-development.md` | Somebody proposes running the client agents in parallel, or adding a fourth agent to that fan-out |
| `development-feature-documents.md` | `feature-development.md` | Every implementation task in a root has returned and the documents are owed |
| `qa-device-lane.md` | `qa-pipeline.md` | A build exists and device coverage was assigned — the only lane that can satisfy a target-platform claim |
| `qa-assurance-gate.md` | `qa-pipeline.md` | The work is **A3 or above** and every other verdict is in |
| `qa-checkpoint-4.md` | `qa-pipeline.md` | Closing a feature. `qa-pipeline.md` still owns CP4; this is its detail |
| `qa-entry-inputs.md` | `qa-pipeline.md` | Taking any entry into QA — and when review did not run |
| `qa-exit-and-custody.md` | `qa-pipeline.md` | **Any QA agent returns** — the eight deliverables, every door out, and where each returned field is recorded |
| `qa-execution-order.md` | `qa-pipeline.md` | Dispatching the coverage assignment; both locks and when each is claimed |
| `review-needs-confirmation.md` | `review-pipeline.md` | `security-reviewer` returned `Needs Confirmation` |
| `review-checkpoint-3.md` | `review-pipeline.md` | Compiling or rejecting CP3. `review-pipeline.md` still owns it |
| `optional-gates.md` | `orchestrator.md` | Implementation returned and a gate would otherwise be dispatched — **read before dispatching either gate, every time** |
| `standalone-runs.md` | `orchestrator.md` | The GD named a pipeline instead of describing a feature |
| `gated-direct-lane.md` | `orchestrator.md` | An input trips a **C2+** criterion and nothing else |
| `loop-termination.md` | every pipeline with a counter | A cap has been reached — and **before adding any loop**: it is the single home for every bound in the layer |
| `review-entry-inputs.md` | `review-pipeline.md` | Dispatching a submission to either gate |
| `review-exit-and-custody.md` | `review-pipeline.md` | **Either gate returns** — which door each result takes, the custody table for every field no `Status:`/`Verdict:` row names, and the supply-chain pre-gate |
| `qa-test-code-gate.md` | `qa-pipeline.md` | `qa-automation-engineer` has written a suite |
| `intake-tech-spec.md` | `feature-intake.md` | Writing or revising a Tech Spec at step 6 — **D3–D5** only |
| `development-escalation-lane.md` | `feature-development.md` | A routine implementation pass has already failed |
| `change-severity-and-custody.md` | `change-request.md` | A Major reopens CP1 for a feature with no prior one, or one dispatch returns both a severity and a `cto` routing |

## Rules

- A file here is promoted content, never a second home for something its source still states. If a fact
  appears in both, the source keeps it and this copy is the one that goes stale.
- Nothing is created here speculatively. A section moves when its source exceeds the 200-line cap or when the
  detail genuinely buries the flow around it — never because the folder "should" have an entry.
- Every file here is pointed at from its source. An orphan is a defect, not an extra.
- Cross-run state is **not** documentation and does not belong here — it lives in `../state/`. Track
  standards are not documentation about the layer either — they live in `.claude/standards/`, indexed by
  `rules/standards-index.md`.
- **Every bound in the layer is stated in `loop-termination.md` and cross-referenced from where it fires** —
  never the other way round. A loop whose cap lives only in the file that owns the loop is a cap the next
  loop added beside it will not know about.
- Executable checks are not documentation either — they live in `../tools/`. `verify-workflow-layer.ps1`
  enforces the orphan rule above rather than restating it: a file here that no source names fails the run.

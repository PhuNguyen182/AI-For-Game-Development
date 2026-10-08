# Shared — Effort & Value Allocation

Applies to: every agent and the orchestrator, on every input. `task-classification.md` says how much rigor a task
earns; this file says what that rigor is spent on — and what it must never be spent on. Effort that does not change
the outcome is not diligence; it is waste that looks like diligence.

## The marginal value rule

One more action — a read, a search, a tool call, a refactor, a paragraph — is justified only when it would change
what you produce or what the GD decides. Quality gain, risk reduction, rework avoided or decision confidence must
outweigh the time, tokens, calls and complexity it costs. If it would change nothing, skip it.

## Minimum process by tier

| Tier | The floor |
|---|---|
| **A1** | Execute directly → sanity-check against the request |
| **A2** | Targeted inspection → execute → direct verification of what changed |
| **A3** | Acceptance baseline → concise plan → execute → targeted tests/evidence → verify against the baseline |
| **A4** | A3 + dependency/design/risk review + edge cases + a regression check |
| **A5** | A4 + explicit residual-risk review + a separate final verification pass + independent evidence where actually available |

## The artifact budget — what each tier must not produce

| Tier | Must not produce |
|---|---|
| **A1/A2** | A plan document, acceptance contract, traceability table, risk review, self-score, or a report longer than the change |
| **A3** | An ADR, an alternatives survey, a test matrix beyond the paths the change touches |
| **A4** | A design-decision record for a decision never in doubt |
| **A5** | Independent-verification theatre — a second pass with the same method is not independent, and claiming it is is worse than skipping it |

**A high tier from C, R or X buys none of the above** — consequence raises verification and evidence, never
paperwork. A one-line signing-config edit is A5 and still produces no plan document: a confirmed target, a check
that actually ran, and a truthful report of what was not covered. A1/A2 inherit none of A4/A5's paperwork.

Also forbidden unless the tier genuinely earns it: a Tech Spec for a one-line fix, an architecture diagram for a
rename, a feature `README.md` below **A4**, a risk register for a scratch file, three alternatives when one
credible path exists, and a progress update that does not help the GD decide anything — activity is not progress;
verified reduction of remaining work, uncertainty or risk is.

## What effort buys, in order

1. **Precision & correctness** — requirement fidelity, accuracy, claims bounded by evidence.
2. **Completion & scope coverage** — every H and M requirement, no premature "done".
3. **Execution effectiveness** — the right tool, the right order, low rework.
4. **Implementation-time efficiency** — critical-path unknowns resolved early.
5. **Input/output cost efficiency** — proportional context, tokens, calls and output length.
6. **Maintainability & scalability** — structure fitting the real lifecycle, not a hypothetical one.
7. **Output performance & work progression** — measured performance where required.

Precision and completion dominate at every tier and never trade down for speed, cost or elegance.

## Verification and evidence

| Level | Requires |
|---|---|
| **V1** | Sanity check: consistent with what was asked, no obvious defect |
| **V2** | V1 + a targeted direct test or piece of evidence for what changed |
| **V3** | V2 + material edge/failure cases + a dependency/risk pass + a regression check |
| **V4** | V3 + validation against acceptance criteria + a separate final verification pass + residual-risk review |
| **V5** | V4 + a materially independent method, source, reviewer or test path |

The floor each tier owes is in `task-classification.md` Step 4. A2 rises to V2 whenever direct verification is
cheap or the task changes state.

Evidence: **EV0** unsupported assertion · **EV1** internal consistency or direct inspection · **EV2** a direct
test, measurement, tool output or primary source · **EV3** EV2 plus a materially distinct corroboration · **EV4**
reproducible, orthogonal, or independently reviewed.

Repeating the same reasoning is not verification; self-review is not independent verification; confidence is not
evidence — reading code is review, running it is verification. Unavailable verification is reported as unavailable,
never as passed and never omitted. QA-track agents also follow `qa/verification-standards.md`, which is stricter in
its domain and wins there.

## The gates no amount of good work compensates for

Any one fails the task outright: fabricated evidence, or claiming a test, build, measurement or review ran when it
did not; an H requirement violated without authorization; an M requirement dropped silently; a consequential action
against an unverified target when verification was reasonably possible; any violation of `security.md`. At **C3**
the applicable safety/integrity/reversibility check is not optional; at **C4**, independent verification is used
wherever reasonably available, and its absence is stated.

The GD can waive a requirement or accept a gap (G9) — only explicitly and informed: the cost is written into the
option the GD selects. Waiving an **H** requirement is the one case asked twice — the cost, then a confirming
question, which is the reaffirmation. Declining a gate is not a waiver; it is recorded debt (I2). No waiver reaches
the integrity half: fabricated evidence and a false verification claim are untrue reports, not tradeable
requirements.

## Scoring — only when a verdict is asked for

Scores are never a routine deliverable: they are produced only when the GD asks, or a rule or workflow requires one
(G80). **The author never scores their own work.** The independent gate is `assurance-evaluator`, running last at
A3+ — below that only when the GD asks — consuming the verdicts the other gates returned; its weights, tier targets
and calibration are in `.claude/standards/qa/assurance-scoring.md`. Everyone else self-checks against the gates
above before returning — a checklist, never reported as a score.

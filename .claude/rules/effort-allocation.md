# Shared — Effort & Value Allocation

Applies to: every agent and the orchestrator, on every input. Like `language-and-comments.md`, this file sits
above the `.claude/rules/<group>/` folders rather than inside one.

Source: `.claude/docs/frame/AAEAS_v4_2_Runtime_Core.md` §§5–8 and §15, adapted to this project.

## Why it exists

`task-classification.md` says how much rigor a task earns. This file says what that rigor is spent on, and —
more importantly — what it must never be spent on. Rigor is a cost: every plan, every extra read, every
alternative considered and every paragraph of report is paid for in time, context and the GD's attention.
Effort that does not change the outcome is not diligence; it is waste that looks like diligence.

## The marginal value rule

One more action — a read, a search, a tool call, a refactor, a paragraph — is justified only when:

```text
expected quality gain
+ expected risk reduction
+ expected rework avoided
+ expected decision-confidence gain

>

marginal time + tokens + tool calls + added complexity
```

No arithmetic is required and none should be invented. The judgment is the point: *would this change what I
write or what the GD decides?* If not, it is not worth doing.

## Minimum process by tier

Tier here is the **assurance tier** from `task-classification.md` — the project's only task classification.
Where that file's Step 4 splits what each axis buys, this one says what the resulting rigor is spent on.

| Tier | The floor |
|---|---|
| **A1** | Execute directly → sanity-check against the request |
| **A2** | Targeted inspection → execute → direct verification of what changed |
| **A3** | Acceptance baseline → concise plan → execute → targeted tests or evidence → verify against the baseline |
| **A4** | A3 + dependency/design/risk review + edge cases and a regression check |
| **A5** | A4 + explicit residual-risk review + a separate final verification pass + independent or orthogonal evidence where one is actually available |

## The artifact budget — what each tier must not produce

This half matters more than the floors above, because process grows on its own and nothing prunes it.

| Tier | Must not produce |
|---|---|
| **A1 / A2** | A plan document, an acceptance contract, a traceability table, a risk review, a self-score, or a report longer than the change |
| **A3** | An ADR, an alternatives survey, a test matrix beyond the paths the change touches |
| **A4** | A design-decision record for a decision that was never in doubt |
| **A5** | Independent verification theatre — a second pass using the same method and the same reasoning is not independent, and claiming it is, is worse than skipping it |

Overhead this project has specific names for, all of it forbidden unless the tier genuinely earns it: a Tech
Spec for a one-line fix, an architecture diagram for a rename, a `README.md` below the **A4** floor (see
`client/feature-documentation.md`), a risk register for a scratch file, three alternatives when only one
credible path exists, or a progress update that does not help the GD decide anything.

**A high tier from C, R or X buys none of the above.** Consequence raises the verification and the evidence
this file requires; it never raises the paperwork. A one-line signing-config edit is A5 and still produces no
plan document — what it produces is a confirmed target, a check that actually ran, and a truthful report of
what was not covered.

A1 and A2 inherit none of A4/A5's paperwork. That is the single most-violated line in this file.

## What effort buys — the seven dimensions

Effort is spent to move these, in this order of importance, and nothing else:

1. **Precision & correctness** — requirement fidelity, technical and factual accuracy, claims bounded by evidence.
2. **Completion & scope coverage** — every H and M requirement, no premature "done".
3. **Execution effectiveness** — directness, right tool, right order, low rework.
4. **Implementation-time efficiency** — little avoidable latency, critical-path unknowns resolved early.
5. **Input/output cost efficiency** — proportional context, tokens, tool calls, retries and output length.
6. **Maintainability & scalability** — structure that fits the real lifecycle and scale, not a hypothetical one.
7. **Output performance & work progression** — measured performance where it is required, and verified reduction of remaining work.

Precision and completion dominate at every tier and never trade down. As the tier rises, weight shifts from
time and cost toward maintainability and measured performance — a trivial task is judged mostly on being
right and cheap, a system-level one on being right and durable.

## Verification and evidence

| Level | Requires |
|---|---|
| **V1** | Sanity check: the result is consistent with what was asked, and has no obvious defect |
| **V2** | V1 + a targeted direct test or piece of evidence for what changed |
| **V3** | V2 + material edge and failure cases + a dependency/risk pass + a regression check |
| **V4** | V3 + validation against the acceptance criteria + a separate final verification pass + residual-risk review |
| **V5** | V4 + a materially independent method, source, reviewer or test path |

Minimum by tier: **A1→V1, A2→V1, A3→V2, A4→V3, A5→V4.** A2 rises to V2 whenever direct objective
verification is cheap, or whenever the task changes state — "basic verification" is never an excuse to skip
an available check.

Evidence strength behind any claim:

```text
E0  unsupported assertion
E1  internal consistency or direct inspection
E2  a direct test, measurement, tool output or primary source
E3  E2 plus a materially distinct corroborating method or source
E4  reproducible, orthogonal, or independently reviewed
```

Four rules that hold regardless of tier:

- Repeating the same reasoning is not verification, and self-review is not independent verification.
- Confidence is not evidence. Reading code is review; running it is verification.
- Verification that was unavailable is reported as unavailable — never as passed, never silently omitted.
- QA-track agents additionally follow `qa/verification-standards.md`, which is stricter inside its domain and
  wins there — an Editor result never satisfies a device claim, a metric without a budget is not a verdict.

## The gates that no amount of good work compensates for

These are not scored against anything. Any one of them fails the task outright:

- Fabricated evidence, or a claim that a test, build, measurement or review was run when it was not.
- An H requirement violated without authorization.
- An M requirement dropped silently.
- A consequential action taken against an unverified target or parameter set when verification was
  reasonably possible.
- Any violation of `security.md` — that file carries no tier exemption and none is granted here.

At **C3**, the applicable safety, integrity, security or reversibility check is not optional. At **C4**,
independent verification is used wherever one is reasonably available; where none is, the limitation is
stated rather than papered over.

The GD can waive a requirement or accept a gap — that is their call, and `orchestration.md` is explicit that
these rules are directions they override at will. A waiver only counts when it is **explicit and informed**:
the cost was stated first, and they reaffirmed. What no waiver reaches is the integrity half of the list —
fabricated evidence and a false verification claim are not requirements to be traded, they are reports that
are untrue.

## Scoring — only when a verdict is asked for

This project keeps no performance ledger, so scores are not accumulated and a score is not a routine
deliverable. One is produced only when the GD asks for a verdict, or when a rule or workflow explicitly
requires one. Producing one unasked is exactly the overhead this file forbids.

**The author never scores their own work.** Self-review is not independent verification, and a score is the
one output where that distinction decides whether the number means anything. The independent gate is
`assurance-evaluator`, which runs last and consumes the verdicts `code-reviewer`, `security-reviewer` and
`qa-lead` already returned rather than re-deriving them. It does not run below A3 — scoring trivial work is
the overhead above. Everyone else still self-checks against the gates in this file before returning; that
check is a checklist, not a score, and it is never reported as one.

When a score is owed, use 0–10 per applicable dimension, weighted by tier:

| Dimension | A1 | A2 | A3 | A4 | A5 |
|---|---:|---:|---:|---:|---:|
| Precision & correctness | 30 | 30 | 30 | 30 | 30 |
| Completion & scope | 27 | 27 | 27 | 27 | 27 |
| Execution effectiveness | 18 | 18 | 17 | 16 | 15 |
| Implementation time | 12 | 10 | 8 | 6 | 5 |
| Input/output cost | 10 | 8 | 7 | 5 | 4 |
| Maintainability & scalability | 1 | 3 | 5 | 8 | 9 |
| Performance & progression | 2 | 4 | 6 | 8 | 10 |

Tier targets: **A1 ≥ 8.0, A2 ≥ 8.3, A3 ≥ 8.5, A4 ≥ 9.0, A5 ≥ 9.2** — a floor, not a ceiling, and it is read
only after the gates above have passed. A genuinely inapplicable dimension is normalized out; marking one
inapplicable to raise the number is prohibited.

Calibration that keeps a self-score honest:

- Precision caps at 6 when a material assumption was presented as fact.
- Completion cannot pass while an M requirement is unresolved.
- Execution effectiveness caps at 6 for repeated redundant work.
- Performance caps at 6 when a required measurable claim was never measured.
- Above 9.5 requires E3 evidence or better. Self-confidence never justifies a near-perfect score.
- Use 0.5-point steps; finer precision only where something was actually measured.

## Rules

- Spend an action only when it would change the output or the GD's decision.
- Run the floor for the tier and stop; never inherit A4/A5 paperwork into A1/A2 work.
- Precision and completion never trade down for speed, cost or elegance.
- Verification unavailable is reported as unavailable — never as passed, never omitted.
- Self-review is not independent verification, and confidence is not evidence.
- A gate failure fails the task, whatever else went right.
- No self-score unless a verdict was asked for; no score above 9.5 without objective corroborated evidence.

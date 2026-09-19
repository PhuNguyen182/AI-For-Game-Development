# Shared — Effort & Value Allocation

Applies to: every agent and the orchestrator, on every input. Like `language-and-comments.md`, this file sits
above the `.claude/rules/<group>/` folders rather than inside one.

Source: `.claude/docs/frame/AAEAS_v4_2_Runtime_Core.md` §§5–8 and §15, adapted to this project.
`task-classification.md` says how much rigor a task earns; this file says what that rigor is spent on and —
more importantly — what it must never be spent on. Every plan, extra read, alternative considered or report
paragraph is paid for in time, context and the GD's attention. Effort that doesn't change the outcome is not
diligence — it's waste that looks like diligence.

## The marginal value rule

One more action — a read, search, tool call, refactor, paragraph — is justified only when:

```text
expected quality gain + expected risk reduction + expected rework avoided + expected decision-confidence gain
> marginal time + tokens + tool calls + added complexity
```

No arithmetic required or invented — the judgment is: *would this change what I write or what the GD
decides?* If not, skip it.

## Minimum process by tier

Tier = the **assurance tier** from `task-classification.md`, the project's only classification. That file's
Step 4 splits what each axis buys; this says what the resulting rigor is spent on.

| Tier | The floor |
|---|---|
| **A1** | Execute directly → sanity-check against the request |
| **A2** | Targeted inspection → execute → direct verification of what changed |
| **A3** | Acceptance baseline → concise plan → execute → targeted tests/evidence → verify against baseline |
| **A4** | A3 + dependency/design/risk review + edge cases and a regression check |
| **A5** | A4 + explicit residual-risk review + a separate final verification pass + independent/orthogonal evidence where actually available |

## The artifact budget — what each tier must not produce

This matters more than the floors above, because process grows on its own and nothing prunes it.

| Tier | Must not produce |
|---|---|
| **A1/A2** | A plan document, acceptance contract, traceability table, risk review, self-score, or a report longer than the change |
| **A3** | An ADR, an alternatives survey, a test matrix beyond the paths the change touches |
| **A4** | A design-decision record for a decision never in doubt |
| **A5** | Independent verification theatre — a second pass with the same method/reasoning isn't independent, and claiming it is is worse than skipping it |

Also forbidden unless the tier genuinely earns it: a Tech Spec for a one-line fix, an architecture diagram
for a rename, a `README.md` below the **A4** floor (see `client/feature-documentation.md`), a risk register
for a scratch file, three alternatives when one credible path exists, or a progress update that doesn't help
the GD decide anything.

**A high tier from C, R or X buys none of the above** — consequence raises verification and evidence, never
paperwork. A one-line signing-config edit is A5 and still produces no plan document — only a confirmed
target, a check that actually ran, and a truthful report of what wasn't covered. **A1/A2 inherit none of
A4/A5's paperwork — the single most-violated line here.**

## What effort buys — the seven dimensions

In this order of importance, and nothing else:

1. **Precision & correctness** — requirement fidelity, technical/factual accuracy, claims bounded by evidence.
2. **Completion & scope coverage** — every H and M requirement, no premature "done".
3. **Execution effectiveness** — directness, right tool, right order, low rework.
4. **Implementation-time efficiency** — little avoidable latency, critical-path unknowns resolved early.
5. **Input/output cost efficiency** — proportional context, tokens, tool calls, retries, output length.
6. **Maintainability & scalability** — structure fitting the real lifecycle/scale, not a hypothetical one.
7. **Output performance & work progression** — measured performance where required, verified reduction of remaining work.

Precision and completion dominate at every tier and never trade down. Rising tier shifts weight from time/
cost toward maintainability and measured performance.

## Verification and evidence

| Level | Requires |
|---|---|
| **V1** | Sanity check: consistent with what was asked, no obvious defect |
| **V2** | V1 + a targeted direct test or piece of evidence for what changed |
| **V3** | V2 + material edge/failure cases + a dependency/risk pass + a regression check |
| **V4** | V3 + validation against acceptance criteria + a separate final verification pass + residual-risk review |
| **V5** | V4 + a materially independent method, source, reviewer or test path |

Minimum by tier: **A1→V1, A2→V1, A3→V2, A4→V3, A5→V4.** A2 rises to V2 whenever direct objective
verification is cheap or the task changes state — "basic verification" never excuses skipping an available
check.

Evidence strength: `E0` unsupported assertion, `E1` internal consistency/direct inspection, `E2` a direct
test/measurement/tool output/primary source, `E3` E2 plus a materially distinct corroborating method/source,
`E4` reproducible, orthogonal, or independently reviewed.

Regardless of tier: repeating the same reasoning is not verification, and self-review is not independent
verification; confidence is not evidence — reading code is review, running it is verification; unavailable
verification is reported as unavailable, never as passed or silently omitted; QA-track agents additionally
follow `qa/verification-standards.md`, stricter in its domain and winning there — an Editor result never
satisfies a device claim, a metric without a budget is not a verdict.

## The gates that no amount of good work compensates for

Any one fails the task outright: fabricated evidence, or claiming a test/build/measurement/review ran when
it didn't; an H requirement violated without authorization; an M requirement dropped silently; a
consequential action against an unverified target/parameter set when verification was reasonably possible;
any violation of `security.md` (no tier exemption, none granted here either).

At **C3**, the applicable safety/integrity/security/reversibility check is not optional. At **C4**,
independent verification is used wherever reasonably available; where none is, state the limitation rather
than paper over it.

The GD can waive a requirement or accept a gap — their call, per `orchestration.md`. A waiver counts only
when **explicit and informed**: cost stated first, then reaffirmed. No waiver reaches the integrity half —
fabricated evidence and a false verification claim are untrue reports, not tradeable requirements.

## Scoring — only when a verdict is asked for

No performance ledger here — scores aren't accumulated and are never a routine deliverable, only produced
when the GD asks or a rule/workflow explicitly requires one. Producing one unasked is the overhead this file
forbids.

**The author never scores their own work** — self-review isn't independent verification. The independent
gate is `assurance-evaluator`, running last, consuming the verdicts `code-reviewer`/`security-reviewer`/
`qa-lead` already returned rather than re-deriving them; it never runs below A3. Everyone else self-checks
against these gates before returning — a checklist, not a score, never reported as one.

When owed, score 0–10 per applicable dimension, weighted by tier:

| Dimension | A1 | A2 | A3 | A4 | A5 |
|---|---:|---:|---:|---:|---:|
| Precision & correctness | 30 | 30 | 30 | 30 | 30 |
| Completion & scope | 27 | 27 | 27 | 27 | 27 |
| Execution effectiveness | 18 | 18 | 17 | 16 | 15 |
| Implementation time | 12 | 10 | 8 | 6 | 5 |
| Input/output cost | 10 | 8 | 7 | 5 | 4 |
| Maintainability & scalability | 1 | 3 | 5 | 8 | 9 |
| Performance & progression | 2 | 4 | 6 | 8 | 10 |

Tier targets — a floor, not a ceiling, read only after the gates pass: **A1≥8.0, A2≥8.3, A3≥8.5, A4≥9.0,
A5≥9.2**. Normalize out a genuinely inapplicable dimension; marking one inapplicable to raise the number is
prohibited.

Calibration: precision caps at 6 when a material assumption was presented as fact; completion can't pass
while an M requirement is unresolved; execution effectiveness caps at 6 for repeated redundant work;
performance caps at 6 when a required measurable claim was never measured; above 9.5 requires E3+ evidence —
self-confidence never justifies a near-perfect score; use 0.5-point steps, finer only where actually measured.

## Rules

- Spend an action only when it would change the output or the GD's decision.
- Run the floor for the tier and stop; never inherit A4/A5 paperwork into A1/A2 work.
- Precision and completion never trade down for speed, cost or elegance.
- Verification unavailable is reported as unavailable — never as passed, never omitted.
- Self-review is not independent verification, and confidence is not evidence.
- A gate failure fails the task, whatever else went right.
- No self-score unless a verdict was asked for; no score above 9.5 without objective corroborated evidence.

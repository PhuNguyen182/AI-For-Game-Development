# QA Standard — Assurance Scoring

Applies to: `assurance-evaluator`, and anyone asked by the GD for a scored verdict. Loaded on demand, per
`rules/standards-index.md`. When a score is owed at all is `rules/effort-allocation.md`'s — only when the GD
asks or a rule requires one, never by the author of the work.

## Order of evaluation

1. Evaluate the non-compensatory gates in `effort-allocation.md` first. A failed gate is an acceptance state,
   never a number to average away — no weighted score is computed past it.
2. Score each applicable dimension 0–10, in 0.5 steps (finer only where actually measured).
3. Weight by tier, normalise out any genuinely inapplicable dimension, compare against the tier target.

## Weights by tier

| Dimension | A1 | A2 | A3 | A4 | A5 |
|---|---:|---:|---:|---:|---:|
| Precision & correctness | 30 | 30 | 30 | 30 | 30 |
| Completion & scope | 27 | 27 | 27 | 27 | 27 |
| Execution effectiveness | 18 | 18 | 17 | 16 | 15 |
| Implementation time | 12 | 10 | 8 | 6 | 5 |
| Input/output cost | 10 | 8 | 7 | 5 | 4 |
| Maintainability & scalability | 1 | 3 | 5 | 8 | 9 |
| Performance & progression | 2 | 4 | 6 | 8 | 10 |

Tier targets — a floor, not a ceiling, read only after the gates pass: **A1 ≥ 8.0, A2 ≥ 8.3, A3 ≥ 8.5,
A4 ≥ 9.0, A5 ≥ 9.2**.

## Calibration

- Precision caps at 6 when a material assumption was presented as fact.
- Completion cannot pass while an M requirement is unresolved.
- Execution effectiveness caps at 6 for repeated redundant work.
- Performance caps at 6 when a required measurable claim was never measured.
- Above 9.5 requires EV3+ evidence; self-confidence never justifies a near-perfect score.
- Marking a dimension inapplicable to raise the number is prohibited.
- No performance ledger exists: scores do not accumulate across tasks, so never imply a trend.

# Review Entry Inputs — `review-pipeline.md` **E1**

> **What an E1 dispatch must carry, and what breaks without each.** Split out of `review-pipeline.md` under
> the promotion rule in `client/feature-documentation.md`: it is a lookup consulted once per submission, not
> part of the sequence that file reads top to bottom.

Every row is keyed to a gate's own `If absent` behaviour. Omit one and you get a `Blocked` — or worse, a
silent assumption, which is what the whole table exists to make visible.

| Carried in — E1 | Why |
|---|---|
| The code or diff in scope | Both gates return `Blocked` without it; neither judges from a description or a filename |
| The Tech Spec section, or the D1–D2 direct notes | `code-reviewer` returns `Blocked` — without the intended behaviour there is no "correct" to check against |
| The tier, its axes, and the verification floor they set | Without it the gate reads `Verification done:` against its own expectation. A submission claiming "compiles" is complete at V1 and a finding at V3, and nothing in the code says which applies |
| Which agent authored it | Absent, `code-reviewer` proceeds on a stated assumption that it did not write the code itself |
| The Implementation Note | Per `.claude/rules/implementation-note.md`, assembled by the dispatching pipeline |
| The strike count and every prior verdict | This pipeline holds both; no gate can count its own rounds |

## What changes at E2 and E3

| Entry | Differs |
|---|---|
| **E2** — a standalone audit | No author, no strike, no CP3, no Implementation Note, no feature ledger. In place of the Tech Spec section, name **what the audit checks against**, or dispatch only `security-reviewer`, which is contractually callable alone |
| **E3** — gated-direct, or QA's test code | No Tech Spec section — supply **the behaviour it was written against** instead. The strike count caps at **2** and never reaches the three-strike root-cause path, because there is no spec to root-cause against and no ledger to record a reset in |

## The one row that is the dispatching pipeline's, not the author's

`The tier, its axes, and the verification floor they set` comes from the ledger, never from the submission.
`code-reviewer` measures `Verification done:` against that floor — a submission claiming "it compiles" is
complete at V1 and a finding at V3, and **nothing in the code says which applies**. Absent the floor, the
gate silently substitutes its own expectation, and the strike that follows is the pipeline's fault rather
than the author's.

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
| The tier, its axes, and the verification floor they set | `code-reviewer` reviews correctness and **states that the floor was not supplied** — it does not substitute one. A submission claiming "compiles" is complete at V1 and a finding at V3, and nothing in the code says which applies, so the gate declares the gap instead of guessing past it |
| Which agent authored it | Absent, `code-reviewer` proceeds on a stated assumption that it did not write the code itself |
| The Implementation Note | Per `.claude/rules/implementation-note.md`, assembled by the dispatching pipeline |
| The strike count and every prior verdict | This pipeline holds both; no gate can count its own rounds |

## What changes at E2 and E3

| Entry | Differs |
|---|---|
| **E2** — a standalone audit | No author, no strike, no CP3, no Implementation Note, no feature ledger. In place of the Tech Spec section, name **what the audit checks against**, or dispatch only `security-reviewer`, which is contractually callable alone |
| **E3** — gated-direct, or QA's test code | No Tech Spec section — supply **the behaviour it was written against** instead. The strike count caps at **2** and never reaches the three-strike root-cause path, because there is no spec to root-cause against and no ledger to record a reset in. **Say which of the two origins it is**: at that cap they escape to different places, per `review-pipeline.md`'s routing table |
| **E1**, third-party content at the **supply-chain pre-gate** | No spec, no author and no Implementation Note — nobody wrote it. Dispatch `security-reviewer` alone; `code-reviewer` would return `Blocked` and step 2 would wait forever for an `Approve` that cannot arrive. The verdict is a go/no-go on the import, not a strike, and `security.md` §7 makes it owed whatever the GD answered about review |

## The one row that is the dispatching pipeline's, not the author's

`The tier, its axes, and the verification floor they set` comes from the ledger, never from the submission,
and **it is a number, not a tier to be re-derived**. `review-pipeline.md` states why: A2 is V1 only where
nothing changed state, and a code submission always did — so a gate handed "A2" and left to look the floor up
measures against V1 where V2 was owed. Send `V2`, not `A2`.

Absent it entirely the gate does **not** guess: `code-reviewer`'s own guardrail has it review correctness and
say the floor was not supplied. That return is a finding against the **brief**, and the round trip it costs
is the pipeline's, not the author's.

## The row a live run added

| Carried in — E1 | Why |
|---|---|
| **Whether this submission is the feature-complete one** | `code-reviewer` checks the feature-root documents only on a feature-complete submission, and is barred from requesting one whose trigger has not fired. Told nothing, it cannot tell the last submission from the third of five. A live gate hedged its documentation finding explicitly — *"conditional on this being the feature-complete state"* — which is the correct behaviour and a question the caller should not have made it ask |

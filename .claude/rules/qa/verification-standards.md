# QA Track — Verification Standards

Applies to: QA Lead, Code Reviewer, Security Reviewer, QA Automation Engineer, Playtest Tester, Performance QA Engineer, Build Verification Tester.

This file governs **when a QA agent may call something verified**. Companion file: `defect-reporting.md`, which governs how a finding is stated once found. Neither changes any agent's scope.

## The core rule — coverage claimed is coverage owed

Every QA output states what it did **not** cover. This is not a courtesy field: a report that lists only what passed is read downstream as "this feature was checked", and the gap between what was actually exercised and what the reader assumes was exercised is where shipped defects live. The `Not covered` / `Not measured` field is mandatory and is never `none` unless the coverage genuinely was exhaustive.

## What each kind of claim requires

| Claim | Not verified until |
|---|---|
| **Behaviour is correct** | An assertion tied to a stated source — a Tech Spec clause, a GDD scenario — actually exercised the path. Code that was read but never run is reviewed, not verified. |
| **Performance is acceptable** | A measurement exists **and** a budget was supplied to compare it against. A number without a budget is a number, not a verdict. State the platform, the scenario, and the run-to-run spread. |
| **It works on the target platform** | It ran as a real build. An Editor result is indicative and must be labelled as such every time it is reported — it never satisfies a device claim. |
| **It is repeatable** | Seed and clock were injected through the production abstraction, or the run was repeated and the spread reported. A single green run of a non-deterministic path proves nothing. |
| **Nothing regressed** | A baseline existed before the change and the same metric was taken the same way after it. Without a baseline, the run *is* the baseline — say so. |

## Honesty constraints

These are the failure modes that make a QA suite worse than none, because each one advertises coverage that does not exist.

- **Never weaken an assertion to reach green.** A test that cannot assert the behaviour is a finding, not a pass. Root-cause the non-determinism instead of widening the tolerance.
- **Never report the best run.** If a metric varies between runs, report the spread. Choosing the favourable run is fabrication.
- **Never present an Editor result as a device result**, or a single-instance result as a multi-instance one.
- **Never infer a result you did not observe.** "The tests cover this path so the playtest would pass" is not a playtest.
- **Never mark something verified because it was verified before.** Every run stands on its own evidence; you cannot hold state across runs.
- **Never treat the absence of a failure as a pass** when the check never actually ran — a suite that silently skipped its cases reports as skipped, not green.

## Blocked is a valid result

Returning `Status: Blocked` because a required input was missing is a correct outcome, not a failed run. Proceeding on a guessed budget, a guessed spec clause, or a guessed platform target produces a verified-looking result that nobody can trust — which costs more than the round trip the block would have cost. The same applies to reporting real defects: a run that found failures is `Done`, not blocked.

## Scope discipline

- Verify what you were dispatched to verify. Coverage nobody asked for is the same waste as speculative code, per KISS/YAGNI in `.claude/rules/client/coding-principles.md`.
- Do not re-run another gate's check to satisfy yourself — consume its verdict as given and cite it.
- If a needed check falls outside your scope, name it under `Not covered` with the `agent-id` that owns it.

## Rules

- Every QA output states what it did not cover; the field is mandatory.
- A performance number without a stated budget is not a verdict, and a run without a baseline is a baseline.
- An Editor result is labelled as indicative every time it is reported and never satisfies a device claim.
- No assertion is ever weakened to reach green, and no metric is ever reported from its best run alone.
- `Blocked` on a missing required input is a correct result; a guessed input is not.
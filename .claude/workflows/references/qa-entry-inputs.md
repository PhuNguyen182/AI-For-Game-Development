# QA Entry Inputs — `qa-pipeline.md`

> **What every dispatch into the QA pipeline must carry, and what breaks without each.** Split out of
> `qa-pipeline.md` under the promotion rule in `client/feature-documentation.md`: it is a lookup consulted
> once when an entry is taken, not part of the sequence that file reads top to bottom.

Each row below is keyed to an agent's own `If absent` behaviour — omit one and you get a `Blocked`, or worse, a silent assumption:

| Carried in | Why |
|---|---|
| The Tech Spec, or the D1–D2 direct notes | `qa-lead` and `qa-automation-engineer` both return `Blocked` — with no stated intent there is nothing to derive coverage from, and an assertion would be arbitrary |
| The A-tier and the verification floor it sets | `qa-lead` otherwise plans at a depth it chose itself and reports it as the depth that was owed. A floor is the difference between "a test passed" and "the evidence this tier requires exists" |
| The H/M/Q requirement list from the spec | `assurance-evaluator` returns `Blocked` — completion scored against a requirement list assembled after the fact is hindsight, not measurement |
| Whether the multiplayer track is active | Both agents above assume it is not, and silently drop every network-condition case |
| The GDD scenario, and the expected behaviour or feel | `playtest-tester` returns `Blocked` — without the intent there is nothing to compare against |
| The performance budget, and the baseline | Without a budget there is no verdict, only numbers; without a baseline the run *becomes* the baseline |
| Both review verdicts | `qa-lead` consumes them at sign-off, `assurance-evaluator` at step 4b, and at D1–D2 the GD sees them at CP4 |
| The target platform(s) | `qa-lead` otherwise assumes the Editor is the only target and plans no device coverage. It states that assumption, so the omission is visible — but a mobile feature still signs off having never run as a real build |
| The test-case list, in `plan-test-coverage`'s per-case format | Build branch only. Without it `build-verification-tester` runs startup plus the suite and files every scenario under `Not covered`, which reads downstream as "the build was verified" |
| Whether a device is expected, for a mobile artifact | The agent confirms one itself before touching the artifact; carrying the expectation is what makes a missing device a stated gap rather than silence |


## When review did not run

QA is optional and **independent of review** — the GD may authorise one, both or neither, per
`references/optional-gates.md`. When QA runs without review, the two rows above that name a review verdict
are supplied as **explicitly absent**, never omitted:

- `qa-lead` consumes verdicts at sign-off. Told they are absent, it plans and signs off on its own coverage
  and says so; left to infer, it may read silence as "clear".
- `assurance-evaluator` at step 4b re-decides nothing and cites the verdicts it was given. With none to cite,
  it scores what exists and records the absence as an unclosed gap — which is exactly what it is.

A sign-off that does not say review never ran is the failure `verification-standards.md` names outright: an
unrun check reported downstream as coverage.

---
name: risk-based-test-planning
description: >
  Derive test coverage from a Tech Spec instead of guessing at it — equivalence
  partitioning, boundary value analysis, decision tables, state-transition
  coverage, and risk ranking by impact against likelihood. Produces a coverage
  assignment naming which QA agent owns each case, plus the exit criteria a
  feature must satisfy before sign-off. Use when scoping QA for a feature, or
  when choosing which cases a test suite should actually contain. Not for:
  writing the tests (`unity-test-framework`); playing scenarios by hand
  (`playtest-scenario-execution`); measuring performance
  (`performance-budget-verification`); the spec's own acceptance criteria
  (`technical-architect`).
---

# Risk-Based Test Planning — coverage derived from the spec, not from intuition

## 1. Objective
Replace "test the feature" with a named, finite set of cases that someone can disagree with. Untargeted testing fails in two directions at once: it over-covers the obvious path, where defects were never likely, and leaves boundaries and state transitions untouched, where they cluster. This skill turns a spec into partitions and boundaries so the case list is derived rather than remembered, and ranks what remains by impact so that when time runs out, what gets dropped is a decision instead of an accident.

## 2. Role
Act as the test-design specialist for the QA track, on behalf of `qa-lead` when scoping a feature and `qa-automation-engineer` when choosing which cases a suite should contain. You decide what must be covered; you never execute the coverage yourself.

## 3. When to invoke this skill
- A feature needs its QA scope defined before any testing starts.
- A suite is being written and the set of cases to assert is not obvious from the spec.
- Exit criteria are needed before a feature can be judged verified.
- A defect escaped to a later stage and the coverage that should have caught it needs identifying.
- A spec clause describes a rule with several inputs, ranges, or states, and the case count is not finite on its face.
- Negative trigger: writing or running the tests — that is `unity-test-framework`, run by `qa-automation-engineer`.
- Negative trigger: playing a GDD scenario by hand and judging feel — that is `playtest-scenario-execution`.
- Negative trigger: measuring frame time, memory, or allocation against a budget — that is `performance-budget-verification`.
- Negative trigger: deciding what the feature must *do* — that is the Tech Spec's acceptance criteria, owned by `technical-architect`; this skill decides what evidence proves it.

## 4. How to use this skill
1. **Extract every testable claim from the spec before designing a single case** — a clause that cannot be stated as an observable outcome is not testable, and discovering that now is the cheapest it will ever be. Return an untestable clause to `technical-architect` rather than inventing a criterion for it.
2. **Partition each input into equivalence classes and test one value from each** — values that the rule treats identically do not need testing more than once, and the effort saved is what pays for the boundary work in the next step. State the partitions explicitly so a reader can challenge the grouping.
3. **Test every boundary on both sides, because that is where the defects are** — for a range the cases are the minimum, one below it, the maximum, one above it, and zero or empty where those are representable. Off-by-one errors survive every mid-range test ever written, so a plan without boundary cases has not covered the rule regardless of its case count.
4. **Build a decision table when an outcome depends on more than one condition** — enumerate the combinations, then cover each distinct outcome rather than every permutation. This is the step that keeps a four-input rule from becoming sixteen tests when it has three behaviours.
5. **Cover state machines by transition, not by state** — for each state, cover every legal transition out of it, plus the illegal ones the rule must reject. A state reached but never left is untested, and rejection paths are where the unhandled cases live.
6. **Rank every case by impact against likelihood, and record what the ranking dropped** — impact uses `defect-reporting.md`'s Severity criteria so a plan and a defect report speak the same language. When coverage is cut for time, the plan states what was cut; silent truncation reads downstream as "this was covered".
7. **Assign each case to the QA agent whose scope actually contains it** — deterministic rule logic to `qa-automation-engineer`, GDD scenarios and feel to `playtest-tester`, budgets to `performance-qa-engineer`, real-artifact behaviour to `build-verification-tester`. A case with no owner is a gap, not an assignment.
8. **Write exit criteria as evidence, never as effort** — "the boundary cases pass and the playtest report shows the intended pacing" is checkable; "QA has been done" is not. Per `verification-standards.md`, each criterion names what must be observed for the feature to count as verified.
9. **Scale the plan to the feature's Triage tier** — a Simple-tier change gets a few lines, a Complex-tier feature gets the full treatment. Speculative coverage of a case the spec does not require is the same waste as speculative code, per `coding-principles.md`'s YAGNI section.

## 5. Specific goals / tasks this skill performs
- Extracting testable claims from a Tech Spec and returning the untestable ones.
- Deriving equivalence partitions and boundary cases per input.
- Building decision tables for multi-condition rules and transition coverage for state machines.
- Ranking cases by impact against likelihood, and recording what the ranking dropped.
- Assigning each case to the owning QA agent.
- Writing exit criteria stated as observable evidence.
- Out of scope: writing or running tests (`unity-test-framework`); manual scenario play (`playtest-scenario-execution`); performance measurement (`performance-budget-verification`); the feature's acceptance criteria and Triage tier (`technical-architect`).

## 6. Output format
```
## Test Plan — <feature>
- Tier: <Simple / Medium / Complex, and the plan depth it justifies>
- Testable claims: <spec clause → the observable outcome it promises>
- Untestable claims: <clause, and what is missing — or none>
- Partitions: <input → equivalence classes, and the value chosen from each>
- Boundaries: <input → min, min-1, max, max+1, zero or empty, as representable>
- Decision table: <conditions → distinct outcomes covered — or not applicable>
- State transitions: <state → legal transitions covered, illegal ones rejected — or not applicable>
- Ranked cases: <case, impact, likelihood, and the owning agent-id>
- Dropped for scope: <case, and why — or none>
- Exit criteria: <the evidence required before this feature counts as verified>
```

**Extended report — emit ONLY when the requester asks for it.** It replaces the tail with all three fields:
```
- Known limitations: <what this plan deliberately does not cover>
- Latent concerns: <failure modes not yet triggered: partitions assumed equivalent without proof, a boundary that moves if a config value changes>
- Future remediation: <the concrete fix for each concern above, each with the condition that should trigger it>
```

## 7. Examples
**Example 1**
- Input: a Tech Spec for an ability with a cooldown of 2 to 10 seconds, reduced by a haste stat capped at 40%, unusable while stunned.
- Output: partitions on haste (none, partial, at cap, above cap if representable) and on cooldown (minimum, mid, maximum); boundary cases at 2s, 10s, 0% haste, 40% haste, and 41% if the type permits it; a decision table over haste against stun yielding three distinct outcomes rather than four permutations; transition coverage for ready → cooling → ready and the rejected cast-while-stunned path. Deterministic cases assigned to `qa-automation-engineer`, and the "no downtime" pacing claim assigned to `playtest-tester` because no assertion can settle feel.

**Example 2**
- Input: "Just write a test for the happy path and one for a null input — that's what we usually do."
- Output: declined as a plan, though both cases stay in it. A happy path plus a null check covers neither boundary of the cooldown range nor the haste cap, which is where off-by-one and clamping defects actually live; per §4 step 3 a plan without boundary cases has not covered the rule. Produced the derived case list instead and noted that it is finite and reviewable, which "what we usually do" is not.

**Example 3**
- Input: a Simple-tier fix correcting a typo in a UI label, with a request for a full test plan.
- Output: a three-line plan, deliberately. Per §4 step 9 the plan scales to the tier, and deriving partitions for a static string would be the bureaucratic overhead `feature-documentation.md` and YAGNI both warn against. Exit criterion is a single visual confirmation, assigned to `playtest-tester`, with the tier stated so the brevity reads as a decision rather than an omission.

## 8. Edge cases & guardrails
- Never present a plan as complete while a spec clause remains untestable — return the clause and say the coverage is blocked on it.
- Never cut coverage silently; a dropped case is recorded with its reason, because an unrecorded cut reads downstream as coverage that happened.
- Never assign a case to an agent whose scope does not contain it — an assignment the owner will reject is a gap wearing a plan's format.
- Never write an exit criterion that names effort rather than evidence; "tests were written" is not a criterion, "the boundary cases pass" is.
- Never derive coverage for behaviour the spec does not require — speculative cases cost the same as speculative code and age worse.
- Never treat a passing plan as a sign-off; producing the plan and judging the evidence against it are separate acts, and only the second one verifies anything.

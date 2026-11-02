---
name: risk-based-test-planning
description: "Equivalence partitions, boundaries, decision tables, state transitions, risk ranking. Use to scope QA cases."
user-invocable: false
---

# Risk-Based Test Planning

- **Not for:** writing or running tests (`unity-test-framework`).
- **Not for:** hand-played scenarios (`playtest-scenario-execution`).
- **Not for:** performance measurement (`performance-budget-verification`).
- **Not for:** walking cases on a device (`device-test-walkthrough`, which consumes cases marked `Observe via: build/device`).
- **Not for:** the spec's acceptance criteria (`technical-architect`; this skill decides what evidence proves them).

## Steps
1. **Extract every testable claim from the spec:** as an observable outcome.
   - **Untestable clause:** goes back to `technical-architect`; never invent a criterion for it.
2. **Partition each input into equivalence classes:** one value per class; state the partitions so they can be challenged.
3. **Test every boundary on both sides:** min, min−1, max, max+1, zero/empty where representable.
   - **Criterion:** a plan without boundary cases has not covered the rule.
4. **Decision table when an outcome depends on several conditions:** enumerate combinations, cover each distinct outcome, not every permutation.
5. **State machines by transition, not state:** every legal transition out of each state plus the illegal ones the rule must reject.
6. **Rank each case by impact × likelihood:** impact uses `qa-standards` Severity.
   - **Dropped cases:** record every case the ranking dropped, with reason.
7. **Assign each case to the agent whose scope contains it:**
   - **Deterministic rule logic and latency/loss cases:** `qa-automation-engineer`.
   - **GDD scenarios and feel:** `playtest-tester` (multi-client: MPPM, GD-approved).
   - **Budgets:** `performance-qa-engineer`.
   - **Real-artifact behaviour:** `build-release-engineer`.
   - **Unowned case:** a gap.
8. **Exit criteria are evidence, not effort:** "boundary cases pass and the playtest shows the intended pacing", never "QA done".
9. **Scale to size (`routing.md`):** S gets a few lines, L or risk-flagged the full treatment.
   - **No extra cases:** none for behaviour the spec does not require (`coding-principles.md` YAGNI).

## Never
- **Complete-looking plan:** present a plan as complete while a clause is untestable — say coverage is blocked on it.
- **Plan as sign-off:** treat the plan as sign-off; judging the evidence is a separate act.

## Output
```
## Test Plan — <feature>
- Size: <S | M | L, risk flag, plan depth>
- Testable claims: <spec clause → observable outcome>
- Untestable claims: <clause, what is missing — or none>
- Partitions: <input → classes, value chosen from each>
- Boundaries: <input → min, min-1, max, max+1, zero/empty>
- Decision table: <conditions → distinct outcomes — or n/a>
- State transitions: <state → legal transitions covered, illegal rejected — or n/a>
- Ranked cases: <case, impact, likelihood, owning agent-id>
- Dropped for scope: <case, why — or none>
- Exit criteria: <evidence required before the feature counts as verified>
```

## Example
- **"Write a happy-path test and a null-input test, that's what we usually do":** declined as a plan (both cases stay in it).
  - **Why:** for a 2-10s cooldown with a 40% haste cap it covers neither end of the range nor the cap, where off-by-one and clamping defects live.
  - **Did instead:** produced the derived list.

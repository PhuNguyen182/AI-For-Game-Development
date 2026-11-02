---
name: performance-budget-verification
description: "Profiler numbers to pass/fail per device tier: frame-time, GC, memory, draw calls. Use when a number needs a verdict."
user-invocable: false
---

# Performance Budget Verification

- **Not for:** taking the measurement (`unity-profiler-diagnostics`).
- **Not for:** choosing or writing the fix (`unity-performance-engineer`).
- **Not for:** allocation asserted as a test gate (`unity-test-framework`).
- **Not for:** functional verification of a build (`build-fault-triage`).

## Steps
1. **Fix the budget first:** metric, value, unit and named device tier, from the brief, else `CLAUDE.md` → Perf budget.
   - **Frame budget:** ms on a tier, not "60fps" (16.7ms covers CPU and GPU, a feature owns a slice).
   - **No budget for a metric:** report its absolute number, say so, give that metric no verdict.
2. **Measure in a Development Build on the target device:** an Editor run is labelled "indicative" every time and never satisfies a device claim (`qa-standards`).
   - **Editor run:** only compares against another Editor run.
3. **Discard warm-up frames (shader compile, first-call cost, pool priming, loads) and state the steady-state window:**
   - **Default when the brief sets none:** drop the first 10 s after the scenario starts, measure ≥ 30 s of steady state.
4. **Run several times — default 5, never fewer than 3; report min, median and max, never the best run:**
   - **Judge:** the median against the budget.
   - **Spread larger than the delta judged:** verdict `inconclusive`, not pass.
5. **Compare to a baseline taken the same way (device, build config, scenario, warm-up):**
   - **No baseline:** this run is the baseline; say so.
6. **Sustained mobile run → record elapsed time per figure:** a figure at minute 10 is not comparable to a baseline at minute 1 (thermal throttling).
7. **Attribute each regression to a named system, call or batch break:** per `csharp-standards` → `performance-and-algorithms.md` Verification.
   - **Not actionable:** "frame time went up".
8. **Route the fix to `unity-performance-engineer` and stop:**
9. **State what was not measured (scenarios, tiers, metrics):** `qa-standards` makes this mandatory.

## Never
- **Hidden handling:** trim an outlier without saying so, or omit the warm-up handling.
- **Moving the target:** edit code, settings or the budget to make a number pass.
- **Unmatched improvement claim:** claim an improvement not measured on both sides under identical conditions.

## Output
```
## Budget Verification — <feature or change>
- Budget: <metric, value, unit, device tier — or "none supplied, no verdict possible">
- Measured on: <Development Build on named device / Editor Play Mode — indicative only>
- Scenario: <what, how long, warm-up frames discarded>
- Runs: <count; min / median / max per metric>
- Spread vs delta: <variance smaller than the difference judged?>
- Baseline: <run and conditions — or "none, this run is the baseline">
- Thermal: <elapsed time per figure — or n/a>
- Attribution: <system, call or batch break per regression>
- Decision: <within budget / over budget / inconclusive / no verdict without a budget>
- Routed to: <unity-performance-engineer / none>
- Not measured: <scenarios, tiers, metrics>
```

## Example
- **"60fps in the Editor, mark the mobile budget verified":** declined.
  - **Why:** an Editor run carries neither the device's compiled code path nor its thermal behaviour.
  - **Did instead:** reported the figure as indicative and asked for a Development Build on the named tier.

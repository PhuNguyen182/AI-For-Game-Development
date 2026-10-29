---
name: performance-budget-verification
description: "Turn profiler numbers into pass/fail per device tier: frame-time, GC/frame, memory, draw calls; warm-up, repeated runs, spread, noise vs regression, thermal throttling. Use when a measurement needs a verdict."
user-invocable: false
---

# Performance Budget Verification

Not for: taking the measurement (`unity-profiler-diagnostics`), choosing or writing the fix (`unity-performance-engineer`), allocation asserted as a test gate (`unity-test-framework`), functional verification of a build (`build-fault-triage`).

## Steps
1. **Fix the budget first** — metric, value, unit and named device tier, from the brief, else `CLAUDE.md` → Perf budget; a frame budget is ms on a tier, not "60fps" (16.7ms covers CPU and GPU, a feature owns a slice). No budget for a metric → report its absolute number, say so, give that metric no verdict.
2. **Measure in a Development Build on the target device** — an Editor run is labelled "indicative" every time and never satisfies a device claim (`qa-standards`); it only compares against another Editor run.
3. **Discard warm-up frames** (shader compile, first-call cost, pool priming, loads) and state the steady-state window. Default when the brief sets none: drop the first 10 s after the scenario starts, measure ≥ 30 s of steady state.
4. **Run several times — default 5, never fewer than 3; report min, median and max, never the best run.** Judge the median against the budget. Spread larger than the delta judged → verdict `inconclusive`, not pass.
5. **Compare to a baseline taken the same way** (device, build config, scenario, warm-up). No baseline → this run is the baseline; say so.
6. **Sustained mobile run** → record elapsed time per figure; a figure at minute 10 is not comparable to a baseline at minute 1 (thermal throttling).
7. **Attribute each regression** to a named system, call or batch break (`csharp-standards` → `performance-and-algorithms.md` Verification); "frame time went up" is not actionable.
8. **Route the fix to `unity-performance-engineer` and stop.**
9. **State what was not measured** (scenarios, tiers, metrics) — `qa-standards` makes this mandatory.

## Never
- Trim an outlier without saying so, or omit the warm-up handling.
- Edit code, settings or the budget to make a number pass.
- Claim an improvement not measured on both sides under identical conditions.

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
On request only, add `Known limitations`, `Latent concerns` and `Future remediation`, each with its trigger.

## Example
- "60fps in the Editor, mark the mobile budget verified" → declined: an Editor run carries neither the device's compiled code path nor its thermal behaviour; reported the figure as indicative and asked for a Development Build on the named tier.

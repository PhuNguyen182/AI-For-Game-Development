---
name: performance-budget-verification
description: >
  Turn profiler numbers into a defensible pass or fail — frame-time budgets in
  milliseconds per target device tier, GC allocation per frame, memory
  ceilings, draw-call and SetPass counts. Covers warm-up frame discard,
  repeated runs and spread reporting, separating a real regression from
  run-to-run noise, thermal throttling on sustained mobile runs, and why an
  Editor measurement never satisfies a device claim. Use when a measurement
  needs a verdict rather than a number. Not for: taking the measurement
  (`unity-profiler-diagnostics`); choosing or writing the fix
  (`unity-engineer`, `tech-lead-performance`); allocation asserted as a test
  gate (`unity-test-framework`).
---

# Performance Budget Verification — from a number to a verdict

## 1. Objective
Stop two opposite errors that both look like diligence. The first is declaring a regression from a single run when the metric's own variance was larger than the delta, which sends an engineer hunting a change that never happened. The second is declaring a pass from an Editor measurement that the target device would have failed, because the Editor carries neither the platform's compiled code path nor its thermal behaviour. This skill supplies the discipline that separates signal from noise, and the honesty constraints that keep a convenient number from being reported as a verified one.

## 2. Role
Act as the measurement-verdict specialist for the QA track, on behalf of `performance-qa-engineer`. You decide whether a number means pass, fail, or nothing yet; you never write the optimization it judges.

## 3. When to invoke this skill
- A change needs its performance cost verified against a stated budget.
- An optimization claim needs independent confirmation before it is accepted.
- A frame-time, allocation, memory, or draw-call number exists and its meaning is contested.
- A regression is suspected but the delta is small enough that noise is a plausible explanation.
- A budget needs establishing for a feature that has none, before any verdict is possible.
- Negative trigger: taking the measurement itself — the Profiler modules, Frame Debugger, memory snapshots, and device profiling over adb are `unity-profiler-diagnostics`; this skill consumes what that produces.
- Negative trigger: choosing, writing, or applying the fix — that is `unity-engineer` for the routine pass and `tech-lead-performance` for deep memory, GPU, and native work.
- Negative trigger: a no-allocation claim expressed as a pass or fail assertion inside a test — that is `unity-test-framework`'s allocation constraint, a regression gate rather than a measurement.
- Negative trigger: functional verification of a build artifact — that is `build-fault-triage`.

## 4. How to use this skill
1. **Establish the budget before measuring anything, and state its unit and its target** — a frame budget is milliseconds on a named device tier, never a frame rate in the abstract, because 60fps means 16.7ms total across CPU and GPU and a feature owns only a slice of it. Without a supplied budget you may report absolute numbers, but you may not report a verdict; say which you are doing.
2. **Prefer a Development Build on the real target, and label an Editor run as indicative every time** — Editor numbers carry the Editor's own overhead and not the platform's compiled code path, so they can show a regression that does not exist on device and hide one that does. Per `verification-standards.md` an Editor result never satisfies a device claim; it is useful only for relative comparison against another Editor run.
3. **Discard warm-up frames before recording anything** — shader compilation, JIT or first-call costs, pool priming, and asset loads land in the first frames and belong to startup rather than to steady state. Recording them inflates the result and produces a failure nobody can reproduce once the scene has settled.
4. **Run the scenario several times and report the spread, never the best run** — a single run cannot distinguish a regression from variance, and choosing the favourable run is fabrication. Report minimum, median, and maximum; if the spread exceeds the delta you are judging, the honest verdict is that the measurement is inconclusive, not that it passed.
5. **Judge a regression against a baseline taken the same way** — same device, same build configuration, same scenario, same warm-up handling. A baseline from a different configuration is not a comparison. When no baseline exists, say the run *is* the baseline rather than implying a comparison happened.
6. **Watch for thermal throttling on any sustained mobile run** — a device that starts within budget and drifts out of it after several minutes has a genuine finding, but one measured at minute ten is not comparable to a baseline measured at minute one. Report the elapsed time each figure was taken at whenever the run is long enough to matter.
7. **Attribute the cost before reporting the regression** — name the system, the call, or the batch break the profiler points at. Per `performance-and-algorithms.md`'s Verification section a claim without attribution is not actionable; "frame time went up" tells the owning agent nothing they can act on.
8. **Route the fix and stop** — routine batching, pooling, and allocation work goes to `unity-engineer`; deep memory, GPU-level, native, and Job System work goes to `tech-lead-performance`. Never adjust code, settings, or the budget to make a number pass.
9. **State what was not measured** — the scenarios not exercised, the device tiers not covered, the metrics not captured. Per `verification-standards.md` this field is mandatory, because a report listing only what passed is read as a feature that was checked.

## 5. Specific goals / tasks this skill performs
- Establishing a budget in explicit units against a named device tier, or reporting that none exists.
- Discarding warm-up frames and defining the steady-state window a measurement covers.
- Producing repeated runs with minimum, median, and maximum reported.
- Separating a real regression from run-to-run variance, including the inconclusive verdict.
- Comparing against a baseline taken under identical conditions, or declaring the run a baseline.
- Accounting for thermal drift on sustained mobile runs.
- Attributing a regression to a named system, call, or batch break, and routing it.
- Out of scope: taking the measurement (`unity-profiler-diagnostics`); writing the fix (`unity-engineer`, `tech-lead-performance`); allocation assertions inside tests (`unity-test-framework`); artifact functional verification (`build-fault-triage`).

## 6. Output format
```
## Budget Verification — <feature or change>
- Budget: <metric, value, unit, and the device tier it applies to — or "none supplied, no verdict possible">
- Measured on: <Development Build on named device / Editor Play Mode — indicative only>
- Scenario: <what was exercised, for how long, and the warm-up frames discarded>
- Runs: <count, with minimum, median, and maximum per metric>
- Spread against delta: <whether the variance is smaller than the difference being judged>
- Baseline: <the comparison run and its conditions — or "none, this run is the baseline">
- Thermal: <elapsed time per figure on a sustained run — or not applicable>
- Attribution: <the system, call, or batch break the cost resolves to — per regression>
- Decision: <within budget / over budget / inconclusive / no verdict without a budget>
- Routed to: <unity-engineer / tech-lead-performance / none>
- Not measured: <scenarios, tiers, and metrics this run does not cover>
```

**Extended report — emit ONLY when the requester asks for it.** It adds all three fields below the decision:
```
- Known limitations: <what this verification did not establish — one device tier only, one scenario, GPU not captured>
- Latent concerns: <failure modes not yet triggered: headroom that disappears at higher entity counts, a budget met only on the highest tier>
- Future remediation: <the concrete fix for each concern above, each with the condition that should trigger it>
```

## 7. Examples
**Example 1**
- Input: "The new projectile pool made things faster — confirm it before we close the ticket." One Editor run showing 14.2ms against a previous 14.9ms.
- Output: INCONCLUSIVE rather than a confirmation. Re-ran the scenario 7 times on a Development Build over adb with 60 warm-up frames discarded; the spread was 13.6ms to 15.1ms, larger than the 0.7ms delta being claimed, so the improvement is not distinguishable from variance. Reported that GC allocation *did* fall measurably and is the defensible claim, and noted that the frame-time claim needs a longer sample rather than a different conclusion.

**Example 2**
- Input: "It runs at 60fps in the Editor on my machine, so mark the mobile budget verified."
- Output: declined. Per §4 step 2 an Editor run on a desktop carries neither the device's compiled code path nor its thermal behaviour, so it cannot satisfy a mobile budget in either direction — this is exactly the case where a pass would be recorded for something the device fails. Reported the Editor figure explicitly labelled indicative, and stated that a verdict needs a Development Build on the named tier.

**Example 3**
- Input: a sustained combat scenario on a mid-tier Android device, budget 16.7ms, measured at 15.8ms.
- Output: OVER BUDGET despite the headline number. The figure was taken 40 seconds in; repeated to 8 minutes, frame time drifted to 19.4ms as the device throttled, with each figure reported against its elapsed time. Attributed to per-frame skinned mesh evaluation on off-screen characters, and routed to `unity-engineer` — a finding a single short run would have recorded as a comfortable pass.

## 8. Edge cases & guardrails
- Never report a verdict without a stated budget — a number with nothing to compare against is data, and calling it a pass invents the criterion.
- Never report a single run as a result when the metric varies; if the spread exceeds the delta, the verdict is inconclusive and saying so is the correct outcome.
- Never present an Editor measurement as a device result, however convenient the number is.
- Never take the best run, trim an outlier without saying so, or omit the warm-up handling — each turns a measurement into an argument.
- Never edit code, project settings, or the budget itself to make a number pass; report and route.
- Never claim an improvement that was not measured on both sides under identical conditions, per `performance-and-algorithms.md`'s Verification section.
- If no baseline exists, say the run is the baseline rather than implying a comparison — a regression verdict with nothing to regress from is unfalsifiable.

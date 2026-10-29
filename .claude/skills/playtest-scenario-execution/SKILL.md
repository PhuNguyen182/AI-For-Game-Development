---
name: playtest-scenario-execution
description: "Run a GDD scenario in one Editor Play Mode session with proof: observable checkpoints, screenshots at the claim, console reading, defect vs design flaw vs as-designed. Use for every hand-played scenario."
user-invocable: false
---

# Playtest Scenario Execution

Not for: automated Edit/Play Mode tests (`unity-test-framework`), cases on a real device (`device-test-walkthrough`), build-only faults (`build-fault-triage`), frame cost and memory (`performance-budget-verification`), choosing which scenarios to run (`risk-based-test-planning`).

## Steps
1. **Convert the GDD passage into numbered observable checkpoints before entering Play Mode** — "feels responsive" cannot fail; "attack animation starts the frame the input registers" can. A passage with no convertible intent is returned, not guessed.
2. **Record the starting state** (scene, entry point, configuration) and change one thing at a time; without it a finding is unreproducible (`qa-standards` finding fields).
3. **Capture evidence on the frame the checkpoint is evaluated**, not after the sequence. Scene-view capture for spatial/layout claims, game-view capture for what the player sees.
4. **Read the console throughout**; excerpt with surrounding lines, since a lone stack trace rarely identifies the step.
5. **Repeat any possibly timing-dependent finding and report hits/attempts.** Intermittent is reported as intermittent, never reliable, never dropped.
6. **Classify each finding by the code** — technical defect (behaviour contradicts the code's instruction), design flaw (code does what it was told, the instruction is wrong), as designed (expectation was mistaken). Severity and routing per `qa-standards`.
7. **Design flaw → `gd` immediately**, never downgraded into a bug.
8. **Report what was not played.**

## Never
- Edit code, assets or configuration to change what you observe.
- Run a second Editor instance or request a platform build (needs an explicit GD request via `build-release-engineer`).
- Report a finding without its capture or console excerpt.

## Output
```
## Playtest — <scenario>
- Intent: <GDD passage as numbered checkpoints>
- Starting state: <scene, entry point, configuration, platform target>
- Played: <steps in order>
- Checkpoint results: <checkpoint → expected, actual, evidence ref>
- Evidence: <capture per claim; console excerpts with context>
- Reproduction: <attempts / hits per finding>
- Classification: <Technical defect / Design flaw / As designed, per finding>
- Routed to: <agent-id per defect, gd for any design flaw>
- Not played: <scenarios, configurations, paths not reached>
```
On request only, add `Known limitations`, `Latent concerns` and `Future remediation`, each with its trigger.

## Example
- "The dash feels bad, log it as a bug against the implementation" → declined as filed: it matches its Tech Spec exactly, the GDD's "no dead time" goal is unreachable at the specified cooldown; classified design flaw, sent to `gd`.

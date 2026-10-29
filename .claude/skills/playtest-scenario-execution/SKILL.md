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
3. **Drive the Editor per `unity:unity-cli` → `playmode-verification-loop.md`**, else the configured MCP tools. Prove frames advance (`job wait` on `Time.frameCount`) before observing anything — a frozen Game view still returns a clean screenshot.
4. **Send input through the input layer** — a Pipeline input command if `unity command --query input` lists one, else synthesized Input System device state via `script eval` (`unity-input-system`). Calling a game method directly skips bindings: label it `Input: bypassed (<method>)`; it can never pass a checkpoint about controls or responsiveness.
5. **Capture on the frame the checkpoint holds** — `job wait` with `on_met.capture`, or pause and `Step()` to that frame. A wait-then-screenshot from the shell proves only a later frame. A frame-exact claim ("the frame the input registers") needs frame counts read via `script eval` or logged, not a screenshot. Scene-view capture for spatial/layout claims, game-view for what the player sees; Screen Space - Overlay UI needs `--source screen`, or read its state.
6. **Read the console throughout**; excerpt with surrounding lines, since a lone stack trace rarely identifies the step.
7. **Repeat any possibly timing-dependent finding and report hits/attempts.** Intermittent is reported as intermittent, never reliable, never dropped.
8. **Classify per `qa-standards`, reading spec and code** — defect (behaviour ≠ spec/GDD clause, even when the code does exactly what it was written to do), design flaw (behaviour matches the spec, the spec is wrong or contradicts an acceptance criterion), as designed (expectation was mistaken).
9. **Design flaw → `gd` immediately**, never downgraded into a bug.
10. **Multi-client scenario → MPPM virtual players**, only when the brief records the GD's approval of extra Editor instances; drive each with `--instance`. Not approved → `Not played`.
11. **Report what was not played.**

## Never
- Edit code, assets or saved configuration to change what you observe. Session-only Editor overrides (auto-tick, `editor.playmode set_run_in_background`) are allowed and reverted before return.
- Run a second Editor instance outside step 10, or request a platform build (needs an explicit GD request via `build-release-engineer`).
- Report a finding without its capture or console excerpt.

## Output
```
## Playtest — <scenario>
- Intent: <GDD passage as numbered checkpoints>
- Starting state: <scene, entry point, configuration, platform target>
- Played: <steps in order; input route — input layer | bypassed (<method>)>
- Checkpoint results: <checkpoint → expected, actual, evidence ref>
- Evidence: <capture per claim; console excerpts with context>
- Reproduction: <attempts / hits per finding>
- Classification: <Defect / Design flaw / As designed, per finding>
- Routed to: <agent-id per defect, gd for any design flaw>
- Not played: <scenarios, configurations, paths not reached>
```
On request only, add `Known limitations`, `Latent concerns` and `Future remediation`, each with its trigger.

## Example
- "The dash feels bad, log it as a bug against the implementation" → declined as filed: it matches its Tech Spec exactly, the GDD's "no dead time" goal is unreachable at the specified cooldown; classified design flaw, sent to `gd`.

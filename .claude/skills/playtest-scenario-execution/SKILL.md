---
name: playtest-scenario-execution
description: "GDD scenario in one Play Mode session: checkpoints, screenshots, console, design flaw. Use for hand-played scenarios."
user-invocable: false
---

# Playtest Scenario Execution

- **Not for:** automated Edit/Play Mode tests (`unity-test-framework`).
- **Not for:** cases on a real device (`device-test-walkthrough`).
- **Not for:** build-only faults (`build-fault-triage`).
- **Not for:** frame cost and memory (`performance-budget-verification`).
- **Not for:** choosing which scenarios to run (`risk-based-test-planning`).

## Steps
1. **Convert the GDD passage into numbered observable checkpoints before entering Play Mode:** "feels responsive" cannot fail; "attack animation starts the frame the input registers" can.
   - **No convertible intent:** the passage is returned, not guessed.
2. **Record the starting state (scene, entry point, configuration) and change one thing at a time:** without it a finding is unreproducible (`qa-standards` finding fields).
3. **Drive the Editor per `unity:unity-cli` → `playmode-verification-loop.md`:** else the configured MCP tools.
   - **Before observing anything:** prove frames advance (`job wait` on `Time.frameCount`).
   - **Why:** a frozen Game view still returns a clean screenshot.
4. **Send input through the input layer:** a Pipeline input command if `unity command --query input` lists one, else synthesized Input System device state via `script eval` (`unity-input-system`).
   - **Calling a game method directly:** skips bindings; label it `Input: bypassed (<method>)`.
   - **Bypassed input:** can never pass a checkpoint about controls or responsiveness.
5. **Capture on the frame the checkpoint holds:** `job wait` with `on_met.capture`, or pause and `Step()` to that frame.
   - **Wait-then-screenshot from the shell:** proves only a later frame.
   - **Frame-exact claim ("the frame the input registers"):** needs frame counts read via `script eval` or logged, not a screenshot.
   - **Scene-view capture:** for spatial/layout claims.
   - **Game-view capture:** for what the player sees.
   - **Screen Space - Overlay UI:** needs `--source screen`, or read its state.
6. **Read the console throughout:** excerpt with surrounding lines, since a lone stack trace rarely identifies the step.
7. **Repeat any possibly timing-dependent finding and report hits/attempts:** intermittent is reported as intermittent, never reliable, never dropped.
8. **Classify per `qa-standards`, reading spec and code:**
   - **Defect:** behaviour ≠ spec/GDD clause, even when the code does exactly what it was written to do.
   - **Design flaw:** behaviour matches the spec, the spec is wrong or contradicts an acceptance criterion.
   - **As designed:** the expectation was mistaken.
9. **Design flaw → `gd` immediately:** never downgraded into a bug.
10. **Multi-client scenario → MPPM virtual players:** only when the brief records the GD's approval of extra Editor instances; drive each with `--instance`.
    - **Not approved:** `Not played`.
11. **Report what was not played:** under `Not played` in Output.

## Never
- **Editing to change what you observe:** edit code, assets or saved configuration.
  - **Exception:** session-only Editor overrides (auto-tick, `editor.playmode set_run_in_background`) are allowed and reverted before return.
- **Extra Editor or build:** run a second Editor instance outside step 10, or request a platform build (needs an explicit GD request via `build-release-engineer`).
- **Finding without evidence:** report a finding without its capture or console excerpt.

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

## Example
- **"The dash feels bad, log it as a bug against the implementation":** declined as filed.
  - **Why:** it matches its Tech Spec exactly; the GDD's "no dead time" goal is unreachable at the specified cooldown.
  - **Did instead:** classified design flaw, sent to `gd`.

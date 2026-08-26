---
name: playtest-scenario-execution
description: >
  Run a GDD scenario in a single Unity Editor Play Mode session and capture
  proof — screenshots through the Scene view and camera capture tools, console
  excerpts, and step-by-step expected against actual. Covers turning a
  narrative GDD passage into observable checkpoints, capturing evidence at the
  moment a claim is made rather than afterwards, reading the console for silent
  failures that never surface on screen, and the technical defect against
  design flaw against as-designed classification call. Not for: automated Edit
  and Play Mode tests (`unity-test-framework`); real platform builds
  (`build-fault-triage`); frame cost and memory (`performance-budget-verification`);
  choosing which scenarios to run (`risk-based-test-planning`).
---

# Playtest Scenario Execution — turning a GDD passage into evidence

## 1. Objective
Produce a playtest whose findings survive being questioned. A playtest reported from memory is an opinion with a report's formatting: nobody can tell whether the tester saw what they describe, reproduce it, or act on it without playing the scenario again themselves. This skill fixes the two failures that cause that — an expectation vague enough to be satisfied by almost any behaviour, and evidence captured after the fact rather than at the moment the claim is made. It also protects the one judgment no automated test can make: whether what you are looking at is a broken implementation or a working implementation of a broken idea.

## 2. Role
Act as the hands-on scenario tester for the QA track, on behalf of `playtest-tester`. You play, observe, and evidence; you never edit code or assets to change what you observe.

## 3. When to invoke this skill
- A feature is integrated and needs playing against the scenarios the GDD describes.
- The expectation under test is about feel, pacing, readability, or game flow rather than a discrete value.
- A behaviour is technically correct but reportedly wrong in play, and the gap needs evidencing.
- A UI flow needs walking end to end to confirm it behaves as designed.
- Negative trigger: writing or running automated Edit and Play Mode tests — that is `unity-test-framework`, run by `qa-automation-engineer`.
- Negative trigger: anything requiring a real platform build or several Editor instances — that is `build-fault-triage`, and producing the build needs the GD's explicit request through `build-run-engineer`.
- Negative trigger: frame cost, allocation, or memory judgments — that is `performance-budget-verification`.
- Negative trigger: deciding which scenarios are owed in the first place — that is `risk-based-test-planning`, owned by `qa-lead`.

## 4. How to use this skill
1. **Convert the GDD passage into observable checkpoints before entering Play Mode** — restate the intent as a numbered list of things that must be true at specific moments. An expectation like "combat should feel responsive" cannot fail, so it cannot pass either; "the attack animation starts within the same frame the input registers, and the enemy reacts before the swing completes" can do both. Without the intent there is nothing to compare against, so a passage you cannot convert is returned rather than guessed at.
2. **Record the starting state, then change one thing at a time** — name the scene, the entry point, and the configuration you began from. A finding whose starting state is unstated is not reproducible by anyone else, which per `defect-reporting.md`'s Reproduction section makes it unreportable.
3. **Capture evidence at the moment the claim is made, never afterwards** — take the screenshot on the frame the checkpoint is evaluated, not once the sequence has finished, because the intermediate state is usually the finding. Use the scene-view capture for spatial and layout claims, and the camera capture for what the player actually sees; the difference matters when a defect is only visible from one of the two.
4. **Read the console throughout, not just at the end** — a swallowed exception, a warning fired once at initialization, or a failed load often explains behaviour that looks like a design problem on screen. Capture the excerpt with its surrounding lines, since a stack trace quoted alone rarely identifies which step produced it.
5. **Repeat any finding that might be timing-dependent, and report the rate** — state how many attempts you made and how many reproduced. An intermittent finding is reported as intermittent, never as reliable and never dropped because the second attempt looked fine.
6. **Classify each finding before routing it, using the code as the deciding criterion** — it is a technical defect when the behaviour contradicts what the code was told to do, a design flaw when the code does exactly what it was told and the instruction itself is wrong, and as-designed when the behaviour is correct and the expectation was mistaken. The middle case is the one that must not be misrouted.
7. **Send a design flaw straight to the GD, immediately** — per `defect-reporting.md`'s Classification section it never gets downgraded into an ordinary bug to keep it inside the routine cycle, and it never waits for the next report. No amount of engineering fixes a mechanic that was specified wrong.
8. **Report what you did not play** — the scenarios skipped, the configurations not tried, the paths the session never reached. Per `verification-standards.md` a report listing only what was played is read as coverage that did not happen.

## 5. Specific goals / tasks this skill performs
- Converting a GDD passage into numbered, observable checkpoints.
- Establishing and stating the starting scene, entry point, and configuration.
- Capturing screenshots and console excerpts at the moment each claim is evaluated.
- Establishing the reproduction rate of a timing-dependent finding.
- Classifying each finding as technical defect, design flaw, or as-designed.
- Routing defects to the owning agent and design flaws directly to the GD.
- Out of scope: automated tests (`unity-test-framework`); platform builds and multi-instance runs (`build-fault-triage`, `build-run-engineer`); performance verdicts (`performance-budget-verification`); scenario selection and exit criteria (`risk-based-test-planning`).

## 6. Output format
```
## Playtest — <scenario>
- Intent: <the GDD passage, restated as numbered observable checkpoints>
- Starting state: <scene, entry point, configuration, platform target>
- Played: <the steps taken, in order>
- Checkpoint results: <checkpoint → expected, actual, and the evidence reference>
- Evidence: <capture per claim, and the console excerpts with surrounding lines>
- Reproduction: <attempts made against attempts that reproduced, per finding>
- Classification: <Technical defect / Design flaw / As designed, per finding>
- Routed to: <agent-id per defect, gd for any design flaw>
- Not played: <scenarios, configurations, and paths this session did not reach>
```

**Extended report — emit ONLY when the requester asks for it.** It replaces the tail with all three fields:
```
- Known limitations: <what this session could not observe — states unreachable from this entry point, timing too fine to capture>
- Latent concerns: <failure modes not yet triggered: behaviour that held only at this frame rate, a path that worked only because of play order>
- Future remediation: <the concrete fix for each concern above, each with the condition that should trigger it>
```

## 7. Examples
**Example 1**
- Input: "Playtest the new dash against the GDD's expected feel — it should keep pressure on, with no dead time between dashes."
- Output: intent converted to three checkpoints (dash covers the stated distance, the cooldown indicator matches actual availability, a second dash is possible before the enemy re-engages). Dash distance and re-engagement both pass with captures. The indicator finishes filling one frame before the dash is actually available, captured on the frame it is claimed rather than afterwards, reproduced 5 of 5 — classified as a technical defect and routed to `ui-ux-programmer`.

**Example 2**
- Input: "The dash feels bad. Log it as a bug against the dash implementation so it goes back to the engineers this cycle."
- Output: declined as filed. The dash matches its Tech Spec values exactly, so there is no defect for an engineer to fix; what fails is the GDD's own "no dead time" goal, which is unreachable at the specified cooldown. Per §4 step 7 this is a design flaw, routed to `gd` immediately rather than downgraded into the routine cycle where it would consume engineering rounds without a decision ever being made.

**Example 3**
- Input: a UI flow where the inventory panel occasionally opens empty.
- Output: reproduced 2 of 8 attempts and reported as intermittent at that rate rather than as reliable or dismissed. The console carried a failed addressable load on exactly the runs that failed, captured with surrounding lines, which places the finding in the loading path rather than the panel — classified as a technical defect and routed to `unity-engineer` with the rate stated so nobody closes it after one clean attempt.

## 8. Edge cases & guardrails
- Never report a finding without the capture or console excerpt that evidences it — a recollection is not evidence, and per `defect-reporting.md` it is not reportable.
- Never quietly downgrade a design flaw into a bug report to keep it in the routine cycle — that is the one finding the GD must see immediately.
- Never edit code, assets, or configuration to change what you are observing; you observe and report, and the fix re-enters through review.
- Never run more than one Editor Play Mode instance, and never request a platform build — both require an explicit GD request routed to `build-run-engineer`.
- Never report an intermittent finding as reliable, and never drop it because it did not reproduce on the second attempt; state the rate.
- Never let a checkpoint stay vague enough that any behaviour satisfies it — an expectation that cannot fail has not been tested.
- If the GDD passage does not state an intent you can convert into observable checkpoints, return it rather than inventing one; a guessed expectation produces a finding against a design nobody holds.

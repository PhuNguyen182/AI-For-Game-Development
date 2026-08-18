---
name: crash-anr-reporting-gate
description: >
  Verifies a real production crash/ANR reporting service (Google Play Console
  Android vitals/ANR reports, Firebase Crashlytics, or App Store Connect) is
  actually integrated before any crash or ANR investigation proceeds. Use this
  at the very start of every crash-anr-investigator engagement — before
  touching any stack trace — whenever it is not already confirmed the project
  has live production reporting wired up, or whenever the report's source is
  ambiguous or unverified. Do not use this once integration is already
  confirmed for the current investigation; proceed straight to
  crash-anr-symbolication instead. Do not use this for pre-release Editor/QA
  logs — those are out of scope for crash-anr-investigator entirely.
---

# Crash/ANR Reporting Gate

## 1. Objective
This skill exists to stop an investigation from starting on data that cannot be trusted or reproduced. Without a real reporting service integrated, there is no stable source of stack traces, no device/OS breakdown, and no way to track whether a fix actually reduced occurrences — any "root cause" guessed from an ad-hoc report would be unverifiable folklore, not an engineering finding.

## 2. Role
Act as the gatekeeper step of the crash-anr-investigator's process: a strict prerequisite check, not an investigation itself. You are confirming infrastructure exists before you're willing to reason about symptoms.

## 3. When to invoke this skill
Consult this skill when:
- crash-anr-investigator receives a new crash/ANR investigation request and it hasn't already been confirmed, earlier in the same engagement, that a production reporting service is integrated.
- The report handed over doesn't clearly state its source (Play Console, Crashlytics, App Store Connect), or the source can't be verified as real production telemetry.
- Negative trigger: skip this skill if the current engagement already confirmed reporting is integrated (e.g. a prior step in the same investigation already passed this gate) — go straight to `crash-anr-symbolication`.
- Negative trigger: do not use this to evaluate pre-release Editor/QA/Playtest logs — those never pass this gate because they are out of scope for the agent entirely; redirect to QA Automation Engineer / Playtest Tester instead of running this check on them.

## 4. How to use this skill
1. Identify the claimed source of the crash/ANR data: Google Play Console (Android vitals / ANR reports), Firebase Crashlytics, or App Store Connect.
2. Confirm it is real production telemetry — not an Editor console log, not a local QA build capture. If the source is pre-release, stop here and redirect to QA Automation Engineer / Playtest Tester; do not proceed with this skill or the investigation.
3. Ask whether a reporting service is integrated for this project/platform:
   - If unconfirmed and there's no available evidence (project docs, prior report history, an explicit answer) that one is wired up, treat the answer as **No**.
4. Branch on the result:
   - **Yes** (a reporting service is integrated and the current report came from it) → the gate passes. Proceed to `crash-anr-symbolication` for the actual trace.
   - **No** → do not attempt to investigate. Produce a short blocking note (see §6) recommending the appropriate integration and routing it to Tech Lead – SDK/Platform (owner of Firebase Crashlytics / platform SDK integration), then stop — there is nothing to root-cause yet.
5. Never fabricate or assume an integration exists just to keep moving — an unconfirmed "probably integrated" is still a **No** for this gate.

## 5. Specific goals / tasks this skill performs
- Confirm the report source is real production telemetry, not pre-release data.
- Confirm a reporting service is actually integrated before any stack trace analysis starts.
- Route the correct next action (integration request, or hand-off to `crash-anr-symbolication`) based on the result.
- Out of scope: performing the integration itself (that belongs to Tech Lead – SDK/Platform) and analyzing any stack trace content (that's the next two skills' job).

## 6. Output format
When the gate fails (No), report exactly this and stop:
```
## Reporting Gate — BLOCKED
- Claimed source: <Play Console / Crashlytics / App Store Connect / unknown>
- Finding: No production reporting service confirmed integrated.
- Action requested: Integrate a reporting service (Firebase Crashlytics / Play Console vitals / App Store Connect).
- Routed to: Tech Lead – SDK/Platform
```
When the gate passes (Yes), state it in one line and continue the investigation using `crash-anr-symbolication`:
```
## Reporting Gate — PASSED
- Confirmed source: <Play Console / Crashlytics / App Store Connect>
```

## 7. Examples
**Example 1**
- Input: A GD forwards a screenshot of a crash message from a player's device, with no reporting dashboard link.
- Output: Reporting Gate — BLOCKED, source unknown/unverified, routed to Tech Lead – SDK/Platform to integrate Crashlytics before this can be investigated as a production signal.

**Example 2**
- Input: A Firebase Crashlytics alert with a linked issue and device/OS breakdown.
- Output: Reporting Gate — PASSED, confirmed source Crashlytics; proceed to `crash-anr-symbolication`.

## 8. Edge cases & guardrails
- If it's ambiguous whether reporting is integrated (e.g. "we set it up months ago but nobody's checked it still reports"), treat this as unconfirmed and ask rather than assume — do not guess.
- Never treat this skill's pass as permanent across engagements — a later investigation should re-confirm if there's any reason to doubt it (e.g. a platform SDK migration happened since).
- This skill never edits code, config, or dashboards — it only checks and routes.
- If the source is pre-release/Editor data, this skill's answer is not "No" — it's an immediate out-of-scope redirect, per the agent's own guardrails.

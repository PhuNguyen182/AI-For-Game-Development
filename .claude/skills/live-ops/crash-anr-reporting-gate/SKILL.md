---
name: crash-anr-reporting-gate
description: >
  Gate that confirms a real production crash and ANR reporting service is
  actually integrated and reporting — Google Play Console Android vitals,
  Firebase Crashlytics, or App Store Connect — before any trace is read. Use
  at the start of every crash or ANR investigation whenever live reporting is
  not already confirmed for this engagement, or the report's source is
  unstated or unverifiable. Not for: reading the trace once the gate passes
  (`crash-anr-symbolication`); attributing the fault
  (`crash-anr-fault-domain-triage`); performing the integration
  (`tech-lead-sdk-platform`); pre-release Editor or QA logs
  (`qa-automation-engineer`, `playtest-tester`).
---

# Crash and ANR Reporting Gate — is there a trustworthy signal at all

## Bundled resources

### References
Read-only context, loaded on demand so SKILL.md itself stays short.

| File | Contents | Read when |
|---|---|---|
| [root-links.md](references/root-links.md) | The three services' documentation roots, and what this skill deliberately does not pin | Starting any gate check, or a vendor page has moved |
| [reporting-services.md](references/reporting-services.md) | What each service actually provides, what "integrated and reporting" requires, retention limits | Deciding whether a claimed source is a production signal |

## 1. Objective
Stop an investigation from starting on data that cannot be reproduced, counted, or tracked. Without a real reporting service there is no stable trace, no device and OS breakdown, and no way to tell whether a shipped fix reduced anything — so a root cause derived from an ad-hoc report is folklore wearing an engineering format. This gate also catches the cheaper failure: a service that was integrated once, silently stopped reporting, and left everyone reading a stale dashboard.

## 2. Role
Act as the gatekeeper of the crash investigation pipeline, on behalf of `crash-anr-investigator`. This is a prerequisite check and never an investigation: you confirm the infrastructure exists before anyone is allowed to reason about symptoms.

## 3. When to invoke this skill
- A crash or ANR investigation request arrives and nothing earlier in this engagement confirmed a production reporting service is integrated.
- The report handed over does not state its source, or the stated source cannot be verified as production telemetry.
- The dashboard exists but has not received anything recently, or a platform SDK migration has happened since anyone last checked it.
- Negative trigger: this engagement already passed the gate — go straight to `crash-anr-symbolication` rather than re-running the check for its own sake.
- Negative trigger: reading, resolving, or interpreting a trace — those are `crash-anr-symbolication` and `crash-anr-fault-domain-triage`; this skill never opens a stack trace.
- Negative trigger: performing the integration itself — that is `tech-lead-sdk-platform`, who owns Crashlytics and platform SDK wiring; this skill requests it and stops.
- Negative trigger: Editor console output, a local QA build capture, or a playtest log — these never pass this gate because they are outside the investigation's scope entirely; redirect to `qa-automation-engineer` or `playtest-tester`.

## 4. How to use this skill
1. **Name the claimed source before anything else** — Play Console Android vitals, Crashlytics, or App Store Connect, per [root-links.md](references/root-links.md) and [reporting-services.md](references/reporting-services.md). A source nobody will name is already the answer, and an unnamed source is not a fourth option to work around.
2. **Redirect pre-release data instead of failing it** — an Editor log or a QA build capture is not a gate failure to be remediated, it is a different activity owned by `qa-automation-engineer` and `playtest-tester`. Say so and stop; requesting a Crashlytics integration in response would be answering a question nobody asked.
3. **Confirm the service is reporting, not merely installed** — an integration that has not received an event in the period the release has been live is indistinguishable from no integration for this purpose, per [reporting-services.md](references/reporting-services.md). Check that the dashboard has data for the version under investigation.
4. **Treat anything unconfirmed as absent** — "we set it up a while ago" is a No, not a qualified Yes. Ask rather than assume, per §8; a gate that passes on optimism defeats its own purpose.
5. **Pass only when the report in hand came from the confirmed service** — a live dashboard plus a screenshot from somewhere else is still a fail, because the trace being investigated is not the one the service can reproduce or count.
6. **Block with a routed action, and say where the flow resumes** — name the service to integrate, route it to `tech-lead-sdk-platform`, then stop. Once the integration ships, the investigation restarts at `crash-anr-symbolication` from a **fresh** report produced by that service; the report that failed this gate is not retroactively made usable, because the build that produced it never carried the SDK.

## 5. Specific goals / tasks this skill performs
- Establishing the claimed source of a crash or ANR report.
- Separating production telemetry from pre-release Editor and QA data, and redirecting the latter.
- Confirming a reporting service is both integrated and actively receiving data for the version under investigation.
- Producing a pass that hands off to `crash-anr-symbolication`, or a block routed to `tech-lead-sdk-platform`.
- Out of scope: performing the integration (`tech-lead-sdk-platform`); reading or resolving a trace (`crash-anr-symbolication`); attributing a fault (`crash-anr-fault-domain-triage`); pre-release defect work (`qa-automation-engineer`, `playtest-tester`).

## 6. Output format
```
## Reporting Gate — <PASSED / BLOCKED / OUT OF SCOPE>
- Claimed source: <Play Console vitals / Crashlytics / App Store Connect / unstated>
- Production telemetry: <confirmed / pre-release data / unverifiable>
- Service receiving data for the version under investigation: <yes / no / unknown>
- Decision: <proceed / block / redirect>
- Action requested: <integrate a named service / none needed / none — wrong pipeline>
- Routed to: <crash-anr-symbolication / tech-lead-sdk-platform / qa-automation-engineer / playtest-tester>
```

**Extended report — emit ONLY when the requester asks for it.** It adds all three fields below the decision:
```
- Known limitations: <what this gate did not establish — for example coverage on one platform only>
- Latent concerns: <failure modes not yet triggered: retention windows about to expire, a platform migration in flight, sampling that hides low-volume signatures>
- Future remediation: <the concrete fix for each concern above, each with the condition that should trigger it>
```

## 7. Examples
**Example 1**
- Input: a screenshot of a crash dialog forwarded from a player, with no dashboard link.
- Output: BLOCKED. The source cannot be verified as production telemetry, and a single device's message gives no frequency, no device breakdown, and no way to confirm a later fix worked. Requested a Crashlytics integration and routed it to `tech-lead-sdk-platform`. No trace was opened, because reading one here would produce a finding nobody could reproduce.

**Example 2**
- Input: "The Editor throws a null reference every time we open the shop scene, can you root-cause the crash?"
- Output: OUT OF SCOPE rather than BLOCKED — this is a pre-release defect, not a production crash, so requesting a reporting integration would be the wrong answer to the right problem. Redirected to `qa-automation-engineer` for a reproducing test, and noted that this pipeline only handles signals from a live store build.

**Example 3**
- Input: a Crashlytics alert with a linked issue, affected-version list, and device and OS breakdown.
- Output: PASSED. Source confirmed, and the dashboard carries events for the version under investigation rather than only for an older one. Proceeded to `crash-anr-symbolication` with the trace.

## 8. Edge cases & guardrails
- Never pass the gate on an assumption — an integration nobody has verified since a platform SDK change is unconfirmed, and unconfirmed is a block.
- Never treat a pass as permanent across engagements — re-confirm whenever a build pipeline, SDK, or store target has changed since.
- Never open a stack trace inside this skill — reading one before the source is trusted is how an unreproducible finding gets an official-looking format.
- Never answer pre-release data with an integration request — it is the wrong pipeline, not a missing tool.
- Never block without naming the service and the owner — an unrouted block is indistinguishable from silence.
- Never edit code, configuration, or a dashboard here — this skill checks and routes, and the integration itself belongs to `tech-lead-sdk-platform`.
- If the report predates the current release by long enough that the service's retention window may have dropped the underlying data, say so rather than treating a visible summary as a retrievable trace, per [reporting-services.md](references/reporting-services.md).

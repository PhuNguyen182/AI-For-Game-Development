---
name: crash-anr-reporting-gate
description: "Confirm a real production crash/ANR reporting service (Play Console vitals, Crashlytics, App Store Connect) is integrated and reporting before reading any trace. Use as stage 1 of a production crash investigation."
user-invocable: false
---

# Crash and ANR Reporting Gate

Not for: reading the trace (`crash-anr-symbolication`), attributing the fault (`crash-anr-fault-domain-triage`), performing the integration (`sdk-platform-engineer`), choosing a vendor when none is committed (`analytics-telemetry-platform`), Editor or playtest logs (`qa-automation-engineer`, `playtest-tester`), faults in a pre-release player build (`build-fault-triage`).
Docs: https://developer.android.com/topic/performance/vitals (also `/anr`, `/crash`), https://firebase.google.com/docs/crashlytics (Unity: `/get-started?platform=unity`), Apple https://developer.apple.com/documentation/xcode/diagnosing-issues-using-crash-reports-and-device-logs — vendor consoles, unversioned. Read the console for thresholds, retention windows and navigation; none is pinned here.

| Reference | Read when |
|---|---|
| [reporting-services.md](references/reporting-services.md) | Deciding whether a claimed source is a production signal and is reporting |

## Steps
1. **Name the claimed source:** Play Console vitals, Crashlytics or App Store Connect. An unnamed source is a block.
2. **Pre-release data is out of scope, not a gate failure.** Editor log or QA capture → `qa-automation-engineer`/`playtest-tester`; fault in a never-shipped player build → `build-fault-triage`. Say so and stop; do not request an integration.
3. **Confirm the service is reporting, not merely installed:** data exists for the version under investigation. Per [reporting-services.md](references/reporting-services.md).
4. **Gate already passed earlier in this engagement and nothing in the pipeline, SDK or store target changed -> go straight to `crash-anr-symbolication`.** Otherwise unconfirmed counts as absent. "Set up a while ago" is a No; ask rather than assume.
5. **Pass only when the report in hand came from the confirmed service.** A live dashboard plus a screenshot from elsewhere fails.
6. **Block with a routed action:** name the service, route to `sdk-platform-engineer`, stop. No service committed → name the gap and route the vendor choice to `analytics-telemetry-platform`. After the integration ships, restart at `crash-anr-symbolication` from a **fresh** report; the failed report stays unusable because its build never carried the SDK.
7. **Report was filed long before the current release → say the service's retention may have dropped the traces**; a visible summary is not a retrievable trace.

## Never
- Open a stack trace here; a finding from an unverified source gets an official-looking format.
- Pass on assumption, or carry a pass across engagements after a build pipeline, SDK or store target changed.
- Edit code, configuration or a dashboard; this skill checks and routes.
- Block without naming the service and the owner.

## Output
```
## Reporting Gate — <PASSED / BLOCKED / OUT OF SCOPE>
- Claimed source: <Play Console vitals / Crashlytics / App Store Connect / unstated>
- Production telemetry: <confirmed / pre-release data / unverifiable>
- Service receiving data for the version under investigation: <yes / no / unknown>
- Decision: <proceed / block / redirect>
- Action requested: <integrate a named service / none needed / none — wrong pipeline>
- Routed to: <crash-anr-symbolication / sdk-platform-engineer / qa-automation-engineer / playtest-tester>
- Known limitations: <what this gate did not establish>
```

## Example
- "The Editor throws a null reference opening the shop scene, root-cause the crash" → OUT OF SCOPE, not BLOCKED: a pre-release defect; redirected to `qa-automation-engineer` for a reproducing test rather than requesting a Crashlytics integration.

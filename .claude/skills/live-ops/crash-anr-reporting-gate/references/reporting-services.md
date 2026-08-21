# Reporting Services — what each one provides, and what "integrated" means

Sources: [Android vitals](https://developer.android.com/topic/performance/vitals), [ANRs](https://developer.android.com/topic/performance/vitals/anr), [Crashlytics](https://firebase.google.com/docs/crashlytics), [Get started with Crashlytics on Unity](https://firebase.google.com/docs/crashlytics/get-started?platform=unity), [Diagnosing issues using crash reports and device logs](https://developer.apple.com/documentation/xcode/diagnosing-issues-using-crash-reports-and-device-logs).
Covers: SKILL.md §4 — **"Name the claimed source before anything else"**, **"Confirm the service is reporting, not merely installed"**.

What each service actually gives an investigation, and the difference between
a service that is installed and one that is reporting. Resolving the frames a
service hands over is `crash-anr-symbolication`'s; performing the integration
is `tech-lead-sdk-platform`'s.

## What each service provides

| Service | Covers | Notable limit | Source |
|---|---|---|---|
| Android vitals | Crashes and ANRs on Android, aggregated across the installed base with device, OS and version breakdowns, and measured against the thresholds Google Play holds a title to | Android only, and it reports what the platform observed rather than what the app chose to send — so an app that never integrated an SDK still appears here | [Android vitals](https://developer.android.com/topic/performance/vitals) |
| Firebase Crashlytics | Crashes, non-fatal exceptions and ANRs across platforms, with custom keys and logs the app attaches itself | Requires an SDK in the build, so a version shipped before the integration reports nothing at all and never will | [Crashlytics](https://firebase.google.com/docs/crashlytics) |
| App Store Connect | Crash reports from opted-in users on Apple platforms | Depends on user opt-in, so low-volume signatures can be absent rather than absent-because-fixed | [Diagnosing issues using crash reports and device logs](https://developer.apple.com/documentation/xcode/diagnosing-issues-using-crash-reports-and-device-logs) |

**Critical caveat**: the platform consoles and the SDK answer different
questions. Android vitals shows what the platform saw across everyone;
Crashlytics shows what the app reported from builds carrying the SDK. A
signature present in one and missing from the other is normal, and is not
evidence that either is broken.

## What "integrated and reporting" requires

| Condition | Why it matters to this gate | Source |
|---|---|---|
| The SDK is in the build under investigation | A later integration does not backfill — the crashing version either carried it or it did not, which is why a blocked gate resumes from a new report rather than the one that failed it | [Get started with Crashlytics on Unity](https://firebase.google.com/docs/crashlytics/get-started?platform=unity) |
| Events have arrived for that version | A dashboard populated only by an older release cannot confirm or count anything about this one | [Crashlytics](https://firebase.google.com/docs/crashlytics) |
| The title is actually distributed through the store | Vitals aggregate what the store's installed base reports, so an internally sideloaded build produces nothing there | [Android vitals](https://developer.android.com/topic/performance/vitals) |
| Reporting was not disabled at runtime | Collection can be turned off by configuration or by a consent flow, which looks identical to an absent integration from the dashboard side | [Crashlytics](https://firebase.google.com/docs/crashlytics) |

## Limits worth stating in a gate result

| Limit | Consequence for the investigation | Source |
|---|---|---|
| Retention | Each service keeps detail for a bounded period the vendor sets, so an old signature may still show a summary while its underlying traces have expired | [Crashlytics](https://firebase.google.com/docs/crashlytics) |
| Aggregation and sampling | Reports are grouped by signature, and a group's representative trace is not necessarily the one that matters — pull several samples before treating one as typical | [Android vitals](https://developer.android.com/topic/performance/vitals) |
| Opt-in coverage | Apple's reports depend on user consent, so absence is weaker evidence than presence | [Diagnosing issues using crash reports and device logs](https://developer.apple.com/documentation/xcode/diagnosing-issues-using-crash-reports-and-device-logs) |
| ANR versus crash | An ANR is the system deciding the app stopped responding rather than the app terminating, so it appears in different views with different thresholds — see `crash-anr-fault-domain-triage` | [ANRs](https://developer.android.com/topic/performance/vitals/anr) |

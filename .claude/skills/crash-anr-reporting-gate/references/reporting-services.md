# Reporting Services

Sources: [a] Android vitals, [b] vitals/anr, [c] Crashlytics, [d] Crashlytics for Unity, [e] Apple crash-report diagnosis; URLs in the SKILL.md `Docs:` line.

## What each service provides

| Service | Covers | Limit |
|---|---|---|
| Android vitals [a] | Android crashes and ANRs across the installed base, with device/OS/version breakdowns, against Google Play thresholds | Android only; reports what the platform saw, so an app with no SDK still appears |
| Firebase Crashlytics [c] | Crashes, non-fatals and ANRs cross-platform, with app-attached custom keys and logs | Needs an SDK in the build: a version shipped before the integration never reports |
| App Store Connect [e] | Crash reports from opted-in Apple users | User opt-in, so low-volume signatures can be absent without being fixed |

**Caveat:** vitals shows what the platform saw across everyone; Crashlytics shows what builds carrying the SDK reported. A signature in one and not the other is normal, not a sign either is broken.

## "Integrated and reporting" requires

| Condition | Why |
|---|---|
| SDK is in the build under investigation [d] | A later integration does not backfill; hence a blocked gate resumes from a new report |
| Events have arrived for that version [c] | A dashboard filled by an older release cannot count this one |
| Title is distributed through the store [a] | Vitals aggregates the store's installed base; a sideloaded build produces nothing |
| Reporting not disabled at runtime [c] | Config or a consent flow can turn collection off; looks identical to no integration |

## Limits to state in a gate result

| Limit | Consequence |
|---|---|
| Retention [c] | An old signature may show a summary while its traces have expired |
| Aggregation and sampling [a] | A group's representative trace may not be typical; pull several samples |
| Opt-in coverage [e] | Absence is weaker evidence than presence |
| ANR vs crash [b] | Different views and thresholds; see `crash-anr-fault-domain-triage` |

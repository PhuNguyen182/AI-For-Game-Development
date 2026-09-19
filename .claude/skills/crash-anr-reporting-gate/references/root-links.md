# Root Links — production crash and ANR reporting services

Source: the root documentation pages listed below, as provided for this skill.
Covers: the whole skill — provenance and version anchor for every file in
this folder.

Anchors every link in this folder. These are vendor consoles rather than
versioned packages, so there is no version to pin — the console itself is the
authority, and its documentation is reorganised more often than a package's
is. Each root below is a landing page chosen because it survives that
reorganisation; deep article links are avoided for the same reason.

## Roots

| Service | Holds | Source |
|---|---|---|
| Android vitals | Crash rate, ANR rate, the thresholds Google Play holds a title to, and the per-device breakdown | [Android vitals](https://developer.android.com/topic/performance/vitals) |
| ANR guidance | What an ANR is, which timeouts produce one, and how they are diagnosed | [ANRs](https://developer.android.com/topic/performance/vitals/anr) |
| Crash guidance | Crash reporting and the data Android collects for it | [Crashes](https://developer.android.com/topic/performance/vitals/crash) |
| Firebase Crashlytics | Cross-platform crash, non-fatal and ANR reporting, including the Unity SDK | [Crashlytics](https://firebase.google.com/docs/crashlytics) |
| Crashlytics for Unity | The integration path this project would actually take on a Unity title | [Get started with Crashlytics on Unity](https://firebase.google.com/docs/crashlytics/get-started?platform=unity) |
| Apple crash reports | How Apple collects, groups and presents crash reports for a shipped app | [Diagnosing issues using crash reports and device logs](https://developer.apple.com/documentation/xcode/diagnosing-issues-using-crash-reports-and-device-logs) |

## What this skill deliberately does not pin

| Subject | Why it is not linked here | Source |
|---|---|---|
| Exact vitals thresholds | Google revises the bad-behaviour thresholds and their measurement windows; quoting a number here would age into a wrong one | [Android vitals](https://developer.android.com/topic/performance/vitals) |
| Console navigation paths | Play Console and App Store Connect layouts change without notice, so a described click path is a liability rather than a help | [Android vitals](https://developer.android.com/topic/performance/vitals) |
| Retention windows | Each service keeps data for a bounded period that the vendor changes; check the console rather than a remembered figure — see [reporting-services.md](reporting-services.md) | [Crashlytics](https://firebase.google.com/docs/crashlytics) |

Read the console for anything numeric. This skill's job is to establish that a
console exists and is receiving data, not to restate figures it can read
directly.

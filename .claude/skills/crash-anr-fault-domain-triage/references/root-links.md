# Root Links — platform, engine and store references for fault attribution

Source: the root documentation pages listed below, as provided for this skill.
Covers: the whole skill — provenance and version anchor for every file in
this folder.

Anchors every link in this folder. These are platform, engine and store
documents rather than versioned packages, so there is no version to pin; the
Unity Manual pages are published unversioned and resolve to the current
release. Landing pages are preferred over deep articles, which move.

## Roots

| Subject | Holds | Source |
|---|---|---|
| Android vitals | Crash and ANR rates, the thresholds a title is held to, and the device and OS breakdown that decides segmentation | [Android vitals](https://developer.android.com/topic/performance/vitals) |
| ANRs | What produces an ANR, which timeouts apply, and how one is diagnosed | [ANRs](https://developer.android.com/topic/performance/vitals/anr) |
| Exit reasons | The recorded reason a process ended, readable on the next launch | [ApplicationExitInfo](https://developer.android.com/reference/android/app/ApplicationExitInfo) |
| Main-thread policy | Detecting accidental disk and network work on the main thread before it becomes an ANR | [StrictMode](https://developer.android.com/reference/android/os/StrictMode) |
| Google Play SDK Index | Known issues and version advice for third-party SDKs | [Google Play SDK Index](https://developer.android.com/distribute/sdk-index) |
| Unity issue tracker | Whether an engine fault is already known and in which version it is fixed | [Unity Issue Tracker](https://issuetracker.unity3d.com/) |
| Unity IL2CPP | Why game code appears as native frames on a shipped build | [IL2CPP](https://docs.unity3d.com/Manual/IL2CPP.html) |
| Apple crash reports | How Apple presents a report, and what its sections mean | [Diagnosing issues using crash reports and device logs](https://developer.apple.com/documentation/xcode/diagnosing-issues-using-crash-reports-and-device-logs) |

## What this skill deliberately does not pin

| Subject | Why it is not linked here | Source |
|---|---|---|
| Exact vitals thresholds and windows | Google revises both, so a number written here ages into a wrong one; read the console | [Android vitals](https://developer.android.com/topic/performance/vitals) |
| Exact ANR timeout durations | They vary by timeout class and platform release; the class matters for attribution, the millisecond figure does not — see [anr-classes-and-mitigation.md](anr-classes-and-mitigation.md) | [ANRs](https://developer.android.com/topic/performance/vitals/anr) |
| Console navigation and device catalogue paths | Play Console and App Store Connect layouts change without notice | [Android vitals](https://developer.android.com/topic/performance/vitals) |
| Which Unity version fixes a given issue | That is per issue and per stream; the tracker is the answer, and `tech-lead-csharp-unity` owns the upgrade decision | [Unity Issue Tracker](https://issuetracker.unity3d.com/) |

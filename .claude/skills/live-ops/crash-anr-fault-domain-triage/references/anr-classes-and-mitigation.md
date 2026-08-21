# ANR Classes and Mitigation — when there is no code fix

Sources: [ANRs](https://developer.android.com/topic/performance/vitals/anr), [Android vitals](https://developer.android.com/topic/performance/vitals), [ApplicationExitInfo](https://developer.android.com/reference/android/app/ApplicationExitInfo), [StrictMode](https://developer.android.com/reference/android/os/StrictMode).
Covers: SKILL.md §4 — **"In game code, separate a fixable defect from a condition only mitigation reaches"**, **"In a system library, establish whether it is segmented by device or broad"**.

What an ANR actually is, the classes it comes in, the causes a Unity title
produces most often, and what to recommend when no code change removes the
fault. Implementing any of this belongs to `unity-engineer` or
`tech-lead-performance`.

## What an ANR is

| Subject | What it decides | Source |
|---|---|---|
| Definition | The system deciding the app stopped responding, not the app terminating — so there is no exception and no crashing frame, only a thread that did not return in time | [ANRs](https://developer.android.com/topic/performance/vitals/anr) |
| Timeout classes | Input dispatch, broadcast handling, service start and content-provider timeouts are distinct classes with distinct causes; the class narrows the search far faster than the stack does | [ANRs](https://developer.android.com/topic/performance/vitals/anr) |
| Which thread matters | Unlike a crash, the blocking thread may not be the main one — a lock held elsewhere is a common cause, so every thread's stack is evidence | [ANRs](https://developer.android.com/topic/performance/vitals/anr) |
| Rate rather than count | Vitals holds a title to a rate against its installed base, so a fault concentrated in a small population can be real and still sit under the threshold — and the reverse | [Android vitals](https://developer.android.com/topic/performance/vitals) |

**Critical caveat**: an ANR trace names where the thread was, not what made
it wait. A main thread parked in a platform wait is the symptom of something
else holding it, and attributing the fault to the platform call is the most
common mistake in ANR triage.

## Causes a Unity title produces

| Cause | Why it blocks | Where the fix lives | Source |
|---|---|---|---|
| Synchronous asset or scene loading on the main thread | The frame loop cannot advance until it returns, and a large enough load exceeds the dispatch timeout — the blocking-completion pattern that `unity-addressables` warns against is a direct example | `unity-engineer`, guided by `unity-addressables` | [ANRs](https://developer.android.com/topic/performance/vitals/anr) |
| Disk or network work on the main thread | The same block, with a duration that depends on the device rather than the code — which is why it reproduces only on lower tiers | `unity-engineer` | [StrictMode](https://developer.android.com/reference/android/os/StrictMode) |
| A lock held across a long operation | The main thread waits on a worker that is itself waiting, so both stacks look idle | `csharp-engineer` or `unity-engineer` by layer | [ANRs](https://developer.android.com/topic/performance/vitals/anr) |
| Sustained frame cost rather than one long call | No single frame exceeds anything, and the app still fails to respond in time — a profiling question before it is a triage one, owned by `unity-profiler-diagnostics` | `unity-engineer` | [ANRs](https://developer.android.com/topic/performance/vitals/anr) |
| Memory pressure during a load | The platform reclaims resources while the app is mid-operation, which the app cannot prevent — mitigation rather than fix | `tech-lead-performance` | [ApplicationExitInfo](https://developer.android.com/reference/android/app/ApplicationExitInfo) |

## Mitigations when no fix exists

| Mitigation | What it buys | Limit | Source |
|---|---|---|---|
| Main-thread policy detection | Catches accidental disk and network work on the main thread during development, before it reaches players as an ANR | A development-time detector, not a runtime guard — it finds the class of cause, it does not prevent one | [StrictMode](https://developer.android.com/reference/android/os/StrictMode) |
| Recorded exit reason | Reads why the process actually ended on the next launch, which converts "it disappeared" into a named reason | Available only from a sufficiently recent platform version, and only on the next launch | [ApplicationExitInfo](https://developer.android.com/reference/android/app/ApplicationExitInfo) |
| Device or OS segmentation | Removes the affected population from distribution, which removes the reported rate | It removes the reporters, not the fault — keep the vendor thread open | [Android vitals](https://developer.android.com/topic/performance/vitals) |
| Reducing the work rather than moving it | The only mitigation that also improves the experience for everyone else | Requires a measurement first, per `performance-and-algorithms.md`'s Verification section | [ANRs](https://developer.android.com/topic/performance/vitals/anr) |

## Deciding segmentation

| Observation | Recommendation | Source |
|---|---|---|
| Confined to one manufacturer or one OS version | Segmentation plus a vendor report — the segmentation buys time, the report is the actual path to a fix | [Android vitals](https://developer.android.com/topic/performance/vitals) |
| Spread across devices and versions | A vendor report alone; segmenting broadly would remove a real share of the audience for no fix | [Android vitals](https://developer.android.com/topic/performance/vitals) |
| Concentrated on low-memory devices | Usually the app's own footprint rather than the platform, so re-check the game-code domain before segmenting | [ApplicationExitInfo](https://developer.android.com/reference/android/app/ApplicationExitInfo) |

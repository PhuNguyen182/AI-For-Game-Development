# Fault-Domain Signals — reading a resolved trace

Sources: [ANRs](https://developer.android.com/topic/performance/vitals/anr), [IL2CPP](https://docs.unity3d.com/Manual/IL2CPP.html), [Diagnosing issues using crash reports and device logs](https://developer.apple.com/documentation/xcode/diagnosing-issues-using-crash-reports-and-device-logs), [Android vitals](https://developer.android.com/topic/performance/vitals).
Covers: SKILL.md §4 — **"Walk the domains in the fixed order and stop at the first match"**, **"Attribute to the frame that faulted, not the frame nearest your own code"**.

What each domain looks like once a trace resolves, and how a stack crossing
several of them is attributed. Everything here assumes the trace is readable;
if it is not, `crash-anr-symbolication` owns that first.

## Recognising each domain

| Domain | What the resolved frames look like | Complication | Source |
|---|---|---|---|
| Game code | Names from this project's own namespaces, appearing as native frames on a shipped build because the build compiled them | An IL2CPP frame still carries the original type and method, so game code is identifiable even though it is native — see [IL2CPP](https://docs.unity3d.com/Manual/IL2CPP.html) | [IL2CPP](https://docs.unity3d.com/Manual/IL2CPP.html) |
| Unity engine | Engine and runtime functions, including the scripting backend and its allocator and job internals | An engine frame very often faults on input the game gave it, which is game code's defect, not the engine's | [IL2CPP](https://docs.unity3d.com/Manual/IL2CPP.html) |
| Third-party SDK | A vendor's own library, frequently on its own thread rather than the main one | An SDK crashing on the main thread during a callback the game registered is still the SDK's frame that faulted | [Android vitals](https://developer.android.com/topic/performance/vitals) |
| System library | Platform libraries with no application code above them, or a main thread blocked inside a platform call | These correlate strongly with a specific manufacturer or OS version, which is the segmentation signal — see [anr-classes-and-mitigation.md](anr-classes-and-mitigation.md) | [ANRs](https://developer.android.com/topic/performance/vitals/anr) |

**Critical caveat**: the domain order is checked outward from what this
project controls, not inward from what looks unfamiliar. An engine or
platform frame at the top of a stack is the most common place a fixable
game-code defect gets misfiled, because the unfamiliar name reads as the
cause when it is the victim.

## Attributing a mixed stack

| Case | Attribution | Source |
|---|---|---|
| Game code calls an SDK, the SDK faults | The SDK — the call site is context, and the faulting frame is the finding | [Android vitals](https://developer.android.com/topic/performance/vitals) |
| SDK calls back into game code, game code faults | Game code, for the same reason in reverse | [Android vitals](https://developer.android.com/topic/performance/vitals) |
| Game code hands the engine invalid state, the engine faults | Game code — the engine frame is where it surfaced, and the defect is the state it was given | [IL2CPP](https://docs.unity3d.com/Manual/IL2CPP.html) |
| The trace is a deliberate abort with a message | Read the message before the frames; a guard that fired is telling you the precondition, not the location | [Diagnosing issues using crash reports and device logs](https://developer.apple.com/documentation/xcode/diagnosing-issues-using-crash-reports-and-device-logs) |
| Several threads present | Only the crashing thread decides a crash; for an ANR every thread matters, because the blocking one may not be the main one — see [anr-classes-and-mitigation.md](anr-classes-and-mitigation.md) | [ANRs](https://developer.android.com/topic/performance/vitals/anr) |

## Evidence that raises or lowers confidence

| Observation | What it supports | Source |
|---|---|---|
| Concentrated on one manufacturer or OS version | A system-library or driver fault, or a device-specific SDK path | [Android vitals](https://developer.android.com/topic/performance/vitals) |
| Present across every device and version | Code this project or its dependencies ship, rather than a platform fault | [Android vitals](https://developer.android.com/topic/performance/vitals) |
| Appeared at a specific app version | Whatever changed in that release — the most direct evidence available, and often faster than reading the stack | [Android vitals](https://developer.android.com/topic/performance/vitals) |
| Disappears when a dependency is disabled | Confirms an SDK attribution rather than merely correlating with it — see [third-party-and-engine-escalation.md](third-party-and-engine-escalation.md) | [Google Play SDK Index](https://developer.android.com/distribute/sdk-index) |
| One sample only | Insufficient for a domain verdict; request more before assigning an owner | [Android vitals](https://developer.android.com/topic/performance/vitals) |

# Third-Party and Engine Escalation — the paths outside code this project writes

Sources: [Google Play SDK Index](https://developer.android.com/distribute/sdk-index), [Unity Issue Tracker](https://issuetracker.unity3d.com/), [Android vitals](https://developer.android.com/topic/performance/vitals), [IL2CPP](https://docs.unity3d.com/Manual/IL2CPP.html).
Covers: SKILL.md §4 — **"In Unity engine code, work down the ladder rather than jumping to a bug report"**, **"In a third-party SDK, update and isolate before contacting the vendor"**.

What to do once the faulting frame belongs to something this project only
consumes. Both paths are slower than a code fix, which is why the domain
order checks game code first. Acting on either belongs to
`tech-lead-csharp-unity` or `tech-lead-sdk-platform`.

## Unity engine faults

Worked as a ladder, in this order, until the signature is resolved.

| Rung | What it establishes | Source |
|---|---|---|
| 1. Search the forums and the issue tracker | Whether the fault is known, and in which stream and version it is fixed — the cheapest rung, and the one that decides whether the rest of the ladder is needed at all | [Unity Issue Tracker](https://issuetracker.unity3d.com/) |
| 2. Upgrade to the version carrying the fix | Whether an already-shipped Unity release removes the signature; this is the resolution in most engine cases, and the decision is `tech-lead-csharp-unity`'s because an upgrade moves every subsystem | [Unity Issue Tracker](https://issuetracker.unity3d.com/) |
| 3. Report a bug | Only once the first two rungs produce nothing — file with the symbolicated trace and the smallest reproduction available, since a report without one rarely progresses | [Unity Issue Tracker](https://issuetracker.unity3d.com/) |

| Check before starting the ladder | Why | Source |
|---|---|---|
| The frame is genuinely the engine's | An engine frame faulting on state the game supplied is game code's defect; confirm the frames below it before escalating — see [fault-domain-signals.md](fault-domain-signals.md) | [IL2CPP](https://docs.unity3d.com/Manual/IL2CPP.html) |
| An interim path exists | A different API or an ordering change often sidesteps a specific engine defect while the ladder runs, rather than waiting on it | [Unity Issue Tracker](https://issuetracker.unity3d.com/) |

**Critical caveat**: an engine upgrade is never a local change. It moves every
other subsystem at once, so recommending one is a proposal to
`tech-lead-csharp-unity`, not a fix this pipeline applies.

## Third-party SDK faults

| Step | What it establishes | Source |
|---|---|---|
| Update to current | Whether the fault is already fixed — the cheapest possible outcome, and the first question a vendor will ask | [Google Play SDK Index](https://developer.android.com/distribute/sdk-index) |
| Disable and observe | Whether the SDK is actually responsible; the signature disappearing is confirmation, where a matching frame alone is only correlation | [Android vitals](https://developer.android.com/topic/performance/vitals) |
| Check the store's SDK index | Whether the version is flagged, or whether the store itself will eventually block it — a policy deadline changes the priority of the whole finding | [Google Play SDK Index](https://developer.android.com/distribute/sdk-index) |
| Contact the vendor | With all three results at once; a report that says only "it crashes" gets a request for exactly the information the previous three steps produce | [Google Play SDK Index](https://developer.android.com/distribute/sdk-index) |
| Decide whether to ship without it | A commercial decision, not a technical one — route it to `tech-lead-sdk-platform` rather than treating the disable step as the resolution | [Android vitals](https://developer.android.com/topic/performance/vitals) |

## What each escalation costs

| Path | Realistic time to a fix | Consequence for the report | Source |
|---|---|---|---|
| Engine version bump | A release cycle, plus regression testing across every system | State the version and let `tech-lead-csharp-unity` weigh it; do not present it as a small change | [Unity Issue Tracker](https://issuetracker.unity3d.com/) |
| Engine bug report | Indefinite; a fix may land in a stream this project is not on | Pair it with an interim recommendation rather than leaving the signature open | [Unity Issue Tracker](https://issuetracker.unity3d.com/) |
| SDK update | Often immediate, and the reason it is the first step | If it resolves the signature, the report closes after verification on a new build | [Google Play SDK Index](https://developer.android.com/distribute/sdk-index) |
| SDK vendor contact | Vendor-dependent and frequently slow | Say so in the report, so the finding is not read as resolved because it was routed | [Google Play SDK Index](https://developer.android.com/distribute/sdk-index) |

# ANR Classes and Mitigation

Sources: [a] vitals/anr, [b] vitals, [c] reference/android/app/ApplicationExitInfo, [d] reference/android/os/StrictMode — under developer.android.com.

Implementing any mitigation belongs to `gameplay-engineer`.

## What an ANR is [a]

- The system decided the app stopped responding: no exception, no crashing frame, only a thread that did not return in time.
- Input dispatch, broadcast, service start and content-provider timeouts are distinct classes; the class narrows the search faster than the stack.
- The blocking thread may not be main (a lock held elsewhere), so every thread's stack is evidence.
- Vitals holds a title to a rate against its installed base [b]: a concentrated fault can be real yet under the threshold.

**Caveat:** an ANR trace names where the thread was, not what made it wait. Blaming the platform call a main thread is parked in is the commonest ANR mistake.

## Causes a Unity title produces

| Cause | Fix lives with |
|---|---|
| Synchronous asset/scene load on main thread (the blocking-completion pattern `unity-addressables` warns against) | `gameplay-engineer` |
| Disk or network on main thread; duration device-dependent, so reproduces on lower tiers [d] | `gameplay-engineer` |
| Lock held across a long operation; both stacks look idle | `csharp-engineer` or `gameplay-engineer` by layer |
| Sustained frame cost, no single long call: a profiling question first (`unity-profiler-diagnostics`) | `gameplay-engineer` |
| Memory pressure during a load: the platform reclaims mid-operation; mitigation, not fix [c] | `gameplay-engineer` |

## Mitigations when no fix exists

| Mitigation | Limit |
|---|---|
| StrictMode main-thread policy [d] | Development-time detector; finds the class of cause, prevents nothing at runtime |
| `ApplicationExitInfo` exit reason [c] | Needs a recent platform version and the next launch; turns "it disappeared" into a named reason |
| Device/OS segmentation [b] | Removes reporters, not the fault; keep the vendor thread open |
| Reduce the work rather than move it | Only one that helps everyone; measure first (`csharp-standards` → `performance-and-algorithms.md`, Verification) |

## Segmentation decision [b][c]

| Observation | Recommendation |
|---|---|
| One manufacturer or OS version | Segmentation plus vendor report (segmentation buys time) |
| Spread across devices and versions | Vendor report alone; broad segmentation drops audience for no fix |
| Low-memory devices | Usually the app's footprint: re-check game code before segmenting |

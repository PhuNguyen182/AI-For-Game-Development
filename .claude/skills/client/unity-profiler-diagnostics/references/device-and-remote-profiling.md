# Device and Remote Profiling — build flags, connections, Deep Profiling availability

Sources: [Collecting performance data](https://docs.unity3d.com/Manual/profiler-profiling-applications.html), [Profiling on an Android device](https://docs.unity3d.com/Manual/android-profile-on-an-android-device.html), [Profiling on an iOS device](https://docs.unity3d.com/Manual/ios-profile-device.html).
Covers: SKILL.md §4 — **"Profile a Development Build on the target device before quoting any number"**, **"Use Deep Profiling to localize a cost, never to quote one"**.

What has to be true of the build and the connection before a capture
represents the shipping game. Which quality tier the device should be running
is not decided here — that is `unity-urp-rendering`'s and the project's
quality settings.

## Build configuration

| Setting | What it decides | Source |
|---|---|---|
| Development Build | Required — a non-development player carries no profiler instrumentation at all, so there is nothing to connect to | [Collecting performance data](https://docs.unity3d.com/Manual/profiler-profiling-applications.html) |
| Autoconnect Profiler | Bakes the Editor's address into the build so it connects at startup, which is the only way to capture the first seconds; it also delays startup while it waits, so leave it off when only steady state matters | [Collecting performance data](https://docs.unity3d.com/Manual/profiler-profiling-applications.html) |
| Deep Profiling Support | A build-time option, separate from the Editor's Deep Profile toggle — a player built without it cannot deep-profile no matter what the window offers | [Collecting performance data](https://docs.unity3d.com/Manual/profiler-profiling-applications.html) |
| Script Debugging | Independent of profiling and adds its own overhead — leave it off for a capture whose absolute numbers will be quoted | [Collecting performance data](https://docs.unity3d.com/Manual/profiler-profiling-applications.html) |

## Connecting

| Path | What it decides | Source |
|---|---|---|
| Android over adb | The reliable option — a USB connection avoids the packet loss and latency a WiFi link adds to the profiler stream itself; the device appears in the Profiler's target dropdown once forwarding is set up | [Profiling on an Android device](https://docs.unity3d.com/Manual/android-profile-on-an-android-device.html) |
| Android over WiFi | Works when the device cannot stay tethered, at the cost of a noisier stream and dropped frames in the capture | [Profiling on an Android device](https://docs.unity3d.com/Manual/android-profile-on-an-android-device.html) |
| iOS over WiFi | The supported route; the Editor host and device must be on the same network with the profiler port range reachable, so a corporate or guest network with client isolation silently prevents the connection | [Profiling on an iOS device](https://docs.unity3d.com/Manual/ios-profile-device.html) |
| Target dropdown shows nothing | Almost always a non-development build, a firewall, or client isolation on the network — not a Unity fault; check the build flags first | [Collecting performance data](https://docs.unity3d.com/Manual/profiler-profiling-applications.html) |

## Why an Editor capture is not a device capture

| Difference | Consequence for the number | Source |
|---|---|---|
| `EditorLoop` and Editor overhead | Counted inside the reported frame time; the same scene reads slower in the Editor for reasons no build pays | [Profiler window reference](https://docs.unity3d.com/Manual/ProfilerWindow.html) |
| Desktop CPU and GPU versus handset | A mobile bottleneck often does not exist on the development machine at all, so an Editor pass can report "fine" for a scene that misses budget on device | [Collecting performance data](https://docs.unity3d.com/Manual/profiler-profiling-applications.html) |
| Thermal state | A handset throttles after sustained load, so a capture taken in the first thirty seconds overstates sustained performance; run the device warm before the capture that will be quoted | [Profiling on an Android device](https://docs.unity3d.com/Manual/android-profile-on-an-android-device.html) |
| Scripting backend | Editor runs managed code under its own runtime while a shipped mobile player is typically IL2CPP, so managed-call costs do not transfer one to one | [Collecting performance data](https://docs.unity3d.com/Manual/profiler-profiling-applications.html) |

**Critical caveat**: Deep Profiling inflates every number it reports, because
it instruments every managed call. Use it to find the culprit, then take the
figure you will quote from a capture with it switched off.

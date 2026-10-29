# Device and Remote Profiling

Docs: https://docs.unity3d.com/Manual/ — pages `profiler-profiling-applications.html`, `android-profile-on-an-android-device.html`, `ios-profile-device.html`.

## Build configuration
| Setting | Rule |
|---|---|
| Development Build | Required; a non-development player has no profiler instrumentation to connect to |
| Autoconnect Profiler | Bakes the Editor address in so startup is captured; delays startup while waiting, so leave off for steady state |
| Deep Profiling Support | Build-time option separate from the Editor toggle; a player built without it cannot deep-profile |
| Script Debugging | Adds its own overhead; off for a capture whose absolute numbers will be quoted |

## Connecting
| Path | Rule |
|---|---|
| Android over adb | Reliable; USB avoids the packet loss and latency WiFi adds to the profiler stream. Device appears in the target dropdown once forwarding is set up |
| Android over WiFi | For a device that cannot stay tethered; noisier stream, dropped frames |
| iOS over WiFi | Supported route; host and device on one network with the profiler port range reachable. Client isolation (corporate/guest networks) silently blocks it |
| Empty target dropdown | Usually a non-development build, firewall or client isolation; check build flags first |

## Editor vs device
| Difference | Consequence |
|---|---|
| `EditorLoop` / Editor overhead | Counted in the reported frame time |
| Desktop vs handset CPU/GPU | A mobile bottleneck may not exist on the dev machine |
| Thermal state | Handsets throttle under sustained load; a first-30-seconds capture overstates; run warm before the quoted capture |
| Scripting backend | Editor runs managed code on its runtime, mobile players are typically IL2CPP; managed-call costs do not transfer 1:1 |

Which quality tier the device runs is the project's quality settings, not decided here.

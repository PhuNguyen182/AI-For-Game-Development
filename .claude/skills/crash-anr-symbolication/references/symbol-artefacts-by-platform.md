# Symbol Artefacts by Platform — what resolves which frames

Sources: [Diagnose native crashes](https://developer.android.com/games/optimize/crash-diagnose), [Shrink, obfuscate, and optimize your app](https://developer.android.com/build/shrink-code), [Get deobfuscated crash reports](https://firebase.google.com/docs/crashlytics/get-deobfuscated-reports?platform=android), [Adding identifiable symbol names to a crash report](https://developer.apple.com/documentation/xcode/adding-identifiable-symbol-names-to-a-crash-report), [IL2CPP](https://docs.unity3d.com/Manual/IL2CPP.html), [Android symbols](https://docs.unity3d.com/Manual/android-symbols.html).
Covers: SKILL.md §4 — **"Compare build and symbol identifiers rather than version strings"**, **"Name which artefact is missing for the platform in hand"**, **"Treat managed and native frames as separate problems on a Unity title"**.

Which artefact resolves which kind of frame, and how a build's identity is
established independently of the version players see. Producing these
artefacts is `build-run-engineer`'s and `tech-lead-sdk-platform`'s; this file
is about recognising which one is absent.

## The artefacts

| Artefact | Resolves | Produced by | Source |
|---|---|---|---|
| Native debug symbols | Engine, plugin and IL2CPP-generated frames on Android — everything compiled to machine code | The Android build, when symbol generation is enabled; a release build strips them from the shipped binary by design | [Android symbols](https://docs.unity3d.com/Manual/android-symbols.html) |
| Obfuscation mapping file | Java and Kotlin frames renamed by the shrinking step — plugin and platform-layer code, not the game's C# | The shrinker, when code shrinking or obfuscation is enabled | [Shrink, obfuscate, and optimize your app](https://developer.android.com/build/shrink-code) |
| dSYM bundle | Native frames on Apple platforms, including everything IL2CPP generated | The Xcode build; the shipped binary carries no symbol names | [Adding identifiable symbol names to a crash report](https://developer.apple.com/documentation/xcode/adding-identifiable-symbol-names-to-a-crash-report) |
| Service-side association | Nothing by itself — it is the step that makes an artefact usable by the reporting service for a specific build | Uploading the artefact to the service | [Get deobfuscated crash reports](https://firebase.google.com/docs/crashlytics/get-deobfuscated-reports?platform=android) |

**Critical caveat**: "symbols are missing" names no artefact and no platform,
so it cannot be acted on. Native debug symbols and the obfuscation mapping
file resolve different frames on the same Android trace, and having one says
nothing about the other.

## Build identity

| Subject | What it decides | Source |
|---|---|---|
| Build or debug identifier | The value the platform records in the binary and in the symbol artefact; symbolication matches on this, and on nothing else | [Adding identifiable symbol names to a crash report](https://developer.apple.com/documentation/xcode/adding-identifiable-symbol-names-to-a-crash-report) |
| Marketing version | What players see; two builds can carry the same version and share no binary, which is why a version match proves nothing | [Diagnose native crashes](https://developer.android.com/games/optimize/crash-diagnose) |
| Rebuilding is not reproducible for this purpose | Rebuilding the same source generally produces a binary with a different identifier, so symbols regenerated after the fact do not retroactively match the crashing build | [Diagnose native crashes](https://developer.android.com/games/optimize/crash-diagnose) |
| Consequence of a mismatch | Nothing can resolve the existing trace; the only path forward is a new build with symbols retained and a fresh report from it | [Get deobfuscated crash reports](https://firebase.google.com/docs/crashlytics/get-deobfuscated-reports?platform=android) |

## Unity and IL2CPP

| Subject | What it decides | Source |
|---|---|---|
| C# becomes native code | IL2CPP converts managed assemblies to C++ and compiles them, so game-code frames appear in the native stack rather than as a managed exception trace | [IL2CPP](https://docs.unity3d.com/Manual/IL2CPP.html) |
| Two failure modes, not one | Native symbols can be present while managed frames still read as generated names, or the reverse — so one kind resolving is not evidence about the other | [IL2CPP](https://docs.unity3d.com/Manual/IL2CPP.html) |
| Generated names | IL2CPP-produced function names encode the original type and method, which is what makes a resolved native frame attributable back to game code at all | [IL2CPP](https://docs.unity3d.com/Manual/IL2CPP.html) |
| Symbol size | Full symbol output is large enough that pipelines routinely produce a reduced variant instead; the reduced form resolves less, which shows up as a partially readable trace rather than an error | [Android symbols](https://docs.unity3d.com/Manual/android-symbols.html) |
| Managed exceptions | A managed exception that terminates the process is not the same signal as a native fault, and the two reach the reporting service by different paths — treat a missing one as absent, not as fixed | [IL2CPP](https://docs.unity3d.com/Manual/IL2CPP.html) |

## Diagnosing which case applies

| Observation | Most likely cause | Source |
|---|---|---|
| Every frame is an address | No artefact is associated for this build, or none matching it exists | [Get deobfuscated crash reports](https://firebase.google.com/docs/crashlytics/get-deobfuscated-reports?platform=android) |
| System frames resolve, the app's do not | The app's own artefact is missing while the platform's own symbols are present | [Diagnose native crashes](https://developer.android.com/games/optimize/crash-diagnose) |
| Names appear but are single letters or generated | The obfuscation mapping file is missing rather than the native symbols | [Shrink, obfuscate, and optimize your app](https://developer.android.com/build/shrink-code) |
| Some app frames resolve and the top one does not | A reduced or partial symbol set, which is the case most likely to be mistaken for a usable trace | [Android symbols](https://docs.unity3d.com/Manual/android-symbols.html) |

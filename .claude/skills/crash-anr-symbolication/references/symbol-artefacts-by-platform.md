# Symbol Artefacts by Platform

Docs: Android native crashes https://developer.android.com/games/optimize/crash-diagnose (NC) · code shrinking https://developer.android.com/build/shrink-code (SH) · Crashlytics https://firebase.google.com/docs/crashlytics/get-deobfuscated-reports?platform=android (CL) · Apple https://developer.apple.com/documentation/xcode/adding-identifiable-symbol-names-to-a-crash-report (AP) · Unity https://docs.unity3d.com/Manual/android-symbols.html (US), https://docs.unity3d.com/Manual/IL2CPP.html (IL).

Producing these is `build-release-engineer`'s and `sdk-platform-engineer`'s; this file identifies which one is absent.

## Artefacts
| Artefact | Resolves | Produced by |
|---|---|---|
| Native debug symbols | Engine, plugin and IL2CPP-generated frames on Android (all machine code) (US) | Android build with symbol generation enabled; release strips them from the shipped binary by design |
| Obfuscation mapping file | Java/Kotlin frames renamed by shrinking: plugin and platform-layer code, not game C# (SH) | The shrinker, when shrinking/obfuscation is on |
| dSYM bundle | Native frames on Apple platforms incl. all IL2CPP output (AP) | Xcode build; shipped binary has no symbol names |
| Service-side association | Nothing alone; makes an artefact usable by the reporting service for a specific build (CL) | Uploading it |

Native debug symbols and the mapping file resolve different frames of one Android trace; having one says nothing about the other.

## Build identity
- The build/debug identifier recorded in the binary and the symbol artefact is the only match key (AP). The marketing version can match across builds sharing no binary (NC).
- Rebuilding the same source generally yields a different identifier, so regenerated symbols do not match the crashed build (NC). Mismatch → only a new symboled build and fresh report help (CL).

## Unity and IL2CPP
- IL2CPP converts C# to C++ and compiles it, so game-code frames appear in the native stack (IL). Generated names encode the original type and method, which is what makes a resolved native frame attributable to game code.
- Native symbols can be present while managed-derived frames still read as generated names, or the reverse.
- Full symbol output is large; pipelines often produce a reduced variant that resolves less, showing as a partially readable trace, not an error (US).
- A managed exception that kills the process is a different signal from a native fault and reaches the service by another path; a missing one is absent, not fixed (IL).

## Diagnosis
| Observation | Likely cause |
|---|---|
| Every frame is an address | No artefact associated for this build, or none matching exists (CL) |
| System frames resolve, app's do not | The app's own artefact is missing (NC) |
| Names appear but are single letters/generated | Obfuscation mapping missing, not native symbols (SH) |
| Some app frames resolve, the top one does not | Reduced or partial symbol set; the case most often mistaken for a usable trace (US) |

# Root Links — symbolication across Android, Apple and Unity

Source: the root documentation pages listed below, as provided for this skill.
Covers: the whole skill — provenance and version anchor for every file in
this folder.

Anchors every link in this folder. These are platform and vendor documents
rather than versioned packages, so there is no version to pin; the Unity
Manual pages are published unversioned and resolve to the current release.
Deep console-navigation articles are deliberately avoided, because those move
more often than the concepts they describe.

## Roots

| Subject | Holds | Source |
|---|---|---|
| Android native crashes | How native stacks are captured and what is needed to read them | [Diagnose native crashes](https://developer.android.com/games/optimize/crash-diagnose) |
| Android code shrinking | The obfuscation and shrinking step that renames managed symbols, and the mapping file it produces | [Shrink, obfuscate, and optimize your app](https://developer.android.com/build/shrink-code) |
| Crashlytics deobfuscation | Attaching mapping and native symbol artefacts so the service resolves frames | [Get deobfuscated crash reports](https://firebase.google.com/docs/crashlytics/get-deobfuscated-reports?platform=android) |
| Apple symbol names | What a dSYM is and how a report becomes readable with one | [Adding identifiable symbol names to a crash report](https://developer.apple.com/documentation/xcode/adding-identifiable-symbol-names-to-a-crash-report) |
| Apple crash reports | How Apple collects and presents reports for a shipped app | [Diagnosing issues using crash reports and device logs](https://developer.apple.com/documentation/xcode/diagnosing-issues-using-crash-reports-and-device-logs) |
| Unity IL2CPP | Why a Unity build's C# appears as native code in a trace | [IL2CPP](https://docs.unity3d.com/Manual/IL2CPP.html) |
| Unity Android symbols | What the Editor produces for symbolication on an Android build | [Android symbols](https://docs.unity3d.com/Manual/android-symbols.html) |

## What this skill deliberately does not pin

| Subject | Why it is not linked here | Source |
|---|---|---|
| Console upload paths | Play Console and App Store Connect layouts change without notice, so a described click path ages badly and helps nobody | [Get deobfuscated crash reports](https://firebase.google.com/docs/crashlytics/get-deobfuscated-reports?platform=android) |
| Exact artefact filenames and directory layout | These vary by Editor version, build type and toolchain; read the actual build output rather than a remembered path — see [symbol-artefacts-by-platform.md](symbol-artefacts-by-platform.md) | [Android symbols](https://docs.unity3d.com/Manual/android-symbols.html) |
| Command-line symbolication tooling | Platform tools are renamed and superseded between toolchain releases; this skill establishes what is missing, and the owner running the pipeline uses whatever is current | [Diagnose native crashes](https://developer.android.com/games/optimize/crash-diagnose) |

Read the build output and the service for anything concrete. This skill's job
is to decide whether a trace is readable and what is missing, not to restate
paths it can inspect.

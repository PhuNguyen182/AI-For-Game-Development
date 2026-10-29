---
name: crash-anr-symbolication
description: "Confirm a crash/ANR trace is fully symbolicated and uploaded symbols match the crashing build id: IL2CPP native symbols, obfuscation mapping, dSYM, Crashlytics. Use as stage 2 of a production crash investigation."
user-invocable: false
---

# Crash and ANR Symbolication

Not for: confirming the report source (`crash-anr-reporting-gate`), attributing the fault (`crash-anr-fault-domain-triage`), producing the build or wiring the upload (`build-release-engineer`, `sdk-platform-engineer`), Editor stack traces (`qa-automation-engineer`), pre-release player-build faults (`build-fault-triage`).
Docs: https://developer.android.com/games/optimize/crash-diagnose · https://docs.unity3d.com/Manual/android-symbols.html · https://docs.unity3d.com/Manual/IL2CPP.html · https://firebase.google.com/docs/crashlytics/get-deobfuscated-reports · https://developer.apple.com/documentation/xcode/adding-identifiable-symbol-names-to-a-crash-report — all unversioned. Console upload paths and artefact filenames vary by Editor/toolchain: read the real build output, not a remembered path.

| Reference | Read when |
|---|---|
| [symbol-artefacts-by-platform.md](references/symbol-artefacts-by-platform.md) | Deciding which artefact is missing, or whether the symbols on file belong to this build |

## Steps
1. **Check the faulting (top) frame before counting resolved frames** — it decides the fault domain, so an unresolved top frame makes the trace as unusable as a fully stripped one.
2. **Compare build and symbol identifiers, never version strings** — equal marketing versions can share no binary ([symbol-artefacts-by-platform.md](references/symbol-artefacts-by-platform.md)).
3. **Name the missing artefact and platform** — native debug symbols, obfuscation mapping or dSYM resolve different frames; "symbols are missing" is not actionable.
4. **On a Unity IL2CPP title treat managed-derived and native frames separately** — one kind resolving says nothing about the other.
5. **Identifiers match → attach the existing artefact**, then re-check from step 1; a wrong file attaches quietly, so attaching is not resolving.
6. **Identifiers differ → request a new build with symbol generation** (`build-release-engineer`) and the upload step (`sdk-platform-engineer`), then wait for a fresh matching report. The crashed binary cannot be fixed retroactively and a rebuild of the same source gets a different id.
7. **Unresolvable and no new build or other resolving sample → report a block**, never reason past it; a domain guessed from offsets routes work to an owner who cannot act. If the access needed to attach symbols sits outside this pipeline, name who has it. If samples may be past service retention, say so (`crash-anr-reporting-gate`) rather than waiting.

## Never
- Build, upload or edit anything here — diagnose the gap and route it.

## Output
```
## Symbolication Check — <RESOLVED / BLOCKED>
- Trace source: <Play Console vitals / Crashlytics / App Store Connect>
- Faulting frame resolves: <yes / no>
- Other frames: <all resolve / partial — which layers>
- Build identity matched against symbols: <yes / no / unknown>
- Artefact involved: <native debug symbols / obfuscation mapping / dSYM / IL2CPP managed frames>
- Decision: <proceed / block>
- Action requested: <attach existing symbols / new build with symbol generation and upload / none needed>
- Routed to: <crash-anr-fault-domain-triage / build-release-engineer / sdk-platform-engineer>
```
On request only, add `Known limitations`, `Latent concerns` and `Future remediation`, each with its trigger.

## Example
- "Most of the stack reads, just root-cause it from what we can see" → declined: the unresolved frames are the top, where the domain is decided; the readable rest only shows how code got there, and the nearest resolved frame would blame the game code that called an engine or SDK fault. Held the gate and requested the missing artefact.

---
name: crash-anr-symbolication
description: "Crash/ANR symbolication: IL2CPP symbols, mapping, dSYM, build id match. Use as stage 2 of a crash investigation."
user-invocable: false
---

# Crash and ANR Symbolication

- **Not for:** confirming the report source (`crash-anr-reporting-gate`).
- **Not for:** attributing the fault (`crash-anr-fault-domain-triage`).
- **Not for:** producing the build or wiring the upload (`build-release-engineer`, `sdk-platform-engineer`).
- **Not for:** Editor stack traces (`qa-automation-engineer`).
- **Not for:** pre-release player-build faults (`build-fault-triage`).
- **Docs:** https://developer.android.com/games/optimize/crash-diagnose · https://docs.unity3d.com/Manual/android-symbols.html · https://docs.unity3d.com/Manual/IL2CPP.html
  - **Crashlytics:** https://firebase.google.com/docs/crashlytics/get-deobfuscated-reports.
  - **Apple:** https://developer.apple.com/documentation/xcode/adding-identifiable-symbol-names-to-a-crash-report.
  - **Versioning:** all unversioned.
  - **Paths:** console upload paths and artefact filenames vary by Editor/toolchain; read the real build output, not a remembered path.

## References
- **[symbol-artefacts-by-platform.md](references/symbol-artefacts-by-platform.md):** Deciding which artefact is missing, or whether the symbols on file belong to this build.

## Steps
1. **Check the faulting (top) frame before counting resolved frames:** it decides the fault domain.
   - **Unresolved top frame:** the trace is as unusable as a fully stripped one.
2. **Compare build and symbol identifiers, never version strings:** equal marketing versions can share no binary ([symbol-artefacts-by-platform.md](references/symbol-artefacts-by-platform.md)).
3. **Name the missing artefact and platform:** native debug symbols, obfuscation mapping or dSYM resolve different frames.
   - **Not actionable:** "symbols are missing".
4. **On a Unity IL2CPP title treat managed-derived and native frames separately:** one kind resolving says nothing about the other.
5. **Identifiers match → attach the existing artefact:** then re-check from step 1.
   - **Why:** a wrong file attaches quietly, so attaching is not resolving.
6. **Identifiers differ → request a new build with symbol generation:** `build-release-engineer` for the build, `sdk-platform-engineer` for the upload step; then wait for a fresh matching report.
   - **Why:** the crashed binary cannot be fixed retroactively and a rebuild of the same source gets a different id.
7. **Unresolvable and no new build or other resolving sample → report a block:** never reason past it.
   - **Why:** a domain guessed from offsets routes work to an owner who cannot act.
   - **Access outside this pipeline:** if the access needed to attach symbols sits outside this pipeline, name who has it.
   - **Retention:** if samples may be past service retention, say so (`crash-anr-reporting-gate`) rather than waiting.

## Never
- **Edits:** build, upload or edit anything here — diagnose the gap and route it.

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

## Example
- **"Most of the stack reads, just root-cause it from what we can see":** declined.
  - **Why:** the unresolved frames are the top, where the domain is decided.
  - **Readable rest:** it only shows how code got there; the nearest resolved frame would blame the game code that called an engine or SDK fault.
  - **Did instead:** held the gate and requested the missing artefact.

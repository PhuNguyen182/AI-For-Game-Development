---
name: investigate-device-crash
description: Investigate a crash or ANR on the connected Android/iOS device (adb logcat, idevicecrashreport) and report fault domain, root cause and fix direction
argument-hint: "[android|ios] [package-or-bundle-id]"
allowed-tools: PowerShell, Bash, Read, Grep, Glob, Skill
---

# Investigate a crash/ANR on the connected device

`$ARGUMENTS`: optional `[android|ios] [package-or-bundle-id]`; infer what is missing, ask if still ambiguous. Live-device only: production telemetry → `crash-anr-investigator`; verifying a known build artifact → `build-release-engineer`. Final report to the GD in Vietnamese, evidence verbatim. One physical device project-wide (`core.md`).

1. **Device** — `adb devices -l`, and `idevice_id -l` if present. One answers, no platform given → use it. Both or neither → disambiguate from `$1` or ask. None connected → `Status: Blocked` (a correct result).
2. **App** — `$2` is the package/bundle id. Else Android: `adb shell dumpsys window | grep mCurrentFocus`; fallback either platform: `applicationIdentifier` in `ProjectSettings/ProjectSettings.asset` (suggestion only). Ambiguous or fallback → confirm with the GD before pulling logs.
3. **Evidence** — Android (logcat is primary; do not assume root for `/data/anr/traces.txt`), filtered to the package: `adb logcat -d -b crash`; `adb logcat -d | grep -A 50 "FATAL EXCEPTION"`; `adb logcat -d | grep -B 5 -A 30 "ANR in <package>"`. iOS (best-effort, no Xcode): `idevicecrashreport -e <dir>`; `idevicesyslog` if reproducible live; `libimobiledevice` missing → blocked, never fake iOS coverage from Android tooling. Nothing found → say so.
4. **Classify** — build-only (AOT/IL2CPP, stripping, native ABI, signing) → read `.claude/skills/build-fault-triage/SKILL.md` directly. Else apply the game code → engine → SDK → system library → non-actionable order from `.claude/skills/crash-anr-fault-domain-triage/references/fault-domain-signals.md` and `anr-classes-and-mitigation.md`, read directly; never invoke that skill or the reporting-gate/symbolication skills (gated to production telemetry, they decline a local trace). Unresolved native addresses → symbolicate only if the artifact exists (`il2cpp_symbols.zip` + `addr2line`, or `.dSYM` + `atos`); missing → name it and stop.
5. **Report** — finding fields per `qa-standards`, plus root cause and fix direction.
```
## Device Crash/ANR Investigation — <package/bundle id>
- Status: Done | Blocked  |  Platform / Signal / Location / Expected / Actual / Evidence / Reproduction
- Fault domain: Game code | Unity engine | SDK | System library | Build-only | Non-actionable
- Root cause: <evidenced only>  |  Severity: Critical|High|Medium|Low
- Fix direction: <concrete file/class/layer, never a diff>  |  Owner: <agent-id>
- Verified on real device: yes  |  Not covered: <tiers/platform/conditions not hit this session>
```

## Never
- Edit code, rebuild, re-sign, flash, or touch device state beyond reading logs.
- Claim a root cause the evidence does not support, or propose a diff (name the change; the owner writes it).
- Present this as production telemetry, or an inference as confirmed.

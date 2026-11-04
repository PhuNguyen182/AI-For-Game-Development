---
name: investigate-device-crash
description: "Device crash/ANR via adb logcat, idevicecrashreport: fault domain, root cause. Use when a test device crashes."
argument-hint: "[android|ios] [package-or-bundle-id]"
allowed-tools: PowerShell, Bash, Read, Grep, Glob, Skill
---

# Investigate a crash/ANR on the connected device

- **Not for:** production telemetry (`crash-anr-investigator`), verifying a known build artifact (`build-release-engineer`).
- **Scope:** live-device only.
- **Input:** `$ARGUMENTS`: optional `[android|ios] [package-or-bundle-id]`.
- **Missing argument:** infer what is missing; still ambiguous → `AskUserQuestion`.
- **Final report:** to the GD in Vietnamese, evidence verbatim.
- **Device hold:** one physical device project-wide (`core.md`).

## Steps
1. **Device:** `adb devices -l`, and `idevice_id -l` if present.
   - **One answers, no platform given:** use it.
   - **Both or neither:** disambiguate from `$1`, else `AskUserQuestion`.
   - **None connected:** `Status: Blocked` (a correct result).
2. **App:** `$2` is the package/bundle id.
   - **Else, Android:** `adb shell dumpsys window | grep mCurrentFocus`.
   - **Fallback, either platform:** `applicationIdentifier` in `ProjectSettings/ProjectSettings.asset` (suggestion only).
   - **Ambiguous or fallback:** confirm with the GD via `AskUserQuestion` before pulling logs.
3. **Evidence:** collect per platform:
   - **Android source:** logcat is primary; do not assume root for `/data/anr/traces.txt`.
   - **Android commands:** filtered to the package:
     - **Crash buffer:** `adb logcat -d -b crash`.
     - **Fatal exceptions:** `adb logcat -d | grep -A 50 "FATAL EXCEPTION"`.
     - **ANR:** `adb logcat -d | grep -B 5 -A 30 "ANR in <package>"`.
   - **iOS commands:** best-effort, no Xcode: `idevicecrashreport -e <dir>`; `idevicesyslog` if reproducible live.
   - **iOS tooling missing:** `libimobiledevice` missing → blocked, never fake iOS coverage from Android tooling.
   - **Nothing found:** say so.
4. **Classify:** build-only first, then the fault domain.
   - **Build-only:** (AOT/IL2CPP, stripping, native ABI, signing) → read `.claude/skills/build-fault-triage/SKILL.md` directly.
   - **Not build-only:** apply the game code → engine → SDK → system library → non-actionable order.
   - **Order source:** `.claude/skills/crash-anr-fault-domain-triage/references/fault-domain-signals.md` and `anr-classes-and-mitigation.md`, read directly.
   - **Gated skills:** never invoke `crash-anr-fault-domain-triage` or the reporting-gate/symbolication skills (gated to production telemetry, they decline a local trace).
   - **Unresolved native addresses:** symbolicate only if the artifact exists (`il2cpp_symbols.zip` + `addr2line`, or `.dSYM` + `atos`).
   - **Symbol artifact missing:** name it and stop.
5. **Report:** finding fields per `qa-standards`, plus root cause and fix direction, in the `## Output` form.
   - **Real device:** the report says "verified on real device: yes".

## Never
- **Changes:** edit code, rebuild, re-sign, flash, or touch device state beyond reading logs.
- **Unsupported root cause:** claim a root cause the evidence does not support.
- **Diffs:** propose a diff (name the change; the owner writes it).
- **Misstated evidence:** present this as production telemetry, or an inference as confirmed.

## Output
```
## Device Crash/ANR Investigation — <package/bundle id>
- Status: Done | Blocked  |  Platform / Signal / Location / Expected / Actual / Evidence / Reproduction
- Fault domain: Game code | Unity engine | SDK | System library | Build-only | Non-actionable
- Root cause: <evidenced only>  |  Severity: Critical|High|Medium|Low
- Fix direction: <concrete file/class/layer, never a diff>  |  Owner: <agent-id>
- Not covered: <tiers/platform/conditions not hit this session>
```

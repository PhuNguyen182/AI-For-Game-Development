---
description: Investigate a crash or ANR on the currently connected Android/iOS device and report the bug, root cause, and fix direction
argument-hint: "[android|ios] [package-or-bundle-id]"
allowed-tools: Powershell, Bash, Read, Grep, Glob, Skill
---

# Investigate a crash/ANR on the connected device

`$ARGUMENTS`: optional `[android|ios] [package-or-bundle-id]` — infer what's missing below, ask the user rather than guess if it stays ambiguous. Ad-hoc, live-device only: not production telemetry (`crash-anr-investigator`'s job) and not verifying a known build artifact (`build-verification-tester`'s job) — redirect if that's what's meant. Reason in English (`language-and-comments.md`); final report to the user is in Vietnamese, evidence verbatim.

**1 — Detect the device**: `adb devices -l`, and `idevice_id -l` if present. One answers, no platform given → use it. Both or neither → disambiguate from `$1` or ask, never pick arbitrarily. None connected → `Status: Blocked` (a correct result per `verification-standards.md`).

**2 — Identify the app**: `$2` given → use as package/bundle id. Else infer — Android via `adb shell dumpsys window | grep mCurrentFocus`; fallback either platform via `applicationIdentifier` in `ProjectSettings/ProjectSettings.asset` (suggestion only). Ambiguous or fallback used → confirm with the user before pulling logs.

**3 — Pull evidence**: Android — `adb logcat -d -b crash`; `adb logcat -d | grep -A 50 "FATAL EXCEPTION"`; `adb logcat -d | grep -B 5 -A 30 "ANR in <package>"`, filtered to the target package (logcat is primary, don't assume root access to `/data/anr/traces.txt`). iOS (best-effort, no Xcode) — `idevicecrashreport -e <dir>`; `idevicesyslog` if reproducible live; missing `libimobiledevice` → report blocked, never fake iOS coverage from Android tooling. Nothing found → say so honestly, don't manufacture a finding.

**4 — Classify the fault**: build-only (AOT/IL2CPP, stripping, native ABI, signing) → read `.claude/skills/build-fault-triage/SKILL.md` directly. Otherwise apply the game code → engine → SDK → system library → non-actionable order from `.claude/skills/crash-anr-fault-domain-triage/references/{fault-domain-signals,anr-classes-and-mitigation}.md`, read directly — never invoke that skill or the reporting-gate/symbolication skills (gated to production telemetry, will decline a local trace). Unresolved native addresses → symbolicate only if the matching artifact exists (`il2cpp_symbols.zip`+`addr2line`, or `.dSYM`+`atos`); missing → name it and stop, never guess past the trace.

**5 — Report**, every element `defect-reporting.md` requires plus root cause and fix direction:
```
## Device Crash/ANR Investigation — <package/bundle id>
- Status: Done | Blocked  |  Platform / Signal / Location / Expected / Actual / Evidence / Reproduction
- Fault domain: Game code | Unity engine | SDK | System library | Build-only | Non-actionable
- Root cause: <evidenced only>  |  Severity: Critical|High|Medium|Low
- Fix direction: <concrete file/class/layer, never a diff>  |  Owner: <agent-id>
- Verified on real device: yes  |  Not covered: <tiers/platform/conditions not hit this session>
```
Translate to Vietnamese for the user, evidence verbatim.

**Guardrails**: never edit code, rebuild, re-sign, flash, or touch device state beyond reading logs; never claim a root cause the evidence doesn't support, or propose a code diff (name the change, the owner writes it); never present this as production telemetry or an inference as confirmed; always state `Not covered`.

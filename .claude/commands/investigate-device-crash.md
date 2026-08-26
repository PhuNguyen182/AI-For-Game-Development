---
description: Investigate a crash or ANR on the currently connected Android/iOS device and report the bug, root cause, and fix direction
argument-hint: "[android|ios] [package-or-bundle-id]"
allowed-tools: Bash, Read, Grep, Glob, Skill
---

# Investigate a crash/ANR on the connected device

Arguments: `$ARGUMENTS` — optional `[android|ios] [package-or-bundle-id]`. Either or both may be omitted; infer what's missing per Step 1/2 below, and confirm with the user before proceeding if it stays ambiguous. Never guess silently.

This command is for **live, ad-hoc investigation of whatever is on the device plugged in right now**. It is not the right tool for two adjacent jobs already owned elsewhere in this project:
- Production telemetry (Play Console vitals, Firebase Crashlytics, App Store Connect) → that is `crash-anr-investigator`'s job, not this command's. Do not invoke it here; if the user actually meant a production signal, say so and redirect.
- Verifying a known, already-produced build artifact against its critical paths and test suite → that is `build-verification-tester`'s job. This command investigates one crash/ANR signature, it does not run a verification pass.

Work internally in English throughout (reasoning, log excerpts, identifiers), per `.claude/rules/language-and-comments.md` — but the **final report handed back to the user must be written in Vietnamese**, with log/code evidence quoted verbatim. This override applies even though the rest of this command's own instructions are in English.

## Step 1 — Detect the connected device

Run:
```
adb devices -l
```
and, if the binary exists, also:
```
idevice_id -l
```

- If exactly one device answers and no platform argument was given, use it.
- If both Android and iOS devices answer, or neither does, require the platform to be disambiguated — from `$1` if given, otherwise ask the user. Do not pick one arbitrarily.
- If nothing is connected at all: stop here and report `Status: Blocked` — "no device connected" is a correct, honest result, not a failure to work around, per `.claude/rules/qa/verification-standards.md`.

## Step 2 — Identify the target app

- If `$2` (or the second token of `$ARGUMENTS`) is given, use it as the package name (Android) or bundle ID (iOS).
- Otherwise, try to infer it:
  - Android: `adb shell dumpsys window | grep mCurrentFocus` for the foreground app.
  - Fallback for either platform: read `applicationIdentifier` out of this Unity project's `ProjectSettings/ProjectSettings.asset` (`grep`/`Read`) as a *suggestion* only.
- If inference is ambiguous or the fallback had to be used, state what you inferred and ask the user to confirm before pulling logs — never silently investigate the wrong app.

## Step 3 — Pull crash/ANR evidence

**Android**
```
adb logcat -d -b crash
adb logcat -d | grep -A 50 "FATAL EXCEPTION"
adb logcat -d | grep -B 5 -A 30 "ANR in <package>"
```
Filter all output to the target package. Do not assume root access to `/data/anr/traces.txt` — the logcat ANR reason block is the primary source unless a rooted/debug device makes the trace file directly readable.

**iOS (best-effort — this environment has no Xcode)**
```
idevicecrashreport -e <output-dir>
idevicesyslog
```
Pull already-synced `.ips`/`.crash` files with `idevicecrashreport`, and capture a short `idevicesyslog` window around the failure if it's reproducible live. If `libimobiledevice` tooling isn't installed, report that plainly as a blocked platform — do not attempt to fake iOS coverage from Android tooling or guesswork.

Capture the raw evidence before interpreting it. If nothing matching a crash or ANR is found for the target package, report that honestly (`Status: Blocked` or "no fault found in the current log window") rather than manufacturing a finding.

## Step 4 — Classify the fault

Reuse this project's existing domain knowledge rather than re-deriving it:

1. Invoke the `build-fault-triage` skill (`.claude/skills/qa/build-fault-triage/SKILL.md`) for build-only fault classes — AOT/IL2CPP limits, managed code stripping, native library/ABI mismatches, signing/permission faults. It already covers Android logcat and the device console as log sources, so it applies directly here.
2. For everything else, apply the same layered attribution order `crash-anr-fault-domain-triage` uses — game code → Unity engine → third-party SDK → system library → non-actionable — by reading its reference files directly (`.claude/skills/live-ops/crash-anr-fault-domain-triage/references/fault-domain-signals.md` and `references/anr-classes-and-mitigation.md` for ANRs specifically). Do not invoke that skill itself or `crash-anr-reporting-gate`/`crash-anr-symbolication` — all three are hard-gated to confirmed production telemetry and will incorrectly decline or redirect a local device trace.
3. If the stack contains unresolved/stripped native addresses, attempt local symbolication only when the matching artifact already exists in this project's build output (IL2CPP `il2cpp_symbols.zip` + `addr2line`, or a `.dSYM` + `atos` for iOS). If it doesn't exist, name the missing artifact and stop — never guess a root cause the trace doesn't support.

## Step 5 — Report

Produce a report carrying every element `.claude/rules/qa/defect-reporting.md` requires, plus the root cause and fix direction the user asked for:

```
## Device Crash/ANR Investigation — <package/bundle id>
- Status: Done | Blocked
- Platform: Android | iOS — <device model, OS version>
- Signal: Crash | ANR
- Location: <path:line if resolved, else the faulting frame/offset>
- Expected: <what should have happened, and its source — Tech Spec clause, GDD, or "normal operation" if no spec is implicated>
- Actual: <what was observed, from the evidence>
- Evidence: <the log excerpt / stack trace that proves it>
- Reproduction: <steps if known, and how many attempts reproduced it — never "reliable" from a single sample>
- Fault domain: Game code | Unity engine | Third-party SDK | System library | Build-only (AOT/stripping/native lib/signing) | Non-actionable
- Root cause: <evidenced from the resolved trace — never a guess past what it supports>
- Severity: Critical | High | Medium | Low — impact if shipped, per defect-reporting.md's table
- Fix direction: <the concrete file/class/layer to change, or the config to fix — never a code diff>
- Owner: <agent-id — csharp-engineer / unity-engineer / tech-lead-sdk-platform / tech-lead-performance / tech-lead-csharp-unity, by the evidenced domain>
- Verified on real device: yes — <this is what an Editor-only result can never claim, per verification-standards.md>
- Not covered: <what this investigation did not check — other device tiers, the other platform, intermittent conditions not hit this session>
```

Then translate this into the final Vietnamese message to the user, keeping log excerpts, identifiers, file paths, and exception names verbatim.

## Guardrails

- Never edit code, never rebuild, re-sign, flash, or reinstall anything on the device, and never modify the device's state beyond reading logs.
- Never claim a root cause the resolved evidence doesn't support — an unresolved/unsymbolicated frame is a reported limitation, not a guessed conclusion.
- Never propose a fix as code — name the concrete change; the owning agent (per `Owner` above) writes it.
- Never present this as a production-telemetry investigation, and never present an inferred app/package as confirmed without saying it was inferred.
- Always state `Not covered` — this is a single investigation on one connected device, not a certification.

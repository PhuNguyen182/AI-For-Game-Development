---
name: crash-anr-symbolication
description: >
  Confirms a crash/ANR stack trace or tombstone is fully symbolicated —
  resolved to readable function/file/line names instead of raw memory
  addresses — and that the uploaded debug symbols' build ID actually matches
  the crashing build, before any root-cause analysis is attempted on it. Use
  this immediately after `crash-anr-reporting-gate` passes, whenever a trace
  contains unresolved addresses/offsets, or whenever it's unclear if symbols
  were uploaded for that specific build. Do not use this on a trace that is
  already confirmed fully symbolicated — skip straight to
  `crash-anr-fault-domain-triage`.
---

# Crash/ANR Symbolication Check

## 1. Objective
This skill exists to stop root-cause analysis from running on a trace that is functionally unreadable. A stripped/unsymbolicated stack trace is just a list of memory offsets — any conclusion drawn from it is a guess dressed up as a finding. Getting symbolication right first is what makes the fault-domain triage in `crash-anr-fault-domain-triage` trustworthy.

## 2. Role
Act as a build/symbol-hygiene checkpoint. You are not analyzing what the crash means yet — only whether the trace in front of you is even in a state that can be analyzed.

## 3. When to invoke this skill
Consult this skill when:
- `crash-anr-reporting-gate` has just passed and a stack trace/tombstone is now in hand.
- A trace shows unresolved addresses, offsets, or `<unknown>`/`??` frames instead of function names and source locations.
- It's unclear whether debug symbols for the exact crashing build/version were ever uploaded to the reporting service (Play Console, Crashlytics, App Store Connect).
- Negative trigger: skip this and go directly to `crash-anr-fault-domain-triage` if the trace is already confirmed fully symbolicated (every frame resolves to a real function, file, and line).

## 4. How to use this skill
1. **Is the stack trace fully symbolicated?**
   - **Yes** → symbolication is done. Proceed straight to `crash-anr-fault-domain-triage`.
   - **No** → continue to step 2.
2. **Does the uploaded symbols' build/debug ID match the crashing build's ID?**
   - **Yes** → the right symbol file exists but wasn't associated with this crash — upload/re-associate the existing symbols to the reporting service for this build, then re-check the trace. Once resolved, proceed to `crash-anr-fault-domain-triage`.
   - **No** → the symbols on file are for a different build than the one that actually crashed. This cannot be resolved retroactively: the fix is a new build with symbol generation enabled and a symbol upload for that build (route this requirement to Unity Engineer / Tech Lead – C# Unity for the build/symbol-upload pipeline; you do not perform builds yourself). Once a new symboled build is available and a fresh matching crash report comes in, re-run step 1.
3. If, after these steps, a trace still cannot be symbolicated within the scope of this investigation (no build pipeline access, no new samples yet), say so explicitly in the Root Cause Report rather than guessing at a root cause from an unresolved trace — this matches the agent's own guardrail against speculating past what the data supports.

## 5. Specific goals / tasks this skill performs
- Confirm every frame in the trace resolves to a real function/file/line, not a raw address.
- When it doesn't, diagnose why: missing upload vs. build/symbol ID mismatch.
- Route the correct next action: upload existing symbols, or request a new symboled build.
- Out of scope: interpreting what the resolved trace means (that's `crash-anr-fault-domain-triage`) and performing builds or symbol uploads yourself.

## 6. Output format
```
## Symbolication Check — <RESOLVED / BLOCKED>
- Trace source: <Play Console / Crashlytics / App Store Connect>
- Fully symbolicated: <Yes / No>
- If No — symbol ID match: <Yes / No>
- Action taken/requested: <Upload existing symbols / Request new build + symbol upload / None needed>
- Next step: <Proceed to crash-anr-fault-domain-triage / Blocked pending new build>
```

## 7. Examples
**Example 1**
- Input: A Crashlytics report where every frame shows `0x00007fa3 <unknown>`.
- Output: Not symbolicated; symbol ID for the crashing build doesn't match any uploaded dSYM/mapping file → requested a new build with symbol upload from Unity Engineer, marked BLOCKED pending that build.

**Example 2**
- Input: A Play Console ANR report with unresolved native frames, but the correct `.so` symbol file exists in the project's build artifacts for that exact version code.
- Output: Symbol ID matches → uploaded/re-associated the existing symbols → trace now resolves → proceed to `crash-anr-fault-domain-triage`.

## 8. Edge cases & guardrails
- Never root-cause a partially symbolicated trace (some frames resolved, the crashing frame itself not) — treat a still-unresolved top frame the same as a fully unresolved trace for the purpose of this gate.
- Don't assume symbol IDs match just because version numbers look the same — build number and symbol/debug ID are the actual source of truth, not the marketing version string.
- This skill never edits code or triggers a build itself — it only diagnoses the symbolication gap and states what's needed to close it.
- If uploading/re-associating symbols is itself blocked by tooling access this agent doesn't have, state that explicitly and hand the concrete next action to the right owner instead of stalling silently.

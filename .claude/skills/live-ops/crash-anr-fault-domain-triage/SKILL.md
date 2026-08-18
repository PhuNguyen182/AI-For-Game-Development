---
name: crash-anr-fault-domain-triage
description: >
  Walks a fully symbolicated crash/ANR stack trace through the fault-domain
  decision tree — game code, Unity engine code, third-party SDK, or
  system/OS library — to pinpoint root cause and the correct fix action and
  owner, ending in a Root Cause Report. Use this once `crash-anr-symbolication`
  has confirmed the trace is readable, whenever crash-anr-investigator needs
  to determine where a crash or ANR actually originates and who should own
  the fix. Do not use this on an unsymbolicated trace — resolve
  `crash-anr-symbolication` first; a fault domain read off unresolved
  addresses is a guess, not a finding.
---

# Crash/ANR Fault-Domain Triage

## 1. Objective
This skill exists to turn a readable stack trace into an actionable, correctly-owned fix — by walking the same fault domain outward from "our code" to "outside our control" every time, so root-causing stays systematic instead of guessed from whichever frame looks suspicious first.

## 2. Role
Act as the actual investigative reasoning step: given a resolved trace, determine which layer of the stack is truly responsible, and hand off to the one engineer/role actually positioned to act on that layer.

## 3. When to invoke this skill
Consult this skill when:
- `crash-anr-symbolication` has confirmed the trace fully resolves to function/file/line names.
- crash-anr-investigator needs to determine the root cause layer (game code, Unity engine, third-party SDK, or system library) and the right owner to route a fix to.
- Negative trigger: do not use this on a trace still showing unresolved frames — send it back through `crash-anr-symbolication` first.

## 4. How to use this skill
Walk the checks below **in this exact order**, stopping at the first "Yes":

### Step 1 — Game code
Is the ANR/crash happening in game code (`Game.Core.*` / `Game.Client.*`, i.e. code this project's own engineers wrote)?
- **Yes** → check the C# code at the faulting frame(s).
  - **Is it fixable?**
    - **Yes** → root cause identified. Recommend the concrete fix, route it to C# Software Engineer (if the fault is in `Game.Core.*`) or Unity Engineer (if in `Game.Client.*`); note that after the fix ships, a new build with symbols must be uploaded and re-verified via `crash-anr-symbolication` before closing the issue.
    - **No** (not directly fixable — e.g. the crash is a defensive last resort against an unpreventable OS-level condition) → recommend a mitigation instead of a code fix: use `StrictMode` (Android — catches accidental disk/network access on the main thread before it causes an ANR) or `ApplicationExitInfo` (Android 11+ — captures the actual exit reason for further diagnosis on the next occurrence). Route to Tech Lead – Performance for the mitigation design.
  - Stop here — do not continue to the checks below.
- **No** → continue to Step 2.

### Step 2 — Unity engine code
Is it happening inside Unity's own engine/runtime code (not this project's game code)?
- **Yes** → check Unity's forums/issue tracker for a known, matching issue.
  - If a fix exists → upgrade the Unity version (patch/LTS bump) that contains it.
  - If no fix exists yet → report a bug to Unity with the symbolicated trace and a minimal repro.
  - Route to Tech Lead – C# Unity either way (they own the Unity version/upgrade decision).
  - Stop here.
- **No** → continue to Step 3.

### Step 3 — Third-party SDK
Is it happening inside a third-party SDK (ad mediation, analytics, IAP, or any other integrated SDK)?
- **Yes** → work down this list until resolved or exhausted:
  1. Update the SDK to its latest version.
  2. If still unresolved, disable the SDK temporarily to confirm/mitigate impact.
  3. Check the Google Play SDK Index for known issues on that SDK/version.
  4. Contact the SDK's developer/support with the findings.
  - Route to Tech Lead – SDK/Platform (owner of all third-party SDK integration).
  - Stop here.
- **No** → continue to Step 4.

### Step 4 — System/OS library
Is it happening inside a system/OS library (neither this project's code, Unity's runtime, nor a third-party SDK)?
- **Yes** → does it only affect certain devices or OS versions?
  - **Yes** → segment supported devices (exclude the affected device/OS combination via the store's device catalog or a minimum OS/device requirement), then contact the platform developer (Google/OEM/Apple) with the report.
  - **No** (affects broadly, not tied to a specific device/OS segment) → contact the platform developer (Google/OEM/Apple) directly.
  - Route to Tech Lead – SDK/Platform (store/platform policy and device segmentation owner) either way.
  - Stop here.
- **No** → none of the four domains match. Mark the finding **Non-actionable**: state explicitly that the trace doesn't map to an identifiable, ownable fault domain, and note it as such in the Root Cause Report rather than forcing a guess into one of the four buckets above.

## 5. Specific goals / tasks this skill performs
- Determine the single fault domain responsible for a given crash/ANR, checked in a fixed, repeatable order (game code → Unity engine → third-party SDK → system library → non-actionable).
- For each domain, produce the specific next action from the decision tree (fix, mitigation, upgrade, bug report, SDK update/disable, device segmentation, or developer contact).
- Route the finding to exactly one correctly-scoped owner.
- Out of scope: writing or editing the actual fix (the receiving engineer does that); re-litigating symbolication (already handled upstream).

## 6. Output format
Feed the result into the agent's standard Root Cause Report:
```
## Root Cause Report — <crash/ANR signature>
- Source: Play Console / Crashlytics / App Store Connect
- Fault domain: Game code / Unity engine code / Third-party SDK / System library / Non-actionable
- Root cause: ...
- Recommended action: ...
- Severity/frequency: ...
- Routed to: <C# Software Engineer / Unity Engineer / Tech Lead – Performance / Tech Lead – C# Unity / Tech Lead – SDK-Platform / none (non-actionable)>
```

## 7. Examples
**Example 1**
- Input: A symbolicated native crash trace whose top frames are entirely inside a third-party ad SDK's native library, reproducible across builds.
- Output: Fault domain = Third-party SDK; SDK already on latest version; disabling it confirms the crash disappears; Google Play SDK Index shows a known issue for that version; routed to Tech Lead – SDK/Platform with a recommendation to contact the SDK vendor.

**Example 2**
- Input: A symbolicated ANR trace showing the main thread blocked inside a synchronous OS `Binder` call, occurring only on a specific OEM's Android 9 devices.
- Output: Fault domain = System library, device/OS-specific; recommended segmenting out that device/OS combination via the Play Console device catalog and contacting the OEM; routed to Tech Lead – SDK/Platform.

## 8. Edge cases & guardrails
- Always check in the fixed order above (game code first, system library last) — don't jump to whichever frame looks most suspicious; the order exists specifically so an actually-fixable game-code bug isn't mistakenly blamed on the OS.
- If a trace has frames spanning more than one domain (e.g. game code calling into a third-party SDK that then crashes), root-cause at the frame that actually faulted, not the frame closest to the game's own call site — attribute to the domain that owns the faulting code.
- Never edit code yourself — this skill only produces the diagnosis and the routed recommendation; the receiving engineer implements it and it re-enters the pipeline through Code Reviewer.
- "Non-actionable" is a legitimate, explicit outcome — don't force a low-confidence guess into one of the four domains just to avoid it.
- Any claim that something is "fixable" or "not fixable" must be grounded in what the resolved trace and code actually show — if genuinely uncertain, say so and request more samples rather than asserting a fixability verdict without support.

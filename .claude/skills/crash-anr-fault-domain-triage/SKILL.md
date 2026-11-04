---
name: crash-anr-fault-domain-triage
description: "Crash/ANR fault domain: game, engine, SDK or system library; routes the fix. Use as stage 3 of a crash investigation."
user-invocable: false
---

# Crash and ANR Fault-Domain Triage

- **Not for:** confirming the report source (`crash-anr-reporting-gate`).
- **Not for:** resolving addresses (`crash-anr-symbolication`).
- **Not for:** writing the fix (`csharp-engineer`, `gameplay-engineer`, `sdk-platform-engineer`).
- **Not for:** pre-release defects (`qa-automation-engineer`, `build-fault-triage`).
- **Docs:** https://developer.android.com/topic/performance/vitals (vitals, `/anr`), https://developer.android.com/distribute/sdk-index
  - **Unity:** https://issuetracker.unity3d.com/, https://docs.unity3d.com/Manual/IL2CPP.html.
  - **Apple:** https://developer.apple.com/documentation/xcode/diagnosing-issues-using-crash-reports-and-device-logs.
  - **Versioning:** unversioned platform pages.
  - **Thresholds:** vitals thresholds and ANR timeouts are revised by Google, so read the console, not a number written here.

## References
- **[fault-domain-signals.md](references/fault-domain-signals.md):** Reading a resolved trace, or two domains both look plausible.
- **[anr-classes-and-mitigation.md](references/anr-classes-and-mitigation.md):** The signal is an ANR, or no code fix exists.
- **[third-party-and-engine-escalation.md](references/third-party-and-engine-escalation.md):** The faulting frame is in an SDK or the engine.

## Steps
1. **Frame unresolved at the top of the stack → return to `crash-anr-symbolication`:** a domain read off offsets is a guess.
   - **One sample only:** request more before assigning an owner.
2. **Walk the domains in fixed order, stop at the first match:** game code, Unity engine, third-party SDK, system library. Per [fault-domain-signals.md](references/fault-domain-signals.md).
3. **Attribute to the frame that faulted, not the one nearest your code:**
   - **Game code into an SDK that faults:** SDK.
   - **SDK calling back into game code that faults:** game code.
4. **Game code:** per [anr-classes-and-mitigation.md](references/anr-classes-and-mitigation.md).
   - **Defect:** a null dereference or self-caused main-thread block is a fix, routed to `csharp-engineer` (Shared Core) or `gameplay-engineer` (client).
   - **Condition the game cannot prevent:** a mitigation, designed with `gameplay-engineer`.
5. **Unity engine:** per [third-party-and-engine-escalation.md](references/third-party-and-engine-escalation.md).
   - **Ladder:** forums and issue tracker, then upgrade to the fixed version, then a bug report only if neither yields one.
   - **Every rung:** goes to `cto` for the version decision (an upgrade is project-wide).
6. **Third-party SDK:** per [third-party-and-engine-escalation.md](references/third-party-and-engine-escalation.md).
   - **Ladder:** update to current, disable to confirm the signal disappears, check the SDK index, then contact the vendor with all three results.
   - **Route:** `sdk-platform-engineer`.
7. **System library:** per [anr-classes-and-mitigation.md](references/anr-classes-and-mitigation.md).
   - **Device- or OS-segmented:** segmentation plus vendor report.
   - **Broad:** vendor report alone.
   - **Route:** both to `sdk-platform-engineer`.
8. **Record "non-actionable" when no ownable domain fits:** it is a finding that more samples are needed, not a miss.
9. **A fix is verified by a lower rate from a new symbolicated build:** re-entering at `crash-anr-symbolication`.
   - **Why:** a merged patch confirms nothing about the installed base.

## Never
- **Suspicious-looking frame first:** start from the most suspicious-looking frame — that instinct blames the OS for the game's own defect.
- **Unsupported claim:** assert fixable or not fixable without the trace and code to support it.
- **Disabling an SDK as a fix:** it is confirmation plus temporary mitigation; shipping without it is `sdk-platform-engineer`'s decision.
- **Device segmentation as a resolution:** it removes the reporters, not the fault.
- **Code edits:** edit code from this skill; the receiving engineer's change goes through `code-reviewer`.

## Output
```
## Root Cause Report — <crash or ANR signature>
- Source: <Play Console vitals / Crashlytics / App Store Connect>
- Signal type: <crash / ANR — timeout class if known>
- Faulting frame: <function, file, line>
- Fault domain: <game code / Unity engine / third-party SDK / system library / non-actionable>
- Why this domain and not the adjacent one: <the frame that decided it>
- Root cause: <what goes wrong>
- Severity and frequency: <rate, versions, device or OS concentration>
- Decision: <fix / mitigation / engine upgrade / SDK action / segmentation / non-actionable>
- Recommended action: <concrete next step>
- Verification: re-enter at crash-anr-symbolication once a new symbolicated build ships
- Routed to: <csharp-engineer / gameplay-engineer / cto / sdk-platform-engineer / none>
```

## Example
- **"Top frame is an engine function, so file a Unity bug":** declined.
  - **Why:** the frame below passes a collection the game already disposed.
  - **Did instead:** the defect is game code, a same-week fix; routed to `gameplay-engineer`.

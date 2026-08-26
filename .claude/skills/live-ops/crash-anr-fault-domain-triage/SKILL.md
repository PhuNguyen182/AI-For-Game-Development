---
name: crash-anr-fault-domain-triage
description: >
  Decision tree that attributes a fully symbolicated crash or ANR to exactly
  one fault domain — game code, Unity engine, third-party SDK, or system
  library — walked in that fixed order, then routes the fix to a single owner
  as a Root Cause Report. Covers ANR timeout classes, `ApplicationExitInfo`,
  `StrictMode`, the Google Play SDK Index, and device or OS segmentation. Use
  once the trace is confirmed readable. Not for: confirming the report source
  (`crash-anr-reporting-gate`); resolving addresses
  (`crash-anr-symbolication`); writing the fix (`csharp-engineer`,
  `unity-engineer`, `tech-lead-sdk-platform`); pre-release defects
  (`qa-automation-engineer`).
---

# Crash and ANR Fault-Domain Triage — which layer is actually responsible

## Bundled resources

### References
Read-only context, loaded on demand so SKILL.md itself stays short.

| File | Contents | Read when |
|---|---|---|
| [root-links.md](references/root-links.md) | Platform, engine and store documentation roots, and what this skill does not pin | Starting a triage, or a vendor page has moved |
| [fault-domain-signals.md](references/fault-domain-signals.md) | What each domain looks like in a resolved trace, and how mixed-domain stacks are attributed | Reading a trace, or two domains both look plausible |
| [anr-classes-and-mitigation.md](references/anr-classes-and-mitigation.md) | ANR timeout classes, the common Unity causes, `StrictMode`, `ApplicationExitInfo`, segmentation | The signal is an ANR rather than a crash, or no code fix exists |
| [third-party-and-engine-escalation.md](references/third-party-and-engine-escalation.md) | The SDK escalation ladder, the Play SDK Index, and the engine bug path | The fault sits outside code this project writes |

## 1. Objective
Turn a readable trace into one owned action. The order the domains are checked in is the whole point: checked outward from code this project controls, an actually fixable game-code defect cannot be misattributed to the operating system, which is the failure that turns a two-hour fix into a vendor ticket nobody answers. The second failure it prevents is the plausible guess — a domain assigned from whichever frame looked suspicious, routed confidently to an owner with no way to act on it.

## 2. Role
Act as the investigative reasoning step of the crash pipeline, on behalf of `crash-anr-investigator`. Given a resolved trace, you decide which layer is responsible and hand the finding to the one role positioned to act on that layer. You never write the fix.

## 3. When to invoke this skill
- `crash-anr-symbolication` has confirmed the trace resolves, including its faulting frame.
- A root cause and an owner must be established for a production crash or ANR.
- The signal is an ANR and it is unclear whether the block is the game's own work, the engine's, an SDK's, or the platform's.
- A trace spans several domains and the attribution is contested.
- Negative trigger: any unresolved frame at the top of the stack — send it back to `crash-anr-symbolication`, because a domain read off offsets is a guess.
- Negative trigger: whether the report is production telemetry at all — that was `crash-anr-reporting-gate`.
- Negative trigger: implementing the fix, the mitigation, the engine upgrade, or the SDK update — those belong to `csharp-engineer`, `unity-engineer`, `tech-lead-csharp-unity`, `tech-lead-performance` and `tech-lead-sdk-platform` respectively; this skill produces the diagnosis and the routing.
- Negative trigger: a defect found before release — that is `qa-automation-engineer` and `playtest-tester`, a different pipeline entirely.

## 4. How to use this skill
1. **Walk the domains in the fixed order and stop at the first match** — game code, then Unity engine, then third-party SDK, then system library, per [fault-domain-signals.md](references/fault-domain-signals.md) and the roots in [root-links.md](references/root-links.md). The order exists so a fixable defect in code this project owns is never blamed on a layer nobody here can change.
2. **Attribute to the frame that faulted, not the frame nearest your own code** — a stack that runs from game code into an SDK that then crashes belongs to the SDK, and the reverse is equally true, per [fault-domain-signals.md](references/fault-domain-signals.md). The call site is context; the faulting frame is the finding.
3. **In game code, separate a fixable defect from a condition only mitigation reaches** — a null dereference or a main-thread block the game itself causes is a fix, routed to `csharp-engineer` for Shared Core or `unity-engineer` for client code. A defensive failure against an unpreventable platform condition is a mitigation instead, designed with `tech-lead-performance`, per [anr-classes-and-mitigation.md](references/anr-classes-and-mitigation.md).
4. **In Unity engine code, work down the ladder rather than jumping to a bug report** — search the forums and the issue tracker, then upgrade to the version carrying the fix, and file a report only once neither rung produces one, per [third-party-and-engine-escalation.md](references/third-party-and-engine-escalation.md). Route the version decision to `tech-lead-csharp-unity` at every rung, since an engine upgrade is never a local change.
5. **In a third-party SDK, update and isolate before contacting the vendor** — update to current, disable it to confirm the signal disappears, then check the store's SDK index for a known issue, and only then approach the vendor with all three results, per [third-party-and-engine-escalation.md](references/third-party-and-engine-escalation.md). Route to `tech-lead-sdk-platform`, who owns every SDK integration.
6. **In a system library, establish whether it is segmented by device or broad** — a fault confined to one manufacturer or OS version is a segmentation decision plus a vendor report, while a broad one is a vendor report alone, per [anr-classes-and-mitigation.md](references/anr-classes-and-mitigation.md). Route both to `tech-lead-sdk-platform`, who owns store policy and the device catalogue.
7. **Record non-actionable as a real outcome rather than forcing a fourth guess** — a trace that maps to no ownable domain is a finding, stated as one. Forcing it into a bucket sends work to someone who will return it, and hides that more samples are what is actually needed.
8. **Send the fix back through the pipeline rather than closing on a shipped build** — a fix is verified when a new build with symbols reports a reduced rate for that signature, which means re-entering at `crash-anr-symbolication`. Closing an issue because a patch merged confirms nothing about the installed base.

## 5. Specific goals / tasks this skill performs
- Attributing a resolved crash or ANR to exactly one fault domain, checked in a fixed, repeatable order.
- Resolving a mixed-domain stack to the frame that actually faulted.
- Distinguishing a fixable game-code defect from a condition only mitigation reaches.
- Producing the domain-specific next action: fix, mitigation, engine upgrade or bug report, SDK update or vendor contact, device segmentation.
- Routing the finding to exactly one correctly scoped owner, as a Root Cause Report.
- Out of scope: writing the fix (`csharp-engineer`, `unity-engineer`); designing the mitigation's implementation (`tech-lead-performance`); the engine version decision (`tech-lead-csharp-unity`); SDK and store action (`tech-lead-sdk-platform`); symbolication (`crash-anr-symbolication`); pre-release defects (`qa-automation-engineer`).

## 6. Output format
```
## Root Cause Report — <crash or ANR signature>
- Source: <Play Console vitals / Crashlytics / App Store Connect>
- Signal type: <crash / ANR — timeout class if known>
- Faulting frame: <function, file, line>
- Fault domain: <game code / Unity engine / third-party SDK / system library / non-actionable>
- Why this domain and not the adjacent one: <the frame that decided it>
- Root cause: <what actually goes wrong>
- Severity and frequency: <rate, affected versions, device or OS concentration>
- Decision: <fix / mitigation / engine upgrade / SDK action / segmentation / non-actionable>
- Recommended action: <the concrete next step, not a description of the problem>
- Verification: re-enter at crash-anr-symbolication once a new symboled build ships
- Routed to: <csharp-engineer / unity-engineer / tech-lead-performance / tech-lead-csharp-unity / tech-lead-sdk-platform / none>
```

**Extended report — emit ONLY when the requester asks for it.** It adds all three fields below the decision:
```
- Known limitations: <what the samples do not establish — for example a single device model, or one OS version>
- Latent concerns: <failure modes not yet triggered: an adjacent signature likely sharing the cause, a vendor dependency with no timeline, a mitigation that trades one failure for another>
- Future remediation: <the concrete fix for each concern above, each with the condition that should trigger it>
```

## 7. Examples
**Example 1**
- Input: a resolved native crash whose top frames sit entirely inside an advertising SDK's library, reproducible across builds.
- Output: third-party SDK. Updated to current and the signature persisted; disabling the SDK removed it, which confirms the attribution rather than merely correlating with it; the store's SDK index lists a known issue for that version. Routed to `tech-lead-sdk-platform` with all three results and a recommendation to contact the vendor, since the fix is not available in a released version.

**Example 2**
- Input: a resolved ANR with the main thread blocked in a synchronous platform call, appearing only on one manufacturer's devices on one OS version.
- Output: system library, device-segmented. Recommended excluding that device and OS combination through the store's device catalogue while the platform vendor is contacted, and routed both to `tech-lead-sdk-platform`. Noted that segmentation removes the reported rate without removing the fault, so the vendor thread stays open.

**Example 3**
- Input: "The top frame is an engine function, so this is a Unity bug — file it."
- Output: declined as premature. The engine frame faulted, but the domain order requires checking game code first, and the frame below it passes a collection the game had already disposed. The engine crashed on input it was given, so the defect is in game code and fixing it is a same-week change rather than a version bump. Routed to `unity-engineer`.

**Example 4**
- Input: a resolved ANR the game cannot prevent — the platform reclaiming resources under memory pressure during a long load.
- Output: game code, not fixable as a defect. Recommended mitigation instead: a main-thread policy check to catch accidental blocking work before it produces an ANR, and reading the recorded exit reason on the next launch to confirm the cause rather than inferring it. Routed to `tech-lead-performance` for the mitigation design, per [anr-classes-and-mitigation.md](references/anr-classes-and-mitigation.md).

## 8. Edge cases & guardrails
- Never start from the most suspicious-looking frame — the fixed order exists precisely because that instinct blames the operating system for the game's own defect.
- Never attribute a mixed-domain stack to the call site — the faulting frame owns the finding, whichever direction the call ran.
- Never assign a domain from a trace whose faulting frame is unresolved — return it to `crash-anr-symbolication`.
- Never assert that something is or is not fixable without the trace and the code supporting it — request more samples instead of producing a verdict the data does not carry.
- Never force a low-confidence trace into a domain to avoid recording non-actionable — that outcome is legitimate and more useful than a misrouted ticket.
- Never treat disabling an SDK as a fix — it is a confirmation step and a temporary mitigation, and the decision to ship without it belongs to `tech-lead-sdk-platform`.
- Never treat device segmentation as a resolution — it removes the population reporting the fault, not the fault.
- Never edit code from this skill — it produces the diagnosis and the routing, and the receiving engineer's change re-enters through `code-reviewer`.
- Never close a signature because a fix merged — verification is a reduced rate from a new symboled build, which re-enters at `crash-anr-symbolication`.

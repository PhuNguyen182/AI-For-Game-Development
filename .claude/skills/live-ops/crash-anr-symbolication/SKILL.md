---
name: crash-anr-symbolication
description: >
  Gate that confirms a crash or ANR trace is fully symbolicated — every frame
  resolved to a function, file and line rather than a raw address — and that
  the uploaded symbols' build ID matches the build that actually crashed.
  Covers Android native debug symbols and the R8 mapping file, iOS dSYM
  bundles, and IL2CPP frames on a Unity title. Use immediately after the
  reporting gate passes, or whenever a trace shows unresolved offsets. Not
  for: confirming the report source (`crash-anr-reporting-gate`); attributing
  the fault (`crash-anr-fault-domain-triage`); producing the build or wiring
  the upload (`build-run-engineer`, `tech-lead-sdk-platform`); Editor stack
  traces (`qa-automation-engineer`).
---

# Crash and ANR Symbolication — is this trace readable at all

## Bundled resources

### References
Read-only context, loaded on demand so SKILL.md itself stays short.

| File | Contents | Read when |
|---|---|---|
| [root-links.md](references/root-links.md) | Platform and service documentation roots, and what this skill deliberately does not pin | Starting a check, or a vendor page has moved |
| [symbol-artefacts-by-platform.md](references/symbol-artefacts-by-platform.md) | Which artefact resolves which frames on Android, iOS and IL2CPP, and how build identity is established | Deciding what is missing, or whether the symbols on file belong to this build |

## 1. Objective
Stop fault attribution from running on a trace that is functionally unreadable. A stripped trace is a list of offsets, and a conclusion drawn from one is a guess in an engineering format — which is worse than no conclusion, because it routes work to the wrong owner. The subtler failure this catches is the partially resolved trace: most frames readable, the faulting frame not, which reads as a usable report right up to the point it names the wrong domain.

## 2. Role
Act as the build and symbol hygiene checkpoint of the crash pipeline, on behalf of `crash-anr-investigator`. You do not yet ask what the crash means — only whether the trace in front of you is in a state where that question can be answered.

## 3. When to invoke this skill
- `crash-anr-reporting-gate` has passed and a trace or tombstone is now in hand.
- A trace shows raw addresses, offsets, or unknown frames where function names should be.
- Some frames resolve and others do not, particularly around the top of the stack.
- It is unclear whether symbols for the exact crashing build were ever uploaded.
- A Unity title's trace mixes managed and native frames and only one kind resolves.
- Negative trigger: the trace already resolves completely, including the faulting frame — go to `crash-anr-fault-domain-triage` rather than re-checking.
- Negative trigger: whether the report is a production signal at all — that was `crash-anr-reporting-gate`, and this skill assumes it passed.
- Negative trigger: deciding which layer is at fault — that is `crash-anr-fault-domain-triage`; reading meaning into a trace here is exactly what this gate exists to defer.
- Negative trigger: producing a build, or configuring the symbol upload step — those are `build-run-engineer` and `tech-lead-sdk-platform`; this skill states what is needed and routes it.
- Negative trigger: an Editor or development-build stack trace, which resolves on its own because nothing stripped it — that is `qa-automation-engineer`'s pipeline, and there is no symbolication question to answer.

## 4. How to use this skill
1. **Check the faulting frame before counting resolved frames** — a trace can be mostly readable and still useless, because the frame that actually crashed is the one that decides the fault domain. Treat an unresolved top frame exactly as you would treat a fully unresolved trace.
2. **Compare build and symbol identifiers rather than version strings** — the marketing version can match across builds that share no binary, per [symbol-artefacts-by-platform.md](references/symbol-artefacts-by-platform.md) and the roots in [root-links.md](references/root-links.md). Identity is the build identifier the platform records, not the number shown to players.
3. **Name which artefact is missing for the platform in hand** — native debug symbols, the obfuscation mapping file, or a dSYM bundle resolve different frames, and "symbols are missing" without naming which one produces an unactionable request, per [symbol-artefacts-by-platform.md](references/symbol-artefacts-by-platform.md).
4. **Treat managed and native frames as separate problems on a Unity title** — an IL2CPP build turns C# into native code, so a managed frame and an engine frame can require different artefacts and fail independently. One resolving is not evidence about the other.
5. **Re-associate the existing symbols when the identifiers match** — the artefact exists and was simply never attached to this build in the service; upload it, then re-check the trace from step 1 rather than assuming the association worked.
6. **Request a new build with symbol generation when the identifiers do not match** — this cannot be fixed retroactively, because the binary that crashed has no symbols anywhere. Route the build to `build-run-engineer` and the upload step to `tech-lead-sdk-platform`, and wait for a fresh matching report.
7. **Report an unresolvable trace as a limit rather than reasoning past it** — if no new build is available and no other sample resolves, say so explicitly in the handoff. An honest block is a finding; a domain guessed from offsets is not, and it sends work to an owner who cannot act on it.

## 5. Specific goals / tasks this skill performs
- Confirming every frame, and specifically the faulting frame, resolves to a function, file and line.
- Diagnosing why a trace does not resolve: a missing upload against a build identity mismatch.
- Naming the specific artefact required for the platform and build type in hand.
- Separating managed from native symbolication on an IL2CPP title.
- Routing the next action: attach existing symbols, or request a new symboled build.
- Out of scope: confirming the report's source (`crash-anr-reporting-gate`); attributing the fault (`crash-anr-fault-domain-triage`); producing builds (`build-run-engineer`); wiring the upload pipeline (`tech-lead-sdk-platform`); Editor stack traces (`qa-automation-engineer`).

## 6. Output format
```
## Symbolication Check — <RESOLVED / BLOCKED>
- Trace source: <Play Console vitals / Crashlytics / App Store Connect>
- Faulting frame resolves: <yes / no>
- Other frames: <all resolve / partial — which layers>
- Build identity matched against symbols: <yes / no / unknown>
- Artefact involved: <native debug symbols / obfuscation mapping / dSYM / IL2CPP managed frames>
- Decision: <proceed / block>
- Action requested: <attach existing symbols / new build with symbol generation and upload / none needed>
- Routed to: <crash-anr-fault-domain-triage / build-run-engineer / tech-lead-sdk-platform>
```

**Extended report — emit ONLY when the requester asks for it.** It adds all three fields below the decision:
```
- Known limitations: <what remains unresolved — for example native frames readable while managed frames are not>
- Latent concerns: <failure modes not yet triggered: symbol upload absent from the build pipeline, retention about to drop the samples, one platform unverified>
- Future remediation: <the concrete fix for each concern above, each with the condition that should trigger it>
```

## 7. Examples
**Example 1**
- Input: a Crashlytics report in which every frame is a bare hexadecimal address.
- Output: BLOCKED. No symbols on file share a build identifier with the crashing binary, so the trace cannot be resolved retroactively at all. Requested a new build with symbol generation enabled from `build-run-engineer` and the upload step from `tech-lead-sdk-platform`, and stated plainly that no domain can be named until a fresh matching report arrives.

**Example 2**
- Input: an ANR report whose native frames are unresolved, while the correct symbol artefact exists in the build output for that exact build.
- Output: identifiers matched, so the artefact was simply never attached in the service. Attached it, re-checked from the top, confirmed the faulting frame now names a function, and proceeded to `crash-anr-fault-domain-triage`.

**Example 3**
- Input: "Most of the stack is readable, just root-cause it from the frames we can see."
- Output: declined — the unresolved frames are the top of the stack, which is where the fault domain is decided, so the readable remainder describes how the code got there rather than what went wrong. Reading a domain off the highest resolved frame would have attributed an engine or SDK fault to the game code that called into it. Held the gate and requested the missing artefact.

## 8. Edge cases & guardrails
- Never attribute a fault from a partially symbolicated trace when the faulting frame is one of the unresolved ones — that is the frame the whole decision rests on.
- Never accept matching version strings as matching builds — the recorded build identifier is the only identity that means anything.
- Never say "symbols are missing" without naming the artefact and the platform — the request cannot be acted on otherwise.
- Never assume that resolving native frames also resolved managed ones on an IL2CPP title, or the reverse.
- Never treat an attached artefact as a resolved trace — re-read the trace and confirm, since attaching the wrong file succeeds quietly.
- Never build, upload, or edit anything from this skill — it diagnoses the gap and routes it to `build-run-engineer` and `tech-lead-sdk-platform`.
- Never let a block stall silently — if the tooling access needed to attach symbols sits outside this pipeline, state that and name who has it.
- If a signature's samples are old enough that the service's retention may have dropped their detail, say so rather than waiting on traces that will not arrive, per `crash-anr-reporting-gate`.

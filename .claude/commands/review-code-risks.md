---
description: Static review of C#/Unity code for runtime performance, memory efficiency, and hidden crash/ANR risk — concise report, fix direction only, never edits code
argument-hint: "[file-or-directory-path...]"
allowed-tools: Read, Grep, Glob, Bash, Skill
---

# Review code for performance, memory, and hidden crash/ANR risk

`$ARGUMENTS`: optional paths; else scope from the current git diff (below). Both empty → ask, never guess. Static-analysis risk sweep, additive to — not a replacement for — `code-reviewer` (full correctness), `performance-qa-engineer`/`tech-lead-performance` (measured verdict), `/investigate-device-crash`/`crash-anr-investigator` (confirmed fault), `build-verification-tester`/`build-fault-triage` (confirmed build fault); name matching findings as risks to verify there, never as confirmed. Reason in English; final report to the user is in Vietnamese, concise, code verbatim.

**1 — Scope**: `$ARGUMENTS` paths (`.cs` only), else union of `git diff --name-only HEAD -- '*.cs'` + staged. Both empty → ask; never scan the whole repo silently.

**2 — Scan against three criteria** (a grep match is a candidate, not automatic — confirm it's in a hot path / a real boundary crossing first; cite the clause when reporting):
- Performance (`performance-and-algorithms.md`): `new`/string concat/LINQ in Update-family methods; uncached per-frame `GetComponent`; `Find`/`FindObjectOfType(s)` at runtime; pool-less hot-path `Instantiate`/`Destroy`; `Distance`/`Sqrt` for a threshold compare instead of `sqrMagnitude`; `SendMessage`/`BroadcastMessage`/string `Invoke`; uncached `new WaitForSeconds` in a coroutine loop; repeated uncached `transform.` reads; string-overload `Animator.Set*` instead of `StringToHash`; boxed `foreach` over `IEnumerable<T>`/LINQ in a hot path; empty Update-family/`OnGUI`/collision-callback bodies; unbounded nested loops over a count-scaling collection.
- Memory (same file): `+=` with no matching `-=` in `OnDisable`/`OnDestroy`; uncleared `StartCoroutine`; a static/singleton field holding a MonoBehaviour/scene object/large collection; an only-growing collection with no cap/pool/clear point; a long-lived lambda capturing `this`/a large collection; high-frequency `Instantiate`/`Destroy` with no `ObjectPool<T>`.
- Crash/ANR risk (`coding-principles.md` Null safety/Exception handling): an unguarded Inspector field or `GetComponent`/`Instantiate` result; a `UnityEngine.Object` reference dereferenced across frames without `if (this.x)` (fake-null); `catch (Exception)`/empty catch swallowing an error — especially around signature/token verification or a payment callback; sync disk/network I/O or a large sync load on the main thread (cite the row in `crash-anr-fault-domain-triage/references/anr-classes-and-mitigation.md`, read directly, don't invoke the skill); a lock/blocking wait across a long main-thread op; reflection/`Activator.CreateInstance`/generic virtual call reachable only via serialization — point to `build-fault-triage`.

**3 — Classify what matters**: drop a match not in a hot path, not a real boundary crossing, or already guarded nearby. Name the fault domain/cause class from the reference table, not "could crash". Severity needing a runtime number → say so and route to `performance-qa-engineer`/`/investigate-device-crash`, never imply it was measured.

**4 — Report**, one line per field, no filler, five `defect-reporting.md` elements, a Severity, a fix direction naming the change without writing it:
```
## Code Risk Review — <scope>
- Status: Done | Blocked  |  Files reviewed: <count/paths or diff range>
### Findings
- Category: Performance | Memory | Crash/ANR risk
- Location: <path:line-range>  |  Expected: <clause>  |  Actual: <one line>
- Evidence: <quoted line(s)>  |  Severity: Critical|High|Medium|Low
- Fix direction: <one line, no diff>  |  Owner: <agent-id>
- Confidence: Static signal only — not measured, not reproduced on device
- Not covered: <paths skipped, anything needing measurement or a real device>
```
Most severe first; clean sweep → report plainly, don't invent a finding. Translate to Vietnamese for the user, code/paths/lines verbatim.

**Guardrails**: never edit code; never claim a confirmed regression/crash from a static read; never widen into full correctness/security review (route instead); never invoke the gated crash-anr skills directly (read their reference files); always state `Not covered`.

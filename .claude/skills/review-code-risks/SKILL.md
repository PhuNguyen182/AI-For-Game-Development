---
name: review-code-risks
description: Static review of C#/Unity code for runtime performance, memory and hidden crash/ANR risk — report with fix direction only, never edits code
argument-hint: "[file-or-directory-path...]"
allowed-tools: PowerShell, Read, Grep, Glob, Bash, Skill
---

# Review code for performance, memory, and hidden crash/ANR risk

`$ARGUMENTS`: optional paths. Additive to `code-reviewer` (correctness), `performance-qa-engineer` (measured verdict), `/investigate-device-crash` (confirmed fault), `build-fault-triage` (confirmed build fault): name matches as risks to verify there, never as confirmed. Final report to the GD in Vietnamese, code verbatim.

1. **Scope** — `$ARGUMENTS` paths (`.cs` only), else `git diff --name-only HEAD -- '*.cs'` plus staged. Both empty → ask; never scan the whole repo.
2. **Scan** — a grep hit is a candidate: confirm hot path or real boundary crossing first, cite the clause.
   - Performance (`csharp-standards` → `references/performance-and-algorithms.md`): `new`/string concat/LINQ in Update-family methods; uncached per-frame `GetComponent`; runtime `Find`/`FindObjectOfType(s)`; hot-path `Instantiate`/`Destroy` without a pool; `Distance`/`Sqrt` for a threshold instead of `sqrMagnitude`; `SendMessage`/`BroadcastMessage`/string `Invoke`; uncached `new WaitForSeconds` in a coroutine loop; repeated uncached `transform.` reads; string-overload `Animator.Set*` instead of `StringToHash`; boxed `foreach` over `IEnumerable<T>`/LINQ in a hot path; empty Update-family/`OnGUI`/collision callbacks; unbounded nested loops over a count-scaling collection.
   - Memory (same file): `+=` without `-=` in `OnDisable`/`OnDestroy`; uncleared `StartCoroutine`; static/singleton field holding a MonoBehaviour, scene object or large collection; only-growing collection with no cap/pool/clear point; long-lived lambda capturing `this` or a large collection; high-frequency `Instantiate`/`Destroy` with no `ObjectPool<T>`.
   - Crash/ANR (`csharp-standards` → `references/coding-principles.md` Null safety / Exception handling): unguarded Inspector field or `GetComponent`/`Instantiate` result; `UnityEngine.Object` dereferenced across frames without `if (this.x)` (fake-null); `catch (Exception)`/empty catch, especially around signature/token verification or a payment callback; sync disk/network I/O or large sync load on the main thread (cite the row in `.claude/skills/crash-anr-fault-domain-triage/references/anr-classes-and-mitigation.md`, read directly, do not invoke that skill); lock/blocking wait across a long main-thread op; reflection/`Activator.CreateInstance`/generic virtual call reachable only via serialization → point to `build-fault-triage`.
3. **Filter** — drop a match that is not hot, not a real boundary crossing, or guarded nearby. Name the cause class from the reference table, not "could crash". Severity needing a runtime number → say so and route to `performance-qa-engineer` / `/investigate-device-crash`.
4. **Report** — most severe first; clean sweep → say so, invent nothing. Fix direction names the change without writing it. Fields per `qa-standards` finding format.
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

## Never
- Edit code.
- Claim a confirmed regression or crash from a static read.
- Widen into a full correctness or security review (route instead).
- Invoke the gated crash-anr skills (read their reference files).

# Code risk patterns

Shared by `/review-code-risks` and `code-reviewer`. A grep hit is a candidate: confirm a hot path or a real boundary crossing first, cite the clause.

## Performance
Clauses: `csharp-standards` → `references/performance-and-algorithms.md`.
- `new`/string concat/LINQ in Update-family methods; uncached per-frame `GetComponent`; runtime `Find`/`FindObjectOfType(s)`.
- Hot-path `Instantiate`/`Destroy` without a pool; `Distance`/`Sqrt` for a threshold instead of `sqrMagnitude`.
- `SendMessage`/`BroadcastMessage`/string `Invoke`; uncached `new WaitForSeconds` in a coroutine loop; repeated uncached `transform.` reads.
- String-overload `Animator.Set*` instead of `StringToHash`; boxed `foreach` over `IEnumerable<T>`/LINQ in a hot path.
- Empty Update-family/`OnGUI`/collision callbacks; unbounded nested loops over a count-scaling collection.

## Memory
Clauses: same file.
- `+=` without `-=` in `OnDisable`/`OnDestroy`; uncleared `StartCoroutine`.
- Static/singleton field holding a MonoBehaviour, scene object or large collection; only-growing collection with no cap/pool/clear point.
- Long-lived lambda capturing `this` or a large collection; high-frequency `Instantiate`/`Destroy` with no `ObjectPool<T>`.

## Crash/ANR
Clauses: `csharp-standards` → `references/coding-principles.md` Null safety / Exception handling.
- Unguarded Inspector field or `GetComponent`/`Instantiate` result; `UnityEngine.Object` dereferenced across frames without `if (this.x)` (fake-null).
- `catch (Exception)`/empty catch, especially around signature/token verification or a payment callback.
- Sync disk/network I/O or large sync load on the main thread — cite the row in `.claude/skills/crash-anr-fault-domain-triage/references/anr-classes-and-mitigation.md`, read directly, never invoke that skill.
- Lock/blocking wait across a long main-thread op.
- Reflection/`Activator.CreateInstance`/generic virtual call reachable only via serialization → point to `build-fault-triage`.

## Filter
- Drop a match that is not hot, not a real boundary crossing, or guarded nearby.
- Name the cause class from the reference table, not "could crash".
- Severity that needs a runtime number → say so and route to `performance-qa-engineer` / `/investigate-device-crash`.
- Every match is a static signal only — not measured, not reproduced on device. Never report it as a confirmed regression or crash.

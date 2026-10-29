# Coding principles

Synthesized from project decisions; adds to rule `csharp.md`.

## Shared Core integrity
- Outcome-deciding logic (damage, state machines, cooldowns, economy) lives only in `Game.Core.*`; Client calls it, never reimplements it.
- Core is deterministic so client prediction and server authority agree: seeded injectable RNG, no wall-clock time, no float math that diverges across platforms.
- A rule needing Unity (raycast): Client resolves the data, Core makes the decision.

## SOLID
- **Single Responsibility** — a MonoBehaviour mixing input, rules and UI is split.
- **Open/Closed** — a growing `switch` on a type enum becomes one implementation per type (`IAbility`).
- **Dependency Inversion** — depend on interfaces (`IInputProvider`), never concrete singletons, ambient statics or `UnityEngine` types in Core; this is what makes Core testable.

## KISS — Keep It Simple
- The boring, obvious design; no abstraction with one caller.

## YAGNI — You Aren't Gonna Need It
- Build only what the spec asks: no speculative hooks, options or extension points.

## Law of Demeter (Principle of Least Knowledge)
- Ask the object you hold (`player.GetEquippedDamage()`); never reach through it.

## POLA/POLS — Principle of Least Astonishment
- A member does only what its name says: `GetHealth()` never mutates, `TakeDamage()` never also saves.

## SLAP — Single Level of Abstraction Principle
- One abstraction level per method body; move low-level detail into a named helper.

## Structure
- Composition over deep MonoBehaviour inheritance.
- Magic values become named constants, ScriptableObject config or Core constants.
- Unity 6.0 compiles C# 9: file-scoped namespaces fail with CS8773, so block-scoped unless the project's compiler is newer.
- `Func<>`/`Action<>` for C#-only callbacks; `UnityEvent` when the Inspector must wire it.

## `this.` qualification
- Every instance field, property, method and event, even with a `_` prefix and no collision — deliberate divergence from the C# default so instance state stands out from locals in long `Update`/coroutine bodies. Statics take the type name.

## `var` and LINQ
- LINQ is fine in editor tooling, SDK/config code and one-off setup; never in a hot path.

## Comments
- Policy per rule `csharp.md`. Form: `//` on its own line above the code, capitalised, ending with a period; never `/* */` or trailing.

## Exception handling
- `using` statement or declaration for every `IDisposable`, never manual `try/finally` + `Dispose()`; release on every path, early returns included.

## Event handlers
- A lambda only when it cannot outlive the subscriber; anything lifetime-bound is a named method unsubscribed in `OnDisable`/`OnDestroy` — a lambda cannot be unsubscribed.

## Performance discipline (both PC and mobile — mobile is the tighter budget)
- Floor: rule `csharp.md` hot paths, including its runtime `Find*` ban; depth in [performance-and-algorithms.md](performance-and-algorithms.md). Outside hot paths, `$""` interpolation is fine.
- Platform branches sit behind an interface service, not scattered `#if UNITY_ANDROID`.

## Modern C# syntax — check the project's language version first
- Raw strings, `required`, collection expressions and primary constructors need C# 11–12; confirm the project's language version and Api Compatibility Level first.

## Obsolete APIs
- No `[Obsolete]` member (own, Unity, SDK) in new code; use the replacement it names; none → flag under `Out of scope`. Existing call sites: fix only within lines you touch; otherwise flag separately.

## Correctness boundaries
- Validate at the boundaries rule `csharp.md` lists; internal calls trust their contracts — no checks for impossible state.
- Coroutines, subscriptions and load handles are released at a defined lifecycle point, on every path.

## Null safety
- A null guarantee (prior check on the same path, or a constructor or C# 11 `required` that makes null unreachable) before dereferencing: boundary values, `[SerializeField]` slots (an empty slot is routine, not hypothetical), Unity API returns (`GetComponent`, `Instantiate`), and Components held across frames (destroyed = fake null).
- `is null`/`is not null` for plain C#; implicit bool only for `UnityEngine.Object` (cheapest fake-null check) — never on Core types, interfaces or `string`.

```csharp
// UnityEngine.Object: implicit bool, not `== null`.
if (!this.ballRigidbody)
    return;

// Plain C#.
if (this.combatState is null)
    return;
```

## Handoff
- Return per skill `agent-protocol`; feature docs per skill `feature-docs`.
- Stay in spec. Within lines you already touch, fix a misleading name, stray log or dead code; flag everything else under `Out of scope`.
- Report exactly what ran, plus any experimental or limited API you shipped on.

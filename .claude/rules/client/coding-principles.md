# Client Track — Coding Principles

Applies to: C# Software Engineer, Unity Engineer, UI/UX Programmer, Tech Lead – C# Unity, Tech Lead – SDK/Platform, Tech Lead – Performance, Technical Artist.

Sources: [Microsoft Learn — Identifier names](https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/coding-style/identifier-names) and [Microsoft Learn — .NET Coding Conventions](https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/coding-style/coding-conventions), adapted for Unity/game-client context where noted.

## Shared Core integrity

- Game-rule logic (damage formulas, state machines, cooldowns, economy math — anything that decides an outcome) lives **only** in `Game.Core.*`. MonoBehaviours and other `Game.Client.*` code call into it; they never reimplement it.
- Shared Core code must be **deterministic**: no `UnityEngine.Random` (use a seeded, injectable RNG instead), no wall-clock time, no float operations that can diverge between platforms/architectures. This is required for client prediction and server authority to ever agree — non-determinism here silently breaks the whole client-server sync model.
- If a rule needs Unity APIs to evaluate (e.g. a raycast), keep the *decision* in Shared Core and pass in the already-resolved data from the Client layer — don't pull Unity calls into Core.

## Core design principles (mandatory)

These are non-negotiable, not stylistic preferences. Code Reviewer checks every submission against them, and a violation is grounds for "request changes" regardless of the feature's Triage tier.

### SOLID

- **Single Responsibility** — a class has exactly one reason to change. A MonoBehaviour that reads input, applies gameplay rules, *and* updates UI has three reasons to change and needs splitting.
- **Open/Closed** — extend behavior by adding new code (a new class implementing an interface), not by editing an existing method's branching logic. A growing `switch` on an "ability type" enum is a signal to introduce an `IAbility` implementation per type instead.
- **Liskov Substitution** — any interface implementation or subclass must be usable wherever the base type is expected, without surprising the caller. An `IDamageable.TakeDamage()` implementation that throws for certain object types, or silently no-ops when callers expect an effect, breaks this.
- **Interface Segregation** — keep interfaces narrow and role-specific (`IDamageable`, `IHealable`) instead of one fat interface (`IEntity`) that forces every implementer to stub out methods it doesn't need.
- **Dependency Inversion** — depend on abstractions, not concrete types. This is why Shared Core must not depend on concrete `UnityEngine` types, and why Client-layer code should depend on interfaces (`IInputProvider`, `IAudioService`) instead of concrete singletons — it's also what makes QA Automation Engineer's unit tests possible in the first place.

### KISS — Keep It Simple

Choose the simplest design that correctly solves what the Tech Spec asked for. A clever one-liner or an extra abstraction layer that only one caller will ever use makes the code harder to review and maintain — prefer the boring, obvious solution.

### YAGNI — You Aren't Gonna Need It

Build only what the current Tech Spec asks for. No speculative hooks, config options, or extensibility points for requirements that don't exist yet — this is the same rule stated operationally in Handoff below (don't add speculative extensibility), restated here as a design principle rather than a submission checklist item.

### Boy Scout Rule

Leave code slightly better than you found it — but only within the lines/method you're already touching for this task. Fix a misleading name, remove a stray debug log, delete now-dead code in that immediate area. This does **not** override the Handoff rule against refactoring unrelated code — it applies strictly to the code your current change already puts your hands on, not the rest of the file.

### Law of Demeter (Principle of Least Knowledge)

A method should only talk to its immediate collaborators, not reach through them. Avoid chains like `player.GetInventory().GetItem(0).GetStats().Damage` — ask the object you already have to do the work (`player.GetEquippedDamage()`) instead of reaching three objects deep to get the answer yourself. This also keeps a Shared Core change from rippling unpredictably through unrelated Client-layer code.

### POLA/POLS — Principle of Least Astonishment

A method or component must behave exactly as its name and signature imply — no hidden side effects. `GetHealth()` must not mutate state; `TakeDamage()` must not silently also save the game or fire an unrelated event. If a method needs to do something a caller wouldn't expect from its name, rename it or split it — don't leave the surprise in place.

### SLAP — Single Level of Abstraction Principle

Every method body should read at one consistent level of abstraction. Don't mix a high-level orchestration call (`ApplyDamage(target, amount)`) with low-level detail (raw bit-shifting, manual loop math) in the same method body — extract the low-level part into a well-named helper so the method reads like a short narrative, not a mix of "what" and "how."

## Explicit access modifiers (mandatory)

- Every type and member declaration states its access modifier explicitly — never rely on a default. This covers `class`, `struct`, `interface`, `record`/`record struct`, `enum`, `delegate`, method, field, property, event, indexer, constructor, and nested type.
- This applies regardless of what the modifier would default to if omitted (a top-level type defaults to `internal`, a class member defaults to `private`, an interface member defaults to `public`) — the rule is about the declaration always being explicit in source, not about changing what any specific member's effective access ends up being.
- Combine with the other applicable modifier(s) the declaration actually needs, in the conventional order — access modifier first, then `static`/`sealed`/`abstract`/`virtual`/`override`/`readonly`/`partial`/`async` as applicable (e.g. `public sealed class AbilityRunner`, `internal static class MathUtility`, `private readonly int _maxCharges`, `public partial class InventoryController`).
- Applies uniformly across `Game.Core.*` and `Game.Client.*` — Shared Core types, MonoBehaviours, ScriptableObjects, editor tooling, everything.
- Example:

```csharp
public sealed class AbilityRunner : MonoBehaviour
{
    private const float DefaultCooldown = 1.5f;

    [SerializeField] private float cooldown = DefaultCooldown;

    private float _remainingCooldown;

    public bool IsReady => this._remainingCooldown <= 0f;

    public void Trigger()
    {
        // ...
    }

    private void ResetCooldown()
    {
        this._remainingCooldown = this.cooldown;
    }
}
```

not:

```csharp
class AbilityRunner : MonoBehaviour   // Missing access modifier on the type.
{
    const float DefaultCooldown = 1.5f;   // Missing access modifier on the constant.

    [SerializeField] float cooldown = DefaultCooldown;   // Missing access modifier on the field.

    float _remainingCooldown;   // Missing access modifier on the field.

    bool IsReady => _remainingCooldown <= 0f;   // Missing access modifier on the property.

    void Trigger()   // Missing access modifier on the method.
    {
        // ...
    }
}
```

- Code Reviewer checks this on every submission, same as SOLID/KISS/YAGNI above — a missing access modifier is grounds for "request changes" regardless of the feature's Triage tier.

## Structure

- One class, one job (see Single Responsibility above). A MonoBehaviour that handles input, gameplay rules, animation, and UI state is a sign the class needs to be split.
- Favor composition over deep inheritance chains, especially for MonoBehaviour components.
- No magic numbers or strings — use named constants, ScriptableObject-driven config, or Shared Core constants.
- Use file-scoped namespaces (`namespace Game.Core.Combat;`) rather than block-scoped, and place `using` directives outside the namespace declaration — placing them inside makes name resolution context-sensitive and can silently break later when a new dependency introduces a colliding namespace.
- Use target-typed `new()` and object initializers to reduce noise: `PlayerState state = new();` and `new AbilityConfig { Cooldown = 2f, MaxCharges = 3 }` over the verbose forms.
- Prefer `Func<>`/`Action<>` over hand-rolled delegate types for internal C#-only callbacks. Exception: an event that must be wireable in the Unity Inspector should use `UnityEvent`/`UnityAction` instead, since `Func<>`/`Action<>` aren't Inspector-serializable.
- Use `&&`/`||`, never `&`/`|`, in conditional expressions — the non-short-circuiting bitwise forms can evaluate an expression that shouldn't run (e.g. dividing when the divisor-is-zero check was supposed to short-circuit it).
- Use language keywords for built-in types (`string`, `int`) instead of the runtime type names (`System.String`, `System.Int32`).

## `this.` qualification

- Always qualify access to an instance field, property, method, or event with `this.` (e.g. `this.health -= damage;`, `this.Attack();`, `this.OnDamaged?.Invoke();`) — never omit it, even when there's no naming collision to disambiguate.
- This is a deliberate project convention and intentionally diverges from the common C# style-guide default of omitting `this.` unless required for disambiguation. Reason: it makes instance-member access visually distinct from local variables, parameters, and static members at a glance — valuable in Unity's MonoBehaviour-heavy code, where a local variable inside a long `Update()`/coroutine body frequently shares a similar name with a field.
- Applies uniformly regardless of the `_camelCase` prefix already used for private fields (see `naming-convention.md`) — the two conventions stack, they don't replace each other.
- Does not apply to static members — `this` cannot qualify a static member; use the type name for those, per standard C# rules.

## `var` and LINQ

- Use `var` only when the type is obvious from the right-hand side (`var health = 100;`, `var controller = new PlayerController();`). If the type isn't obvious from the assignment itself, spell it out.
- Always use an explicit type for `foreach` loop variables — the collection's element type usually isn't obvious at the call site.
- LINQ is fine for readability in non-performance-critical code (editor tooling, SDK/config code, one-off Shared Core setup) — use meaningful query variable names and put `where` before other clauses. **Never use LINQ inside a hot path** (`Update`, `FixedUpdate`, per-frame/per-tick code) — see Performance discipline below.

## Comments

- Comments explain non-obvious **why** (a workaround, a hidden constraint), never restate **what** the code already says. This project intentionally writes fewer comments than typical Microsoft samples — don't add an XML doc comment to every public member by default; add one only when the member's contract genuinely isn't obvious from its name and signature.
- When a comment is warranted: use `//`, not `/* */`. Put it on its own line above the code, not trailing at end of line. Capitalize the first letter, end with a period, one space after `//`.

## Code aesthetics & elegance (mandatory)

Correctness and stability come from code that is easy to scan and hard to misread. These rules exist to keep a control-flow mistake or a mid-chain exception from hiding inside a dense line — same motivation as Null safety and Exception handling elsewhere in this file, applied to layout and expression shape.

- **No inline statement bodies.** Never write a statement's body on the same line as its header — `if (x) return;`, `for (...) DoWork();`, a single-line property/method with `=>` hiding a non-trivial call. The body always starts on its own line below the header. This applies to `if`/`else`/`for`/`foreach`/`while`/`switch` arms alike.
- **Single-statement `if`/`for`/`foreach`/`while` bodies still go on their own line, but may skip `{ }`** — per the Layout exception above:

    ```csharp
    if (!this.target)
        return;

    foreach (Ability ability in this.abilities)
        ability.Tick(deltaTime);
    ```

    Never write `if (!this.target) return;` on one line. And the moment a second statement is needed, add Allman `{ }` around both — don't leave a dangling second line that looks like part of the block but isn't:

    ```csharp
    if (!this.target)
    {
        this.CancelAbility();
        return;
    }
    ```

- **Break up chained/sequential calls into named temporaries.** A chain of calls or a sequence of dependent operations written inline hides *which* step failed or returned an unexpected value, and makes the chain unreadable and unstable to modify. Give each meaningful intermediate result its own well-named local variable instead of nesting calls or chaining them inline:

    ```csharp
    Inventory inventory = this.player.GetInventory();
    Item equippedWeapon = inventory.GetEquippedItem(EquipSlot.Weapon);
    int equippedDamage = equippedWeapon.GetStats().Damage;
    ```

    not:

    ```csharp
    int equippedDamage = this.player.GetInventory().GetEquippedItem(EquipSlot.Weapon).GetStats().Damage;
    ```

    **Exception** — a fluent builder-style API (a builder pattern, LINQ's own fluent methods outside hot paths, UI Toolkit's `.Query<T>()` chains, or any API explicitly designed to be chained as one expression) is exempt: chaining *is* that API's intended shape, and breaking it into temporaries per intermediate step fights the pattern instead of clarifying it. This exception is about the API's own designed fluent surface — it does not extend to an incidental chain of ordinary calls that merely happen to return objects (like the Law of Demeter example above), which still gets broken into temporaries.
- **Wrap long lines, and align the wrap.** When a line grows hard to scan — a method signature with many parameters, a long conditional, a chained call that must wrap — break it across lines and align the continuation to the opening column, so parameters/operands read as a clean vertical column rather than a ragged one:

    ```csharp
    public void ApplyDamage(IDamageable target,
                             float amount,
                             DamageType type,
                             Entity source)
    {
        // ...
    }
    ```

    not a ragged, inconsistently indented wrap.
- **Prefer modern operators over hand-rolled checks.** Use the language's own null/type/condition idiom instead of writing the equivalent logic by hand:
  - Null checks: `?.` (null-conditional) and `??`/`??=` (null-coalescing) instead of a manual `if (x != null) { ... }` just to guard a single access or assignment.
  - Null tests as conditions: `is null` / `is not null` instead of `== null`/`!= null` for plain C# reference types (this does not override the `UnityEngine.Object` implicit-`bool` rule in Null safety above — that rule still wins for Unity object references).
  - Type checks: pattern matching (`if (value is PlayerController controller)`) instead of `GetType() == typeof(...)` or an `as` cast followed by a separate manual null check.
  - Branch-on-type/value logic: a `switch` expression with property/positional patterns instead of a chain of `if`/`else if` re-testing the same value.
  - Apply these everywhere they read at least as clearly as the manual form — never force one in where the manual form is genuinely the clearer read (see KISS).
- **Elegance over verbosity.** Prefer the shortest form that stays fully readable — expression-bodied members for a true one-liner (`public bool IsReady => this._remainingCooldown <= 0f;`), target-typed `new()`, object/collection initializers. This does not relax any other rule in this file — an expression-bodied member is still subject to the "no inline statement bodies" rule above if its body is a call chain that should be broken into temporaries, and KISS/YAGNI still governs: elegant means *shortest-while-clear*, never clever or cryptic.

## Exception handling

- Catch specific exception types with a clear reason you can act on; never catch bare `System.Exception` (or `catch {}`) to silently swallow an error.
- Use `using` (the statement or the C# 8+ declaration form) for any `IDisposable` instead of manual `try/finally` + `Dispose()` — relevant mainly in SDK/Platform and R&D code that touches non-Unity resources (file handles, network clients); most `UnityEngine.Object` lifetimes are managed by Unity itself, not `IDisposable`.

## Event handlers

- A lambda inline handler is fine only when its lifetime can't outlive the subscriber (e.g. a one-shot local callback). For any event subscription tied to a MonoBehaviour's lifetime, use a named method instead of a lambda, and unsubscribe it in `OnDisable`/`OnDestroy` — an inline lambda can't be unsubscribed, which is a common source of Unity memory leaks and dangling references to destroyed objects.

## Performance discipline (both PC and mobile — mobile is the tighter budget)

- No per-frame allocations in `Update()`/`FixedUpdate()`/`LateUpdate()` — no `new`, no LINQ, no string interpolation/concatenation, no boxing in hot paths.
- Cache `GetComponent<T>()` results outside of per-frame methods; never call it inside `Update()`.
- Never use `Find`/`FindObjectOfType` at runtime — use direct references, a service locator, or an event system instead.
- Pool frequently instantiated/destroyed objects (projectiles, VFX, enemies) rather than `Instantiate`/`Destroy` in hot paths.
- Outside hot paths, use string interpolation (`$"{a}, {b}"`) for one-off strings, and `StringBuilder` when appending in a loop.
- Keep platform-specific branches behind a clean abstraction (an interface-based platform service), not scattered `#if UNITY_ANDROID` / `#if UNITY_IOS` directives across gameplay code.

## Layout

- 4-space indentation, no tabs.
- Allman brace style — opening brace on its own line, matching the block's indentation. **Exception**: an `if`/`else`/`for`/`foreach`/`while` body that is a single statement may omit `{ }` entirely, provided that statement is on its own line below the header (never on the same line as the header) — see Code aesthetics & elegance below for the full rule and its risk trade-off. Any body with more than one statement always gets Allman `{ }`, no exception.
- One statement and one declaration per line.
- Blank line between method/property definitions.
- Use parentheses to make operator precedence explicit in non-trivial expressions, even when not strictly required.
- No fixed character-per-line limit is enforced (Microsoft's own 65-character guidance is for their docs website, not production code) — keep lines readable, wrap when a line's intent gets hard to scan, particularly for method signatures with many parameters. See Code aesthetics & elegance below for how to align a wrapped signature/chain.

## Modern C# syntax — check the project's language version first

Raw string literals, `required` properties, collection expressions (`[...]`), and primary constructors are all real Microsoft-recommended patterns, but they require a C# language version Unity's compiler toolchain (Mono or IL2CPP, depending on the target platform) must actually support. Confirm the project's configured C# version before using any of them — don't assume the latest syntax compiles on this project's Unity version.

## Obsolete APIs

- Never write new code that declares or consumes a class, struct, field, method, property, event, or any other member marked with `[Obsolete]` — including Unity API members Unity itself has marked obsolete (e.g. an old `UnityEngine.Networking` type, a deprecated `Input` API superseded by the new Input System, an old Addressables/Analytics call). This applies whether the `[Obsolete]` attribute lives in this project's own code, a first-party Unity API, or a third-party SDK.
- Before using any API you're not certain is current, check whether it (or its containing type) carries `[Obsolete]` — in the IDE this shows as a strikethrough/deprecation warning — and if so, find the modern replacement the deprecation message or current documentation points to, and use that instead.
- If a Tech Spec or existing surrounding code calls for behavior only reachable through an obsolete member with no direct replacement, don't silently keep using it — flag it back per the Handoff rule below instead of shipping new code against it.
- This rule governs new usage going forward. It does not by itself mandate a standalone refactor of pre-existing obsolete-API call sites outside your current change — remove one only if it falls within the lines/method you're already touching (see Boy Scout Rule above); otherwise flag it separately rather than expanding the current submission's scope.

## Correctness boundaries

- Validate only at real boundaries: user input, save-data deserialization, network messages (when the backend track is active), third-party SDK callbacks. Internal calls between your own classes can trust their contracts — don't defensive-check state that can't actually happen.
- Clean up coroutines and event subscriptions on `OnDisable`/`OnDestroy` — leaked coroutines and dangling event handlers are a recurring source of hard-to-reproduce bugs.

## Null safety

Every reference-type value that crosses one of the real boundaries above — or that Unity itself can leave
unassigned or silently invalidate — must have a **null guarantee** before it is ever dereferenced: either an
explicit null check that has already run in the same code path, or a mechanism that makes null structurally
unreachable (a `required` property, a constructor that always assigns it, or the language's nullable
reference type feature if enabled for this project's confirmed C# version — see the Modern C# syntax caveat
above). This is not a blanket call to defensive-check everything; it applies at the same boundaries
`Correctness boundaries` already names, plus the Unity-specific ones below that are easy to forget because
they don't look like external input:

- A `[SerializeField]` or public Inspector-serialized reference — an unassigned Inspector slot is a routine
  real-world null, not a hypothetical one, so it does not qualify for the "internal calls can trust their
  contracts" carve-out even though the field lives on your own class.
- The result of `GetComponent<T>()`, `Instantiate(...)`, or any Unity API that returns a reference — Unity
  APIs fail by returning null (or a destroyed reference) rather than by throwing.
- Any `MonoBehaviour`/`Component` reference held across frames — Unity can destroy the underlying native
  object at any time, leaving a C# reference that isn't literally `null` but must be treated as gone (see
  below).

**Plain C# reference types** (`Game.Core.*` types, interfaces, records, `string`, and any other type that
does not derive from `UnityEngine.Object`) use the ordinary explicit comparison:

```csharp
if (this.combatState != null)
{
    // ...
}
```

**Types derived from `UnityEngine.Object`** (`GameObject`, `Component`, `MonoBehaviour`, `Collider`,
`Rigidbody`, `Transform`, and the like) use Unity's overloaded implicit `bool` check instead of an explicit
`!= null` comparison:

```csharp
if (this.collider)
{
    // ...
}

if (!this.ballRigidbody)
{
    return;
}
```

not:

```csharp
if (this.collider != null)
{
    // ...
}

if (this.ballRigidbody == null)
{
    return;
}
```

Reason: Unity overloads `==`/`!=`/`bool` on `UnityEngine.Object` to detect a "fake null" — a managed wrapper
whose native object has already been destroyed but whose C# reference isn't literally `null` yet.
`if (this.collider)` reaches that check through the single overloaded `bool` operator directly; `!= null`
routes through equality-operator overload resolution first. Both give the correct destroyed-object result,
but the direct `bool` check is the cheaper path at runtime, and it is Unity's own recommended idiom — default
to it anywhere this runs often (`Update`, physics/collision callbacks, per-frame code).

This exception is narrow and literal: it applies only to `UnityEngine.Object`-derived references. Never apply
the same implicit-`bool` shortcut to a `Game.Core.*` type, an interface, a `string`, or any other plain C#
reference — none of those carry Unity's overloaded operator, and `if (value)` would not even compile for most
of them.

## Handoff

- Every submission to Code Reviewer includes a short note of assumptions/known limitations (per the Implementation Note handoff format in `.claude/rules/implementation-note.md`).
- Stay scoped to what the Tech Spec asked for. Don't refactor unrelated code, don't add speculative extensibility, don't fix unrelated issues in the same submission — flag them separately instead.
- When a Complex-tier feature (per Technical Architect's Triage) reaches completion, its handoff also includes the `README.md` required by `.claude/rules/client/feature-documentation.md`. Simple/Medium tier work is exempt from this.

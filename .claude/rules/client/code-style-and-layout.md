# Client Track — Code Style & Layout

Applies to: C# Software Engineer, Unity Engineer, UI/UX Programmer, Tech Lead – C# Unity, Tech Lead – SDK/Platform, Tech Lead – Performance, Technical Artist.

## Relationship to other rules

This file governs **mechanical style**: explicit declaration modifiers, brace/indentation layout, statement shape, and the preference for modern language operators over hand-rolled equivalents. It does not replace `coding-principles.md`, which owns architecture-level design principles (SOLID/KISS/YAGNI), Shared Core integrity, correctness/safety boundaries (exception handling, null safety), and submission handoff — read both before writing any code. `naming-convention.md` owns identifier casing and namespace-to-folder mapping; this file owns how a declaration and its body are shaped once named.

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

- Code Reviewer checks this on every submission, same as SOLID/KISS/YAGNI in `coding-principles.md` — a missing access modifier is grounds for "request changes" regardless of the feature's Triage tier.

## Layout

- 4-space indentation, no tabs.
- Allman brace style — opening brace on its own line, matching the block's indentation. **Exception**: an `if`/`else`/`for`/`foreach`/`while` body that is a single statement may omit `{ }` entirely, provided that statement is on its own line below the header (never on the same line as the header) — see Code aesthetics & elegance below for the full rule and its risk trade-off. Any body with more than one statement always gets Allman `{ }`, no exception.
- One statement and one declaration per line.
- Blank line between method/property definitions.
- Use parentheses to make operator precedence explicit in non-trivial expressions, even when not strictly required.
- No fixed character-per-line limit is enforced (Microsoft's own 65-character guidance is for their docs website, not production code) — keep lines readable, wrap when a line's intent gets hard to scan, particularly for method signatures with many parameters. See Code aesthetics & elegance below for how to align a wrapped signature/chain.

## Code aesthetics & elegance (mandatory)

Correctness and stability come from code that is easy to scan and hard to misread. These rules exist to keep a control-flow mistake or a mid-chain exception from hiding inside a dense line — same motivation as Null safety and Exception handling in `coding-principles.md`, applied here to layout and expression shape.

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

    **Exception** — a fluent builder-style API (a builder pattern, LINQ's own fluent methods outside hot paths, UI Toolkit's `.Query<T>()` chains, or any API explicitly designed to be chained as one expression) is exempt: chaining *is* that API's intended shape, and breaking it into temporaries per intermediate step fights the pattern instead of clarifying it. This exception is about the API's own designed fluent surface — it does not extend to an incidental chain of ordinary calls that merely happen to return objects (like the Law of Demeter example in `coding-principles.md`), which still gets broken into temporaries.
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
  - Null tests as conditions: `is null` / `is not null` instead of `== null`/`!= null` for plain C# reference types (this does not override the `UnityEngine.Object` implicit-`bool` rule in `coding-principles.md`'s Null safety section — that rule still wins for Unity object references).
  - Type checks: pattern matching (`if (value is PlayerController controller)`) instead of `GetType() == typeof(...)` or an `as` cast followed by a separate manual null check.
  - Branch-on-type/value logic: a `switch` expression with property/positional patterns instead of a chain of `if`/`else if` re-testing the same value.
  - Apply these everywhere they read at least as clearly as the manual form — never force one in where the manual form is genuinely the clearer read (see KISS in `coding-principles.md`).
- **Elegance over verbosity.** Prefer the shortest form that stays fully readable — expression-bodied members for a true one-liner (`public bool IsReady => this._remainingCooldown <= 0f;`), target-typed `new()`, object/collection initializers. This does not relax any other rule in this file — an expression-bodied member is still subject to the "no inline statement bodies" rule above if its body is a call chain that should be broken into temporaries, and KISS/YAGNI in `coding-principles.md` still governs: elegant means *shortest-while-clear*, never clever or cryptic.

## Rules

- Every type and member declaration is explicit about its access modifier — no relying on a default, no exceptions.
- Allman braces everywhere except a single-statement `if`/`for`/`foreach`/`while` body, which still goes on its own line.
- Never write a statement body on the same line as its header.
- A chain of dependent calls is broken into named temporaries, except a designed fluent/builder API, which stays chained.
- A wrapped long line aligns its continuation to the opening column rather than an inconsistent ragged indent.
- Modern null/type/condition operators (`?.`, `??`/`??=`, `is null`/`is not null`, pattern matching, `switch` expressions) are preferred over hand-rolled equivalents wherever they read at least as clearly.
- Shortest-while-clear wins over verbose ceremony — but never at the cost of another rule in this file or in `coding-principles.md`.

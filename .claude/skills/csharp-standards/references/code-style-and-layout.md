# Code style and layout

Synthesized from project decisions; adds to rule `csharp.md`.

## Explicit access modifiers
- Access modifier first, then `static`/`sealed`/`abstract`/`virtual`/`override`/`readonly`/`partial`/`async`. Core, Client, editor tooling and tests alike.

```csharp
public sealed class AbilityRunner : MonoBehaviour
{
    private const float DefaultCooldown = 1.5f;

    [SerializeField] private float cooldown = DefaultCooldown;

    private float _remainingCooldown;

    public bool IsReady => this._remainingCooldown <= 0f;

    private void ResetCooldown()
    {
        this._remainingCooldown = this.cooldown;
    }
}
```

## Layout
- A one-statement `if`/`else`/`for`/`foreach`/`while` body may skip braces, on its own line; a second statement brings Allman braces around both.
- Parentheses make non-trivial precedence explicit. No fixed line length.

## Code aesthetics & elegance
- **Named temporaries** for a chain of dependent calls, so the failing step is visible:

    ```csharp
    Inventory inventory = this.player.GetInventory();
    Item weapon = inventory.GetEquippedItem(EquipSlot.Weapon);
    int damage = weapon.GetStats().Damage;
    ```

    Exempt: an API designed to chain (builders, LINQ outside hot paths, UI Toolkit `Query<T>()`). An incidental chain of ordinary calls is not exempt.
- **Aligned wraps** — continuation lines align to the opening column:

    ```csharp
    public void ApplyDamage(IDamageable target,
                            float amount,
                            DamageType type)
    ```

- **Operators** — `?.`/`??=` over a manual guard for one access; `is T x` over `GetType() == typeof(T)` or `as` + null check; a `switch` expression over an `if`/`else if` chain re-testing one value. Only where at least as clear. Not on `UnityEngine.Object`: `?.`/`??`/`is null` bypass fake-null; use the implicit bool.
- **Shortest while clear** — expression body only for a true one-liner; target-typed `new()` and initializers; never clever.

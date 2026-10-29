# Delegate Objects (Strategy) and Extendable Enums

Sources: Manual `class-ScriptableObject.html`; `CreateAssetMenuAttribute`. Shapes follow Ryan Hipple (Unite Austin 2017) and the classic Strategy pattern.

## Delegate Object
An abstract SO with one behavior method, implemented by concrete SO subclasses (one asset per variant). The consuming prefab holds `[SerializeField] AbilityTargetingSO targeting`; swapping behavior is reassigning the asset, with no code edit or `switch` on a behavior enum (Open/Closed, per `csharp-standards`).
- Contract example: `abstract IReadOnlyList<Vector3> GetTargetPoints(Vector3 origin, Vector3 direction)`; subclasses `ConeTargetingSO`, `SingleTargetTargetingSO`.
- Use when behavior varies by design-time choice, not by a runtime condition one method could branch on.
- The method may resolve spatial candidates (presentation concern). What those points mean (damage, hit, cooldown) stays in `Game.Core.*`; pass resolved points in as data. A Delegate Object that also computes damage reimplements a rule outside Core.

## Extendable Enum
Replaces a closed C# `enum` (every new case recompiles every `switch`) with a base SO type (`DamageTypeSO`, `[SerializeField] string id`) and one asset per case (`SO_DamageType_Fire.asset`). Designers add cases as assets; lookups use `Dictionary<DamageTypeSO, float>` (e.g. a resistance table) instead of a growing `switch`.
- Compare by `Id`, not reference `==`, whenever a case could load twice (duplicated import, two Addressables bundles each containing a copy). Reference equality is safe only when every case loads from exactly one asset.
- It adds cases only; it does not model transitions or guards (`stateless-state-machines`).

## Which one
| | Delegate Object | Extendable Enum |
|---|---|---|
| Varies | Behavior (what happens) | Identity/category (which kind) |
| Typical member | Abstract method | `Id`/data fields only |

They combine: a category SO can hold a Delegate Object reference for "what this category does".

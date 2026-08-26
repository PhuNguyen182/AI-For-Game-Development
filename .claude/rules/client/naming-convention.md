# Client Track — Naming Convention

Applies to: C# Software Engineer, Unity Engineer, UI/UX Programmer, Tech Lead – C# Unity, Tech Lead – SDK/Platform, Tech Lead – Performance, Technical Artist.

Source: [Microsoft Learn — Identifier names: rules and conventions (C#)](https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/coding-style/identifier-names), combined with the standard Unity convention for Inspector-serialized fields (see override below).

## Mandatory naming quality requirement

Every identifier — regardless of casing rule — must be:
- **Concise** — no unnecessary words, no redundant type/context repetition (`Player.playerHealth` is wrong; `Player.health` is right).
- **Meaningful** — the name alone should say what the thing is or does, without needing a comment.
- **Natural language** — real words, not cryptic shorthand. Avoid abbreviations or acronyms unless they're widely known and unambiguous in a game-dev context (`Hp`, `Ui`, `Vfx`, `Ai` are fine; `plyrMgr`, `dmgCalc` are not).
- Never a single letter, except a simple loop counter (`for (int i = 0; ...)`).
- Never two consecutive underscores (`__`) — that pattern is reserved for compiler-generated identifiers.

## C# identifier casing

| Element | Convention | Example |
|---|---|---|
| Namespace | PascalCase, meaningful/hierarchical | `Game.Core.Combat`, `Game.Client.UI` |
| Class / Struct / Record / Delegate | PascalCase | `PlayerController`, `readonly record struct DamageInfo` |
| Interface | PascalCase, `I` prefix | `IDamageable`, `IAbilityHandler` |
| Public method / local function | PascalCase | `CalculateDamage()` |
| Public property | PascalCase | `CurrentHealth` |
| Public field (plain C# class, not Inspector-serialized) | PascalCase — but keep public fields rare; prefer properties | `IsValid` |
| Record positional parameter | PascalCase (becomes a public property) | `public record PhysicalAddress(string Street, string City);` |
| Private / internal non-constant field | `_camelCase` | `_currentHealth` |
| Private / internal static field | `s_camelCase` | `s_instanceCount` |
| Private / internal `[ThreadStatic]` field | `t_camelCase` | `t_scratchBuffer` |
| Constant (field or local, any access modifier) | PascalCase | `MaxHealth` |
| Local variable / method parameter | camelCase | `damageAmount` |
| Primary constructor parameter — `class`/`struct` | camelCase (same as any parameter) | `public class DataService(IWorkerQueue workerQueue)` |
| Primary constructor parameter — `record` | PascalCase (becomes a public property) | `public record Address(string Street, string City);` |
| Generic type parameter | `T` alone if self-explanatory; otherwise `T`-prefixed descriptive name | `List<T>`, `ISessionChannel<TSession>` |
| Enum type | PascalCase, singular noun (plural if `[Flags]`) | `enum AbilityState`, `[Flags] enum InputActions` |
| Attribute type | PascalCase, `Attribute` suffix | `RequiresAuthorityAttribute` |

## Unity override — Inspector-serialized fields use camelCase

Any field Unity's Inspector can see and edit is exposed as **design-time data**, not public API surface — so it follows Unity's own convention (camelCase) instead of the general C# public-field rule above:

- A `public` field on a `[Serializable]` class/struct.
- Any `private`/`protected` field marked `[SerializeField]`.

```csharp
[Serializable]
public struct AbilityConfig
{
    public float cooldown;      // public, but Inspector-serialized → camelCase
    public int maxCharges;
}

public class PlayerController : MonoBehaviour
{
    [SerializeField] private float moveSpeed;   // SerializeField → camelCase, keeps _ off since it's Inspector data, not internal state
    [SerializeField] private AbilityConfig ability;
}
```

This is the only exception to the PascalCase-for-public rule. A `public` field or property that is **not** meant for the Inspector (i.e. real public API, not `[Serializable]`/`[SerializeField]`) still follows standard PascalCase.

## Supplementary clarity conventions (beyond the MS doc, kept for consistency)

| Case | Convention | Example |
|---|---|---|
| Boolean (any scope) | `Is` / `Has` / `Can` / `Should` prefix | `isGrounded` (serialized) / `IsGrounded` (property) |
| Event field | PascalCase, describes what happened — no forced prefix | `public event Action PlayerDied;` |
| Event handler / subscriber method | `On<Event>` prefix | `void OnPlayerDied()` |
| Async method | `Async` suffix | `LoadLevelAsync()` |

## Unity assets (not C# identifiers, but named the same disciplined way)

| Asset type | Convention | Example |
|---|---|---|
| Prefab | PascalCase, `Category_Name` | `Enemy_Goblin`, `Weapon_Sword` |
| Scene | `Scene_Name` | `Scene_MainMenu`, `Scene_Level01` |
| ScriptableObject asset | `SO_Name` | `SO_PlayerStats` |
| Material | `Mat_Name` | `Mat_WaterSurface` |
| Texture | `Tex_Name` | `Tex_PlayerAlbedo` |
| Animation clip | `Anim_Name` | `Anim_PlayerRun` |
| Animator Controller | `AC_Name` | `AC_Player` |
| Shader | `Shader_Name` | `Shader_ToonWater` |
| VFX / Particle prefab | `VFX_Name` | `VFX_ExplosionSmall` |
| Assembly Definition (.asmdef) | matches its root namespace | `Game.Core.asmdef` |

## Namespace boundary (enforces the Shared Core rule)

- `Game.Core.*` — Shared Core only. No `UnityEngine` dependency. Owned by C# Software Engineer.
- `Game.Client.*` — Unity-side integration (MonoBehaviours, scenes, prefabs). Owned by Unity Engineer / UI/UX Programmer.
- `Game.Server.*` — server-authoritative wrapper (only exists when the backend track is active). Owned by Server-Authoritative Logic Engineer.

If a class needs to live in `Game.Core.*`, it must not reference `UnityEngine` types. If it does, it belongs in `Game.Client.*` instead.

## Rules

- Follow the casing table exactly — it is not optional per file or per author.
- Never use Hungarian-style type prefixes on variables (no `strName`, `bIsActive`).
- Keep naming consistent even if a specific PR's context suggests a shortcut — consistency across the whole client track matters more than local convenience.

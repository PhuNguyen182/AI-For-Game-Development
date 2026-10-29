# Naming convention

Synthesized from project decisions; adds to rule `csharp.md`.

## C# identifier casing

Base casing: rule `csharp.md`; this table lists only the additions.

| Element | Convention |
|---|---|
| Internal field / internal static field | `_camelCase` / `s_camelCase`, as private |
| `[ThreadStatic]` field | `t_camelCase` |
| Public field, not Inspector-serialized | PascalCase; rare, prefer a property |
| Record positional / record primary-constructor parameter | PascalCase (`record Address(string Street)`) |
| Class/struct primary-constructor parameter | camelCase |
| Boolean | `Is`/`Has`/`Can`/`Should`: `isGrounded` serialized, `IsGrounded` property |
| Enum | Singular; plural if `[Flags]` |
| Event | PascalCase, what happened, no prefix: `PlayerDied`; its handler `OnPlayerDied` |

- No context repetition (`Player.health`, not `Player.playerHealth`). Game-dev abbreviations only (`Hp`, `Ui`, `Vfx`, `Ai`; never `plyrMgr`). Single letters only for loop counters. Never `__`.

## Unity override — Inspector-serialized fields use camelCase
- A `public` field on a `[Serializable]` type, or a `[SerializeField]` private/protected field: camelCase, no `_`. A public non-serialized member stays PascalCase.

```csharp
[Serializable]
public struct AbilityConfig
{
    public float cooldown;
}
```

## Unity assets
- Prefab `Category_Name` (`Enemy_Goblin`) · Scene `Scene_Name` · ScriptableObject `SO_Name` · Material `Mat_` · Texture `Tex_` · Animation clip `Anim_` · Animator Controller `AC_` · Shader `Shader_` · VFX/particle prefab `VFX_` · `.asmdef` = its root namespace (`Game.Core.asmdef`).

## Namespace boundary (enforces the Shared Core rule)
- `Game.Core.*` — Shared Core, no `UnityEngine`; `csharp-engineer`. A class needing `UnityEngine` belongs in Client.
- `Game.Client.*` — Unity integration; `gameplay-engineer`, `ui-engineer`.
- `Game.Server.*` — server-authoritative wrapper, only when the backend track is active; `netcode-engineer`.

## Namespace must mirror the folder path
- Every folder segment below `Assets/`, each PascalCased (`ui` → `UI`); the file name is never a segment. Every `.cs` file, tests and editor tooling included; the `.asmdef` name does not change it.
- `Assets/Game.Client/UI/Inventory/InventoryPanel.cs` → `Game.Client.UI.Inventory`.

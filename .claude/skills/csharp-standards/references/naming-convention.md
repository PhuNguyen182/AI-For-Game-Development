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
- Prefab `Category_Name` (`Enemy_Goblin`) · Scene `Scene_Name` · ScriptableObject `SO_Name` · Material `Mat_` · Texture `Tex_` · Animation clip `Anim_` · Animator Controller `AC_` · Shader `Shader_` · VFX/particle prefab `VFX_` · `.asmdef` `name` = `rootNamespace` = its folder path below `Assets/`, segments joined by `.` (`_Project.Scripts.Ads.Core.asmdef` in `Assets/_Project/Scripts/Ads/Core/`).

## Folders
- PascalCase segments, never a `.` in a folder name; a leading `_` is allowed (`_Project`).
- Feature layout (root `Assets/_Project/Scripts/` unless `CLAUDE.md` overrides it); create only the folders the feature uses:

| Folder | asmdef | Holds | Owner |
|---|---|---|---|
| `<Feature>/` | `…<Feature>` | Unity code: `DataControllers/`, `Views/` | `gameplay-engineer`, `ui-engineer` |
| `DataModels/` | `…<Feature>.DataModels`, `noEngineReferences` | Plain data types | `csharp-engineer` |
| `Core/` | `…<Feature>.Core`, `noEngineReferences`, refs `DataModels` | Game rules | `csharp-engineer` |
| `DataControllers/` | feature root | Load/save, ScriptableObject, adapters into Core | `gameplay-engineer` |
| `Views/` | feature root | MonoBehaviour, UI | `gameplay-engineer`, `ui-engineer` |
| `Server/` | `…<Feature>.Server` | Server-authoritative wrapper; backend/netcode track only | `netcode-engineer` |
| `Editor/` | `…<Feature>.Editor`, Editor only | Editor tooling | owner of the code it serves |
| `Tests/EditMode/` | `…<Feature>.Tests.EditMode` | Edit Mode tests: Core, DataModels | `csharp-engineer` |
| `Tests/PlayMode/` | `…<Feature>.Tests.PlayMode` | Play Mode tests: scene, prefab, UI | Client implementers |

- Shared Core = every assembly with `noEngineReferences: true` (`Core/`, `DataModels/`). A class needing `UnityEngine` belongs in the feature root.
- Cross-feature contracts live in the `Shared` feature (same layout). Feature references are one-way, never a cycle; a Core assembly never references a feature root.

## Namespace = asmdef `rootNamespace` + folder path relative to that asmdef's folder
- No asmdef above the file → the folder path below `Assets/`. Never `Assets`, never the file name. Every `.cs` file, tests and editor tooling included.
- `Assets/_Project/Scripts/Ads/AdsCustomUnit.cs`, no asmdef → `_Project.Scripts.Ads`.
- Same file, asmdef `_Project.Scripts` in `Assets/_Project/` → `_Project.Scripts.Scripts.Ads`: why every asmdef's `rootNamespace` must equal its folder path.
- With that rule, namespace = folder path: `Assets/_Project/Scripts/Ads/Core/Rules/AdCap.cs` → `_Project.Scripts.Ads.Core.Rules`.
- In a `….Editor` namespace the sibling namespace hides `UnityEditor.Editor` (CS0118): write `UnityEditor.Editor` fully qualified, or put `using UnityEditor;` inside the namespace block.
- Existing code keeps its layout; only new features follow it. Moving a file updates its namespace in the same change.

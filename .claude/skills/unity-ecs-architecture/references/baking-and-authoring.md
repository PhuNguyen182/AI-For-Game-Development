# Baking and Authoring

Docs: https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/ (baking-overview, baking-baker-overview, baking-phases).

- Baking runs only in the Editor and writes entity scenes; there is no runtime equivalent.
- The authoring `MonoBehaviour` holds Inspector-editable design data and never ships as runtime state.
- One `Baker<TAuthoring>` per authoring type converts it to entity data (`AddComponent`/`AddBuffer` on the Baker write onto the entity).
- Bakers run first and independently per component; baking systems then post-process the whole result, which is where cross-entity work belongs.

## Dependencies
| Call | Effect |
|---|---|
| `GetEntity(authoring.prefab, ...)` | Registers the prefab as a dependency, returns its baked `Entity` |
| Baker's own `GetComponent<T>()` | Reads another authoring component and records the dependency |
| `authoring.GetComponent<T>()` (Unity's) | Reads the same value with no dependency registered |

An undeclared dependency does not error: incremental baking never re-runs for that value, so the Editor keeps old data while a clean build is correct, an Editor-only bug that survives playtests done in builds.

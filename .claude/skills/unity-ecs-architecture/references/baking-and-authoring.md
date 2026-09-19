# Baking & Authoring — The `Baker<T>` Contract

Sources: [Baking](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/baking.html), [Baker overview](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/baking-baker-overview.html), [Baking phases](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/baking-phases.html).
Covers: SKILL.md §4 — **"Read authoring data through the `Baker<T>` dependency APIs, never off the authoring object directly"**.

How design-time GameObject data becomes entities, and the dependency rule that
decides whether incremental baking sees a change. Baking is Editor-only; there
is no runtime equivalent to fall back on.

## The pipeline

| Subject | What it decides | Source |
|---|---|---|
| Baking | Runs **only in the Editor**, writing entity scenes — so no baking logic can be replicated as a runtime step | [Baking](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/baking.html) |
| Authoring `MonoBehaviour` | Holds design-time data in a form the Inspector can edit; never ships as runtime state | [Baking overview](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/baking-overview.html) |
| `Baker<TAuthoring>` | Declares the conversion from one authoring component to entity data; one Baker per authoring type | [Baker overview](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/baking-baker-overview.html) |
| Baker phase → baking-systems phase | Bakers run first and independently per component; baking systems then post-process the whole baked result, which is where cross-entity work belongs | [Baking phases](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/baking-phases.html) |

## Declaring dependencies

| Call | What it decides | Source |
|---|---|---|
| `GetEntity(authoring.prefab, …)` | Registers the referenced prefab as a baking dependency and returns its baked `Entity` | [Baker overview](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/baking-baker-overview.html) |
| The Baker's own `GetComponent<T>()` | Reads another authoring component **and** records the dependency, so a later change re-triggers baking | [Baker overview](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/baking-baker-overview.html) |
| `authoring.GetComponent<T>()` (Unity's own) | Reads the same value with **no** dependency registered — the silent failure this file exists for | [Baker overview](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/baking-baker-overview.html) |
| `AddComponent` / `AddBuffer` on the Baker | Writes baked component data onto the entity created for this authoring object | [Authoring and baking workflow](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/ecs-workflow-example-authoring-baking.html) |

**Critical caveat**: an undeclared dependency does not error. Incremental
baking simply never re-runs for that value, so the entity keeps its old data in
the Editor while a clean build produces the correct result — an
Editor-only-wrong bug that survives every playtest done in a build.

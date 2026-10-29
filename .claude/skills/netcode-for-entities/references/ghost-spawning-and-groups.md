# Ghost Spawning and Groups

Pages (6.6): `ghost-spawning`, ghost groups.

## Spawn paths

| Path | Mechanism |
|---|---|
| Server | `EntityManager.Instantiate` on the server; snapshots replicate it |
| Interpolated client | Delayed until `NetworkTime.InterpolationTick` passes `GhostInstance.spawnTick` |
| Predicted client | Instantiate in `PredictedSimulationSystemGroup`, guarded by `NetworkTime.IsFirstTimeFullyPredictingTick` to avoid duplicates on rollback |
| Pre-spawned | Prefab instances baked into a subscene's section 0 (never a regular scene), sorted deterministically by position/rotation, so those must be unique per ghost type |

## Predicted spawn classification
- `GhostSpawnClassificationSystem` matches a predicted spawn to the arriving server ghost by `GhostType` and spawn tick within a 5-tick window.
- A custom classifier updates in `GhostSimulationSystemGroup` after the built-in one, comparing `GhostSpawnQueue` entries (on the `GhostSpawnBuffer`) against the `PredictedGhostSpawn` buffer on the `PredictedGhostSpawnList` singleton.
- Prerequisites: a `NetworkStreamInGame` connection, the prefab's `GhostType` in the `GhostCollectionPrefab` buffer and registered in `GhostCollection`. `PredictedGhostSpawnRequest` marks an entity as such a spawn.

## Pre-spawned ghosts
- Get a `SubSceneGhostComponentHash` shared component automatically. The server assigns ID ranges via `SubSceneWithPrespawnGhosts`; clients report subscene readiness by RPC (`DisableAutomaticPrespawnSectionReporting` turns that off).
- Do not move a pre-spawned ghost before its connection is in-game: it breaks the delta-compression baseline and data may not replicate correctly.

## Ghost groups
`GhostGroup` buffer on the root prefab plus `GhostChildEntity` on each member: all are always sent in the same snapshot as the root.
- One root per group, no nesting.
- `Static` optimization is incompatible; members are forced to `Dynamic`.
- Members inherit the root's relevancy, but irrelevant-root propagation to children is a known gap in the 6.6 docs.
- A member's own `Importance`, `GhostImportance` scaling and `MaxSendRate` are ignored; the root's apply.
- Serialization is significantly slower than ungrouped, and a group exceeding `NetworkParameterConstants.MaxMessageSize` risks fragmentation. Use only for state that must arrive atomically (a vehicle and its passengers).

# Ghost Spawning and Groups — creation, pre-spawning, classification, GhostGroup

Sources: [Spawn Ghosts](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/ghost-spawning.html), [Ghost Groups](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/ghost-groups.html).
Covers: SKILL.md §4 — **"Model every piece of networked state as a ghost, never as a stream of ad hoc RPCs"**, escalation branch.

How a ghost instance actually comes into existence — server spawn, client
predicted spawn, or subscene pre-spawn — and how several ghosts are kept in
lockstep as one replication unit. The prefab-level declaration these
instances are created from is [ghost-authoring.md](ghost-authoring.md).

## Spawn paths

| Path | Mechanism | Source |
|---|---|---|
| Server spawn | `EntityManager.Instantiate` on the server; replicated to clients automatically by the snapshot system | [Spawn Ghosts](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/ghost-spawning.html) |
| Interpolated client spawn | Delayed until `NetworkTime.InterpolationTick` passes the ghost's `GhostInstance.spawnTick`, per `ClientTickRate.InterpolationTimeNetTicks` | [Spawn Ghosts](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/ghost-spawning.html) |
| Predicted client spawn | Client instantiates inside `PredictedSimulationSystemGroup`, guarded by `NetworkTime.IsFirstTimeFullyPredictingTick` to avoid duplicate spawns during rollback | [Spawn Ghosts](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/ghost-spawning.html) |
| Pre-spawned | Ghost prefab instances baked into a **subscene**, section 0, with deterministic sort by position/rotation | [Spawn Ghosts](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/ghost-spawning.html) |

## Predicted spawn classification

`GhostSpawnClassificationSystem` matches a client's predicted spawn to the
server-authoritative ghost that later arrives, within a **five-tick window**,
comparing `GhostType` and spawn tick. A custom classification system must
update in `GhostSimulationSystemGroup`, run **after**
`GhostSpawnClassificationSystem`, and compare `GhostSpawnQueue` entries
(on the `GhostSpawnBuffer`) against the `PredictedGhostSpawn` buffer on the
`PredictedGhostSpawnList` singleton.

**Prerequisites for a predicted spawn to work at all**: a
`NetworkStreamConnectionInGame` singleton must exist, the prefab's `GhostType`
must already have an entry in the `GhostCollectionPrefab` buffer, and the
prefab must be registered in `GhostCollection`'s type-to-index map. A
`PredictedGhostSpawnRequest` component marks an entity as this kind of spawn
automatically.

## Pre-spawned ghosts

- Must live inside a subscene's main section (**section 0**), never a regular scene.
- Position/rotation must be unique per ghost type — sort determinism depends on it.
- Gets a `SubSceneGhostComponentHash` shared component automatically.
- Server assigns unique ID ranges tracked via `SubSceneWithPrespawnGhosts`;
  clients report readiness for a matching subscene by RPC after loading it.

**Critical caveat**: moving a pre-spawned ghost **before** its connection
goes in-game breaks delta compression's baseline assumption, and its data
may not replicate correctly afterward — leave pre-spawned transforms alone
until `NetworkStreamInGame` is set.

## Ghost Groups

`GhostGroup` (buffer, on the root prefab) plus `GhostChildEntity` (on each
member) forces a set of ghosts to always be sent together, in the same
snapshot as their root.

| Rule | Source |
|---|---|
| Exactly one root per group; no nesting (a member cannot belong to two groups) | [Ghost Groups](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/ghost-groups.html) |
| `GhostOptimizationMode.Static` is incompatible — all members forced to `Dynamic` | [Ghost Groups](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/ghost-groups.html) |
| Members inherit the root's relevancy — but irrelevant-root propagation to children is a known gap (as of the 6.6 docs) | [Ghost Groups](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/ghost-groups.html) |
| A member's own `Importance`/`GhostImportance` scaling/`MaxSendRate` is ignored — only the root's values apply | [Ghost Groups](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/ghost-groups.html) |

**Critical caveat**: per-child chunk traversal makes group serialization
"significantly slower" than ungrouped ghosts, per the manual, and a group
whose combined entries exceed `NetworkParameterConstants.MaxMessageSize`
risks snapshot fragmentation — reserve groups for state that genuinely must
arrive atomically (e.g. a vehicle and its seated passengers), not for
convenience organization.

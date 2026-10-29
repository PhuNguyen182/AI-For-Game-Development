# Queries, events, pipeline hooks

Sources (under `manual/`): `collision-queries.html`, `simulation-results.html`, `simulation-modification.html`, `physics-pipeline.html`; `api/Unity.Physics.CollisionWorld.html`, `SimulationSingleton.html`.

## Queries
| Query | Answers |
|---|---|
| Ray cast | All or closest hits along an oriented segment |
| Collider cast | Sweeps a shape along a path, stops at first contact; right for a swept volume (a fan of rays only approximates it) |
| Collider distance | Closest points between two shapes within a radius |
| Point distance | Nearest surfaces to a point |
| Overlap | Bodies whose bounding boxes intersect a region (coarse, not exact) |

- Target: one collider when it is known; the whole `CollisionWorld` via `PhysicsWorldSingleton` (bounding-volume tree) when not.
- Filtering through collision filters is the preferred way to control results.
- Queries are designed for Burst jobs; scheduling is `unity-job-system-and-burst`.

## Events
- Direct: `GetSingleton<SimulationSingleton>().AsSimulation()` exposes `CollisionEvents` and `TriggerEvents`.
- Job: `ICollisionEventsJob` / `ITriggerEventsJob`, `Schedule()` or `ScheduleParallel()`.
- Valid only after `PhysicsSimulationGroup` finishes until it starts next frame; outside it the streams are stale or empty without error.
- Triggers never collide; they raise an event where a collision would have occurred.

## Pipeline stages, in order
| Stage | Role |
|---|---|
| `PhysicsInitializeGroup` | ECS components to simulation data |
| `PhysicsCreateBodyPairsGroup` | Broadphase AABB pairs; cheapest place to exclude an interaction |
| `PhysicsCreateContactsGroup` | Narrowphase contacts |
| `PhysicsCreateJacobiansGroup` | Constraint setup; last point before solving |
| `PhysicsSolveAndIntegrateGroup` | Solve and integrate |
| `ExportPhysicsWorld` | Writes back `LocalTransform`/`PhysicsVelocity`; before it, components hold last frame's values |

## Hooks (escalation after filters and `PhysicsCustomTags`)
| Hook | Point |
|---|---|
| Direct `PhysicsWorld` change | After `PhysicsInitializeGroup`, via `GetSingletonRW<PhysicsWorldSingleton>()` and `PhysicsWorldExtensions` (e.g. an impulse) |
| `IBodyPairsJob` | After broadphase: disable/filter interactions before contacts exist |
| `IContactsJob` | After narrowphase: modify normals and distances |
| `IJacobiansJob` | After constraint setup: adjust friction and constraints |

Every hook system needs `[UpdateAfter]`/`[UpdateBefore]` against the pipeline groups and `GetSingletonRW()` access.

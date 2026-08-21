# Queries, Events & Simulation Modification

Sources: [Collision queries](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/collision-queries.html), [Simulation results](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/simulation-results.html), [Modifying simulation behavior](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/simulation-modification.html).
Covers: SKILL.md §4 — **"Pick the query type from the question being asked"**, **"Read collision and trigger events only inside their validity window"**, **"Reach for a pipeline hook only after a filter has been ruled out"**.

## Contents
- [Query types](#query-types)
- [Events](#events)
- [Modifying simulation behaviour](#modifying-simulation-behaviour)

Asking the world a question, reading what the step produced, and overriding
what it would otherwise do. Scheduling every job interface named here belongs
to `unity-job-system-and-burst`.

## Query types

| Query | What it decides | Source |
|---|---|---|
| Ray cast | All or closest intersections along an oriented line segment | [Collision queries](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/collision-queries.html) |
| Collider cast | Sweeps a shape along a path and stops at first contact — the right answer for a swept volume, where a fan of rays is an approximation | [Collision queries](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/collision-queries.html) |
| Collider distance | Closest points between two shapes within a radius | [Collision queries](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/collision-queries.html) |
| Point distance | Nearest surfaces to a point | [Collision queries](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/collision-queries.html) |
| Overlap | Bodies whose bounding boxes intersect a region — a coarse test, not an exact one | [Collision queries](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/collision-queries.html) |
| Target scope | Against one collider when the target is known, or the whole `CollisionWorld` via `PhysicsWorldSingleton`, which uses a bounding-volume tree | [CollisionWorld](https://docs.unity3d.com/Packages/com.unity.physics@6.6/api/Unity.Physics.CollisionWorld.html) |
| Filtering | The preferred, data-driven way to control results — narrowing the query beats discarding hits afterwards | [Collision queries](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/collision-queries.html) |

## Events

| Subject | What it decides | Source |
|---|---|---|
| Direct access | `GetSingleton<SimulationSingleton>().AsSimulation()` exposes the `CollisionEvents` and `TriggerEvents` streams | [SimulationSingleton](https://docs.unity3d.com/Packages/com.unity.physics@6.6/api/Unity.Physics.SimulationSingleton.html) |
| `ICollisionEventsJob` / `ITriggerEventsJob` | The same read as a scheduled job, `Schedule()` serially or `ScheduleParallel()` | [Simulation results](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/simulation-results.html) |
| Validity window | Valid **only** after `PhysicsSimulationGroup` finishes and until it starts again next frame — outside it the streams are stale or empty rather than erroring | [Simulation results](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/simulation-results.html) |
| Triggers | Never physically collide; they raise an event where a collision would otherwise have occurred | [Simulation results](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/simulation-results.html) |

## Modifying simulation behaviour

| Hook | What it decides | Source |
|---|---|---|
| Direct `PhysicsWorld` modification | After `PhysicsInitializeGroup`, via `GetSingletonRW<PhysicsWorldSingleton>()` and `PhysicsWorldExtensions` — applying an impulse, for instance | [Simulation modification](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/simulation-modification.html) |
| `IBodyPairsJob` | After broadphase: disable or filter interactions before contacts exist — the cheapest interception point | [Simulation modification](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/simulation-modification.html) |
| `IContactsJob` | After narrowphase: modify contact normals and distances | [Simulation modification](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/simulation-modification.html) |
| `IJacobiansJob` | After constraint setup: adjust friction and constraints before solving | [Simulation modification](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/simulation-modification.html) |
| Placement | Every interception system needs correct `[UpdateAfter]`/`[UpdateBefore]` against the pipeline groups and `GetSingletonRW()` access | [Simulation modification](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/simulation-modification.html) |
| Custom Physics Body Tags | Recommended for fine-grained filtering of which entities a modification affects — reach here before reaching for interception | [Simulation modification](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/simulation-modification.html) |

**Critical caveat**: queries are documented as belonging inside Burst-compiled
jobs, not main-thread C#. Running one on the main thread works and quietly
gives up both the parallelism and the codegen the design assumes.

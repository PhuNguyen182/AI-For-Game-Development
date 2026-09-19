# DOTS Pillars — Which Package Owns Which Concern

Sources: [ECS packages](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/ecs-packages.html); the dependency claims below are synthesized from that page plus each sibling package's own stated requirements.
Covers: SKILL.md §4 — **"Name the architecture-level decision that approved ECS for this feature"**.

DOTS is several packages, not one; three of them are usable with no entities
involved at all. This file exists to settle, before any modeling starts, which
of the seven owns the concern in front of you — because the most common way
this skill goes wrong is answering a scheduling or compilation question in ECS
terms.

## Independent of ECS

| Package | What it decides | Source |
|---|---|---|
| C# Job System (`unity-job-system-and-burst`) | Schedules `IJob`/`IJobParallelFor` over plain `NativeArray` data with zero entities present — needing jobs is not a reason to adopt ECS | [ECS packages](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/ecs-packages.html) |
| Burst (`unity-burst-compiler`) | Compiles any HPC#-compliant static method or job, ECS or not — `[BurstCompile]` on an `ISystem` follows identical rules to a plain job | [ECS packages](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/ecs-packages.html) |
| Collections (`unity-collections`) | `NativeArray<T>`, `FixedString`, allocator lifetime — works in ordinary MonoBehaviour code | [ECS packages](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/ecs-packages.html) |
| Mathematics (`unity-mathematics`) | `float3`, `quaternion`, `Random`, `noise` — the everyday field types of ECS components, but the type choice is not an ECS decision | [ECS packages](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/ecs-packages.html) |

## Requires ECS to run at all

| Package | What it decides | Source |
|---|---|---|
| Entities — this skill | Data modeling, archetypes, systems, queries, baking, structural-change batching | [Entities Manual](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/index.html) |
| Unity Physics (`unity-physics`) | `PhysicsCollider`/`PhysicsVelocity`/`PhysicsMass`, collider shapes, joints, spatial queries — ordinary ECS components, but which ones to use is that skill's call | synthesized |
| Entities Graphics (`unity-entities-graphics`) | `RenderMeshArray`/`MaterialMeshInfo`, DOTS Instancing compatibility, material overrides — and narrows the adoption gate further to URP Forward+ or HDRP only | synthesized |

## Where the hand-off actually falls

| Situation | Owner | Source |
|---|---|---|
| An `IJobEntity` needs its `JobHandle` chained or its container disposed | `unity-job-system-and-burst` — once scheduled it is an ordinary job | synthesized |
| An `ISystem` is `[BurstCompile]`d and must be verified in the Burst Inspector | `unity-burst-compiler` — identical workflow to a plain job | synthesized |
| A `DynamicBuffer<T>` needs sizing or a `NativeHashMap` feeds a system | `unity-collections` | synthesized |
| An entity should render, collide, or be queried spatially | `unity-entities-graphics` / `unity-physics` | synthesized |

**Critical caveat**: needing multithreading is not a reason to adopt ECS. The
Job System and Burst deliver parallelism and native codegen with no entities
at all, so "we need this on worker threads" resolves to
`unity-job-system-and-burst`, never to this skill.

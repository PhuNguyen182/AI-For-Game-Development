# Relationship to ECS, Jobs, Burst, Collections & Mathematics

Sources: [ECS packages](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/ecs-packages.html); the ownership rows below are synthesized from this skill set's own boundaries.
Covers: SKILL.md §4 — **"Name the ECS-adoption decision this physics work sits on top of"**.

Unity Physics is a specialized simulation layer on top of the DOTS packages,
not a peer of them. This file settles which skill owns a request that touches
physics plus one of its foundations.

## What it requires

| Subject | What it decides | Source |
|---|---|---|
| Entities package | **Required** — `PhysicsWorld` is rebuilt from ECS component data every step, so this skill inherits `unity-ecs-architecture`'s adoption gate and never justifies ECS by itself | [ECS packages](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/ecs-packages.html) |
| Job System, Burst, Collections, Mathematics | Built on all four — the simulation group is Burst-compiled by default and the docs expect queries to run inside Burst jobs | [ECS packages](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/ecs-packages.html) |
| A live `World` | Physics cannot be hosted in `Game.Core.*` the way pure `Unity.Mathematics` code can — the rule decision stays in Core and receives physics output as input | synthesized |

## Who owns what

| Concern | Owner | Source |
|---|---|---|
| Which physics component, collider, joint, query, or hook to use | This skill | synthesized |
| `Baker<T>` mechanics, `SystemGroup` conventions, `EntityCommandBuffer`, blob assets generically | `unity-ecs-architecture` | synthesized |
| Scheduling `ICollisionEventsJob`, `IContactsJob` and the rest — dependencies, `.Complete()`, disposal | `unity-job-system-and-burst` | synthesized |
| Container and allocator choice under event streams and query results | `unity-collections` | synthesized |
| `float3`/`quaternion` type and function choice in every parameter | `unity-mathematics` | synthesized |
| HPC# compliance and `FloatMode` for physics-adjacent jobs | `unity-burst-compiler` | synthesized |
| Client prediction and reconciliation built on this determinism | `netcode-engineer` | synthesized |
| `Rigidbody`, `Collider`, `Physics.Raycast` on ordinary GameObjects | `unity-engineer` | synthesized |

**Critical caveat**: determinism makes this engine attractive for rollback
netcode, and that attraction is where scope creep starts. Determinism is a
property this skill preserves; the protocol built on it is designed elsewhere.

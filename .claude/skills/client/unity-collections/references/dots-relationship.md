# DOTS Relationship — Package Boundaries & Hand-Off

Source: not sourced from a single URL — synthesized from this package's manual content and the boundary each sibling skill declares in its own `description`.
Covers: SKILL.md §4 — **"Decide managed vs. unmanaged deliberately"**, **"If the request's data shape or crossing boundary is unstated, ask before choosing"**.

Settles where this package ends and each neighbouring one begins, which is
what makes the managed-vs-unmanaged decision answerable: unmanaged is only
justified by a boundary something actually crosses. Use it to name the
hand-off explicitly rather than extending guidance into a sibling's territory.

## Package independence

| Claim | What it decides | Source |
|---|---|---|
| Collections is foundational and independent | `NativeArray`/`NativeList` work in plain MonoBehaviour code with no job, no Burst, and no entity involved — reaching for one implies nothing about the other three | synthesized |
| A container is not evidence of DOTS adoption | Choosing an unmanaged container never obliges the project to adopt jobs, Burst, or ECS | synthesized |

## Boundaries with sibling skills

| Neighbour | This skill owns | The neighbour owns | Source |
|---|---|---|---|
| `unity-job-system-and-burst` | Which container, its allocator, its population | Scheduling, `JobHandle` dependency chaining, the routine allocator pick for one scheduled job's data | synthesized |
| `unity-burst-compiler` | That every type here is blittable and unmanaged by construction | Compilation correctness and tuning — HPC# subset, `FloatMode`, intrinsics, AOT settings | synthesized |
| `unity-ecs-architecture` | The container mechanics `DynamicBuffer<T>` and chunk storage are built from | Modeling components, `IBufferElementData`/`DynamicBuffer<T>`, and queries | synthesized |
| `unity-mathematics` | The container that holds the math types, e.g. `NativeArray<float3>` | The vector/matrix/quaternion/`Random`/`noise` types themselves | synthesized |
| `unity-physics` | General blob-asset and `NativeStream` mechanics | `BlobAssetReference<Collider>`, `CollisionEvents`/`TriggerEvents` stream shapes | synthesized |
| `unity-entities-graphics` | General shared-component and container mechanics | `RenderMeshArray`'s internal mesh/material lists | synthesized |

## Deciding managed vs. unmanaged

| Question | Answer it forces | Source |
|---|---|---|
| Does the data cross into a job, a Burst-compiled method, or an ECS component? | No → managed `List<T>`/`Dictionary<TKey,TValue>` is correct and simpler | synthesized |
| Is the boundary stated in the request? | No → ask; guessing picks a container that looks right and is wrong | synthesized |
| Is the container the whole ask, or is a job implied? | A job implied → choose and populate here, then hand scheduling to `unity-job-system-and-burst` | synthesized |

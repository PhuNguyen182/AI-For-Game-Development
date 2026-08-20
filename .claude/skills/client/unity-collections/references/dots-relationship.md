# How Collections Relates to the Rest of DOTS

Covers SKILL.md step 9 and the cross-skill boundary this skill is scoped around. Not sourced from a single URL — synthesized from `unity-ecs-architecture`'s `dots-pillars.md` research and this package's own manual content.

- Collections is a **foundational, independent** package: `NativeArray`/`NativeList`/etc. work in plain MonoBehaviour code with zero jobs, zero Burst, and zero entities involved — reaching for one doesn't imply any of the other three DOTS pieces.
- The C# Job System (`unity-job-system-and-burst`) consumes these containers as job input/output; that skill owns *scheduling* and dependency-chaining, not which container type to pick or how to size/allocate it — that division of labor is this skill's reason to exist separately.
- Burst (`unity-burst-compiler`) compiles code that touches these containers efficiently because every type here is blittable/unmanaged by construction; that skill owns compilation correctness and tuning, not container choice.
- ECS (`unity-ecs-architecture`) builds its own higher-level types on similar ideas — `DynamicBuffer<T>` behaves like a `NativeList<T>` scoped to an entity, and ECS internally uses `Native-`/`Unsafe-` collections for archetype/chunk storage — but modeling a component or buffer is that skill's territory, not this one's.
- `Unity.Mathematics` (`unity-mathematics`) is a separate, sibling foundational package; its vector/matrix/`Random`/`noise` types are commonly stored *inside* the collections covered here (e.g. `NativeArray<float3>`), but the math types themselves are out of this skill's scope.

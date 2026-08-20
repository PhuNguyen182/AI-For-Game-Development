# DOTS Pillars — How ECS, Job System & Burst Relate

Covers SKILL.md step 1 and the cross-skill boundary this whole skill is scoped around.

## Manual
- [ECS packages](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/ecs-packages.html) — Unity's Data-Oriented Technology Stack (DOTS) is made of several independent pieces working together: the **Entities** package (ECS data model — this skill), the **C# Job System** (multithreading — `unity-job-system-and-burst`), the **Burst compiler** (native-quality code generation — `unity-burst-compiler`), plus the Collections and Mathematics packages used by all three.

## The relationship, explicitly
- The Job System and Burst compiler are **independent of ECS** — a project can schedule `IJob`/`IJobFor`/`IJobParallelFor` over plain `NativeArray` data and apply `[BurstCompile]` to it with zero entities, components, or systems involved. Don't assume either one requires ECS.
- ECS's own iteration job types (`IJobEntity`, `IJobChunk`) are built **on top of** the same underlying Job System — once scheduled, they follow the identical `JobHandle`/`.Complete()`/`NativeContainer`-lifetime rules as any other job, covered by `unity-job-system-and-burst`, not restated here.
- Burst compilation of an ECS job or `ISystem` (HPC# subset compliance, `FloatMode`, verifying via the Burst Inspector, AOT settings) follows exactly the same rules as Burst-compiling a plain job — covered by `unity-burst-compiler`, not restated here.
- This skill (`unity-ecs-architecture`) owns only the ECS-specific concerns: how data is modeled as entities/components, how systems are organized and query that data, baking/authoring, and structural-change batching.

---
name: unity-ecs-architecture
description: >
  Technique for the Entities/ECS pillar of Unity DOTS — modeling gameplay data
  as entities/components/archetypes, authoring→baking workflow, system
  design and update-order placement, EntityQuery/SystemAPI.Query/IJobEntity/
  IJobChunk data iteration, batching structural changes via
  EntityCommandBuffer, enableable components, and blob assets. ECS, the C#
  Job System, and the Burst compiler are the three independent pillars of
  DOTS — this skill owns only the ECS pillar. Use this only on top of an
  already-justified decision to model a feature in ECS — per
  `performance-and-algorithms.md`, ECS/Job System/Burst is
  architecture-level, escalation territory for Tech Lead – Performance /
  Technical Architect, not a routine default. Do not use this for job
  scheduling, `JobHandle` dependency chaining, or `NativeContainer` allocator
  lifetime — the Job System operates independently of ECS and that mechanics
  layer is `unity-job-system-and-burst`, even when the job being scheduled is
  an `IJobEntity`/`IJobChunk`. Do not use this for Burst-specific compilation
  tuning (HPC# subset, `FloatMode`, intrinsics, AOT settings, `[NoAlias]`,
  `FunctionPointer<T>`/`SharedStatic<T>`) — Burst also operates independently
  of ECS and that's `unity-burst-compiler`, whether the Burst target is a
  plain job or an ECS system. Do not use this for a GPU-driven visual effect
  — that's `compute-shader-vfx`.
---

# Unity ECS Architecture — Entities, Components, Systems & Queries

Sources: see [references/](references/) for the Unity Manual/Scripting API root links, split by topic — [root-links.md](references/root-links.md), [dots-pillars.md](references/dots-pillars.md), [core-concepts.md](references/core-concepts.md), [component-types.md](references/component-types.md), [systems-and-scheduling.md](references/systems-and-scheduling.md), [queries-and-iteration.md](references/queries-and-iteration.md), [baking-and-authoring.md](references/baking-and-authoring.md), [structural-changes-and-ecb.md](references/structural-changes-and-ecb.md), [blob-assets.md](references/blob-assets.md), [debugging-tools.md](references/debugging-tools.md).

## 1. Objective
Model a feature's gameplay data and logic correctly in ECS — entities/components that map cleanly to archetypes, systems placed in the right update group, queries that read the data efficiently, and structural changes batched rather than scattered — without silently drifting into the Job System's scheduling mechanics or the Burst compiler's tuning concerns, which are separate, independently-usable pillars of DOTS.

## 2. Role
Act as the ECS data/system-architecture specialist inside Tech Lead – Performance's / Technical Architect's escalation territory: given a feature that has already been decided (per `performance-and-algorithms.md`) to warrant ECS, you design its entities, components, archetypes, systems, and queries — you don't make the "should this be ECS" call yourself, and once a query needs to run as a scheduled job or needs Burst tuning, you hand off to the sibling skills instead of re-deriving their mechanics.

## 3. When to invoke this skill
- Modeling a feature's runtime data as entities/components — choosing between `IComponentData` (unmanaged, the default), `ISharedComponentData`, `IBufferElementData`, and enableable components (`IEnableableComponent`).
- Designing the authoring → baking pipeline: authoring `MonoBehaviour` components and their `Baker<T>` classes that convert GameObject-based design-time data into baked entities.
- Choosing between `ISystem` and `SystemBase`, and placing a system correctly in the default system-group hierarchy (`InitializationSystemGroup`/`SimulationSystemGroup`/`PresentationSystemGroup`) or a custom group.
- Writing entity data iteration via `SystemAPI.Query<T>`, `IJobEntity`, or `IJobChunk`, and picking the one that fits the case.
- Batching structural changes (entity creation/destruction, add/remove component, shared-component value changes) through an `EntityCommandBuffer` instead of direct `EntityManager` calls mid-iteration.
- Introducing a `BlobAssetReference<T>` for immutable bulk data referenced by many entities, instead of duplicating the same static data per component instance.
- Diagnosing archetype/chunk fragmentation, or verifying actual entity/system layout via the Entities Hierarchy window / Systems window.
- Negative trigger: scheduling a job, chaining `JobHandle` dependencies, or managing `NativeContainer` allocator lifetime — that's `unity-job-system-and-burst`, even for an `IJobEntity`/`IJobChunk`, since those job types are ordinary Job System jobs underneath.
- Negative trigger: Burst-specific compilation tuning (HPC# subset compliance, `FloatMode`, intrinsics, AOT settings, `[NoAlias]`, `FunctionPointer<T>`/`SharedStatic<T>`) — that's `unity-burst-compiler`, whether the target is a plain job or a Burst-compiled ECS system.
- Negative trigger: no prior architecture decision justifying ECS at all — per `performance-and-algorithms.md` this is escalation territory (Tech Lead – Performance / Technical Architect), not a routine default; don't convert an ordinary small-scale MonoBehaviour-driven feature to ECS "because it's faster" without that justification.
- Negative trigger: the deliverable is a GPU-driven visual effect — that's `compute-shader-vfx`, not this skill.

## 4. How to use this skill
1. **Confirm the prerequisite before modeling a single entity.** State which architecture-level decision (per `performance-and-algorithms.md` and Tech Lead – Performance/Technical Architect) justified using ECS for this specific feature — this skill doesn't re-litigate whether ECS is warranted.
2. **Choose the right component kind deliberately.** Default to unmanaged `IComponentData` — never managed components, which are deprecated, GC-tracked, and unusable in jobs/Burst. Use `ISharedComponentData` only when many entities genuinely share the same value (unique per-entity values fragment chunks). Use `IBufferElementData` for per-entity variable-length data. Use `IEnableableComponent` for state that toggles frequently/unpredictably, instead of add/remove churn that triggers a structural change every toggle.
3. **Design entities/archetypes for query efficiency, not per-instance convenience.** Keep an entity's component set stable where possible — an unstable, highly-varied per-entity component combination fragments archetypes and chunks, hurting both memory layout and query performance.
4. **Author → bake correctly.** Put design-time data on an authoring `MonoBehaviour` and convert it via a `Baker<TAuthoring>`; baking runs only in the Editor, never at runtime — don't try to replicate baking logic as a runtime step.
5. **Choose the system type and placement deliberately.** Prefer `ISystem` (unmanaged, Burst-compilable) over `SystemBase` (managed) when the system doesn't need managed API calls. Place it in the correct default `SystemGroup`, and only add `UpdateBefore`/`UpdateAfter`/`OrderFirst`/`OrderLast` when a real ordering dependency exists — don't reorder speculatively.
6. **Pick the iteration approach that matches the case.** `SystemAPI.Query<T>` foreach for straightforward main-thread iteration; `IJobEntity` for per-entity work that should run as a scheduled job; `IJobChunk` when you need direct per-chunk `NativeArray` access or want to check an optional component once per chunk instead of once per entity. Once you reach for `IJobEntity`/`IJobChunk`, the scheduling/dependency/disposal mechanics are `unity-job-system-and-burst`'s territory, not this skill's — don't re-derive them here.
7. **Batch structural changes through an `EntityCommandBuffer`.** Never call `EntityManager` structural-change APIs directly inside a job or a tight iteration loop — each structural change is a main-thread-only sync point; an ECB consolidates many into one playback.
8. **Use a `BlobAssetReference<T>` for immutable bulk data shared by many entities**, built via `BlobBuilder`, instead of duplicating the same static data per-entity-component-instance.
9. **Don't reach for Aspects (`IAspect`).** They're obsolete and removed as of the Entities 6.x line — use `Component`/`EntityQuery` APIs directly (`SystemAPI.Query<T>`, `IJobEntity`, `IJobChunk`) instead.
10. **Verify with the actual editor tools and a measurement, not by inspection.** Confirm the intended archetype/system layout via the Entities Hierarchy window / Systems window, and confirm any claimed performance win via `unity-profiler-diagnostics` — per the Verification section of `performance-and-algorithms.md`.

## 5. Specific goals / tasks this skill performs
- Modeling entities/components (`IComponentData`/`ISharedComponentData`/`IBufferElementData`/`IEnableableComponent`) for an already-justified ECS feature.
- Designing the authoring-component → `Baker<T>` → baked-entity pipeline.
- Choosing system type (`ISystem`/`SystemBase`) and correct `SystemGroup` placement/update order.
- Designing `EntityQuery`-based data access via `SystemAPI.Query<T>`, `IJobEntity`, or `IJobChunk`.
- Batching structural changes via `EntityCommandBuffer` instead of direct mid-loop `EntityManager` calls.
- Introducing `BlobAssetReference<T>` for immutable shared bulk data.
- Diagnosing archetype/chunk fragmentation and verifying entity/system layout via the Entities Hierarchy/Systems windows.
- Out of scope: deciding *whether* a feature warrants ECS at all (`performance-and-algorithms.md`/Tech Lead – Performance/Technical Architect's call); scheduling jobs, `JobHandle` dependency chains, `NativeContainer` allocator lifetime, even for `IJobEntity`/`IJobChunk` (`unity-job-system-and-burst`); Burst-specific compilation tuning for any Burst-compiled job or system (`unity-burst-compiler`); the initial Profiler measurement that justifies this work (`unity-profiler-diagnostics`); GPU-driven visual effects (`compute-shader-vfx`).

## 6. Output format
```
## ECS Architecture Work — <feature/system name>
- Prerequisite decision: <which already-approved ECS adoption this sits on top of>
- Components: <IComponentData/ISharedComponentData/IBufferElementData/IEnableableComponent — which, and why>
- Authoring/baking: <authoring MonoBehaviour + Baker<T>, or "none — pure runtime entities">
- System(s): <ISystem/SystemBase, SystemGroup placement, ordering constraints if any>
- Data iteration: <SystemAPI.Query<T> / IJobEntity / IJobChunk — rationale>
- Structural changes: <EntityCommandBuffer usage, or "none needed">
- Blob assets: <yes/no — what data, why>
- Verified via: <Entities Hierarchy window / Systems window — what was confirmed>
- Before/after measurement: <from unity-profiler-diagnostics, if a performance claim is made>
- Known limitations: <...>
```

## 7. Examples
**Example 1**
- Input: Tech Lead – Performance approved converting the game's large-scale bullet/projectile system to ECS after a `unity-profiler-diagnostics` capture showed thousands of per-frame bullet updates dominating main-thread time and being fully data-parallel.
- Output: modeled `BulletData` (`IComponentData`, unmanaged: position, velocity, lifetime) and an authoring `MonoBehaviour` + `Baker<BulletAuthoring>` for design-time bullet prefabs; wrote an `IJobEntity` job (handed to `unity-job-system-and-burst` for scheduling/dependency wiring and `unity-burst-compiler` for `[BurstCompile]` verification) that advances position and decrements lifetime; used an `EntityCommandBuffer` to destroy expired bullets in a single batched playback instead of calling `EntityManager.DestroyEntity` per-entity mid-iteration; confirmed the system's placement in `SimulationSystemGroup` via the Systems window and the resulting archetype via the Entities Hierarchy window; re-measured in `unity-profiler-diagnostics` to confirm the drop the original approval was based on.

**Example 2**
- Input: "Can you convert the player's small inventory panel (a dozen item slots) to ECS since ECS is faster?" — no architecture-level justification, and the data set is tiny.
- Output: declined — per `performance-and-algorithms.md`'s escalation gate and KISS/YAGNI in `coding-principles.md`, a dozen-item inventory doesn't need archetype-based storage or query iteration; recommended keeping it as ordinary Shared Core state with normal MonoBehaviour composition, and reported that ECS's added architectural complexity (baking pipeline, system-group placement, query design) isn't justified here.

## 8. Edge cases & guardrails
- Never introduce ECS without a prior architecture-level decision — this is escalation territory per `performance-and-algorithms.md`, not a routine default, exactly like Job System/Burst.
- Don't use managed components (`IComponentData` on a class) — they're deprecated; default to unmanaged components.
- Don't use Aspects (`IAspect`) — obsolete and removed as of Entities 6.x; use `Component`/`EntityQuery` APIs directly instead.
- Never call `EntityManager` structural-change APIs directly inside a job or a tight iteration loop — always batch through an `EntityCommandBuffer`; a structural change is a main-thread-only sync point.
- Don't assume `IJobEntity`/`IJobChunk` scheduling differs from a plain Job System job — the same `JobHandle`/`.Complete()`/disposal rules from `unity-job-system-and-burst` apply unchanged; this skill doesn't restate them.
- Don't assume an ECS job/system is Burst-compiled just because it's `IJobEntity`/`ISystem` — verify via `unity-burst-compiler`'s workflow (Burst Inspector) exactly as for a plain job.
- Watch for archetype/chunk fragmentation — giving many entities unique shared-component values, or an unstable per-entity component set, fragments chunks and hurts both memory and query performance.
- Keep the World/SystemGroup topology deliberate — don't create extra Worlds or override the default update order without a stated reason.

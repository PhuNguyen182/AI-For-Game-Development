---
name: unity-ecs-architecture
description: >
  Technique for the Entities/ECS pillar of Unity DOTS: modeling data as
  entities and `IComponentData`, `ISharedComponentData`, `IBufferElementData`,
  `IEnableableComponent`; archetype and 16 KiB chunk layout; authoring
  `MonoBehaviour` plus `Baker<T>` baking; `ISystem` versus `SystemBase` and
  `SystemGroup` update order; `SystemAPI.Query`, `IJobEntity`, `IJobChunk`
  iteration; `EntityCommandBuffer` structural batching; `BlobAssetReference<T>`.
  Use when a feature already approved for ECS needs its entity, system, or query
  layout designed or diagnosed.
  Not for: job scheduling, `JobHandle` chains, allocator lifetime
  (`unity-job-system-and-burst`); HPC# subset, `FloatMode`, intrinsics, AOT
  (`unity-burst-compiler`); container choice (`unity-collections`);
  `float3`/`quaternion` maths (`unity-mathematics`); `PhysicsCollider`, colliders,
  joints (`unity-physics`); `RenderMeshArray`, DOTS Instancing
  (`unity-entities-graphics`); GPU-driven effects (`compute-shader-vfx`); whether
  ECS is warranted at all (`tech-lead-performance`).
---

# Unity ECS Architecture — Entities, Components, Systems & Queries

## Bundled resources

### References
Read-only context, loaded on demand so SKILL.md itself stays short.

| File | Contents | Read when |
|---|---|---|
| [root-links.md](references/root-links.md) | Entities package manual/API roots and the version pin | Starting any task here, or checking which package version the docs describe |
| [dots-pillars.md](references/dots-pillars.md) | Which DOTS package owns which concern, and what depends on ECS | A request mixes ECS with jobs, Burst, physics, or rendering and the boundary must be settled first |
| [core-concepts.md](references/core-concepts.md) | Entity, World, archetype, chunk, structural change | Modeling a feature's data for the first time, or reasoning about chunk layout |
| [component-types.md](references/component-types.md) | The five component kinds and their storage consequences | Choosing how one specific value should be stored on an entity |
| [systems-and-scheduling.md](references/systems-and-scheduling.md) | `ISystem`/`SystemBase`, `SystemGroup` order, `SystemAPI` | Placing a system, or reaching the point where iteration becomes a job |
| [queries-and-iteration.md](references/queries-and-iteration.md) | `SystemAPI.Query`, `IJobEntity`, `IJobChunk`, `EntityQuery` | Deciding which of the three iteration forms a loop should take |
| [baking-and-authoring.md](references/baking-and-authoring.md) | Baking phases and the `Baker<TAuthoring>` contract | Design-time GameObject data has to reach entities |
| [structural-changes-and-ecb.md](references/structural-changes-and-ecb.md) | Sync points and `EntityCommandBuffer` recording/playback | Entities are created or destroyed, or components added or removed, during iteration |
| [blob-assets.md](references/blob-assets.md) | `BlobBuilder` and `BlobAssetReference<T>` constraints | The same immutable table would otherwise be duplicated per entity |
| [debugging-tools.md](references/debugging-tools.md) | Entities Hierarchy and Systems windows | The runtime layout must be confirmed against what the code intended |

## 1. Objective
Model a feature's data and logic in ECS so the result is what was actually intended — archetypes that stay dense in their chunks, systems that update in a defensible order, queries that read only what they need, and structural changes batched into one playback instead of scattered sync points that stall every running job. It prevents the failures that survive compilation: silently fragmented chunks, stale entity data from broken incremental baking, dangling component handles after a structural change, nondeterministic parallel command-buffer playback, and game rules quietly reimplemented inside `OnUpdate` instead of called from Shared Core.

## 2. Role
Act as the ECS data- and system-architecture specialist for the client track — the tool reached for once Tech Lead – Performance or Technical Architect has already approved modeling a feature in ECS, and its entities, components, systems, and queries have to be designed or diagnosed. You design an approved adoption; you never grant one, and you hand scheduling and compilation concerns to the sibling pillars rather than re-deriving them.

## 3. When to invoke this skill
- Deciding how a feature's runtime values are stored on entities — `IComponentData`, `ISharedComponentData`, `IBufferElementData`, or `IEnableableComponent`.
- Designing the authoring `MonoBehaviour` → `Baker<TAuthoring>` → baked-entity pipeline for design-time data.
- Choosing `ISystem` versus `SystemBase` and placing a system inside `InitializationSystemGroup`, `SimulationSystemGroup`, `PresentationSystemGroup`, or a custom group.
- Writing entity iteration with `SystemAPI.Query<T>`, `IJobEntity`, or `IJobChunk`, and picking which of the three fits.
- A reported symptom of ECS layout gone wrong: entities per chunk dropping, a query walking far more chunks than expected, entity data that is correct in a fresh build but stale in the Editor, or entities that appear one frame late.
- Introducing `BlobAssetReference<T>` for immutable bulk data referenced by many entities.
- Negative trigger: scheduling a job, chaining `JobHandle` dependencies, or managing `NativeContainer` allocator lifetime — that is `unity-job-system-and-burst`, unchanged for `IJobEntity`/`IJobChunk`, which are ordinary Job System jobs underneath.
- Negative trigger: HPC# subset compliance, `FloatMode`, intrinsics, AOT settings, `[NoAlias]`, `FunctionPointer<T>` — that is `unity-burst-compiler`, whether the Burst target is a plain job or an `ISystem`.
- Negative trigger: choosing a container or allocator for data feeding a system — that is `unity-collections`; this skill decides only how data is modeled as components and buffers.
- Negative trigger: choosing `Unity.Mathematics` types or functions — that is `unity-mathematics`, even though `float3`/`quaternion` are the everyday component field types.
- Negative trigger: `PhysicsCollider`/`PhysicsVelocity`/`PhysicsMass`, collider shapes, joints, or spatial queries — that is `unity-physics`, a specialist built on this skill's mechanics rather than a replacement for them.
- Negative trigger: `RenderMeshArray`/`MaterialMeshInfo`, DOTS Instancing shader compatibility, material overrides, or Companion Components — that is `unity-entities-graphics`.
- Negative trigger: a GPU-driven visual effect — that is `compute-shader-vfx`.
- Negative trigger: no prior decision justifying ECS for this feature — that call belongs to `tech-lead-performance`; converting a small MonoBehaviour feature "because ECS is faster" is the escalation `performance-and-algorithms.md` forbids skipping.

## 4. How to use this skill
1. **Name the architecture-level decision that approved ECS for this feature** — per `performance-and-algorithms.md`'s Multithreading section this is escalation territory, so if no such decision exists, stop and route to `tech-lead-performance` instead of designing. [dots-pillars.md](references/dots-pillars.md) settles which sibling package owns each adjacent concern, and [root-links.md](references/root-links.md) pins the package version every API below describes.
2. **Keep the game rule in `Game.Core.*` and only the iteration in the system** — per `coding-principles.md`'s Shared Core integrity section. `Unity.Entities` is a Unity dependency, so a formula rewritten inside `OnUpdate` is a second implementation of a Core rule, not a port of it; the system reads components, calls the pure Core function, and writes the result back.
3. **Model entities and archetypes before naming a single system**, per [core-concepts.md](references/core-concepts.md) — an entity is an ID, the archetype is the component set, and the archetype is what queries actually match; deciding systems first produces component sets shaped by code structure rather than by access pattern.
4. **Choose each component kind from how its value changes, not from what it holds**, per [component-types.md](references/component-types.md) — unmanaged `IComponentData` by default; `ISharedComponentData` only when many entities genuinely share one value, since unique values fragment chunks; `IBufferElementData` for variable-length per-entity data; `IEnableableComponent` for state that toggles often, which avoids a structural change per toggle.
5. **Budget the archetype against the 16 KiB chunk** — entities per chunk is that fixed budget divided by the archetype's per-entity size, so every field added to a hot archetype means fewer entities per chunk and more chunks walked per query. Split rarely-read data into a separate component rather than widening the one the hot query touches.
6. **Read authoring data through the `Baker<T>` dependency APIs, never off the authoring object directly**, per [baking-and-authoring.md](references/baking-and-authoring.md) — `GetComponent` inside a Baker registers an incremental-baking dependency; bypassing it means the entity is not re-baked when that value changes, which shows up as data that is stale in the Editor and correct in a clean build.
7. **Prefer `ISystem` in an existing `SystemGroup`**, per [systems-and-scheduling.md](references/systems-and-scheduling.md) — `SystemBase` is managed and not Burst-compilable, so reach for it only when a managed API is genuinely required. Add `UpdateBefore`/`UpdateAfter` only for a real data dependency; speculative ordering is invisible coupling.
8. **Pick the iteration form by what the loop needs per chunk**, per [queries-and-iteration.md](references/queries-and-iteration.md) — `SystemAPI.Query<T>` for main-thread iteration, `IJobEntity` for per-entity work that should be scheduled, `IJobChunk` when the loop needs raw per-chunk `NativeArray` access or an optional-component check once per chunk instead of once per entity.
9. **Batch every structural change through an `EntityCommandBuffer`**, per [structural-changes-and-ecb.md](references/structural-changes-and-ecb.md) — a direct `EntityManager` structural change is a main-thread sync point that completes every job which could touch the affected data, not just the calling one, so a per-entity call inside a loop serializes the whole frame.
10. **Give every parallel `EntityCommandBuffer` write an explicit sort key** — `AsParallelWriter()` playback order follows that key, and without a stable one (the entity-in-query index) the same inputs produce different results per run, breaking the determinism `coding-principles.md`'s Shared Core integrity section requires for prediction and server authority to agree.
11. **Re-acquire every component handle after a structural change** — a `DynamicBuffer<T>`, `ComponentLookup<T>`, or `RefRW<T>` obtained before an add, remove, or destroy points into chunk memory that has since moved; the stale view compiles and reads plausible garbage.
12. **Move immutable bulk data behind a `BlobAssetReference<T>`**, per [blob-assets.md](references/blob-assets.md) — built with `BlobBuilder` and containing no managed data, so one copy is shared by reference instead of duplicated into every component instance.
13. **Confirm the built layout in the Entities Hierarchy and Systems windows before claiming it**, per [debugging-tools.md](references/debugging-tools.md) — archetype and update order are emergent, not declared, and any performance claim additionally needs a before/after capture from `unity-profiler-diagnostics`, per `performance-and-algorithms.md`'s Verification section.
14. **State the assumption in the handoff when the approved scope doesn't settle a modeling choice** — if it is unclear whether a value is shared across entities or unique per entity, model it as unique (`IComponentData`), say so explicitly, and flag it; never silently pick `ISharedComponentData`, whose cost only appears later as chunk fragmentation.

## 5. Specific goals / tasks this skill performs
- Component and archetype design for an already-approved ECS feature, including the chunk-density trade-off behind each choice.
- The authoring-component → `Baker<T>` → baked-entity pipeline, with incremental-baking dependencies declared correctly.
- System type selection and `SystemGroup` placement, with ordering attributes only where a data dependency justifies them.
- Query and iteration design across `SystemAPI.Query<T>`, `IJobEntity`, and `IJobChunk`.
- `EntityCommandBuffer` batching, including deterministic sort keys for parallel writes.
- `BlobAssetReference<T>` introduction for immutable shared bulk data.
- Diagnosis of chunk fragmentation, stale baked data, and post-structural-change handle invalidation.
- Out of scope: whether a feature warrants ECS at all (`tech-lead-performance`); job scheduling and allocator lifetime (`unity-job-system-and-burst`); Burst compilation tuning (`unity-burst-compiler`); container selection (`unity-collections`); maths types (`unity-mathematics`); physics components (`unity-physics`); rendering components (`unity-entities-graphics`); the Profiler capture that justifies the work (`unity-profiler-diagnostics`); GPU-driven effects (`compute-shader-vfx`).

## 6. Output format
```
## ECS Architecture Work — <feature/system name>
- Approved by: <the architecture decision this sits on top of, and who made it>
- Core boundary: <which rule logic stayed in Game.Core.*, and what the system calls>
- Components: <kind per value — and the chunk-density consequence of each>
- Authoring/baking: <authoring MonoBehaviour + Baker<T>, or "none — runtime-created entities">
- System(s): <ISystem/SystemBase, group placement, ordering constraints and their data reason>
- Iteration: <SystemAPI.Query / IJobEntity / IJobChunk — what decided it>
- Structural changes: <ECB usage and sort key, or "none needed">
- Blob assets: <what data, why — or "none">
- Verified via: <Entities Hierarchy / Systems window — what was confirmed>
- Measurement: <before/after from unity-profiler-diagnostics, or "no performance claim made">
- Layer: <Game.Core.* rule modules / Game.Client.* systems and components>
- Known limitations: <...>
```

**Extended report — emit ONLY when the requester asks for it.** It replaces the one-line `Known limitations` above with all three fields:
```
- Known limitations: <what the delivered solution does not cover>
- Latent concerns: <failure modes not yet triggered: assumptions that hold only under current conditions, thresholds not yet reached, trade-offs knowingly deferred>
- Future remediation: <the concrete fix for each concern above, each with the condition that should trigger it>
```

## 7. Examples
**Example 1**
- Input: Tech Lead – Performance approved moving the projectile system to ECS after a Profiler capture showed several thousand per-frame bullet updates dominating main-thread time.
- Output: `BulletData` as unmanaged `IComponentData` (position, velocity, lifetime) with the damage-on-hit formula left in `Game.Core.Combat` and called from the system, per Shared Core integrity; damage falloff moved into a `BlobAssetReference<DamageCurve>` shared by every bullet instead of copied per entity; an authoring `MonoBehaviour` + `Baker<BulletAuthoring>` reading its prefab reference through `GetEntity` so incremental baking tracks it; an `IJobEntity` advancing motion, handed to `unity-job-system-and-burst` for scheduling and `unity-burst-compiler` for `[BurstCompile]` verification; expiry routed through an `EntityCommandBuffer.ParallelWriter` keyed on the entity-in-query index so playback order is reproducible; archetype confirmed in the Entities Hierarchy window and the frame-time drop re-measured in `unity-profiler-diagnostics`.

**Example 2**
- Input: "Give each enemy an `ISharedComponentData` holding its faction ID and current target entity, so we can filter queries by faction cheaply."
- Output: declined as written — faction ID alone is a good shared component, but folding the current target into it makes the value effectively unique per entity, and shared-component values partition chunks, so a per-entity target would fragment the archetype into roughly one chunk per enemy and destroy the density the whole model depends on. Split it: faction ID stays `ISharedComponentData`, the target becomes an ordinary `IComponentData`, per §4's component-kind criterion.

**Example 3**
- Input: enemies spawned by a system appear correctly in a player build but keep their old spawn count in the Editor until the scene is reopened.
- Output: traced to a `Baker<SpawnerAuthoring>` reading a second authoring component through `authoring.GetComponent<T>()` directly instead of the Baker's own `GetComponent`, so incremental baking never registered the dependency and never re-baked on change; corrected to the Baker API per §4's authoring-data step, which restored Editor and build agreement without touching the runtime system.

## 8. Edge cases & guardrails
- Never introduce ECS without a prior architecture-level decision — per `performance-and-algorithms.md` this is escalation territory, and an unapproved conversion buys a baking pipeline and system-group topology the feature's scale may never repay.
- Never reimplement a Shared Core rule inside a system — `Unity.Entities` cannot be referenced from `Game.Core.*`, so the duplicate silently diverges from the authority the server validates against.
- Never call `EntityManager` structural-change APIs inside a job or an iteration loop — the sync point completes every job that could touch that data, converting parallel work back into serial work.
- Never use a component handle acquired before a structural change — chunk memory moves, and the stale view reads plausible-looking garbage rather than throwing.
- Never leave a parallel `EntityCommandBuffer` write without a deterministic sort key — nondeterministic playback breaks prediction and server reconciliation, and reproduces only intermittently.
- Never use managed `IComponentData` classes or Aspects (`IAspect`) — managed components are deprecated and unusable in jobs or Burst; `IAspect` is obsolete and removed as of the Entities 6.x line, replaced by direct `SystemAPI.Query<T>`/`IJobEntity`/`IJobChunk` access.
- Never create extra Worlds or override default update order without a stated reason — both are invisible in the code that depends on them and surface as ordering bugs nobody can localize.
- If it is ambiguous whether a value is shared or per-entity, model it per-entity and flag the assumption — the chunk-fragmentation cost of guessing wrong appears long after the choice.

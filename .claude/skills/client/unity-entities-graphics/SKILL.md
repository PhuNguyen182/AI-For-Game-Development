---
name: unity-entities-graphics
description: >
  Technique for `com.unity.entities.graphics` — the package that renders ECS
  entities by bridging `Unity.Entities` data to Unity's existing SRP
  rendering architecture via `BatchRendererGroup`. Covers the baked/runtime
  rendering component set (`RenderMeshArray`, `MaterialMeshInfo`,
  `RenderMeshDescription`, `RenderBounds`, `RenderMeshUnmanaged`), the
  `RenderMeshUtility.AddComponents` runtime-creation API, DOTS Instancing
  shader compatibility, material property overrides (via C#/Burst or a
  Material Override Asset), Companion Components for non-ECS-convertible
  MonoBehaviours (`Light`, `ParticleSystem`, `VisualEffect`, etc.),
  compute-shader-based mesh deformations (skinning/blend shapes), and the
  package's own performance-measurement/known-issues guidance. Entities
  Graphics only supports URP (Forward+ only) and HDRP on Unity 2022 LTS+ —
  it does not support the Built-in Render Pipeline at all. Do not use this
  for the initial URP-vs-HDRP pipeline decision — that's
  `render-pipeline-urp-hdrp`. Do not use this for URP's own systems (Renderer
  Features, rendering paths, 2D Renderer, camera stacking) or HDRP's own
  systems (Frame Settings, Volumes, Custom Pass, Diffusion Profiles, APV, ray
  tracing) once the pipeline is confirmed — that's `unity-urp-rendering` /
  `unity-hdrp-rendering`; this skill only owns how ECS entities get fed into
  whichever pipeline is active. Do not use this for Shader Graph node
  logic/HLSL content itself — that's `shader-authoring`, even though this
  skill decides whether a shader must be DOTS Instancing compatible and which
  properties need "Hybrid Per Instance" declared. Do not use this to model
  ECS entities/components/systems in general, or the authoring→baking
  pipeline for non-rendering data — that's `unity-ecs-architecture`; this
  skill is only invoked once ECS is an already-approved architecture
  decision, the same escalation gate `unity-ecs-architecture` and
  `unity-physics` sit on. Do not use this for job scheduling, `JobHandle`
  dependencies, or `NativeContainer` allocator lifetime for a Burst system
  that updates material-override components — that's
  `unity-job-system-and-burst`. Do not use this for Burst compilation tuning
  itself — that's `unity-burst-compiler`, even though every material-override
  system here is expected to be Burst-compiled. Do not use this for
  `Unity.Mathematics` type choice — that's `unity-mathematics`, even though
  override components are commonly `float4`-typed.
---

# Unity Entities Graphics — Rendering ECS Entities via BatchRendererGroup

Sources: see [references/](references/) for the Unity Manual/Scripting API root links, split by topic — [root-links.md](references/root-links.md), [overview-and-setup.md](references/overview-and-setup.md), [rendering-components.md](references/rendering-components.md), [dots-instancing-and-material-overrides.md](references/dots-instancing-and-material-overrides.md), [companion-components.md](references/companion-components.md), [batch-renderer-group.md](references/batch-renderer-group.md), [mesh-deformations.md](references/mesh-deformations.md), [runtime-creation-and-performance.md](references/runtime-creation-and-performance.md), [dots-relationship.md](references/dots-relationship.md).

## 1. Objective
Get ECS entities rendering correctly through URP/HDRP — the right rendering component set, DOTS Instancing-compatible shaders, correctly scoped material overrides, deliberate Companion Component usage, and honest performance/known-issue disclosure — without drifting into URP/HDRP's own pipeline configuration, Shader Graph node authoring, or general ECS data modeling, which are sibling skills' territory.

## 2. Role
Act as the Entities Graphics specialist inside an already-ECS project: given entities that need to render (via baking or runtime creation), you choose the correct rendering component set, confirm shader/material compatibility, wire material overrides the right way, and decide when a Companion Component or the deformation system is actually warranted — you don't configure URP/HDRP's own systems and you don't author shader node graphs yourself.

## 3. When to invoke this skill
- Confirming the project's render pipeline/Unity version actually supports Entities Graphics (URP Forward+ or HDRP, Unity 2022 LTS+, linear color space; **not** Built-in, **not** URP Forward/Deferred, **not** Web platforms) before any entity-rendering work starts.
- Choosing/inspecting the baked rendering component set an entity needs (`RenderMeshArray`, `MaterialMeshInfo`, `RenderMeshDescription`, `RenderBounds`, `RenderMeshUnmanaged`) versus what baking already produces automatically from `MeshRenderer`/`MeshFilter`/`LODGroup`.
- Verifying a shader is DOTS Instancing compatible before it's used on an entity — built-in URP/HDRP shaders qualify automatically; a custom Shader Graph or hand-written shader needs explicit work.
- Setting up material property overrides — deciding between the C#/Burst `IComponentData` + `[MaterialProperty]` approach and a no-code Material Override Asset, and marking the right Shader Graph properties "Hybrid Per Instance."
- Deciding whether a MonoBehaviour-only component (`Light`, `ReflectionProbe`, `ParticleSystem`, `VisualEffect`, HDRP `DecalProjector`/`LocalVolumetricFog`, etc.) should ride along as a Companion Component, and disclosing the managed-code/main-thread-only cost that comes with it.
- Diagnosing a rendering/batching problem by reasoning about `BatchRendererGroup` behavior (draw-call batching, why a batch fragmented) without needing to call its API directly.
- Setting up the experimental compute-shader mesh deformation system (Skin Matrix/Blend Shape Weight components + a "Compute Deformation"-node Shader Graph) for skinned/blend-shaped entities, with its documented limitations disclosed up front.
- Creating renderable entities at runtime via `RenderMeshUtility.AddComponents`, and structuring it as "build one prototype entity, then `Instantiate` many copies" rather than calling `AddComponents` per spawn.
- Measuring/reporting Entities Graphics-specific rendering performance (instances-per-draw-call via FrameDebugger's "Hybrid Batch Groups," `EntitiesGraphicsStatsDrawer`, Profiler markers) or disclosing a documented known issue (subscene lightmap limits, shader-stripping build-time/memory cost, Companion Component preview gaps) that a symptom matches.
- Negative trigger: deciding *whether* the project should be on URP or HDRP at all — that's `render-pipeline-urp-hdrp`.
- Negative trigger: configuring URP's own systems (Renderer Features, rendering path choice, 2D Renderer, camera stacking, URP Asset quality settings) or HDRP's own systems (Frame Settings, the Volume system, Custom Pass Volumes, Diffusion Profiles, Adaptive Probe Volumes, ray/path tracing) — that's `unity-urp-rendering` / `unity-hdrp-rendering`, even when the entity being rendered depends on those settings being correct (e.g. URP must be on Forward+).
- Negative trigger: writing the actual Shader Graph node logic or hand-written HLSL/ShaderLab — that's `shader-authoring`; this skill only decides DOTS Instancing compatibility and which properties need "Hybrid Per Instance," not the shading model itself.
- Negative trigger: no prior ECS-adoption architecture decision, or general non-rendering ECS component/system/query/baking design — that's `unity-ecs-architecture`.
- Negative trigger: scheduling the Burst system that updates a material-override component, chaining `JobHandle` dependencies, or `NativeContainer` allocator lifetime — that's `unity-job-system-and-burst`.
- Negative trigger: Burst compilation tuning itself (HPC# subset, `FloatMode`, AOT settings) — that's `unity-burst-compiler`.
- Negative trigger: choosing `Unity.Mathematics` vector/quaternion types — that's `unity-mathematics`, even though override components are commonly `float4`-typed.

## 4. How to use this skill
1. **Confirm the ECS-adoption prerequisite first**, per `unity-ecs-architecture`'s own gate — this skill assumes entities already exist or are being modeled; it doesn't make the "should this be ECS" call.
2. **Confirm platform/pipeline support before anything else.** Entities Graphics requires Unity 2022 LTS+ and either URP (Forward+ path only) or HDRP — never the Built-in Render Pipeline, never Web platforms, and check the per-platform matrix (e.g. Android is URP-only) before assuming a target device is covered.
3. **Let baking do the default work.** For design-time content, author with ordinary `MeshRenderer`/`MeshFilter`/`LODGroup` on a sub-scene GameObject and let baking produce `RenderMeshArray`/`MaterialMeshInfo`/`RenderBounds`/`LocalToWorld` automatically — don't hand-assemble the rendering component set unless there's a genuine runtime-creation need.
4. **For runtime entity creation, use `RenderMeshUtility.AddComponents` once, then `Instantiate`.** Build a single prototype entity with the full rendering component set, then clone it via `Instantiate` (in a Burst job with `EntityCommandBuffer.ParallelWriter` for bulk spawns) and update only what varies (transform, per-instance material properties) via `SetComponent` — repeatedly calling `AddComponents` per spawn is the documented anti-pattern.
5. **Verify shader DOTS Instancing compatibility before assuming a custom shader will render.** Built-in URP/HDRP shaders already qualify; a custom Shader Graph needs its exposed properties handled correctly, and a hand-written shader needs to follow the sample DOTS-instancing shader's pattern — check `dots-instancing-and-material-overrides.md` rather than assuming.
6. **Choose the material-override mechanism by who needs to touch it.** A designer-facing, no-code need → Material Override Asset (`Assets > Create > Shader > Material Override Asset`, "Hybrid Per Instance" declaration, per-GameObject or per-asset editing). A runtime/animated/systematic need → `[MaterialProperty("_PropName")] IComponentData` struct + a Burst system writing it via `SystemAPI.Query<RefRW<T>>()` — hand the actual scheduling/Burst tuning to the sibling skills once the component shape is decided.
7. **Reach for a Companion Component only when the MonoBehaviour genuinely can't be modeled as ECS data** (e.g. `Light`, `ParticleSystem`, `VisualEffect`, HDRP-specific volumetric/decal components) — disclose upfront that it costs managed-code, main-thread-only access (`foreach`, never a Burst job) and that transform hierarchy isn't preserved (it becomes a root GameObject); anything not on the supported list gets silently stripped, so verify the target component is actually supported before relying on it.
8. **Treat mesh deformation as an explicit, disclosed trade-off, not a default.** It's experimental, compute-shader-only (vertex-shader skinning won't be supported going forward), has no frustum/occlusion culling, no VFX Graph integration, and is missing standard Skinned Mesh Renderer features (cloth, bake-mesh) — confirm the Tech Spec actually needs it before setting up "Compute Deformation" Shader Graph nodes and Skin Matrix/Blend Shape Weight components.
9. **Measure batching health with the package's own tools**, not guesswork — FrameDebugger's Hybrid Batch Groups and instances-per-draw-call ratio, `EntitiesGraphicsStatsDrawer` (Editor-only overlay), and Profiler markers (`SRPBRender.ApplyShader`, `BatchRendererGroup` operations) — and disclose that Entities Graphics can be *slower* than plain GameObject rendering below a certain object count, since batch-creation overhead is real.
10. **State hand-offs explicitly.** Pipeline choice → `render-pipeline-urp-hdrp`; URP/HDRP system configuration → `unity-urp-rendering`/`unity-hdrp-rendering`; shader node content → `shader-authoring`; general ECS design → `unity-ecs-architecture`; job scheduling → `unity-job-system-and-burst`; Burst tuning → `unity-burst-compiler`; math types → `unity-mathematics`.

## 5. Specific goals / tasks this skill performs
- Confirming platform/pipeline/version support for Entities Graphics before entity-rendering work starts.
- Choosing/verifying the baked or runtime rendering component set for an entity.
- Verifying/establishing DOTS Instancing shader compatibility for custom shaders.
- Setting up material property overrides via C#/Burst (`[MaterialProperty]`) or a Material Override Asset, choosing between them deliberately.
- Deciding when a Companion Component is warranted and disclosing its managed-code/main-thread cost.
- Structuring runtime entity creation via `RenderMeshUtility.AddComponents` + `Instantiate` rather than a per-spawn `AddComponents` call.
- Setting up and scoping compute-shader mesh deformation (skinning/blend shapes) with its documented limitations disclosed.
- Measuring batching efficiency and diagnosing rendering/performance issues using the package's own tools, and cross-checking symptoms against documented known issues.
- Out of scope: the URP-vs-HDRP decision (`render-pipeline-urp-hdrp`); URP/HDRP's own system configuration (`unity-urp-rendering`/`unity-hdrp-rendering`); Shader Graph node/HLSL content (`shader-authoring`); general non-rendering ECS design (`unity-ecs-architecture`); job scheduling (`unity-job-system-and-burst`); Burst tuning (`unity-burst-compiler`); `Unity.Mathematics` type choice (`unity-mathematics`).

## 6. Output format
```
## Entities Graphics Work — <feature/system name>
- ECS-adoption prerequisite: <which architecture decision this sits on top of>
- Platform/pipeline confirmed: <URP Forward+ / HDRP, Unity version, target platforms checked against the feature matrix>
- Rendering component set: <baked automatically / RenderMeshUtility.AddComponents — which components>
- Shader DOTS Instancing compatibility: <built-in pipeline shader / custom Shader Graph with Hybrid Per Instance / hand-written — confirmed how>
- Material override mechanism: <C#/Burst IComponentData / Material Override Asset / none> — rationale
- Companion Components used: <yes/no — which, cost disclosed>
- Mesh deformation used: <yes/no — justification if yes, limitations disclosed>
- Runtime creation pattern: <prototype + Instantiate / baked only / not applicable>
- Performance verified via: <FrameDebugger Hybrid Batch Groups / EntitiesGraphicsStatsDrawer / Profiler markers — or "not applicable">
- Hand-off: <pipeline config / shader content / ECS design / job scheduling / Burst tuning / math types, if applicable>
- Known limitations: <...>
```

## 7. Examples
**Example 1**
- Input: a large-scale crowd system (already approved for ECS per `unity-ecs-architecture`) needs thousands of instanced NPC entities spawned at runtime, each with a random tint color, rendering through URP.
- Output: confirmed URP is on Forward+ (per `unity-urp-rendering`'s Asset settings) since Entities Graphics doesn't support any other URP path; built one prototype entity via `RenderMeshUtility.AddComponents` with a URP Lit shader (already DOTS Instancing compatible, no extra work needed); added a `[MaterialProperty("_BaseColor")] struct TintColor : IComponentData { float4 Value; }` and a Burst system writing a random per-entity tint (handed job scheduling to `unity-job-system-and-burst` and Burst tuning to `unity-burst-compiler`, math type `float4` per `unity-mathematics`); spawned via `Instantiate` in a parallel job rather than calling `AddComponents` per NPC; verified batching via FrameDebugger's Hybrid Batch Groups showing a high instances-per-draw-call ratio.

**Example 2**
- Input: "Add a `Light` component to these ECS-converted torch entities so they cast light in the scene."
- Output: used a Companion Component for `Light` since it's on the supported list and can't be modeled as ECS data directly; disclosed upfront that reading/writing it from a system requires `foreach` iteration on the main thread (no Burst job), and that the torch entity's transform hierarchy under the companion GameObject isn't preserved as a parent-child relationship — confirmed with the requester that querying a handful of torches this way was an acceptable cost given the small count, rather than treating Companion Components as a free general-purpose bridge.

## 8. Edge cases & guardrails
- Never assume Entities Graphics works on the Built-in Render Pipeline, on URP paths other than Forward+, or on Web platforms — check `overview-and-setup.md`'s requirements/feature-matrix pages before any entity-rendering work, not after something fails to render.
- Never call `RenderMeshUtility.AddComponents` per-instance in a spawn loop — build one prototype entity and `Instantiate` it; this is the package's own documented anti-pattern for a reason (each `AddComponents` call is a structural change).
- Don't assume a custom shader "just works" with entities — confirm DOTS Instancing compatibility (built-in pipeline shaders qualify automatically; custom Shader Graph/hand-written shaders don't without explicit setup).
- Don't reach for a Companion Component as a general-purpose ECS/MonoBehaviour bridge — it only covers a fixed supported list (anything else gets silently stripped), forces main-thread-only managed access, and drops transform hierarchy; use it only when the MonoBehaviour genuinely can't be ECS data.
- Don't set up compute-shader mesh deformation without disclosing it's experimental — no frustum/occlusion culling, no VFX Graph integration, no cloth/bake-mesh support, and vertex-shader skinning won't gain future support.
- Don't claim a batching/performance win from switching to Entities Graphics without measuring via FrameDebugger/`EntitiesGraphicsStatsDrawer`/Profiler — below a certain object count, batch-creation overhead can make it slower than plain GameObject rendering, per `entities-graphics-performance.html`.
- Cross-check an unexplained rendering symptom (subscene lightmap gaps, missing ambient light from a directional light inside a subscene, RenderTexture-on-subscene-material glitches, longer build times from `DOTS_INSTANCING_ON` variants) against the documented known issues before treating it as a new bug.
- Don't confuse this skill's ECS-to-rendering bridging concerns with `unity-urp-rendering`'s/`unity-hdrp-rendering`'s own pipeline-configuration concerns — an entity can be perfectly set up for Entities Graphics and still render wrong because the URP/HDRP Asset itself is misconfigured; check both independently.

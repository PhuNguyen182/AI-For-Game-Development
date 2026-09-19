---
name: unity-entities-graphics
description: >
  Technique for `com.unity.entities.graphics`, the package that renders ECS
  entities by feeding `Unity.Entities` data to URP or HDRP through
  `BatchRendererGroup`: the rendering component set (`RenderMeshArray`,
  `MaterialMeshInfo`, `RenderMeshDescription`, `RenderBounds`,
  `RenderMeshUnmanaged`), `RenderMeshUtility.AddComponents` runtime creation,
  DOTS Instancing shader compatibility, `[MaterialProperty]` and Material
  Override Asset overrides, Hybrid Per Instance properties, Companion
  Components, compute mesh deformation, and instances-per-draw-command
  batching. Use when entities must render, or render wrongly.
  Not for: the URP versus HDRP decision (`render-pipeline-urp-hdrp`); pipeline
  configuration (`unity-urp-rendering`, `unity-hdrp-rendering`); shader node or
  HLSL content (`shader-authoring`); general entity and system design
  (`unity-ecs-architecture`); scheduling (`unity-job-system-and-burst`); Burst
  tuning (`unity-burst-compiler`); maths types (`unity-mathematics`); bespoke
  GPU compute passes (`compute-shader-vfx`).
---

# Unity Entities Graphics — Rendering ECS Entities Through URP & HDRP

## Bundled resources

### References
Read-only context, loaded on demand so SKILL.md itself stays short.

| File | Contents | Read when |
|---|---|---|
| [root-links.md](references/root-links.md) | Package manual and API roots plus the version pin | Starting any task here, or confirming the installed package version |
| [dots-relationship.md](references/dots-relationship.md) | What this package requires, and which sibling skill owns each adjacent concern | A request spans rendering plus ECS, jobs, Burst, or pipeline configuration |
| [overview-and-setup.md](references/overview-and-setup.md) | Requirements, feature matrix, per-platform support, installation | Before any entity is expected to render, or a target platform is added |
| [rendering-components.md](references/rendering-components.md) | The `Unity.Rendering` component set and what baking produces | Deciding which components an entity needs, or auditing what baking made |
| [runtime-creation-and-performance.md](references/runtime-creation-and-performance.md) | `RenderMeshUtility.AddComponents`, the prototype pattern, batching metrics, known issues | Spawning renderable entities in code, or diagnosing batching and rendering symptoms |
| [dots-instancing-and-material-overrides.md](references/dots-instancing-and-material-overrides.md) | DOTS Instancing compatibility and both override mechanisms | A custom shader is involved, or a property must vary per entity |
| [companion-components.md](references/companion-components.md) | The supported MonoBehaviour list and its access cost | A MonoBehaviour has to ride along on an entity |
| [mesh-deformations.md](references/mesh-deformations.md) | Compute skinning and blend shapes, and the features it lacks | Skinned or blend-shaped meshes must render as entities |
| [batch-renderer-group.md](references/batch-renderer-group.md) | What Entities Graphics is built on, for reasoning about batching | Explaining why batches fragmented or why a draw-call count is what it is |

## 1. Objective
Get entities rendering correctly and efficiently through the project's active render pipeline — the right component set, a shader that DOTS Instancing can actually use, overrides wired to properties the shader really declares, and batching measured rather than assumed. It prevents the failures this package produces silently: nothing rendering because the URP Asset is on the wrong path, a `[MaterialProperty]` whose name does not match the shader so the override simply never applies, a Companion Component stripped at bake time because its type was not on the supported list, `AddComponents` called per spawn so every instance pays a structural change, and batches fragmented by mesh or shader-variant differences nobody measured.

## 2. Role
Act as the Entities Graphics specialist for the client track — the tool reached for once a project is already on ECS and its entities have to appear on screen, or are appearing wrongly. You own the bridge from entity data to the pipeline; you do not configure the pipeline itself, author shader content, or design non-rendering ECS data.

## 3. When to invoke this skill
- Confirming Entities Graphics is even supported here — Unity 2022 LTS or later, URP on Forward+ or HDRP, linear colour space, and the target platform present in the feature matrix.
- Choosing or auditing an entity's rendering components against what baking already produces from `MeshRenderer`, `MeshFilter`, and `LODGroup`.
- Making a custom Shader Graph or hand-written shader DOTS Instancing compatible, and marking properties Hybrid Per Instance.
- Setting up per-entity material overrides, whether through a `[MaterialProperty]` `IComponentData` or a Material Override Asset.
- Spawning renderable entities at runtime through `RenderMeshUtility.AddComponents`.
- A reported rendering symptom on entities: nothing draws, a per-entity colour never changes, draw calls scale with instance count, a `Light` disappeared after baking, or a subscene's lighting is wrong.
- Deciding whether a MonoBehaviour should ride along as a Companion Component, and disclosing what that costs.
- Setting up compute-shader mesh deformation for skinned or blend-shaped entities.
- Negative trigger: choosing URP or HDRP for the project — that is `render-pipeline-urp-hdrp`.
- Negative trigger: configuring Renderer Features, rendering path, camera stacking, Frame Settings, Volumes, or Custom Passes — that is `unity-urp-rendering`/`unity-hdrp-rendering`, even when an entity renders wrongly because of one of those settings.
- Negative trigger: writing Shader Graph node logic or HLSL — that is `shader-authoring`; this skill decides only that a shader must be DOTS Instancing compatible and which properties are Hybrid Per Instance.
- Negative trigger: modeling non-rendering components, systems, queries, or baking in general — that is `unity-ecs-architecture`, which also owns the ECS-adoption gate this skill sits behind.
- Negative trigger: scheduling the system that writes an override component, or its container lifetime — that is `unity-job-system-and-burst`.
- Negative trigger: HPC# compliance or `FloatMode` on that system — that is `unity-burst-compiler`.
- Negative trigger: choosing `Unity.Mathematics` types — that is `unity-mathematics`, even though override components are typically `float4`.
- Negative trigger: a bespoke compute pass driving a visual effect outside this package's own deformation system — that is `compute-shader-vfx`; the Compute Deformation path here is fixed-purpose skinning and blend shapes, not a general GPU simulation hook.

## 4. How to use this skill
1. **Name the ECS-adoption decision this rendering work sits on top of**, per [dots-relationship.md](references/dots-relationship.md) — Entities Graphics cannot run without the Entities package, so it inherits `unity-ecs-architecture`'s escalation gate rather than providing its own reason to adopt ECS. [root-links.md](references/root-links.md) pins the package version below.
2. **Confirm pipeline, rendering path, colour space, and target platforms before any entity renders**, per [overview-and-setup.md](references/overview-and-setup.md) — the Built-in pipeline is unsupported outright, URP works only on Forward+, colour space must be linear, and platform support is uneven (Android is URP-only, Web is unsupported). Record the check, because the URP path is owned by another skill and can be changed without anyone touching this code.
3. **Let baking produce the rendering component set wherever the content is design-time**, per [rendering-components.md](references/rendering-components.md) — authoring an ordinary `MeshRenderer`/`MeshFilter`/`LODGroup` in a subscene yields the correct components with the best data layout, so hand-assembly is justified only by a genuine runtime-creation need.
4. **Create runtime entities from one prototype and `Instantiate` it**, per [runtime-creation-and-performance.md](references/runtime-creation-and-performance.md) — call `RenderMeshUtility.AddComponents` once to build the prototype, then clone and vary per-instance data with `SetComponent`; calling `AddComponents` per spawn is a structural change per instance and is the package's own documented anti-pattern.
5. **Keep `RenderMeshArray` shared across everything that can share it** — it is an `ISharedComponentData`, so entities pointing at different mesh/material lists never occupy the same chunk; one array indexed by `MaterialMeshInfo` keeps the archetype dense, and a per-entity array fragments it exactly as `unity-ecs-architecture` describes.
6. **Confirm DOTS Instancing compatibility before a custom shader reaches an entity**, per [dots-instancing-and-material-overrides.md](references/dots-instancing-and-material-overrides.md) — built-in URP and HDRP shaders already qualify; a custom Shader Graph qualifies for its own properties only once overrides are implemented, and a hand-written shader must follow the package's sample pattern.
7. **Choose the material-override mechanism by who has to change the value** — a Material Override Asset when a designer sets a fixed per-instance value with no code, or a `[MaterialProperty("_Name")] IComponentData` written by a Burst system when the value is computed or animated. Every Hybrid Per Instance property needs exactly one matching struct.
8. **Match the override's property name to the shader's declared name exactly** — a mismatched `[MaterialProperty]` string compiles, runs, and silently never reaches the shader, so verify the rendered result changes rather than trusting that the component is being written.
9. **Reach for a Companion Component only for a MonoBehaviour on the supported list**, per [companion-components.md](references/companion-components.md) — `Light`, `ReflectionProbe`, `ParticleSystem`, `VisualEffect` and the HDRP-specific types qualify; anything else is stripped during baking with no error. Disclose that access is main-thread managed iteration, never a Burst job, and that the companion becomes a root GameObject with its hierarchy lost.
10. **Treat mesh deformation as an experimental, disclosed trade-off**, per [mesh-deformations.md](references/mesh-deformations.md) — compute-shader skinning has no frustum or occlusion culling, no VFX Graph integration, and no cloth or bake-mesh support, so confirm the Tech Spec genuinely requires it before building Compute Deformation graphs.
11. **Measure batching as instances per draw command**, using FrameDebugger's Hybrid Batch Groups, `EntitiesGraphicsStatsDrawer`, and the `BatchRendererGroup` Profiler markers described in [batch-renderer-group.md](references/batch-renderer-group.md) — differing meshes or shader variants fragment batches, and per `performance-and-algorithms.md`'s Verification section a batching claim without this measurement is not a claim.
12. **Disclose the cases where this package costs more than it saves** — below a modest instance count, batch-creation overhead can make entity rendering slower than plain GameObjects, and `DOTS_INSTANCING_ON` variants are always compiled into a Player build, lengthening build times and raising memory. Say so rather than presenting the switch as free.
13. **Check an unexplained symptom against the documented known issues before calling it a bug** — subscene lightmap limits, a directional light inside a subscene breaking ambient lighting, RenderTexture-on-subscene-material glitches, and missing Companion Component previews are all known and listed.
14. **Ask which pipeline and path the project is actually on when it is not stated** — do not infer it from the presence of a URP asset; the Forward+ requirement is specific enough that guessing wrong invalidates everything downstream.

## 5. Specific goals / tasks this skill performs
- Verifying pipeline, path, colour space, and platform support before entity-rendering work starts.
- Auditing or assembling an entity's rendering component set, baked or runtime-created.
- Establishing DOTS Instancing compatibility for custom shaders and Hybrid Per Instance properties.
- Wiring per-entity material overrides through `[MaterialProperty]` components or Material Override Assets.
- Structuring runtime spawning as prototype plus `Instantiate` rather than per-spawn `AddComponents`.
- Deciding on Companion Components and disclosing their access and hierarchy cost.
- Scoping compute mesh deformation with its limitations stated.
- Measuring instances per draw command and diagnosing batch fragmentation and known issues.
- Out of scope: the URP versus HDRP decision (`render-pipeline-urp-hdrp`); pipeline configuration (`unity-urp-rendering`, `unity-hdrp-rendering`); shader content (`shader-authoring`); general ECS design and the adoption gate (`unity-ecs-architecture`); job scheduling (`unity-job-system-and-burst`); Burst tuning (`unity-burst-compiler`); maths types (`unity-mathematics`).

## 6. Output format
```
## Entities Graphics Work — <feature/system name>
- ECS prerequisite: <the adoption decision this sits on top of>
- Pipeline confirmed: <URP Forward+ / HDRP, Unity version, colour space, platforms checked>
- Component set: <baked automatically / AddComponents — which components>
- Shader compatibility: <built-in / custom Shader Graph with Hybrid Per Instance / hand-written — how confirmed>
- Overrides: <mechanism, property names, and how the change was seen to reach the shader>
- Companion Components: <which, and the disclosed cost — or "none">
- Mesh deformation: <used and why, limitations disclosed — or "none">
- Runtime creation: <prototype + Instantiate / baked only / not applicable>
- Batching measured: <instances per draw command, tool used — or "no batching claim made">
- Costs disclosed: <build-size, memory, low-count overhead, known issues that apply>
- Layer: <Game.Client.* rendering components and systems>
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
- Input: a crowd system already approved for ECS needs thousands of NPC entities spawned at runtime, each with its own tint, rendering through URP.
- Output: confirmed the URP Asset is on Forward+ and the project is in linear colour space before writing anything; built one prototype entity with `RenderMeshUtility.AddComponents` using URP Lit, which is already DOTS Instancing compatible; added `[MaterialProperty("_BaseColor")] struct Tint : IComponentData { public float4 Value; }` with a Burst system writing it, handing scheduling to `unity-job-system-and-burst` and compilation to `unity-burst-compiler`; spawned by `Instantiate` of the prototype through an `EntityCommandBuffer.ParallelWriter`; kept a single `RenderMeshArray` so every NPC shares one chunk-friendly shared-component value; measured 1 draw command per few thousand instances in FrameDebugger's Hybrid Batch Groups.

**Example 2**
- Input: "The tint component is definitely being written every frame — the shader must be broken, can you rewrite the Shader Graph?"
- Output: declined to touch the shader — the graph was fine and rewriting it is `shader-authoring`'s territory anyway. The `[MaterialProperty]` string was `"_Color"` while the graph declared `_BaseColor`, and a mismatched name never binds and never errors, so the system was writing a component nothing read. Corrected the attribute per §4's name-matching step and confirmed the change by seeing the rendered colour move, not by re-reading the component.

**Example 3**
- Input: torch entities converted from prefabs lost their `Light` after baking, and their `TorchFlickerBehaviour` script is gone too.
- Output: `Light` is on the Companion Component supported list and was restored as one, with the cost disclosed — main-thread managed iteration only, and the companion becomes a root GameObject so the torch hierarchy is not preserved. `TorchFlickerBehaviour` is not on the list, which is why it was stripped silently; its flicker was re-expressed as an ECS component driving the existing `[MaterialProperty]` override, since a bespoke MonoBehaviour has no companion path.

## 8. Edge cases & guardrails
- Never assume rendering works before checking the pipeline gate — Built-in is unsupported, URP works only on Forward+, colour space must be linear, and a path change owned by another skill can break this silently.
- Never call `RenderMeshUtility.AddComponents` per spawn — each call is a structural change; build one prototype and `Instantiate` it.
- Never trust a `[MaterialProperty]` name without seeing the rendered result change — a mismatch fails silently in both directions.
- Never give entities per-entity `RenderMeshArray` values — it is a shared component, and unique values fragment chunks the same way any other shared component does.
- Never treat Companion Components as a general MonoBehaviour bridge — only the supported list survives baking, everything else is stripped without an error to notice.
- Never set up mesh deformation without disclosing that it is experimental — no culling, no VFX Graph, no cloth or bake-mesh, and vertex-shader skinning has no future support.
- Never claim a batching win without instances-per-draw-command evidence — below a modest object count this package is measurably slower than GameObject rendering.
- Never present the switch as cost-free — `DOTS_INSTANCING_ON` variants always ship, adding build time and memory whether or not instancing is used.
- If the active pipeline and rendering path are unstated, ask — inferring them from the presence of a URP asset is the assumption that invalidates every later step.

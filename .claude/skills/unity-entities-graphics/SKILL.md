---
name: unity-entities-graphics
description: "Entities Graphics: rendering ECS entities via BatchRendererGroup, RenderMeshArray, MaterialMeshInfo, material overrides, LODs, culling. Use when ECS entities must render."
user-invocable: false
---

# Unity Entities Graphics

Not for: URP vs HDRP choice (`render-pipeline-urp-hdrp`), pipeline configuration (`unity-urp-rendering`, `unity-hdrp-rendering`), shader node/HLSL content (`shader-authoring`), non-rendering entity design, baking and the ECS adoption gate (`unity-ecs-architecture`), scheduling (`unity-job-system-and-burst`), Burst tuning (`unity-burst-compiler`), maths types (`unity-mathematics`), bespoke GPU compute (`compute-shader-vfx`), light setup/lightmap UVs/bake/probes (`unity-lighting`).
Docs: https://docs.unity3d.com/Packages/com.unity.entities.graphics@6.6/ (`manual/`, `api/`) — pinned 6.6; support statements differ between versions, so check the installed one.

| Reference | Read when |
|---|---|
| [overview-and-setup.md](references/overview-and-setup.md) | Before any entity is expected to render, or a platform is added |
| [rendering-components.md](references/rendering-components.md) | Choosing an entity's components, or auditing what baking made |
| [runtime-creation-and-performance.md](references/runtime-creation-and-performance.md) | Spawning renderable entities in code, a batching claim, or an unexplained rendering symptom |
| [dots-instancing-and-material-overrides.md](references/dots-instancing-and-material-overrides.md) | A custom shader is involved, or a property must vary per entity |
| [companion-components.md](references/companion-components.md) | A MonoBehaviour must ride along on an entity, or one vanished after baking |
| [mesh-deformations.md](references/mesh-deformations.md) | Skinned or blend-shaped meshes must render as entities |

## Steps
1. **Require an approved ECS adoption** — Entities Graphics renders `Unity.Entities` data only, so it inherits `unity-ecs-architecture`'s gate. The pipeline it needs is narrower than the pipeline choice: a project correctly on URP can render nothing because the path is not Forward+.
2. **Confirm pipeline, rendering path, colour space and platforms before any entity renders**, per [overview-and-setup.md](references/overview-and-setup.md). Not stated → ask; never infer from a URP asset being present. Record the path verified: another skill can change it later.
3. **Let baking produce the component set for design-time content**, per [rendering-components.md](references/rendering-components.md); hand-assembly only for genuine runtime creation.
4. **Create runtime entities from one prototype and `Instantiate` it**, per [runtime-creation-and-performance.md](references/runtime-creation-and-performance.md). `AddComponents` once; per-instance data via `SetComponent`.
5. **Share one `RenderMeshArray`** across everything that can; it is shared component data, so per-entity arrays fragment chunks.
6. **Confirm DOTS Instancing compatibility before a custom shader reaches an entity**, per [dots-instancing-and-material-overrides.md](references/dots-instancing-and-material-overrides.md).
7. **Pick the override mechanism by who changes the value**: Material Override Asset for a designer-set fixed value, `[MaterialProperty("_Name")] IComponentData` written by a Burst system for a computed or animated one.
8. **Verify an override by seeing the rendered result change**, not by confirming the component is written; a name mismatch never errors.
9. **Companion Component only for a supported MonoBehaviour**, per [companion-components.md](references/companion-components.md). Disclose main-thread managed access and lost hierarchy.
10. **Treat mesh deformation as experimental**, per [mesh-deformations.md](references/mesh-deformations.md); confirm the Tech Spec requires it, since it has no culling.
11. **Measure batching as instances per draw command** (tools in [runtime-creation-and-performance.md](references/runtime-creation-and-performance.md)); without it a batching claim is not a claim (`csharp-standards` → `performance-and-algorithms.md` → Verification).
12. **Disclose costs**: below a modest instance count this can be slower than GameObjects, and `DOTS_INSTANCING_ON` variants always ship, adding build time and memory.
13. **Check an unexplained symptom against the known issues** in the same reference before calling it a bug.

## Never
- Treat Companion Components as a general MonoBehaviour bridge; unsupported types are stripped at bake with no error.

## Output
```
## Entities Graphics Work — <feature/system name>
- ECS prerequisite: <the adoption decision this sits on>
- Pipeline confirmed: <URP Forward+ / HDRP, Unity version, colour space, platforms checked>
- Component set: <baked / AddComponents — which>
- Shader compatibility: <built-in / custom Shader Graph with Hybrid Per Instance / hand-written — how confirmed>
- Overrides: <mechanism, property names, how the change was seen to reach the shader>
- Companion Components: <which and the disclosed cost — or "none">
- Mesh deformation: <used and why, limitations disclosed — or "none">
- Runtime creation: <prototype + Instantiate / baked only / n/a>
- Batching measured: <instances per draw command, tool — or "no batching claim made">
- Costs disclosed: <build size, memory, low-count overhead, known issues>
- Known limitations: <...>
```
On request only, add `Latent concerns` and `Future remediation`, each with its trigger.

## Example
- "The tint component is written every frame, so rewrite the Shader Graph" → declined: the `[MaterialProperty]` string was `"_Color"` while the graph declared `_BaseColor`; fixed the attribute and confirmed the rendered colour moved.

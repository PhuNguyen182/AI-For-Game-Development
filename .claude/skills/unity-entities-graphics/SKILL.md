---
name: unity-entities-graphics
description: "Entities Graphics: BatchRendererGroup, RenderMeshArray, MaterialMeshInfo, LODs. Use when ECS entities must render."
user-invocable: false
---

# Unity Entities Graphics

- **Not for:** URP vs HDRP choice (`render-pipeline-urp-hdrp`).
- **Not for:** pipeline configuration (`unity-urp-rendering`, `unity-hdrp-rendering`).
- **Not for:** shader node/HLSL content (`shader-authoring`).
- **Not for:** non-rendering entity design, baking and the ECS adoption gate (`unity-ecs-architecture`).
- **Not for:** scheduling (`unity-job-system-and-burst`).
- **Not for:** Burst tuning (`unity-burst-compiler`).
- **Not for:** maths types (`unity-mathematics`).
- **Not for:** bespoke GPU compute (`compute-shader-vfx`).
- **Not for:** light setup, lightmap UVs, bake and probes (`unity-lighting`).
- **Docs:** https://docs.unity3d.com/Packages/com.unity.entities.graphics@6.6/ (`manual/`, `api/`) — pinned 6.6.
  - **Version:** support statements differ between versions, so check the installed one.

## References
- **[overview-and-setup.md](references/overview-and-setup.md):** Before any entity is expected to render, or a platform is added.
- **[rendering-components.md](references/rendering-components.md):** Choosing an entity's components, or auditing what baking made.
- **[runtime-creation-and-performance.md](references/runtime-creation-and-performance.md):** Spawning renderable entities in code, a batching claim, or an unexplained rendering symptom.
- **[dots-instancing-and-material-overrides.md](references/dots-instancing-and-material-overrides.md):** A custom shader is involved, or a property must vary per entity.
- **[companion-components.md](references/companion-components.md):** A MonoBehaviour must ride along on an entity, or one vanished after baking.
- **[mesh-deformations.md](references/mesh-deformations.md):** Skinned or blend-shaped meshes must render as entities.

## Steps
1. **Require an approved ECS adoption:** Entities Graphics renders `Unity.Entities` data only, so it inherits the gate of `unity-ecs-architecture`.
   - **Pipeline needed:** narrower than the pipeline choice; a project correctly on URP can render nothing because the path is not Forward+.
2. **Confirm pipeline, rendering path, colour space and platforms before any entity renders:** per [overview-and-setup.md](references/overview-and-setup.md).
   - **Path verified:** record it, because another skill can change it later.
   - **Any of the four not stated:** step 14.
3. **Let baking produce the component set for design-time content:** per [rendering-components.md](references/rendering-components.md).
   - **Hand-assembly:** only for genuine runtime creation.
4. **Create runtime entities from one prototype and `Instantiate` it:** per [runtime-creation-and-performance.md](references/runtime-creation-and-performance.md).
   - **`AddComponents`:** once.
   - **Per-instance data:** via `SetComponent`.
5. **Share one `RenderMeshArray` across everything that can:** it is shared component data, so per-entity arrays fragment chunks.
6. **Confirm DOTS Instancing compatibility before a custom shader reaches an entity:** per [dots-instancing-and-material-overrides.md](references/dots-instancing-and-material-overrides.md).
7. **Pick the override mechanism by who changes the value:**
   - **Designer-set fixed value:** Material Override Asset.
   - **Computed or animated value:** `[MaterialProperty("_Name")] IComponentData` written by a Burst system.
8. **Verify an override by seeing the rendered result change:** not by confirming the component is written.
   - **Name mismatch:** never errors.
9. **Companion Component only for a supported MonoBehaviour:** per [companion-components.md](references/companion-components.md).
   - **Disclose:** main-thread managed access and lost hierarchy.
10. **Treat mesh deformation as experimental:** per [mesh-deformations.md](references/mesh-deformations.md).
    - **Tech Spec:** confirm it requires deformation, since deformation has no culling.
11. **Measure batching as instances per draw command:** tools in [runtime-creation-and-performance.md](references/runtime-creation-and-performance.md).
    - **Without the measurement:** a batching claim is not a claim (`csharp-standards` → `performance-and-algorithms.md` → Verification).
12. **Disclose costs:**
    - **Low instance count:** below a modest instance count this can be slower than GameObjects.
    - **Variants:** `DOTS_INSTANCING_ON` variants always ship, adding build time and memory.
13. **Check an unexplained symptom against the known issues in the same reference:** before calling it a bug.
14. **Missing input:** pipeline, rendering path, colour space or platforms not stated → dispatched agent `Blocked` or `Needs-decision`; main session `AskUserQuestion`.
    - **Never infer:** do not infer them from a URP asset being present.

## Never
- **Treat Companion Components as a general MonoBehaviour bridge:** unsupported types are stripped at bake with no error.

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
```

## Example
- **"The tint component is written every frame, so rewrite the Shader Graph":** declined, the `[MaterialProperty]` string was `"_Color"` while the graph declared `_BaseColor`.
  - **Did instead:** fixed the attribute and confirmed the rendered colour moved.

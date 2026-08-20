# DOTS & Rendering-Pipeline Relationship

Hand-authored synthesis — not a single source page — covering how this skill sits relative to the rest of the DOTS family and the render-pipeline skills.

## ECS dependency
Entities Graphics renders `Unity.Entities` data, so — like `unity-physics` — it requires the Entities package to run at all and sits on the same ECS-adoption escalation gate `unity-ecs-architecture` sits on (per `performance-and-algorithms.md`). Unlike Collections/Mathematics (independent of ECS), neither Physics nor Entities Graphics work with zero entities involved.

## Relationship to sibling DOTS skills
- **`unity-ecs-architecture`** owns general entity/component/system/query/baking design. This skill only owns the *rendering-specific* slice of that: which rendering components an entity ends up with, and whether a material-override component is correctly declared — it doesn't restate general ECS mechanics.
- **`unity-job-system-and-burst`** still owns scheduling/dependency/disposal mechanics for any Burst system this skill's material-override work introduces (e.g. a system writing a `[MaterialProperty]` component) — Entities Graphics doesn't add a new job interface the way Unity Physics's `ICollisionEventsJob` family does; it's an ordinary ECS system once material overrides are wired up.
- **`unity-burst-compiler`** still owns Burst compilation tuning for that same system — every material-override system is expected to be Burst-compiled, but HPC# subset compliance/`FloatMode`/verification stays that skill's territory.
- **`unity-collections`** owns the general blob-asset/`NativeContainer` mechanics that `RenderMeshArray`'s internal mesh/material lists are conceptually similar to — this skill doesn't reach into that mechanism directly, it just consumes `RenderMeshArray` as a shared component.
- **`unity-mathematics`** owns the `float4`/`float3`/`quaternion` type choice — material-override components (`BaseColor`, custom "Hybrid Per Instance" properties) are typically `float4`-typed, but which `Unity.Mathematics` type/function to use is that skill's call.
- **`unity-physics`** — no direct dependency between the two packages; both independently require ECS and both are DOTS-family packages, but a physics body and a renderable entity are separate concerns that happen to often coexist on the same entity.

## Relationship to render-pipeline skills
- **`render-pipeline-urp-hdrp`** makes the URP-vs-HDRP decision this skill's platform/pipeline gate (see `overview-and-setup.md`) depends on — Entities Graphics narrows that further (URP Forward+ only; HDRP fully; never Built-in).
- **`unity-urp-rendering`** / **`unity-hdrp-rendering`** own the pipeline's own configuration (Renderer Features, Frame Settings, Volumes, etc.) that entities render *through* — this skill doesn't reconfigure either pipeline, it just requires the right settings already be in place (e.g. URP's Forward+ path).
- **`shader-authoring`** owns the actual Shader Graph node logic/HLSL content — this skill only decides whether that shader needs to be DOTS Instancing compatible and which of its properties need "Hybrid Per Instance" declared for material overrides to reach it.

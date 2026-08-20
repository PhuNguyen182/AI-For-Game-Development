# Mesh Deformations (Skinning & Blend Shapes)

Covers SKILL.md step 8 — the experimental compute-shader-based deformation system.

## Manual
- [Mesh Deformations](https://docs.unity3d.com/Packages/com.unity.entities.graphics@6.6/manual/mesh_deformations.html) — an **experimental**, compute-shader-based system mimicking Skinned Mesh Renderer behavior for entities.
  - **Setup**: install Entities Graphics; optionally add a scripting define for HDRP motion-vector support; build materials with a Shader Graph using the "Compute Deformation" node wired to vertex position/normal/tangent outputs; source meshes need a Skinned Mesh Renderer with blend shapes and/or valid bind poses + skin weights.
  - **Control**: driven by two ECS components — Skin Matrix and Blend Shape Weight — modified by a custom system to animate the deformation.
  - **Limitations**: not compatible with Scene View Draw Modes; no frustum/occlusion culling; no VFX Graph integration; missing standard Skinned Mesh Renderer features (cloth simulation, bake-mesh). Compute-shader processing is the supported path — vertex-shader skinning is discouraged and will not receive future support.

Confirm the Tech Spec genuinely needs this before setting it up — see SKILL.md's edge-case guardrail on disclosing its experimental status up front.

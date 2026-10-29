# Mesh deformations (compute skinning, blend shapes)

Source: `manual/mesh_deformations.html`. Experimental; the limitations decide whether to use it.

## Setup
- Shader Graph "Compute Deformation" node wired to vertex position, normal and tangent outputs.
- Source mesh: Skinned Mesh Renderer with blend shapes and/or valid bind poses plus skin weights.
- Skin Matrix and Blend Shape Weight components, written by a custom system, animate it.
- HDRP motion vectors need an additional scripting define.

## Limitations
- No frustum or occlusion culling: off-screen characters still cost, which can invalidate a crowd budget (the usual reason to decline it).
- No VFX Graph integration; no cloth simulation; no bake-mesh.
- Not compatible with Scene View Draw Modes.
- Vertex-shader skinning is discouraged and gets no future support; compute is the only forward path.

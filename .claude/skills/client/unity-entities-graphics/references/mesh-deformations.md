# Mesh Deformations — Compute Skinning & Blend Shapes

Source: [Mesh Deformations](https://docs.unity3d.com/Packages/com.unity.entities.graphics@6.6/manual/mesh_deformations.html).
Covers: SKILL.md §4 — **"Treat mesh deformation as an experimental, disclosed trade-off"**.

The experimental compute-shader system that mimics Skinned Mesh Renderer
behaviour for entities. Its limitations are the deliverable of this file — they
decide whether it can be used at all.

## Setup

| Step | What it decides | Source |
|---|---|---|
| Shader Graph "Compute Deformation" node | Wired to vertex position, normal, and tangent outputs — without it the material cannot deform | [Mesh Deformations](https://docs.unity3d.com/Packages/com.unity.entities.graphics@6.6/manual/mesh_deformations.html) |
| Source mesh requirements | A Skinned Mesh Renderer with blend shapes and/or valid bind poses plus skin weights | [Mesh Deformations](https://docs.unity3d.com/Packages/com.unity.entities.graphics@6.6/manual/mesh_deformations.html) |
| Skin Matrix and Blend Shape Weight components | The two ECS components a custom system writes to animate the deformation | [Mesh Deformations](https://docs.unity3d.com/Packages/com.unity.entities.graphics@6.6/manual/mesh_deformations.html) |
| HDRP motion vectors | Requires an additional scripting define | [Mesh Deformations](https://docs.unity3d.com/Packages/com.unity.entities.graphics@6.6/manual/mesh_deformations.html) |

## What it does not do

| Limitation | What it decides | Source |
|---|---|---|
| No frustum or occlusion culling | Deformation cost is paid for off-screen characters too, which changes the crowd budget entirely | [Mesh Deformations](https://docs.unity3d.com/Packages/com.unity.entities.graphics@6.6/manual/mesh_deformations.html) |
| No VFX Graph integration | Effects driven from deformed geometry are not available | [Mesh Deformations](https://docs.unity3d.com/Packages/com.unity.entities.graphics@6.6/manual/mesh_deformations.html) |
| No cloth simulation, no bake-mesh | Standard Skinned Mesh Renderer features simply absent | [Mesh Deformations](https://docs.unity3d.com/Packages/com.unity.entities.graphics@6.6/manual/mesh_deformations.html) |
| Not compatible with Scene View Draw Modes | Some Editor diagnostics do not work on deformed entities | [Mesh Deformations](https://docs.unity3d.com/Packages/com.unity.entities.graphics@6.6/manual/mesh_deformations.html) |
| Vertex-shader skinning | Discouraged and will receive no future support — compute is the only forward path | [Mesh Deformations](https://docs.unity3d.com/Packages/com.unity.entities.graphics@6.6/manual/mesh_deformations.html) |

**Critical caveat**: missing culling is the limitation that most often decides
against this system. A crowd sized on the assumption that off-screen characters
are cheap is sized wrongly here, and the discrepancy appears only once the
camera turns away.

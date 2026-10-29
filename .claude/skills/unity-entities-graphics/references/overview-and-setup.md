# Requirements, feature matrix, setup

Sources (under `manual/`): `requirements-and-compatibility.html` (req), `entities-graphics-versions.html` (matrix), `creating-a-new-entities-graphics-project.html` (setup), `overview.html` (ovw).

Failing this gate gives entities that do not draw, with no error.

## Hard requirements
| Subject | Rule |
|---|---|
| Unity | 2022 LTS or later (req) |
| Built-in RP | Not supported (req) |
| URP | Forward+ path only; Forward and Deferred are not covered, so a path change silently removes support (req) |
| HDRP | Supported on 2022 LTS and later (req) |
| Colour space | Linear only, both pipelines (matrix) |
| Platforms | Uneven: Android URP-only, consoles both, Web unsupported (req) |

## Ruled out (matrix)
- Shader coverage: Lit and Unlit on both; Decal HDRP-only, Particle URP-only.
- LOD crossfade unsupported on both.
- Texture streaming, ray tracing, streaming virtual texturing not implemented.
- Skinning and mesh deformation experimental on both ([mesh-deformations.md](mesh-deformations.md)).

## Setup (setup)
- Hub "3D (URP)" or "3D (HDRP)" template arrives configured: the low-risk start.
- Existing project: Package Manager pulls the ECS dependencies; enable SRP Batcher and check colour space by hand.
- Baking (ovw): `MeshRenderer`/`MeshFilter` become render components, `LODGroup` becomes `MeshLODComponent`, `Transform` becomes `LocalToWorld`.

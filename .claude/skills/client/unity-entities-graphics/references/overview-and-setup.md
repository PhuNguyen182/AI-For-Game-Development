# Requirements, Feature Matrix & Setup

Sources: [Requirements and compatibility](https://docs.unity3d.com/Packages/com.unity.entities.graphics@6.6/manual/requirements-and-compatibility.html), [Entities Graphics Feature Matrix](https://docs.unity3d.com/Packages/com.unity.entities.graphics@6.6/manual/entities-graphics-versions.html), [Overview](https://docs.unity3d.com/Packages/com.unity.entities.graphics@6.6/manual/overview.html).
Covers: SKILL.md §4 — **"Confirm pipeline, rendering path, colour space, and target platforms before any entity renders"**.

The gate every other step in this skill assumes has passed. Failing it produces
entities that simply do not draw, with no error, so it is checked first and
recorded. Which pipeline the project should use is `render-pipeline-urp-hdrp`.

## Hard requirements

| Subject | What it decides | Source |
|---|---|---|
| Unity 2022 LTS or later | Below it the package does not apply at all | [Requirements](https://docs.unity3d.com/Packages/com.unity.entities.graphics@6.6/manual/requirements-and-compatibility.html) |
| Built-in Render Pipeline | **Not supported** — no configuration makes entities render under it | [Requirements](https://docs.unity3d.com/Packages/com.unity.entities.graphics@6.6/manual/requirements-and-compatibility.html) |
| URP | Supported on the **Forward+ path only**; Forward and Deferred are not covered, so a path change silently removes support | [Requirements](https://docs.unity3d.com/Packages/com.unity.entities.graphics@6.6/manual/requirements-and-compatibility.html) |
| HDRP | Fully supported on 2022 LTS and later | [Requirements](https://docs.unity3d.com/Packages/com.unity.entities.graphics@6.6/manual/requirements-and-compatibility.html) |
| Colour space | Linear only, on both pipelines | [Feature matrix](https://docs.unity3d.com/Packages/com.unity.entities.graphics@6.6/manual/entities-graphics-versions.html) |
| Platform coverage | Uneven — Android is URP-only, consoles support both, Web is unsupported | [Requirements](https://docs.unity3d.com/Packages/com.unity.entities.graphics@6.6/manual/requirements-and-compatibility.html) |

## What the feature matrix rules out

| Subject | What it decides | Source |
|---|---|---|
| Shader coverage | Lit and Unlit on both; Decal is HDRP-only, Particle is URP-only — a shader family available in one pipeline may not exist in the other | [Feature matrix](https://docs.unity3d.com/Packages/com.unity.entities.graphics@6.6/manual/entities-graphics-versions.html) |
| LOD crossfade | Unsupported on both pipelines | [Feature matrix](https://docs.unity3d.com/Packages/com.unity.entities.graphics@6.6/manual/entities-graphics-versions.html) |
| Texture streaming, ray tracing, streaming virtual texturing | Not implemented — features a pipeline offers that entities do not get | [Feature matrix](https://docs.unity3d.com/Packages/com.unity.entities.graphics@6.6/manual/entities-graphics-versions.html) |
| Skinning and mesh deformation | Experimental on both — see [mesh-deformations.md](mesh-deformations.md) | [Feature matrix](https://docs.unity3d.com/Packages/com.unity.entities.graphics@6.6/manual/entities-graphics-versions.html) |

## Setup

| Path | What it decides | Source |
|---|---|---|
| Unity Hub "3D (URP)" or "3D (HDRP)" template | Arrives pre-configured, which is why it is the low-risk start | [Installing Entities Graphics](https://docs.unity3d.com/Packages/com.unity.entities.graphics@6.6/manual/creating-a-new-entities-graphics-project.html) |
| Adding to an existing project | Package Manager pulls the ECS dependencies, but SRP Batcher must be enabled and colour space checked by hand | [Installing Entities Graphics](https://docs.unity3d.com/Packages/com.unity.entities.graphics@6.6/manual/creating-a-new-entities-graphics-project.html) |
| What baking produces | `MeshRenderer`/`MeshFilter` become render components, `LODGroup` becomes `MeshLODComponent`, `Transform` becomes `LocalToWorld` | [Overview](https://docs.unity3d.com/Packages/com.unity.entities.graphics@6.6/manual/overview.html) |

**Critical caveat**: this gate is not a one-time check. The URP rendering path
belongs to `unity-urp-rendering`, so a later change there can withdraw support
from every entity in the project without touching a line of this skill's code.
Record which path was verified, and when.

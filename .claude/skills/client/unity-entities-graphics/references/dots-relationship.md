# Relationship to ECS, the DOTS Family & the Pipeline Skills

Source: Not sourced from a single URL — synthesized from each package's stated requirements and from this skill set's own boundaries.
Covers: SKILL.md §4 — **"Name the ECS-adoption decision this rendering work sits on top of"**.

Where this package sits: it requires ECS, it does not configure the render
pipeline, and it does not author shaders. This file exists to settle which
skill owns a request that spans two of those.

## What this package requires

| Subject | What it decides | Source |
|---|---|---|
| Entities package | Required — Entities Graphics renders `Unity.Entities` data and does nothing with zero entities, so it inherits `unity-ecs-architecture`'s adoption gate rather than justifying ECS by itself | synthesized |
| A supported SRP | URP on Forward+ or HDRP; the pipeline still owns content authoring and pass definitions, this package only supplies data to it | [Requirements and compatibility](https://docs.unity3d.com/Packages/com.unity.entities.graphics@6.6/manual/requirements-and-compatibility.html) |
| Independence from Physics | No dependency either way with `unity-physics`; both require ECS and often coexist on one entity, but neither implies the other | synthesized |

## Who owns what

| Concern | Owner | Source |
|---|---|---|
| Which rendering components an entity carries, and whether an override is declared correctly | This skill | synthesized |
| Non-rendering components, systems, queries, baking, the ECS adoption gate | `unity-ecs-architecture` | synthesized |
| Scheduling and container lifetime for a system that writes an override component | `unity-job-system-and-burst` — this package adds no job interface of its own | synthesized |
| HPC# compliance and `FloatMode` for that same system | `unity-burst-compiler` | synthesized |
| `float4`/`float3` type choice inside an override component | `unity-mathematics` | synthesized |
| Whether the project runs URP or HDRP at all | `render-pipeline-urp-hdrp` | synthesized |
| Renderer Features, rendering path, Frame Settings, Volumes, Custom Passes | `unity-urp-rendering` / `unity-hdrp-rendering` | synthesized |
| Shader Graph node logic and HLSL | `shader-authoring` — this skill only decides DOTS Instancing compatibility and which properties are Hybrid Per Instance | synthesized |

**Critical caveat**: the pipeline requirement is narrower than the pipeline
choice. A project can be correctly on URP, chosen by `render-pipeline-urp-hdrp`
and configured by `unity-urp-rendering`, and still render no entities at all
because that configuration selected a path other than Forward+.

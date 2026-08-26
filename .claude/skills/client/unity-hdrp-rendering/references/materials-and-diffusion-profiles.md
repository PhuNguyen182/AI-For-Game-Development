# Master Stacks & Diffusion Profiles

Sources: [Diffusion Profile reference](https://docs.unity3d.com/Packages/com.unity.render-pipelines.high-definition@17.5/manual/diffusion-profile-reference.html), [StackLit master stack](https://docs.unity3d.com/Packages/com.unity.render-pipelines.high-definition@17.5/manual/master-stack-stacklit.html), [Layered Lit Shader](https://docs.unity3d.com/Packages/com.unity.render-pipelines.high-definition@17.5/manual/Layered-Lit-Shader.html).
Covers: SKILL.md §4 — **"Pick the master stack from the surface type"**, **"Register every Diffusion Profile in the project's Diffusion Profile list"**.

Which shading model a surface uses, and the registration step that decides
whether subsurface scattering appears at all. The graph's node content is
`shader-authoring`'s.

## Master stacks

| Stack | What it decides | Source |
|---|---|---|
| Lit | General physically based surfaces — the default, and the right answer for most opaque geometry | [Layered Lit](https://docs.unity3d.com/Packages/com.unity.render-pipelines.high-definition@17.5/manual/Layered-Lit-Shader.html) |
| StackLit | Multiple specular lobes and coat layers — car paint, lacquer, anything Lit can only approximate | [StackLit master stack](https://docs.unity3d.com/Packages/com.unity.render-pipelines.high-definition@17.5/manual/master-stack-stacklit.html) |
| Layered Lit | Blends several Lit material layers on one surface, driven by masks | [Layered Lit](https://docs.unity3d.com/Packages/com.unity.render-pipelines.high-definition@17.5/manual/Layered-Lit-Shader.html) |
| Decal | Projected decals, which need their own stack rather than a Lit material on a quad | [HDRP Manual index](https://docs.unity3d.com/Packages/com.unity.render-pipelines.high-definition@17.5/manual/index.html) |
| Fabric / Hair | Dedicated shading models whose look cannot be produced by tuning Lit parameters | [HDRP Manual index](https://docs.unity3d.com/Packages/com.unity.render-pipelines.high-definition@17.5/manual/index.html) |

## Diffusion Profiles

| Subject | What it decides | Source |
|---|---|---|
| What it is | The asset describing subsurface scattering behaviour — skin, wax, foliage, marble | [Diffusion Profile reference](https://docs.unity3d.com/Packages/com.unity.render-pipelines.high-definition@17.5/manual/diffusion-profile-reference.html) |
| Registration | A profile must be in the project's Diffusion Profile list to be loaded; assigned but unregistered renders as though the material had none | [Diffusion Profile reference](https://docs.unity3d.com/Packages/com.unity.render-pipelines.high-definition@17.5/manual/diffusion-profile-reference.html) |
| Bounded list | The list holds a limited number of profiles, so slots are a project-wide budget rather than a per-material choice | [Diffusion Profile reference](https://docs.unity3d.com/Packages/com.unity.render-pipelines.high-definition@17.5/manual/diffusion-profile-reference.html) |
| StackLit coupling | Setting Dual Specular Lobe Parametrization to "From Diffusion Profile" lets the profile drive the specular lobes too | [StackLit master stack](https://docs.unity3d.com/Packages/com.unity.render-pipelines.high-definition@17.5/manual/master-stack-stacklit.html) |

**Critical caveat**: an unregistered profile fails exactly like a badly tuned
one — the material renders, it simply renders without scattering. Check
registration before adjusting a single profile parameter.

# Master Stacks and Diffusion Profiles

Pages (17.5): `manual/master-stack-stacklit.html`, `manual/Layered-Lit-Shader.html`, `manual/diffusion-profile-reference.html`. Graph node content is `shader-authoring`'s.

| Stack | Use for |
|---|---|
| Lit | General PBR; default for most opaque geometry |
| StackLit | Multiple specular lobes or coat layers (car paint, lacquer) that Lit only approximates |
| Layered Lit | Several Lit layers on one surface, blended by masks |
| Decal | Projected decals; not a Lit material on a quad |
| Fabric / Hair | Dedicated shading models Lit parameters cannot reproduce |

## Diffusion Profiles
- Describe subsurface scattering (skin, wax, foliage, marble).
- A profile must be in the project's Diffusion Profile list to load. Assigned but unregistered renders as none, so check registration before tuning any parameter.
- The list is bounded: treat slots as a project-wide budget, not one per character.
- StackLit with Dual Specular Lobe Parametrization "From Diffusion Profile" lets the profile drive the specular lobes too.

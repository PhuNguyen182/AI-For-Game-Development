# Rendering — Pipelines, Materials, Draw Calls, Alpha Workflow, Shaders

Source: [spine-unity-rendering](https://esotericsoftware.com/spine-unity-rendering).

## Render pipeline support
- **Built-in Render Pipeline** — default shaders ship in the spine-unity runtime package.
- **Universal Render Pipeline (URP)** — a separate extension UPM package, with 2D and 3D Forward Renderer shader variants.
- **Lightweight Render Pipeline (LWRP)** — a separate legacy extension UPM package.
- **Deferred Shading** — not supported by Spine shaders (Built-in or URP).

Never mix shader families across a pipeline boundary — a Built-in `Spine/Skeleton` shader under URP, or a URP Spine shader under the Built-in pipeline, is a broken combination even where it happens to render *something*.

## Materials and atlas management
Each atlas page texture gets its own Material, auto-created at import. Using a slot blend mode other than `Normal` creates additional per-blend-mode materials too (except `Additive` under PMA, which reuses the normal material). `SkeletonRenderer`/`SkeletonGraphic` rebuild the Materials array every frame from the currently-assigned attachments, their atlas assets, and slot blend modes — **any direct edit to the Materials array is overwritten on the next `LateUpdate()`**. Use `SkeletonRendererCustomMaterials`/`SkeletonGraphicCustomMaterials` (see utility-components.md) for a per-instance override instead, or edit the Atlas asset itself for a project-wide change.

## Material switching and draw calls
Material order in the array follows draw order. When attachments span multiple atlas pages or blend modes (material `A`, material `B`, ...), the array is populated in the order draw order actually needs them — each entry is one draw call. Minimize material switching by packing attachments across fewer atlas pages and organizing them with draw order in mind, not just visual grouping.

### Per-instance customization without breaking batching
```csharp
// Full material swap (breaks batching with other instances on the original material)
skeletonAnimation.CustomMaterialOverride[originalMaterial] = newMaterial;
skeletonAnimation.CustomMaterialOverride.Remove(originalMaterial);
// Get the original material from SkeletonDataAsset.atlasAssets[0].PrimaryMaterial, not MeshRenderer.material

// Per-slot override
skeletonAnimation.CustomSlotMaterials[slot] = newMaterial;
```

**Tinting without breaking batching**: set `Skeleton.R`/`G`/`B`/`A` (with `Advanced → PMA Vertex Colors` enabled) instead of swapping materials — same technique works per-slot. `MaterialPropertyBlock` (via `Renderer.SetPropertyBlock()`) is the other per-instance override path, but different property values per instance still break batching; batching only happens when values actually match.

## Transparency and draw order
Alpha blending defeats automatic z-buffer depth sorting — triangles must render back-to-front. Within one mesh, slot draw order guarantees this. Between meshes/renderers, order is decided (in priority) by: camera depth → `Material.renderQueue` → shader `Queue` tag → `SortingGroup` components → `SortingLayer`/`sortingOrder` → distance from camera. Cameras also expose a `transparencySortMode` property.

**Sorting Layer / Order in Layer**: exposed on the SkeletonRenderer inspector as friendly properties, backed by `MeshRenderer.sortingLayerID`/`sortingOrder`.

**Multi-page skeletons under an orthographic camera** can sort incorrectly — fix by adding a `SortingGroup` component to the skeleton GameObject, or by rotating the camera a negligible amount (e.g. Y rotation = 0.001) to break the degenerate sort case.

**Rendering something between skeleton parts**: use `SkeletonRenderSeparator` (see utility-components.md) to split rendering into multiple parts.

**Fading a skeleton in/out**: don't just lower alpha — overlapping attachments will show through each other. Render to a temporary `RenderTexture` at full opacity, then draw that texture at the target fade opacity, via `SkeletonRenderTexture`/`SkeletonRenderTextureFadeout` (see utility-components.md). Example scene: `Spine Examples/Other Examples/RenderTexture FadeOut Transparency`.

## Shader catalog

Default shader: `Spine/Skeleton`. **Only special `CanvasRenderer`-compatible shaders (`Spine/SkeletonGraphic*`) work with `SkeletonGraphic`** — this restriction is repeated because it's the single most common Spine rendering mistake.

### Built-in pipeline shaders
| Shader | Notes |
|---|---|
| `Spine/Skeleton` | Unlit, no z-write; default for `SkeletonRenderer` |
| `Spine/Skeleton Graphic` | Unlit, no z-write, single texture only; default for `SkeletonGraphic` |
| `Spine/Skeleton Lit` | Simple lit, no z-write |
| `Spine/Skeleton Lit ZWrite` | Simple lit, with z-write |
| `Spine/Skeleton Fill` | Unlit with a customizable color overlay (`FillColor`, `FillPhase`) |
| `Spine/Skeleton Tint` | Unlit, two-color tint (light via `Tint Color`, dark via `Black Point`) |
| `Spine/Skeleton Tint Black` | Unlit, animated per-slot tint-black support |
| `Spine/Skeleton Tint Black Additive` | Additive variant of the above |
| `Spine/SkeletonGraphic Tint Black` | `SkeletonGraphic` variant, supports Additive with `CanvasGroup` |
| `Spine/Sprite` (Unlit / Vertex Lit / Pixel Lit) | Advanced configurable shaders — normal maps, metallic, emission, cel-shading ramps, rim lighting |
| `Spine/Special` (Grayscale, Ghost) | Ghost is the trail-rendering variant used by `SkeletonGhost` |
| `Spine/Blend Modes` (PMA Additive, Multiply, Screen) | For slot blend modes beyond Normal |
| `Spine/Outline` (incl. `Spine/Outline/OutlineOnly-ZWrite`) | Outline variants; the ZWrite variant is meant for combined-mesh rendering |

### Tint Black setup
Enable `Advanced → Tint Black` on the `SkeletonAnimation`/`SkeletonRenderer` component. For `SkeletonGraphic`, additionally enable TexCoord1 and TexCoord2 under the Canvas's Additional Shader Channels. The Additive blend variant on `SkeletonGraphic` also requires enabling "CanvasGroup Compatible" on both the shader and the component.

### URP shaders (extension package)
Separate UPM package. **Do not use with `SkeletonGraphic` or the Deferred rendering path.**

- 2D Renderer: `Universal Render Pipeline/2D/Spine/Skeleton`, `.../Skeleton Lit`, `.../Sprite`.
- 3D Forward Renderer: `Universal Render Pipeline/Spine/Skeleton`, `.../Skeleton Lit`, `.../Sprite`, `.../Outline/Skeleton-OutlineOnly`.

Example scenes: `com.esotericsoftware.spine.URP-shaders/Examples/3D/URP 3D Shaders.unity`, `2D/URP 2D Shaders.unity`, `Outline Shaders URP.unity`.

### LWRP shaders (extension package, legacy)
`Lightweight Render Pipeline/Spine/Skeleton`, `.../Skeleton Lit`, `.../Sprite`. Example scene: `com.esotericsoftware.spine.lwrp-shaders-4.2/Examples/LWRP Shaders.unity`.

## Post-processing interaction
Effects needing the z-buffer (e.g. Depth of Field) require z-write. Enable the shader's "Depth Write" option, or switch the material's Render Queue from Transparent to AlphaTest — some Render Pipeline Assets need both changes together.

## PMA vs. straight alpha
- **Premultiplied Alpha (PMA)** — RGB pre-multiplied by alpha; blend mode `Blend One OneMinusSrcAlpha`; lets Normal and Additive slot blend modes share a single-pass shader via PMA vertex colors. Was the default until spine-unity 4.2.
- **Straight Alpha** — RGB not pre-multiplied; either the standard `Blend SrcAlpha OneMinusSrcAlpha` (no Additive slots), or a shader-level conversion: `#if defined(_STRAIGHT_ALPHA_INPUT) texColor.rgb *= texColor.a; #endif`.

Enable `Advanced → PMA Vertex Colors` on `SkeletonRenderer`/`SkeletonGraphic` whenever the material is using PMA. See faq.md's Visual section for the specific artifacts (dark borders, washed-out colors, colorful stripes) each mismatch produces, and root-links.md's link to spine-unity-assets for the import-side setting.

## Writing a custom Spine shader
- `Cull Off` is mandatory — flipped/negatively-scaled skeletons need both faces rendered.
- No normals by default — enable `Advanced → Add Normals` if the shader needs lighting.
- No tangents by default — enable `Advanced → Solve Tangents` if the shader needs normal maps.
- Multiply texture by vertex color for PMA, with `Advanced → PMA Vertex Colors` enabled to match.
- Correct blend mode for the chosen alpha workflow: `Blend One OneMinusSrcAlpha` (PMA) or `Blend SrcAlpha OneMinusSrcAlpha` (straight).
- Keep the UI/non-UI shader split strict: UI (`CanvasRenderer`-compatible) shaders only ever go on `SkeletonGraphic`; non-UI shaders only ever go on `SkeletonAnimation`/`SkeletonMecanim`.

`Spine/Skeleton`'s own shader demonstrates the pattern: PMA blend (`Blend One OneMinusSrcAlpha`), `ZWrite Off`, `Cull Off`, `return (texColor * i.vertexColor)` for tint/blend application, a `"ShadowCaster"` pass with an alpha-threshold clip, and an optional `#pragma shader_feature _STRAIGHT_ALPHA_INPUT` toggle.

No official Shader Graph nodes exist for Spine; straight-alpha-exported textures work fine with ordinary non-Spine shaders. Community Amplify Shader Editor templates exist on the forum. Starting from an existing Spine shader is the fastest path to a working custom one.

## Z-spacing
When enabling z-write or using a non-transparent shader, set `Advanced → Z-Spacing` to a non-zero value on `SkeletonRenderer`/`SkeletonGraphic` to avoid Z-fighting (especially under lighting) — depth-buffer writing can also cause aliasing at semi-transparent edges, which Z-Spacing doesn't fully solve on its own.

# FAQ — Import, Visual, Performance, Licensing Q&A

Source: [spine-unity-faq](https://esotericsoftware.com/spine-unity-faq).

## Unity compatibility
- **Which Unity versions are compatible with my spine-unity runtime?** Check the Compatible Unity Versions table on the [installation page](https://esotericsoftware.com/spine-unity-installation#Compatible-Unity-Versions) for the supported range per runtime version.
- **Compile errors mentioning Unity methods — is my Unity version supported?** Confirm the Unity version is one officially supported by the installed spine-unity runtime, per the same table.

## Import
- **"Could not automatically set the AtlasAsset for .."** — the atlas file must use the `.atlas.txt` extension, not `.atlas`. Also check for missing attachments via the Find and Replace window with "Missing images" enabled.
- **"Failed to read version info at skeleton"** — the export was made selecting a lower Spine version than the actual editor (e.g. exporting as 4.2 from a 4.3 project). That kind of lower-version export exists only for importing into a lower-version *Spine Editor* — a runtime can't load it directly; re-export at the matching version instead.
- **"Opening scene in read-only package!"** — a Unity bug prevents opening example scenes directly from a git-sourced UPM package. Copy the scene files into the project's own `Assets` directory via a file manager first.

## Workflows — straight alpha vs. PMA
Use **straight alpha** when: the project uses Linear color space (Unity's default), might switch color spaces later, needs compatibility with standard (non-Spine) Unity shaders, or a simpler workflow is preferred. Use **PMA** when: the project uses Gamma color space exclusively, mipmap quality at transparent edges matters, and the team understands PMA's workflow limitations. See rendering.md's PMA-vs-straight-alpha section for the shader-level mechanics.

## Visual symptoms and root causes
- **Dark borders around transparent areas** — usually exported as PMA but imported/rendered with mismatched settings; PMA isn't supported under Linear color space at all. Straight alpha with mipmaps can also show this if transparent-pixel color bleed is missing.
- **Washed-out/desaturated colors** — almost always Linear color space (the default) combined with PMA-oriented auto-import settings, which sets `sRGB (Color Texture)` incorrectly. Only straight alpha works correctly under Linear; switch to Gamma color space (`Project Settings → Player → Other Settings → Color Space`) only if PMA is actually required.
- **Colorful stripes in transparent areas** — exported as straight alpha but imported/rendered as if PMA. See the Premultiplied vs. Straight Alpha Import section on the spine-unity-assets page (root-links.md).
- **White borders around attachments with Generate Mip Maps enabled** — PMA textures with `sRGB (Color Texture)` incorrectly left enabled.
- **Wrong colors specifically with Tint Black** — confirm `Advanced → Tint Black` is actually enabled on the `SkeletonRenderer`/`SkeletonAnimation` component, not just on the shader/material.
- **Can't assign a material directly on the MeshRenderer** — expected: `SkeletonRenderer` rebuilds the Materials array every frame. Use `SkeletonRendererCustomMaterials`/`CustomMaterialOverride`/`CustomSlotMaterials` instead (rendering.md).
- **Spine shaders look wrong in URP** — the base runtime only ships Built-in Render Pipeline shaders; install the separate URP Shaders extension UPM package (rendering.md).
- **Outline shader shows only outlines in URP** — either a Built-in outline shader is being used under URP (switch to the URP outline shader), or a single-pass outline-only shader is in use where a combined render is needed; use `RenderExistingMesh` to re-render with the outline shader as a second pass.
- **Outline shader shows unwanted inner outlines between skeleton parts** — caused by multiple materials producing separately-outlined submeshes. Reduce to a single material via atlas packing or runtime repacking (main-components.md's Combining Skins section), or use `RenderCombinedMesh` with an outline-only shader.
- **Normal map looks wrong** — confirm `Advanced → Solve Tangents` is enabled on the `SkeletonRenderer`.
- **SkeletonGraphic brightens during a CanvasGroup alpha fade** — see main-components.md's CanvasGroup-alpha section.
- **Skeleton parts show through each other during an alpha fade** — the standard overlapping-triangle transparency artifact; see rendering.md's "Fading a skeleton in/out" guidance (RenderTexture-based fade, not a naive alpha reduction).
- **Repacked skin renders fine in the Editor but shows white polygons in a build** — check the runtime-repacking failure checklist in main-components.md (Read/Write enabled, Compression `None`, full-resolution quality tier, power-of-two source texture).

## Inconsistent behavior across machines
- **Project behaves differently on different machines when using a git UPM URL** — a URL ending in `#4.3` always resolves to the branch's *latest* commit, so different machines pulling at different times get different code. Pin to a specific commit hash instead (e.g. `#5e8e4c21f11603ba1b72c220369d367582783744`).
- **Getting a commit hash for the Package Manager URL** — open the [GitHub commits page](https://github.com/EsotericSoftware/spine-runtimes/commits/4.3) for the target branch and copy the full SHA via the commit's copy button.

## Performance
- **FPS drop or GC allocation when instantiating a skeleton** — switch the export from `.json` to binary `.skel.bytes`; load skeletons at level-load time; use object pooling instead of Instantiate/Destroy (pre-warm ~10 instances); enable/reposition pooled instances instead of instantiating new ones; on despawn, disable the GameObject and call `AnimationState.ClearTracks()` instead of destroying it.
- **Many draw calls/batches/materials for one skeleton** — usually multiple atlas pages, or slots alternating blend modes. See rendering.md's Materials / Material Switching and Draw Calls sections; consider runtime repacking (main-components.md).
- **General skeleton performance improvement checklist**: avoid clipping-attachment polygons where Unity masking would do instead, and minimize clipping-polygon vertex count when clipping is unavoidable; minimize mesh-deformation keys; minimize overall vertex count; remove unnecessary keyframes; audit via the [Metrics view](https://esotericsoftware.com/spine-metrics#Metrics-view); minimize the number of atlas page textures; order attachments in draw order to minimize material switches; share a single larger atlas across multiple skeletons via the `SkeletonDataAsset`'s atlas array instead of one atlas per skeleton.

## Licensing
A Spine license is required to integrate the Spine Runtimes into any application.

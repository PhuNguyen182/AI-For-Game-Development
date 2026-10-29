# FAQ — symptom to cause

Page: faq. Most visual faults trace to one alpha-workflow or Color Space mismatch, not a shader defect. Linear Color Space (Unity default) does not support PMA, so a default project has effectively chosen straight alpha.

| Choose | When |
|---|---|
| Straight alpha | Linear space, possible later colour-space switch, standard non-Spine shaders, simpler workflow |
| PMA | Gamma space only, mipmap quality at transparent edges matters, PMA workflow limits accepted |

## Import
| Symptom | Cause / fix |
|---|---|
| Compile errors naming Unity methods | Unity version outside the runtime's range — Installation page, Compatible Unity Versions |
| "Could not automatically set the AtlasAsset for .." | Atlas must be `.atlas.txt`, not `.atlas`; also Find and Replace with "Missing images" enabled |
| "Failed to read version info at skeleton" | Export targeted a lower Spine version (only for importing into a lower-version Spine *Editor*) — re-export at the matching version |
| "Opening scene in read-only package!" | Unity bug with example scenes from a git UPM package — copy scenes into `Assets` |
| Behaviour differs per machine with a git UPM URL | `#4.3` resolves to the branch's latest commit — pin a full commit SHA (from `github.com/EsotericSoftware/spine-runtimes/commits/4.3`) |

## Visual
| Symptom | Cause / fix |
|---|---|
| Dark borders around transparency | PMA exported but imported/rendered mismatched; straight alpha with mipmaps and no transparent-pixel colour bleed does it too |
| Washed-out colours | Linear space + PMA-oriented auto-import wrongly setting `sRGB (Color Texture)`; Gamma only if PMA is genuinely required |
| Colourful stripes in transparency | Straight alpha exported but imported/rendered as PMA (Assets page, premultiplied-vs-straight import) |
| White borders with Generate Mip Maps | PMA textures with `sRGB (Color Texture)` left on |
| Wrong colours only with Tint Black | `Tint Black` on the material but not on the component |
| Material on `MeshRenderer` does not stick | Rebuilt every frame — custom-materials components ([rendering.md](rendering.md)) |
| Shaders wrong under URP | Base runtime ships Built-in shaders only — install the URP Shaders extension package |
| Outline shows only outlines under URP | Built-in outline shader under URP (use the URP one), or single-pass outline-only where a combined render is needed (`RenderExistingMesh` second pass) |
| Unwanted inner outlines between parts | Multiple materials → separately outlined submeshes; one material via atlas packing/repacking, or `RenderCombinedMesh` with an outline-only shader |
| Normal map wrong | `Solve Tangents` off on the renderer |
| `SkeletonGraphic` brightens in `CanvasGroup` fade | [main-components.md](main-components.md) |
| Parts show through each other in a fade | Render-texture fade ([utility-components.md](utility-components.md)) |
| Repacked skin fine in Editor, white polygons in build | Repack precondition failed ([skeleton-api.md](skeleton-api.md)) |

## Performance
| Symptom | Cause / fix |
|---|---|
| FPS drop / GC on instantiate | Export binary `.skel.bytes`, not `.json`; load at level load; pool (pre-warm ~10); on despawn disable and `AnimationState.ClearTracks()`, not destroy |
| Many draw calls/materials for one skeleton | Multiple atlas pages or alternating slot blend modes ([rendering.md](rendering.md)); consider runtime repacking |

Checklist: avoid clipping attachments where Unity masking works, minimise their vertices; minimise mesh-deformation keys, vertex count and redundant keys; audit in the Metrics view (`esotericsoftware.com/spine-metrics`); minimise atlas pages and order attachments to cut material switches; share one larger atlas across skeletons via the `SkeletonDataAsset` atlas array.

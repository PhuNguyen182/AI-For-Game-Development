# Shadows

Docs: Manual `Shadows`, shadow cascades, shadow distance, troubleshooting shadows; URP shadow pages; API `UniversalRenderPipelineAsset`, `UniversalAdditionalLightData`. Owning asset per setting: see SKILL.md.

Cost is set by how much world the map covers, not by texel count: lowering distance usually fixes soft shadows where raising resolution does not.

## Distance and cascades
| Setting | Decides |
|---|---|
| Shadow distance | Radius where realtime shadows exist; halving roughly quarters the area one map covers. First lever |
| Cascade count (2 or 4) | Splits the same distance into nested maps; does not extend reach |
| Cascade splits | Boundaries as fractions of distance; defaults suit a ground camera, top-down/long sightlines need redistribution. Visualize cascades in the Scene view to check |
| Border / fade | Too narrow = visible cut line on the ground |
| Cost | Each cascade re-renders the casters it holds: four cascades is near four passes |
| Applies to | Directional only; point/spot get one map each (point = cube) |

## Bias
| Symptom | Lever |
|---|---|
| Acne (striped self-shadowing) | Normal bias first: barely disturbs contact |
| Peter-panning (shadow detaches, object floats) | Too much depth bias: reduce, take remaining acne on normal bias |
| Acne no bias fixes | Resolution or distance: too few texels for the area; more bias trades artifacts |
| `shadowNearPlane` | Raise it to recover precision when casters are all far from the light |

## Resolution (URP)
- `mainLightShadowmapResolution`: split across cascades (2048 with four = 1024 each).
- `additionalLightsShadowmapResolution`: one atlas for all shadow-casting point/spot lights; more casters = smaller slices.
- Low/Medium/High tiers on the Asset; each additional light selects one.
- `supportsSoftShadows` is a pipeline-wide gate: off = Soft lights render hard, silently.
- `conservativeEnclosingSphere` fixes caster pop-out at cascade edges; off by default, existing projects must opt in.
- Screen space shadows: an extra full-screen pass; only where map resolution cannot give the contact quality.

## `UniversalAdditionalLightData`
- `additionalLightsShadowResolutionTier`: which Asset tier the light uses.
- `usePipelineSettings`: Asset bias vs the light's own; why a per-light bias edit can appear to do nothing.
- `softShadowQuality`: per-light filtering, independent of the pipeline toggle.
- `customShadowLayers`/`shadowRenderingLayers`: casters differ from lit objects; see [rendering-layers.md](rendering-layers.md).

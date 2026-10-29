# Light Sources

Docs: Manual `Lighting` pages (light types, Light component reference, cookies, `urp/light-limits`); API `Light`, `LightRenderMode`, `LightmapBakeType`.

## Types
| Type | Capability and trap |
|---|---|
| Directional | Infinite parallel light. Position ignored (only rotation read); no Range; the only type with cascaded shadows |
| Point | Omnidirectional, bounded by Range. Shadow = cube map (six faces): first to disable on a budget |
| Spot | Cone (`spotAngle`, `innerSpotAngle`), bounded by Range. `enableSpotReflector` redistributes intensity by cone width, so narrowing brightens |
| Area (Rectangle, Disc, Tube) | Baked only; inert at runtime, reports nothing |

`LightShape` is obsolete; shape variants live on `LightType` (`Spot`, `Pyramid`, `Box`, `Rectangle`, `Disc`, `Tube`).

## Intensity and units
- `intensity` is meaningless without `lightUnit` (lux vs lumen vs candela): an imported or copied light can be orders of magnitude off.
- `luxAtDistance`: reference distance of a directional light's lux under physical units.
- `colorTemperature` only applies with `useColorTemperature` on; otherwise it is shown and does nothing.
- `bounceIntensity` scales indirect only and is bake-time.
- `renderMode` (`ForcePixel`/`ForceVertex`) is Built-in only; URP's equivalent lever is the light limit.

## Range, angle, cookies
- `range` is a hard cutoff, not a falloff: a light stopping short needs more range, not intensity.
- Equal `spotAngle` and `innerSpotAngle` give a hard-edged cone, usually an artifact.
- `cookie` masks light shape cheaply (window bars, foliage); directional cookies tile, sized by `cookieSize2D`.
- `areaSize`/`shapeRadius` are read at bake time only.

## Scoping
- `cullingMask`: under an SRP it does not scope the shadow pass, so an excluded object can still cast a shadow; see [rendering-layers.md](rendering-layers.md).
- `renderingLayerMask`: the SRP mask; filters shadow rendering.
- `lightmapBakeType` (Light Mode): see [global-illumination.md](global-illumination.md).

## How many lights (URP)
- Forward: lights beyond the per-object additional-light limit are dropped for that renderer; the scene still looks lit while objects lose lights and flicker. Documented symptom, not a bug. Check the count first when lights flicker or vanish (`Troubleshooting lights flickering`).
- Forward+: no per-object limit, a per-camera cap instead. The path choice is `unity-urp-rendering`'s; this constraint is its input.
- Each shadow-casting additional light takes a slice of the additional-light shadow atlas: more casters = smaller slices.

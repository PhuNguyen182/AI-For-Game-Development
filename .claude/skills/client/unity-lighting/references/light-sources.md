# Light Sources — Types, Parameters, and URP Light Limits

Sources: [Light sources](https://docs.unity3d.com/Manual/lighting-light-sources.html), [Types of Light component](https://docs.unity3d.com/Manual/Lighting.html), [Light component Inspector reference](https://docs.unity3d.com/Manual/class-Light.html), [Light API](https://docs.unity3d.com/ScriptReference/Light.html), [Light limits in URP](https://docs.unity3d.com/Manual/urp/lighting/light-limits-in-urp.html).
Covers: SKILL.md §4 — **"Choose the light type by what it can do, not by how it looks in the viewport"**.

Four light types, and the differences that matter between them are not
visual — they are about what each one is capable of participating in. Two of
the four ignore a property the Inspector still shows for them, and one does
nothing at all outside a bake.

## Contents

- [Types](#types)
- [Intensity and units](#intensity-and-units)
- [Range, angle, and cookies](#range-angle-and-cookies)
- [Scoping which objects a light reaches](#scoping-which-objects-a-light-reaches)
- [How many lights](#how-many-lights)

## Types

| Type | What it can do, and what it ignores | Source |
|---|---|---|
| Directional | Infinite parallel light. **Position is ignored entirely** — only rotation is read, so moving the sun object does nothing. Has no Range. The only type that gets cascaded shadows | [Types of Light component](https://docs.unity3d.com/Manual/Lighting.html) |
| Point | Omnidirectional from a position, bounded by Range. Its shadow costs a cube map — six faces — which is why point-light shadows are the first to disable on a budget | [Types of Light component](https://docs.unity3d.com/Manual/Lighting.html) |
| Spot | A cone with Spot Angle and Inner Spot Angle, bounded by Range. `enableSpotReflector` redistributes intensity by cone width, so narrowing the cone brightens it rather than only masking it | [Light API](https://docs.unity3d.com/ScriptReference/Light.html) |
| Area — Rectangle, Disc, Tube | **Baked only.** Contributes through the lightmapper and is inert at runtime, so a realtime Area light produces nothing and reports nothing | [Types of Light component](https://docs.unity3d.com/Manual/Lighting.html) |

`LightShape` is obsolete; the shape variants live on `LightType` — `Spot`,
`Pyramid`, `Box`, `Rectangle`, `Disc`, `Tube`.

## Intensity and units

| Member | What it decides | Source |
|---|---|---|
| `intensity` | Meaningless without knowing `lightUnit` — the same number is a different brightness in lux than in lumen or candela, which is why an imported or copied light can be orders of magnitude off | [Light.lightUnit](https://docs.unity3d.com/ScriptReference/Light-lightUnit.html) |
| `luxAtDistance` | The distance a directional light's lux value is defined at, when physical units are in use | [Light.luxAtDistance](https://docs.unity3d.com/ScriptReference/Light-luxAtDistance.html) |
| `useColorTemperature` / `colorTemperature` | Drives colour in Kelvin instead of the RGB swatch. With it off, `colorTemperature` is present in the Inspector and does nothing | [Light.colorTemperature](https://docs.unity3d.com/ScriptReference/Light-colorTemperature.html) |
| `bounceIntensity` | Scales the light's **indirect** contribution only. A bake-time value — changing it at runtime on a baked light changes nothing until a re-bake | [Light.bounceIntensity](https://docs.unity3d.com/ScriptReference/Light-bounceIntensity.html) |
| `renderMode` | `ForcePixel` or `ForceVertex` on the Built-in pipeline — vertex lighting is far cheaper and far coarser. Has no URP counterpart; URP's equivalent lever is the light limit | [LightRenderMode](https://docs.unity3d.com/ScriptReference/LightRenderMode.html) |

## Range, angle, and cookies

| Member | What it decides | Source |
|---|---|---|
| `range` | A **hard cutoff**, not a physical falloff. A light that stops short of where it is wanted needs more range; raising intensity instead blows out everything inside the existing radius and reaches no further | [Light.range](https://docs.unity3d.com/ScriptReference/Light-range.html) |
| `spotAngle` / `innerSpotAngle` | Outer cone and the angle at which falloff begins. Equal values give a hard-edged cone, which reads as an artifact more often than as a style | [Light.spotAngle](https://docs.unity3d.com/ScriptReference/Light-spotAngle.html) |
| `cookie` | A texture masking the light's shape — the cheap way to get window bars or foliage break-up without geometry. Directional cookies tile across the scene and are sized by `cookieSize2D` | [Cookies](https://docs.unity3d.com/Manual/Cookies.html) |
| `areaSize` / `shapeRadius` | Area light dimensions, read only at bake time | [Light.areaSize](https://docs.unity3d.com/ScriptReference/Light-areaSize.html) |

## Scoping which objects a light reaches

| Member | What it decides | Source |
|---|---|---|
| `cullingMask` | Layer-based exclusion. Under an SRP this does **not** scope the shadow pass, so an excluded object can still cast a shadow from that light — see [rendering-layers.md](rendering-layers.md) | [Light.cullingMask](https://docs.unity3d.com/ScriptReference/Light-cullingMask.html) |
| `renderingLayerMask` | The SRP-era mask, matched against each `Renderer.renderingLayerMask`, and the one that filters shadow rendering | [Light.renderingLayerMask](https://docs.unity3d.com/ScriptReference/Light-renderingLayerMask.html) |
| `lightmapBakeType` | `Realtime`, `Baked`, or `Mixed` — the Light Mode, covered in [global-illumination.md](global-illumination.md) | [LightmapBakeType](https://docs.unity3d.com/ScriptReference/LightmapBakeType.html) |

## How many lights

| Constraint | What it produces when exceeded | Source |
|---|---|---|
| Forward — additional lights per object | Lights beyond the per-object limit are dropped **for that renderer**, so the scene still looks lit while individual objects lose lights and flicker as the set is re-evaluated. This is the documented symptom, not a bug | [Light limits in URP](https://docs.unity3d.com/Manual/urp/lighting/light-limits-in-urp.html) |
| Forward+ | Removes the per-object limit, at a per-camera cap instead. Choosing the path is `unity-urp-rendering`'s decision, which this constraint is the input to | [Light limits in URP](https://docs.unity3d.com/Manual/urp/lighting/light-limits-in-urp.html) |
| Shadow-casting additional lights | Each one takes a slice of the additional-light shadow atlas; more casters means less resolution each, not more atlas | [Shadows in URP](https://docs.unity3d.com/Manual/urp/Shadows-in-URP.html) |
| Lights flickering or disappearing | Unity documents this symptom against the light limit directly — check the count before investigating anything else | [Troubleshooting lights flickering](https://docs.unity3d.com/Manual/urp/ts-lights-flicker-disappear.html) |

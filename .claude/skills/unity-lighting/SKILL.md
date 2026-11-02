---
name: unity-lighting
description: "Built-in/URP lighting: baked/mixed/realtime GI, Light Probes, Reflection Probes, cascades. Use for lighting, bakes."
user-invocable: false
---

# Unity Lighting

- **Not for:** pipeline choice (`render-pipeline-urp-hdrp`).
- **Not for:** HDRP pipeline settings and the APV enable toggle on HDRP (`unity-hdrp-rendering`).
- **Not for:** rendering path, Renderer Features and `Light2D` (`unity-urp-rendering`).
- **Not for:** post-process Volumes (`unity-post-processing`).
- **Not for:** shader content (`shader-authoring`).
- **Not for:** entity subscene rendering and its lighting limits (`unity-entities-graphics`).
- **Not for:** gameplay rules that read light state, such as stealth (Core, `csharp-engineer`).
- **Docs:** https://docs.unity3d.com/Manual/ (`LightingOverview`, `lighting-reference`, `urp/lighting-landing`) and `ScriptReference/Light`, `RenderSettings`.
  - **SRP package pages:** pinned `@17.6`.
  - **Unversioned Manual links:** resolve to current docs, so confirm any quoted default against the installed Editor.

## References
- **[light-sources.md](references/light-sources.md):** Placing or tuning lights, or lights vanish from some objects.
- **[global-illumination.md](references/global-illumination.md):** Anything is baked, or a bake came out wrong.
- **[shadows.md](references/shadows.md):** Tuning shadow cost or quality, acne or peter-panning.
- **[reflections.md](references/reflections.md):** A surface must reflect its surroundings, not only the skybox.
- **[probe-volumes.md](references/probe-volumes.md):** Dynamic objects need baked indirect light, or light leaks through walls.
- **[rendering-layers.md](references/rendering-layers.md):** One light must affect only some renderers, including across an APV boundary.
- **[custom-lighting-api.md](references/custom-lighting-api.md):** A custom lit URP shader must read Unity's lights.

## Which asset owns which setting
- **Built-in RP:** reads Quality Settings and `RenderSettings`.
- **URP:** reads its own Asset for the same concepts.
- **Editing the wrong one:** is accepted, saved and has no effect.

| Setting | Built-in | URP |
|---|---|---|
| Shadow distance, cascades | `QualitySettings.shadowDistance`, `shadowCascades`, `shadowCascade2Split`/`4Split` | `UniversalRenderPipelineAsset.shadowDistance`, `shadowCascadeCount`, `cascade2Split`–`cascade4Split` |
| Shadow resolution | `QualitySettings.shadowResolution`, `Light.shadowCustomResolution` | `mainLightShadowmapResolution`, `additionalLightsShadowmapResolution`, three per-light tiers on the Asset |
| Per-light shadow tier, soft quality, shadow layers | n/a | `UniversalAdditionalLightData` (added beside the `Light`) |
| Shadowmask mode | `QualitySettings.shadowmaskMode` | Same field, still read under URP |
| Ambient, skybox, fog | `RenderSettings`, Lighting window Environment tab | Same; not duplicated on the Asset |
| Adaptive Probe Volumes | Not supported | Toggle on the pipeline Asset (set here on URP) |

## Steps
1. **Confirm the pipeline and which asset owns the setting:** see the table above.
2. **Choose the light type by capability:** per [light-sources.md](references/light-sources.md):
   - **Area:** bake-only.
   - **Directional:** ignores position.
   - **Point/Spot Range:** a hard cutoff, so raising intensity only blows out the near field.
3. **Set each light's Mode before authoring around it:** per [global-illumination.md](references/global-illumination.md).
   - **Realtime/Baked/Mixed:** a bake-time setting, so changing the Mode later invalidates the bake.
   - **Lighting Mode:** the scene's single Lighting Mode applies to every Mixed light.
4. **Flag geometry (Contribute GI) and give it lightmap UVs before blaming the lightmapper:** both failures report success.
5. **Spend shadow budget on distance before resolution:** per [shadows.md](references/shadows.md).
   - **Cascades:** they subdivide the distance, they do not extend it.
   - **Per-tier values on the pipeline Asset:** `unity-performance-engineer`'s; state the need, and `unity-performance-engineer` sets them.
6. **Fix acne with normal bias before depth bias:** depth bias detaches contact shadows (peter-panning).
7. **Pick Reflection Probe mode by whether the reflected content changes:** per [reflections.md](references/reflections.md).
   - **Box projection:** fit it to the real room.
8. **Default to Adaptive Probe Volumes over a legacy Light Probe Group:** per [probe-volumes.md](references/probe-volumes.md).
   - **Android low-end tier:** keep APV only after a measured cost within budget, else Light Probe Groups.
   - **APV enablement:** confirm APV is enabled on the pipeline Asset first, because volumes bake and render nothing otherwise.
   - **Volume size:** the traversable space, not the whole level.
9. **Treat an APV leak as placement before bias:** a Probe Adjustment Volume or a rendering layer mask removes the cause; leak-reduction bias only trades artifacts.
10. **Scope lights with Rendering Layers, not culling masks, under an SRP:** per [rendering-layers.md](references/rendering-layers.md).
    - **Rendering Layers:** enable them on the Asset first.
11. **Supply the lighting HLSL surface and hand the shader off:** per [custom-lighting-api.md](references/custom-lighting-api.md).
12. **Attach a measurement to any performance claim:** bake time, frame time or memory on the claimed tier, per `csharp-standards` → `performance-and-algorithms.md` Verification.
13. **Device or tier:** verify on one, and name it with the bake time and frame time measured.

## Never
- **Treat Light Mode as a runtime switch:** a runtime write to `lightmapBakeType` re-lights nothing.
- **Give two Mixed lights different Lighting Modes:** the mode is scene-wide and the Inspector will not warn.
- **Leave a Realtime Reflection Probe on every-frame refresh without time slicing:** it costs six face renders, invisible in the Inspector.
- **Rely on a light's culling mask to keep an object out of its shadows under an SRP:** the shadow pass filters on rendering layer mask.
- **Use obsolete `LightShape` in new SRP work:** use `LightType.Spot`/`Pyramid`/`Box`.
- **Use obsolete `LightProbeProxyVolume` in new SRP work:** use APV.

## Output
```
## Lighting — <scene or feature>
- Pipeline / owning asset: <Built-in / URP version / HDRP — asset edited>
- Lights: <type, intensity+unit, range, Mode> — scene Lighting Mode: <Baked Indirect / Shadowmask / Subtractive>
- Bake: <lightmapper, resolution, Contribute GI coverage, lightmap UV source, bake time>
- Dynamic-object lighting: <APV density + Baking Set / Light Probes / none>
- Shadows: <distance, cascades and splits, bias, resolution tier>
- Reflections / Rendering Layers: <probe modes, box fit — layers and Asset enablement — or "unused">
```

## Example
- **"Objects stop being lit in the crowded market":** not a bake bug, Forward's per-object additional-light limit drops lights per renderer.
  - **Did instead:** confirmed the count, cut overlapping decorative point lights.
  - **Routed:** the Forward+ choice to `unity-urp-rendering`.

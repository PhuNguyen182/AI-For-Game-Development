# Cross-Pipeline Effect Availability

Source: Manual `post-processing-effect-availability-reference.html` (6000.5). Gaps run both ways; a missing effect has no error state, it is just absent from the Add list.

| Effect | Built-in (PPv2) | URP | HDRP |
|---|---|---|---|
| Auto Exposure | yes | **no** | yes (Exposure) |
| Fog | yes (Deferred Fog) | **no** (Lighting-window setting) | yes (Fog) |
| Screen Space Reflection | yes | **no** | yes |
| Panini Projection | **no** | yes | yes |
| Shadows Midtones Highlights | **no** | yes | yes |
| Split Toning | **no** | yes | yes |
| Color Lookup | no separate effect; `ColorGrading` External mode | yes | yes |

Present in all three: Ambient Occlusion, Bloom, Channel Mixer, Chromatic Aberration, Color Adjustments, Color Curves, Depth of Field, Film Grain (PPv2: Grain), Lens Distortion, Lift Gamma Gain, Motion Blur, Tonemapping, Vignette, White Balance, post-process anti-aliasing.

## Same effect, different shape
- PPv2 `ColorGrading` folds Channel Mixer, Color Adjustments, Color Curves, Lift Gamma Gain, White Balance and tonemapping into one class; no standalone tonemapper type.
- Anti-aliasing: Camera setting in URP, `PostProcessLayer` setting in PPv2; in neither is it in an effect list.
- Ambient Occlusion: Renderer Feature in URP, effect in PPv2 and HDRP.
- HDRP renames some overrides (Exposure, Fog); HDRP work routes to `unity-hdrp-rendering`.

Unverified: per-effect HDRP/PPv2 links on the source page were read off the table, and two rows pin older package versions; check the installed package before trusting a property list.

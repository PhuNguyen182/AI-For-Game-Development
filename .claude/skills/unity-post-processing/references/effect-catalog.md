# URP Override Catalog: The Property That Decides

Source: Manual `urp/EffectList.html` and per-override pages. Several overrides overlap (three can warm an image, two darken edges), so select by mechanism.

| Override | Decides the result |
|---|---|
| Bloom | **Threshold**; below the sky/snow luminance the whole background blooms. Intensity and Scatter shape what Threshold selected |
| Tonemapping | **Mode** None/Neutral/ACES. ACES adds contrast and desaturates highlights, so a grade made before ACES reads differently. Needs HDR |
| Color Adjustments | **Post Exposure**, then Contrast, Saturation. Color Filter multiplies, tinting and darkening together: not for temperature |
| White Balance | **Temperature**, **Tint**: shifts the white point; the correct warm/cool tool |
| Color Curves | Per-channel and Hue-vs-Sat curves for targeted correction |
| Color Lookup | **Lookup Texture** + Contribution: externally authored LUT; cheapest art-directed grade with no runtime tuning |
| Lift, Gamma, Gain | Three-way trackballs (ASC CDL) |
| Shadows Midtones Highlights | As above plus **Shadow/Highlight Limits** that move the range boundaries |
| Split Toning | Shadows colour, Highlights colour, **Balance**: quick two-colour stylisation |
| Channel Mixer | Input-to-output channel mix; corrective |
| Depth of Field | Focus distance, aperture, blur: the focus pull. Expensive; first to drop on mobile |
| Motion Blur | **Mode**: Camera Only is cheap; Camera and Objects needs motion vectors and costs more. Intensity does nothing on moving objects without it |
| Vignette | Intensity, Smoothness, Center, Rounded. Draws attention, not mood; a low-health cue from Vignette alone reads as a camera artifact |
| Film Grain | Type, Intensity, **Response** (ties grain to luminance, keeps it out of highlights) |
| Chromatic Aberration | **Intensity** 0-1; 0 disables |
| Lens Distortion | Intensity, X/Y multipliers, Center, **Scale** (crops edges; skipping it leaves black corners) |
| Panini Projection | **Distance**: corrects wide-FOV edge stretching; a FOV fix, not stylisation |
| Screen Space Lens Flare | Built from the same bright areas Bloom reads, so retuning Bloom Threshold changes it |

## Not Volume Overrides
- Anti-aliasing (FXAA/SMAA/TAA): Camera setting under Rendering (`unity-urp-rendering`).
- Ambient Occlusion: Renderer Feature on the Renderer asset (`unity-urp-rendering`).
- Auto Exposure, Fog, Screen Space Reflection: absent from URP ([pipeline-availability.md](pipeline-availability.md)).

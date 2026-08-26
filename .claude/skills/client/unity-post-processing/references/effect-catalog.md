# URP Volume Override Catalog — What Each Effect Decides

Sources: [Post-processing Volume Overrides reference for URP](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/EffectList.html) and the individual override pages linked per row.
Covers: SKILL.md §4 — **"Pick each override from what it decides rather than from what it is called"**.

The overrides URP ships with, each reduced to the property that actually
decides the result. Several of these overlap in what they can express — three
separate overrides can warm an image, two can darken its edges — so the
selection below is by mechanism rather than by appearance, because the wrong
mechanism produces the right look on one shot and the wrong one on the next.

| Override | The property that decides the result | Source |
|---|---|---|
| Bloom | **Threshold** — luminance above which a pixel blooms. Set below the scene's own sky or snow luminance and the entire background blooms, which reads as a broken effect rather than a mis-set number. Intensity and Scatter shape what Threshold already selected | [Bloom](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/post-processing-bloom.html) |
| Tonemapping | **Mode** — None, Neutral, or ACES. ACES adds strong contrast and desaturates highlights as part of the transform, so a scene graded before ACES is applied will read differently afterwards. Requires HDR to have anything above one to remap | [Tonemapping](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/post-processing-tonemapping.html) |
| Color Adjustments | **Post Exposure** for overall level, then Contrast and Saturation. Color Filter multiplies the image, so it tints and darkens together — not the tool for a pure temperature shift | [Color Adjustments](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/Post-Processing-Color-Adjustments.html) |
| White Balance | **Temperature** and **Tint** — the correct mechanism for warming or cooling an image, because it shifts the white point instead of multiplying colour | [White Balance](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/Post-Processing-White-Balance.html) |
| Color Curves | Per-channel and Hue-versus-Sat curves — the tool for a targeted correction (one hue range oversaturating) rather than a global grade | [Color Curves](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/Post-Processing-Color-Curves.html) |
| Color Lookup | **Lookup Texture** plus Contribution — a full grade authored externally as a LUT strip, blended in by amount. The cheapest way to ship an art-directed grade that does not need runtime tuning | [Color Lookup](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/post-processing-color-lookup.html) |
| Lift, Gamma, Gain | Three-way trackballs over shadows, midtones, highlights — ASC CDL grading when a single Contrast control is too blunt | [Lift Gamma Gain](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/Post-Processing-Lift-Gamma-Gain.html) |
| Shadows Midtones Highlights | Same three tonal ranges, but with **Shadow Limits** and **Highlight Limits** defining where each range starts — use when the ranges themselves need moving, not just their colour | [Shadows Midtones Highlights](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/Post-Processing-Shadows-Midtones-Highlights.html) |
| Split Toning | Shadows colour, Highlights colour, **Balance** — a two-colour stylisation, narrower than the trackball overrides and faster to dial in | [Split Toning](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/Post-Processing-Split-Toning.html) |
| Channel Mixer | How much each input channel feeds one output channel — a corrective tool, rarely the right first reach for a look | [Channel Mixer](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/Post-Processing-Channel-Mixer.html) |
| Depth of Field | Focus distance, aperture, blur — the actual focus pull. Expensive, and the first effect to drop from a mobile tier | [Depth of Field](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/depth-of-field-urp.html) |
| Motion Blur | **Mode** — Camera Only is cheap; Camera and Objects requires motion vectors and costs meaningfully more. Intensity without the right Mode produces nothing on moving objects | [Motion Blur](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/Post-Processing-Motion-Blur.html) |
| Vignette | Intensity, Smoothness, Center, Rounded — darkens edges toward the centre. Reaches for attention, not for mood; a low-health cue built from Vignette alone reads as a camera artifact | [Vignette](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/post-processing-vignette.html) |
| Film Grain | Type, **Intensity**, Response — Response ties grain strength to luminance, so grain can be kept out of highlights where it reads as noise | [Film Grain](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/Post-Processing-Film-Grain.html) |
| Chromatic Aberration | **Intensity** only, 0–1, where 0 disables the effect entirely | [Chromatic Aberration](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/post-processing-chromatic-aberration.html) |
| Lens Distortion | Intensity plus X/Y multipliers, Center, Scale — Scale exists to crop away the edges distortion pulls in, and skipping it leaves black corners | [Lens Distortion](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/Post-Processing-Lens-Distortion.html) |
| Panini Projection | **Distance** — corrects the stretching a wide field of view produces at frame edges, keeping vertical lines straight. A field-of-view fix, not a stylisation | [Panini Projection](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/Post-Processing-Panini-Projection.html) |
| Screen Space Lens Flare | Generates flares and streaks from the **same bright areas Bloom reads**, so its result changes whenever Bloom's Threshold is retuned | [Screen Space Lens Flare](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/shared/lens-flare/post-processing-screen-space-lens-flare.html) |

## Not in this list

| Effect | Where it actually lives | Source |
|---|---|---|
| Anti-aliasing (FXAA, SMAA, TAA) | A **Camera** setting under Rendering, not a Volume Override — searching the override catalog for it finds nothing | [Camera component reference](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/camera-component-reference.html) |
| Ambient Occlusion | A **Renderer Feature** on the URP Renderer asset, owned by `unity-urp-rendering`, not a Volume Override | [SSAO in URP](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/post-processing-ssao.html) |
| Auto Exposure, Fog, Screen Space Reflection | Not present in URP at all — see [pipeline-availability.md](pipeline-availability.md) | [Effect availability reference](https://docs.unity3d.com/6000.5/Documentation/Manual/post-processing-effect-availability-reference.html) |

# Cross-Pipeline Effect Availability

Source: [Post-processing effect availability reference](https://docs.unity3d.com/6000.5/Documentation/Manual/post-processing-effect-availability-reference.html), the Unity 6000.5 comparison table across Built-in RP (through the Post Processing v2 package), URP, and HDRP.
Covers: SKILL.md §4 — **"Check the effect exists on the target pipeline before designing around it"**.

The three pipelines' effect sets overlap but do not match, and the gaps run in
both directions — URP is missing effects the older Built-in stack has, not
only the reverse. A look designed against one pipeline's catalog and then
moved is where this bites, because the missing effect has no error state: it
simply is not in the list to add.

## Absent by pipeline

| Effect | Built-in RP (PPv2) | URP | HDRP | Source |
|---|---|---|---|---|
| Auto Exposure | yes | **no** | yes (Exposure override) | [Availability reference](https://docs.unity3d.com/6000.5/Documentation/Manual/post-processing-effect-availability-reference.html) |
| Fog | yes (Deferred Fog) | **no** — URP fog is a Lighting-window setting, not a post-process | yes (Fog override) | [Availability reference](https://docs.unity3d.com/6000.5/Documentation/Manual/post-processing-effect-availability-reference.html) |
| Screen Space Reflection | yes | **no** | yes | [Availability reference](https://docs.unity3d.com/6000.5/Documentation/Manual/post-processing-effect-availability-reference.html) |
| Panini Projection | **no** | yes | yes | [Availability reference](https://docs.unity3d.com/6000.5/Documentation/Manual/post-processing-effect-availability-reference.html) |
| Shadows Midtones Highlights | **no** | yes | yes | [Availability reference](https://docs.unity3d.com/6000.5/Documentation/Manual/post-processing-effect-availability-reference.html) |
| Split Toning | **no** | yes | yes | [Availability reference](https://docs.unity3d.com/6000.5/Documentation/Manual/post-processing-effect-availability-reference.html) |
| Color Lookup | **no** as a separate effect — PPv2 exposes LUTs through `ColorGrading`'s External mode | yes | yes | [Color Grading (PPv2)](https://docs.unity3d.com/Packages/com.unity.postprocessing@3.5/api/UnityEngine.Rendering.PostProcessing.ColorGrading.html) |

Present in all three: Ambient Occlusion, Bloom, Channel Mixer, Chromatic
Aberration, Color Adjustments, Color Curves, Depth of Field, Film Grain (named
Grain in PPv2), Lens Distortion, Lift Gamma Gain, Motion Blur, Tonemapping,
Vignette, White Balance, and post-process anti-aliasing.

## Where the same effect has a different shape

| Divergence | What it means for a port | Source |
|---|---|---|
| PPv2 folds Channel Mixer, Color Adjustments, Color Curves, Lift Gamma Gain, White Balance, and tonemapping into one `ColorGrading` class | A URP profile using five separate overrides maps to a single PPv2 effect with five property groups — there is no standalone PPv2 tonemapper type to look for | [ColorGrading API](https://docs.unity3d.com/Packages/com.unity.postprocessing@3.5/api/UnityEngine.Rendering.PostProcessing.ColorGrading.html) |
| Anti-aliasing is a Camera setting in URP and a `PostProcessLayer` setting in PPv2 | Neither one is found by searching an effect or override list | [Camera component reference](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/camera-component-reference.html) |
| Ambient Occlusion is a Renderer Feature in URP and an effect in PPv2 and HDRP | In URP it is added to the Renderer asset, not to a profile, and belongs to `unity-urp-rendering` | [SSAO in URP](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/post-processing-ssao.html) |
| HDRP names several overrides differently — Exposure for Auto Exposure, Fog for Deferred Fog | A name search across pipelines under-reports parity; HDRP work routes to `unity-hdrp-rendering` regardless | [Render pipeline feature comparison](https://docs.unity3d.com/6000.5/Documentation/Manual/render-pipelines-feature-comparison.html) |

## Provenance note

The per-effect HDRP and PPv2 links on the source availability page use Unity's
`@latest`/`@X.Y` package-doc URL pattern and were read off that table rather
than each re-fetched individually. Two rows on it carry older pinned package
versions than the rest, so treat a specific HDRP or PPv2 property list reached
from there as needing a version check against the installed package.

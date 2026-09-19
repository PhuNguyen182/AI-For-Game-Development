# Rendering Paths — Forward, Forward+, Deferred, Deferred+

Sources: [Choose a rendering path in URP](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/rendering-paths-comparison.html), [Forward and Forward+ rendering paths](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/rendering/forward-rendering-paths.html), [Deferred and Deferred+ rendering paths](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/rendering/deferred-rendering-path-landing.html).
Covers: SKILL.md §4 — **"Choose the rendering path against measured light counts per tier"**.

What each path costs and what it gives up. The path is set per Renderer asset,
so it is a per-tier decision, and each option removes a different constraint.

| Path | What it decides | Source |
|---|---|---|
| Forward | Lights are evaluated per object with a hard per-object limit — extra lights stop affecting *that object*, which is why a scene can look lit while individual props go dark | [Forward and Forward+](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/rendering/forward-rendering-paths.html) |
| Forward+ | Removes the per-object limit using a screen-space light structure, at a higher base cost; keeps MSAA and transparent lighting | [Forward and Forward+](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/rendering/forward-rendering-paths.html) |
| Deferred | Renders a G-buffer and lights everything once, scaling with light count rather than object count — costs bandwidth and gives up MSAA | [Deferred paths](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/rendering/deferred-rendering-path-landing.html) |
| Deferred+ | Deferred with the clustered light structure, combining G-buffer shading with better light scaling | [Deferred paths](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/rendering/deferred-rendering-path-landing.html) |
| Transparents | Still shaded forward under any deferred path, so transparent-heavy scenes do not get deferred's light scaling | [Choose a rendering path](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/rendering-paths-comparison.html) |
| Where it is set | On the Renderer asset — so different quality tiers can and often should differ | [Choose a rendering path](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/rendering-paths-comparison.html) |

**Critical caveat**: "lights stopped working past a certain count" is the
signature of Forward's *per-object* limit, and Forward+ addresses it directly.
Reaching for Deferred instead trades away MSAA — which mobile tiers commonly
rely on — to solve a problem the cheaper option already solves.

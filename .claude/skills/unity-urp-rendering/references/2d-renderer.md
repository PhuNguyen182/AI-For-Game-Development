# The 2D Renderer & `Light2D`

Sources: [Introduction to 2D lighting in URP](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/Lights-2D-intro.html), [Renderer 2D asset reference](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/2DRendererData-overview.html).
Covers: SKILL.md §4 — **"Confirm the active Renderer is the 2D Renderer before relying on `Light2D`"**.

2D lighting is a property of the Renderer asset, not of the project or the
sprites. Everything below exists only under `Renderer2DData`.

| Subject | What it decides | Source |
|---|---|---|
| `Renderer2DData` | The Renderer asset that enables 2D lighting at all — under the Universal Renderer none of this exists | [Renderer 2D asset](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/2DRendererData-overview.html) |
| `Light2D` | The 2D light component — Freeform, Sprite, Spot, Point, and Global types, each suiting a different shape of illumination | [Light 2D component reference](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/2DLightProperties.html) |
| Global light | Lights every sprite on its target sorting layers — the baseline a 2D scene starts from, without which lit sprites read as black | [Introduction to 2D lighting](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/Lights-2D-intro.html) |
| Target sorting layers | Each light affects only the sorting layers it targets, which is how foreground and background are lit separately | [Create a 2D light](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/2d-light-properties-explained.html) |
| Lit sprite materials | Sprites must use a lit 2D material to receive `Light2D` at all; an unlit sprite ignores every light | [Introduction to 2D lighting](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/Lights-2D-intro.html) |
| Tilemap integration | Tilemap renderers need their own lit setup to participate in 2D lighting | [Enable 2D lighting with the Tilemap Renderer](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/2d/tilemap-renderer-2d-renderer.html) |

**Critical caveat**: the two ways this fails look identical — the Renderer is
not the 2D Renderer, or the sprites use unlit materials. In both cases the
`Light2D` components sit in the scene doing nothing, with no warning that they
are inert.

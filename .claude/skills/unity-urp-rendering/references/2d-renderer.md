# The 2D Renderer and `Light2D`

Sources (manual paths under the `Docs:` base): [i] `Lights-2D-intro.html`, [r] `2DRendererData-overview.html`, [t] `2d/tilemap-renderer-2d-renderer.html`.

2D lighting is a property of the Renderer asset, not the project or the sprites; all of it exists only under `Renderer2DData` [r].

| Subject | Fact that decides |
|---|---|
| `Light2D` types | Freeform, Sprite, Spot, Point, Global; each suits a different illumination shape |
| Global light | Baseline for every sprite on its target sorting layers; without it lit sprites read as black [i] |
| Target sorting layers | Each light affects only the sorting layers it targets; how foreground and background are lit separately |
| Lit sprite materials | Sprites need a lit 2D material to receive `Light2D`; an unlit sprite ignores every light [i] |
| Tilemap | Tilemap renderers need their own lit setup [t] |

**Caveat:** a non-2D Renderer and unlit sprite materials look identical: `Light2D` components sit in the scene doing nothing, with no warning.

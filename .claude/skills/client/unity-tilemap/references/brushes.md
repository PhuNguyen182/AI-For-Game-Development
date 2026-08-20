# Brushes & Brush Picks

Sources: https://docs.unity3d.com/Manual/tilemaps/tile-palettes/brushes/brush-picks/brush-picks-landing.html, https://docs.unity3d.com/Manual/tilemaps/tile-palettes/brushes/brush-picks/brush-picks.html, https://docs.unity3d.com/Manual/tilemaps/tile-palettes/brushes/brush-picks/brush-picks-overlay-reference.html

## Built-in brush types

Set via the Tile Palette window's Brush Inspector dropdown (see [tile-palette-and-tiles.md](tile-palette-and-tiles.md)):

| Brush | Behavior |
|---|---|
| Default | Standard single-tile paint/erase/fill — what most painting uses. |
| Line | Paints a straight line of tiles between two points. |
| Random | Paints a random tile from a weighted set each stroke. |
| GameObject | Paints by instantiating GameObjects/prefabs onto the grid instead of `Tile` assets. |
| Group | Paints a fixed multi-tile arrangement as one unit. |

For a brush type none of these cover, author a custom Scriptable Brush — see [custom-tiles-and-brushes.md](custom-tiles-and-brushes.md).

## Brush Picks

A **Brush Pick** saves a tile (or group of tiles) together with its current brush settings, so the exact same paint configuration can be reused later without re-selecting everything from the palette each time. Brush Picks are managed and re-applied through the **Brush Picks overlay** in the Scene view.

| Control | Description |
|---|---|
| Brush Picks overlay | Scene-view panel listing saved Brush Picks; select one to load it back into the active brush/selection. |
| Save current selection as Brush Pick | Captures the current palette selection + brush settings as a new, reusable Brush Pick. |

Note: a tile using the **Default Brush** can't have its Brush Pick icon customized — that customization is only available for tiles using other brush types.

## Practical guidance

- Reach for **Random**/**Line**/**Group** brushes only when the design genuinely needs that painting behavior repeatedly (e.g. randomized grass tufts) — for a one-off arrangement, plain **Default** brush painting is simpler (KISS in `coding-principles.md`).
- Save a **Brush Pick** for any tile configuration (a specific decorated wall corner, a GameObject-brush prop) that gets reused across many painting sessions, instead of re-deriving the same selection by hand each time.

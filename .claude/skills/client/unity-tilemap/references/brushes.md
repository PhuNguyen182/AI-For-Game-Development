# Brushes & Brush Picks — Painting Behaviour

Sources: [Brush Picks](https://docs.unity3d.com/Manual/tilemaps/tile-palettes/brushes/brush-picks/brush-picks-landing.html), [Use Brush Picks](https://docs.unity3d.com/Manual/tilemaps/tile-palettes/brushes/brush-picks/brush-picks.html), [Brush Picks overlay reference](https://docs.unity3d.com/Manual/tilemaps/tile-palettes/brushes/brush-picks/brush-picks-overlay-reference.html).
Covers: SKILL.md §4 — **"Check the 2D Tilemap Extras package before writing anything custom"**.

The brush decides *how* a paint stroke turns into tiles. Only the Default
brush ships with core Unity; the four alternatives below come from the 2D
Tilemap Extras package, and referencing one in a project without that package
is a setup failure rather than a behaviour difference.

## Brush types

| Brush | What it decides | Ships with | Source |
|---|---|---|---|
| Default | One tile per cell, plus erase and fill — what most authoring uses | Core Unity | [Tile Palette editor reference](https://docs.unity3d.com/Manual/tilemaps/tile-palettes/tile-palette-editor-reference.html) |
| Line | Paints a straight run between two clicks, with optional gap filling so diagonals stay orthogonally connected | 2D Tilemap Extras — see [tilemap-extras-brushes.md](tilemap-extras-brushes.md) | [Line Brush](https://docs.unity3d.com/Packages/com.unity.2d.tilemap.extras@8.0/manual/LineBrush.html) |
| Random | Picks from a pool per stroke with **equal chance and no weighting**, so a genuinely rare variant needs a different mechanism | 2D Tilemap Extras | [Random Brush](https://docs.unity3d.com/Packages/com.unity.2d.tilemap.extras@8.0/manual/RandomBrush.html) |
| GameObject | Instantiates prefabs onto cells instead of writing `Tile` data — so the result is scene objects, not tilemap content | 2D Tilemap Extras | [GameObject Brush](https://docs.unity3d.com/Packages/com.unity.2d.tilemap.extras@8.0/manual/GameObjectBrush.html) |
| Group | Picks a whole contiguous group as one unit, by adjacency | 2D Tilemap Extras | [Group Brush](https://docs.unity3d.com/Packages/com.unity.2d.tilemap.extras@8.0/manual/GroupBrush.html) |
| Custom `GridBrushBase` | Anything the five above cannot express — see [custom-tiles-and-brushes.md](custom-tiles-and-brushes.md) | Authored in-project | [Create a scriptable brush](https://docs.unity3d.com/Manual/tilemaps/tile-palettes/brushes/create-scriptable-brush.html) |

## Brush Picks

| Control | What it decides | Source |
|---|---|---|
| Brush Picks overlay | Scene-view panel listing saved picks; selecting one restores that exact tile selection *and* brush settings, which is what makes a complex arrangement reusable across sessions | [Brush Picks overlay reference](https://docs.unity3d.com/Manual/tilemaps/tile-palettes/brushes/brush-picks/brush-picks-overlay-reference.html) |
| Save current selection as Brush Pick | Captures the selection plus settings — the alternative to re-deriving the same multi-tile arrangement by hand each time | [Use Brush Picks](https://docs.unity3d.com/Manual/tilemaps/tile-palettes/brushes/brush-picks/brush-picks.html) |
| Icon customisation | Unavailable for tiles using the Default brush; only other brush types can carry a custom Brush Pick icon | [Brush Picks overlay reference](https://docs.unity3d.com/Manual/tilemaps/tile-palettes/brushes/brush-picks/brush-picks-overlay-reference.html) |

A one-off arrangement does not justify a specialised brush — the Default brush
plus a saved Brush Pick usually expresses it, per KISS in
`coding-principles.md`.

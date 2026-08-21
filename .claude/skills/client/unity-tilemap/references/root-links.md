# Root Links — Unity Tilemap & 2D Tilemap Extras 8.0

Source: the Unity Manual section roots and the 2D Tilemap Extras package index listed below, as provided for this skill.
Covers: the whole skill — provenance and version anchor for every file in this folder.

Two provenance rules apply here, because this skill spans two products. Core
Tilemap lives in Unity's Manual, published without a version segment, so its
pages always resolve to the current release and any default quoted from them
is current-at-authoring-time only. The Extras package is pinned to
`com.unity.2d.tilemap.extras@8.0`; keep that segment when following its links.
Anything outside these roots belongs to a sibling skill — sprite art to
`unity-2d-sprite`, physics to `unity-2d-physics`, splines to
`unity-2d-spriteshape`, lighting to `unity-urp-rendering`.

| Root | Holds | Source |
|---|---|---|
| Tilemaps section | Every core authoring topic this skill covers | [Tilemaps](https://docs.unity3d.com/Manual/tilemaps/tilemaps.html) |
| Tiles for tilemaps | Palette creation and `Tile` asset authoring | [Tiles for Tilemaps](https://docs.unity3d.com/Manual/tilemaps/tiles-for-tilemaps/create-tile-palette-landing.html) |
| Work with tilemaps | Painting, renderer, collider, non-rectangular layouts | [Work with Tilemaps](https://docs.unity3d.com/Manual/tilemaps/work-with-tilemaps/create-tilemap-landing.html) |
| Custom tiles and brushes | The scripting extension surface | [Custom tiles and brushes](https://docs.unity3d.com/Manual/tilemaps/custom-tiles-brushes.html) |
| 2D Tilemap Extras 8.0 | Rule Tile, Auto Tile, Animated Tile, extra brushes, `GridInformation` | [2D Tilemap Extras](https://docs.unity3d.com/Packages/com.unity.2d.tilemap.extras@8.0/manual/index.html) |

## Topic → file map

| Topic | File | Source |
|---|---|---|
| `Grid` and `Tilemap` components, layer hierarchy | [grid-and-tilemap.md](grid-and-tilemap.md) | [Grid component reference](https://docs.unity3d.com/Manual/tilemaps/grid-reference.html) |
| Palette creation and `Tile` assets | [tile-palette-and-tiles.md](tile-palette-and-tiles.md) | [Create tile assets](https://docs.unity3d.com/Manual/tilemaps/tiles-for-tilemaps/create-tile-assets.html) |
| Brush types and Brush Picks | [brushes.md](brushes.md) | [Brush Picks](https://docs.unity3d.com/Manual/tilemaps/tile-palettes/brushes/brush-picks/brush-picks-landing.html) |
| Renderer mode, sorting, culling | [tilemap-renderer.md](tilemap-renderer.md) | [Tilemap Renderer reference](https://docs.unity3d.com/Manual/tilemaps/work-with-tilemaps/tilemap-renderer-reference.html) |
| Collision generation | [tilemap-collider-2d.md](tilemap-collider-2d.md) | [Tilemap Collider 2D](https://docs.unity3d.com/Manual/tilemaps/work-with-tilemaps/tilemap-collider-2d.html) |
| Isometric and hexagonal layouts | [isometric-hexagonal.md](isometric-hexagonal.md) | [Isometric Tilemaps](https://docs.unity3d.com/Manual/tilemaps/work-with-tilemaps/isometric-tilemaps/isometric-tilemap-landing.html) |
| Runtime tile reads and writes | [scripting-api.md](scripting-api.md) | [Tilemap API](https://docs.unity3d.com/ScriptReference/Tilemaps.Tilemap.html) |
| Custom `TileBase` and `GridBrushBase` | [custom-tiles-and-brushes.md](custom-tiles-and-brushes.md) | [Scriptable Tiles](https://docs.unity3d.com/Manual/tilemaps/tiles-for-tilemaps/scriptable-tiles/scriptable-tiles.html) |
| Rule Tile, Auto Tile, Animated Tile | [tilemap-extras-tiles.md](tilemap-extras-tiles.md) | [Extras Tiles](https://docs.unity3d.com/Packages/com.unity.2d.tilemap.extras@8.0/manual/Tiles.html) |
| Extra brushes and `GridInformation` | [tilemap-extras-brushes.md](tilemap-extras-brushes.md) | [Extras Brushes](https://docs.unity3d.com/Packages/com.unity.2d.tilemap.extras@8.0/manual/Brushes.html) |

## Disclosed gaps — pages that returned 404 at authoring time

| Type | What this skill does instead | Source |
|---|---|---|
| `UnityEditor.Tilemaps.GridBrushBase` / `GridBrush` API pages | Custom-brush guidance is taken from the Manual's workflow page, so method signatures are unconfirmed — verify against the live API or package source before implementing | [Create a scriptable brush](https://docs.unity3d.com/Manual/tilemaps/tile-palettes/brushes/create-scriptable-brush.html) |
| `UnityEngine.Tilemaps.RuleTile<T>` API page | Rule Tile guidance is taken from the Manual's Inspector reference; confirm members before subclassing | [Rule Tile](https://docs.unity3d.com/Packages/com.unity.2d.tilemap.extras@8.0/manual/RuleTile.html) |

The Extras package's `LineBrush`, `RandomBrush`, `GroupBrush`,
`GameObjectBrush`, `AnimatedTile`, and `GridInformation` API pages do resolve
and are cited directly in their own files.

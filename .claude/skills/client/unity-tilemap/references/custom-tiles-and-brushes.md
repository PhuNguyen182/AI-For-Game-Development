# Custom Tiles & Brushes — `TileBase` and `GridBrushBase`

Sources: [Custom tiles and brushes](https://docs.unity3d.com/Manual/tilemaps/custom-tiles-brushes.html), [Scriptable Tiles](https://docs.unity3d.com/Manual/tilemaps/tiles-for-tilemaps/scriptable-tiles/scriptable-tiles.html), [Create a scriptable brush](https://docs.unity3d.com/Manual/tilemaps/tile-palettes/brushes/create-scriptable-brush.html), [Tile Template asset](https://docs.unity3d.com/Manual/tilemaps/tile-palettes/tile-template-asset.html).
Covers: SKILL.md §4 — **"Write a custom `TileBase` or `GridBrushBase` only once nothing built-in or Extras fits"**.

Two extension points: a **Scriptable Tile** decides what a cell renders, and a
**Scriptable Brush** decides how painting writes cells. Before either, check
that Rule Tile, Auto Tile, or Animated Tile does not already cover it — see
[tilemap-extras-tiles.md](tilemap-extras-tiles.md) — because most auto-tiling
and animation requirements are already solved there.

## Scriptable Tile — extend `TileBase`

| Member | What it decides | Source |
|---|---|---|
| `GetTileData(Vector3Int, ITilemap, ref TileData)` | Required. Populates `sprite`, `color`, `transform`, `gameObject`, and `flags` — the whole visual result of the cell | [Scriptable Tiles](https://docs.unity3d.com/Manual/tilemaps/tiles-for-tilemaps/scriptable-tiles/scriptable-tiles.html) |
| `GetTileAnimationData(Vector3Int, ITilemap, ref TileAnimationData)` | Supplies animation frames, for a tile that animates itself rather than relying on Animated Tile | [Scriptable Tiles](https://docs.unity3d.com/Manual/tilemaps/tiles-for-tilemaps/scriptable-tiles/scriptable-tiles.html) |
| `RefreshTile(Vector3Int, ITilemap)` | Controls which **neighbouring** cells re-run their own `GetTileData` — this is the mechanism behind every auto-tiling tile, and omitting it is why a neighbour-aware tile fails to update its surroundings | [Scriptable Tiles](https://docs.unity3d.com/Manual/tilemaps/tiles-for-tilemaps/scriptable-tiles/scriptable-tiles.html) |
| `StartUp(Vector3Int, ITilemap, GameObject)` | Runs on the first frame the scene plays — runtime initialisation, not edit-time | [Scriptable Tiles](https://docs.unity3d.com/Manual/tilemaps/tiles-for-tilemaps/scriptable-tiles/scriptable-tiles.html) |
| `OnEnable` / `OnDisable` | Asset load and unload | [Scriptable Tiles](https://docs.unity3d.com/Manual/tilemaps/tiles-for-tilemaps/scriptable-tiles/scriptable-tiles.html) |
| `TileData` fields | `sprite`, `color`, `transform`, `gameObject`, `flags`, plus `spriteEntityId`/`gameObjectEntityId` for DOTS entity references | [Scriptable Tiles](https://docs.unity3d.com/Manual/tilemaps/tiles-for-tilemaps/scriptable-tiles/scriptable-tiles.html) |

```csharp
using UnityEngine;
using UnityEngine.Tilemaps;

[CreateAssetMenu]
public class AutoTintTile : TileBase
{
    [SerializeField] private Sprite sprite;
    [SerializeField] private Color tint = Color.white;

    public override void GetTileData(Vector3Int position, ITilemap tilemap, ref TileData tileData)
    {
        tileData.sprite = this.sprite;
        tileData.color = this.tint;
    }
}
```

`[CreateAssetMenu]` is what makes the tile creatable from the Assets menu and
draggable into a palette like any other tile.

## Scriptable Brush — extend `GridBrushBase`

| Member | What it decides | Source |
|---|---|---|
| `Paint` / `Erase` | Adding and removing content at the painted cells — the two overrides a minimal brush needs | [Create a scriptable brush](https://docs.unity3d.com/Manual/tilemaps/tile-palettes/brushes/create-scriptable-brush.html) |
| `FloodFill` | Contiguous fill behaviour, if it should differ from painting cell by cell | [Create a scriptable brush](https://docs.unity3d.com/Manual/tilemaps/tile-palettes/brushes/create-scriptable-brush.html) |
| `Rotate` / `Flip` | How the brush's own content transforms before being written | [Create a scriptable brush](https://docs.unity3d.com/Manual/tilemaps/tile-palettes/brushes/create-scriptable-brush.html) |
| `ChangeZPosition` / `ResetZPosition` | Height handling when painting into an Isometric Z as Y tilemap — see [isometric-hexagonal.md](isometric-hexagonal.md) | [Create a scriptable brush](https://docs.unity3d.com/Manual/tilemaps/tile-palettes/brushes/create-scriptable-brush.html) |
| `OnPaintInspectorGUI` / `OnPaintSceneGUI` | Custom Inspector and Scene-view controls for the brush | [Create a scriptable brush](https://docs.unity3d.com/Manual/tilemaps/tile-palettes/brushes/create-scriptable-brush.html) |
| `CustomGridBrush` attribute | Adjusts how the brush is presented in the Brush Inspector dropdown | [Create a scriptable brush](https://docs.unity3d.com/Manual/tilemaps/tile-palettes/brushes/create-scriptable-brush.html) |

`GridBrushBase` lives in `UnityEditor.Tilemaps`, so a brush is editor-only
code and must not be referenced from runtime assemblies.

**Critical caveat**: the `GridBrushBase` and `GridBrush` API pages returned 404
at authoring time — see the disclosed-gap table in
[root-links.md](root-links.md). Confirm signatures against the live API before
implementing.

## Tile Template

| Concept | What it decides | Source |
|---|---|---|
| Extend `TileTemplate` | Customises how Unity generates `Tile` assets *from* a texture during the Tile Set Importer flow, rather than what a tile does once created | [Tile Template asset](https://docs.unity3d.com/Manual/tilemaps/tile-palettes/tile-template-asset.html) |

Name custom tiles and brushes per `naming-convention.md` — they become project
assets other people select from a dropdown, so the name is the whole interface.

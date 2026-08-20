# Custom Tiles & Brushes (Scripting)

Sources: https://docs.unity3d.com/Manual/tilemaps/custom-tiles-brushes.html, https://docs.unity3d.com/Manual/tilemaps/tiles-for-tilemaps/scriptable-tiles/scriptable-tiles.html, https://docs.unity3d.com/Manual/tilemaps/tile-palettes/brushes/create-scriptable-brush.html, https://docs.unity3d.com/Manual/tilemaps/tile-palettes/tile-template-asset.html, `UnityEngine.Tilemaps.TileBase`/`TileData` scripting API

Note: the `UnityEditor.Tilemaps.GridBrushBase`/`GridBrush` Scripting API pages returned 404 at authoring time — this file's brush guidance is sourced from the Manual's workflow page instead; verify current method signatures against the live Scripting API or the `com.unity.2d.tilemap.extras` package docs before implementing.

## Custom Scriptable Tile

Extend `UnityEngine.Tilemaps.TileBase` for a tile that dynamically changes its own look or the look of neighboring tiles (animated tiles, auto-tiling/terrain-blending tiles, randomized-variant tiles).

| Method | Purpose |
|---|---|
| `GetTileData(Vector3Int position, ITilemap tilemap, ref TileData tileData)` | Required. Determines the tile's render data — populate `tileData.sprite`, `.color`, `.transform`, `.gameObject`, `.flags` as needed. |
| `GetTileAnimationData(Vector3Int position, ITilemap tilemap, ref TileAnimationData tileAnimationData)` | Supplies animation frame data for an animated tile. |
| `RefreshTile(Vector3Int position, ITilemap tilemap)` | Called on refresh; also controls which neighboring tiles re-run their own `GetTileData` (the mechanism behind auto-tiling/terrain-blend tiles). |
| `StartUp(Vector3Int position, ITilemap tilemap, GameObject go)` | Called on the first frame the Scene runs — runtime initialization. |
| `OnEnable()` / `OnDisable()` | Called when the tile asset is loaded / goes out of scope. |

`TileData` struct fields: `sprite`, `color`, `transform`, `gameObject`, `flags`, plus `spriteEntityId`/`gameObjectEntityId` (DOTS entity references, when applicable).

```csharp
[CreateAssetMenu]
public class AutoTintTile : TileBase
{
    public override void GetTileData(Vector3Int position, ITilemap tilemap, ref TileData tileData)
    {
        tileData.color = Color.white;
    }
}
```

Add `[CreateAssetMenu]`, create an instance via the Assets menu, then drag it into a Tile Palette like any other tile.

## Custom Scriptable Brush

Extend `UnityEditor.Tilemaps.GridBrushBase` (editor-only) for painting behavior the built-in brushes (Default/Line/Random/GameObject/Group — see [brushes.md](brushes.md)) don't cover.

| Method | Purpose |
|---|---|
| `Paint` | Add items to the grid at the given position(s). |
| `Erase` | Remove items from the grid. |
| `FloodFill` | Fill a contiguous area. |
| `Rotate` / `Flip` | Rotate/mirror the current brush content. |
| `ChangeZPosition` / `ResetZPosition` | Manage 3D height when painting into an Isometric Z as Y tilemap. |

```csharp
using UnityEngine;
using UnityEngine.Tilemaps;
using UnityEditor.Tilemaps;

[CreateAssetMenu]
public class MyCustomBrush : GridBrushBase
{
    // Override Paint/Erase/FloodFill/etc. as needed.
}
```

`[CreateAssetMenu]` makes the brush creatable as a project asset, which then appears in the Tile Palette's Brush Inspector dropdown. Override `OnPaintInspectorGUI`/`OnPaintSceneGUI` for custom Inspector/Scene-view controls, or apply a `CustomGridBrush` attribute to adjust default display behavior.

## Tile Template asset

For customizing how Unity generates `Tile` assets *from* a texture (the auto-creation step in [tile-palette-and-tiles.md](tile-palette-and-tiles.md)'s Tile Set Importer path), extend `TileTemplate` instead of hooking `TileBase` directly.

## Practical guidance

- Reach for a custom `TileBase`/`GridBrushBase` only when a built-in tile/brush genuinely can't express the requirement (auto-tiling, procedural variation, non-standard painting) — a plain `Tile` asset with the Default Brush covers the overwhelming majority of tilemap content (YAGNI in `coding-principles.md`).
- A custom tile's `GetTileData`/`RefreshTile` runs in the editor and at runtime — keep it free of gameplay-rule decisions (which tile *should* be there per game state); resolve that in Shared Core and have the tile only render whatever the Shared Core-resolved layout already decided, per `coding-principles.md`'s Shared Core integrity rule.
- Follow this project's naming convention for any custom tile/brush class (`AutoTintTile`, `RandomVariantBrush`) per `naming-convention.md` — PascalCase class names, no Hungarian prefixes.

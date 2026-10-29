# Custom Tiles & Brushes

Pages: https://docs.unity3d.com/Manual/tilemaps/custom-tiles-brushes.html, https://docs.unity3d.com/Manual/tilemaps/tiles-for-tilemaps/scriptable-tiles/scriptable-tiles.html, https://docs.unity3d.com/Manual/tilemaps/tile-palettes/brushes/create-scriptable-brush.html

Check Rule Tile, Auto Tile and Animated Tile first (tilemap-extras-tiles.md). Gaps: the `GridBrushBase`/`GridBrush` API pages returned 404 when this was written, so brush signatures below come from the workflow page; verify against live API or package source before implementing.

## Scriptable Tile — extend `TileBase`

| Member | Decision |
|---|---|
| `GetTileData(Vector3Int, ITilemap, ref TileData)` | Required. Fills `sprite`, `color`, `transform`, `gameObject`, `flags` (plus `spriteEntityId`/`gameObjectEntityId` for DOTS) |
| `GetTileAnimationData(Vector3Int, ITilemap, ref TileAnimationData)` | Animation frames for a self-animating tile |
| `RefreshTile(Vector3Int, ITilemap)` | Which **neighbours** re-run `GetTileData`; the mechanism of auto-tiling, and omitting it leaves neighbours stale |
| `StartUp(Vector3Int, ITilemap, GameObject)` | First frame of Play; runtime init, not edit time |
| `OnEnable` / `OnDisable` | Asset load/unload |

```csharp
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

`[CreateAssetMenu]` makes it creatable from the Assets menu and draggable into a palette.

## Scriptable Brush — extend `GridBrushBase`

Lives in `UnityEditor.Tilemaps`: editor-only, never reference from runtime assemblies.

| Member | Decision |
|---|---|
| `Paint` / `Erase` | Minimal brush needs these two |
| `FloodFill` | Contiguous fill if different from cell-by-cell |
| `Rotate` / `Flip` | How brush content transforms before writing |
| `ChangeZPosition` / `ResetZPosition` | Height when painting Isometric Z as Y |
| `OnPaintInspectorGUI` / `OnPaintSceneGUI` | Custom Inspector / Scene controls |
| `CustomGridBrush` attribute | Presentation in the Brush Inspector dropdown |

## Tile Template

Extend `TileTemplate` to customise how the Tile Set Importer generates `Tile` assets from a texture (not what a tile does once created). Page: https://docs.unity3d.com/Manual/tilemaps/tile-palettes/tile-template-asset.html

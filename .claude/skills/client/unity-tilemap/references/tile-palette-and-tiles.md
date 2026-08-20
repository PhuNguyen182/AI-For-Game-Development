# Tile Palette & Tile Assets

Sources: https://docs.unity3d.com/Manual/tilemaps/tiles-for-tilemaps/create-tile-palette-landing.html, https://docs.unity3d.com/Manual/tilemaps/tiles-for-tilemaps/create-tile-assets.html, https://docs.unity3d.com/Manual/tilemaps/tiles-for-tilemaps/tile-asset-reference.html, https://docs.unity3d.com/Manual/tilemaps/tile-palettes/tile-palette-editor-reference.html, https://docs.unity3d.com/Manual/tilemaps/tile-palettes/tools/tile-palette-tools-landing.html, https://docs.unity3d.com/Manual/tilemaps/tile-palettes/tile-set-properties.html

## Creating a Tile Palette

A Tile Palette holds the set of `Tile` assets available to paint. Two creation paths:

1. **Manual / drag-in (no auto-update)** — Open **Window > 2D > Tile Palette**, create a new palette via **Active Palette > Create New Palette**, then drag a sprite asset, a spritesheet texture, or a folder from the Project window onto the palette. If the texture's Sprite Mode is Multiple, Unity creates one `Tile` per child sprite and prompts for a save location. **The resulting `Tile` assets are not linked back to the source sprite/texture** — re-editing the source art does not update the tiles.
2. **Tile Set Importer (auto-updating)** — **Assets > Create > 2D > Tile Palette > New Tile Set**, select the created asset, open **Texture Sources**, add (+) a texture reference, **Apply**. Tiles generated this way regenerate automatically when the source texture changes — prefer this path whenever the source art is expected to iterate, per the Boy Scout/YAGNI-adjacent principle of not hand-maintaining data a tool can keep in sync.

Palette **Grid** type (Rectangle/Hexagon/Isometric) is set at creation and must match the target `Tilemap`'s Cell Layout — see [isometric-hexagonal.md](isometric-hexagonal.md).

## Tile Palette window reference

| Toolbar tool | Shortcut | Description |
|---|---|---|
| Select | S | Select a tile in the palette or Scene view. |
| Move | M | Relocate painted tiles in the Scene. |
| Paint | B | Paint tiles from the current selection. |
| Box Fill | U | Paint a rectangular region. |
| Pick | I | Pick a tile from the palette or Scene view into the active selection. |
| Eraser | D | Remove tiles. |
| Flood Fill | G | Fill a contiguous blank area or area of identical tiles. |
| Rotate Counter-Clockwise / Clockwise | `[` / `]` | Rotate the current selection 90°. |
| Flip X / Flip Y | Shift+`[` / Shift+`]` | Mirror the current selection. |

| Control | Description |
|---|---|
| Active Tile Palette | Which palette asset is displayed/edited. |
| Active Tilemap | Which scene `Tilemap` painting operations target. |
| Hide / Ping Tilemap | Scene-view visibility toggle / locate in Hierarchy. |
| Create New Tilemap | Creates a new `Grid`+`Tilemap` matching a chosen layout, without leaving the window. |
| Tile Palette Edit mode | Switches the main area to edit the source tiles themselves (select/move/scale/delete), instead of painting into the Scene — see [tools/tile-palette-tools-landing.html](https://docs.unity3d.com/Manual/tilemaps/tile-palettes/tools/tile-palette-tools-landing.html). |
| Brush Picks Overlay / Tile Palette Overlay | Scene-view overlays — see [brushes.md](brushes.md). |
| Brush Inspector | Brush type dropdown (**Default**/**Line**/**Random**/**GameObject**/**Group**), the brush's `Script` reference, **Flood Fill Contiguous Only**, **Lock Z Position**, Scene View/Palette Z Position. |

## Tile asset reference

| Property | Description |
|---|---|
| Sprite | The rendered sprite. |
| Color | Tints the sprite; white = no tint. |
| Collider Type | **None** (no collision), **Sprite** (uses the sprite's custom physics shape — see `unity-2d-sprite`'s [custom-physics-shape.md](../../unity-2d-sprite/references/custom-physics-shape.md)), or **Grid** (uses the tilemap cell's own shape). |
| Flags | **Lock Color**, **Lock Transform**, **Instantiate GameObject Runtime Only**, **Keep GameObject Runtime Only**, **Lock All**. |
| Offset / Rotation / Scale | Fixed per-tile transform overrides (only editable when Lock Transform/Lock All is set). |
| GameObject to Instantiate | A prefab spawned at the tile's position when painted — must be dragged from the Project window, not the Hierarchy. |

## Practical guidance

- Choose **Collider Type = Grid** for ordinary rectangular/hex/iso solid tiles (cheapest, matches `performance-and-algorithms.md`'s simplest-shape rule) and reserve **Sprite** for tiles whose silhouette genuinely differs from the cell shape (a rounded rock, a thin fence rail).
- The auto-updating Tile Set Importer path is the default choice for any tileset still under active art iteration; the manual drag-in path is fine for a one-off, final-art palette that won't change again.
- `GameObject to Instantiate` is for a per-tile visual/behavioral prefab (e.g. an animated torch) — it is not a substitute for gameplay-rule logic; any rule that prefab's behavior expresses still belongs in Shared Core per `coding-principles.md`.

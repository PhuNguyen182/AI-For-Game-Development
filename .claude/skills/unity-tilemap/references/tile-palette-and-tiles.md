# Tile Palette & Tile Assets — Creation Paths, Tools & Tile Fields

Sources: [Create a Tile Palette](https://docs.unity3d.com/Manual/tilemaps/tiles-for-tilemaps/create-tile-palette-landing.html), [Create tile assets](https://docs.unity3d.com/Manual/tilemaps/tiles-for-tilemaps/create-tile-assets.html), [Tile asset reference](https://docs.unity3d.com/Manual/tilemaps/tiles-for-tilemaps/tile-asset-reference.html), [Tile Palette editor reference](https://docs.unity3d.com/Manual/tilemaps/tile-palettes/tile-palette-editor-reference.html).
Covers: SKILL.md §4 — **"Create the palette through the Tile Set Importer whenever the art will change again"**, **"Set each `Tile`'s Collider Type to the cheapest shape that plays correctly"**.

A palette holds the `Tile` assets available to paint. The two creation paths
look equivalent in the Editor and differ in one decisive way: only one of them
keeps the generated tiles connected to the texture they came from.

## The two creation paths

| Path | What it decides | Source |
|---|---|---|
| Manual drag-in — **Active Palette > Create New Palette**, then drag a sprite, sheet, or folder in | Generates one `Tile` per sub-sprite and asks where to save them. **Those tiles are not linked back to the source**, so re-editing the art does not update them and nothing reports the drift | [Create a Tile Palette](https://docs.unity3d.com/Manual/tilemaps/tiles-for-tilemaps/create-tile-palette-landing.html) |
| Tile Set Importer — **Assets > Create > 2D > Tile Palette > New Tile Set**, add a texture under Texture Sources, Apply | Generated tiles regenerate whenever the source texture changes — the correct default for any art still iterating | [Create a Tile Palette](https://docs.unity3d.com/Manual/tilemaps/tiles-for-tilemaps/create-tile-palette-landing.html) |
| Palette Grid type | Set at creation and must match the target `Tilemap`'s Cell Layout; a mismatch paints to the wrong cells rather than erroring — see [isometric-hexagonal.md](isometric-hexagonal.md) | [Create a Tile Palette](https://docs.unity3d.com/Manual/tilemaps/tiles-for-tilemaps/create-tile-palette-landing.html) |

## Window tools

| Tool | Shortcut | What it decides | Source |
|---|---|---|---|
| Select / Pick | S / I | Selects in the palette or Scene; Pick captures an existing arrangement straight from the Scene view | [Tile Palette editor reference](https://docs.unity3d.com/Manual/tilemaps/tile-palettes/tile-palette-editor-reference.html) |
| Paint / Box Fill / Flood Fill | B / U / G | Single cells, a rectangle, or a contiguous region of matching cells | [Tile Palette editor reference](https://docs.unity3d.com/Manual/tilemaps/tile-palettes/tile-palette-editor-reference.html) |
| Move / Eraser | M / D | Relocates painted tiles, or removes them | [Tile Palette editor reference](https://docs.unity3d.com/Manual/tilemaps/tile-palettes/tile-palette-editor-reference.html) |
| Rotate / Flip | `[` `]` / Shift+`[` `]` | Transforms the current selection before painting — the cheap alternative to authoring rotated variants | [Tile Palette editor reference](https://docs.unity3d.com/Manual/tilemaps/tile-palettes/tile-palette-editor-reference.html) |

| Control | What it decides | Source |
|---|---|---|
| Active Tilemap | Which layer painting writes into — the usual cause of tiles appearing on the wrong layer | [Tile Palette editor reference](https://docs.unity3d.com/Manual/tilemaps/tile-palettes/tile-palette-editor-reference.html) |
| Tile Palette Edit mode | Switches the main area to editing the palette's own tiles rather than painting a scene | [Tile Palette tools](https://docs.unity3d.com/Manual/tilemaps/tile-palettes/tools/tile-palette-tools-landing.html) |
| Brush Inspector | Brush type, its script reference, Flood Fill Contiguous Only, Lock Z Position, and Z position controls — see [brushes.md](brushes.md) | [Tile Palette editor reference](https://docs.unity3d.com/Manual/tilemaps/tile-palettes/tile-palette-editor-reference.html) |

## Tile asset fields

| Property | What it decides | Source |
|---|---|---|
| Sprite | The rendered art; authored by `unity-2d-sprite`, consumed here | [Tile asset reference](https://docs.unity3d.com/Manual/tilemaps/tiles-for-tilemaps/tile-asset-reference.html) |
| Color | Per-tile tint, multiplied with the `Tilemap`'s own Color | [Tile asset reference](https://docs.unity3d.com/Manual/tilemaps/tiles-for-tilemaps/tile-asset-reference.html) |
| Collider Type | **None** for decoration, **Grid** for anything matching its cell — the cheapest working shape — or **Sprite**, which uses the physics shape authored on the sprite by `unity-2d-sprite` and is only as accurate as that authoring | [Tile asset reference](https://docs.unity3d.com/Manual/tilemaps/tiles-for-tilemaps/tile-asset-reference.html) |
| Flags | Lock Color, Lock Transform, Instantiate GameObject Runtime Only, Keep GameObject Runtime Only, Lock All — the Runtime Only pair keep editor scenes free of instances that only matter at play time | [Tile asset reference](https://docs.unity3d.com/Manual/tilemaps/tiles-for-tilemaps/tile-asset-reference.html) |
| Offset / Rotation / Scale | Fixed per-tile transform, editable only once Lock Transform or Lock All is set | [Tile asset reference](https://docs.unity3d.com/Manual/tilemaps/tiles-for-tilemaps/tile-asset-reference.html) |
| GameObject to Instantiate | A prefab spawned per painted cell; it must be a Project-window prefab, not a scene instance. Its behaviour is presentation, not a place for game rules | [Tile asset reference](https://docs.unity3d.com/Manual/tilemaps/tiles-for-tilemaps/tile-asset-reference.html) |

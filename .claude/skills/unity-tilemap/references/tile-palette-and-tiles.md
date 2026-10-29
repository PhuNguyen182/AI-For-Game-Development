# Tile Palette, Tile Assets & Brush Picks

Pages: https://docs.unity3d.com/Manual/tilemaps/tiles-for-tilemaps/create-tile-palette-landing.html, https://docs.unity3d.com/Manual/tilemaps/tile-palettes/tile-palette-editor-reference.html

## Creation paths

| Path | Decision |
|---|---|
| Drag-in: Active Palette > Create New Palette, drag a sprite/sheet/folder | One `Tile` per sub-sprite, saved where asked. **Not linked to the source**: art edits do not update them and nothing reports drift |
| Tile Set Importer: Assets > Create > 2D > Tile Palette > New Tile Set, add a texture under Texture Sources, Apply | Tiles regenerate when the source texture changes; default for art still iterating |
| Palette Grid type | Set at creation; must match the target Tilemap's Cell Layout (mismatch paints to wrong cells silently) |

## Window tools

Select/Pick (S/I; Pick captures an arrangement from the Scene), Paint/Box Fill/Flood Fill (B/U/G), Move/Eraser (M/D), Rotate/Flip (`[` `]` / Shift+`[` `]`; cheaper than authoring rotated variants). Tile Palette Edit mode edits the palette's own tiles. Brush Inspector holds brush type, script, Flood Fill Contiguous Only, Lock Z Position and Z controls.

## Tile asset fields

| Property | Decision |
|---|---|
| Sprite / Color | Art (`unity-2d-sprite`); tint multiplied with the Tilemap Color |
| Collider Type | **None** decoration; **Grid** for cell-shaped tiles (cheapest); **Sprite** uses the sprite's physics shape |
| Flags | Lock Color, Lock Transform, Instantiate GameObject Runtime Only, Keep GameObject Runtime Only, Lock All; the Runtime Only pair keep play-time-only instances out of editor scenes |
| Offset / Rotation / Scale | Per-tile transform, editable only with Lock Transform or Lock All |
| GameObject to Instantiate | Prefab per painted cell; must be a Project prefab, not a scene instance; presentation only, no game rules |

## Brushes and Brush Picks

Only the Default brush (one tile per cell, erase, fill) ships with core Unity; Line, Random, Group, GameObject come from Extras (tilemap-extras-brushes.md), custom brushes from custom-tiles-and-brushes.md.

- Brush Picks overlay (Scene view) lists saved picks; selecting one restores the exact tile selection and brush settings. Save via "Save current selection as Brush Pick". A one-off arrangement is Default brush plus a Brush Pick, not a new brush.
- Custom Brush Pick icons are unavailable for tiles using the Default brush.

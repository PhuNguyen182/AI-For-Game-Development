# Isometric & Hexagonal Tilemaps

Sources: https://docs.unity3d.com/Manual/tilemaps/work-with-tilemaps/isometric-tilemaps/isometric-tilemap-landing.html, https://docs.unity3d.com/Manual/tilemaps/work-with-tilemaps/isometric-tilemaps/create-isometric-tilemap.html, https://docs.unity3d.com/Manual/tilemaps/work-with-tilemaps/isometric-tilemaps/renderer/tilemap-renderer-isometric-modes.html, https://docs.unity3d.com/Manual/tilemaps/work-with-tilemaps/hexagonal-tilemaps/hexagonal-tilemap-landing.html

## Isometric

Isometric tilemaps use a 2D grid to simulate a 3D environment (height/depth illusion) — common in strategy games.

**Setup:**
1. Import isometric sprites with Mesh Type = Tight, Pixels Per Unit = the tile's pixel width, and a custom pivot set (in the Sprite Editor) to the center of the tile's 3D floor — see `unity-2d-sprite`'s [import-settings.md](../../unity-2d-sprite/references/import-settings.md) and [sprite-editor.md](../../unity-2d-sprite/references/sprite-editor.md).
2. **Assets > Create > 2D > Tile Palette**, set its type to **Isometric**. In the Inspector, set **Cell Size y** = (3D floor height in pixels) / (tile width in pixels) — e.g. a 32px-tall floor on a 64px-wide tile gives Cell Size y = 0.5.
3. Create the tilemap as either **Isometric Tilemap** (flat — one tilemap per height level, stack separate tilemaps for height) or **Isometric Z as Y Tilemap** (a single tilemap encodes height directly via Z-as-Y painting). Match the `Grid`'s **Cell Size y** to the palette's value.
4. On the active 2D Renderer asset (URP) set **Transparency Sort Mode = Custom Axis**, **Transparency Sort Axis = (0, 1, 0)** — for the Built-in Render Pipeline, set the equivalent under **Edit > Project Settings > Graphics > Camera Settings** instead. Without this, isometric depth sorting reads wrong.
5. Paint tiles as usual (see [grid-and-tilemap.md](grid-and-tilemap.md)).

**Adding 3D height:** either stack multiple flat `Isometric Tilemap`s (one per level) or use a single **Isometric Z as Y** tilemap and set height while painting.

## Hexagonal

Hexagonal tiles keep a consistent distance from center to any edge point, and neighboring tiles always share a full edge — well suited to tactical/strategy movement.

| Type | Layout |
|---|---|
| Point Top | Vertex at top/bottom; alternating rows offset rightward by half a cell. |
| Flat Top | Flat edge at top/bottom, x/y axes swapped from Point Top — Cell Size **x** affects vertical spacing, **y** affects horizontal spacing; alternating columns offset downward by half a cell. |

**Setup:**
1. Import sprite assets — hexagon spritesheet frames can stay as ordinary rectangular slices, or individual sprites can use Sprite Mode = Polygon for a tighter hex shape.
2. Create a Tile Palette (see [tile-palette-and-tiles.md](tile-palette-and-tiles.md)) with type **Hexagonal Point Top** or **Hexagonal Flat Top**, matching the source art.
3. Create the tilemap and set the `Grid`'s **Cell Layout = Hexagon** to match.

## Practical guidance

- The isometric Cell Size y formula (floor-height-px / tile-width-px) is the single most common source of a "tiles don't line up" bug — verify it against the actual imported sprite's pixel dimensions rather than eyeballing a round number.
- Choose **Isometric Z as Y** only when height genuinely varies within one continuous playable layer (ramps, multi-level terrain) — stacked flat **Isometric Tilemap** layers are simpler for a small, fixed number of discrete height levels (KISS in `coding-principles.md`).
- Flat Top's swapped x/y Cell Size semantics is a common source of confusion when copying settings from a Point Top project — double check which axis governs which spacing before trusting a pasted value.

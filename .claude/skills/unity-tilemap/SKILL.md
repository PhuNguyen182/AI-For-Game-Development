---
name: unity-tilemap
description: >
  Unity built-in Tilemap authoring (`UnityEngine.Tilemaps`) — the
  `Grid`/`Tilemap` hierarchy, Cell Layout Rectangle, Hexagon, Isometric and
  Isometric Z as Y, Tile Palette creation by drag-in or Tile Set Importer,
  `Tile` assets and Collider Type, painting brushes and Brush Picks,
  `TilemapRenderer` Chunk/Individual/SRP Batch mode, `TilemapCollider2D`
  with `CompositeCollider2D`, `SetTiles`/`BoxFill`/`FloodFill`, custom
  `TileBase` and `GridBrushBase`, plus 2D Tilemap Extras `RuleTile`,
  `AnimatedTile`, Auto Tile and `GridInformation`. Use for tile-based level
  building, auto-tiling, and tile collision. Not for: sprite import and
  atlasing (`unity-2d-sprite`), bodies and joints (`unity-2d-physics`),
  spline geometry (`unity-2d-spriteshape`), `Light2D`
  (`unity-urp-rendering`), level-generation rules (`csharp-engineer`).
---

# Unity Tilemap — Grid Authoring, Painting, Rendering, Collision & Custom Tiles

## Bundled resources

### References

| File | Contents | Read when |
|---|---|---|
| [root-links.md](references/root-links.md) | Manual roots, package pins, topic→file map, disclosed 404 gaps | Starting any tilemap task, or a type has no documented page |
| [grid-and-tilemap.md](references/grid-and-tilemap.md) | `Grid` and `Tilemap` properties, layer hierarchy, painting flow | Setting up the scene hierarchy, or painting lands misaligned |
| [tile-palette-and-tiles.md](references/tile-palette-and-tiles.md) | Both palette creation paths, window tools, `Tile` asset fields | Building a palette, or source art edits do not propagate |
| [brushes.md](references/brushes.md) | Built-in and Extras brush behaviours, Brush Picks | Choosing how to paint, or reusing a paint configuration |
| [tilemap-renderer.md](references/tilemap-renderer.md) | Mode, sorting, mask interaction, chunk culling | Tiles sort wrongly against sprites, or pop in at chunk edges |
| [tilemap-collider-2d.md](references/tilemap-collider-2d.md) | Collider generation, composite pairing, rebuild threshold | Adding collision to a painted level |
| [isometric-hexagonal.md](references/isometric-hexagonal.md) | Cell Size maths, Z as Y, Point Top vs Flat Top, sort axis | Building a non-rectangular grid, or tiles do not line up |
| [scripting-api.md](references/scripting-api.md) | `Tilemap` reads, batched writes, refresh methods | Changing tiles from code |
| [custom-tiles-and-brushes.md](references/custom-tiles-and-brushes.md) | `TileBase` and `GridBrushBase` override surfaces | No built-in or Extras tile or brush fits |
| [tilemap-extras-tiles.md](references/tilemap-extras-tiles.md) | Rule Tile, Auto Tile, Animated Tile, override variants | Auto-tiling, terrain blending, or animated tiles |
| [tilemap-extras-brushes.md](references/tilemap-extras-brushes.md) | Line, Random, Group, GameObject brushes, `GridInformation` | Repetitive painting patterns, or per-cell metadata |

## 1. Objective
Build a tile-based level that lines up, sorts correctly, collides efficiently, and keeps following its source art as that art changes — avoiding the failure modes this pipeline hides: a palette created by drag-in that silently stops tracking its texture, an isometric Cell Size derived by eye rather than from the sprite, a composite setting that does nothing because no composite component exists, a chunk culling bound that clips oversized tiles, and a custom tile written for something Rule Tile already does.

## 2. Role
Act as the built-in Tilemap authoring specialist for the client track — the skill reached for whenever `Grid`, `Tilemap`, `TilemapRenderer`, `TilemapCollider2D`, a Tile Palette, or a custom tile or brush must be created, configured, or driven from code.

## 3. When to invoke this skill
- Setting up a `Grid` and its `Tilemap` layers, including Cell Size, Gap, Layout, Swizzle, Tile Anchor, and Orientation.
- Creating a Tile Palette by either path, or authoring `Tile` asset properties.
- Painting, filling, erasing, rotating, or flipping tiles, choosing a brush, or saving a Brush Pick.
- Configuring `TilemapRenderer` mode, sorting, mask interaction, or chunk culling bounds.
- Generating collision with `TilemapCollider2D`, with or without a `CompositeCollider2D`.
- Setting up an isometric or hexagonal grid, including Z as Y height.
- Editing tiles at runtime through the `Tilemap` API.
- Reaching for auto-tiling, terrain blending, tile animation, or per-cell metadata.
- Writing a custom `TileBase` or `GridBrushBase` when nothing built-in fits.
- Negative trigger: importing, slicing, or atlasing the sprite art tiles are made from — that's `unity-2d-sprite`; this skill consumes finished `Sprite` assets.
- Negative trigger: the `Rigidbody2D`, physics material, effector, or joint on the generated collider — that's `unity-2d-physics`; this skill stops at generating collision shapes.
- Negative trigger: spline-based level geometry rather than cells — that's `unity-2d-spriteshape`.
- Negative trigger: `Light2D` or 2D Renderer Data setup — that's `unity-urp-rendering`.
- Negative trigger: deciding *which* tile belongs where — procedural generation, destructible terrain rules — that's `csharp-engineer`'s Shared Core, per `coding-principles.md`'s Shared Core integrity section.

## 4. How to use this skill
1. **Settle the Cell Layout before creating anything**, per [grid-and-tilemap.md](references/grid-and-tilemap.md) — Rectangle, Hexagon, Isometric, or Isometric Z as Y must match between the `Grid` and every palette painted into it, and a mismatch produces tiles that paint to the wrong cells rather than an error; [root-links.md](references/root-links.md) pins which package version each feature below belongs to. One `Grid` with several `Tilemap` children keeps ground, walls, and decoration cell-aligned; separate `Grid` hierarchies with differing cell sizes are the usual cause of misalignment.
2. **Create the palette through the Tile Set Importer whenever the art will change again**, per [tile-palette-and-tiles.md](references/tile-palette-and-tiles.md) — tiles produced by dragging a texture in are **not** linked back to it, so a later art edit silently fails to propagate, while importer-generated tiles regenerate on source change. Manual drag-in is for a settled, final palette only.
3. **Set each `Tile`'s Collider Type to the cheapest shape that plays correctly** — Grid for anything whose silhouette matches its cell, Sprite only where the outline genuinely differs, per `performance-and-algorithms.md`'s Physics section. Sprite type consumes the physics shape authored by `unity-2d-sprite`, so it is only as good as that authoring.
4. **Derive isometric Cell Size y from the sprite, never by eye**, per [isometric-hexagonal.md](references/isometric-hexagonal.md) — it is the tile's 3D floor height in pixels divided by its width in pixels, and it is the single most common source of a grid that will not line up. Hexagonal Flat Top swaps which axis governs which spacing, so a value copied from a Point Top project is wrong by construction.
5. **Set the isometric sort axis before judging any depth problem** — Transparency Sort Mode Custom Axis with axis (0, 1, 0), on the 2D Renderer Data under URP or under Project Settings > Graphics > Camera Settings for the Built-in pipeline. The general sorting semantics belong to `unity-2d-sprite`; this step is the isometric-specific value.
6. **Keep `TilemapRenderer` on Chunk mode unless tiles must interleave with other sprites**, per [tilemap-renderer.md](references/tilemap-renderer.md) — Individual mode gives per-tile depth sorting and gives up batching to do it. Set Detect Chunk Culling Bounds to Manual whenever tiles carry oversized sprites or GameObject-brush content, since an underestimated bound pops content in at chunk edges.
7. **Pair `TilemapCollider2D` with a `CompositeCollider2D` for level terrain**, per [tilemap-collider-2d.md](references/tilemap-collider-2d.md) — merging beats hundreds of per-tile colliders, and Composite Operation and Order do nothing at all until that component is actually present. Hand the resulting body and material to `unity-2d-physics`.
8. **Check the 2D Tilemap Extras package before writing anything custom** ([tilemap-extras-tiles.md](references/tilemap-extras-tiles.md), [tilemap-extras-brushes.md](references/tilemap-extras-brushes.md)) — Rule Tile, Auto Tile, and Animated Tile already solve most auto-tiling, terrain-blending, and animation needs, and the Line, Random, Group, and GameObject brushes cover most repetitive painting, compared against the Default brush in [brushes.md](references/brushes.md). None of them ship with core Unity, so confirm the package is installed first.
9. **Order Rule Tile rules with the most common case first** — evaluation is sequential top-to-bottom and stops at the first match, so rule order is both a correctness decision and an edit-time cost. Choose Rule Tile when neighbour conditions are authored explicitly, and Auto Tile when the art already arrives as a masked floor-layout sheet.
10. **Write a custom `TileBase` or `GridBrushBase` only once nothing built-in or Extras fits**, per [custom-tiles-and-brushes.md](references/custom-tiles-and-brushes.md) and YAGNI in `coding-principles.md` — and follow `naming-convention.md` for the class name, since these become project assets other people pick from a dropdown.
11. **Batch runtime tile edits and keep them out of `Update`**, per [scripting-api.md](references/scripting-api.md) — `SetTiles`, `BoxFill`, and `FloodFill` avoid the repeated collider and render invalidation a loop of `SetTile` calls causes, and a tile change should be event-driven. Note that exceeding Maximum Tile Change Count turns an incremental collider update into a full rebuild.
12. **Keep the layout's meaning out of this layer**, per `coding-principles.md`'s Shared Core integrity section — `Game.Core.*` decides which tile a generator or a destruction rule produces, and this skill's components only paint, render, and collide the result. `GridInformation` may carry authoring metadata to the painting layer, but it never interprets it.

## 5. Specific goals / tasks this skill performs
- `Grid` and `Tilemap` hierarchy setup, including non-rectangular layouts and Z as Y height.
- Tile Palette creation by either path, and `Tile` asset authoring.
- Painting workflows, brush selection, and Brush Picks.
- `TilemapRenderer` and `TilemapCollider2D` configuration, including composite pairing.
- Batched runtime tile edits through the `Tilemap` API.
- Rule Tile, Auto Tile, Animated Tile, override variants, and `GridInformation` metadata.
- Custom Scriptable Tiles and Brushes when no built-in covers the requirement.
- Out of scope: sprite import and atlasing (`unity-2d-sprite`), 2D physics dynamics (`unity-2d-physics`), spline geometry (`unity-2d-spriteshape`), 2D lighting (`unity-urp-rendering`), level-generation rules (`csharp-engineer`).

## 6. Output format
```
## Tilemap Work — <level/feature name>
- Layout: Cell Layout <Rectangle/Hexagon/Isometric/Isometric Z as Y>, Cell Size <x,y>, Gap, Swizzle; Tilemap layers <names and purpose>
- Palette: creation path <Tile Set Importer/manual drag-in> and why, Grid type match confirmed <yes/no>
- Tiles: Collider Type(s) used and rationale, GameObject to Instantiate <yes/no>
- Painting: brush(es) used, Brush Picks saved, Extras package installed <yes/no/not needed>
- Renderer: Mode <Chunk/Individual/SRP Batch>, sorting, mask interaction, chunk culling <Auto/Manual + bound>
- Collision: TilemapCollider2D <yes/no>, CompositeCollider2D <yes/no>, Extrusion Factor, Delaunay <on/off>
- Isometric/Hex (if applicable): Cell Size y derivation, sort mode and axis, Point Top vs Flat Top
- Extras / custom (if applicable): Rule Tile / Auto Tile / Animated Tile used, or why a custom TileBase/GridBrushBase was needed
- Shared Core boundary: <what Core decides vs what this layer paints>
- Layer: Game.Client.* / Editor-only (palette and tile assets)
- Known limitations: <...>
```

**Extended report — emit ONLY when the requester asks for it.** It replaces the one-line `Known limitations` above with all three fields:
```
- Known limitations: <what the delivered solution does not cover — omit this line entirely if there are genuinely none>
- Latent concerns: <failure modes not yet triggered: assumptions that hold only under current conditions, thresholds not yet reached, trade-offs knowingly deferred>
- Future remediation: <the concrete fix for each concern above, each with the condition that should trigger it>
```

## 7. Examples
**Example 1**
- Input: "Platformer level: ground the player stands on, plus background tiles that should not collide."
- Output: one `Grid` with Ground and Background `Tilemap` children so both stay cell-aligned; palette built through the Tile Set Importer because the tileset is still being iterated; Ground tiles at Collider Type Grid and Background at None; `TilemapCollider2D` plus `CompositeCollider2D` on Ground only, backed by a Static `Rigidbody2D`; both renderers left on Chunk mode with Background behind via Order in Layer. Hand-off: the ground's physics material and any effector → `unity-2d-physics`; the tileset's import settings → `unity-2d-sprite`.

**Example 2**
- Input: "Write a custom TileBase that picks the right wall sprite based on its neighbours."
- Output: declined as new code. That is exactly Rule Tile: a 3×3 neighbour grid of match, no-match, and don't-care conditions mapped to output sprites, already shipping in 2D Tilemap Extras with editor tooling, override variants, and animation output. Installed the package, authored the rules with the most common case first because evaluation stops at the first match, and kept a custom `RuleTile<T>` subclass on the table only for the one case needing a neighbour condition the built-in set cannot express — where custom neighbour IDs start at 3, since 0 to 2 are reserved.

**Example 3**
- Input: "The isometric map's tiles don't line up and the depth sorting looks inverted."
- Output: two independent causes, both usual. Cell Size y had been set to a round 0.5 rather than derived — the actual sprites are 64 px wide with a 24 px floor, giving 0.375 — and the palette and `Grid` must both carry it. Separately, the 2D Renderer Data was on the default Transparency Sort Mode, which sorts by camera distance and reads backwards for an isometric camera; set Custom Axis with axis (0, 1, 0). Fixing only the first leaves the sorting wrong and invites a second round of "it's still broken".

## 8. Edge cases & guardrails
- Never assume a drag-in palette tracks its source art — those `Tile` assets have no link back, so texture edits silently do not propagate.
- Never let the palette's Grid type and the `Tilemap`'s Cell Layout diverge — painting goes to the wrong cells rather than reporting a mismatch.
- Never set isometric Cell Size y by eye — derive it from floor height over tile width, and re-derive it whenever the tile art's dimensions change.
- Never reuse a Point Top hexagonal Cell Size on a Flat Top grid — the axes govern the opposite spacings.
- Never expect Composite Operation or Composite Order to do anything without an actual `CompositeCollider2D` on the object.
- Never leave chunk culling on Auto when tiles carry oversized sprites or painted GameObjects — content pops in at chunk boundaries.
- Never switch `TilemapRenderer` to Individual mode for depth that Sorting Layers already express — it gives up batching for the whole tilemap.
- Never reference a Rule Tile, Auto Tile, Animated Tile, or a Line, Random, Group, or GameObject brush without confirming 2D Tilemap Extras is installed — none of them ship with core Unity.
- Never assume Random Brush respects per-tile weighting — its pool is uniform, so a "rare" variant needs a different mechanism.
- Never edit tiles from `Update` — batch through `SetTiles`, `BoxFill`, or `FloodFill` on an event, per `performance-and-algorithms.md`'s hot-path rules.
- Never use `SwapTile` to change one cell — it replaces every instance of that tile across the whole tilemap.
- Never decide gameplay state inside a tile's `GetTileData` or a brush — those run at edit time as well as runtime, and the decision belongs in Shared Core.
- If a misalignment could be Cell Size, Grid type, or pivot, name which is being assumed before editing shared palette assets — a palette is referenced by every scene painted from it.

---
name: unity-tilemap
description: >
  Technique for Unity's built-in Tilemap authoring pipeline
  (`UnityEngine.Tilemaps.*`, `UnityEditor.Tilemaps.*`) — the `Grid`/`Tilemap`
  GameObject hierarchy, Tile Palette creation (manual drag-in vs. the
  auto-updating Tile Set Importer), Tile asset properties (Sprite, Color,
  Collider Type, Flags, GameObject to Instantiate), the Tile Palette
  window's painting toolbar (Paint/Box Fill/Flood Fill/Eraser/Rotate/Flip),
  built-in brush types (Default plus the 2D Tilemap Extras package's
  Line/Random/GameObject/Group) and Brush Picks, `TilemapRenderer` (Mode
  Chunk/Individual/SRP Batch, sorting, mask interaction),
  `TilemapCollider2D` + `Composite Collider 2D` collision generation,
  isometric tilemaps (Cell Size y, Isometric Z as Y, Custom Axis
  transparency sorting) and hexagonal tilemaps (Point Top/Flat Top), custom
  Scriptable Tiles (`TileBase`/`TileData`) and Scriptable Brushes
  (`GridBrushBase`), and the 2D Tilemap Extras package
  (`com.unity.2d.tilemap.extras`: `RuleTile`, `AnimatedTile`, Auto Tile,
  Rule/Advanced Rule Override Tile, `GridInformation`). Use this for any
  task touching `Tilemap`, `TilemapRenderer`, `TilemapCollider2D`, the Tile
  Palette window, `Tile` assets, `Grid` (when its Cell Layout is set up for
  tilemap painting), custom `TileBase`/`GridBrushBase` scripting, or the 2D
  Tilemap Extras package's brushes/tiles. Do not use this for
  authoring the underlying Sprite art (import settings, Sprite Editor
  slicing/outline/physics-shape/atlas packing) tiles are made from — that's
  `unity-2d-sprite`, a separate skill; this skill only consumes
  already-imported `Sprite` assets as tile art. Do not use this for
  `Rigidbody2D`/`Collider2D` dynamics, effectors, or joints beyond what
  `TilemapCollider2D` itself generates — that's `unity-2d-physics`. Do not
  use this for URP 2D Lighting (`Light2D`, 2D Renderer Data) consuming a
  tile sprite's secondary textures — that's `unity-urp-rendering`. Do not
  use this for Sprite Shape (a separate spline-based 2D authoring system,
  no dedicated skill exists yet in this project — flag as out of scope). Do
  not use this for gameplay rule logic that happens to decide tilemap
  content (procedural level generation, which tile a destructible-terrain
  rule should place) — that belongs in Shared Core per
  `coding-principles.md`'s Shared Core integrity rule; this skill only
  covers wiring the Unity-side tilemap components/painting themselves.
---

# Unity Tilemap — Built-in Grid/Tilemap Authoring, Rendering, Collision & Custom Tiles/Brushes

Sources: see [references/](references/) for the Unity Manual root links, split by topic — [root-links.md](references/root-links.md), [grid-and-tilemap.md](references/grid-and-tilemap.md), [tile-palette-and-tiles.md](references/tile-palette-and-tiles.md), [brushes.md](references/brushes.md), [tilemap-renderer.md](references/tilemap-renderer.md), [tilemap-collider-2d.md](references/tilemap-collider-2d.md), [isometric-hexagonal.md](references/isometric-hexagonal.md), [custom-tiles-and-brushes.md](references/custom-tiles-and-brushes.md), [scripting-api.md](references/scripting-api.md), [tilemap-extras-tiles.md](references/tilemap-extras-tiles.md), [tilemap-extras-brushes.md](references/tilemap-extras-brushes.md).

## 1. Objective
Configure Unity's built-in Tilemap pipeline correctly — right `Grid`/`Tilemap` hierarchy, right Tile Palette creation path, right `TilemapRenderer`/`TilemapCollider2D` settings for the visual/collision requirement, right isometric/hexagonal layout math, right custom tile/brush only when the built-ins genuinely fall short — without drifting into sprite authoring, 2D physics dynamics, URP lighting, Sprite Shape, or gameplay rule logic that belong to sibling skills or roles.

## 2. Role
Act as the built-in Tilemap authoring specialist: given a need for tile-based level geometry, painting tools, collision generation, or specialized grid layouts, you choose and configure the right `UnityEngine.Tilemaps`/`UnityEditor.Tilemaps`-namespace components and assets — you don't decide gameplay outcomes from tilemap state (that's Shared Core's job), you don't author the underlying Sprite art or configure `Rigidbody2D`/`Collider2D` dynamics beyond `TilemapCollider2D`'s own generation, and you don't reach into 2D lighting or Sprite Shape, which are sibling skills'/roles' territory.

## 3. When to invoke this skill
- Setting up a **`Grid`/`Tilemap` hierarchy** — Cell Size/Gap/Layout/Swizzle, Tilemap Animation Frame Rate/Color/Tile Anchor/Orientation.
- Creating a **Tile Palette** (manual drag-in vs. the auto-updating Tile Set Importer) or authoring **Tile assets** (Sprite, Color, Collider Type, Flags, GameObject to Instantiate).
- Using the **Tile Palette window** to paint/erase/fill/rotate/flip tiles, or choosing a **brush type** (Default/Line/Random/GameObject/Group) or a **Brush Pick**.
- Configuring **`TilemapRenderer`** — Mode (Chunk/Individual/SRP Batch), sorting, mask interaction, chunk culling.
- Adding **`TilemapCollider2D`** (+ `Composite Collider 2D`) to generate collision from tile data.
- Setting up an **isometric** (Cell Size y math, Isometric vs. Isometric Z as Y, Custom Axis transparency sorting) or **hexagonal** (Point Top vs. Flat Top) tilemap.
- Writing a **custom Scriptable Tile** (`TileBase`/`GetTileData`) or **Scriptable Brush** (`GridBrushBase`) when a built-in tile/brush can't express the requirement.
- Using the **2D Tilemap Extras** package (`com.unity.2d.tilemap.extras`) — **Rule Tile**/**Auto Tile**/**Animated Tile**, Rule/Advanced Rule Override Tile variants, the Line/Random/GameObject/Group brushes, or `GridInformation` per-cell metadata storage.
- Negative trigger: authoring the underlying Sprite art (import settings, Sprite Editor slicing/outline/physics-shape/secondary-textures/atlas packing) that tile art is made from — that's `unity-2d-sprite`, a separate skill despite this skill consuming its output.
- Negative trigger: configuring `Rigidbody2D`, standalone `Collider2D`, 2D joints, or 2D effectors beyond what `TilemapCollider2D` itself generates — that's `unity-2d-physics`.
- Negative trigger: setting up `Light2D`, 2D Renderer Data, or any lighting-side consumption of tile sprites' secondary textures — that's `unity-urp-rendering`.
- Negative trigger: Sprite Shape authoring — a separate spline-based 2D system; no dedicated skill exists yet in this project, flag explicitly as out of scope rather than guessing at a workflow.
- Negative trigger: the actual gameplay decision that happens to be expressed through tilemap content (procedural level generation, a destructible-terrain rule deciding which tile replaces a broken wall) — that's `csharp-engineer`'s Shared Core, per `coding-principles.md`'s Shared Core integrity rule; this skill stops at placing/rendering/colliding whatever layout Core already decided.

## 4. How to use this skill
1. **Confirm scope first.** This skill is the built-in Tilemap authoring pipeline (`Grid`/`Tilemap`/`TilemapRenderer`/`TilemapCollider2D`, Tile Palette, custom tiles/brushes). If the task is authoring the Sprite art itself, hand off to `unity-2d-sprite`. If it's 2D physics dynamics beyond collision generation, hand off to `unity-2d-physics`. If it's 2D lighting, hand off to `unity-urp-rendering`. If it's Sprite Shape, state explicitly that no dedicated skill covers it yet.
2. **Set up `Grid`/`Tilemap` deliberately**, per [grid-and-tilemap.md](references/grid-and-tilemap.md): one shared `Grid` per set of cell-aligned layers (ground/walls/decoration as separate `Tilemap` children), Cell Layout matched to the design (Rectangle by default, Hexagon/Isometric per [isometric-hexagonal.md](references/isometric-hexagonal.md)).
3. **Build the Tile Palette the right way**, per [tile-palette-and-tiles.md](references/tile-palette-and-tiles.md): the auto-updating Tile Set Importer path for art still under iteration, manual drag-in only for a settled final palette. Set each Tile's Collider Type to `Grid` by default (cheapest) and `Sprite` only when the silhouette genuinely needs it.
4. **Respect the Shared Core boundary.** Any gameplay decision that happens to manifest as tilemap content (procedural level layout, which tile a destructible-terrain event places) is decided in `Game.Core.*`; this skill's components only paint/render/collide whatever layout Core already resolved — they never decide it themselves, per `coding-principles.md`'s Shared Core integrity rule.
5. **Configure `TilemapRenderer` deliberately**, per [tilemap-renderer.md](references/tilemap-renderer.md): Mode = Chunk by default, Individual only when tiles must depth-sort against other sprites; set Manual chunk culling bounds when tile content extends past the auto-estimated bounds.
6. **Add `TilemapCollider2D` + `Composite Collider 2D` for level terrain**, per [tilemap-collider-2d.md](references/tilemap-collider-2d.md) — merge shapes rather than leaving hundreds of per-tile colliders; hand off the resulting body's `Rigidbody2D`/effector/joint configuration to `unity-2d-physics`.
7. **Get isometric/hexagonal math right before painting**, per [isometric-hexagonal.md](references/isometric-hexagonal.md): verify the isometric Cell Size y formula against the actual imported sprite's pixel dimensions, and confirm Point Top vs. Flat Top's swapped Cell Size axis semantics before reusing settings across projects.
8. **Check the 2D Tilemap Extras package before writing anything custom** ([tilemap-extras-tiles.md](references/tilemap-extras-tiles.md), [tilemap-extras-brushes.md](references/tilemap-extras-brushes.md)) — confirm it's installed (Package Manager > Unity Registry), then reach for Rule Tile/Auto Tile/Animated Tile or the Line/Random/GameObject/Group brushes before writing a fully custom `TileBase`/`GridBrushBase`.
9. **Reach for a fully custom Scriptable Tile/Brush only when a built-in one — core or Extras package — genuinely can't express the requirement** ([custom-tiles-and-brushes.md](references/custom-tiles-and-brushes.md)) — non-standard neighbor logic, non-standard painting; per YAGNI in `coding-principles.md`.
10. **Use the batched `Tilemap` scripting API** ([scripting-api.md](references/scripting-api.md)) — `SetTiles`/`BoxFill`/`FloodFill` over a hand-rolled loop of `SetTile` calls, and never edit tiles from a per-frame hot path.
11. **State the hand-off explicitly.** Sprite art authoring → `unity-2d-sprite`. 2D physics dynamics beyond collision generation → `unity-2d-physics`. 2D Lighting → `unity-urp-rendering`. Sprite Shape → flagged as uncovered, not improvised. Gameplay decisions behind tilemap content → `csharp-engineer`'s Shared Core.

## 5. Specific goals / tasks this skill performs
- Setting up `Grid`/`Tilemap` hierarchies and their cell-layout properties.
- Creating Tile Palettes (manual or Tile Set Importer) and authoring Tile asset properties.
- Painting/erasing/filling tiles via the Tile Palette window, choosing brush types, and managing Brush Picks.
- Configuring `TilemapRenderer` (mode, sorting, mask interaction, chunk culling).
- Adding `TilemapCollider2D` + `Composite Collider 2D` for tile-derived collision.
- Setting up isometric (including Z-as-Y height) and hexagonal (Point Top/Flat Top) tilemaps.
- Writing custom Scriptable Tiles (`TileBase`) and Scriptable Brushes (`GridBrushBase`).
- Using the `Tilemap` scripting API for batched runtime tile edits.
- Using the 2D Tilemap Extras package's Rule Tile/Auto Tile/Animated Tile, Rule/Advanced Rule Override Tile, Line/Random/GameObject/Group brushes, and `GridInformation`.
- Out of scope: Sprite import/Sprite Editor/atlas authoring (`unity-2d-sprite`); `Rigidbody2D`/`Collider2D`/joint/effector configuration beyond `TilemapCollider2D`'s own generation (`unity-2d-physics`); `Light2D`/2D Renderer Data lighting setup (`unity-urp-rendering`); Sprite Shape (uncovered — flag explicitly); gameplay rule logic driving tilemap content (`csharp-engineer`'s Shared Core).

## 6. Output format
```
## Tilemap Work — <level/feature name>
- Scope confirmed: built-in Tilemap pipeline (not Sprite authoring, not 2D physics dynamics, not 2D Lighting, not Sprite Shape)
- Grid/Tilemap setup (if applicable): Cell Layout <Rectangle/Hexagon/Isometric/Isometric Z as Y>, Cell Size/Gap/Swizzle, Tilemap layer(s) and their purpose
- Tile Palette (if applicable): creation path <manual drag-in/Tile Set Importer>, Tile Collider Type(s) used, rationale
- Painting/brushes (if applicable): brush type(s) used, Brush Picks saved
- TilemapRenderer settings: Mode, sorting, mask interaction, chunk culling as applicable
- TilemapCollider2D (if applicable): Composite Collider 2D pairing <yes/no>, Extrusion Factor, Use Delaunay Mesh, rationale
- Isometric/Hexagonal (if applicable): Cell Size y calculation, sort mode/axis, Point Top vs Flat Top
- 2D Tilemap Extras (if applicable): package installed <yes/no>, tile/brush type(s) used (Rule Tile/Auto Tile/Animated Tile/Line/Random/GameObject/Group/GridInformation)
- Custom Tile/Brush (if applicable): why neither a core built-in nor an Extras-package tile/brush covered the requirement
- Shared Core boundary: confirmed no gameplay decision made in tilemap-layer code
- Hand-off: <sprite authoring → unity-2d-sprite / physics dynamics → unity-2d-physics / lighting → unity-urp-rendering / Sprite Shape → flagged uncovered / gameplay logic → csharp-engineer, as applicable>
- Known limitations: <...>
```

## 7. Examples
**Example 1**
- Input: "Build a simple platformer level: ground tiles the player can stand on, plus a few decorative background tiles that shouldn't collide."
- Output: created one `Grid` with two `Tilemap` children ("Ground", "Background") sharing Cell Layout = Rectangle; populated a Tile Palette via the Tile Set Importer from the existing tileset texture (still under art iteration); set Ground tiles' Collider Type = Grid, Background tiles' Collider Type = None; added `TilemapCollider2D` + `Composite Collider 2D` (Static `Rigidbody2D`) to the Ground tilemap only; kept `TilemapRenderer` on default Chunk mode for both layers, Background sorted behind Ground via Order in Layer.
- Hand-off: the Ground `Rigidbody2D`'s physics material/friction tuning and any player-vs-ground effector behavior → `unity-2d-physics`; the tileset art's import settings/slicing → `unity-2d-sprite` (assumed already done, tileset was pre-existing).

**Example 2**
- Input: "An isometric strategy map with a few elevated plateau tiles, and a destructible wall that should swap to a rubble tile when destroyed."
- Output: set the Tile Palette and `Grid` to Isometric Z as Y, computed Cell Size y from the tileset's actual floor-height/tile-width pixel ratio, set the 2D Renderer's Transparency Sort Mode to Custom Axis (0,1,0); painted the plateau tiles at a raised Z-as-Y height using the Isometric Z as Y tilemap; for the destructible wall, wired a `Tilemap.SetTile` call that swaps the wall tile for a rubble tile at a specific cell.
- Hand-off: the actual "wall is destroyed" decision (damage threshold, trigger condition) → `csharp-engineer`'s Shared Core; this skill's code only executes the `SetTile` swap once Core signals the wall broke.

## 8. Edge cases & guardrails
- Never assume this skill covers authoring the Sprite art tiles are made from — route Sprite import settings, Sprite Editor work, and atlas packing to `unity-2d-sprite`.
- Never assume `Rigidbody2D`/standalone `Collider2D`/effector/joint configuration is this skill's territory, even on the same GameObject as `TilemapCollider2D` — route that to `unity-2d-physics`.
- Never assume `Light2D`/2D Renderer Data lighting setup is this skill's territory — route that to `unity-urp-rendering`.
- Sprite Shape is a separate spline-based 2D authoring system; this project has no dedicated skill for it yet — state that explicitly rather than stretching this skill's guidance to cover it.
- Never make a gameplay decision (which tile a procedural generator or destructible-terrain rule should place) inside tilemap-layer code — resolve the decision in Shared Core and let `Tilemap`/`Tile`/brush code only carry out whatever layout Core already decided.
- Manually drag-in Tile Palettes are **not** linked back to their source sprite/texture — a source-art edit silently doesn't propagate; use the Tile Set Importer path whenever the art is still iterating.
- The isometric Cell Size y formula and Flat-Top's swapped x/y Cell Size axis semantics are common, easy-to-miss sources of misaligned tiles — verify both explicitly against the actual sprite/palette rather than reusing a value from another project without checking.
- `Composite Operation`/`Composite Order` on `TilemapCollider2D` only take effect when paired with an actual `Composite Collider 2D` component — verify that component is present before assuming those settings do anything.
- Don't reach for a custom `TileBase`/`GridBrushBase` when a built-in tile + Default/Line/Random/GameObject/Group brush, or a 2D Tilemap Extras Rule Tile/Auto Tile/Animated Tile, already expresses the requirement — see YAGNI in `coding-principles.md`.
- The Line/Random/GameObject/Group brushes and Rule Tile/Animated Tile/Auto Tile all require the separate **2D Tilemap Extras** package (`com.unity.2d.tilemap.extras`) to be installed (Package Manager > Unity Registry) — never assume they're available in a project without confirming the package is present.
- The core `UnityEditor.Tilemaps.GridBrushBase`/`GridBrush` Scripting API pages, and the Extras package's `UnityEngine.Tilemaps.RuleTile<T>` page, were unreachable (404) at authoring time; this skill's `GridBrushBase` guidance is sourced from the Manual workflow page and its Rule Tile guidance from the Manual's Inspector reference — verify current method signatures against the live Scripting API or the `com.unity.2d.tilemap.extras` package source before implementing a custom brush or extending `RuleTile<T>`.

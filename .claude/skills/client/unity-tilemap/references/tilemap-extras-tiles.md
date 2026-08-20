# 2D Tilemap Extras — Tile Types (Animated, Rule, Auto)

Sources: https://docs.unity3d.com/Packages/com.unity.2d.tilemap.extras@8.0/manual/index.html, https://docs.unity3d.com/Packages/com.unity.2d.tilemap.extras@8.0/manual/Tiles.html, https://docs.unity3d.com/Packages/com.unity.2d.tilemap.extras@8.0/manual/AnimatedTile.html, https://docs.unity3d.com/Packages/com.unity.2d.tilemap.extras@8.0/manual/RuleTile-landing.html, https://docs.unity3d.com/Packages/com.unity.2d.tilemap.extras@8.0/manual/RuleTile-introduction.html, https://docs.unity3d.com/Packages/com.unity.2d.tilemap.extras@8.0/manual/RuleTile.html, https://docs.unity3d.com/Packages/com.unity.2d.tilemap.extras@8.0/manual/RuleTile-Inspector.html, https://docs.unity3d.com/Packages/com.unity.2d.tilemap.extras@8.0/manual/CustomRulesForRuleTile.html, https://docs.unity3d.com/Packages/com.unity.2d.tilemap.extras@8.0/manual/RuleOverrideTile.html, https://docs.unity3d.com/Packages/com.unity.2d.tilemap.extras@8.0/manual/AdvancedRuleOverrideTile.html, https://docs.unity3d.com/Packages/com.unity.2d.tilemap.extras@8.0/manual/AutoTile.html, https://docs.unity3d.com/Packages/com.unity.2d.tilemap.extras@8.0/manual/AutoTile-Inspector.html, https://docs.unity3d.com/Packages/com.unity.2d.tilemap.extras@8.0/manual/sample-projects.html, `UnityEngine.Tilemaps.AnimatedTile` scripting API

## Package requirement

Every tile type on this page ships in the separate **2D Tilemap Extras** package (`com.unity.2d.tilemap.extras`), not Unity's core Tilemap module — install it first via **Window > Package Manager > Unity Registry > 2D Tilemap Extras** before creating any asset described below.

## Animated Tile

Plays through a list of sprites in sequence — for a waterfall, a torch, an idle-animated decoration.

1. Right-click in the Project window > **Create > 2D > Tiles > Animated Tile**.
2. Lock the Inspector, drag sprites in one by one (each becomes a frame).
3. Add the tile to a palette and paint it. Animation only plays in **Play mode**, not in the Scene view while editing.

| Property | Description |
|---|---|
| Sprite List | The animation's frames, reorderable by drag handle. |
| Minimum / Maximum Speed | Unity picks a random playback speed (fps) between these two values per instance. |
| Start Time | Initial time offset, in seconds. |
| Start Frame | Which sprite the animation begins on. |
| Collider Type | None, Sprite, or Grid — same semantics as an ordinary `Tile` (see [tile-palette-and-tiles.md](tile-palette-and-tiles.md)). |
| Animation Flags | **Loop Once** (play once, then stop), **Pause Animation**, **Update Physics** (re-evaluate collision every animation frame), **Unscaled Time** (ignore `Time.timeScale`), **Sync Animation** (keep identical tiles' animations in lock-step). |

Scripting API — `UnityEngine.Tilemaps.AnimatedTile` (extends `TileBase`): backing fields `m_AnimatedSprites`, `m_AnimationStartFrame`, `m_AnimationStartTime`, `m_MinSpeed`/`m_MaxSpeed`, `m_TileAnimationFlags`, `m_TileColliderType`; overrides `GetTileData()` and `GetTileAnimationData()`.

## Rule Tile vs. Auto Tile

Both change which sprite Unity paints based on surrounding tiles, but differ in authoring model:

| | Rule Tile | Auto Tile |
|---|---|---|
| Authoring model | Explicit per-rule neighbor conditions (3×3 grid of match/no-match/either) mapped to an output sprite. | A spritesheet of pre-drawn floor-layout sprites (corners, corridors, etc.), each tagged with a mask of which surrounding cells it represents. |
| Best for | Fine-grained, conditional control (walls that cap differently depending on 8-directional neighbors, pipes, dungeon walls). | Fast iteration when the art is already organized as a floor-layout spritesheet. |

## Rule Tile

1. **Create > 2D > Tiles > Rule Tile** (or an isometric-specific variant, if the target `Tilemap`'s Cell Layout is Isometric).
2. Set **Default Sprite** — what paints when no rule matches.
3. Click **+** under Tiling Rules to add a rule; use the 3×3 neighbor grid to mark which neighbor cells must match (green arrow), must not match (red cross), or don't care (empty).
4. Assign the rule's output **Sprite** (or Random/Animation output — see table below).
5. Order rules with the most common case first — Unity evaluates rules top-to-bottom and stops at the first match.
6. Add the tile to a palette and paint normally; editing rules/sprites later re-applies automatically across the whole tilemap.

| Property | Description |
|---|---|
| Default Sprite / Default GameObject / Default Collider | Used when no tiling rule matches. |
| Extend Neighbor | Expands the 3×3 rule grid outward for rules that need to check farther neighbors. |
| Output (per rule) | **Single** sprite, **Random** (with Noise/Shuffle/Size), or **Animation** (with Min/Max Speed, Size). |
| GameObject / Collider (per rule) | Per-rule prefab spawn / collider shape override. |

Note: the `UnityEngine.Tilemaps.RuleTile<T>` scripting API page returned 404 at authoring time — verify current members against the live Scripting API or the `com.unity.2d.tilemap.extras` package source before extending it.

**Custom neighbor-checking** — subclass `RuleTile<CustomRuleTile.Neighbor>`, define custom neighbor IDs starting at 3 (0–2 are reserved), and override `RuleMatch`:

```csharp
public override bool RuleMatch(int neighbor, TileBase tile)
{
    switch (neighbor)
    {
        case 3:
            return tile == null;
    }

    return base.RuleMatch(neighbor, tile);
}
```

**Rule Override Tile** — a variant of an existing Rule Tile that swaps sprites/GameObjects while keeping its rule logic. Drag/pick the base Rule Tile into the **Tile** field, then fill **Override Sprites**/**Override GameObjects** (leave an entry empty to keep the original).

**Advanced Rule Override Tile** — same idea, but also lets the rules themselves be overridden, not just sprites/GameObjects. Same **Tile** field to pick the base Rule Tile; the rest of the Inspector matches the base Rule Tile's own editing UI.

## Auto Tile

1. Prepare a 2×2 or 3×3 spritesheet of floor-layout sprites (corners, corridors, etc.) and slice it in the Sprite Editor.
2. **Create > 2D > Tiles > Auto Tile**.
3. Set **Default Sprite** (all-floor, no walls), **Mask Type** (Mask_2x2 or Mask_3x3), add the spritesheet under **Textures**.
4. For each sprite, click it and paint a red mask over the cells that represent floor for that layout.
5. Add to a palette; painting a tile represents floor, and Unity auto-selects the bordering sprite based on neighbors.

| Property | Description |
|---|---|
| Default Sprite / Default GameObject | Used when neighboring tiles don't match any configured mask. |
| Tile Collider | None, Sprite (Custom Physics Shape), or Grid. |
| Has Physics Shape | Read-only indicator; falls back Tile Collider to None if the sprite has no physics shape. |
| Mask Type | Mask_2x2 or Mask_3x3 — how many surrounding cells Unity checks. |
| Random | Picks randomly among sprites sharing the same mask, instead of always the first match. |
| Textures | The spritesheet(s) supplying layout sprites; **Add (+)** / **Remove (-)**. |
| Load / Save | Reuse a saved mask template across different textures. |

## Sample projects

Importable via Package Manager, each with pre-made tiles in a Tiles subfolder ready to drop onto a palette:

| Sample | Demonstrates |
|---|---|
| Waterfall Animated Tile | Animated Tile — enter Play mode to see the animation. |
| Pipe Rule Tile | Rule Tile reacting to 8-directional neighbors. |
| Dungeon Rule Tile | Rule Tile reacting to 4-directional neighbors. |
| Auto Tile (3×3) | Auto Tile floor-layout auto-selection. |

## Practical guidance

- Reach for **Rule Tile**/**Auto Tile** before writing a fully custom `TileBase` from scratch ([custom-tiles-and-brushes.md](custom-tiles-and-brushes.md)) — most auto-tiling/terrain-blending needs are already covered by one of these two, per YAGNI in `coding-principles.md`.
- Order Rule Tile rules with the most frequent case first; rule evaluation is sequential top-to-bottom, so a rarely-hit rule placed first adds unnecessary comparisons to every paint/refresh at edit time.
- Follow this project's naming convention for a custom `RuleTile<T>` subclass or its nested `Neighbor` type (PascalCase, no Hungarian prefixes) per `naming-convention.md`.
- A Rule Tile/Auto Tile only decides which **sprite** to render for a given neighbor configuration — it does not decide gameplay state. If the neighbor configuration itself represents gameplay data (e.g. "this cell is walkable"), that determination still belongs in Shared Core, per `coding-principles.md`'s Shared Core integrity rule.

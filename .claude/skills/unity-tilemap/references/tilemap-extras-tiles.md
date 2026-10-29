# 2D Tilemap Extras — Rule Tile, Auto Tile, Animated Tile

Package `com.unity.2d.tilemap.extras@8.0` (Window > Package Manager > Unity Registry). Pages: https://docs.unity3d.com/Packages/com.unity.2d.tilemap.extras@8.0/manual/Tiles.html (and RuleTile.html, AutoTile.html, AnimatedTile.html there).

| | Rule Tile | Auto Tile |
|---|---|---|
| Model | Explicit 3×3 neighbour conditions (match / no-match / don't-care) mapped to output sprites | Pre-drawn floor-layout sheet, each sprite tagged with a mask of the cells it represents |
| Choose when | Fine-grained or asymmetric conditions (wall caps by direction, pipes, dungeon edges) | Art already arrives as a layout sheet and iteration speed beats per-case control |

## Rule Tile

| Aspect | Decision |
|---|---|
| Default Sprite / GameObject / Collider | Paints when **no** rule matches; the visible sign of a coverage hole |
| Rule order | Top to bottom, **stops at first match**: order is correctness, and a rare rule first adds comparisons to every paint and refresh |
| 3×3 grid | Green arrow must match, red cross must not, empty don't care; don't-care cells prevent over-specified rules |
| Extend Neighbor | Widens the grid beyond 3×3 |
| Output per rule | **Single**, **Random** (noise, shuffle, size), or **Animation** (min/max speed) |
| Per-rule GameObject / Collider | Override for a matched case (one wall variant gains a collider) |
| Isometric | Separate Rule Tile types exist for Isometric layouts; the rectangular one does not fit their neighbour topology |

Custom neighbour conditions: subclass `RuleTile<T>`, override `RuleMatch`. **Custom neighbour IDs start at 3** (0-2 reserved). The `RuleTile<T>` API page returned 404 when this was written; confirm members against package source before subclassing.

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

| Override variant | Decision |
|---|---|
| Rule Override Tile | Swaps sprites/GameObjects, keeps base rule logic; an empty entry keeps the original |
| Advanced Rule Override Tile | Also overrides the rules; for a variant that behaves differently |

## Auto Tile

| Property | Decision |
|---|---|
| Default Sprite / GameObject | Used when neighbours match no mask |
| Mask Type | Mask_2x2 or Mask_3x3: cells examined, hence art the sheet must supply |
| Textures | Layout sheets; mask each sprite by painting the cells it represents as floor |
| Random | Picks among sprites sharing a mask; breaks repetition |
| Tile Collider / Has Physics Shape | Collider Type; read-only indicator falls back to None if the sprite has no physics shape |
| Load / Save | Reuse a mask template across textures |

## Animated Tile

| Property | Decision |
|---|---|
| Sprite List | Frames, reorderable |
| Minimum / Maximum Speed | Random rate per instance; identical tiles desynchronise |
| Start Time / Start Frame | Initial offset in seconds / frame |
| Animation Flags | Loop Once, Pause Animation, **Update Physics** (collision re-evaluated each frame), Unscaled Time, **Sync Animation** (lock-step, opposite of random speed) |

Plays in **Play mode only**; the Scene view shows a static frame while editing, which is usually why "the animation isn't working". Samples (package): Waterfall Animated Tile, Pipe Rule Tile (8-direction), Dungeon Rule Tile (4-direction), Auto Tile 3×3.

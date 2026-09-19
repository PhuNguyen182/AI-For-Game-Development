# 2D Tilemap Extras — Rule Tile, Auto Tile & Animated Tile

Sources: [Extras Tiles](https://docs.unity3d.com/Packages/com.unity.2d.tilemap.extras@8.0/manual/Tiles.html), [Animated Tile](https://docs.unity3d.com/Packages/com.unity.2d.tilemap.extras@8.0/manual/AnimatedTile.html), [Rule Tile](https://docs.unity3d.com/Packages/com.unity.2d.tilemap.extras@8.0/manual/RuleTile.html), [Custom rules for Rule Tile](https://docs.unity3d.com/Packages/com.unity.2d.tilemap.extras@8.0/manual/CustomRulesForRuleTile.html), [Auto Tile](https://docs.unity3d.com/Packages/com.unity.2d.tilemap.extras@8.0/manual/AutoTile.html).
Covers: SKILL.md §4 — **"Order Rule Tile rules with the most common case first"**.

Every tile type here ships in `com.unity.2d.tilemap.extras@8.0`, not core
Unity — install it from **Window > Package Manager > Unity Registry** first.
Between them they cover most reasons a project would otherwise write a custom
`TileBase`.

## Contents

- [Rule Tile versus Auto Tile](#rule-tile-versus-auto-tile)
- [Rule Tile](#rule-tile)
- [Auto Tile](#auto-tile)
- [Animated Tile](#animated-tile)
- [Samples](#samples)

## Rule Tile versus Auto Tile

| Axis | Rule Tile | Auto Tile | Source |
|---|---|---|---|
| Authoring model | Explicit 3×3 neighbour conditions — match, no-match, or don't-care — mapped to an output sprite | A pre-drawn floor-layout spritesheet, each sprite tagged with a mask of which surrounding cells it represents | [Extras Tiles](https://docs.unity3d.com/Packages/com.unity.2d.tilemap.extras@8.0/manual/Tiles.html) |
| Choose it when | Conditions are fine-grained or asymmetric — walls capping differently by direction, pipes, dungeon edges | The art already arrives organised as a layout sheet and iteration speed matters more than per-case control | [Extras Tiles](https://docs.unity3d.com/Packages/com.unity.2d.tilemap.extras@8.0/manual/Tiles.html) |

## Rule Tile

| Aspect | What it decides | Source |
|---|---|---|
| Default Sprite, GameObject, Collider | What paints when **no** rule matches — the visible signal that rule coverage has a hole | [Rule Tile Inspector](https://docs.unity3d.com/Packages/com.unity.2d.tilemap.extras@8.0/manual/RuleTile-Inspector.html) |
| Rule order | Evaluation runs top to bottom and **stops at the first match**, so order is a correctness decision, and a rare rule placed first adds comparisons to every paint and refresh | [Rule Tile](https://docs.unity3d.com/Packages/com.unity.2d.tilemap.extras@8.0/manual/RuleTile.html) |
| 3×3 neighbour grid | Green arrow means must match, red cross must not, empty means don't care — the don't-care cells are what keep a rule from being over-specified | [Rule Tile](https://docs.unity3d.com/Packages/com.unity.2d.tilemap.extras@8.0/manual/RuleTile.html) |
| Extend Neighbor | Widens the rule grid beyond 3×3 for conditions that must look further | [Rule Tile Inspector](https://docs.unity3d.com/Packages/com.unity.2d.tilemap.extras@8.0/manual/RuleTile-Inspector.html) |
| Output per rule | **Single** sprite, **Random** with noise, shuffle, and size, or **Animation** with min and max speed | [Rule Tile Inspector](https://docs.unity3d.com/Packages/com.unity.2d.tilemap.extras@8.0/manual/RuleTile-Inspector.html) |
| Per-rule GameObject and Collider | Overrides for a specific matched case — how one wall variant gains a collider the others do not | [Rule Tile Inspector](https://docs.unity3d.com/Packages/com.unity.2d.tilemap.extras@8.0/manual/RuleTile-Inspector.html) |
| Isometric variants | Separate Rule Tile types exist for Isometric cell layouts; the rectangular one does not fit an isometric grid's neighbour topology | [Rule Tile](https://docs.unity3d.com/Packages/com.unity.2d.tilemap.extras@8.0/manual/RuleTile.html) |

Custom neighbour conditions come from subclassing `RuleTile<T>` and overriding
`RuleMatch`. **Custom neighbour IDs start at 3** — 0 to 2 are reserved.

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

| Override variant | What it decides | Source |
|---|---|---|
| Rule Override Tile | Swaps sprites and GameObjects while keeping the base tile's rule logic; an empty entry keeps the original | [Rule Override Tile](https://docs.unity3d.com/Packages/com.unity.2d.tilemap.extras@8.0/manual/RuleOverrideTile.html) |
| Advanced Rule Override Tile | Also overrides the rules themselves, not only their outputs — the choice when a variant genuinely behaves differently | [Advanced Rule Override Tile](https://docs.unity3d.com/Packages/com.unity.2d.tilemap.extras@8.0/manual/AdvancedRuleOverrideTile.html) |

**Critical caveat**: the `RuleTile<T>` API page returned 404 at authoring time
— confirm members against the package source before subclassing, per the
disclosed-gap table in [root-links.md](root-links.md).

## Auto Tile

| Property | What it decides | Source |
|---|---|---|
| Default Sprite / GameObject | Used when neighbours match no configured mask | [Auto Tile Inspector](https://docs.unity3d.com/Packages/com.unity.2d.tilemap.extras@8.0/manual/AutoTile-Inspector.html) |
| Mask Type | Mask_2x2 or Mask_3x3 — how many surrounding cells are examined, and therefore how much art the sheet must supply | [Auto Tile](https://docs.unity3d.com/Packages/com.unity.2d.tilemap.extras@8.0/manual/AutoTile.html) |
| Textures | The layout spritesheets; each sprite is masked by painting the cells it represents as floor | [Auto Tile](https://docs.unity3d.com/Packages/com.unity.2d.tilemap.extras@8.0/manual/AutoTile.html) |
| Random | Picks among sprites sharing a mask instead of always the first — the cheap way to break visual repetition | [Auto Tile Inspector](https://docs.unity3d.com/Packages/com.unity.2d.tilemap.extras@8.0/manual/AutoTile-Inspector.html) |
| Tile Collider / Has Physics Shape | Collider Type as usual, with a read-only indicator that falls back to None when the sprite carries no physics shape | [Auto Tile Inspector](https://docs.unity3d.com/Packages/com.unity.2d.tilemap.extras@8.0/manual/AutoTile-Inspector.html) |
| Load / Save | Reuses a mask template across different textures, so a second tileset does not need re-masking | [Auto Tile Inspector](https://docs.unity3d.com/Packages/com.unity.2d.tilemap.extras@8.0/manual/AutoTile-Inspector.html) |

## Animated Tile

| Property | What it decides | Source |
|---|---|---|
| Sprite List | The frames, reorderable by drag | [Animated Tile](https://docs.unity3d.com/Packages/com.unity.2d.tilemap.extras@8.0/manual/AnimatedTile.html) |
| Minimum / Maximum Speed | A random playback rate per instance between the two — identical tiles desynchronise, which is usually the intent | [Animated Tile](https://docs.unity3d.com/Packages/com.unity.2d.tilemap.extras@8.0/manual/AnimatedTile.html) |
| Start Time / Start Frame | Initial offset in seconds and starting frame | [Animated Tile](https://docs.unity3d.com/Packages/com.unity.2d.tilemap.extras@8.0/manual/AnimatedTile.html) |
| Animation Flags | Loop Once, Pause Animation, **Update Physics** (re-evaluates collision every frame), Unscaled Time, and **Sync Animation** (keeps identical tiles in lock-step, the opposite of the random-speed behaviour) | [Animated Tile](https://docs.unity3d.com/Packages/com.unity.2d.tilemap.extras@8.0/manual/AnimatedTile.html) |
| Where it plays | **Play mode only** — the Scene view shows a static frame while editing, so "the animation isn't working" is usually just edit mode | [Animated Tile](https://docs.unity3d.com/Packages/com.unity.2d.tilemap.extras@8.0/manual/AnimatedTile.html) |

## Samples

| Sample | Demonstrates | Source |
|---|---|---|
| Waterfall Animated Tile | Animated Tile in Play mode | [Sample projects](https://docs.unity3d.com/Packages/com.unity.2d.tilemap.extras@8.0/manual/sample-projects.html) |
| Pipe Rule Tile | Eight-directional neighbour conditions | [Sample projects](https://docs.unity3d.com/Packages/com.unity.2d.tilemap.extras@8.0/manual/sample-projects.html) |
| Dungeon Rule Tile | Four-directional neighbour conditions | [Sample projects](https://docs.unity3d.com/Packages/com.unity.2d.tilemap.extras@8.0/manual/sample-projects.html) |
| Auto Tile (3×3) | Mask-driven layout selection | [Sample projects](https://docs.unity3d.com/Packages/com.unity.2d.tilemap.extras@8.0/manual/sample-projects.html) |

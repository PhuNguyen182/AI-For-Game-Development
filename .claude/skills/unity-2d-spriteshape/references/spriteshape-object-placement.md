# Sprite Shape Object Placement — Props Pinned to a Spline

Sources: [Sprite Shape Object Placement](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/manual/SSObjectPlacement.html), [SpriteShapeObjectPlacement API](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/api/UnityEngine.U2D.SpriteShapeObjectPlacement.html).
Covers: SKILL.md §4 — **"Place spline-attached props with `SpriteShapeObjectPlacement`"**.

`SpriteShapeObjectPlacement` keeps a GameObject positioned along another
object's spline — a lamp post on a winding path, a torch on a cave wall — so
it follows the outline as the level is reshaped. The one fact that shapes how
it is used: placement is addressed by control-point **index**, not by
position, so structural spline edits move every placement after them.

| Property | What it decides | Source |
|---|---|---|
| `spriteShapeController` | Which shape's spline this object rides | [SpriteShapeObjectPlacement API](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/api/UnityEngine.U2D.SpriteShapeObjectPlacement.html) |
| `startPoint` / `endPoint` | The control-point pair the object sits between. Both must be valid indices with start below end — and inserting or removing a point renumbers them, silently relocating the prop | [SpriteShapeObjectPlacement API](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/api/UnityEngine.U2D.SpriteShapeObjectPlacement.html) |
| `ratio` | Position between those two points, 0 to 1 | [SpriteShapeObjectPlacement API](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/api/UnityEngine.U2D.SpriteShapeObjectPlacement.html) |
| `setNormal` | Rotates the object to the spline's normal at that point — what makes a torch stand out from a wall rather than stay world-upright | [SpriteShapeObjectPlacement API](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/api/UnityEngine.U2D.SpriteShapeObjectPlacement.html) |
| `mode` = `Auto` | The transform can still be nudged by hand while staying constrained to the spline surface — the mode for art direction in progress | [SpriteShapeObjectPlacementMode API](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/api/UnityEngine.U2D.SpriteShapeObjectPlacementMode.html) |
| `mode` = `Manual` | Placement is driven strictly by the index and ratio data, with no free-hand editing — the mode for data-driven or script-generated placement | [SpriteShapeObjectPlacementMode API](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/api/UnityEngine.U2D.SpriteShapeObjectPlacementMode.html) |

**Critical caveat**: after any structural edit to the source spline — a point
inserted or deleted, per
[spriteshape-controller.md](spriteshape-controller.md) — re-verify every
placement that references it. Nothing warns, and the props simply appear in
the wrong places.

If a placed object's *appearance* should react to game state, that decision
belongs in `Game.Core.*` per `coding-principles.md`'s Shared Core integrity
section; this component only answers where along the spline it sits.

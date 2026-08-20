# Sprite Shape Object Placement

Sources: https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/manual/SSObjectPlacement.html, `UnityEngine.U2D.SpriteShapeObjectPlacement`/`SpriteShapeObjectPlacementMode` scripting API.

Attach a `SpriteShapeObjectPlacement` component to any GameObject to position it *along* a `SpriteShapeController`'s spline — e.g. a lamp post that should always sit on a winding path's edge, or a prop that follows a terrain outline as it's edited.

## Inspector / scripting API reference

| Property | Scripting API member | Description |
|---|---|---|
| — | `spriteShapeController` (`SpriteShapeController`) | The source controller whose spline this object is placed along. |
| Start Point | `startPoint` (`int`) | Start of the control-point pair the object is placed between. Must be a valid index in the spline and smaller than End Point. |
| End Point | `endPoint` (`int`) | End of the pair. Must be a valid index and larger than Start Point. |
| Ratio | `ratio` (`float`) | Distance ratio between Start and End points where the object sits, in `[0, 1]`. |
| Set Normal | `setNormal` (`bool`) | When enabled, rotates the object to align with the spline's normal direction at the placement point. |
| Mode | `mode` (`SpriteShapeObjectPlacementMode`) | `Auto` — the object's transform can still be edited by hand while staying constrained to the spline surface. `Manual` — placement is driven strictly by `startPoint`/`endPoint`/`ratio`; no free-hand transform editing. |

## Practical guidance

- Use `Auto` mode while a prop's exact placement is still being art-directed by hand in the Scene view; switch to `Manual` once the placement should be driven by data (e.g. spawned/positioned by a level-generation script via `startPoint`/`endPoint`/`ratio`).
- `startPoint`/`endPoint` reference the *same* spline control-point indices documented in [spriteshape-controller.md](spriteshape-controller.md) — an edit that inserts/removes control points on the source spline can shift what index a placement references; re-verify placements after structural spline edits.
- If the placed object needs to react to gameplay state (e.g. a switch that changes appearance once triggered), keep that decision in Shared Core and let this component only handle *where along the spline* it sits, per `coding-principles.md`'s Shared Core integrity rule.

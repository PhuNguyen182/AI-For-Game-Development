# Sprite Shape object placement

Sources: `manual/SSObjectPlacement.html`, `api/UnityEngine.U2D.SpriteShapeObjectPlacement.html`, `.SpriteShapeObjectPlacementMode.html`.

`SpriteShapeObjectPlacement` keeps a GameObject on another object's spline (lamp post, wall torch) as the level is reshaped. Placement is addressed by control-point **index**, so a point inserted or deleted moves every placement after it; nothing warns and props appear in wrong places. Re-verify all placements after a structural edit.

| Property | Decides |
|---|---|
| `spriteShapeController` | Which shape's spline it rides |
| `startPoint` / `endPoint` | The control-point pair it sits between; valid indices, start below end |
| `ratio` | Position between them, 0 to 1 |
| `setNormal` | Rotates the object to the spline normal (a torch stands out from a wall) |
| `mode` = `Auto` | Hand-nudgeable while constrained to the spline; for art direction in progress |
| `mode` = `Manual` | Driven strictly by index and ratio, no free-hand editing; for data-driven or scripted placement |

Appearance reacting to game state is decided in Core; this component only answers where along the spline the object sits.

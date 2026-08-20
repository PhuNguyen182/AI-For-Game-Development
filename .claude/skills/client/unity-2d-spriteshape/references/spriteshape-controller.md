# Sprite Shape Controller & Spline

Sources: https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/manual/SSController.html, `UnityEngine.U2D.SpriteShapeController`/`Spline`/`SplineControlPoint`/`ShapeTangentMode`/`QualityDetail` scripting API.

**GameObject > 2D Object > Sprite Shape** (Open Shape or Closed Shape) creates a GameObject with `SpriteShapeController`, `SpriteShapeRenderer`, and the spline data the outline is drawn with.

## Inspector reference

| Property | Description |
|---|---|
| Profile | The `SpriteShape` asset (see [spriteshape-profile.md](spriteshape-profile.md)) this instance draws sprites from. |
| Edit Spline | Toggles Control Point handles visible/editable in the Scene view. |
| Detail | Tessellation quality preset — High/Medium/Low (`QualityDetail.High`=16, `.Mid`=8, `.Low`=4 — the number is the geometry detail multiplier). |
| Open Ended | Whether the shape's two ends connect (mirrors `Spline.isOpenEnded`). |
| Adaptive UV | Enabled by default; Unity adjusts UVs to keep sprite tiling seamless as the spline is edited. |
| Enable Tangents | Adds a tangent channel to generated geometry, required for certain shader features under 2D URP (normal-map lighting) — see the 2D URP manual link in [root-links.md](root-links.md). |
| Corner Threshold | A point is treated as a corner at this angle (degrees) or lower; default 30. |
| Pixels Per Unit | Scale of the Fill texture on closed shapes; default 100. |
| World Space UV | Fill texture UVs are computed in world space instead of per-object local space. |
| Stretched Corners | Shown when a control point's corner mode is Stretched — see Point Modes below. |
| Additional Collider settings | Shown once a `Collider2D` is attached — see [spriteshape-collision.md](spriteshape-collision.md). |

## Editing the spline

With **Edit Spline** enabled and a Control Point selected, keyboard shortcuts cycle per-point behavior:

| Key | Action |
|---|---|
| M | Cycle Point Mode (Linear / Continuous Mirrored / Broken Mirrored). |
| N | Cycle which sprite variant (Angle Range sprite index) renders at this point. |
| Del | Remove the selected Control Point. |
| B | Mirror tangent lengths at the selected point. |

### Point Modes (`ShapeTangentMode`)

| Mode | `ShapeTangentMode` value | Behavior |
|---|---|---|
| Linear | `Linear` | Tangents are zero — a straight edge on both sides of the point. |
| Continuous Mirrored | `Continuous` | Left/right tangents are set so the Bezier curve stays continuous (smooth) through the point. |
| Broken Mirrored | `Broken` | Left and right tangents are set independently — allows a sharp direction change. |

## `SpriteShapeController` — key scripting API

| Member | Description |
|---|---|
| `spline` (`Spline`) | The Bezier control-point data this controller renders. |
| `spriteShape` (`SpriteShape`) | The assigned Profile asset. |
| `spriteShapeRenderer` | Returns the `SpriteShapeRenderer` component (see disclosed-gap note in [root-links.md](root-links.md) — no confirmed public API page for this type itself). |
| `splineDetail` / `colliderDetail` (`int`) | Level of detail for render / collider geometry generation. |
| `cornerAngleThreshold` (`float`) | Script-side equivalent of Corner Threshold. |
| `fillPixelsPerUnit` / `stretchTiling` (`float`) | Fill/stretch UV scale controls. |
| `enableTangents` / `worldSpaceUVs` (`bool`) | Script-side equivalents of Enable Tangents / World Space UV. |
| `autoUpdateCollider` / `optimizeCollider` / `colliderOffset` | Collider generation controls — see [spriteshape-collision.md](spriteshape-collision.md). |
| `modifiers` (`List<SpriteShapeGeometryModifier>`) / `spriteShapeCreator` | Custom geometry post-processing hooks — see [custom-geometry-scripting.md](custom-geometry-scripting.md). |
| `spriteShapeHashCode` (`int`) | Hash tracking whether the SpriteShape configuration changed. |
| `BakeMesh()` | Generates geometry on a job; returns a `JobHandle`. |
| `BakeCollider()` | Updates the collider for this object. |
| `RefreshSpriteShape()` | Forces regeneration on the next visible frame. |
| `UpdateSpriteShapeParameters()` | Forces a parameter update; returns `true` if a change was detected. |

## `Spline` — key scripting API

Index-based accessors over the control-point list (no direct indexer — always go through these methods):

| Member | Description |
|---|---|
| `isOpenEnded` (`bool`) | Script-side equivalent of Open Ended. |
| `GetPointCount()` | Number of control points. |
| `GetPosition(int)` / `SetPosition(int, Vector3)` | Control point position. |
| `GetLeftTangent(int)` / `SetLeftTangent(int, Vector3)`, `GetRightTangent(int)` / `SetRightTangent(int, Vector3)` | Tangent vectors. |
| `GetTangentMode(int)` / `SetTangentMode(int, ShapeTangentMode)` | Point Mode per point. |
| `GetHeight(int)` / `SetHeight(int, float)` | Per-point height (affects generated geometry). |
| `GetCorner(int)` / `SetCorner(int, bool)` | Whether corner mode is enabled at this point. |
| `GetSpriteIndex(int)` / `SetSpriteIndex(int, int)` | Which Angle Range sprite variant renders at this point. |
| `InsertPointAt(int, Vector3)` / `RemovePointAt(int)` | Add/remove points (throws `ArgumentException` on an invalid index). |
| `Clear()` | Removes all control points. |

`SplineControlPoint` is the plain-data struct equivalent (`position`, `height`, `leftTangent`, `rightTangent`, `mode`, `corner`, `spriteIndex`, plus a `cornerMode` (`Corner` enum: `Automatic`/`Disable`/`Stretched`) property) — used when reading/constructing point data outside the indexed `Spline` accessor API.

## Practical guidance

- Prefer `splineDetail`/`colliderDetail` tuned to the actual visual/collision fidelity the shape needs — a higher Detail level generates more geometry every bake; don't leave it at High by default for background-only shapes never seen up close (`performance-and-algorithms.md`'s measured-tradeoff principle).
- `BakeMesh()`/`BakeCollider()` are authoring/level-load-time operations — never call them from a per-frame hot path; drive spline edits from an authored/event-driven change (a level-load, an editor tool), not `Update()`.
- The actual outline shape (a procedurally generated cave wall, a destructible terrain edge) is Shared Core's decision when it's gameplay-rule-driven; this component only renders whatever control-point layout Core already resolved, per `coding-principles.md`'s Shared Core integrity rule.

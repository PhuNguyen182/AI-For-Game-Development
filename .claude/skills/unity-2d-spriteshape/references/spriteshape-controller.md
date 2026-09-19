# Sprite Shape Controller & Spline — Settings, Point Modes, API

Sources: [Sprite Shape Controller](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/manual/SSController.html), [SpriteShapeController API](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/api/UnityEngine.U2D.SpriteShapeController.html), [Spline API](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/api/UnityEngine.U2D.Spline.html).
Covers: SKILL.md §4 — **"Set Detail from how closely the shape is actually seen"**, **"Pick the Point Mode that matches the edge, not the one that looks smoothest"**.

**GameObject > 2D Object > Sprite Shape** creates a GameObject carrying a
`SpriteShapeController`, a `SpriteShapeRenderer`, and the spline the outline is
drawn from. The controller holds the per-instance shape; the Profile it points
at holds the shared look — see
[spriteshape-profile.md](spriteshape-profile.md).

## Inspector

| Property | What it decides | Source |
|---|---|---|
| Profile | The `SpriteShape` asset supplying sprites per angle | [Sprite Shape Controller](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/manual/SSController.html) |
| Edit Spline | Shows the control-point handles in the Scene view — everything below in the editing section needs it on | [Sprite Shape Controller](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/manual/SSController.html) |
| Detail | Tessellation preset, and the number behind it is the geometry multiplier: `QualityDetail.High` is 16, `Mid` is 8, `Low` is 4. Every bake pays for the choice, so a background shape never seen close does not need High | [QualityDetail API](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/api/UnityEngine.U2D.QualityDetail.html) |
| Open Ended | Whether the two ends connect; mirrors `Spline.isOpenEnded` and must agree with the Profile's topology | [Sprite Shape Controller](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/manual/SSController.html) |
| Adaptive UV | On by default; adjusts UVs so tiling stays seamless as the spline is edited — turning it off is what produces visible stretching mid-segment | [Sprite Shape Controller](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/manual/SSController.html) |
| Enable Tangents | Adds a tangent channel to the generated mesh, required by 2D URP normal-map lighting. Off unless that lighting is actually in use, since it is geometry paid for either way | [Sprite Shape Controller](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/manual/SSController.html) |
| Corner Threshold | A point at or below this angle counts as a corner; default 30°. Raise it and gentle bends start consuming corner sprites, lower it and sharp bends stretch an edge sprite instead | [Sprite Shape Controller](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/manual/SSController.html) |
| Pixels Per Unit | Scale of the Fill texture on closed shapes; default 100 | [Sprite Shape Controller](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/manual/SSController.html) |
| World Space UV | Computes fill UVs in world space instead of per object — how several adjacent shapes share one continuous texture rather than each restarting it | [Sprite Shape Controller](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/manual/SSController.html) |
| Stretched Corners | Appears when a control point's corner mode is Stretched | [Sprite Shape Controller](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/manual/SSController.html) |

## Editing the spline

| Shortcut | Effect | Source |
|---|---|---|
| M | Cycles Point Mode on the selected control point | [Sprite Shape Controller](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/manual/SSController.html) |
| N | Cycles which Angle Range sprite variant renders at that point | [Sprite Shape Controller](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/manual/SSController.html) |
| B | Mirrors tangent lengths at the point | [Sprite Shape Controller](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/manual/SSController.html) |
| Del | Removes the point — and renumbers every index after it, which matters for [spriteshape-object-placement.md](spriteshape-object-placement.md) | [Sprite Shape Controller](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/manual/SSController.html) |

| Point Mode | `ShapeTangentMode` | What it decides | Source |
|---|---|---|---|
| Linear | `Linear` | Tangents are zero — a straight edge on both sides, and the correct choice for a hard architectural edge | [ShapeTangentMode API](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/api/UnityEngine.U2D.ShapeTangentMode.html) |
| Continuous Mirrored | `Continuous` | Tangents are kept mirrored so the curve stays smooth through the point | [ShapeTangentMode API](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/api/UnityEngine.U2D.ShapeTangentMode.html) |
| Broken Mirrored | `Broken` | Each side's tangent is independent, allowing a sharp direction change that still curves on both sides | [ShapeTangentMode API](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/api/UnityEngine.U2D.ShapeTangentMode.html) |

## Controller API

| Member | What it decides | Source |
|---|---|---|
| `spline`, `spriteShape` | The outline data and the Profile this instance uses | [SpriteShapeController API](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/api/UnityEngine.U2D.SpriteShapeController.html) |
| `splineDetail` / `colliderDetail` | Render and collider tessellation **independently** — a detailed silhouette can carry a coarse collider | [SpriteShapeController API](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/api/UnityEngine.U2D.SpriteShapeController.html) |
| `cornerAngleThreshold`, `fillPixelsPerUnit`, `stretchTiling`, `enableTangents`, `worldSpaceUVs` | Script equivalents of the Inspector fields above | [SpriteShapeController API](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/api/UnityEngine.U2D.SpriteShapeController.html) |
| `BakeMesh()` | Generates geometry on a job and returns a `JobHandle` — a load-time and authoring operation, never per-frame work | [SpriteShapeController API](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/api/UnityEngine.U2D.SpriteShapeController.html) |
| `RefreshSpriteShape()` | Forces regeneration on the next visible frame, rather than immediately | [SpriteShapeController API](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/api/UnityEngine.U2D.SpriteShapeController.html) |
| `UpdateSpriteShapeParameters()` | Applies parameter changes and returns whether anything actually changed — the cheap guard before forcing a rebuild | [SpriteShapeController API](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/api/UnityEngine.U2D.SpriteShapeController.html) |
| `spriteShapeHashCode` | Tracks whether the configuration changed, for tooling that must detect edits | [SpriteShapeController API](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/api/UnityEngine.U2D.SpriteShapeController.html) |

## Spline API

`Spline` exposes no indexer — every read and write goes through an
index-based accessor, and an invalid index throws rather than clamping.

| Member | What it decides | Source |
|---|---|---|
| `GetPointCount()` | Point count, and therefore the valid index range for everything below | [Spline API](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/api/UnityEngine.U2D.Spline.html) |
| `GetPosition(int)` / `SetPosition(int, Vector3)` | Control point position | [Spline API](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/api/UnityEngine.U2D.Spline.html) |
| `GetLeftTangent` / `GetRightTangent` and setters | Tangent vectors — only meaningful for non-Linear point modes | [Spline API](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/api/UnityEngine.U2D.Spline.html) |
| `GetTangentMode(int)` / `SetTangentMode(int, ShapeTangentMode)` | Point Mode from code | [Spline API](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/api/UnityEngine.U2D.Spline.html) |
| `GetHeight(int)` / `SetHeight(int, float)` | Per-point geometry height, for tapering a shape along its length | [Spline API](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/api/UnityEngine.U2D.Spline.html) |
| `GetSpriteIndex(int)` / `SetSpriteIndex(int, int)` | Which sprite from the covering Angle Range's pool renders there | [Spline API](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/api/UnityEngine.U2D.Spline.html) |
| `InsertPointAt(int, Vector3)` / `RemovePointAt(int)` | Structural edits — both renumber later indices, and throw `ArgumentException` on an invalid index | [Spline API](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/api/UnityEngine.U2D.Spline.html) |
| `SplineControlPoint` | The plain-data equivalent — `position`, `height`, tangents, `mode`, `corner`, `spriteIndex`, `cornerMode` — for reading or constructing point data outside the accessors | [SplineControlPoint API](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/api/UnityEngine.U2D.SplineControlPoint.html) |

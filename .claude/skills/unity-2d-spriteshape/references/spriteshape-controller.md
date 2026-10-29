# Sprite Shape Controller and Spline

Sources: `manual/SSController.html` (ctl), `api/UnityEngine.U2D.SpriteShapeController.html` (api), `.Spline.html`, `.ShapeTangentMode.html`, `.QualityDetail.html`, `.SplineControlPoint.html`.

**GameObject > 2D Object > Sprite Shape** creates a GameObject with a `SpriteShapeController`, a `SpriteShapeRenderer` and the spline. The controller holds the per-instance shape; the Profile ([spriteshape-profile.md](spriteshape-profile.md)) holds the shared look.

## Inspector (ctl)
| Property | Decides |
|---|---|
| Profile | The `SpriteShape` asset supplying sprites per angle |
| Edit Spline | Shows control-point handles in Scene view |
| Detail | `QualityDetail.High` 16, `Mid` 8, `Low` 4: geometry multiplier paid on every bake; a background shape needs no High |
| Open Ended | Whether ends connect; mirrors `Spline.isOpenEnded`, must agree with the Profile topology |
| Adaptive UV | On by default; keeps tiling seamless while editing. Off causes visible mid-segment stretching |
| Enable Tangents | Tangent channel for 2D URP normal-map lighting; off unless that lighting is used (geometry is paid either way) |
| Corner Threshold | Default 30 degrees; a point at or below counts as a corner. Higher: gentle bends consume corner sprites. Lower: sharp bends stretch an edge sprite |
| Pixels Per Unit | Fill texture scale on closed shapes; default 100 |
| World Space UV | Fill UVs in world space, so adjacent shapes share one continuous texture |
| Stretched Corners | Appears when a point's corner mode is Stretched |

## Editing shortcuts (ctl)
- M cycles Point Mode; N cycles the Angle Range sprite variant at the point; B mirrors tangent lengths.
- Del removes the point and renumbers later indices ([spriteshape-object-placement.md](spriteshape-object-placement.md)).

| Point Mode | `ShapeTangentMode` | Effect |
|---|---|---|
| Linear | `Linear` | Zero tangents; straight edge on both sides |
| Continuous Mirrored | `Continuous` | Mirrored tangents; smooth through the point |
| Broken Mirrored | `Broken` | Independent tangents; sharp turn, still curved both sides |

## Controller API (api)
- `spline`, `spriteShape`: outline data and Profile.
- `splineDetail` / `colliderDetail`: render and collider tessellation, independent.
- `cornerAngleThreshold`, `fillPixelsPerUnit`, `stretchTiling`, `enableTangents`, `worldSpaceUVs`: script equivalents of the fields above.
- `BakeMesh()`: generates on a job, returns a `JobHandle`; load-time/authoring only.
- `RefreshSpriteShape()`: regenerates on the next visible frame.
- `UpdateSpriteShapeParameters()`: applies changes, returns whether anything changed; the cheap guard before forcing a rebuild.
- `spriteShapeHashCode`: detects configuration changes.

## Spline API
No indexer; all access is by index and an invalid index throws rather than clamping.
- `GetPointCount()`: valid index range.
- `GetPosition(int)` / `SetPosition(int, Vector3)`.
- `GetLeftTangent` / `GetRightTangent` and setters: meaningful for non-Linear modes only.
- `GetTangentMode(int)` / `SetTangentMode(int, ShapeTangentMode)`.
- `GetHeight(int)` / `SetHeight(int, float)`: per-point height, for tapering.
- `GetSpriteIndex(int)` / `SetSpriteIndex(int, int)`: sprite from the covering Angle Range's pool.
- `InsertPointAt(int, Vector3)` / `RemovePointAt(int)`: renumber later indices; `ArgumentException` on an invalid index.
- `SplineControlPoint`: plain data (`position`, `height`, tangents, `mode`, `corner`, `spriteIndex`, `cornerMode`).

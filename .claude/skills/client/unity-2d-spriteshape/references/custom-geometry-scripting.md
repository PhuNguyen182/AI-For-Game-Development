# Custom Geometry Scripting (Advanced)

Sources: `UnityEngine.U2D.SpriteShapeGeometryModifier`/`SpriteShapeGeometryCreator`/`SplineUtility`/`BezierUtility` scripting API.

Extension points for code that needs to post-process — or fully replace — the mesh geometry Sprite Shape generates from a spline. Both are `ScriptableObject`-based abstract classes assigned via `SpriteShapeController.modifiers` / `spriteShapeCreator`.

## `SpriteShapeGeometryModifier` — post-process generated geometry

Runs **after** Sprite Shape's own geometry generation, as an additional job stage. A `SpriteShapeController` can hold a `List<SpriteShapeGeometryModifier>` (its `modifiers` property).

| Member | Description |
|---|---|
| `GetVersion()` → `int` | Version number the system uses to decide whether regeneration is needed. |
| `MakeModifierJob(JobHandle generator, SpriteShapeController spriteShapeController, NativeArray<ushort> indices, NativeSlice<Vector3> positions, NativeSlice<Vector2> texCoords, NativeSlice<Vector4> tangents, NativeArray<SpriteShapeSegment> segments, NativeArray<float2> colliderData)` → `JobHandle` | Receives the already-generated geometry buffers and returns a job handle for further modification. |

## `SpriteShapeGeometryCreator` — replace geometry generation entirely

An abstract base for generating SpriteShape geometry from scratch instead of Sprite Shape's built-in generator, assigned via `SpriteShapeController.spriteShapeCreator`.

| Member | Description |
|---|---|
| `GetVersion()` → `int` | Same regeneration-tracking role as the Modifier's. |
| `GetVertexArrayCount(SpriteShapeController)` → `int` | Determines how much vertex/index data to allocate for the job. |
| `MakeCreatorJob(SpriteShapeController, NativeArray<ushort> indices, NativeSlice<Vector3> positions, NativeSlice<Vector2> texCoords, NativeSlice<Vector4> tangents, NativeArray<SpriteShapeSegment> segments, NativeArray<float2> colliderData)` → `JobHandle` | Builds geometry from scratch via a job, returning the handle. |

Note: `SpriteShapeSegment` is referenced as a parameter type here but has no confirmed public Scripting API page of its own (see the disclosed-gap table in [root-links.md](root-links.md)) — verify its field layout against the live Scripting API or package source before writing job code against it.

## `SplineUtility` / `BezierUtility` — static math helpers

| Method | Signature | Description |
|---|---|---|
| `SplineUtility.CalculateTangents` | `static void CalculateTangents(Vector3 point, Vector3 prevPoint, Vector3 nextPoint, Vector3 forward, float scale, out Vector3 rightTangent, out Vector3 leftTangent)` | Computes left/right tangents for a control point given its neighbors. |
| `SplineUtility.SlopeAngle` | `static float SlopeAngle(Vector2 start, Vector2 end)` | Angle between two direction vectors. |
| `BezierUtility.BezierPoint` | `static Vector3 BezierPoint(Vector3 startRightTangent, Vector3 startPosition, Vector3 endPosition, Vector3 endLeftTangent, float t)` | Evaluates a point on the Bezier curve between two control points at interval `t` in `(0, 1)`. |

Useful for spline-adjacent tooling (custom placement logic, procedural spline generation) without duplicating Sprite Shape's own tangent/Bezier math by hand.

## Practical guidance

- Reach for `SpriteShapeGeometryModifier`/`spriteShapeCreator` only when the built-in generation pipeline genuinely can't express the requirement (a non-standard fill pattern, a procedural mesh detail Sprite Shape's Angle Range/Corner Sprite model doesn't cover) — for anything the standard Profile-driven generation already handles, that's simpler and better-tested, per KISS/YAGNI in `coding-principles.md`.
- These job-based methods (`MakeModifierJob`/`MakeCreatorJob`) run through Unity's Job System — the geometry buffers they receive (`NativeArray`/`NativeSlice`) follow standard Job System safety rules (no managed-object capture, disposal ownership matters); this is Job System-adjacent scripting territory, not a routine everyday task — escalate to `tech-lead-performance` or `tech-lead-csharp-unity` if the job logic itself becomes non-trivial, per the Job System escalation guidance in `performance-and-algorithms.md`.
- Don't decide gameplay outcomes (which segment is "dangerous terrain") inside a geometry modifier/creator — it only computes *mesh data*; any gameplay-relevant interpretation belongs in Shared Core, per `coding-principles.md`'s Shared Core integrity rule.

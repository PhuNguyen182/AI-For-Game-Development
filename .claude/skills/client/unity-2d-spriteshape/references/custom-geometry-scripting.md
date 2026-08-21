# Custom Geometry Scripting — Modifier, Creator & Spline Maths

Sources: [SpriteShapeGeometryModifier](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/api/UnityEngine.U2D.SpriteShapeGeometryModifier.html), [SpriteShapeGeometryCreator](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/api/UnityEngine.U2D.SpriteShapeGeometryCreator.html), [SplineUtility](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/api/UnityEngine.U2D.SplineUtility.html), [BezierUtility](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/api/UnityEngine.U2D.BezierUtility.html).
Covers: SKILL.md §4 — **"Reach for custom geometry only when the Profile model genuinely cannot express the shape"**.

Two `ScriptableObject` extension points sit either side of Sprite Shape's
generator: a **Modifier** post-processes the buffers it produced, a **Creator**
replaces it entirely. Both hand back `JobHandle`s and operate on
`NativeArray`/`NativeSlice` buffers, so both are Job System code with the
ownership and safety rules that implies — escalate non-trivial job logic per
`performance-and-algorithms.md`'s Multithreading section.

## Modifier — post-process generated geometry

| Member | What it decides | Source |
|---|---|---|
| `GetVersion()` | The version the system compares to decide whether regeneration is needed — a static return means edits never take effect | [SpriteShapeGeometryModifier](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/api/UnityEngine.U2D.SpriteShapeGeometryModifier.html) |
| `MakeModifierJob(JobHandle, SpriteShapeController, NativeArray<ushort>, NativeSlice<Vector3>, NativeSlice<Vector2>, NativeSlice<Vector4>, NativeArray<SpriteShapeSegment>, NativeArray<float2>)` | Receives indices, positions, texcoords, tangents, segments, and collider data already generated, and returns the handle for further work — chain onto the incoming handle rather than ignoring it | [SpriteShapeGeometryModifier](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/api/UnityEngine.U2D.SpriteShapeGeometryModifier.html) |
| `SpriteShapeController.modifiers` | The ordered list applied to a controller | [SpriteShapeController API](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/api/UnityEngine.U2D.SpriteShapeController.html) |

## Creator — replace generation

| Member | What it decides | Source |
|---|---|---|
| `GetVertexArrayCount(SpriteShapeController)` | How much vertex and index storage is allocated — under-reporting truncates the mesh rather than growing the buffer | [SpriteShapeGeometryCreator](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/api/UnityEngine.U2D.SpriteShapeGeometryCreator.html) |
| `MakeCreatorJob(...)` | Builds all geometry from scratch into the same buffer set a Modifier would have received | [SpriteShapeGeometryCreator](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/api/UnityEngine.U2D.SpriteShapeGeometryCreator.html) |
| `SpriteShapeController.spriteShapeCreator` | The assigned creator; setting one bypasses the built-in generator entirely, so Angle Ranges and Corner Sprites no longer apply | [SpriteShapeController API](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/api/UnityEngine.U2D.SpriteShapeController.html) |

**Critical caveat**: `SpriteShapeSegment` appears in both signatures but has no
published API page — see the disclosed-gap table in
[root-links.md](root-links.md). Confirm its layout against the package source
before writing job code that reads or writes it.

## Spline maths helpers

| Method | What it decides | Source |
|---|---|---|
| `SplineUtility.CalculateTangents(Vector3 point, Vector3 prevPoint, Vector3 nextPoint, Vector3 forward, float scale, out Vector3 rightTangent, out Vector3 leftTangent)` | Produces the same tangents the editor would, so generated splines match hand-authored ones instead of approximating them | [SplineUtility](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/api/UnityEngine.U2D.SplineUtility.html) |
| `SplineUtility.SlopeAngle(Vector2 start, Vector2 end)` | The angle between two directions — the value Angle Range selection is reasoned about in | [SplineUtility](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/api/UnityEngine.U2D.SplineUtility.html) |
| `BezierUtility.BezierPoint(Vector3 startRightTangent, Vector3 startPosition, Vector3 endPosition, Vector3 endLeftTangent, float t)` | Evaluates a point on the curve between two control points, for placement or sampling tools that must agree with the rendered outline | [BezierUtility](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/api/UnityEngine.U2D.BezierUtility.html) |

These helpers are the reason spline-adjacent tooling does not need to
re-derive Sprite Shape's tangent and Bezier maths by hand — a re-derivation
drifts from the renderer the moment either side changes.

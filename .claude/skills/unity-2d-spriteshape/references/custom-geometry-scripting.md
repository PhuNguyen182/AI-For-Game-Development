# Custom geometry: Modifier, Creator, spline maths

Sources (under `api/`): `UnityEngine.U2D.SpriteShapeGeometryModifier.html`, `.SpriteShapeGeometryCreator.html`, `.SpriteShapeController.html`, `.SplineUtility.html`, `.BezierUtility.html`.

Two ScriptableObject extension points: a **Modifier** post-processes the generated buffers, a **Creator** replaces generation. Both return `JobHandle`s over `NativeArray`/`NativeSlice` buffers, so both are Job System code; escalate non-trivial job logic per `csharp-standards` → `performance-and-algorithms.md` → Multithreading.

## Modifier
- `GetVersion()`: compared to decide whether to regenerate; a static return means edits never apply.
- `MakeModifierJob(JobHandle, SpriteShapeController, NativeArray<ushort>, NativeSlice<Vector3>, NativeSlice<Vector2>, NativeSlice<Vector4>, NativeArray<SpriteShapeSegment>, NativeArray<float2>)`: receives indices, positions, texcoords, tangents, segments and collider data already generated; chain onto the incoming handle.
- `SpriteShapeController.modifiers`: the ordered list applied.

## Creator
- `GetVertexArrayCount(SpriteShapeController)`: sizes vertex and index storage; under-reporting truncates the mesh.
- `MakeCreatorJob(...)`: builds all geometry into the same buffer set a Modifier would get.
- `SpriteShapeController.spriteShapeCreator`: setting one bypasses the built-in generator, so Angle Ranges and Corner Sprites no longer apply.

`SpriteShapeSegment` appears in both signatures but has no published page; confirm its layout against the package source before job code reads or writes it.

## Spline maths
- `SplineUtility.CalculateTangents(Vector3 point, Vector3 prevPoint, Vector3 nextPoint, Vector3 forward, float scale, out Vector3 rightTangent, out Vector3 leftTangent)`: the editor's tangents, so generated splines match hand-authored ones.
- `SplineUtility.SlopeAngle(Vector2 start, Vector2 end)`: the angle Angle Range selection is reasoned in.
- `BezierUtility.BezierPoint(Vector3 startRightTangent, Vector3 startPosition, Vector3 endPosition, Vector3 endLeftTangent, float t)`: a point on the curve, agreeing with the rendered outline.

# Root Links — 2D Sprite Shape 15.0

Source: the package Manual and Scripting API index pages listed below, as provided for this skill.
Covers: the whole skill — provenance and version anchor for every file in this folder.

Anchors every link in this folder to `com.unity.2d.spriteshape@15.0`. Keep the
`@15.0` segment when following any link from this skill; a different package
version's API may differ. Anything not reachable under a root below is outside
this skill: sprite import belongs to `unity-2d-sprite`, physics on the
generated collider to `unity-2d-physics`, grid-cell levels to `unity-tilemap`,
and 2D lighting to `unity-urp-rendering`.

| Root | Holds | Source |
|---|---|---|
| Manual | Every authoring workflow this skill covers | [Sprite Shape manual](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/manual/index.html) |
| Scripting API | Types and members for driving shapes from code | [Sprite Shape API](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/api/index.html) |
| `UnityEngine.U2D` namespace | The namespace every public type here lives in | [UnityEngine.U2D](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/api/UnityEngine.U2D.html) |

## Topic → file map

| Topic | File | Source |
|---|---|---|
| Topology, Angle Ranges, Corner Sprites, Fill | [spriteshape-profile.md](spriteshape-profile.md) | [Sprite Shape Profile](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/manual/SSProfile.html) |
| Controller settings and spline editing | [spriteshape-controller.md](spriteshape-controller.md) | [Sprite Shape Controller](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/manual/SSController.html) |
| Collider generation | [spriteshape-collision.md](spriteshape-collision.md) | [Enabling Collision](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/manual/SSCollision.html) |
| Props pinned along a spline | [spriteshape-object-placement.md](spriteshape-object-placement.md) | [Object Placement](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/manual/SSObjectPlacement.html) |
| Custom geometry generation | [custom-geometry-scripting.md](custom-geometry-scripting.md) | [SpriteShapeGeometryModifier](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/api/UnityEngine.U2D.SpriteShapeGeometryModifier.html) |

## Key types

| Type | Source |
|---|---|
| `SpriteShapeController` | [SpriteShapeController](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/api/UnityEngine.U2D.SpriteShapeController.html) |
| `Spline` | [Spline](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/api/UnityEngine.U2D.Spline.html) |
| `SplineControlPoint` | [SplineControlPoint](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/api/UnityEngine.U2D.SplineControlPoint.html) |
| `ShapeTangentMode` | [ShapeTangentMode](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/api/UnityEngine.U2D.ShapeTangentMode.html) |
| `SpriteShape` | [SpriteShape](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/api/UnityEngine.U2D.SpriteShape.html) |
| `AngleRange` | [AngleRange](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/api/UnityEngine.U2D.AngleRange.html) |
| `CornerSprite` | [CornerSprite](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/api/UnityEngine.U2D.CornerSprite.html) |
| `QualityDetail` | [QualityDetail](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/api/UnityEngine.U2D.QualityDetail.html) |
| `SpriteShapeObjectPlacement` | [SpriteShapeObjectPlacement](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/api/UnityEngine.U2D.SpriteShapeObjectPlacement.html) |
| `SplineUtility` | [SplineUtility](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/api/UnityEngine.U2D.SplineUtility.html) |
| `BezierUtility` | [BezierUtility](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/api/UnityEngine.U2D.BezierUtility.html) |

## Disclosed gaps — types with no published API page

These types appear in documented signatures or return types, but their own
pages returned HTTP 404 at authoring time. Their members are inferred, not
confirmed — verify against the live API or the package source before writing
code that depends on their layout.

| Type | Why it is referenced | Source |
|---|---|---|
| `SpriteShapeRenderer` | Declared return type of `SpriteShapeController.spriteShapeRenderer`, yet absent from the namespace index | [SpriteShapeController](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/api/UnityEngine.U2D.SpriteShapeController.html) |
| `SpriteShapeSegment` | Parameter type of the geometry job methods, as `NativeArray<SpriteShapeSegment>` | [SpriteShapeGeometryModifier](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/api/UnityEngine.U2D.SpriteShapeGeometryModifier.html) |
| `AngleRangeInfo` | Element type of `SpriteShapeController.angleRangeInfoArray` | [SpriteShapeController](https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/api/UnityEngine.U2D.SpriteShapeController.html) |
| `SpriteShapeParameters` | Inferred by naming convention only; existence unconfirmed | synthesized |
| `UnityEditor.U2D` namespace root | Editor-side tooling is not published as a separate documented namespace here | synthesized |

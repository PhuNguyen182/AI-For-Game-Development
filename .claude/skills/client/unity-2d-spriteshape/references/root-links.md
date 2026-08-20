# Root Reference Links — 2D Sprite Shape

Root Manual/Scripting API landing pages for the **2D Sprite Shape** package (`com.unity.2d.spriteshape`, version 15.0 docs). Each row's "Covered in" column points to the reference file that expands that topic with full Inspector/Scripting API detail.

## Manual

| Topic | URL | Covered in |
|---|---|---|
| Package manual index (landing) | https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/manual/index.html | (this file) |
| Sprite Shape Profile | https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/manual/SSProfile.html | [spriteshape-profile.md](spriteshape-profile.md) |
| Sprite Shape Controller | https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/manual/SSController.html | [spriteshape-controller.md](spriteshape-controller.md) |
| Enabling Collision | https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/manual/SSCollision.html | [spriteshape-collision.md](spriteshape-collision.md) |
| Sprite Shape Object Placement | https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/manual/SSObjectPlacement.html | [spriteshape-object-placement.md](spriteshape-object-placement.md) |

## Scripting API

| Topic | URL | Covered in |
|---|---|---|
| Package API index (landing) | https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/api/index.html | (this file) |
| `UnityEngine.U2D` namespace index | https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/api/UnityEngine.U2D.html | (this file) |
| `SpriteShapeController` | https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/api/UnityEngine.U2D.SpriteShapeController.html | [spriteshape-controller.md](spriteshape-controller.md) |
| `Spline` | https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/api/UnityEngine.U2D.Spline.html | [spriteshape-controller.md](spriteshape-controller.md) |
| `SplineControlPoint` | https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/api/UnityEngine.U2D.SplineControlPoint.html | [spriteshape-controller.md](spriteshape-controller.md) |
| `ShapeTangentMode` (enum) | https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/api/UnityEngine.U2D.ShapeTangentMode.html | [spriteshape-controller.md](spriteshape-controller.md) |
| `SpriteShape` (ScriptableObject) | https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/api/UnityEngine.U2D.SpriteShape.html | [spriteshape-profile.md](spriteshape-profile.md) |
| `AngleRange` | https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/api/UnityEngine.U2D.AngleRange.html | [spriteshape-profile.md](spriteshape-profile.md) |
| `CornerSprite` | https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/api/UnityEngine.U2D.CornerSprite.html | [spriteshape-profile.md](spriteshape-profile.md) |
| `Corner` (enum) | https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/api/UnityEngine.U2D.Corner.html | [spriteshape-profile.md](spriteshape-profile.md) |
| `CornerType` (enum) | https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/api/UnityEngine.U2D.CornerType.html | [spriteshape-profile.md](spriteshape-profile.md) |
| `QualityDetail` (enum) | https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/api/UnityEngine.U2D.QualityDetail.html | [spriteshape-controller.md](spriteshape-controller.md) |
| `SpriteShapeObjectPlacement` | https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/api/UnityEngine.U2D.SpriteShapeObjectPlacement.html | [spriteshape-object-placement.md](spriteshape-object-placement.md) |
| `SpriteShapeObjectPlacementMode` (enum) | https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/api/UnityEngine.U2D.SpriteShapeObjectPlacementMode.html | [spriteshape-object-placement.md](spriteshape-object-placement.md) |
| `SpriteShapeGeometryModifier` | https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/api/UnityEngine.U2D.SpriteShapeGeometryModifier.html | [custom-geometry-scripting.md](custom-geometry-scripting.md) |
| `SpriteShapeGeometryCreator` | https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/api/UnityEngine.U2D.SpriteShapeGeometryCreator.html | [custom-geometry-scripting.md](custom-geometry-scripting.md) |
| `SplineUtility` | https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/api/UnityEngine.U2D.SplineUtility.html | [custom-geometry-scripting.md](custom-geometry-scripting.md) |
| `BezierUtility` | https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/api/UnityEngine.U2D.BezierUtility.html | [custom-geometry-scripting.md](custom-geometry-scripting.md) |

## Disclosed gaps — pages that 404'd at authoring time

These URLs were guessed from strong signals (a property's declared return type, or the DocFX naming convention used by every other page in this namespace) but returned HTTP 404 when fetched directly. Don't assume they don't exist at all — verify against the live Scripting API or the package source before depending on their exact members:

| Guessed URL | Why it was guessed |
|---|---|
| `.../api/UnityEngine.U2D.SpriteShapeRenderer.html` | `SpriteShapeController.spriteShapeRenderer` is documented as returning a `SpriteShapeRenderer`, but this type is absent from the `UnityEngine.U2D` namespace index page itself — no confirmed public API page exists for it. |
| `.../api/UnityEngine.U2D.SpriteShapeSegment.html` | Referenced as a `NativeArray<SpriteShapeSegment>` parameter type in `SpriteShapeGeometryModifier`/`SpriteShapeGeometryCreator`'s job methods. |
| `.../api/UnityEngine.U2D.SpriteShapeParameters.html` | Guessed by naming-convention analogy to other packages; not confirmed to exist. |
| `.../api/UnityEngine.U2D.AngleRangeInfo.html` | `SpriteShapeController.angleRangeInfoArray` is typed `AngleRangeInfo[]`, but no confirmed public API page exists for the type itself. |
| `.../api/UnityEditor.U2D.html` | Guessed editor-only namespace root (analogous to `UnityEditor.Tilemaps` in the sibling `unity-tilemap` skill); no confirmed public API page — Editor-side Sprite Shape tooling (custom Inspectors, Scene handles) is not documented as a separate public namespace at this URL.

## Parent context

| Page | URL |
|---|---|
| 2D game development overview | https://docs.unity3d.com/Manual/Unity2D.html |
| Sprites landing (Sprite Shape paints/tiles ordinary Sprites along a spline) | https://docs.unity3d.com/Manual/sprite/sprite-landing.html |
| 2D physics collider landing (`EdgeCollider2D`/`PolygonCollider2D` fundamentals Sprite Shape's auto-generated collider builds on) | https://docs.unity3d.com/Manual/2d-physics/collider/collider-2d-landing.html |
| 2D Renderer / 2D URP lighting (referenced by Sprite Shape's Enable Tangents property) | https://docs.unity3d.com/Packages/com.unity.render-pipelines.universal@9.0/manual/2d-index.html |

## Scripting API — namespace roots

| Member | Description |
|---|---|
| `UnityEngine.U2D.SpriteShapeController` | `MonoBehaviour` holding the `Spline` and `SpriteShape` profile reference; generates SpriteShape geometry. See [spriteshape-controller.md](spriteshape-controller.md). |
| `UnityEngine.U2D.Spline` / `SplineControlPoint` | The editable outline data a `SpriteShapeController` draws geometry from. See [spriteshape-controller.md](spriteshape-controller.md). |
| `UnityEngine.U2D.SpriteShape` | `ScriptableObject` profile asset — Angle Ranges, Corner Sprites, fill texture. See [spriteshape-profile.md](spriteshape-profile.md). |
| `UnityEngine.U2D.AngleRange` / `CornerSprite` | Profile sub-data: which sprites render at which outline angle / corner type. See [spriteshape-profile.md](spriteshape-profile.md). |
| `UnityEngine.U2D.SpriteShapeObjectPlacement` | Positions a GameObject along a `SpriteShapeController`'s spline. See [spriteshape-object-placement.md](spriteshape-object-placement.md). |
| `UnityEngine.U2D.SpriteShapeGeometryModifier` / `SpriteShapeGeometryCreator` | Extension points for post-processing or fully replacing generated geometry. See [custom-geometry-scripting.md](custom-geometry-scripting.md). |
| `UnityEngine.U2D.SplineUtility` / `BezierUtility` | Static helper math for tangents, slope angle, and Bezier point evaluation. See [custom-geometry-scripting.md](custom-geometry-scripting.md). |
| `EdgeCollider2D` / `PolygonCollider2D` | Core-Unity collider types Sprite Shape auto-generates/updates mesh data for — see [spriteshape-collision.md](spriteshape-collision.md). |

For authoring the underlying Sprite art referenced by an Angle Range or Corner Sprite (import settings, Sprite Editor slicing/atlas packing), see the sibling `unity-2d-sprite` skill — this skill only consumes already-imported `Sprite` assets. For `Rigidbody2D` dynamics, effectors, or joints beyond the collider mesh `SpriteShapeController` itself auto-generates, see `unity-2d-physics`. For a grid/tile-based (non-spline) 2D level authoring alternative, see `unity-tilemap`. For 2D URP normal-map lighting setup that Enable Tangents feeds into, see `unity-urp-rendering`. For gameplay-rule-driven outline/shape decisions (procedural terrain, destructible ground), see `csharp-engineer`'s Shared Core.

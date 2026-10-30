---
name: unity-2d-spriteshape
description: "Sprite Shape spline-based 2D terrain: SpriteShapeController, profiles, corners, fill, colliders, runtime spline edits. Use for spline-built 2D levels."
user-invocable: false
---

# Unity 2D Sprite Shape

Not for: sprite import and atlasing (`unity-2d-sprite`), body/joint/material setup on the generated collider (`unity-2d-physics`), grid-cell levels (`unity-tilemap`), `Light2D` (`unity-urp-rendering`), procedural shape rules (`csharp-engineer`), heavy job logic in a custom creator (`unity-job-system-and-burst`).
Docs: https://docs.unity3d.com/Packages/com.unity.2d.spriteshape@15.0/ (`manual/`, `api/`; types in `UnityEngine.U2D`) — pinned 15.0; a different version's API may differ.

| Reference | Read when |
|---|---|
| [spriteshape-profile.md](references/spriteshape-profile.md) | Building the palette, or a sprite renders at the wrong angle |
| [spriteshape-controller.md](references/spriteshape-controller.md) | Setting up a shape, or editing an outline from code |
| [spriteshape-collision.md](references/spriteshape-collision.md) | Adding collision, or a manual collider edit keeps reverting |
| [spriteshape-object-placement.md](references/spriteshape-object-placement.md) | Pinning a prop to an outline that will keep changing |
| [custom-geometry-scripting.md](references/custom-geometry-scripting.md) | The built-in generator cannot express the shape |

## Steps
1. **Choose Open or Closed Shape first**, per [spriteshape-profile.md](references/spriteshape-profile.md). Closed loops and fills from `fillTexture`; Open has distinct ends and no fill. Fill, corners and collider choice all follow from it.
2. **Cover the whole angle space with non-overlapping Angle Ranges** — overlap makes selection ambiguous at the boundary, a gap leaves an angle with no sprite. Set Order for intersections; the first sprite in a range's pool is the default.
3. **Check sprite import before assigning art to a Profile**: Sprite (2D and UI), Single, Full Rect; any atlas with Allow Rotation and Tight Packing off. Do the import via `unity-2d-sprite`.
4. **Set Detail from how closely the shape is seen**, per [spriteshape-controller.md](references/spriteshape-controller.md). Enable Tangents only if 2D lighting consumes them; check Corner Threshold against the Profile's Corner Sprites.
5. **Pick the Point Mode that matches the edge**: Linear for a hard straight edge, Continuous Mirrored for a smooth curve, Broken Mirrored for a sharp direction change.
6. **Attach only `EdgeCollider2D` or `PolygonCollider2D`**, per [spriteshape-collision.md](references/spriteshape-collision.md), and keep `colliderDetail` independent of render Detail.
7. **Disable Update Collider before any manual collider edit**; otherwise the next spline change overwrites it. Leave it on while the art iterates.
8. **Place props with `SpriteShapeObjectPlacement`**, per [spriteshape-object-placement.md](references/spriteshape-object-placement.md). Re-check every placement after inserting or removing a point.
9. **Keep outline content out of this layer** — when a rule decides the shape (procedural terrain, destroyed ground), Core resolves the control-point layout and these components only render and collide it (`csharp-standards` → `coding-principles.md` → Shared Core integrity).
10. **Use custom geometry only when the Profile model cannot express the shape**, per [custom-geometry-scripting.md](references/custom-geometry-scripting.md). It is Job System code with the safety rules that implies.
11. **Drive spline changes from events** and keep `BakeMesh`/`BakeCollider` out of `Update` (`csharp-standards` → `performance-and-algorithms.md`).
12. **Symptom could be Profile coverage, import mode or Corner Threshold** → say which is assumed before editing; a Profile is shared by every shape that references it.

## Never
- Write against `SpriteShapeRenderer`, `SpriteShapeSegment`, `AngleRangeInfo` or `SpriteShapeParameters` without checking the live API; they had no published page (404 at authoring), so their members are inferred.
- Decide gameplay meaning inside a geometry Modifier or Creator; it computes mesh data, interpretation belongs in Shared Core.

## Output
```
## Sprite Shape Work — <level/feature name>
- Topology: Open / Closed — why
- Profile: Angle Range count and coverage, Corner Sprites <types>, Fill <texture/offset/borders or n/a>
- Sprite import: Single + Full Rect confirmed <yes/no>, atlas rotation and tight packing off <yes/no/not atlased>
- Controller: Detail <High/Mid/Low>, Open Ended, Adaptive UV, Enable Tangents <on/off + why>, Corner Threshold <deg>, PPU <n>, World Space UV
- Spline: Point Modes used, notable per-point height / corner / sprite-index choices
- Collision: <EdgeCollider2D/PolygonCollider2D/none>, colliderDetail <n>, autoUpdateCollider <on/off + why>
- Object placement: mode <Auto/Manual>, startPoint/endPoint/ratio, setNormal, index-stability note — or "none"
- Custom geometry: Modifier vs Creator, what the built-in generator could not express — or "none"
- Shared Core boundary: <what Core decides vs what this layer renders>
- Known limitations: <...>
```
On request only, add `Latent concerns` and `Future remediation`, each with its trigger.

## Example
- "Just write a geometry Creator, it's cleaner than fighting Angle Ranges" → declined: the real defect was the sprite at the top of a slope, an uncovered angle; fixed with one range edit and no code.

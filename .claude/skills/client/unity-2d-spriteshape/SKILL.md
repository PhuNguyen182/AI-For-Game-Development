---
name: unity-2d-spriteshape
description: >
  Unity 2D Sprite Shape (`com.unity.2d.spriteshape`) — spline-based world
  building that tiles and deforms Sprites along an editable outline.
  Covers `SpriteShapeController` (Detail, Open Ended, Adaptive UV, Enable
  Tangents, Corner Threshold, World Space UV), `Spline` and
  `SplineControlPoint` with `ShapeTangentMode` Linear, Continuous, Broken,
  the `SpriteShape` Profile asset with `AngleRange` and `CornerSprite`,
  auto-generated `EdgeCollider2D`/`PolygonCollider2D` geometry,
  `SpriteShapeObjectPlacement`, and `SpriteShapeGeometryModifier`. Use for
  platforms, terrain, ropes, ponds, and props pinned to a spline. Not for:
  sprite import and atlasing (`unity-2d-sprite`), body and joint setup
  (`unity-2d-physics`), grid-cell levels (`unity-tilemap`), `Light2D`
  (`unity-urp-rendering`), procedural shape rules (`csharp-engineer`).
---

# Unity 2D Sprite Shape — Spline-Based World Building

## Bundled resources

### References

| File | Contents | Read when |
|---|---|---|
| [root-links.md](references/root-links.md) | Package Manual and API roots, version pin, disclosed 404 gaps | Starting any task, or a type has no documented page |
| [spriteshape-profile.md](references/spriteshape-profile.md) | Open vs Closed, Angle Ranges, Corner Sprites, Fill, import rules | Building the palette, or a sprite renders at the wrong angle |
| [spriteshape-controller.md](references/spriteshape-controller.md) | Inspector fields, spline editing, Point Modes, `Spline` API | Setting up a shape, or editing an outline from code |
| [spriteshape-collision.md](references/spriteshape-collision.md) | Supported colliders, auto-update, collider detail, `BakeCollider` | Adding collision, or a manual collider edit keeps reverting |
| [spriteshape-object-placement.md](references/spriteshape-object-placement.md) | Placing props along a spline, Auto vs Manual mode | Pinning a prop to an outline that will keep changing |
| [custom-geometry-scripting.md](references/custom-geometry-scripting.md) | `SpriteShapeGeometryModifier`/`Creator`, spline maths helpers | The built-in generator cannot express the shape |

## 1. Objective
Turn a spline into level geometry that tiles correctly at every angle, collides at the fidelity gameplay needs, and keeps its props attached as the outline changes — while avoiding this package's characteristic silent failures: an angle the Profile's ranges do not cover, sprites imported in a mode that breaks tiling, a manual collider edit overwritten by the next spline change, and object placements that shift because their control-point indices moved.

## 2. Role
Act as the Sprite Shape authoring specialist for the client track — the skill reached for whenever spline-based 2D geometry (platforms, terrain, ropes, water bodies) must be built, tuned, or driven from code.

## 3. When to invoke this skill
- Creating or editing a `SpriteShape` Profile — Open or Closed preset, Angle Ranges, Corner Sprites, Fill texture.
- Setting up a `SpriteShapeController` — Detail, Open Ended, Adaptive UV, Enable Tangents, Corner Threshold, Pixels Per Unit, World Space UV.
- Editing an outline: control points, Point Modes, per-point height, corner mode, sprite variant, or the same through the `Spline` API.
- Enabling collision on a Sprite Shape and choosing its collider detail.
- Attaching a prop to a spline with `SpriteShapeObjectPlacement`.
- A symptom report: a sprite tiling wrong around a bend, a stretched corner where a corner sprite was expected, a shape whose collider does not follow its art.
- Writing a `SpriteShapeGeometryModifier` or `SpriteShapeGeometryCreator`.
- Negative trigger: importing, slicing, or atlasing the sprite art an Angle Range references — that's `unity-2d-sprite`; this skill only states the constraints those imports must satisfy.
- Negative trigger: the `Rigidbody2D`, material, effector, or joint attached to the generated collider — that's `unity-2d-physics`; this skill stops at generating the collider mesh.
- Negative trigger: building a level from cells on a grid — that's `unity-tilemap`, a different authoring model entirely.
- Negative trigger: `Light2D` or 2D Renderer Data setup that consumes the tangents Enable Tangents produces — that's `unity-urp-rendering`.
- Negative trigger: deciding what shape to generate — procedural terrain rules, destructible-ground logic — that's `csharp-engineer`'s Shared Core, per `coding-principles.md`'s Shared Core integrity section.
- Negative trigger: non-trivial job logic inside a custom geometry creator — escalate to `unity-job-system-and-burst` or `tech-lead-performance`.

## 4. How to use this skill
1. **Choose Open or Closed Shape before anything else**, per [spriteshape-profile.md](references/spriteshape-profile.md) — Closed loops the outline and fills the interior from `fillTexture`, Open has distinct ends and no fill at all. This is not a toggle to revisit: Fill settings, corner behaviour, and which collider makes sense all follow from it.
2. **Cover the whole angle space with non-overlapping Angle Ranges** — overlap makes sprite selection ambiguous at the boundary, and a gap leaves an outline angle with no sprite assigned. Set each range's Order for the intersections, and remember the first sprite in a range's pool is its default until a control point selects otherwise.
3. **Verify the sprite import mode before assigning art to a Profile** — Sprite Shape needs Texture Type Sprite (2D and UI), Sprite Mode Single, and Mesh Type Full Rect, and any atlas holding them must have Allow Rotation and Tight Packing off, because both distort the border data tiling depends on. Route the import work itself to `unity-2d-sprite`.
4. **Set Detail from how closely the shape is actually seen**, per [spriteshape-controller.md](references/spriteshape-controller.md) — High, Mid, and Low are geometry multipliers of 16, 8, and 4, and every bake pays for the choice. Enable Tangents only if the project's 2D lighting actually consumes them, and check Corner Threshold against the Profile's Corner Sprites so corners resolve the way the art expects.
5. **Pick the Point Mode that matches the edge, not the one that looks smoothest** — Linear for a hard straight edge, Continuous Mirrored for a smooth curve, Broken Mirrored where the outline must change direction sharply. Per-point corner mode Automatic, Disable, or Stretched then overrides what the Corner Threshold decided.
6. **Attach only `EdgeCollider2D` or `PolygonCollider2D`**, per [spriteshape-collision.md](references/spriteshape-collision.md) — no other `Collider2D` type receives generated geometry, and one added by mistake stays silently empty. Keep `colliderDetail` independent of render Detail: a background cliff can collide far more coarsely than it draws.
7. **Disable Update Collider before any manual collider edit** — with `autoUpdateCollider` on, the next spline change or bake overwrites the edit without warning. Leave it on for as long as the art is still iterating, which is most of a shape's life.
8. **Place spline-attached props with `SpriteShapeObjectPlacement`**, per [spriteshape-object-placement.md](references/spriteshape-object-placement.md) — Auto while placement is still being art-directed by hand, Manual once `startPoint`, `endPoint`, and `ratio` should drive it. Those two fields are control-point *indices*, so re-check every placement after inserting or removing points.
9. **Keep the outline's content out of this layer**, per `coding-principles.md`'s Shared Core integrity section — when a rule decides the shape (procedural terrain, ground destroyed by a hit), `Game.Core.*` resolves the control-point layout and this skill's components only render and collide it.
10. **Reach for custom geometry only when the Profile model genuinely cannot express the shape**, per [custom-geometry-scripting.md](references/custom-geometry-scripting.md) and YAGNI in `coding-principles.md` — a Modifier post-processes the generated buffers, a Creator replaces generation entirely, and both run as Job System work with the safety rules that implies.
11. **Keep `BakeMesh` and `BakeCollider` out of per-frame code** — they are authoring and load-time operations returning job handles, per `performance-and-algorithms.md`'s hot-path rules. Drive spline changes from an event, not from `Update`.
12. **Verify a type against the live API before writing code against it when it appears in this skill's disclosed-gap list** ([root-links.md](references/root-links.md)) — several types referenced by documented signatures have no published page, so their members are unconfirmed rather than known.

## 5. Specific goals / tasks this skill performs
- Sprite Shape Profile authoring: shape topology, Angle Ranges, Corner Sprites, Fill.
- `SpriteShapeController` configuration and spline outline editing, in the Editor or through the `Spline` API.
- Collider generation setup and detail tuning on the supported collider types.
- Spline-attached prop placement.
- Custom geometry extension via Modifier or Creator when the built-in generator falls short.
- Out of scope: sprite import and atlasing (`unity-2d-sprite`), 2D physics dynamics (`unity-2d-physics`), grid-cell authoring (`unity-tilemap`), 2D lighting (`unity-urp-rendering`), procedural shape rules (`csharp-engineer`), heavy job work (`unity-job-system-and-burst`).

## 6. Output format
```
## Sprite Shape Work — <level/feature name>
- Topology: Open / Closed Shape — why
- Profile: Angle Range count and angle coverage, Corner Sprites <types used>, Fill <texture/offset/borders or n/a>
- Sprite import constraint: Full Rect + Single confirmed <yes/no>, atlas rotation and tight packing off <yes/no/not atlased>
- Controller: Detail <High/Mid/Low>, Open Ended, Adaptive UV, Enable Tangents <on/off + why>, Corner Threshold <deg>, PPU <n>, World Space UV
- Spline: Point Mode(s) used, notable per-point height / corner / sprite-index choices
- Collision: collider <EdgeCollider2D/PolygonCollider2D/none>, colliderDetail <n>, autoUpdateCollider <on/off + why>
- Object placement (if applicable): mode <Auto/Manual>, startPoint/endPoint/ratio, setNormal, index-stability note
- Custom geometry (if applicable): Modifier vs Creator, what the built-in generator could not express
- Shared Core boundary: <what Core decides vs what this layer renders>
- Layer: Game.Client.*
- Known limitations: <...>
```

**Extended report — emit ONLY when the requester asks for it.** It replaces the one-line `Known limitations` above with all three fields:
```
- Known limitations: <what the delivered solution does not cover — omit this line entirely if there are genuinely none>
- Latent concerns: <failure modes not yet triggered: assumptions that hold only under current conditions, thresholds not yet reached, trade-offs knowingly deferred>
- Future remediation: <the concrete fix for each concern above, each with the condition that should trigger it>
```

## 7. Examples
**Example 1**
- Input: "Winding grass platform the player stands on, with a proper rounded sprite where the ground curves sharply."
- Output: Closed Shape Profile, since the platform has a filled interior; one Angle Range covering the near-flat top and further ranges covering the sides so no outline angle is left unassigned; Corner Sprites assigned for the outer corner types the design needs. Controller at Detail Mid with Corner Threshold left at 30°, spline built from Continuous Mirrored points along the curve and one Linear point at the hard edge. `EdgeCollider2D` attached with `autoUpdateCollider` on, since the art is still iterating, and `colliderDetail` set below render Detail because the surface only needs to be walkable. Hand-off: friction and the body on that collider → `unity-2d-physics`; the grass sprite import → `unity-2d-sprite`.

**Example 2**
- Input: "Just write a geometry Creator — it'll be cleaner than fighting with Angle Ranges."
- Output: declined. A Creator replaces geometry generation wholesale and runs as Job System code, so it inherits the safety rules, the disposal ownership, and the escalation path in `performance-and-algorithms.md` — for a requirement that was actually "the sprite at the top of a slope is wrong", which is an Angle Range that did not cover that angle. Fixed the coverage gap in the Profile, which took one range edit and no code. A Creator stays on the table only for something the Angle Range and Corner Sprite model genuinely cannot express.

**Example 3**
- Input: "The torch props on the cave wall jumped to the wrong places after the level designer reshaped it."
- Output: expected, not a bug. `SpriteShapeObjectPlacement` addresses its position by `startPoint`/`endPoint` control-point *indices*, and inserting or removing points renumbers everything after the insertion — so each placement now refers to a different pair. Re-pointed the placements after the reshape and flagged in the Implementation Note that any structural spline edit requires the same pass, since nothing warns about it.

## 8. Edge cases & guardrails
- Never leave an outline angle uncovered by an Angle Range, and never let two ranges overlap — the first leaves a segment with no sprite, the second makes selection ambiguous at the boundary.
- Never assign a sprite imported as Multiple, or with Mesh Type Tight, to a Profile — Sprite Shape requires Single and Full Rect, and border-based tiling breaks silently otherwise.
- Never pack Sprite Shape art into an atlas with Allow Rotation or Tight Packing on — both distort the border data the tiling depends on.
- Never attach a collider type other than `EdgeCollider2D` or `PolygonCollider2D` — the component sits there receiving no generated geometry.
- Never hand-edit a collider mesh with `autoUpdateCollider` still enabled — the next spline change silently discards the edit.
- Never assume `startPoint`/`endPoint` survive a structural spline edit — they are indices, and inserting a point renumbers everything after it.
- Never call `BakeMesh` or `BakeCollider` from `Update` — they are load-time and authoring-time operations, per `performance-and-algorithms.md`'s hot-path rules.
- Never decide gameplay meaning inside a geometry Modifier or Creator — it computes mesh data, and any interpretation of that data belongs in Shared Core.
- Never write against a type listed in this skill's disclosed-gap table without checking the live API first — those signatures are inferred, not confirmed.
- If the requester's symptom could be Profile coverage, import mode, or Corner Threshold, say which is being assumed before editing shared assets — a Profile is reused across every shape that references it.

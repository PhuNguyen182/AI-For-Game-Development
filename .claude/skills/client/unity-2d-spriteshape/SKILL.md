---
name: unity-2d-spriteshape
description: >
  Technique for Unity's 2D Sprite Shape package (`com.unity.2d.spriteshape`,
  `UnityEngine.U2D.*`) — the spline-based world-building system that tiles
  and auto-deforms Sprites along an editable outline. Covers the
  `SpriteShapeController` (Detail, Open Ended, Adaptive UV, Enable Tangents,
  Corner Threshold, Pixels Per Unit, World Space UV) and its `Spline`/
  `SplineControlPoint` data (Point Modes Linear/Continuous Mirrored/Broken
  Mirrored, per-point height/corner/sprite-index), the `SpriteShape` Profile
  asset (Open/Closed Shape, Angle Ranges, Corner Sprites, Fill texture),
  collision setup (`EdgeCollider2D`/`PolygonCollider2D` auto-updating
  collider mesh), `SpriteShapeObjectPlacement` (positioning a GameObject
  along the spline, Auto/Manual mode), and the advanced custom-geometry
  scripting surface (`SpriteShapeGeometryModifier`, `SpriteShapeGeometryCreator`,
  `SplineUtility`, `BezierUtility`). Use this for any task touching
  `SpriteShapeController`, a Sprite Shape Profile asset, spline/outline
  editing for 2D level geometry (platforms, terrain, ropes, ponds), or
  Sprite Shape's collider/object-placement/custom-geometry APIs. Do not use
  this for authoring the underlying Sprite art (import settings, Sprite
  Editor slicing/outline/atlas packing) an Angle Range or Corner Sprite
  references — that's `unity-2d-sprite`, a separate skill; this skill only
  consumes already-imported `Sprite` assets. Do not use this for
  `Rigidbody2D` dynamics, effectors, or joints beyond the collider mesh
  `SpriteShapeController` itself auto-generates — that's `unity-2d-physics`.
  Do not use this for grid/tile-based (non-spline) 2D level authoring —
  that's `unity-tilemap`, a separate skill covering a different (grid-cell)
  authoring model. Do not use this for 2D URP normal-map lighting setup
  itself (`Light2D`, 2D Renderer Data) that Sprite Shape's Enable Tangents
  property feeds into — that's `unity-urp-rendering`. Do not use this for
  gameplay rule logic that happens to decide outline/shape content
  (procedural terrain generation, a destructible-ground rule reshaping a
  spline) — that belongs in Shared Core per `coding-principles.md`'s Shared
  Core integrity rule; this skill only covers wiring the Unity-side spline/
  geometry components themselves.
---

# Unity 2D Sprite Shape — Spline-Based World Building

Sources: see [references/](references/) for the package Manual/Scripting API root links, split by topic — [root-links.md](references/root-links.md), [spriteshape-profile.md](references/spriteshape-profile.md), [spriteshape-controller.md](references/spriteshape-controller.md), [spriteshape-collision.md](references/spriteshape-collision.md), [spriteshape-object-placement.md](references/spriteshape-object-placement.md), [custom-geometry-scripting.md](references/custom-geometry-scripting.md).

## 1. Objective
Configure Unity's 2D Sprite Shape package correctly — right Profile (Angle Ranges/Corner Sprites/Fill) for the sprite set, right `SpriteShapeController`/spline setup for the outline, right collider generation, right object-placement-along-spline usage, custom geometry scripting only when the built-in generator genuinely falls short — without drifting into sprite authoring, 2D physics dynamics, grid/tile-based level authoring, 2D lighting setup, or gameplay rule logic that belong to sibling skills or roles.

## 2. Role
Act as the Sprite Shape authoring specialist: given a need for spline-based 2D terrain/platforms/props, you choose and configure the right `UnityEngine.U2D`-namespace components and assets — you don't decide gameplay outcomes from shape state (that's Shared Core's job), you don't author the underlying Sprite art or configure `Rigidbody2D`/`Collider2D` dynamics beyond the auto-generated collider mesh, and you don't reach into grid/tile-based authoring or 2D lighting, which are sibling skills'/roles' territory.

## 3. When to invoke this skill
- Creating or configuring a **Sprite Shape Profile** asset — Open/Closed Shape, Angle Ranges (Start/End/Order/Sprites), Corner Sprites, Fill texture (Use Sprite Borders/Texture/Offset).
- Setting up a **`SpriteShapeController`** — Detail, Open Ended, Adaptive UV, Enable Tangents, Corner Threshold, Pixels Per Unit, World Space UV.
- Editing a shape's **spline/outline** — Point Modes (Linear/Continuous Mirrored/Broken Mirrored), per-point height/corner mode/sprite variant, via the `Spline`/`SplineControlPoint` scripting API.
- Enabling **collision** on a Sprite Shape — `EdgeCollider2D`/`PolygonCollider2D` attachment, auto-updating vs. manually-edited collider mesh.
- Using **`SpriteShapeObjectPlacement`** to position a GameObject along a spline (Auto vs. Manual mode).
- Writing a **custom `SpriteShapeGeometryModifier`/`SpriteShapeGeometryCreator`** when the built-in geometry generator can't express the requirement.
- Negative trigger: authoring the underlying Sprite art (import settings, Sprite Editor slicing/outline/atlas packing) that Angle Range/Corner Sprite pools reference — that's `unity-2d-sprite`, a separate skill despite this skill consuming its output.
- Negative trigger: configuring `Rigidbody2D`, physics materials, effectors, or joints on the auto-generated `EdgeCollider2D`/`PolygonCollider2D` — that's `unity-2d-physics`.
- Negative trigger: grid/tile-based (non-spline) 2D level authoring — that's `unity-tilemap`, a different authoring model entirely.
- Negative trigger: setting up `Light2D`/2D Renderer Data or any lighting-side consumption of the tangent data Enable Tangents produces — that's `unity-urp-rendering`.
- Negative trigger: the actual gameplay decision that happens to be expressed through shape content (procedural terrain generation, a destructible-ground rule reshaping a spline) — that's `csharp-engineer`'s Shared Core, per `coding-principles.md`'s Shared Core integrity rule; this skill stops at rendering/colliding whatever outline Core already decided.

## 4. How to use this skill
1. **Confirm scope first.** This skill is the Sprite Shape spline-based authoring pipeline (`SpriteShapeController`, Profile, collider, object placement, custom geometry). If the task is authoring the Sprite art itself, hand off to `unity-2d-sprite`. If it's 2D physics dynamics beyond the auto-generated collider mesh, hand off to `unity-2d-physics`. If it's grid/tile-based level authoring, hand off to `unity-tilemap`. If it's 2D lighting, hand off to `unity-urp-rendering`.
2. **Build the Profile first**, per [spriteshape-profile.md](references/spriteshape-profile.md): pick Open vs. Closed Shape to match the outline's topology, define non-overlapping Angle Ranges covering the full angle space the outline will actually produce, assign Corner Sprites for any Angle-Threshold corner the design needs a purpose-made sprite for.
3. **Verify sprite import settings** before assigning sprites to a Profile — Texture Type Sprite (2D and UI), Sprite Mode Single, Mesh Type Full Rect, and (if atlased) Allow Rotation/Tight Packing disabled; route the actual import work to `unity-2d-sprite`.
4. **Set up the `SpriteShapeController`**, per [spriteshape-controller.md](references/spriteshape-controller.md): Detail tuned to actual visual/collision fidelity needed (not left at High by default), Enable Tangents only if the project's 2D URP lighting setup actually consumes tangent data, Corner Threshold verified against the Profile's Corner Sprites setup.
5. **Respect the Shared Core boundary.** Any gameplay decision that happens to manifest as shape content (procedural terrain outline, a destructible-ground event reshaping a spline) is decided in `Game.Core.*`; this skill's components only render/collide whatever control-point layout Core already resolved — they never decide it themselves, per `coding-principles.md`'s Shared Core integrity rule.
6. **Enable collision deliberately**, per [spriteshape-collision.md](references/spriteshape-collision.md): only `EdgeCollider2D`/`PolygonCollider2D` are supported; leave Update Collider (`autoUpdateCollider`) on while the spline is still under art iteration, and hand off the resulting collider's `Rigidbody2D`/physics-material/effector/joint configuration to `unity-2d-physics`.
7. **Use `SpriteShapeObjectPlacement` for spline-attached props**, per [spriteshape-object-placement.md](references/spriteshape-object-placement.md): `Auto` mode while still hand-placing in the Scene view, `Manual` mode once placement should be driven by `startPoint`/`endPoint`/`ratio` data.
8. **Reach for custom geometry scripting only when the built-in generator genuinely can't express the requirement** ([custom-geometry-scripting.md](references/custom-geometry-scripting.md)) — per YAGNI in `coding-principles.md`; this is Job System-adjacent scripting territory, escalate non-trivial job logic to `tech-lead-performance`/`tech-lead-csharp-unity` per `performance-and-algorithms.md`.
9. **State the hand-off explicitly.** Sprite art authoring → `unity-2d-sprite`. 2D physics dynamics beyond the auto-generated collider → `unity-2d-physics`. Grid/tile-based level authoring → `unity-tilemap`. 2D Lighting → `unity-urp-rendering`. Gameplay decisions behind shape content → `csharp-engineer`'s Shared Core.

## 5. Specific goals / tasks this skill performs
- Creating and configuring Sprite Shape Profile assets (Angle Ranges, Corner Sprites, Fill texture).
- Setting up `SpriteShapeController` instances and their Inspector properties.
- Editing spline outlines via Point Modes, per-point height/corner/sprite-variant data.
- Enabling and tuning Sprite Shape's auto-generated collider mesh.
- Positioning GameObjects along a spline via `SpriteShapeObjectPlacement`.
- Writing custom `SpriteShapeGeometryModifier`/`SpriteShapeGeometryCreator` extensions for non-standard geometry needs.
- Out of scope: Sprite import/Sprite Editor/atlas authoring (`unity-2d-sprite`); `Rigidbody2D`/physics-material/joint/effector configuration beyond the auto-generated collider mesh (`unity-2d-physics`); grid/tile-based level authoring (`unity-tilemap`); `Light2D`/2D Renderer Data lighting setup (`unity-urp-rendering`); gameplay rule logic driving shape/outline content (`csharp-engineer`'s Shared Core).

## 6. Output format
```
## Sprite Shape Work — <level/feature name>
- Scope confirmed: Sprite Shape spline-based pipeline (not Sprite authoring, not 2D physics dynamics, not grid/tile authoring, not 2D Lighting)
- Profile (if applicable): Open/Closed Shape, Angle Range count and coverage, Corner Sprites used, Fill texture settings
- SpriteShapeController settings: Detail, Open Ended, Adaptive UV, Enable Tangents, Corner Threshold, Pixels Per Unit, World Space UV, as applicable
- Spline (if applicable): Point Mode(s) used, notable per-point height/corner/sprite-index decisions
- Collision (if applicable): collider type <EdgeCollider2D/PolygonCollider2D>, autoUpdateCollider <on/off>, rationale
- Object Placement (if applicable): mode <Auto/Manual>, Start/End Point + Ratio if Manual
- Custom geometry (if applicable): why the built-in generator didn't cover the requirement, Modifier vs. Creator choice
- Shared Core boundary: confirmed no gameplay decision made in shape-layer code
- Hand-off: <sprite authoring → unity-2d-sprite / physics dynamics → unity-2d-physics / grid-tile authoring → unity-tilemap / lighting → unity-urp-rendering / gameplay logic → csharp-engineer, as applicable>
- Known limitations: <...>
```

## 7. Examples
**Example 1**
- Input: "A 2D platformer needs a winding grass platform the player can stand on, with a rounded edge sprite where the ground curves sharply."
- Output: created a Sprite Shape Profile (Closed Shape preset, since the platform has a filled interior) with one Angle Range covering the near-flat top surface and Corner Sprites assigned for the Automatic corner mode case; created a `SpriteShapeController` GameObject, Detail = Medium, Corner Threshold left at default 30°; edited the spline with Continuous Mirrored points along the smooth curve and one Linear point at a sharp platform edge; attached an `EdgeCollider2D` with `autoUpdateCollider` left on (art still iterating).
- Hand-off: the platform's `Rigidbody2D`/physics-material friction tuning → `unity-2d-physics`; the grass/edge sprite import settings and atlas packing → `unity-2d-sprite` (assumed pre-existing art).

**Example 2**
- Input: "Place a torch prop that stays glued to the edge of a winding cave-wall Sprite Shape, and should move with it if the wall is ever redesigned."
- Output: added a `SpriteShapeObjectPlacement` component to the torch prefab instance, `spriteShapeController` set to the cave wall's controller, `startPoint`/`endPoint` set to the nearest control-point pair, `ratio` = 0.5, `mode` = Auto (art still hand-placing), `setNormal` enabled so the torch orients to the wall's outline normal.
- Hand-off: if the torch's lit/unlit state should react to a gameplay trigger, that decision routes to `csharp-engineer`'s Shared Core — this skill's work only covers *where along the spline* the torch sits.

## 8. Edge cases & guardrails
- Never assume this skill covers authoring the Sprite art an Angle Range/Corner Sprite pool references — route Sprite import settings, Sprite Editor work, and atlas packing to `unity-2d-sprite`.
- Never assume `Rigidbody2D`/physics-material/effector/joint configuration is this skill's territory, even on the same GameObject as the auto-generated collider — route that to `unity-2d-physics`.
- Never assume grid/tile-cell-based level authoring is this skill's territory — that's a different authoring model covered by the sibling `unity-tilemap` skill.
- Never assume `Light2D`/2D Renderer Data lighting setup is this skill's territory — route that to `unity-urp-rendering`; this skill only exposes the Enable Tangents data feeding into it.
- Never make a gameplay decision (which outline shape a procedural generator or destructible-ground rule should produce) inside Sprite Shape-layer code — resolve the decision in Shared Core and let the spline/`SpriteShapeController` only carry out whatever control-point layout Core already decided.
- Only `EdgeCollider2D`/`PolygonCollider2D` integrate with Sprite Shape's collider mesh generation — other `Collider2D` types silently don't get auto-updated geometry.
- Disabling `autoUpdateCollider` before a manual collider edit is required — otherwise the next spline change or bake silently overwrites the manual edit.
- Angle Ranges must not overlap — an overlap makes sprite selection ambiguous at the boundary angle; verify full angle-space coverage against the actual outline shapes the design will produce.
- Don't reach for a custom `SpriteShapeGeometryModifier`/`SpriteShapeGeometryCreator` when the standard Profile-driven generation (Angle Ranges/Corner Sprites/Fill) already expresses the requirement — see YAGNI in `coding-principles.md`; these are Job System-adjacent APIs (`NativeArray`/`NativeSlice`/`JobHandle`), non-trivial job logic is `tech-lead-performance`/`tech-lead-csharp-unity` escalation territory per `performance-and-algorithms.md`.
- Several guessed Scripting API URLs 404'd at authoring time and are not covered by confirmed page content: `UnityEngine.U2D.SpriteShapeRenderer`, `SpriteShapeSegment`, `SpriteShapeParameters`, `AngleRangeInfo`, and the `UnityEditor.U2D` namespace root — see the disclosed-gap table in [root-links.md](references/root-links.md). Verify any signature involving these types against the live Scripting API or package source before implementing against them.
- The exact Sprite Shape Profile Inspector UI for assigning Corner Sprites wasn't spelled out in the fetched Manual page (only the Scripting API confirms the `CornerSprite`/`CornerType` data model) — verify the live Editor's control layout before writing precise step-by-step UI instructions for it.

# Utility Components — Followers, SkeletonUtility, Root Motion, Separation & Effects

Source: [spine-unity Utility Components](https://esotericsoftware.com/spine-unity-utility-components).
Covers: SKILL.md §4 — **"Prefer a follower or utility component over per-frame bone-copying code"**, **"Use render separation whenever another GameObject must draw between skeleton parts"**, **"Use `SkeletonRenderTexture` for a full-skeleton alpha fade, never a per-slot alpha reduction"**.

Every component here exists so a task does not need hand-written per-frame
bone copying. The selection question is almost always the same: does this need
one isolated transform, or a full mirrored hierarchy? Bone access in code is
[skeleton-api.md](skeleton-api.md); the material side of the rendering
utilities is [rendering.md](rendering.md).

## Contents

- [Followers — isolated tracking](#followers--isolated-tracking)
- [SkeletonUtility — mirrored hierarchies](#skeletonutility--mirrored-hierarchies)
- [Root motion](#root-motion)
- [Material and rendering utilities](#material-and-rendering-utilities)
- [Effect components](#effect-components)

## Followers — isolated tracking

| Component | Effect | Use when | Source |
|---|---|---|---|
| `BoneFollower` | Matches its own transform to a named bone every update, as a fully isolated GameObject | A particle system, prop, or object should visually track one bone | [Utility Components](https://esotericsoftware.com/spine-unity-utility-components) |
| `BoneFollowerGraphic` | The `SkeletonGraphic` (UI) variant of the above | The same need inside a Canvas | [Utility Components](https://esotericsoftware.com/spine-unity-utility-components) |
| `PointFollower` | Tracks a `PointAttachment` instead of a bone; also isolated | The anchor is a point attachment, not a bone | [Utility Components](https://esotericsoftware.com/spine-unity-utility-components) |
| `BoundingBoxFollower` | Extracts a `BoundingBoxAttachment` into a `PolygonCollider2D`, enabling and disabling it per animation frame | A collider must match the current frame's bounding box | [Utility Components](https://esotericsoftware.com/spine-unity-utility-components) |

**Critical caveat**: `BoundingBoxFollower` does **not** follow the bone's
position on its own — pair it with a `BoneFollower` — and does **not** follow
vertex-deformation animation, only the undeformed shape. Keep deformation on
bounding-box attachments minimal. Simulating physics on the resulting collider
is `unity-2d-physics`, not this skill.

## SkeletonUtility — mirrored hierarchies

| Element | Effect | Use when | Source |
|---|---|---|---|
| `SkeletonUtilityBone` Follow mode | The GameObject mirrors the bone, read-only | Reading bone state through the transform hierarchy | [Utility Components](https://esotericsoftware.com/spine-unity-utility-components) |
| `SkeletonUtilityBone` Override mode | The GameObject drives the bone, applied before the world-transform update | Physics or manual control should win over the animation | [Utility Components](https://esotericsoftware.com/spine-unity-utility-components) |
| `SkeletonUtility` "Spawn Hierarchy" | Generates the mirrored hierarchy; modes are Follow all, Follow (Root Only), Override all, Override (Root Only) | A full mirror is genuinely needed — added from the renderer's Advanced section | [Utility Components](https://esotericsoftware.com/spine-unity-utility-components) |
| `SkeletonUtilityConstraint` | Base class for custom constraints; a subclass auto-registers with the parent `SkeletonUtility`. Shipped examples: `SkeletonUtilityGroundConstraint`, `SkeletonUtilityEyeConstraint` | A custom constraint must run in step with the skeleton update | [Utility Components](https://esotericsoftware.com/spine-unity-utility-components) |

**Critical caveat**: `SkeletonUtilityBone` uses **local** transform values and
requires a GameObject hierarchy mirroring the skeleton's actual bone
hierarchy. Deleting an intermediate GameObject breaks everything below it.

| Hinge chain | Generates | Source |
|---|---|---|
| 3D — "Create 3D Hinge Chain" on the first element | A `HingeChain` parent at the scene root with per-element `HingeJoint`s; per-element drag and mass are adjustable, and the rig auto-rotates 180° on skeleton flip | [Utility Components](https://esotericsoftware.com/spine-unity-utility-components) |
| 2D — "Create 2D Hinge Chain" | A `HingeChain` parent with "Hinge Chain" and "Hinge Chain FlippedX" children that auto-toggle on flip | [Utility Components](https://esotericsoftware.com/spine-unity-utility-components) |

**Critical caveat**: never reparent a hinge-chain root under the skeleton's
own bones. It disconnects the chain from skeleton-driven momentum and the rig
stops behaving physically, without any error.

## Root motion

| Component | Pairs with | Notable properties | Source |
|---|---|---|---|
| `SkeletonRootMotion` | `SkeletonAnimation`/`SkeletonGraphic` | `Root Motion Bone`, per-axis `X`/`Y`, `Root Motion Scale (X)`/`(Y)`, `Animation Tracks`; optional `Rigidbody`/`Rigidbody2D` to move via physics; `AdjustRootMotionToDistance(targetDelta, trackIndex)` | [Utility Components](https://esotericsoftware.com/spine-unity-utility-components) |
| `SkeletonMecanimRootMotion` | `SkeletonMecanim` — auto-added when the `Animator`'s "Apply Root Motion" is enabled | Same shape, but `Mecanim Layers` instead of `Animation Tracks` | [Utility Components](https://esotericsoftware.com/spine-unity-utility-components) |

**Critical caveat**: the two are not interchangeable — each is tied to its own
animation driver. Attaching the wrong one produces no root motion rather than
an error.

## Material and rendering utilities

| Component | Effect | Source |
|---|---|---|
| `SkeletonRendererCustomMaterials` | Per-instance and per-slot overrides for `SkeletonRenderer`; arrays `Custom Slot Materials` and `Custom Material Overrides`; code access via `CustomMaterialOverride`/`CustomSlotMaterials` | [Utility Components](https://esotericsoftware.com/spine-unity-utility-components) |
| `SkeletonGraphicCustomMaterials` | The UI equivalent; arrays `Custom Texture Overrides`, `Custom Material Overrides` (per original texture), and `Custom Slot Materials` in 4.3+ | [Utility Components](https://esotericsoftware.com/spine-unity-utility-components) |
| `SkeletonRenderSeparator` | Splits a `SkeletonRenderer` into two or more `SkeletonPartsRenderer`s with independent sorting, so another GameObject can draw between parts | [Utility Components](https://esotericsoftware.com/spine-unity-utility-components) |

| Separation setup step | Action | Source |
|---|---|---|
| 1 | Identify the separator slots in the skeleton's draw order | [Utility Components](https://esotericsoftware.com/spine-unity-utility-components) |
| 2 | Right-click `SkeletonRenderer` → "Add Skeleton Render Separator", then assign `Separator Slot Names` | [Utility Components](https://esotericsoftware.com/spine-unity-utility-components) |
| 3 | Click "Add the missing renderers (n)", then set `Sorting Layer`/`Order in Layer` per renderer | [Utility Components](https://esotericsoftware.com/spine-unity-utility-components) |
| Note | The generated `SkeletonPartsRenderer`s need not be children of the Spine GameObject | [Utility Components](https://esotericsoftware.com/spine-unity-utility-components) |

```csharp
this.skeletonRenderSeparator.enabled = true;   // Disables the original renderer's own rendering.
this.skeletonRenderSeparator.enabled = false;  // Re-enables it automatically.

SkeletonRenderSeparator.AddToSkeletonRenderer(this.skeletonAnimation);
```

`SkeletonGraphic` needs no separator component — it has a built-in
`Advanced → Enable Separation` toggle instead.

## Effect components

| Component | Effect | Use when | Source |
|---|---|---|---|
| `SkeletonRenderTexture` / `SkeletonGraphicRenderTexture` | Renders the skeleton to a `RenderTexture` rather than straight to the frame buffer | An effect needs the composited skeleton as a single image — **expensive**, keep disabled otherwise | [Utility Components](https://esotericsoftware.com/spine-unity-utility-components) |
| `SkeletonRenderTextureFadeout` | Renders at full opacity to that texture, then draws it at the target opacity | Fading without the overlapping-attachment show-through; requires the render-texture component | [Utility Components](https://esotericsoftware.com/spine-unity-utility-components) |
| `SkeletonGhost` | Draws the skeleton repeatedly with a customizable material (speed, power) | A motion-trail or motion-blur effect | [Utility Components](https://esotericsoftware.com/spine-unity-utility-components) |
| `SkeletonRagdoll` / `SkeletonRagdoll2D` | Converts an animated skeleton into a physics-driven ragdoll via a guided rig setup | A death or knockdown simulation | [Utility Components](https://esotericsoftware.com/spine-unity-utility-components) |
| `SkeletonUtilityKinematicShadow` | Applies inertia to bones or propagates movement between them; chains can inherit velocity from a parent transform or an unrelated rigidbody | A cape or similar should follow character movement convincingly | [Utility Components](https://esotericsoftware.com/spine-unity-utility-components) |
| `RenderExistingMesh` / `RenderExistingMeshGraphic` | Re-renders an already-generated mesh elsewhere without re-animating it | Many identical copies of one animated skeleton, or an outline-only second pass | [Utility Components](https://esotericsoftware.com/spine-unity-utility-components) |
| `RenderCombinedMesh` | Combines submeshes into one mesh before rendering | A multi-material skeleton needs an outline without inner seams between submeshes | [Utility Components](https://esotericsoftware.com/spine-unity-utility-components) |

**Critical caveat**: lowering a skeleton's alpha directly is never the fade
technique — overlapping attachments show through each other at any opacity
below full. The render-texture path exists specifically for this.

## Example scenes

| Scene | Demonstrates | Source |
|---|---|---|
| `Spine Examples/Getting Started/4 Object Oriented Sample` | `BoneFollower` | [Utility Components](https://esotericsoftware.com/spine-unity-utility-components) |
| `Spine Examples/Getting Started/6 Skeleton Graphic` | `BoneFollowerGraphic` | [Utility Components](https://esotericsoftware.com/spine-unity-utility-components) |
| `Spine Examples/Other Examples/SkeletonUtility Animated Physics` | `SkeletonUtilityBone`, `SkeletonUtilityKinematicShadow` | [Utility Components](https://esotericsoftware.com/spine-unity-utility-components) |
| `Spine Examples/Other Examples/SkeletonUtility GroundConstraint & Eyes` | `SkeletonUtilityConstraint` | [Utility Components](https://esotericsoftware.com/spine-unity-utility-components) |
| `Spine Examples/Other Examples/SkeletonUtility Ragdoll` | `SkeletonRagdoll2D` | [Utility Components](https://esotericsoftware.com/spine-unity-utility-components) |
| `Spine Examples/Other Examples/SkeletonRenderSeparator` | `SkeletonRenderSeparator` | [Utility Components](https://esotericsoftware.com/spine-unity-utility-components) |

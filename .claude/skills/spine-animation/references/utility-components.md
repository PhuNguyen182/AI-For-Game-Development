# Utility Components

Page: utility-components. Question for most tasks: one isolated transform, or a full mirrored hierarchy?

## Followers (isolated GameObjects)
| Component | Tracks |
|---|---|
| `BoneFollower` | a named bone, every update |
| `BoneFollowerGraphic` | same, for `SkeletonGraphic` |
| `PointFollower` | a `PointAttachment` |
| `BoundingBoxFollower` | a `BoundingBoxAttachment` → `PolygonCollider2D`, enabled/disabled per frame |

`BoundingBoxFollower` does not follow bone position (pair with a `BoneFollower`) nor vertex deformation, only the undeformed shape — keep deformation on bounding boxes minimal.

## SkeletonUtility (mirrored hierarchy)
- Added from the renderer's Advanced section; "Spawn Hierarchy" modes: Follow all, Follow (Root Only), Override all, Override (Root Only).
- `SkeletonUtilityBone`: Follow = GameObject mirrors the bone (read-only); Override = GameObject drives the bone before the world-transform update (physics/manual wins over animation).
- It uses **local** transforms and needs a hierarchy mirroring the real bone hierarchy; deleting an intermediate GameObject breaks everything below it.
- `SkeletonUtilityConstraint`: base for custom constraints (subclasses auto-register); shipped: `SkeletonUtilityGroundConstraint`, `SkeletonUtilityEyeConstraint`.
- Hinge chains: "Create 3D Hinge Chain" on the first element makes a `HingeChain` at scene root with `HingeJoint`s (per-element drag/mass; auto-rotates 180° on flip). "Create 2D Hinge Chain" makes `HingeChain` with "Hinge Chain" and "Hinge Chain FlippedX" children that toggle on flip. Never reparent the root under the skeleton's bones: it loses skeleton-driven momentum, no error.
- `SkeletonUtilityKinematicShadow`: inertia for bones/capes; chains can inherit velocity from a parent transform or unrelated rigidbody.
- `SkeletonRagdoll` / `SkeletonRagdoll2D`: guided rig setup for a physics ragdoll.

## Root motion
| Component | Pairs with | Notes |
|---|---|---|
| `SkeletonRootMotion` | `SkeletonAnimation`/`SkeletonGraphic` | `Root Motion Bone`, per-axis `X`/`Y`, `Root Motion Scale (X)/(Y)`, `Animation Tracks`; optional `Rigidbody`/`Rigidbody2D`; `AdjustRootMotionToDistance(targetDelta, trackIndex)` |
| `SkeletonMecanimRootMotion` | `SkeletonMecanim` (auto-added when Animator "Apply Root Motion" is on) | same, with `Mecanim Layers` |

The wrong one gives no root motion and no error.

## Custom materials and separation
- `SkeletonRendererCustomMaterials`: per-instance/per-slot overrides (`Custom Slot Materials`, `Custom Material Overrides`; code: `CustomMaterialOverride`/`CustomSlotMaterials`). `SkeletonGraphicCustomMaterials`: `Custom Texture Overrides`, `Custom Material Overrides`, and (4.3+) `Custom Slot Materials`.
- `SkeletonRenderSeparator` splits a `SkeletonRenderer` into `SkeletonPartsRenderer`s with independent sorting:
  1. Find the separator slots in draw order.
  2. Right-click `SkeletonRenderer` → "Add Skeleton Render Separator"; set `Separator Slot Names`.
  3. "Add the missing renderers (n)"; set `Sorting Layer`/`Order in Layer` per renderer (they need not be children).
- `SkeletonGraphic` instead has `Advanced → Enable Separation`.

```csharp
separator.enabled = true;    // disables the original renderer's own rendering
separator.enabled = false;   // re-enables it
SkeletonRenderSeparator.AddToSkeletonRenderer(skeletonAnimation);
```

## Effects
| Component | Use |
|---|---|
| `SkeletonRenderTexture` / `SkeletonGraphicRenderTexture` | Composited skeleton as one image; expensive, keep disabled otherwise |
| `SkeletonRenderTextureFadeout` | Fade without overlap show-through (renders at full opacity, draws at target); requires the render-texture component |
| `SkeletonGhost` | Motion trail (customisable material, speed, power) |
| `RenderExistingMesh` / `RenderExistingMeshGraphic` | Re-render a generated mesh elsewhere: many identical copies, or an outline-only second pass |
| `RenderCombinedMesh` | Combine submeshes before rendering: outline without inner seams |

Lowering skeleton alpha directly is never the fade technique: overlapping attachments show through below full opacity.

Example scenes (`Spine Examples/...`): `Getting Started/4 Object Oriented Sample` (`BoneFollower`), `Getting Started/6 Skeleton Graphic` (`BoneFollowerGraphic`), `Other Examples/SkeletonUtility Animated Physics`, `.../SkeletonUtility GroundConstraint & Eyes`, `.../SkeletonUtility Ragdoll`, `.../SkeletonRenderSeparator`.

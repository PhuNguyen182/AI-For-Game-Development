# Utility Components — Followers, SkeletonUtility, Root Motion, Render Separation & Effects

Source: [spine-unity-utility-components](https://esotericsoftware.com/spine-unity-utility-components).

## Root motion

### SkeletonRootMotion
Drives a `SkeletonAnimation`/`SkeletonGraphic`'s position from a bone's movement (like Mecanim's "Apply Root Motion"). Properties: `Root Motion Bone`, per-axis `X`/`Y` toggles, `Root Motion Scale (X)`/`(Y)` (delta compensation), `Animation Tracks` (which tracks contribute). Optional `Rigidbody2D`/`Rigidbody` to move via physics instead of `Transform`. Method: `AdjustRootMotionToDistance(targetDelta, trackIndex)` for dynamic distance compensation.

**Incompatible with `SkeletonMecanim`** — use `SkeletonMecanimRootMotion` there instead.

### SkeletonMecanimRootMotion
The `SkeletonMecanim` equivalent; auto-added when the `Animator`'s "Apply Root Motion" is enabled. Same shape of properties (`Root Motion Bone`, `X`/`Y`, `Root Motion Scale`), but `Mecanim Layers` instead of `Animation Tracks`. Same `AdjustRootMotionToDistance(...)` method and optional `Rigidbody`/`Rigidbody2D` support.

## Followers

### BoneFollower / BoneFollowerGraphic
Sets its own GameObject's transform to match a named bone of a `SkeletonRenderer`/`SkeletonGraphic`, every update. Works as a fully isolated GameObject — no need to build a parent bone hierarchy. Use for a particle system, prop, or any object that should visually track one bone. `BoneFollowerGraphic` is the UI (`SkeletonGraphic`) variant.

### PointFollower
Same idea as `BoneFollower`, but tracks a `PointAttachment` instead of a bone. Also isolated — no parent hierarchy required.

### BoundingBoxFollower
Extracts a `BoundingBoxAttachment`'s current shape into a `PolygonCollider2D`, enabling/disabling it each frame to match the active animation frame. **Does not** follow the bone's position on its own (pair it with a `BoneFollower`) and **does not** follow vertex-deformation animation on the bounding box (only the initial/undeformed shape). The Inspector has an "Add Bone Follower" convenience button.

## SkeletonUtility / SkeletonUtilityBone

### SkeletonUtilityBone
Lets a GameObject either follow a bone's position or override it via manual control/physics.

- **Follow mode** — the GameObject mirrors the bone (read-only).
- **Override mode** — the GameObject drives the bone's position, applied before the skeleton's world-transform update.

Uses **local transform values** and requires a GameObject hierarchy that mirrors the skeleton's actual bone hierarchy — deleting a middle GameObject in that hierarchy breaks the chain below it. The Inspector can create child bones (selectively or recursively) and generate 2D/3D hinge chains for physics. Hierarchy icons differ: a bone icon marks Follow mode, a pose-bones icon marks Override mode.

### SkeletonUtility
Quick way to spawn a `SkeletonUtilityBone` hierarchy mirroring the skeleton's bones. Add via the `SkeletonRenderer`/`SkeletonGraphic` Inspector's Advanced section ("Add Skeleton Utility"), then "Spawn Hierarchy" with a mode: Follow all bones, Follow (Root Only), Override all bones, Override (Root Only). More bones can be added afterward via the `SkeletonUtilityBone` inspector; unwanted ones can be deleted while keeping the rest of the chain intact.

### 2D/3D hinge chains (physics)
Built from a `SkeletonUtilityBone` hierarchy.

- **3D**: select the first chain element → "Create 3D Hinge Chain" → generates a `HingeChain` parent at the scene root (not parented under the skeleton) with per-element `HingeJoint`s; rigidbody drag/mass are adjustable per element; the rig auto-rotates 180° when the skeleton flips.
- **2D**: select the first element → "Create 2D Hinge Chain" → generates a `HingeChain` parent with two children, "Hinge Chain" and "Hinge Chain FlippedX," which auto-activate/deactivate on skeleton flip.

**Critical caveat**: never reparent a hinge-chain root under the skeleton's own bones — doing so disconnects the chain from the skeleton's movement and breaks the physics simulation's momentum coupling.

### SkeletonUtilityConstraint
Base class for custom constraint behaviors; a subclass auto-registers itself with the parent `SkeletonUtility` and updates alongside it. Shipped examples: `SkeletonUtilityGroundConstraint`, `SkeletonUtilityEyeConstraint`.

## Material/rendering utilities

### SkeletonRendererCustomMaterials
Per-instance/per-slot material overrides for `SkeletonRenderer`. Add via right-click → "Add Basic Serialized Custom Materials." Arrays: `Custom Slot Materials` (per-slot), `Custom Material Overrides` (global substitution). Code access: `SkeletonRenderer.CustomMaterialOverride`, `SkeletonRenderer.CustomSlotMaterials`.

### SkeletonGraphicCustomMaterials
The `SkeletonGraphic` (UI) equivalent. Arrays: `Custom Texture Overrides`, `Custom Material Overrides` (per original texture), `Custom Slot Materials` (spine-unity 4.3+). Code access: `SkeletonGraphic.CustomMaterialOverride`, `SkeletonGraphic.CustomTextureOverride`.

### SkeletonRenderSeparator
Splits a `SkeletonRenderer` into two or more `SkeletonPartsRenderer`s with independent sorting/layer order, so another GameObject can render between skeleton parts (e.g. a character running behind a tree trunk with one leg in front, one behind).

**Setup**: identify the separator slot(s) in the skeleton's draw order → right-click `SkeletonRenderer` → "Add Skeleton Render Separator" → assign `Separator Slot Names` → click "Add the missing renderers (n)" → set `Sorting Layer`/`Order in Layer` per resulting renderer. The generated `SkeletonPartsRenderer`s don't need to be children of the Spine GameObject.

```csharp
skeletonRenderSeparator.enabled = true;   // enable separation
skeletonRenderSeparator.enabled = false;  // disable separation

// separatorSlots list on SkeletonRenderer — Add/Remove/Clear as needed

SkeletonRenderSeparator.AddToSkeletonRenderer(skeletonAnimation);  // add at runtime
```

Enabling separation disables the original `SkeletonRenderer`'s own rendering; disabling separation re-enables it automatically. `SkeletonGraphic` doesn't need this component — it has a built-in `Advanced → Enable Separation` toggle instead.

## Effects and misc example components

### SkeletonRagdoll / SkeletonRagdoll2D
Turns an animated skeleton into a physics-driven ragdoll (e.g. a death/knockdown simulation) via a guided interface for creating the ragdoll rig.

### SkeletonRenderTexture / SkeletonGraphicRenderTexture
Renders the skeleton to a `RenderTexture` instead of directly to the frame buffer, enabling effects like a correct full-skeleton alpha fade. **Expensive** relative to direct rendering — keep it disabled except while the effect is actually active.

### SkeletonRenderTextureFadeout
Fades a skeleton via transparency without the overlapping-attachment show-through artifact. Requires `SkeletonRenderTexture`/`SkeletonGraphicRenderTexture` already present: it renders the skeleton at full opacity to a temporary texture, then draws that texture's content at the desired fade opacity.

### SkeletonGhost
Draws the skeleton multiple times with a customizable material to produce a motion-trail/motion-blur effect (speed, power).

### SkeletonUtilityKinematicShadow
Applies inertia to bones or propagates movement from other bones — e.g. making a cape follow a character's movement convincingly. Hinge chains built this way can inherit velocity from parent-transform changes or from an unrelated rigidbody.

### RenderExistingMesh / RenderExistingMeshGraphic
Re-renders an already-generated skeleton mesh at a different location without re-animating it — a performance win for many identical copies of the same animated skeleton, and also usable to render an outline-only pass via a URP outline shader.

### RenderCombinedMesh
Combines a skeleton's submeshes into one mesh before rendering, producing correct outlines when a skeleton needs multiple materials and an outline shader is applied (a naive multi-submesh render otherwise outlines each submesh separately, showing inner seams).

## Key caveats and gotchas
- A `SkeletonUtilityBone` hierarchy must mirror the skeleton's actual bone hierarchy — removing an intermediate GameObject breaks everything parented below it.
- Never reparent a hinge-chain root onto the skeleton's own bones — it disconnects the chain from skeleton-driven momentum.
- `BoundingBoxFollower` only reflects the bounding box's initial/undeformed shape and doesn't track bone position on its own — pair with `BoneFollower` and keep deformation on bounding-box attachments minimal.
- `SkeletonRenderTexture`/`SkeletonGraphicRenderTexture` are expensive — enable only while the effect that needs them is active.
- `SkeletonRootMotion` and `SkeletonMecanimRootMotion` are mutually exclusive by which animation-driving component they pair with — never attach the wrong one.

## Example scenes referenced
- `Spine Examples/Getting Started/4 Object Oriented Sample` — `BoneFollower`.
- `Spine Examples/Getting Started/6 Skeleton Graphic` — `BoneFollowerGraphic`.
- `Spine Examples/Other Examples/SkeletonUtility Animated Physics` — `SkeletonUtilityBone`, `SkeletonUtilityKinematicShadow`.
- `Spine Examples/Other Examples/SkeletonUtility GroundConstraint & Eyes` — `SkeletonUtilityConstraint`.
- `Spine Examples/Other Examples/SkeletonUtility Ragdoll` — `SkeletonRagdoll2D`.
- `Spine Examples/Other Examples/SkeletonRenderSeparator` — `SkeletonRenderSeparator`.

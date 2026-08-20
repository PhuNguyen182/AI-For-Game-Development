---
name: spine-animation
description: >
  Technique for integrating Esoteric Software's Spine 2D skeletal animation
  runtime into Unity (`Spine.Unity.*`, package `com.esotericsoftware.spine.*`)
  — the `SkeletonRenderer`/`SkeletonAnimation`/`SkeletonGraphic`/
  `SkeletonMecanim` main components, `Spine.AnimationState`/`TrackEntry`
  track-based animation control (mixing, empty animations, events, coroutine
  yield instructions), skin/attachment/skeleton manipulation and runtime
  mix-and-match/repacking, utility components (`BoneFollower`/
  `PointFollower`/`BoundingBoxFollower`/`SkeletonUtility`/
  `SkeletonUtilityBone`/`SkeletonRootMotion`/`SkeletonRenderSeparator`/
  `SkeletonGhost`/`SkeletonRagdoll` and related), rendering (Built-in/URP/LWRP
  shader selection, PMA vs. straight alpha, material/atlas/draw-call
  management, sorting, tint black, outline shaders), the Timeline extension
  (SkeletonAnimation/SkeletonGraphic/Skeleton Flip tracks), and the
  on-demand-loading/Addressables extension for deferring skin/atlas texture
  loads. Use this for any task touching a Spine skeleton asset
  (`SkeletonDataAsset`, `.atlas.txt`, `.skel.bytes`/`.json` export), a
  `Spine.Unity` component, or `Spine.AnimationState`/`Spine.Skeleton`
  scripting. Do not use this for Unity's own Mecanim/`Animator`/
  `AnimationClip` system on a non-Spine rig — that's `unity-animation`;
  `SkeletonMecanim` (a Spine skeleton driven by Mecanim) is still in scope
  here since it's a Spine component, but authoring the Animator
  Controller/state-machine underneath it follows `unity-animation`'s
  guidance. Do not use this for Unity's native Sprite/SpriteRenderer 2D
  pipeline on art that has no Spine skeleton — that's `unity-2d-sprite`. Do
  not use this for 2D physics simulation on a `PolygonCollider2D` a
  `BoundingBoxFollower` produced — that's `unity-2d-physics`; this skill only
  covers producing/updating that collider shape. Do not use this to write a
  new non-Spine shader from scratch — that's `shader-authoring`; this skill
  only covers selecting/configuring the fixed catalog of `Spine/*` and
  `Universal Render Pipeline/*/Spine/*` shaders and their PMA/straight-alpha/
  tint-black/outline options. Do not use this for URP/HDRP pipeline setup
  itself (Renderer Features, URP Asset settings, Volumes) — that's
  `unity-urp-rendering`/`render-pipeline-urp-hdrp`; this skill only decides
  which Spine shader package matches the confirmed pipeline. Do not use this
  for generic particle-system VFX — that's `vfx-particle-authoring`;
  `SkeletonGhost`'s trail effect and `RenderExistingMesh`/`RenderCombinedMesh`
  duplication are Spine-specific mesh-rendering tricks, not particle
  authoring. Do not use this for the generic Addressables loading/
  reference-counting contract — that's `unity-addressables`; this skill only
  covers Spine's own `com.esotericsoftware.spine.addressables`/
  `on-demand-loading` extension that swaps atlas textures for placeholders at
  build time. Never call any `Spine.Unity`/`UnityEngine` API from
  `Game.Core.*` — Spine's runtime depends on `UnityEngine`, so skeleton
  control code belongs in `Game.Client.*`, receiving already-decided gameplay
  outcomes (which animation to play, which skin to equip) from Shared Core
  rather than deciding them itself.
---

# Spine Animation — Unity Runtime Integration

Sources: see [references/](references/) for the specific sub-pages this skill was built from, split by topic — [root-links.md](references/root-links.md), [main-components.md](references/main-components.md) (`SkeletonRenderer`/`SkeletonAnimation`/`SkeletonGraphic`/`SkeletonMecanim`, the `Skeleton`/`AnimationState`/`TrackEntry` scripting API, skin/attachment/repacking, runtime instantiation), [utility-components.md](references/utility-components.md) (followers, `SkeletonUtility`/`SkeletonUtilityBone`, root motion, render separation, ragdoll/ghost/render-texture helpers), [rendering.md](references/rendering.md) (render pipeline support, materials/draw calls, sorting, shader catalog, PMA vs. straight alpha, custom shader requirements), [timeline.md](references/timeline.md) (the Timeline extension's tracks/clips), [on-demand-loading.md](references/on-demand-loading.md) (the on-demand-loading/Addressables extension), [faq.md](references/faq.md) (import/visual/performance/licensing Q&A).

## 1. Objective
Wire Spine-exported skeletons into Unity correctly: the right main component for the rendering/animation surface actually needed (`SkeletonRenderer`+`SkeletonAnimation`, `SkeletonGraphic`, or `SkeletonMecanim`), animation played through `AnimationState`'s track/mix model instead of restarted every frame, skins/attachments/materials manipulated through the documented `Skeleton` API instead of ad-hoc mesh hacks, rendering configured with the shader/alpha workflow that actually matches the active render pipeline, and Timeline/on-demand-loading wired per the extension packages' real contract — never inventing a substitute technique for something the runtime already provides.

## 2. Role
Act as the 2D skeletal-animation specialist for the client track — the tool Unity Engineer / Technical Artist reach for whenever a feature involves a Spine-exported character, prop, or UI skeleton, from initial component setup through skin swapping, root motion, render separation, and Timeline-driven cinematics.

## 3. When to invoke this skill
- Setting up a newly-imported skeleton (`_SkeletonData` asset) as a scene GameObject — deciding `SkeletonAnimation` vs. `SkeletonGraphic` vs. `SkeletonMecanim` for the actual rendering surface (world-space `MeshRenderer` vs. UI `Canvas` vs. Mecanim-driven).
- Playing, queuing, or mixing animations via `Spine.AnimationState`/`TrackEntry` — `SetAnimation`/`AddAnimation`, empty-animation mixing, multi-track layering, or reacting to `Start`/`Interrupt`/`End`/`Complete`/`Dispose`/`Event` callbacks.
- Changing a skeleton's skin or attachment at runtime — `Skeleton.SetSkin`/`SetAttachment`, mix-and-match skin composition, or runtime atlas repacking via `AtlasUtilities`.
- Reading or driving bone transforms — `Skeleton.FindBone`, `Bone.GetWorldPosition`/`SetPositionSkeletonSpace`, or subscribing to `UpdateWorld`/`UpdateComplete`/`UpdateLocal`/`BeforeApply` for correctly-timed manipulation.
- Attaching a GameObject/particle system to a bone or point (`BoneFollower`/`BoneFollowerGraphic`/`PointFollower`), extracting a physics collision shape (`BoundingBoxFollower`), or spawning a bone-mirroring hierarchy for physics/constraints (`SkeletonUtility`/`SkeletonUtilityBone`, 2D/3D hinge chains).
- Adding root motion (`SkeletonRootMotion` for `SkeletonAnimation`/`SkeletonGraphic`, `SkeletonMecanimRootMotion` for `SkeletonMecanim` — never mix the two).
- Splitting a skeleton's draw order across layers so another GameObject can render between skeleton parts (`SkeletonRenderSeparator`/`SkeletonPartsRenderer`, or `SkeletonGraphic`'s built-in `Enable Separation`).
- Configuring rendering: choosing Built-in vs. URP vs. LWRP Spine shaders, PMA vs. straight-alpha import/material setup, tint black, outline shaders, sorting/z-spacing, or per-instance material/texture overrides (`SkeletonRendererCustomMaterials`/`SkeletonGraphicCustomMaterials`, `CustomMaterialOverride`/`CustomSlotMaterials`).
- Fading a skeleton in/out without the overlapping-attachment transparency artifact (`SkeletonRenderTexture`/`SkeletonRenderTextureFadeout`/`SkeletonGraphicRenderTexture`), or adding a motion-trail effect (`SkeletonGhost`).
- Animating a Spine skeleton in Unity Timeline — SkeletonAnimation Track / SkeletonGraphic Track / Skeleton Flip Track, clip mixing/blend-in parameters, track ordering for base vs. overlay tracks.
- Reducing memory/download size by deferring atlas texture loads — the `com.esotericsoftware.spine.on-demand-loading`/`com.esotericsoftware.spine.addressables` extension packages, a `SpineAtlasAsset`'s Addressables Loader, or a custom `GenericOnDemandTextureLoader`/`OnDemandTextureLoader` subclass.
- Diagnosing a Spine-specific visual/import/performance symptom (dark borders, washed-out colors, colorful stripes, wrong outline rendering, excessive draw calls, GC spikes on instantiate) — check [faq.md](references/faq.md) before treating it as a generic Unity rendering/performance bug.
- Negative trigger: Mecanim Animator Controller/state-machine/Blend Tree authoring on a non-Spine rig, or Playables API work unrelated to Spine — that's `unity-animation`.
- Negative trigger: native `SpriteRenderer`/`Sprite` pipeline work on art with no Spine skeleton — that's `unity-2d-sprite`.
- Negative trigger: simulating physics on a `PolygonCollider2D`/`Rigidbody2D` once `BoundingBoxFollower` has produced it — that's `unity-2d-physics`.
- Negative trigger: authoring a new non-Spine shader from scratch, or general HLSL/Shader Graph technique — that's `shader-authoring`; this skill only selects/configures the existing `Spine/*` catalog.
- Negative trigger: URP/HDRP pipeline-level configuration (Renderer Features, URP Asset, Volumes) — that's `unity-urp-rendering`/`render-pipeline-urp-hdrp`.
- Negative trigger: generic particle VFX authoring — that's `vfx-particle-authoring`.
- Negative trigger: the general Addressables loading/reference-counting contract for non-Spine assets — that's `unity-addressables`; this skill only covers Spine's own on-demand-loading extension.
- Negative trigger: any `Game.Core.*` code — Spine's runtime depends on `UnityEngine`; Shared Core only ever receives an already-decided outcome (which animation/skin to apply) from `Game.Client.*`.

## 4. How to use this skill
1. **Pick the right main component up front, per [main-components.md](references/main-components.md).** `SkeletonRenderer` alone only for manual/no-transition posing (rare — e.g. a UI gauge); pair it with `SkeletonAnimation` for Spine's own track-based `AnimationState` control (the default choice, highest customizability); use `SkeletonGraphic` instead of `SkeletonRenderer`+`SkeletonAnimation` when the skeleton renders inside a UI `Canvas` (it uses `CanvasRenderer`, not `MeshRenderer`); use `SkeletonMecanim` only when the project specifically wants Mecanim's Animator Controller/state-machine/Blend Tree authoring driving the skeleton, and budget for its documented limitations (setup-pose keys required on second animations, no per-track mix thresholds, no real threaded-animation gain).
2. **Never call `AnimationState.SetAnimation` every frame.** It restarts the animation from frame 1 each call, freezing the visible pose. Track current animation state and call `SetAnimation`/`AddAnimation` only on an actual change; use `TrackEntry.trackTime` to hold on a specific frame instead.
3. **Respect the update life-cycle when reading/writing bone or skeleton state.** `SkeletonAnimation`/`SkeletonMecanim` update local values then world transforms every `Update`/`LateUpdate`; get or set bone positions from the `UpdateWorld`/`UpdateComplete`/`BeforeApply` delegates (or via `[DefaultExecutionOrder]` relative to the Spine component) rather than an arbitrary `Update()`, or the change will be one frame late or silently overwritten. After changing a skin, always call `Skeleton.SetupPoseSlots()` before the next `AnimationState.Apply()`/`SkeletonMecanim.Update()` so stale attachment visibility doesn't leak through.
4. **Use the `[SpineBone]`/`[SpineSlot]`/`[SpineAttachment]`/`[SpineSkin]`/`[SpineAnimation]`/`[SpineEvent]`/`[SpineIkConstraint]`/`[SpineTransformConstraint]`/`[SpinePathConstraint]` attributes on any public string field referencing skeleton data**, instead of a bare string field — they give an Inspector dropdown populated from the actual `SkeletonDataAsset`, catching a typo'd name at edit time instead of a silent runtime no-op.
5. **Prefer a follower/utility component over manual per-frame bone-copying code**, per [utility-components.md](references/utility-components.md). `BoneFollower`/`PointFollower`/`BoneFollowerGraphic` for an isolated GameObject that needs one bone/point's transform without a full mirrored hierarchy; `SkeletonUtility`+`SkeletonUtilityBone` only when a full bone-hierarchy mirror is actually needed (physics rigs, hinge chains); `BoundingBoxFollower` for a `PolygonCollider2D` synced to the current frame's bounding-box attachment (it does not follow bone position or vertex deformation on its own — pair with `BoneFollower` and keep bounding-box deformation minimal).
6. **Match the render workflow to the render pipeline once, per [rendering.md](references/rendering.md) — don't mix.** Built-in Spine shaders (`Spine/Skeleton`, `Spine/Skeleton Graphic`, `Spine/Skeleton Tint Black`, etc.) for the Built-in Render Pipeline; the separate URP/LWRP Spine shader extension packages for those pipelines (never a URP shader with `SkeletonGraphic`, never a Built-in `Spine/Skeleton` shader under URP). Only `Spine/SkeletonGraphic*`-family shaders (or their UI-safe URP/LWRP equivalents, where offered) on `SkeletonGraphic` — a non-`CanvasRenderer`-compatible shader can look correct in the Editor and still break silently on-device. Confirm PMA vs. straight-alpha matches both the texture's actual export/import settings and the project's Color Space (Linear supports straight alpha only) before debugging a color artifact as something else — check [faq.md](references/faq.md)'s Visual section first.
7. **Never assign a skeleton's Materials array directly, or expect a `MeshRenderer.material` edit to stick.** `SkeletonRenderer`/`SkeletonGraphic` rebuild the Materials array every `LateUpdate()` from the current attachments/atlas/blend-mode state; use `SkeletonRendererCustomMaterials`/`SkeletonGraphicCustomMaterials` (or `CustomMaterialOverride`/`CustomSlotMaterials` in code) for per-instance overrides, and use `Skeleton.R`/`G`/`B`/`A` (with PMA vertex colors enabled) for tinting that preserves batching instead of swapping to a per-instance material.
8. **Use `SkeletonRenderSeparator`/`SkeletonPartsRenderer` (or `SkeletonGraphic`'s built-in `Enable Separation`) whenever another GameObject needs to render between skeleton parts** — don't try to fake this with sorting-order tweaks on a single renderer, since one skeleton's draw order is otherwise atomic.
9. **Use `SkeletonRenderTexture`/`SkeletonRenderTextureFadeout` for a full-skeleton alpha fade**, not a naive per-slot/per-vertex alpha reduction — overlapping attachments show through each other at anything less than full opacity under normal alpha blending. Keep the RenderTexture component disabled except while the fade effect is actually needed; it's an expensive intermediate render pass.
10. **When authoring on Timeline** (per [timeline.md](references/timeline.md)), keep the base animation track at the top and any overlay tracks below it, assign each track's `Track Index` deliberately for multi-track mixing, and verify actual mixing behavior in Play Mode — Edit-mode preview mixing in the Timeline window can visually differ from runtime playback. `SkeletonMecanim` has no Timeline track support; don't attempt to target it with these tracks.
11. **Only reach for on-demand loading** (per [on-demand-loading.md](references/on-demand-loading.md)) **once a measured build-size/memory problem justifies it** — install the Addressables extension package (which depends on the On-Demand Loading package), mark the relevant textures Addressable, then add the loader via the `SpineAtlasAsset`'s "Add Addressables Loader" — no custom loading code needed for the standard case. Low-resolution placeholders only apply in actual builds, not the Editor; use the `AddressableTextureLoader`'s "Testing → Assign Placeholders" menu to preview, and never manually assign placeholders as a substitute for a real build.
12. **Diagnose a Spine-specific symptom against [faq.md](references/faq.md) before assuming a generic Unity cause** — dark borders/washed colors/colorful stripes are almost always a PMA-vs-straight-alpha/Color-Space mismatch, not a shader bug; excessive draw calls are almost always multiple atlas pages or alternating slot blend modes, fixable via repacking or draw-order-aware atlas packing, not something to brute-force with LOD/culling tricks meant for other renderers.
13. **Prefer the binary `.skel.bytes` export over `.json` for shipped content**, and pool skeleton instances (pre-warmed, `AnimationState.ClearTracks()` + disable instead of `Destroy()`) per [faq.md](references/faq.md)'s Performance guidance — this is the Spine-specific instance of `performance-and-algorithms.md`'s general pooling requirement, not a separate rule.

## 5. Specific goals / tasks this skill performs
- Setting up a new skeleton in-scene with the correct main component (`SkeletonAnimation` / `SkeletonGraphic` / `SkeletonMecanim`) for its rendering surface.
- Playing/queuing/mixing animations through `AnimationState`/`TrackEntry`, including event callbacks and coroutine yield instructions (`WaitForSpineAnimationComplete`/`End`/`WaitForSpineEvent`).
- Runtime skin/attachment changes, mix-and-match skin composition, and atlas repacking via `AtlasUtilities`.
- Wiring follower/utility components (`BoneFollower`, `PointFollower`, `BoundingBoxFollower`, `SkeletonUtility`/`SkeletonUtilityBone`, hinge-chain physics rigs) and root motion (`SkeletonRootMotion`/`SkeletonMecanimRootMotion`).
- Configuring render separation, custom materials, tint black, outline shaders, and PMA/straight-alpha correctness for the confirmed render pipeline.
- Building a fade-in/out or motion-trail effect via `SkeletonRenderTexture`/`SkeletonRenderTextureFadeout`/`SkeletonGhost`.
- Authoring Spine Timeline tracks/clips (SkeletonAnimation Track, SkeletonGraphic Track, Skeleton Flip Track).
- Wiring the on-demand-loading/Addressables texture extension for large skin/atlas variant sets.
- Diagnosing Spine-specific import/visual/performance symptoms against faq.md before treating them as generic Unity issues.
- Out of scope: non-Spine Mecanim/Animator authoring (`unity-animation`), native Sprite pipeline (`unity-2d-sprite`), 2D physics simulation itself (`unity-2d-physics`), new shader authoring (`shader-authoring`), URP/HDRP pipeline configuration (`unity-urp-rendering`/`render-pipeline-urp-hdrp`), generic particle VFX (`vfx-particle-authoring`), the general Addressables contract (`unity-addressables`), any `Game.Core.*` usage.

## 6. Output format
```
## Spine Animation Work — <skeleton/feature name>
- Main component: SkeletonRenderer+SkeletonAnimation / SkeletonGraphic / SkeletonMecanim — rationale
- Animation control: AnimationState track(s)/mix plan — track index(es), empty-animation transitions, events wired
- Skin/attachment handling: <static / SetSkin swap / mix-and-match / runtime repack> — SetupPoseSlots confirmed after each skin change
- Bone/utility wiring: <BoneFollower / PointFollower / BoundingBoxFollower / SkeletonUtility hierarchy / none> — update-timing hook used (UpdateWorld/UpdateComplete/BeforeApply) if bone state is read or written manually
- Root motion: <SkeletonRootMotion / SkeletonMecanimRootMotion / none>
- Rendering: shader family (Built-in/URP/LWRP Spine shader) — PMA or straight alpha, tint black yes/no, outline yes/no, render separation yes/no
- Timeline: <tracks used, track ordering — or "not applicable">
- On-demand loading: <Addressables texture loader configured — or "not applicable">
- Layer: Game.Client.* (never Game.Core.*) — Shared Core only ever supplies the decided animation/skin outcome
- Known limitations: <...>
```

## 7. Examples
**Example 1**
- Input: a new player character skeleton needs to play a locomotion loop with a smooth crossfade into an attack animation, then return to locomotion.
- Output: `SkeletonRenderer`+`SkeletonAnimation` on a world-space GameObject; `AnimationState.SetAnimation(0, "locomotion", true)` called once on state entry (not every frame); attack triggered via `AnimationState.SetAnimation(0, "attack", false)` on the actual input edge, with the configured `SkeletonDataAsset` mix duration handling the crossfade; subscribed to `TrackEntry.Complete` on the attack entry to call `SetAnimation(0, "locomotion", true)` back, deferred one frame via a coroutine to avoid the same-frame Start/End ordering issue.

**Example 2**
- Input: an equipment system needs to swap a character's weapon/armor skins at runtime based on inventory state.
- Output: built the target loadout as a `Skin` via `AddSkin(...)` calls from `SkeletonData.FindSkin(...)` per equipped piece, called `skeleton.SetSkin(mixAndMatchSkin)` then `skeleton.SetupPoseSlots()`, then `skeletonAnimation.AnimationState.Apply(skeleton)` to force-refresh the current pose against the new skin immediately instead of waiting a frame.

**Example 3**
- Input: "just tint the boss skeleton red for a hit-flash by swapping in a red-tinted material instance."
- Output: declined — swapping materials breaks batching with other instances and gets overwritten on the next `LateUpdate()` anyway since `SkeletonRenderer` rebuilds the Materials array every frame; used `Skeleton.R`/`G`/`B` with `Advanced → PMA Vertex Colors` enabled instead, which tints without breaking batching or fighting the automatic material rebuild.

**Example 4**
- Input: a UI equipment-preview panel needs to show the same skeleton the world uses, inside a `Canvas`.
- Output: used `SkeletonGraphic`, not `SkeletonRenderer`+`SkeletonAnimation` reused as-is, since the panel needs `CanvasRenderer`/`RectMask2D` compatibility; assigned a `Spine/SkeletonGraphic*` material (confirmed via the `Detect Material` button) instead of reusing the world skeleton's `Spine/Skeleton` material, which would have rendered incorrectly under `CanvasRenderer`; ran `Match RectTransform with Mesh` to set correct `RectMask2D` bounds.

**Example 5**
- Input: a scene has 40 crowd-filler skeletons all playing the same idle animation, causing a noticeable CPU/GC cost.
- Output: flagged per faq.md's Performance guidance — switched export to `.skel.bytes`, pre-warmed and pooled the instances instead of Instantiate/Destroy per spawn, and evaluated `RenderExistingMesh` for skeletons that are visually identical copies at different positions instead of running 40 independent animated instances.

## 8. Edge cases & guardrails
- Never call `AnimationState.SetAnimation` every frame — it restarts the animation from frame 1, freezing the visible pose; call it only on an actual animation change and use `TrackEntry.trackTime` to hold a frame.
- Never skip `Skeleton.SetupPoseSlots()` after a `SetSkin(...)` call — a stale attachment from the previous skin can keep affecting visibility.
- Never read or write bone transforms from an arbitrary `Update()` without considering the Spine update life-cycle — do it from `UpdateWorld`/`UpdateComplete`/`BeforeApply` (or via matched `[DefaultExecutionOrder]`) or the change lands a frame late or gets silently overwritten.
- Never assign a `Spine/Skeleton`/URP/LWRP non-UI shader (or any non-`CanvasRenderer`-compatible shader) to a `SkeletonGraphic` — it can look fine in the Editor and still fail on-device; only `Spine/SkeletonGraphic*`-family materials belong there.
- Never assign a Materials array entry or `MeshRenderer.material` directly on a Spine-rendered skeleton — `SkeletonRenderer`/`SkeletonGraphic` overwrite it every `LateUpdate()`; use `CustomMaterialOverride`/`CustomSlotMaterials` or the matching custom-materials component instead.
- Never mix Built-in and URP/LWRP Spine shader families on the same pipeline, and never use a Spine shader with the Deferred rendering path — none of the Spine shaders support it.
- Never lower a skeleton's alpha directly for a fade effect — overlapping attachments show through each other; use `SkeletonRenderTexture`/`SkeletonRenderTextureFadeout` instead, and keep it disabled except while actively fading.
- Never reparent a `SkeletonUtilityBone` hinge-chain root under the skeleton's own bones — it disconnects the chain from skeleton-driven momentum and breaks the physics rig.
- Never delete a middle GameObject out of a `SkeletonUtilityBone` hierarchy expecting the rest to keep working — the hierarchy must mirror the skeleton's actual bone structure to function.
- Never attach `SkeletonRootMotion` to a `SkeletonMecanim`-driven skeleton (or vice versa with `SkeletonMecanimRootMotion`) — the two root-motion components are tied to their respective animation-driving component and aren't interchangeable.
- Never target `SkeletonMecanim` with a Timeline SkeletonAnimation/SkeletonGraphic/Skeleton Flip track — Timeline support doesn't exist for it.
- Never treat Timeline's Edit-mode mixing preview as ground truth — verify the actual transition in Play Mode before shipping a Timeline-driven sequence.
- Never manually assign on-demand-loading placeholder textures as a substitute for running a real build — the pre/post-build swap already handles production builds; manual placeholder assignment is Editor-preview-only and has no effect on the shipped executable.
- Never adopt on-demand loading speculatively for a skeleton with only one or two skins — reserve it for a measured build-size/memory problem, per `performance-and-algorithms.md`'s "measured, practical performance" principle.
- Never call a `Spine.Unity`/`UnityEngine` API from `Game.Core.*` — Spine depends on `UnityEngine`; skeleton control belongs entirely in `Game.Client.*`.

---
name: spine-animation
description: >
  spine-unity runtime integration: `SkeletonRenderer`, `SkeletonAnimation`,
  `SkeletonGraphic`, `SkeletonMecanim`, the `Skeleton`/`AnimationState`/
  `TrackEntry` API (`SetAnimation`, `AddAnimation`, `SetEmptyAnimation`,
  `SetSkin`, `SetupPoseSlots`, `FindBone`), `[SpineBone]`/`[SpineSlot]`/
  `[SpineAnimation]` attributes, followers (`BoneFollower`, `PointFollower`,
  `BoundingBoxFollower`), `SkeletonUtility`, `SkeletonRootMotion`,
  `SkeletonRenderSeparator`, `SkeletonRenderTexture`, `SkeletonGhost`,
  `AtlasUtilities` repacking, the `Spine/*` shader catalog, PMA vs. straight
  alpha, Spine Timeline tracks, and the on-demand-loading/Addressables
  extension. Not for: non-Spine Mecanim authoring (`unity-animation`), the
  native Sprite pipeline (`unity-2d-sprite`), 2D physics simulation
  (`unity-2d-physics`), writing new shaders (`shader-authoring`), pipeline
  configuration (`unity-urp-rendering`), particle VFX
  (`vfx-particle-authoring`), the general Addressables contract
  (`unity-addressables`).
---

# Spine Animation — Unity Runtime Integration

## Bundled resources

### References
Read-only context, loaded on demand so this file stays short.

| File | Contents | Read when |
|---|---|---|
| [root-links.md](references/root-links.md) | The spine-unity documentation roots this skill was built from | Starting any task here, or a needed page is not covered below |
| [main-components.md](references/main-components.md) | Component matrix, Inspector surface of each, `SkeletonGraphic` UI constraints, `SkeletonMecanim` limitations, runtime instantiation, `[Spine*]` attributes | Choosing or configuring the component a skeleton runs on |
| [skeleton-api.md](references/skeleton-api.md) | Skins, attachments, mix-and-match, `AtlasUtilities` repacking, flipping, bone read/write and the update life-cycle | Changing a skin or attachment, or touching bone transforms in code |
| [animation-state.md](references/animation-state.md) | `SetAnimation`/`AddAnimation`/empty animations, `TrackEntry` lifetime, the six event kinds, coroutine yield instructions | Playing, queuing, mixing, or reacting to animations |
| [utility-components.md](references/utility-components.md) | Followers, `SkeletonUtility` hierarchies and hinge chains, root motion, render separation, render-texture and ghost effects | A GameObject must track a bone, or draw order/fade/ragdoll behaviour is needed |
| [rendering.md](references/rendering.md) | Pipeline support matrix, shader catalog, material rebuild behaviour, draw-call causes, PMA vs. straight alpha, z-spacing | Assigning a material or shader, or a colour/batching issue appears |
| [timeline.md](references/timeline.md) | The three Spine track types, clip mixing parameters, known issues | Authoring a Timeline-driven sequence with a skeleton |
| [on-demand-loading.md](references/on-demand-loading.md) | The two extension packages, Addressables loader setup, Editor preview caveat | A measured build-size or memory problem points at atlas textures |
| [faq.md](references/faq.md) | Import, visual, cross-machine, performance, and licensing symptoms with root causes | Any Spine-specific symptom, before treating it as a generic Unity bug |

## 1. Objective
Wire Spine-exported skeletons into Unity correctly: the right main component for the rendering surface actually needed, animation played through `AnimationState`'s track and mix model instead of restarted every frame, skins and attachments manipulated through the documented `Skeleton` API instead of ad-hoc mesh hacks, rendering configured with the shader and alpha workflow that matches the active pipeline, and Timeline/on-demand-loading wired per each extension's real contract — never inventing a substitute for something the runtime already provides.

## 2. Role
Act as the 2D skeletal-animation specialist for the client track — the tool Unity Engineer and Technical Artist reach for whenever a feature involves a Spine-exported character, prop, or UI skeleton, from component setup through skin swapping, root motion, render separation, and Timeline-driven cinematics.

## 3. When to invoke this skill
- Setting up a newly imported `_SkeletonData` asset in a scene — deciding `SkeletonAnimation` vs. `SkeletonGraphic` vs. `SkeletonMecanim` for the actual rendering surface.
- Playing, queuing, or mixing animations via `AnimationState`/`TrackEntry`, or reacting to `Start`/`Interrupt`/`End`/`Complete`/`Dispose`/`Event` callbacks.
- Changing a skin or attachment at runtime — `SetSkin`/`SetAttachment`, mix-and-match composition, or `AtlasUtilities` repacking.
- Reading or driving bone transforms (`FindBone`, `GetWorldPosition`, `SetPositionSkeletonSpace`), or attaching a GameObject, collider, or physics rig to a bone (`BoneFollower`, `PointFollower`, `BoundingBoxFollower`, `SkeletonUtility`).
- Adding root motion, splitting draw order across layers, fading a skeleton without the overlapping-attachment artifact, or adding a motion trail.
- Configuring rendering: Built-in vs. URP vs. LWRP Spine shaders, PMA vs. straight alpha, tint black, outlines, sorting, or per-instance material overrides.
- Authoring Spine Timeline tracks, or deferring atlas texture loads via the on-demand-loading/Addressables extension.
- Diagnosing a Spine-specific symptom — dark borders, washed-out colours, colourful stripes, excessive draw calls, GC spikes on instantiate.
- Negative trigger: Mecanim Animator Controller, state machine, or Blend Tree authoring on a non-Spine rig, and Playables work unrelated to Spine — that's `unity-animation`.
- Negative trigger: native `SpriteRenderer`/`Sprite` pipeline work on art with no Spine skeleton — that's `unity-2d-sprite`.
- Negative trigger: simulating physics on the `PolygonCollider2D`/`Rigidbody2D` once `BoundingBoxFollower` has produced it — that's `unity-2d-physics`.
- Negative trigger: authoring a new shader or general HLSL/Shader Graph technique — that's `shader-authoring`; this skill only selects and configures the existing `Spine/*` catalog.
- Negative trigger: URP/HDRP pipeline configuration — Renderer Features, URP Asset, Volumes — that's `unity-urp-rendering`/`render-pipeline-urp-hdrp`.
- Negative trigger: generic particle VFX authoring — that's `vfx-particle-authoring`.
- Negative trigger: the general Addressables loading and reference-counting contract for non-Spine assets — that's `unity-addressables`; this skill covers only Spine's own extension.
- Negative trigger: any `Game.Core.*` code — Spine's runtime depends on `UnityEngine`, so Shared Core only ever receives an already-decided outcome from `Game.Client.*`.

## 4. How to use this skill
1. **Pick the right main component before anything else**, per [main-components.md](references/main-components.md) and the roots in [root-links.md](references/root-links.md) — `SkeletonRenderer` alone only for fully manual posing with no transitions; paired with `SkeletonAnimation` for Spine's own track model (the default); `SkeletonGraphic` when the skeleton renders inside a UI `Canvas`, since that uses `CanvasRenderer` rather than `MeshRenderer`; `SkeletonMecanim` only when Mecanim authoring is specifically wanted, and then budget for its documented limitations.
2. **Never call `AnimationState.SetAnimation` every frame**, per [animation-state.md](references/animation-state.md) — each call restarts from frame 1, so the pose visibly freezes. Track the current animation and call `SetAnimation`/`AddAnimation` only on an actual change; hold a specific frame with `TrackEntry.trackTime`.
3. **Call `Skeleton.SetupPoseSlots()` after every `SetSkin(...)`**, before the next `AnimationState.Apply()` or `SkeletonMecanim.Update()`, per [skeleton-api.md](references/skeleton-api.md) — otherwise an attachment set under the previous skin keeps affecting visibility, with nothing reported.
4. **Read and write bone state only from the update life-cycle hooks** — `UpdateWorld`, `UpdateComplete`, or `BeforeApply`, or a matched `[DefaultExecutionOrder]`, per [skeleton-api.md](references/skeleton-api.md). From an arbitrary `Update()` the read lands one frame late or the write is silently overwritten.
5. **Use the `[Spine*]` attributes on every string field naming skeleton data**, per [main-components.md](references/main-components.md) — they populate an Inspector dropdown from the real `SkeletonDataAsset`, turning a typo into an edit-time error instead of a silent runtime no-op.
6. **Prefer a follower or utility component over per-frame bone-copying code**, per [utility-components.md](references/utility-components.md) — `BoneFollower`/`PointFollower`/`BoneFollowerGraphic` for one isolated transform; `SkeletonUtility` + `SkeletonUtilityBone` only when a full mirrored hierarchy is genuinely needed; `BoundingBoxFollower` for a collider synced to the current frame's bounding-box attachment.
7. **Match the shader family to the render pipeline and never mix them**, per [rendering.md](references/rendering.md) — Built-in `Spine/*` shaders for the Built-in pipeline, the URP/LWRP extension packages for those, and only `Spine/SkeletonGraphic*`-family materials on `SkeletonGraphic`. Confirm PMA vs. straight alpha against both the texture import settings and the project Color Space before treating a colour artifact as anything else.
8. **Never assign a Materials array entry or `MeshRenderer.material` directly**, per [rendering.md](references/rendering.md) — `SkeletonRenderer`/`SkeletonGraphic` rebuild that array every `LateUpdate()` from current attachment and blend state. Use `SkeletonRendererCustomMaterials`/`CustomSlotMaterials` for overrides, and `Skeleton.R`/`G`/`B`/`A` for tinting that preserves batching.
9. **Use render separation whenever another GameObject must draw between skeleton parts**, per [utility-components.md](references/utility-components.md) — `Separator Slot Names` plus `SkeletonRenderSeparator`, or `SkeletonGraphic`'s built-in `Enable Separation`. A single skeleton's draw order is atomic, so sorting-order tweaks cannot achieve this.
10. **Use `SkeletonRenderTexture` for a full-skeleton alpha fade, never a per-slot alpha reduction**, per [utility-components.md](references/utility-components.md) — overlapping attachments show through each other below full opacity. Keep the component disabled except while the fade runs; it costs an intermediate render pass.
11. **On Timeline, order tracks base-first and verify mixing in Play Mode**, per [timeline.md](references/timeline.md) — assign each `Track Index` deliberately for multi-track mixing, and treat the Edit-mode preview as indicative only. `SkeletonMecanim` has no Timeline track support at all.
12. **Reach for on-demand loading only once a measured build-size or memory problem justifies it**, per [on-demand-loading.md](references/on-demand-loading.md) and `performance-and-algorithms.md`'s Verification section — then install the Addressables extension, mark the textures Addressable, and use the `SpineAtlasAsset`'s "Add Addressables Loader"; no custom loading code is needed for the standard case.
13. **Diagnose a Spine-specific symptom against the FAQ before assuming a generic Unity cause**, per [faq.md](references/faq.md) — dark borders, washed colours, and colourful stripes are almost always a PMA/straight-alpha or Color Space mismatch, and excessive draw calls are almost always multiple atlas pages or alternating slot blend modes.
14. **Ship the binary `.skel.bytes` export and pool skeleton instances** — pre-warm, then `AnimationState.ClearTracks()` and disable rather than `Destroy()`, per [faq.md](references/faq.md). This is the Spine-specific instance of `performance-and-algorithms.md`'s pooling requirement, not a separate rule.
15. **If the rendering surface, render pipeline, or alpha workflow is unstated, ask before wiring anything** — surface decides step 1, pipeline and alpha decide step 7, and all three are invisible in code that compiles and renders wrongly only on device.

## 5. Specific goals / tasks this skill performs
- Setting up a skeleton in-scene with the correct main component for its rendering surface.
- Playing, queuing, and mixing animations through `AnimationState`/`TrackEntry`, including events and coroutine yield instructions.
- Runtime skin/attachment changes, mix-and-match composition, and `AtlasUtilities` repacking.
- Wiring followers, `SkeletonUtility` hierarchies, hinge-chain physics rigs, and root motion.
- Configuring render separation, custom materials, tint black, outlines, and PMA/straight-alpha correctness for the confirmed pipeline.
- Building fade or motion-trail effects, authoring Spine Timeline tracks, and wiring the on-demand-loading extension.
- Diagnosing Spine-specific import, visual, and performance symptoms before escalating them as generic Unity issues.
- Out of scope: non-Spine Mecanim authoring (`unity-animation`); native Sprite pipeline (`unity-2d-sprite`); 2D physics simulation (`unity-2d-physics`); new shader authoring (`shader-authoring`); pipeline configuration (`unity-urp-rendering`/`render-pipeline-urp-hdrp`); particle VFX (`vfx-particle-authoring`); the general Addressables contract (`unity-addressables`); any `Game.Core.*` usage.

## 6. Output format
```
## Spine Animation Work — <skeleton/feature name>
- Main component: <SkeletonRenderer+SkeletonAnimation / SkeletonGraphic / SkeletonMecanim> — rationale
- Animation control: <track indices, mix plan, empty-animation transitions, events wired>
- Skin/attachment handling: <static / SetSkin swap / mix-and-match / runtime repack> — SetupPoseSlots confirmed
- Bone/utility wiring: <BoneFollower / PointFollower / BoundingBoxFollower / SkeletonUtility / none> — life-cycle hook used
- Root motion: <SkeletonRootMotion / SkeletonMecanimRootMotion / none>
- Rendering: <shader family> — PMA or straight alpha, tint black, outline, render separation
- Timeline: <tracks and ordering — or "not applicable">
- On-demand loading: <Addressables loader configured — or "not applicable">
- Rule compliance: <pooling and export format, per Memory discipline>
- Verification: <measurement behind any performance claim, or "not applicable">
- Layer: Game.Client.* — never Game.Core.*
- Known limitations: <...>
```

**Extended report — emit ONLY when the requester asks for it.** It replaces the one-line `Known limitations` above with all three fields:
```
- Known limitations: <what the delivered solution does not cover>
- Latent concerns: <failure modes not yet triggered: assumptions holding only under current conditions, thresholds not yet reached>
- Future remediation: <the concrete fix for each concern, each with its trigger condition>
```

## 7. Examples
**Example 1**
- Input: a player skeleton must loop locomotion, crossfade into an attack, then return to locomotion.
- Output: `SkeletonRenderer`+`SkeletonAnimation` in world space; `SetAnimation(0, "locomotion", true)` called once on state entry, never per frame; attack triggered on the actual input edge, with the `SkeletonDataAsset` mix duration handling the crossfade; subscribed to that entry's `Complete` to return to locomotion, deferred one frame by coroutine to avoid the same-frame Start/End ordering documented in [animation-state.md](references/animation-state.md).

**Example 2**
- Input: "just tint the boss skeleton red for a hit-flash by swapping in a red-tinted material instance."
- Output: declined — a swapped material breaks batching with other instances and is overwritten on the next `LateUpdate()` anyway, since `SkeletonRenderer` rebuilds the Materials array every frame. Used `Skeleton.R`/`G`/`B` with PMA Vertex Colors enabled, which tints without breaking batching or fighting the rebuild.

**Example 3**
- Input: a UI equipment-preview panel must show the same skeleton the world uses, inside a `Canvas`.
- Output: used `SkeletonGraphic` rather than reusing the world setup, for `CanvasRenderer`/`RectMask2D` compatibility; assigned a `Spine/SkeletonGraphic*` material via the `Detect Material` button instead of the world skeleton's `Spine/Skeleton` material, which renders incorrectly under `CanvasRenderer`; ran `Match RectTransform with Mesh` so `RectMask2D` bounds are correct.

**Example 4**
- Input: an equipment system must swap weapon and armour skins at runtime from inventory state.
- Output: composed the loadout with `AddSkin(...)` calls from `SkeletonData.FindSkin(...)` per equipped piece, called `SetSkin(...)` then `SetupPoseSlots()`, then `AnimationState.Apply(skeleton)` to refresh the current pose immediately rather than waiting a frame — per [skeleton-api.md](references/skeleton-api.md).

## 8. Edge cases & guardrails
- Never call `SetAnimation` every frame, and never skip `SetupPoseSlots()` after `SetSkin(...)` — the first freezes the pose, the second leaks stale attachment visibility, and neither raises an error.
- Never read or write bone transforms from an arbitrary `Update()` — use `UpdateWorld`/`UpdateComplete`/`BeforeApply` or a matched `[DefaultExecutionOrder]`.
- Never put a non-`CanvasRenderer`-compatible shader on `SkeletonGraphic` — it can look correct in the Editor and fail on device; only `Spine/SkeletonGraphic*` materials belong there.
- Never assign a Materials array entry or `MeshRenderer.material` on a Spine skeleton — it is rebuilt every `LateUpdate()`; use the custom-materials components instead.
- Never mix Built-in and URP/LWRP Spine shader families, and never use any Spine shader with the Deferred rendering path — none support it.
- Never lower a skeleton's alpha directly for a fade — overlapping attachments show through each other; use `SkeletonRenderTexture`/`SkeletonRenderTextureFadeout` and keep it disabled otherwise.
- Never reparent a `SkeletonUtilityBone` hinge-chain root under the skeleton's own bones, and never delete a middle GameObject from the hierarchy — both break the rig, the first by cutting it off from skeleton-driven momentum.
- Never pair `SkeletonRootMotion` with `SkeletonMecanim` or `SkeletonMecanimRootMotion` with `SkeletonAnimation` — each is tied to its own animation driver.
- Never target `SkeletonMecanim` with a Timeline track, and never treat Timeline's Edit-mode mixing preview as ground truth — verify in Play Mode.
- Never manually assign on-demand-loading placeholder textures as a substitute for a real build — that path is Editor-preview only and has no effect on the shipped executable.
- Never adopt on-demand loading for a skeleton with one or two skins — that's speculative complexity YAGNI already forbids; wait for a measurement.
- Never call a `Spine.Unity` or `UnityEngine` API from `Game.Core.*` — skeleton control belongs entirely in `Game.Client.*`.
- If the rendering surface, pipeline, or alpha workflow is unstated, ask — each decides a different §6 field and none is recoverable from the code afterwards.

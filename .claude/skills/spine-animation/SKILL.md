---
name: spine-animation
description: "spine-unity runtime: SkeletonAnimation/SkeletonGraphic/SkeletonMecanim, AnimationState tracks, SetSkin/SetupPoseSlots, events, BoneFollower, SkeletonUtility, Spine shaders, PMA, Timeline. Use on Spine-animated characters or UI."
user-invocable: false
---

# Spine Animation

Not for: Mecanim on non-Spine rigs (`unity-animation`), native Sprite pipeline (`unity-2d-sprite`), physics on the collider a `BoundingBoxFollower` produces (`unity-2d-physics`), Canvas/`RectTransform`/Layout Group around a `SkeletonGraphic` (`ugui`), new shaders (`shader-authoring`), pipeline config (`unity-urp-rendering`), particle VFX (`vfx-particle-authoring`), general Addressables contract (`unity-addressables`).
Docs: `https://esotericsoftware.com/spine-unity-<page>` (installation, main-components, utility-components, rendering, timeline, on-demand-loading, faq, assets) — spine-unity 4.3+; URLs are unversioned, so confirm against the installed runtime. A Spine licence is required to ship the runtimes; flag `Spine.Unity.*` without a confirmed licence.

| Reference | Read when |
|---|---|
| [main-components.md](references/main-components.md) | Choosing/configuring the component a skeleton runs on; `SkeletonGraphic` or `SkeletonMecanim` behaves oddly; `[Spine*]` attributes; instantiating from code |
| [skeleton-api.md](references/skeleton-api.md) | Changing a skin/attachment, repacking, flipping, or reading/writing bones in code |
| [animation-state.md](references/animation-state.md) | Playing, queuing, mixing, or reacting to animations and events |
| [utility-components.md](references/utility-components.md) | A GameObject/collider must track a bone; hinge chains, root motion, render separation, fade, ghost trail |
| [rendering.md](references/rendering.md) | Assigning a material/shader, tinting, draw-call count, sorting, or a pipeline/alpha mismatch |
| [timeline.md](references/timeline.md) | Authoring a Timeline sequence with a skeleton |
| [on-demand-loading.md](references/on-demand-loading.md) | A measured build-size/memory problem points at atlas textures |
| [faq.md](references/faq.md) | Any Spine symptom (import error, dark borders, stripes, GC/draw-call spikes), before blaming generic Unity |

## Steps
1. **Rendering surface, pipeline or alpha workflow unstated → `Blocked` naming it** — they decide steps 2 and 7 and are invisible in code that compiles and renders wrongly only on device.
2. **Pick the component**, per [main-components.md](references/main-components.md): `SkeletonRenderer` + `SkeletonAnimation` by default (world); `SkeletonGraphic` inside a Canvas (`CanvasRenderer`); `SkeletonMecanim` only when Mecanim authoring is wanted and its limits are accepted; `SkeletonRenderer` alone only for fully manual posing.
3. **Call `SetAnimation` only on a change**, per [animation-state.md](references/animation-state.md) — each call restarts from frame 1, so per-frame calls freeze the pose. Hold a frame with `TrackEntry.trackTime`.
4. **Call `Skeleton.SetupPoseSlots()` after every `SetSkin(...)`**, then `AnimationState.Apply(skeleton)` (`SkeletonMecanim.Update()` on Mecanim) — otherwise attachments from the previous skin keep affecting visibility. Per [skeleton-api.md](references/skeleton-api.md).
5. **Read/write bones only in `BeforeApply`/`UpdateLocal`/`UpdateWorld`/`UpdateComplete`** or under a matched `[DefaultExecutionOrder]` — from a plain `Update()` reads are a frame late and writes are overwritten.
6. **Type skeleton-data string fields with `[SpineBone]`/`[SpineSlot]`/`[SpineSkin]`/`[SpineAnimation]`/`[SpineEvent]`…** — a misspelled bare string is a silent runtime no-op.
7. **Match shader family to pipeline**, per [rendering.md](references/rendering.md): Built-in `Spine/*`, URP/LWRP extension packages for those, only `Spine/SkeletonGraphic*` on `SkeletonGraphic`. Check PMA vs straight alpha (texture import + Color Space) before treating a colour artifact as anything else.
8. **Override materials via `SkeletonRendererCustomMaterials`/`SkeletonGraphicCustomMaterials`, tint via `Skeleton.R/G/B/A`** — the Materials array is rebuilt every `LateUpdate()`, so direct edits vanish and swapped materials break batching.
9. **Prefer followers over per-frame bone-copy code**, per [utility-components.md](references/utility-components.md): `BoneFollower`/`PointFollower`/`BoneFollowerGraphic` for one transform; `BoundingBoxFollower` for a collider; `SkeletonUtility` only for a full mirrored hierarchy.
10. **Draw another object between skeleton parts with render separation** (`Separator Slot Names` + `SkeletonRenderSeparator`, or `SkeletonGraphic` `Enable Separation`) — one skeleton's draw order is atomic, so sorting tweaks cannot do it.
11. **Fade a whole skeleton with `SkeletonRenderTexture` + `SkeletonRenderTextureFadeout`**, enabled only during the fade (extra render pass) — lowering alpha directly shows overlapping attachments through each other.
12. **Timeline**, per [timeline.md](references/timeline.md): base animation on the top track, overlays below, distinct `Track Index` per track, verify mixing in Play Mode.
13. **Adopt on-demand loading only after a measurement**, per [on-demand-loading.md](references/on-demand-loading.md) and `csharp-standards` → `performance-and-algorithms.md` (Verification).
14. **Diagnose symptoms against [faq.md](references/faq.md) first.** Ship binary `.skel.bytes`; pool skeletons (pre-warm; on despawn `ClearTracks()` and disable, not `Destroy`).
15. **Keep all Spine code in the feature's Unity assembly** — never `Spine.Unity` in a Core assembly.

## Never
- Mix Built-in and URP/LWRP Spine shader families, or use any Spine shader with Deferred.
- Put a URP/non-UI shader on `SkeletonGraphic` — it can look right in the Editor and fail on device.
- Pair `SkeletonRootMotion` with `SkeletonMecanim`, or `SkeletonMecanimRootMotion` with `SkeletonAnimation` — no root motion, no error.
- Reparent a hinge-chain root under the skeleton's bones, or delete a middle `SkeletonUtilityBone` GameObject — the rig breaks silently.
- Target `SkeletonMecanim` with a Timeline track — none exists.
- Hand-assign on-demand placeholder textures as a build substitute — Editor preview only.

## Output
```
## Spine Animation — <skeleton/feature>
- Component: <SkeletonRenderer+SkeletonAnimation / SkeletonGraphic / SkeletonMecanim> — why
- Animation: <tracks, mixes, events>
- Skin/attachments: <static / SetSkin / mix-and-match / repack> — SetupPoseSlots confirmed
- Bones/utilities: <followers / SkeletonUtility / root motion / none>
- Rendering: <shader family>, PMA or straight, tint black, separation
- Timeline / on-demand loading: <setup — or n/a>
- Verified: <measurement behind any performance claim, or "not run">
- Known limitations: <...>
```
On request only, add `Latent concerns` and `Future remediation`, each with its trigger.

## Example
- "Tint the boss red for a hit-flash by swapping in a red material" → declined: the Materials array is rebuilt every `LateUpdate()` and a swap breaks batching; used `Skeleton.R/G/B` with PMA Vertex Colors.

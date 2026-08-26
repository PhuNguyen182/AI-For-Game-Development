# Skeleton API — Skins, Attachments, Repacking & Bone Access

Source: [spine-unity Main Components](https://esotericsoftware.com/spine-unity-main-components#Main-Components) (spine-unity v4.3+).
Covers: SKILL.md §4 — **"Call `Skeleton.SetupPoseSlots()` after every `SetSkin(...)`"**, **"Read and write bone state only from the update life-cycle hooks"**.

The `Skeleton` object, reached through `SkeletonRenderer.Skeleton` or
`SkeletonGraphic.Skeleton`, manipulates bones, slots, skins, and attachments
directly. Two ordering constraints govern almost everything here: a skin change
needs a pose refresh, and a bone access needs the right life-cycle hook.
Track playback is [animation-state.md](animation-state.md); the components
exposing this object are [main-components.md](main-components.md).

## Contents

- [Core calls](#core-calls)
- [Mix-and-match skin composition](#mix-and-match-skin-composition)
- [Runtime repacking](#runtime-repacking)
- [Bone access and the update life-cycle](#bone-access-and-the-update-life-cycle)

## Core calls

| Call | Effect | Use when | Source |
|---|---|---|---|
| `skeleton.SetAttachment("slot", "attachment")` | Swaps one slot's attachment; returns success | A single visual part changes without a full skin swap | [Main Components](https://esotericsoftware.com/spine-unity-main-components) |
| `skeleton.SetSkin("skinName")` | Replaces the active skin; returns success | A whole named skin applies | [Main Components](https://esotericsoftware.com/spine-unity-main-components) |
| `skeleton.SetupPoseSlots()` | Resets slot state to the setup pose | **Immediately after every `SetSkin`**, before the next apply | [Main Components](https://esotericsoftware.com/spine-unity-main-components) |
| `skeleton.SetupPose()` / `SetupPoseBones()` | Resets the full pose, or bones only | A manual pose reset is wanted before applying animation | [Main Components](https://esotericsoftware.com/spine-unity-main-components) |
| `skeleton.ScaleX = -skeleton.ScaleX` | Flips horizontally; `ScaleY` flips vertically; `ScaleX < 0` reports the current state | Mirroring a character without a second animation set | [Main Components](https://esotericsoftware.com/spine-unity-main-components) |

**Critical caveat**: omitting `SetupPoseSlots()` after `SetSkin(...)` lets an
attachment set under the previous skin keep affecting visibility. Nothing
throws; the wrong part simply stays visible.

```csharp
[SpineSlot] public string slotProperty = "slotName";
[SpineAttachment] public string attachmentProperty = "attachmentName";

bool applied = this.skeletonRenderer.Skeleton.SetAttachment(this.slotProperty, this.attachmentProperty);
```

## Mix-and-match skin composition

| Step | Call | Source |
|---|---|---|
| Build an empty skin | `new Skin("custom-girl")` | [Main Components](https://esotericsoftware.com/spine-unity-main-components) |
| Add each source skin | `mixAndMatchSkin.AddSkin(skeletonData.FindSkin("skin-base"))` | [Main Components](https://esotericsoftware.com/spine-unity-main-components) |
| Apply it | `skeleton.SetSkin(mixAndMatchSkin)` | [Main Components](https://esotericsoftware.com/spine-unity-main-components) |
| Refresh slots | `skeleton.SetupPoseSlots()` | [Main Components](https://esotericsoftware.com/spine-unity-main-components) |
| Force the pose now | `skeletonAnimation.AnimationState.Apply(skeleton)`, or `skeletonMecanim.Update()` on `SkeletonMecanim` | [Main Components](https://esotericsoftware.com/spine-unity-main-components) |

```csharp
Skeleton skeleton = this.skeletonRenderer.Skeleton;
SkeletonData skeletonData = skeleton.Data;

var mixAndMatchSkin = new Skin("custom-girl");
mixAndMatchSkin.AddSkin(skeletonData.FindSkin("skin-base"));
mixAndMatchSkin.AddSkin(skeletonData.FindSkin("nose/short"));

skeleton.SetSkin(mixAndMatchSkin);
skeleton.SetupPoseSlots();
this.skeletonAnimation.AnimationState.Apply(skeleton);
```

Example scenes: `Spine Examples/Other Examples/Mix and Match`, `Mix and Match Equip`.

## Runtime repacking

Combines the attachments of a composed skin into one texture via
`Spine.Unity.AttachmentTools.AtlasUtilities`, so a mix-and-match character does
not cost one draw call per source skin.

| Element | Effect | Source |
|---|---|---|
| `repackingOutput.DestroyGeneratedAssets()` | Cleans up the previous repack — call before repacking again or the textures leak | [Main Components](https://esotericsoftware.com/spine-unity-main-components) |
| `RepackAttachmentsSettings.Default` | The starting settings; `UseSourceMaterialsFrom(skeletonDataAsset)` and `maxAtlasSize` are the usual edits | [Main Components](https://esotericsoftware.com/spine-unity-main-components) |
| `collectedSkin.GetRepackedSkin(name, settings, ref output)` | Produces the repacked skin; assign to `skeleton.Skin`, then `SetupPoseSlots()` and apply | [Main Components](https://esotericsoftware.com/spine-unity-main-components) |
| `AtlasUtilities.ClearCache()` | Optional cleanup after several repack operations | [Main Components](https://esotericsoftware.com/spine-unity-main-components) |
| Normal maps | Add `settings.additionalTexturePropertyIDsToCopy = new[] { Shader.PropertyToID("_BumpMap") }` plus a matching `repackingOutput.additionalOutputTextures` | [Main Components](https://esotericsoftware.com/spine-unity-main-components) |

| Repack failure cause | Fix | Source |
|---|---|---|
| Source textures not readable | Enable `Read/Write` on the texture import settings | [Main Components](https://esotericsoftware.com/spine-unity-main-components) |
| Texture compression enabled | Set Compression to `None`, not `Normal Quality` | [Main Components](https://esotericsoftware.com/spine-unity-main-components) |
| Reduced-resolution quality tier | Quality tiers must use full-resolution textures — half/quarter hits a Unity bug | [Main Components](https://esotericsoftware.com/spine-unity-main-components) |
| Non-power-of-two source | Make the texture power-of-two, or enable `Power of two` in the Spine export | [Main Components](https://esotericsoftware.com/spine-unity-main-components) |

## Bone access and the update life-cycle

| Call | Effect | Source |
|---|---|---|
| `skeleton.FindBone("boneName")` | Returns the `Bone` — cache it rather than looking it up per frame | [Main Components](https://esotericsoftware.com/spine-unity-main-components) |
| `bone.GetWorldPosition(skeletonRenderer.transform)` | World position; on `SkeletonGraphic` also scale by the Canvas `referencePixelsPerUnit` | [Main Components](https://esotericsoftware.com/spine-unity-main-components) |
| `bone.SetPositionSkeletonSpace(position)` | Writes the position in skeleton space | [Main Components](https://esotericsoftware.com/spine-unity-main-components) |
| `bone.GetQuaternion()` | World rotation as a `Quaternion` | [Main Components](https://esotericsoftware.com/spine-unity-main-components) |

| Hook | Fires | Use when | Source |
|---|---|---|---|
| `BeforeApply` | Before animations are applied this frame | Seeding state the animation should then override | [Main Components](https://esotericsoftware.com/spine-unity-main-components) |
| `UpdateLocal` | After animations applied to local values | Adjusting local bone values before world transforms resolve | [Main Components](https://esotericsoftware.com/spine-unity-main-components) |
| `UpdateWorld` | After world transforms are calculated | Reading or overriding world bone state; calling `skeleton.UpdateWorldTransform()` here re-applies overrides | [Main Components](https://esotericsoftware.com/spine-unity-main-components) |
| `UpdateComplete` | After the full update finishes | Reading final state with no further modification intended | [Main Components](https://esotericsoftware.com/spine-unity-main-components) |

**Critical caveat**: bone access from an arbitrary `Update()` reads one frame
late or is silently overwritten by the next apply. Use a hook above, or a
`[DefaultExecutionOrder]` matched against `SkeletonAnimation`.

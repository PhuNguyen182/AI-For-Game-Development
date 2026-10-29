# Skeleton API

`Skeleton` via `SkeletonRenderer.Skeleton` / `SkeletonGraphic.Skeleton`. Page: main-components.

| Call | Effect |
|---|---|
| `SetAttachment("slot", "attachment")` | Swap one slot's attachment; returns success |
| `SetSkin("name")` / `SetSkin(Skin)` | Replace the active skin; returns success |
| `SetupPoseSlots()` | Reset slot state — **after every `SetSkin`**, else the previous skin's attachments keep affecting visibility, with no error |
| `SetupPose()` / `SetupPoseBones()` | Reset full pose / bones only |
| `ScaleX = -ScaleX` | Flip horizontally (`ScaleY` vertical; `ScaleX < 0` reads state) |

## Mix-and-match
```csharp
var skin = new Skin("custom-girl");
skin.AddSkin(skeletonData.FindSkin("skin-base"));
skin.AddSkin(skeletonData.FindSkin("nose/short"));
skeleton.SetSkin(skin);
skeleton.SetupPoseSlots();
skeletonAnimation.AnimationState.Apply(skeleton);   // SkeletonMecanim: skeletonMecanim.Update()
```
Scenes: `Spine Examples/Other Examples/Mix and Match`, `Mix and Match Equip`.

## Runtime repacking
`Spine.Unity.AttachmentTools.AtlasUtilities` merges a composed skin's attachments into one texture, so it is not one draw call per source skin.
- `RepackAttachmentsSettings.Default`; usual edits: `UseSourceMaterialsFrom(skeletonDataAsset)`, `maxAtlasSize`.
- `collectedSkin.GetRepackedSkin(name, settings, ref output)` → assign to `skeleton.Skin`, `SetupPoseSlots()`, apply.
- `repackingOutput.DestroyGeneratedAssets()` before repacking again, else textures leak. `AtlasUtilities.ClearCache()` is optional after several repacks.
- Normal maps: `settings.additionalTexturePropertyIDsToCopy = new[] { Shader.PropertyToID("_BumpMap") }` plus matching `repackingOutput.additionalOutputTextures`.
- Fine in Editor, white polygons in a build — a precondition failed: source textures need `Read/Write`; Compression `None` (not `Normal Quality`); quality tiers must use full-resolution textures (half/quarter hits a Unity bug); source must be power-of-two (or enable `Power of two` in the Spine export).

## Bones and the update life-cycle
`FindBone("name")` (cache it); `bone.GetWorldPosition(transform)` (on `SkeletonGraphic` also scale by Canvas `referencePixelsPerUnit`); `bone.SetPositionSkeletonSpace(pos)`; `bone.GetQuaternion()`.

| Hook | Fires | Use |
|---|---|---|
| `BeforeApply` | before animations apply | seed state the animation overrides |
| `UpdateLocal` | after apply, before world transforms | adjust local bone values |
| `UpdateWorld` | after world transforms | read/override world state; `skeleton.UpdateWorldTransform()` here re-applies overrides |
| `UpdateComplete` | after the full update | read final state |

From a plain `Update()`, reads are a frame late or writes are overwritten; use a hook or a `[DefaultExecutionOrder]` matched against `SkeletonAnimation`.

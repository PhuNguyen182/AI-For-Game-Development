# Timeline

Page: timeline. Separate UPM package. Several parameters silently do nothing, and Edit-mode preview mixing is not the Play Mode code path.

| Track | Drives |
|---|---|
| SkeletonAnimation Track | `SkeletonAnimation`, at `AnimationState` level |
| SkeletonGraphic Track | `SkeletonGraphic`, at `AnimationState` level |
| Skeleton Flip Track | flips either skeleton |

Older names: "Spine AnimationState Track", "Spine AnimationState Graphic Track", "Spine Skeleton Flip Track". `SkeletonMecanim` has no track and no workaround short of switching component.

## Setup
1. Add `SkeletonAnimationPlayableHandle` (or `SkeletonGraphicPlayableHandle`) to the target.
2. Timeline window → right-click → Spine → track type; bind the skeleton GameObject.
3. Drag an `AnimationReferenceAsset` onto the track for a clip (Ctrl/Cmd+D duplicates).

## Parameters
- Track: `Track Index` (which `AnimationState` track; distinct per Timeline track on one skeleton), `Unscaled Time`. Order tracks with the base animation on top, overlays below.
- Clip: `Clip In`, `Blend In Duration` (drag clip edge), `Speed Multiplier`, `Don't Pause with Director`, `Don't End with Clip` (keep playing instead of an empty animation in the following blank space), `Clip End Mix Out Duration` (negative pauses instead of mixing out), `Default Mix Duration` (use `SkeletonData` mix; disable for custom `Mix Duration`), `Use Blend Duration` (sync `Mix Duration` to the clip's blend length).
- `Event Threshold`, `Attachment Threshold`, `Draw Order Threshold`, `Alpha` map to `TrackEntry.EventThreshold`, `MixAttachmentThreshold`, `MixDrawOrderThreshold`, `Alpha`.
- "Ease Out Duration" and "Blend Curves" are shown but **ignored**.

## Runtime behaviour
- `SetAnimation()` fires at each clip start with its `AnimationReferenceAsset`; an unassigned clip calls `SetEmptyAnimation`.
- A missing animation reference is **silently ignored**: the previous animation keeps playing.
- Whatever played before the Timeline continues until the first clip begins.
- Clip duration matters from Timeline 4.0; in 3.8 an animation persisted across blank space.
- Verify real transitions in Play Mode.

## Skeleton Flip Track
Clip parameters `Flip X`, `Flip Y` applied every frame. Add via the same handle, Spine → "Skeleton Flip Track", right-click dopesheet → "Add Spine Skeleton Flip Clip". At end of playback it restores the flip state captured at start, not an unflipped default.

The console error `DrivenPropertyManager has failed to register property 'm_Script'...` is a documented Unity-side issue, not a Spine bug.

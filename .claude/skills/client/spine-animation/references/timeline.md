# Timeline Extension — SkeletonAnimation/SkeletonGraphic/Skeleton Flip Tracks

Source: [spine-unity-timeline](https://esotericsoftware.com/spine-unity-timeline).

Distributed as a separate UPM package. Provides three Timeline track types:

1. **SkeletonAnimation Track** — animates a `SkeletonAnimation` component.
2. **SkeletonGraphic Track** — animates a `SkeletonGraphic` component.
3. **Skeleton Flip Track** — flips a `SkeletonAnimation` or `SkeletonGraphic` skeleton.

(Older versions named these "Spine AnimationState Track," "Spine AnimationState Graphic Track," and "Spine Skeleton Flip Track" — same components, renamed.)

**Limitation**: only `SkeletonAnimation` and `SkeletonGraphic` are supported — `SkeletonMecanim` has no Timeline integration.

## SkeletonAnimation Track / SkeletonGraphic Track

Set animations at the `AnimationState` level of the target component.

**Track parameters**:
- `Track Index` — which `AnimationState` track index this Timeline track targets. Matters as soon as more than one Timeline track drives the same skeleton — **order tracks with the base track on top and overlay tracks below it.**
- `Unscaled Time` — sets the target's `UnscaledTime` when starting clips, for per-track normal-vs-unscaled time control.

### Spine Animation State Clip
Add by dragging an `AnimationReferenceAsset` onto the track.

**Timing**: `Clip In` (local start-time offset into the animation), `Blend In Duration` (drag the clip's edge to adjust), `Speed Multiplier` (2.0 = double speed, 0.5 = half speed).

**Clip parameters**: `Don't Pause with Director` (keep playing while the Director is paused), `Don't End with Clip` (keep playing past the clip's end instead of setting an empty animation in the following blank space), `Clip End Mix Out Duration` (mix duration into the empty animation that follows blank timeline space — a negative value pauses instead of mixing out).

**Mixing**: `Default Mix Duration` (use the `SkeletonData` asset's own configured mix duration) vs. a custom `Mix Duration` when disabled; `Use Blend Duration` (sync `Mix Duration` to the timeline clip's own blend/transition length for easy cross-fade tuning); `Event Threshold` / `Attachment Threshold` / `Draw Order Threshold` / `Alpha` map directly to `TrackEntry.EventThreshold` / `MixAttachmentThreshold` / `MixDrawOrderThreshold` / `Alpha` from main-components.md's AnimationState API.

**Ignored parameters**: "Ease Out Duration" and "Blend Curves" have no effect — don't rely on them.

### Setup
1. Add a `SkeletonAnimationPlayableHandle` (or `SkeletonGraphicPlayableHandle` for `SkeletonGraphic`) component to the target GameObject.
2. Right-click in the Timeline window → Spine → "SkeletonAnimation Track" (or "SkeletonGraphic Track").
3. Assign the skeleton GameObject as the track's binding.
4. Drag an `AnimationReferenceAsset` into the track to create a clip. Duplicate clips with Ctrl/Cmd+D.

### Runtime behavior
- `AnimationState.SetAnimation()` fires at the start of each clip, using that clip's `AnimationReferenceAsset`.
- Clip duration matters from Timeline 4.0 onward (in 3.8, animation persisted across blank space regardless of clip length).
- A clip left unassigned calls `SetEmptyAnimation`.
- A missing/unresolved animation reference is silently ignored — the previous animation just keeps playing; this is a common silent-failure mode to check for.
- Whatever animation was playing before the Timeline started continues until the first clip actually begins.
- **Edit-mode preview mixing in the Timeline window can visually differ from actual Play Mode mixing** — always verify the real transition in Play Mode before treating an edit-mode preview as ground truth.

## Skeleton Flip Track

**Spine Skeleton Flip Clip parameters**: `Flip X`, `Flip Y` — applied for the clip's duration.

### Setup
1. Add `SkeletonAnimationPlayableHandle`/`SkeletonGraphicPlayableHandle` to the target.
2. Right-click in Timeline → Spine → "Skeleton Flip Track."
3. Assign the skeleton GameObject as the track binding.
4. Right-click the track's dopesheet → "Add Spine Skeleton Flip Clip" → adjust timing/name/`Flip X`/`Flip Y`.

### Runtime behavior
The specified flip values apply every frame for the clip's duration. At the end of the whole timeline's playback, the track reverts the skeleton's flip state to whatever it was captured as when playback started — not necessarily to an "unflipped" default.

## Known issues
A harmless console error can appear: `"DrivenPropertyManager has failed to register property 'm_Script'..."` — a documented Unity-side issue, not a Spine bug; safe to ignore.

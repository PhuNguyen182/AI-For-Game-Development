# Timeline Extension — SkeletonAnimation, SkeletonGraphic & Skeleton Flip Tracks

Source: [spine-unity Timeline](https://esotericsoftware.com/spine-unity-timeline).
Covers: SKILL.md §4 — **"On Timeline, order tracks base-first and verify mixing in Play Mode"**.

A separate UPM package providing three track types. The two failure modes worth
knowing before authoring: several parameters silently do nothing, and Edit-mode
preview mixing is not the same code path as Play Mode. Track playback outside
Timeline is [animation-state.md](animation-state.md).

## Contents

- [The three track types](#the-three-track-types)
- [Track parameters](#track-parameters)
- [Clip parameters](#clip-parameters)
- [Setup](#setup)
- [Runtime behaviour](#runtime-behaviour)
- [Skeleton Flip Track](#skeleton-flip-track)

## The three track types

| Track | Drives | Source |
|---|---|---|
| SkeletonAnimation Track | A `SkeletonAnimation` component, at the `AnimationState` level | [Timeline](https://esotericsoftware.com/spine-unity-timeline) |
| SkeletonGraphic Track | A `SkeletonGraphic` component, at the `AnimationState` level | [Timeline](https://esotericsoftware.com/spine-unity-timeline) |
| Skeleton Flip Track | Flips a `SkeletonAnimation` or `SkeletonGraphic` skeleton | [Timeline](https://esotericsoftware.com/spine-unity-timeline) |

Older versions named these "Spine AnimationState Track", "Spine AnimationState
Graphic Track", and "Spine Skeleton Flip Track" — same components, renamed.

**Critical caveat**: `SkeletonMecanim` has no Timeline integration at all.
There is no track that targets it and no workaround short of switching the
component.

## Track parameters

| Parameter | Effect | Use when | Source |
|---|---|---|---|
| `Track Index` | Selects which `AnimationState` track index this Timeline track drives | More than one Timeline track drives the same skeleton | [Timeline](https://esotericsoftware.com/spine-unity-timeline) |
| `Unscaled Time` | Sets the target's `UnscaledTime` when clips start | A track must run on unscaled time independently of others | [Timeline](https://esotericsoftware.com/spine-unity-timeline) |

**Critical caveat**: order tracks with the base animation on top and overlay
tracks below it. Wrong ordering produces a plausible-looking result that mixes
the wrong layer on top.

## Clip parameters

| Parameter | Effect | Source |
|---|---|---|
| `Clip In` | Local start-time offset into the animation | [Timeline](https://esotericsoftware.com/spine-unity-timeline) |
| `Blend In Duration` | Adjusted by dragging the clip's edge | [Timeline](https://esotericsoftware.com/spine-unity-timeline) |
| `Speed Multiplier` | `2.0` double speed, `0.5` half speed | [Timeline](https://esotericsoftware.com/spine-unity-timeline) |
| `Don't Pause with Director` | Keeps playing while the Director is paused | [Timeline](https://esotericsoftware.com/spine-unity-timeline) |
| `Don't End with Clip` | Keeps playing past the clip end instead of setting an empty animation in the blank space after it | [Timeline](https://esotericsoftware.com/spine-unity-timeline) |
| `Clip End Mix Out Duration` | Mix duration into the empty animation following blank space; a negative value pauses instead of mixing out | [Timeline](https://esotericsoftware.com/spine-unity-timeline) |
| `Default Mix Duration` | Uses the `SkeletonData` asset's configured mix duration; disable it to supply a custom `Mix Duration` | [Timeline](https://esotericsoftware.com/spine-unity-timeline) |
| `Use Blend Duration` | Syncs `Mix Duration` to the Timeline clip's own blend length, so cross-fades are tuned in one place | [Timeline](https://esotericsoftware.com/spine-unity-timeline) |
| `Event Threshold`, `Attachment Threshold`, `Draw Order Threshold`, `Alpha` | Map directly onto `TrackEntry.EventThreshold`, `MixAttachmentThreshold`, `MixDrawOrderThreshold`, and `Alpha` — see [animation-state.md](animation-state.md) | [Timeline](https://esotericsoftware.com/spine-unity-timeline) |
| "Ease Out Duration", "Blend Curves" | **No effect** — present in the Inspector but ignored | [Timeline](https://esotericsoftware.com/spine-unity-timeline) |

## Setup

| Step | Action | Source |
|---|---|---|
| 1 | Add `SkeletonAnimationPlayableHandle` (or `SkeletonGraphicPlayableHandle`) to the target GameObject | [Timeline](https://esotericsoftware.com/spine-unity-timeline) |
| 2 | Right-click in the Timeline window → Spine → the track type | [Timeline](https://esotericsoftware.com/spine-unity-timeline) |
| 3 | Assign the skeleton GameObject as the track's binding | [Timeline](https://esotericsoftware.com/spine-unity-timeline) |
| 4 | Drag an `AnimationReferenceAsset` into the track to create a clip; duplicate with Ctrl/Cmd+D | [Timeline](https://esotericsoftware.com/spine-unity-timeline) |

## Runtime behaviour

| Behaviour | Consequence | Source |
|---|---|---|
| `SetAnimation()` fires at each clip's start | Using that clip's `AnimationReferenceAsset` | [Timeline](https://esotericsoftware.com/spine-unity-timeline) |
| Clip duration matters from Timeline 4.0 | In 3.8 an animation persisted across blank space regardless of clip length | [Timeline](https://esotericsoftware.com/spine-unity-timeline) |
| An unassigned clip calls `SetEmptyAnimation` | Blank clips mix out rather than doing nothing | [Timeline](https://esotericsoftware.com/spine-unity-timeline) |
| A missing animation reference is **silently ignored** | The previous animation keeps playing with no error — a common silent failure | [Timeline](https://esotericsoftware.com/spine-unity-timeline) |
| Pre-Timeline animation continues | Whatever was playing before the Timeline started runs until the first clip begins | [Timeline](https://esotericsoftware.com/spine-unity-timeline) |
| Edit-mode preview mixing differs from Play Mode | Always verify the real transition in Play Mode before shipping | [Timeline](https://esotericsoftware.com/spine-unity-timeline) |

## Skeleton Flip Track

| Aspect | Effect | Source |
|---|---|---|
| Clip parameters | `Flip X`, `Flip Y`, applied every frame for the clip's duration | [Timeline](https://esotericsoftware.com/spine-unity-timeline) |
| Setup | Same handle component, then Timeline → Spine → "Skeleton Flip Track", then right-click the dopesheet → "Add Spine Skeleton Flip Clip" | [Timeline](https://esotericsoftware.com/spine-unity-timeline) |
| End-of-playback restore | Reverts flip state to whatever was captured when playback started — **not** to an unflipped default | [Timeline](https://esotericsoftware.com/spine-unity-timeline) |

A harmless console error `"DrivenPropertyManager has failed to register
property 'm_Script'..."` is a documented Unity-side issue, not a Spine bug.

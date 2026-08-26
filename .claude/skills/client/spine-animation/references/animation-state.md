# AnimationState API — Tracks, Mixing, Events & Yield Instructions

Source: [spine-unity Main Components](https://esotericsoftware.com/spine-unity-main-components#Main-Components) (spine-unity v4.3+).
Covers: SKILL.md §4 — **"Never call `AnimationState.SetAnimation` every frame"**.

`AnimationState` holds the playing and queued animations and applies them to
the skeleton every update. Everything here is state that persists between
frames, which is why the single most common defect is calling into it as if it
were idempotent. The skeleton it applies to is
[skeleton-api.md](skeleton-api.md).

## Contents

- [Playing and queuing](#playing-and-queuing)
- [TrackEntry](#trackentry)
- [Events](#events)
- [Coroutine yield instructions](#coroutine-yield-instructions)

## Playing and queuing

| Call | Effect | Use when | Source |
|---|---|---|---|
| `SetAnimation(trackIndex, name, loop)` | Replaces what is on the track and restarts from frame 1 | An animation genuinely changes — **never per frame** | [Main Components](https://esotericsoftware.com/spine-unity-main-components) |
| `AddAnimation(trackIndex, name, loop, delay)` | Queues behind the current entry, after `delay` seconds | A follow-up should play without a second decision point | [Main Components](https://esotericsoftware.com/spine-unity-main-components) |
| `SetEmptyAnimation(trackIndex, mixDuration)` | Mixes the track out to nothing | Cleanly ending a layered or overlay animation | [Main Components](https://esotericsoftware.com/spine-unity-main-components) |
| `AddEmptyAnimation(trackIndex, mixDuration, delay)` | Queues that mix-out | The mix-out should follow the current entry | [Main Components](https://esotericsoftware.com/spine-unity-main-components) |
| `ClearTrack(trackIndex)` / `ClearTracks()` | Empties one track, or all of them | Resetting an instance, including before returning it to a pool | [Main Components](https://esotericsoftware.com/spine-unity-main-components) |
| `skeletonAnimation.timeScale` | Scales playback speed — `0.5f` half, `2f` double | Slow motion, speed-up, or freezing playback at `0f` | [Main Components](https://esotericsoftware.com/spine-unity-main-components) |

**Critical caveat**: `SetAnimation` restarts from frame 1 on every call, so
calling it each frame freezes the visible pose on frame 1 while reporting no
error. Track the current animation and call only on a change; hold a specific
frame with `TrackEntry.trackTime`.

```csharp
[SpineAnimation] public string walkAnimation = "walk";

private void OnMovementStarted()
{
    this.entry = this.skeletonAnimation.AnimationState.SetAnimation(0, this.walkAnimation, true);
}
```

## TrackEntry

| Property | What it decides | Source |
|---|---|---|
| Returned by `SetAnimation`/`AddAnimation` | Customizes one playback instance — `EventThreshold`, `TrackEnd`, `trackTime` | [Main Components](https://esotericsoftware.com/spine-unity-main-components) |
| Lifetime | Valid only until the animation is removed — never retain a reference past its `Dispose` event | [Main Components](https://esotericsoftware.com/spine-unity-main-components) |
| Per-entry delegates | The same six event kinds exist per entry, scoped to that playback instance rather than every animation | [Main Components](https://esotericsoftware.com/spine-unity-main-components) |

## Events

| Event | Fires when | Source |
|---|---|---|
| `Start` | The entry begins playing | [Main Components](https://esotericsoftware.com/spine-unity-main-components) |
| `Interrupt` | A new animation supersedes this one, or the track is cleared | [Main Components](https://esotericsoftware.com/spine-unity-main-components) |
| `End` | The entry finished without interruption; can repeat when looped | [Main Components](https://esotericsoftware.com/spine-unity-main-components) |
| `Complete` | A full cycle finished; fires repeatedly while looping | [Main Components](https://esotericsoftware.com/spine-unity-main-components) |
| `Dispose` | The entry is disposed — the reference must not outlive this | [Main Components](https://esotericsoftware.com/spine-unity-main-components) |
| `Event` | A user-defined Spine event fired | [Main Components](https://esotericsoftware.com/spine-unity-main-components) |

**Critical caveat**: interrupting a previous animation raises `Interrupt` and
`End`, never `Complete`. Logic hung on `Complete` silently stops running the
moment anything can interrupt that animation.

| Concern | Guidance | Source |
|---|---|---|
| Event comparison cost | Cache the `EventData` once via `Skeleton.Data.FindEvent("targetEvent")` and compare by reference, not by string, per `performance-and-algorithms.md`'s hot-path rules | [Main Components](https://esotericsoftware.com/spine-unity-main-components) |
| Changing state inside a callback | Callbacks fire during `SkeletonAnimation.Update()`, before the `LateUpdate()` mesh rebuild; calling `SetAnimation` from an `End` callback fires `Start` the same frame, and mixing can put the next `Start` before the previous `End` | [Main Components](https://esotericsoftware.com/spine-unity-main-components) |
| Enforcing order | Defer the follow-up one frame with a coroutine when strict ordering matters | [Main Components](https://esotericsoftware.com/spine-unity-main-components) |

```csharp
private void Awake()
{
    this.animationState = this.GetComponent<SkeletonAnimation>().AnimationState;
    this.animationState.Complete += this.OnSpineAnimationComplete;
    this.animationState.Event += this.OnUserDefinedEvent;
}

private void OnDestroy()
{
    this.animationState.Complete -= this.OnSpineAnimationComplete;
    this.animationState.Event -= this.OnUserDefinedEvent;
}

private void OnUserDefinedEvent(Spine.TrackEntry trackEntry, Spine.Event raised)
{
    if (raised.Data == this.spawnBulletEvent)
    {
        this.SpawnBullet();
    }
}
```

## Coroutine yield instructions

| Instruction | Waits for | Source |
|---|---|---|
| `WaitForSpineAnimation(track, eventTypes)` | Any combination of `AnimationEventTypes` flags, e.g. `Complete \| End` | [Main Components](https://esotericsoftware.com/spine-unity-main-components) |
| `WaitForSpineAnimationComplete(track)` | That entry's `Complete` | [Main Components](https://esotericsoftware.com/spine-unity-main-components) |
| `WaitForSpineAnimationEnd(track)` | That entry's `End` | [Main Components](https://esotericsoftware.com/spine-unity-main-components) |
| `WaitForSpineEvent(state, "spawn bullet")` | A named user event; a cached `EventData` overload avoids the string comparison | [Main Components](https://esotericsoftware.com/spine-unity-main-components) |

**Critical caveat**: `WaitForSpineAnimationComplete` never returns when the
animation is interrupted, since interruption raises `End` instead. Wait on
`Complete | End` whenever interruption is possible.

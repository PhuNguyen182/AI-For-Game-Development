# AnimationState

Persistent state between frames; calls are not idempotent. Page: main-components.

| Call | Effect |
|---|---|
| `SetAnimation(track, name, loop)` | Replace the track, restart from frame 1 — **never per frame** (freezes the pose on frame 1, no error). Call on change; hold a frame with `TrackEntry.trackTime` |
| `AddAnimation(track, name, loop, delay)` | Queue behind the current entry |
| `SetEmptyAnimation(track, mixDuration)` / `AddEmptyAnimation(track, mixDuration, delay)` | Mix the track out (now / queued) |
| `ClearTrack(i)` / `ClearTracks()` | Empty one / all tracks (also before pooling) |
| `skeletonAnimation.timeScale` | Speed; `0f` freezes |

## TrackEntry
Returned by `SetAnimation`/`AddAnimation`: per-playback `EventThreshold`, `TrackEnd`, `trackTime`, and the same six events scoped to that entry. Valid only until removed — drop the reference at its `Dispose`.

## Events
| Event | Fires |
|---|---|
| `Start` | entry begins |
| `Interrupt` | superseded by a new animation, or track cleared |
| `End` | entry finished or was interrupted; can repeat when looped |
| `Complete` | a full cycle finished; repeats while looping |
| `Dispose` | entry disposed |
| `Event` | a user-defined Spine event |

- Interruption raises `Interrupt` and `End`, never `Complete`: logic on `Complete` stops running once something can interrupt.
- Cache `Skeleton.Data.FindEvent("name")` and compare `raised.Data` by reference, not string.
- Callbacks fire during `SkeletonAnimation.Update()`, before the `LateUpdate()` mesh rebuild. `SetAnimation` inside an `End` callback fires `Start` the same frame, and mixing can order the next `Start` before the previous `End`; defer the follow-up one frame with a coroutine when order matters.
- Subscribe in `Awake`, unsubscribe in `OnDestroy`.

## Coroutine yields
- `WaitForSpineAnimation(track, eventTypes)` — `AnimationEventTypes` flags, e.g. `Complete | End`.
- `WaitForSpineAnimationComplete(track)` — never returns if interrupted; wait on `Complete | End` when interruption is possible.
- `WaitForSpineAnimationEnd(track)`.
- `WaitForSpineEvent(state, "name")` — a cached `EventData` overload avoids the string compare.

# Transform Sync and Latency — NetworkTransform, Interpolation, Anticipation, Ticks

Sources: [a] manual/components/helper/networktransform.html, [b] api/Unity.Netcode.Components.NetworkTransform.html, [c] manual/components/helper/networkanimator.html, [d] manual/components/helper/networkrigidbody.html, [e] manual/advanced-topics/physics.html, [f] manual/components/helper/attachablebehaviour.html, [g] manual/components/helper/componentcontroller.html, [h] manual/advanced-topics/client-anticipation.html, [i] manual/advanced-topics/networktime-ticks.html, [j] api/Unity.Netcode.NetworkTimeSystem.html, [k] manual/learn/clientside-interpolation.html, [l] manual/learn/dealing-with-latency.html.

## NetworkTransform defaults

| Property | Default | Fact |
|---|---|---|
| `PositionThreshold` | `0.001` | Smaller deltas are not sent |
| `RotAngleThreshold` / `ScaleThreshold` | `0.01` / `0.01` | Same, per rotation angle / scale |
| `Interpolate` | `true` | Smooth vs snap on receivers |
| `UseUnreliableDeltas` | `true` per API; the manual says disabled — read the Inspector before relying on it | Unreliable-sequenced deltas; off = reliable fragmented sequenced for every update; exclusive with `SwitchTransformSpaceWhenParented` |
| `InLocalSpace` | `false` | World vs local space |
| `SyncPositionX/Y/Z`, `SyncRotAngleX/Y/Z`, `SyncScaleX/Y/Z` | all `true` | Per-axis opt-out; rotation axes vanish once `UseQuaternionSynchronization` is on |
| `AutoOwnerAuthorityTickOffset` | `true` | Tick-offset compensation in owner mode |
| `InterpolationBufferTickOffset` (static) | `1` tick + tick latency | Buffer interpolation holds behind the newest state |
| `NetworkConfig.TickRate` | `30` Hz | Send baseline [a] |
| `AuthorityModes` | `Server` | `Owner` = owner pushes; Distributed Authority forces `Owner` on every `NetworkTransform` |

| `InterpolationTypes` | Behaviour |
|---|---|
| `LegacyLerp` | Lerp between states, optional 2nd-phase lerp by `deltaTime / maxInterpolationTime`; loses precision on sharp turns |
| `Lerp` | Keeps time-to-target under `InterpolationBufferTickOffset` at high tick latency; smoothing `1.0 - maxInterpolationTime` |
| `SmoothDampening` | Smooth-damps by accumulated delta vs time-to-target; smooth at lower precision |

| Precision | Bytes per rotation | Fact |
|---|---|---|
| Full (default) | 16 | Lossless |
| `UseHalfFloatPrecision` | 8 | Position, rotation, scale as half floats (`HalfVector3`, 6 bytes for 3 axes) |
| `UseQuaternionCompression` | 4 | Smallest-three into a `uint`; overrides half-float for rotation; slight loss |

**Caveat:** half-float position (`NetworkDeltaPosition`) caps the per-update delta at 64 world units — 1,920 units/s at 30 Hz. Faster objects need a higher tick rate or full precision, or the delta silently misbehaves [a].

| Gotcha | Fact |
|---|---|
| Runtime change teleports | Changing `UseUnreliableDeltas`, `InLocalSpace`, `Interpolate`, `SlerpPosition`, `UseQuaternionSynchronization`, `UseQuaternionCompression` or `UseHalfFloatPrecision` resyncs and resets interpolation |
| Periodic resync | Full axial resync once per second, even with unreliable deltas |
| `UseUnreliableDeltas` + `SwitchTransformSpaceWhenParented` | Mutually exclusive — the latter needs reliable deltas |
| Nested `NetworkTransform`s | Costly at many instances — prefer `NetworkAnimator` or a time-based algorithm |
| Spawn-time parenting | Set it in an overridden `OnNetworkSpawn()` **before** `base.OnNetworkSpawn()` |
| Owner-authoritative spawn | Spawn under server authority, then transfer ownership — avoids a latency glitch |
| Placement | On the `NetworkObject`'s GameObject or any descendant; one `NetworkObject` anchors many `NetworkTransform`s |

## NetworkAnimator

| Fact | Detail |
|---|---|
| Syncs | Parameters, states, transitions, deltas per frame; `Animator` may be root or child. Late joiners get state, **not** triggers already fired |
| `AuthorityMode` | `Server` (default): owner's own actions lag one RTT. `Owner`: instant locally, others lag one RTT. `OnIsServerAuthoritative()` override beats the Inspector |
| Triggers | `NetworkAnimator.SetTrigger(string)` / `SetTrigger(int hash, bool = true)`, `ResetTrigger`; `Animator.SetTrigger()` breaks sync |
| Per-parameter opt-out | `EnableParameterSynchronization(name or hash, bool)` at runtime; Inspector **Animator Parameter Entries** statically |

## NetworkRigidbody / NetworkRigidbody2D

Simulates only on the authority; every other instance is kinematic and follows `NetworkTransform`, which must sit on the same GameObject (the rigidbody component does no wire sync).

| Member | Default | Fact |
|---|---|---|
| `UseRigidBodyForMotion` | `false` | `true` = read pose from physics in `FixedUpdate` instead of `Transform` |
| `AutoUpdateKinematicState` | `true` | Flips kinematic by authority; off only for custom handling |
| `AutoSetKinematicOnDespawn` | — | Kinematic on despawn, for pooling |
| `MovePosition`/`MoveRotation` vs `SetPosition`/`SetRotation` | — | Smooth vs teleport |
| `AttachToFixedJoint()` / `DetachFromFixedJoint()` | — | Authority-only joint between two bodies |

**Caveat:** `UseUnreliableDeltas` with `UseRigidBodyForMotion` degrades interpolation [d]. Inbound Rpcs and `NetworkVariable` callbacks run in `EarlyUpdate`, before that frame's physics step; mutating Rigidbody state there jitters — apply it after `FixedUpdate` [e].

## Attachables, ComponentController, contacts

| Fact | Detail |
|---|---|
| `AttachableBehaviour.Attach(AttachableNode)` / `Detach()` | Parent/child without `NetworkObject` reparenting or nested-`NetworkTransform` cost; both sides spawned; `Detach()` restores the prior parent |
| `AutoDetach` flags | `OnOwnershipChanged`, `OnDespawn`, `OnAttachNodeDestroy` |
| `AttachStateChange` / `OnAttachStateChanged()` / `OnHasAuthority()` | Attach-state hook; authority override |
| `AttachableNode` Detach On Despawn | Default `true`: detaches (and destroys) attached behaviours when the node despawns |
| `ComponentController` | Enables components by authority state, e.g. an avatar shown only to its owner |
| ComponentController entries | **Auto Trigger**; **Enable On Attach** (default: off while attached, on while detached) |
| `ComponentController.SetEnabled(bool)` | Authority only; honours each entry's `InvertEnabled` |
| `EnableDelay` / `DisableDelay` | Default `0` s, synced; ignored when an `AttachableNode` is destroyed [g] |
| ComponentController transport | RPC-driven field, not `NetworkVariable`, for attach/detach ordering |
| `RigidbodyContactEventManager.Instance.RegisterHandler(IContactEventHandler, bool)` | Central contact dispatch; each collider needs `providesContacts` |
| `IContactEventHandler` | `ContactEvent(ulong eventId, Vector3 averagedCollisionNormal, Rigidbody collidingBody, Vector3 contactPoint, bool hasCollisionStay = false, Vector3 averagedCollisionStayNormal = default)`, `Rigidbody GetRigidbody()` |
| Child colliders | Parented under a networked Rigidbody, they count toward its collisions [e] |
| Physics parenting | `AttachableBehaviour` for most; Joints when the child needs its own velocity or sibling interaction |

## Interpolation and anticipation

| Fact | Detail |
|---|---|
| Lag compensation (server rewind) | Not implemented in NGO [l] |
| `BufferedLinearInterpolator<T>.MaximumInterpolationTime` | `0.016`–`1`; 2nd-phase smoothing divisor. The API warns the dual lerp can over-smooth |
| `AddMeasurement` / `Update` / `ResetTo` / `Clear` | Queue, advance, reset at a server time (teleport), full reset |
| Anticipation model | Anticipate-and-correct only — no rollback-and-replay; full prediction is "advanced users only" [h] |
| `Value`/`AnticipatedState` vs `AuthoritativeValue`/`AuthoritativeState` | Client-visual vs server truth (writable with permission, updated at frame end on the server) |
| `Anticipate(T)`, `AnticipateMove/Rotate/Scale`, `AnticipateState(TransformState)` | Set the visual value; confirmation expected within one RTT |
| `PreviousAnticipatedValue` / `PreviousAnticipatedState` | Last anticipation, kept across server updates |
| `StaleDataHandling` | `Ignore` (default) or `Reanticipate` when a server value is older than the anticipation |
| `ShouldReanticipate`; `NetworkBehaviour.OnReanticipate(double lastRoundTripTime)` / `NetworkManager.OnReanticipate` | Conflict flag and callbacks — where manual rollback/replay goes |
| `Smooth(from, to, durationSeconds, delegate)` | Client smooths the transform, server only the visual state; needs e.g. `Mathf.Lerp` |

**Caveat:** anticipation costs a `StaleDataHandling` choice, `OnReanticipate` logic and `AnticipationCounter`/`ShouldReanticipate` bookkeeping; plain interpolated `NetworkTransform` already hides RTT/2. Escalate only after a measured, visible correction snap.

## Ticks, time, update loop

| Fact | Detail |
|---|---|
| Physics alignment | With `FixedUpdate`/physics, set the tick rate equal to the fixed update rate [i] |
| Update rate vs tick rate | A client update rate below the server tick rate wastes the higher tick; a weapon firing faster than the update rate bundles hits into one update ("super bullets") |
| `NetworkTickSystem.Tick` | Fires once per tick, **before** `NetworkVariable` changes are collected |
| `NetworkTickSystem.NoTick` | `-2147483648` = no tick info |
| `NetworkTime.Tick`, `TickRate`, `Time`/`TimeAsFloat`, `FixedTime`, `TickOffset`, `TickWithPartial` | `FixedDeltaTime` = `1.0 / TickRate`, constant per session |
| `LocalTime` vs `ServerTime` | `LocalTime` runs ahead — client-authoritative/predicted objects. `ServerTime` — server-authoritative objects and interpolation; `NetworkTransform` keys off it |
| `NetworkTimeSystem.ServerBufferSec` | Default **0.05 s** client buffer; higher = more latency, smoother [j] |
| `LocalBufferSec` / `TickLatency` | Server-side buffer for client messages / averaged latency in ticks |
| `AdjustmentRatio` / `HardResetThresholdSec` | Drift-correction speed / threshold past which time hard-resets |

| `NetworkUpdateStage` (order) | Runs |
|---|---|
| 1 `Initialization` | First update of the frame |
| 2 `EarlyUpdate` | **Inbound messages**: Rpcs, `NetworkVariable` callbacks |
| 3 `FixedUpdate` | Physics, state machines, animation |
| 4 `PreUpdate` / 5 `Update` | Before / with `MonoBehaviour.Update()`; `Update` is the `RegisterNetworkUpdate` default |
| 6 `PreLateUpdate` / 7 `PostLateUpdate` | Before / after `LateUpdate()`; **7 processes dirty `NetworkVariable`s and sends** |
| 8 `PostScriptLateUpdate` | After `LateUpdate()`, before rendering. `Unset` is not a stage |

| Custom system API | Fact |
|---|---|
| `INetworkUpdateSystem.NetworkUpdate(NetworkUpdateStage)` | Called once per registered stage |
| `NetworkUpdateLoop.RegisterNetworkUpdate(system, stage = Update)` | One stage |
| `RegisterAllNetworkUpdates` / `UnregisterNetworkUpdate` / `UnregisterAllNetworkUpdates` | All stages / remove |
| `NetworkUpdateLoop.UpdateStage` (static) | Stage currently executing |

Unverified: [k] is read as "the interpolation delay must stay shorter than the server send interval, else the buffer starves" — that contradicts the usual rule that the buffer must cover at least one send interval; confirm before tuning `InterpolationBufferTickOffset`.

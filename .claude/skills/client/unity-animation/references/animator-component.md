# Animator Component

Sources: `https://docs.unity3d.com/Manual/class-Animator.html`, `https://docs.unity3d.com/ScriptReference/Animator.html`, and sub-pages (see [root-links.md](root-links.md)).

## What it is
`Animator` is the MonoBehaviour that drives a GameObject's animation playback using an assigned Animator Controller (and, for humanoid characters, an Avatar). It lives in `Game.Client.*` — it is a Unity engine type and must never be referenced from `Game.Core.*`, per `coding-principles.md`'s Shared Core integrity rule.

## Inspector fields

| Field | Description |
|---|---|
| `Controller` | The Animator Controller asset that "defines which animation clips to use, and controls when and how to blend and transition between them." See [animator-controller.md](animator-controller.md). |
| `Avatar` | The Avatar for this character, used only if the Animator is animating a Humanoid character. See [avatar-setup.md](avatar-setup.md). |
| `Apply Root Motion` | Whether position/rotation is driven by animation curve data or by script. Shows `Handled by Script` automatically once `OnAnimatorMove` is implemented on the same GameObject. |
| `Update Mode` | `Normal` — updates in-sync with `Update()`, speed follows current timescale. `Animate Physics` — updates in-sync with `FixedUpdate()` (lock-step with physics). `Unscaled Time` — updates in-sync with `Update()` but ignores timescale. |
| `Culling Mode` | `Always Animate` — no culling when offscreen. `Cull Update Transforms` — retargeting, IK, and Transform writes are disabled when renderers aren't visible. `Cull Completely` — animation evaluation is fully disabled when renderers aren't visible. |

**Performance note (directly relevant to this project's rules):** `Culling Mode` should virtually never be left at `Always Animate` for characters that can go off-screen — per `performance-and-algorithms.md`, set `Animator`'s Culling Mode to "Cull Update Transforms" or "Based On Renderers" (`Cull Completely` for the strongest saving) so off-screen characters skip animation evaluation entirely instead of paying for it unseen. `Cull Completely` is the cheapest option but means the character's Transforms freeze while offscreen (state resumes visually on becoming visible again) — pick based on whether resumed-state pop is acceptable for that character type. See [performance-and-faq.md](performance-and-faq.md) for the full optimization guidance.

### IK Pass (per-layer, not a top-level Animator field)
IK is enabled per-layer, not on the `Animator` component directly: Animator window → **Layers** pane → cog icon on a layer → enable **IK Pass**. This causes Unity to invoke `OnAnimatorIK()` during that layer's evaluation. See [avatar-setup.md](avatar-setup.md)'s Inverse Kinematics section.

## Key scripting API (`UnityEngine.Animator`)

### Playback control
| Member | Signature | Description |
|---|---|---|
| `Play` | `Play(string stateName, int layer = -1, float normalizedTime = float.NegativeInfinity)` | Plays a state immediately (hard cut, no blend). |
| `PlayInFixedTime` | `PlayInFixedTime(string stateName, int layer = -1, float fixedTime = 0f)` | Same as `Play`, but the time argument is in seconds instead of normalized time. |
| `CrossFade` | `CrossFade(string stateName, float transitionDuration, int layer = -1, float normalizedTime = float.NegativeInfinity)` | Crossfades from the current state to any other state, using normalized time. |
| `CrossFadeInFixedTime` | `CrossFadeInFixedTime(string stateName, float transitionDuration, int layer = -1, float fixedTime = 0f)` | Same as `CrossFade`, but using seconds instead of normalized time. |

### Parameters
| Member | Description |
|---|---|
| `SetFloat(string name, float value)` / `SetFloat(int hash, float value)` | Sends a float value to affect transitions/blend trees. |
| `SetBool(string name, bool value)` / `SetBool(int hash, bool value)` | Sets a bool parameter. |
| `SetInteger(string name, int value)` / `SetInteger(int hash, int value)` | Sets an int parameter. |
| `SetTrigger(string name)` / `SetTrigger(int hash)` | Sets a trigger parameter (auto-resets once consumed by a transition). |
| `ResetTrigger(string name)` / `ResetTrigger(int hash)` | Manually resets a trigger without it firing a transition. |
| `GetFloat` / `GetBool` / `GetInteger` (string or hash overloads) | Reads back the current parameter value. |
| `Animator.StringToHash(string name)` | Generates an int parameter id from a string, for the hashed overloads above. |

**Performance note:** per `coding-principles.md` / `performance-and-algorithms.md`, cache the result of `Animator.StringToHash` once (e.g. a `static readonly int` field) and always call the `int`-hash overloads of `SetFloat`/`SetBool`/`SetTrigger`/`SetInteger` in hot paths — the string overloads re-hash the parameter name on every single call.

```csharp
private static readonly int SpeedHash = Animator.StringToHash("Speed");
// ...
this._animator.SetFloat(SpeedHash, currentSpeed);
```

### State/layer inspection
| Member | Description |
|---|---|
| `GetCurrentAnimatorStateInfo(int layerIndex)` | Returns an `AnimatorStateInfo` describing the currently playing state on that layer. |
| `GetNextAnimatorStateInfo(int layerIndex)` | Returns an `AnimatorStateInfo` for the state being transitioned into, if any. |
| `IsInTransition(int layerIndex)` | Whether the given layer is currently mid-transition. |
| `layerCount` | Number of layers on the controller. |
| `GetLayerWeight(int layerIndex)` / `SetLayerWeight(int layerIndex, float weight)` | Read/write a layer's blend weight at runtime. |

### Other key properties
| Member | Description |
|---|---|
| `runtimeAnimatorController` | The runtime `RuntimeAnimatorController` driving this Animator — assigning an `AnimatorOverrideController` here is how skin/weapon-variant clip swapping is applied at runtime (see [animator-override-controller.md](animator-override-controller.md)). |
| `applyRootMotion` | Bool; whether root motion is applied. |
| `updateMode` | Mirrors the `Update Mode` Inspector field. |
| `cullingMode` | Mirrors the `Culling Mode` Inspector field. |
| `avatar` | Get/set the current Avatar. |
| `gravityWeight` | Current gravity weight derived from the playing animation's root-motion Y-axis bake settings. |

### IK scripting members (used inside `OnAnimatorIK`)
`SetIKPositionWeight`, `SetIKRotationWeight`, `SetIKPosition`, `SetIKRotation`, `SetLookAtPosition`, `bodyPosition`, `bodyRotation` — target limbs via `AvatarIKGoal` (e.g. `AvatarIKGoal.RightHand`).

## Root motion / IK callbacks (MonoBehaviour messages, not `Animator` methods)
| Callback | Fires when | Typical use |
|---|---|---|
| `OnAnimatorMove()` | After animation evaluation, when root motion needs to be applied. | Manually apply computed motion to `transform.position`/`transform.rotation` — required whenever a clip is authored "in place" and movement is script-driven instead of baked into the animation. |
| `OnAnimatorIK(int layerIndex)` | During the IK pass, only if that layer has **IK Pass** enabled. | Set IK goal positions/weights for hands, feet, look-at, etc. |

## Practical guidance
- Never call `GetComponent<Animator>()` inside `Update()`/hot paths — cache it once (e.g. in `Awake()`), per `coding-principles.md`.
- Always use the hashed (`int`) overloads of `SetFloat`/`SetBool`/`SetTrigger`/`SetInteger` with a cached `Animator.StringToHash` result — never the raw string overloads in a per-frame call.
- Set `Culling Mode` deliberately per character type instead of leaving the default — this is a direct, low-effort win against the project's per-frame budget for any character that can go offscreen.
- `Update Mode = Animate Physics` is the correct choice whenever root motion or IK needs to stay in lock-step with the physics tick (e.g. a character whose movement also depends on `FixedUpdate`-driven physics); otherwise `Normal` is the default.
- Keep the *decision* of what an IK/root-motion outcome means for gameplay in `Game.Core.*` — the `OnAnimatorMove`/`OnAnimatorIK` Unity callbacks themselves, and any `Animator`/`AvatarIKGoal` calls, must stay in `Game.Client.*` (see `coding-principles.md`'s Shared Core integrity rule).
- Swapping the visual skin/weapon of a character without touching the state machine is done by assigning an `AnimatorOverrideController` to `runtimeAnimatorController`, not by editing `Controller` — see [animator-override-controller.md](animator-override-controller.md).

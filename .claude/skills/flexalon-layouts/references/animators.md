# Animators

Pages: `/docs/animators`, `/docs/customAnimators`, API `TransformUpdater`, `FlexalonCurveAnimator`, `FlexalonLerpAnimator`, `FlexalonRigidBodyAnimator`.

An animator is a `TransformUpdater`: the Update Transforms stage, the only one that writes the transform. Without one the object snaps. Animators only carry an object to its layout result; arbitrary tweens belong to `dotween-tweening`/`litmotion-tweening`.

| Animator | Mechanism | Correct when | Wrong when |
|---|---|---|---|
| `FlexalonCurveAnimator` | `AnimationCurve` (0 to 1), restarted on every result change | Rare discrete changes (swap, insert) | Result changes each frame: restarts forever |
| `FlexalonLerpAnimator` | Interpolates toward the result, faster as the gap widens | Constantly moving target (constraint chain, dragged layout) | An authored easing shape is required |
| `FlexalonRigidBodyAnimator` | Applies forces to the `Rigidbody`/`Rigidbody2D` | Object has a rigid body (mandatory then: otherwise physics and pipeline jitter) | No rigid body |

| Property | On | Decides |
|---|---|---|
| `AnimatePosition/Rotation/Scale` | Curve, Lerp | Channels animated; others snap |
| `AnimateInWorldSpace` | Curve, Lerp | Use local space when the parent itself moves |
| `Curve` | Curve | Shape |
| `InterpolationSpeed` | Lerp | Fraction per frame times `Time.deltaTime` |
| `PositionForce`, `RotationForce` | Rigid Body | Force per frame toward the result |
| `ScaleInterpolationSpeed` | Rigid Body | Scale is interpolated, not forced |

## `TransformUpdater`
- `PreUpdate(FlexalonNode)`: capture the current transform.
- `UpdatePosition/UpdateRotation/UpdateScale(FlexalonNode, value)`: move toward the computed local value. Return `true` to be called again next frame, `false` to stop until the result changes.
- `UpdateRectSize(FlexalonNode, Vector2)`: the uGUI channel; ignoring it leaves UI unsized while animating.
- Register with `FlexalonNode.SetTransformUpdater`.

Returning `true` keeps the node updating every frame, so a custom updater must return `false` on arrival (compare squared distances).

## Animating the layout instead
Driving a layout property with a Unity `Animator` (e.g. `FlexalonCurveLayout.StartAt`) moves every child, but the whole subtree re-measures and re-arranges each frame the property changes. Use for the formation as a whole traveling; use animator components when objects enter, leave or swap. Profile the first.

# Animators — moving objects to their layout result

Sources: [Animators](https://www.flexalon.com/docs/animators), [Custom Animators](https://www.flexalon.com/docs/customAnimators), [Interface TransformUpdater](https://www.flexalon.com/docs/api/Flexalon.TransformUpdater.html), [Class FlexalonCurveAnimator](https://www.flexalon.com/docs/api/Flexalon.FlexalonCurveAnimator.html), [Class FlexalonLerpAnimator](https://www.flexalon.com/docs/api/Flexalon.FlexalonLerpAnimator.html), [Class FlexalonRigidBodyAnimator](https://www.flexalon.com/docs/api/Flexalon.FlexalonRigidBodyAnimator.html).
Covers: SKILL.md §4 — **"Choose the animator by how often the layout result changes"**.

An animator is a `TransformUpdater`: the pipeline's Update Transforms
stage, the only stage that writes the transform. Without one the object snaps to its result. These are
not general-purpose tweens — they only carry an object from where it is to
where layout says it should be; arbitrary timed interpolation belongs to
`dotween-tweening`/`litmotion-tweening`.

## Choosing one — by how often the result changes

| Animator | Mechanism | Correct when | Wrong when | Source |
|---|---|---|---|---|
| `FlexalonCurveAnimator` | Applies an `AnimationCurve`, **restarted every time the layout result changes** | Results change rarely and discretely — a drag-and-drop swap, an item inserted into a list | The result changes every frame: the curve restarts each frame and never progresses | [Animators](https://www.flexalon.com/docs/animators) |
| `FlexalonLerpAnimator` | Interpolates continuously from the current position toward the result, speeding up as the gap widens | The target moves constantly — a chain of constrained objects, a layout being dragged | A precise, authored easing shape is required; lerp has no curve | [Animators](https://www.flexalon.com/docs/animators) |
| `FlexalonRigidBodyAnimator` | Applies **forces** to the `Rigidbody`/`Rigidbody2D` instead of writing the transform | The object has a rigid body at all | There is no rigid body — the other two are cheaper and exact | [Animators](https://www.flexalon.com/docs/animators) |

**Critical caveat**: a `Rigidbody` or `Rigidbody2D` on a Flexalon-managed
object makes physics and the pipeline compete for the same transform every
frame. `FlexalonRigidBodyAnimator` is the documented resolution, and it is
not optional styling — without it the object jitters between the two writers.

## Shared properties

| Property | Present on | What it decides | Source |
|---|---|---|---|
| `AnimatePosition`, `AnimateRotation`, `AnimateScale` (`bool`) | Curve, Lerp | Which channels the animator owns. A channel left off snaps instead of animating — the way to animate position while size updates instantly | [Class FlexalonCurveAnimator](https://www.flexalon.com/docs/api/Flexalon.FlexalonCurveAnimator.html) |
| `AnimateInWorldSpace` (`bool`) | Curve, Lerp | World space, or local space. **Use local space when the parent is itself moving or animating** and parent and child must stick together | [Animators](https://www.flexalon.com/docs/animators) |
| `Curve` (`AnimationCurve`) | Curve | The shape applied; it "should begin at 0 and end at 1" | [Class FlexalonCurveAnimator](https://www.flexalon.com/docs/api/Flexalon.FlexalonCurveAnimator.html) |
| `InterpolationSpeed` (`float`) | Lerp | Fraction interpolated per frame, **multiplied by `Time.deltaTime`** | [Class FlexalonLerpAnimator](https://www.flexalon.com/docs/api/Flexalon.FlexalonLerpAnimator.html) |
| `PositionForce`, `RotationForce` (`float`) | Rigid Body | Force applied per frame toward the layout position/rotation | [Class FlexalonRigidBodyAnimator](https://www.flexalon.com/docs/api/Flexalon.FlexalonRigidBodyAnimator.html) |
| `ScaleInterpolationSpeed` (`float`) | Rigid Body | Scale is interpolated, not forced — physics has no scale channel | [Class FlexalonRigidBodyAnimator](https://www.flexalon.com/docs/api/Flexalon.FlexalonRigidBodyAnimator.html) |

## `TransformUpdater` — the interface behind all three

| Member | Contract | Source |
|---|---|---|
| `PreUpdate(FlexalonNode)` | Called before the layout system updates any transform — capture the current transform here | [Interface TransformUpdater](https://www.flexalon.com/docs/api/Flexalon.TransformUpdater.html) |
| `UpdatePosition(FlexalonNode, Vector3)` | Move toward the computed **local** position. **Return `true` to be called again next frame**; return `false` to stop until the result changes | [Custom Animators](https://www.flexalon.com/docs/customAnimators) |
| `UpdateRotation(FlexalonNode, Quaternion)` | Same contract, for local rotation | [Custom Animators](https://www.flexalon.com/docs/customAnimators) |
| `UpdateScale(FlexalonNode, Vector3)` | Same contract, for local scale | [Custom Animators](https://www.flexalon.com/docs/customAnimators) |
| `UpdateRectSize(FlexalonNode, Vector2)` | Same contract, for a `RectTransform`'s rect — the uGUI channel, see [ugui-integration.md](ugui-integration.md) | [Interface TransformUpdater](https://www.flexalon.com/docs/api/Flexalon.TransformUpdater.html) |
| `FlexalonNode.SetTransformUpdater(TransformUpdater)` | Registers a custom updater for a node | [Custom Animators](https://www.flexalon.com/docs/customAnimators) |

**The return value is the cost model.** Returning `true` keeps the node
updating every frame; a Lerp animator that never quite reaches its target
keeps its subtree live indefinitely. A custom updater must return `false`
once it has arrived — see [core-concepts-and-pipeline.md](core-concepts-and-pipeline.md).

```csharp
using UnityEngine;
using Flexalon;

namespace Game.Client.Layout
{
    // Snaps rotation and scale, eases position, and stops once it arrives.
    public class SnapToLayoutUpdater : MonoBehaviour, TransformUpdater
    {
        private const float ArrivalThreshold = 0.001f;

        public void PreUpdate(FlexalonNode node)
        {
        }

        public bool UpdatePosition(FlexalonNode node, Vector3 position)
        {
            Transform t = this.transform;
            t.localPosition = Vector3.Lerp(t.localPosition, position, 10f * Time.deltaTime);
            return (t.localPosition - position).sqrMagnitude > (ArrivalThreshold * ArrivalThreshold);
        }

        public bool UpdateRotation(FlexalonNode node, Quaternion rotation)
        {
            this.transform.localRotation = rotation;
            return false;
        }

        public bool UpdateScale(FlexalonNode node, Vector3 scale)
        {
            this.transform.localScale = scale;
            return false;
        }

        public bool UpdateRectSize(FlexalonNode node, Vector2 rect)
        {
            return false;
        }
    }
}
```

The arrival test compares squared distances rather than calling
`Vector3.Distance`, per `performance-and-algorithms.md`'s Core principle
section — this method runs every frame the node is animating.

## Animating layout properties instead of objects

A second, distinct technique: drive a **layout's own property** with a
standard Unity `Animator` and let the pipeline move every child as a
consequence. The documented example animates `FlexalonCurveLayout.StartAt` to
sweep objects along a curve (see [radial-curve-and-shape-layouts.md](radial-curve-and-shape-layouts.md)).

| Aspect | Animating objects (animator component) | Animating the layout (Unity `Animator`) | Source |
|---|---|---|---|
| What moves | Each object toward its own result | The arrangement itself; every child follows | [Animators](https://www.flexalon.com/docs/animators) |
| Cost | Only nodes still animating stay live | The whole subtree re-measures and re-arranges every frame the property changes | [Animators](https://www.flexalon.com/docs/animators) |
| Use when | Objects enter, leave, or swap places | The formation as a whole must travel, rotate, or breathe | [Animators](https://www.flexalon.com/docs/animators) |

Both are legitimate; the second is the one to profile before shipping, per
`performance-and-algorithms.md`'s Verification section.

# Joints 2D — The Nine Constraints, Motors, Limits & Breaking

Sources: [2D Joints](https://docs.unity3d.com/Manual/2d-physics/joints/2d-joints-landing.html), [Introduction to 2D joints](https://docs.unity3d.com/Manual/2d-physics/joints/introduction-to-2d-joints.html), [2D joint constraints](https://docs.unity3d.com/Manual/2d-physics/joints/2d-joint-constraints.html).
Covers: SKILL.md §4 — **"Choose the joint by the constraint the design states, not by generality"**.

A `Joint2D` connects a `Rigidbody2D` to another body, or to a fixed world
position when `connectedBody` is left empty. Joints work by applying corrective
forces when their constraint is violated, and the solver corrects
*gradually* — which is why a loaded joint visibly stretches or lags, and why a
large external force can fight the joint rather than being absorbed by it.

## Contents

- [Choosing a joint](#choosing-a-joint)
- [Shared base properties](#shared-base-properties)
- [Motors and limits](#motors-and-limits)

## Choosing a joint

| Joint | What it decides | Source |
|---|---|---|
| `DistanceJoint2D` | Holds a set distance with a very stiff spring and no rotational force. `maxDistanceOnly` off is a rigid link like a spoke; on, the body moves freely inside the radius and only pulls taut at the limit, like a rope | [Distance Joint 2D](https://docs.unity3d.com/Manual/2d-physics/joints/distance-joint-2d-fundamentals.html) |
| `FixedJoint2D` | Holds relative position *and* rotation via a maximally stiff spring — so unlike Transform parenting, a little give remains and the link can be broken | [Fixed Joint 2D](https://docs.unity3d.com/Manual/2d-physics/joints/fixed-joint-2d-fundamentals.html) |
| `FrictionJoint2D` | Drives relative linear and angular velocity toward zero with a low-power motor — damping between two bodies, not a surface property | [Friction Joint 2D](https://docs.unity3d.com/Manual/2d-physics/joints/friction-joint-2d-fundamentals.html) |
| `HingeJoint2D` | One shared rotation pivot, with an optional motor and angle limits — doors, seesaws, driven wheels | [Hinge Joint 2D](https://docs.unity3d.com/Manual/2d-physics/joints/hinge-joint-2d-fundamentals.html) |
| `SliderJoint2D` | Constrains motion to a line at a chosen angle, with an optional motor and translation limits — lifts, sliding doors | [Slider Joint 2D](https://docs.unity3d.com/Manual/2d-physics/joints/slider-joint-2d-fundamentals.html) |
| `SpringJoint2D` | Elastic distance constraint with frequency and damping — visibly stretches and oscillates, which is the difference from Distance | [Spring Joint 2D](https://docs.unity3d.com/Manual/2d-physics/joints/spring-joint-2d-fundamentals.html) |
| `WheelJoint2D` | A suspension line plus a rotation pivot in one component, with a motor — vehicle wheels, where a Slider and Hinge pair would fight each other | [Wheel Joint 2D](https://docs.unity3d.com/Manual/2d-physics/joints/wheel-joint-2d-fundamentals.html) |
| `TargetJoint2D` | Pulls **one** body toward a moving world-space point with a spring — dragging, tractor beams. Has no `connectedBody` and no anchors | [Target Joint 2D](https://docs.unity3d.com/Manual/2d-physics/joints/target-joint-2d-fundamentals.html) |
| `RelativeJoint2D` | Maintains a linear and angular offset between two bodies using a motor rather than a spring — a following body that keeps station without being welded | [Relative Joint 2D](https://docs.unity3d.com/Manual/2d-physics/joints/relative-joint-2d-fundamentals.html) |

**Critical caveat**: `RelativeJoint2D` and `TargetJoint2D` derive from
`Joint2D` directly and therefore have **no** `anchor`/`connectedAnchor`. The
other seven derive from `AnchoredJoint2D` and pin to a local point on each
body. Code written against anchors does not generalise across all nine.

## Shared base properties

| Property | What it decides | Source |
|---|---|---|
| `connectedBody` | The other body, or empty to anchor to a fixed world position — the difference between a swinging rope and a rope tied to the sky | [Introduction to 2D joints](https://docs.unity3d.com/Manual/2d-physics/joints/introduction-to-2d-joints.html) |
| `enableCollision` | Whether the two connected bodies still collide with each other; off is what stops a jointed pair jittering against itself | [Introduction to 2D joints](https://docs.unity3d.com/Manual/2d-physics/joints/introduction-to-2d-joints.html) |
| `breakForce` / `breakTorque` | Thresholds past which the joint breaks; infinite by default, so a joint never breaks until this is set deliberately | [2D joint constraints](https://docs.unity3d.com/Manual/2d-physics/joints/2d-joint-constraints.html) |
| `breakAction` | What happens on break — destroy the component, disable it, or only notify | [2D joint constraints](https://docs.unity3d.com/Manual/2d-physics/joints/2d-joint-constraints.html) |
| `OnJointBreak2D` | The message raised on break; the hook that must exist if breaking is part of the design rather than an accident | [2D joint constraints](https://docs.unity3d.com/Manual/2d-physics/joints/2d-joint-constraints.html) |
| `anchor` / `connectedAnchor` (AnchoredJoint2D) | Local pin points on each body; `autoConfigureConnectedAnchor` derives the second from the current pose at setup time | [2D joint constraints](https://docs.unity3d.com/Manual/2d-physics/joints/2d-joint-constraints.html) |

## Motors and limits

| Structure | What it decides | Source |
|---|---|---|
| `JointMotor2D` | `motorSpeed` and `maxMotorTorque` — a motor drives *toward* a speed and is capped by torque, so an underpowered motor stalls rather than erroring | [Hinge Joint 2D](https://docs.unity3d.com/Manual/2d-physics/joints/hinge-joint-2d-fundamentals.html) |
| `JointAngleLimits2D` | Min and max rotation for Hinge — the clamp that makes a door a door | [Hinge Joint 2D](https://docs.unity3d.com/Manual/2d-physics/joints/hinge-joint-2d-fundamentals.html) |
| `JointTranslationLimits2D` | Min and max travel for Slider and Wheel suspension | [Slider Joint 2D](https://docs.unity3d.com/Manual/2d-physics/joints/slider-joint-2d-fundamentals.html) |
| `JointSuspension2D` | Wheel suspension frequency, damping ratio, and angle — a low frequency is a soft ride, and too low lets the chassis bottom out | [Wheel Joint 2D](https://docs.unity3d.com/Manual/2d-physics/joints/wheel-joint-2d-fundamentals.html) |
| Spring `frequency` / `dampingRatio` | Stiffness and settling of Spring, Target, and Wheel constraints — a high frequency approaches a rigid link, which is when Distance or Fixed is the honest choice | [Spring Joint 2D](https://docs.unity3d.com/Manual/2d-physics/joints/spring-joint-2d-fundamentals.html) |

For the bodies these joints connect, see [rigidbody-2d.md](rigidbody-2d.md).

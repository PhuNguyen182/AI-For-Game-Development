# 2D Joints — Distance, Fixed, Friction, Hinge, Relative, Slider, Spring, Target & Wheel

Covers SKILL.md step 6 (choosing a 2D joint by required constraint/degrees-of-freedom behavior).

## Overview

A `Joint2D` component connects a `Rigidbody2D` GameObject to another `Rigidbody2D` GameObject, or to a fixed position in world space (leave `connectedBody` unset). 2D joints are "the 2D counterparts of the 3D joint physics components, and are made to work only with 2D GameObjects" — they run on Unity's Box2D-backed 2D physics engine and every 2D joint component name ends in `2D` in the component browser. Joints work by applying linear and/or angular (torque) forces to satisfy a constraint (e.g. maintain a distance, hold an angle, keep a body on a line); when the constraint already holds, no force is applied, and when it's violated the solver corrects it gradually rather than instantaneously — which is why a jointed object can visibly stretch or lag under load. Applying large external forces to a jointed body with significant mass can fight the joint's own corrective forces, so keep that in mind when tuning.

Every 2D joint shares the same base concepts from `Joint2D`:

- **Connected Rigid Body** (`connectedBody`) — the other `Rigidbody2D` this joint attaches to. Leave unset to anchor to a fixed point in world space instead of another body.
- **Enable Collision** (`enableCollision`) — whether the two bodies connected by the joint should still collide with each other.
- **Break Force** / **Break Torque** (`breakForce` / `breakTorque`) — the force/torque threshold that, once exceeded, breaks the joint; `breakAction` determines what happens when it breaks (e.g. destroy the joint), and `OnJointBreak2D` is the message sent to the GameObject when it does.

Most joint types (all except `RelativeJoint2D` and `TargetJoint2D`) additionally inherit from the intermediate base class `AnchoredJoint2D`, which adds the anchor-point concepts (`anchor` / `connectedAnchor`) shared by every joint that pins to a specific local point on each body rather than to the bodies' origins.

## Manual

| Page | URL | Covers |
|---|---|---|
| 2D Joints (landing) | https://docs.unity3d.com/Manual/2d-physics/joints/2d-joints-landing.html | Index of all 9 joint types |
| Introduction to 2D joints | https://docs.unity3d.com/Manual/2d-physics/joints/introduction-to-2d-joints.html | What a 2D joint connects (Rigidbody2D to Rigidbody2D or fixed world position), that 2D joints can apply forces and limit movement |
| 2D joint constraints | https://docs.unity3d.com/Manual/2d-physics/joints/2d-joint-constraints.html | Limiting vs. driving constraints, how the solver corrects violated constraints, `breakForce`/`breakTorque`/`breakAction` |
| Distance Joint 2D (landing + fundamentals + reference) | https://docs.unity3d.com/Manual/2d-physics/joints/distance-joint-2d-landing.html , https://docs.unity3d.com/Manual/2d-physics/joints/distance-joint-2d-fundamentals.html | Fixed-length vs. max-distance-only spring constraint between two anchor points |
| Fixed Joint 2D (landing + fundamentals) | https://docs.unity3d.com/Manual/2d-physics/joints/fixed-joint-2d-landing.html , https://docs.unity3d.com/Manual/2d-physics/joints/fixed-joint-2d-fundamentals.html | Rigid positional + rotational connection via a very stiff simulated spring |
| Friction Joint 2D (landing + fundamentals) | https://docs.unity3d.com/Manual/2d-physics/joints/friction-joint-2d-landing.html , https://docs.unity3d.com/Manual/2d-physics/joints/friction-joint-2d-fundamentals.html | Damps relative linear and angular velocity to zero via a low-power simulated motor |
| Hinge Joint 2D (landing + fundamentals) | https://docs.unity3d.com/Manual/2d-physics/joints/hinge-joint-2d-landing.html , https://docs.unity3d.com/Manual/2d-physics/joints/hinge-joint-2d-fundamentals.html | Single rotation pivot, optional motor and angle limits |
| Relative Joint 2D (landing + fundamentals) | https://docs.unity3d.com/Manual/2d-physics/joints/relative-joint-2d-landing.html , https://docs.unity3d.com/Manual/2d-physics/joints/relative-joint-2d-fundamentals.html | Maintains a linear + angular offset between two bodies via a motor (not a spring) |
| Slider Joint 2D (landing + fundamentals) | https://docs.unity3d.com/Manual/2d-physics/joints/slider-joint-2d-landing.html , https://docs.unity3d.com/Manual/2d-physics/joints/slider-joint-2d-fundamentals.html | Constrains motion to an infinite (or limited) line, optional motor |
| Spring Joint 2D (landing + fundamentals) | https://docs.unity3d.com/Manual/2d-physics/joints/spring-joint-2d-landing.html , https://docs.unity3d.com/Manual/2d-physics/joints/spring-joint-2d-fundamentals.html | Elastic distance constraint that can stretch and oscillate |
| Target Joint 2D (landing + fundamentals) | https://docs.unity3d.com/Manual/2d-physics/joints/target-joint-2d-landing.html , https://docs.unity3d.com/Manual/2d-physics/joints/target-joint-2d-fundamentals.html | Pulls a single Rigidbody2D toward a (potentially moving) world-space target point via a spring |
| Wheel Joint 2D (landing + fundamentals) | https://docs.unity3d.com/Manual/2d-physics/joints/wheel-joint-2d-landing.html , https://docs.unity3d.com/Manual/2d-physics/joints/wheel-joint-2d-fundamentals.html | Combines a slider (suspension line) with a hinge (rotation), for vehicle wheels |

## Shared Joint2D base API

Members common to every 2D joint. `Joint2D` is the root (inherits `Behaviour`); `AnchoredJoint2D` is an intermediate base that adds anchor-point support and is itself the base for `DistanceJoint2D`, `FixedJoint2D`, `FrictionJoint2D`, `HingeJoint2D`, `SliderJoint2D`, `SpringJoint2D`, and `WheelJoint2D`. `RelativeJoint2D` and `TargetJoint2D` inherit `Joint2D` directly and do **not** have `anchor`/`connectedAnchor`.

| Member | From | Description |
|---|---|---|
| `attachedRigidbody` | `Joint2D` | The `Rigidbody2D` attached to the joint (the GameObject the joint component sits on). |
| `connectedBody` | `Joint2D` | The `Rigidbody2D` object to which the other end of the joint is attached. |
| `enableCollision` | `Joint2D` | Should the two connected `Rigidbody2D` still collide with each other? |
| `breakForce` | `Joint2D` | The force that must be applied for this joint to break. |
| `breakTorque` | `Joint2D` | The torque that must be applied for this joint to break. |
| `breakAction` | `Joint2D` | The action to take when the joint breaks past `breakForce`/`breakTorque`. |
| `reactionForce` | `Joint2D` | Gets the reaction force of the joint. |
| `reactionTorque` | `Joint2D` | Gets the reaction torque of the joint. |
| `GetReactionForce(timeStep)` | `Joint2D` | Gets the reaction force of the joint given the specified time step. |
| `GetReactionTorque(timeStep)` | `Joint2D` | Gets the reaction torque of the joint given the specified time step. |
| `OnJointBreak2D` | `Joint2D` (message) | MonoBehaviour message sent when a `Joint2D` on the same GameObject breaks. |
| `anchor` | `AnchoredJoint2D` | The joint's anchor point, in local space, on the object that has the joint component. |
| `connectedAnchor` | `AnchoredJoint2D` | The joint's anchor point on the second (connected) object. |
| `autoConfigureConnectedAnchor` | `AnchoredJoint2D` | Should `connectedAnchor` be calculated automatically instead of set manually? |

## Distance Joint

Maintains a set distance between two anchor points (two `Rigidbody2D`, or one body and a fixed world position) using a very stiff simulated spring, with no rotational force. With `maxDistanceOnly` off it's a rigid fixed-length link (e.g. a bicycle-wheel spoke); with it on, the body is free to move anywhere within that maximum distance, only getting pulled taut at the limit (e.g. a yo-yo).

| Member | Description |
|---|---|
| `distance` | The distance separating the two ends of the joint. |
| `maxDistanceOnly` | Whether to maintain a maximum distance only (free movement inside it) instead of the absolute distance. |
| `autoConfigureDistance` | Should `distance` be calculated automatically from the objects' current positions? |

## Fixed Joint

Rigidly connects two bodies (or one body to a fixed world position) so they hold both relative position and relative rotation, implemented internally as a spring pre-configured to be as stiff as the simulation allows — so unlike Transform parenting, a small amount of give is still physically possible. Use it for rigidly-connected structures (e.g. bridge sections) where an easily-breakable rigid link is wanted.

| Member | Description |
|---|---|
| `frequency` | The frequency at which the spring oscillates around the distance between the objects; higher = stiffer. |
| `dampingRatio` | The amount by which the spring force is reduced in proportion to movement speed (controls oscillation). |
| `referenceAngle` | The angle referenced between the two bodies, used as the rotational constraint for the joint. |

## Friction Joint

Slows relative motion between two anchor points until they stop moving relative to each other, using a simulated motor pre-configured with low motor power. It enforces two constraints simultaneously: zero relative linear velocity and zero relative angular velocity.

| Member | Description |
|---|---|
| `maxForce` | The maximum force that can be generated when trying to maintain the friction joint's linear-velocity constraint. |
| `maxTorque` | The maximum torque that can be generated when trying to maintain the friction joint's angular-velocity constraint. |

## Hinge Joint

Lets a GameObject rotate around a single shared pivot point, connecting two anchor points on two `Rigidbody2D` (or one body to a fixed world point) — a seesaw, a door, a scissor mechanism, or a powered vehicle wheel. Optional sub-features add a driven rotational motor and/or angle limits that clamp the rotation range.

| Member | Description |
|---|---|
| `useMotor` | Should the joint be rotated automatically by a motor torque? |
| `motor` (`JointMotor2D`) | Parameters for the motor force applied to the joint. |
| `GetMotorTorque(timestep)` | Gets the motor torque of the joint given the specified timestep. |
| `useLimits` | Should limits be placed on the range of rotation? |
| `limits` (`JointAngleLimits2D`) | Limit of angular rotation (in degrees) on the joint. |
| `limitState` | Gets the current state of the joint limit (read-only). |
| `jointAngle` | The current joint angle, in degrees, with respect to the reference angle (read-only). |
| `jointSpeed` | The current joint speed (read-only). |
| `referenceAngle` | The angle, in degrees, referenced between the two bodies used as the constraint for the joint. |
| `useConnectedAnchor` | Controls whether the connected anchor is used or not. |

**`JointMotor2D`** (motor config, also used by Slider and Wheel joints):

| Field | Description |
|---|---|
| `motorSpeed` | The desired speed for the `Rigidbody2D` to reach as it moves with the joint. |
| `maxMotorTorque` | The maximum force that can be applied at the joint to attain the target speed. |

**`JointAngleLimits2D`** (angle limit config):

| Field | Description |
|---|---|
| `min` | Lower angular limit of rotation. |
| `max` | Upper angular limit of rotation. |

## Relative Joint

Makes two `Rigidbody2D` maintain a fixed linear and angular offset relative to each other, driven by a simulated motor rather than a spring. Good for a trailing object that follows a leader with configurable lag (a camera tracking a player, an object trailing behind another while staying rotationally in sync).

| Member | Description |
|---|---|
| `linearOffset` | The current linear offset maintained between the two connected `Rigidbody2D`. |
| `angularOffset` | The current angular offset maintained between the two connected `Rigidbody2D`. |
| `autoConfigureOffset` | Should both `linearOffset` and `angularOffset` be calculated automatically? |
| `correctionScale` | Scales both the linear and angular forces used to correct toward the required relative orientation. |
| `maxForce` | The maximum force that can be generated when trying to maintain the relative joint's linear constraint. |
| `maxTorque` | The maximum torque that can be generated when trying to maintain the relative joint's angular constraint. |
| `target` | The world-space position the joint is currently trying to maintain. |

Note: `RelativeJoint2D` inherits `Joint2D` directly (not `AnchoredJoint2D`) — it has no `anchor`/`connectedAnchor` members.

## Slider Joint

Constrains a body to move only along a line (infinite by default) defined by the joint's angle, by applying linear force to keep it on that line — e.g. a vertically-sliding platform that reacts to weight but can't move sideways. Optional sub-features add a driven linear motor along the line and/or translation limits that bound movement to a segment of the line instead of the whole infinite line.

| Member | Description |
|---|---|
| `angle` | The angle of the line in space, in degrees. |
| `autoConfigureAngle` | Should `angle` be calculated automatically? |
| `useMotor` | Should a motor force be applied automatically to the `Rigidbody2D` along the line? |
| `motor` (`JointMotor2D`) | Parameters for the motor force applied automatically along the line. |
| `GetMotorForce(timestep)` | Gets the motor force of the joint given the specified timestep. |
| `useLimits` | Should motion limits be used? |
| `limits` (`JointTranslationLimits2D`) | Restrictions on how far the joint can slide in each direction along the line. |
| `limitState` | Gets the current state of the joint limit (read-only). |
| `jointTranslation` | The current joint translation (read-only). |
| `jointSpeed` | The current joint speed (read-only). |
| `referenceAngle` | The angle, in degrees, referenced between the two bodies used as the constraint for the joint. |

**`JointTranslationLimits2D`** (translation limit config, also used by Wheel joint):

| Field | Description |
|---|---|
| `min` | Minimum distance the `Rigidbody2D` can move from the joint's anchor. |
| `max` | Maximum distance the `Rigidbody2D` can move from the joint's anchor. |

## Spring Joint

Keeps two anchor points a target distance apart using a real spring — unlike Distance Joint, the length can stretch and oscillate under `frequency`/`dampingRatio` tuning instead of staying rigid. Applies linear force only, no torque. Good for semi-rigid multi-part character bodies that need to flex relative to each other.

| Member | Description |
|---|---|
| `distance` | The distance the spring will try to keep between the two objects. |
| `autoConfigureDistance` | Should `distance` be calculated automatically? |
| `frequency` | The frequency at which the spring oscillates around the target distance. |
| `dampingRatio` | The amount by which the spring force is reduced in proportion to movement speed. |

## Target Joint

Pulls a single `Rigidbody2D`'s anchor point toward a world-space `target` position (not another Rigidbody) using a spring, so the target can be moved every frame — e.g. dragging an object to a destination with the mouse, or letting a picked-up object hang naturally if grabbed off-center. Applies linear force only; the body can still rotate naturally if the anchor isn't at its center of mass.

| Member | Description |
|---|---|
| `target` | The world-space position the joint attempts to move the body to. |
| `autoConfigureTarget` | Should `target` be calculated automatically (from the body's current position) instead of set manually? |
| `anchor` | The local-space anchor on the Rigidbody the joint is attached to. |
| `frequency` | The frequency at which the target spring oscillates around the target position. |
| `dampingRatio` | The amount by which the target spring force is reduced in proportion to movement speed. |
| `maxForce` | The maximum force that can be generated when trying to maintain the target joint constraint. |

Note: `TargetJoint2D` inherits `Joint2D` directly (not `AnchoredJoint2D`) — its own `anchor` member above takes the place of the inherited one, and it has no `connectedBody`-relative `connectedAnchor` (it always targets a world-space point, never another body).

## Wheel Joint

Combines a Slider Joint's line constraint (the suspension travel line) with a Hinge Joint's rotation (the wheel spin), keeping two connected points aligned on an infinite line while letting the wheel body rotate freely at that point — purpose-built for vehicle wheels with suspension. A motor drives rotation (wheel spin/drive torque) while `suspension` tuning (frequency/damping) controls how stiff or loose the suspension travel is.

| Member | Description |
|---|---|
| `useMotor` | Should a motor force be applied automatically to the `Rigidbody2D` along the line? |
| `motor` (`JointMotor2D`) | Parameters for the motor force applied automatically to drive wheel rotation. |
| `GetMotorTorque(timestep)` | Gets the motor torque of the joint given the specified timestep. |
| `suspension` (`JointSuspension2D`) | The joint's suspension configuration. |
| `jointAngle` | The current joint angle, in degrees — the relative angle between the two connected `Rigidbody2D` (read-only). |
| `jointTranslation` | The current joint translation (read-only). |
| `jointSpeed` | The current joint rotational speed, in degrees/sec (read-only). |
| `jointLinearSpeed` | The current joint linear speed, in meters/sec (read-only). |

**`JointSuspension2D`** (suspension config):

| Field | Description |
|---|---|
| `angle` | The world angle, in degrees, along which the suspension moves. |
| `frequency` | The frequency at which the suspension spring oscillates. |
| `dampingRatio` | The amount by which the suspension spring force is reduced in proportion to movement speed. |

## Choosing a 2D joint by required behavior

| Requirement | Joint |
|---|---|
| Rigid link with fixed length between two anchor points (spoke, taut cable) | Distance Joint |
| Rigid link allowing free movement up to a max distance (yo-yo, leash) | Distance Joint (`maxDistanceOnly` on) |
| Rigidly hold both position and rotation between two bodies, still breakable | Fixed Joint |
| Damp relative motion to zero without rigidly locking it (drag/resistance) | Friction Joint |
| Single rotation pivot, optional motor/limits (door, seesaw, scissor, powered wheel) | Hinge Joint |
| Maintain a fixed linear + angular offset between two bodies (trailing follower, tracking camera) | Relative Joint |
| Constrain motion to a line, optional motor/limits (sliding platform, drawer, elevator) | Slider Joint |
| Elastic distance constraint that stretches and oscillates (springy limb, flexible link) | Spring Joint |
| Pull a single body toward a moving world-space point (drag-to-place, mouse-grab) | Target Joint |
| Vehicle wheel: rotation + suspension travel along a line, driven by a motor | Wheel Joint |

For Rigidbody2D body types joints connect, see [rigidbody-2d.md](rigidbody-2d.md). For collider setup, see [collider-2d.md](collider-2d.md).

# Joints 2D

Sources: Manual `2d-physics/joints/`. A `Joint2D` connects a `Rigidbody2D` to another body, or to a fixed world position when `connectedBody` is empty. The solver corrects gradually, so a loaded joint stretches or lags and a large external force fights it.

| Joint | Decides |
|---|---|
| `DistanceJoint2D` | Fixed distance, very stiff, no rotation force. `maxDistanceOnly` off = rigid spoke; on = rope (taut only at the limit) |
| `FixedJoint2D` | Holds relative position and rotation via a stiff spring: a little give remains and it can break, unlike parenting |
| `FrictionJoint2D` | Drives relative linear/angular velocity to zero: damping between two bodies, not a surface property |
| `HingeJoint2D` | One pivot, optional motor and angle limits (doors, seesaws, driven wheels) |
| `SliderJoint2D` | Motion on a line at an angle, optional motor and translation limits (lifts) |
| `SpringJoint2D` | Elastic distance with frequency/damping; visibly oscillates, unlike Distance |
| `WheelJoint2D` | Suspension line + rotation pivot + motor in one: a Slider+Hinge pair would fight |
| `TargetJoint2D` | Pulls **one** body to a moving world point with a spring (dragging); no `connectedBody`, no anchors |
| `RelativeJoint2D` | Keeps a linear/angular offset between two bodies by motor, not spring |

`RelativeJoint2D` and `TargetJoint2D` derive from `Joint2D` and have **no** `anchor`/`connectedAnchor`; the other seven are `AnchoredJoint2D`. Anchor code does not generalise across all nine.

## Shared properties

| Property | Decides |
|---|---|
| `enableCollision` | Whether the connected pair still collide; off stops a jointed pair jittering against itself |
| `breakForce` / `breakTorque` | Infinite by default; a joint never breaks until set |
| `breakAction` | Destroy the component, disable it, or notify only |
| `OnJointBreak2D` | Break message; required hook when breaking is designed |
| `anchor` / `connectedAnchor` | Local pin points; `autoConfigureConnectedAnchor` derives the second from the pose at setup |

## Motors and limits

| Structure | Decides |
|---|---|
| `JointMotor2D` | `motorSpeed` and `maxMotorTorque`; an underpowered motor stalls without error |
| `JointAngleLimits2D` | Hinge min/max rotation |
| `JointTranslationLimits2D` | Slider and Wheel travel |
| `JointSuspension2D` | Wheel frequency, damping ratio, angle; too low lets the chassis bottom out |
| Spring `frequency` / `dampingRatio` | Spring, Target, Wheel stiffness; a high frequency approaches rigid, when Distance or Fixed is the honest choice |

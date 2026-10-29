# Joints

Sources: Manual `Joints`, `class-HingeJoint`, `class-CharacterJoint`, `class-SpringJoint`, `create-configurable-joint`, `RagdollStability`.

A joint ties a `Rigidbody` to another body, an `ArticulationBody` or a fixed world point with corrective forces around a shared anchor. Named joints ship with the limits and drives their use case needs; `ConfigurableJoint` needs everything specified.

## Choosing

| Joint | Use |
|---|---|
| `FixedJoint` | Weld; parenting through physics, breakable |
| `HingeJoint` | One axis, optional spring, motor, limits: doors, levers, driven wheels |
| `SpringJoint` | Elastic distance (min/max, spring, damper); visibly stretches |
| `CharacterJoint` | Twist axis plus two swing axes; ragdoll limbs, what the Ragdoll Wizard generates |
| `ConfigurableJoint` | Per-axis Free/Limited/Locked motion, limits, drives; only when no named joint fits |
| `ArticulationBody` | Alternative, not a joint: whole hierarchy solved together ([ragdoll-physics.md](ragdoll-physics.md)) |

## Shared properties
- Connected Body: empty anchors to a world point.
- Anchor / Connected Anchor: local-space pivots. `autoConfigureConnectedAnchor` derives the second from the current pose, so moving a body afterwards changes the constraint.
- Break Force / Break Torque: infinite by default; set deliberately, and handle `OnJointBreak` if breaking is designed.
- Enable Collision off stops a jointed pair fighting itself.
- Enable Preprocessing destabilises joints whose constraints cannot be met; turn it off for anything spawned overlapping geometry.
- Mass Scale / Connected Mass Scale: scale apparent mass for the solver only, the sanctioned way to solve an extreme real mass ratio.

## Drives and limits
- `JointMotor` drives toward a speed; an underpowered one stalls silently.
- `JointSpring` settles a hinge at an angle; `JointLimits` clamps min/max angle (with bounciness, contact distance).
- `SoftJointLimit` with spring gives a soft stop on Character Joint twist/swing.
- Projection (Character, Configurable) snaps back into compliance, trading accuracy for visual stability; last resort for visible stretching.

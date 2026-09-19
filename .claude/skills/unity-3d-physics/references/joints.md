# Joints — Fixed, Hinge, Spring, Character & Configurable

Sources: [Introduction to joints](https://docs.unity3d.com/Manual/Joints.html), [Hinge Joint](https://docs.unity3d.com/Manual/class-HingeJoint.html), [Character Joint](https://docs.unity3d.com/Manual/class-CharacterJoint.html), [Create a configurable joint](https://docs.unity3d.com/Manual/create-configurable-joint.html).
Covers: SKILL.md §4 — **"Choose the joint by required degrees of freedom, not by generality"**.

A joint connects a `Rigidbody` to another body, an `ArticulationBody`, or a
fixed world point, and constrains their relative motion by applying corrective
forces around a shared anchor. Every joint can break above a force or torque
threshold. Choosing a named joint over `ConfigurableJoint` is not a style
preference: the named joints ship with the limits and drives their use case
needs already wired, and a Configurable Joint must have all of them specified.

## Choosing one

| Joint | What it decides | Source |
|---|---|---|
| `FixedJoint` | Removes all relative freedom — parenting resolved through physics rather than the hierarchy, and therefore breakable. Adds no properties beyond the shared base | [Fixed Joint](https://docs.unity3d.com/Manual/class-FixedJoint.html) |
| `HingeJoint` | One rotation axis, with optional spring, motor, and angle limits — doors, levers, driven wheels | [Hinge Joint](https://docs.unity3d.com/Manual/class-HingeJoint.html) |
| `SpringJoint` | Elastic distance constraint between two anchors, with min and max distance plus spring and damper — visibly stretches, which is the difference from Fixed | [Spring Joint](https://docs.unity3d.com/Manual/class-SpringJoint.html) |
| `CharacterJoint` | Extended ball-and-socket with a twist axis and two swing axes — built for ragdoll limbs, and what the Ragdoll Wizard generates | [Character Joint](https://docs.unity3d.com/Manual/class-CharacterJoint.html) |
| `ConfigurableJoint` | Per-axis linear and angular motion, limits, and drives — correct only when no named joint expresses the combination, since everything must be specified explicitly | [Create a configurable joint](https://docs.unity3d.com/Manual/create-configurable-joint.html) |
| `ArticulationBody` | Not a joint but its alternative — a whole hierarchy solved together, see [ragdoll-physics.md](ragdoll-physics.md) | [Articulation Body](https://docs.unity3d.com/Manual/class-ArticulationBody.html) |

## Shared base properties

| Property | What it decides | Source |
|---|---|---|
| Connected Body | The other body, or empty to anchor to a fixed world point | [Introduction to joints](https://docs.unity3d.com/Manual/Joints.html) |
| Anchor / Connected Anchor | The pivot in each body's local space; `autoConfigureConnectedAnchor` derives the second from the current pose, so moving a body afterwards changes the constraint | [Introduction to joints](https://docs.unity3d.com/Manual/Joints.html) |
| Break Force / Break Torque | Thresholds past which the joint separates; infinite by default, so a joint never breaks until this is set deliberately | [Introduction to joints](https://docs.unity3d.com/Manual/Joints.html) |
| Enable Collision | Whether the two connected bodies still collide with each other; off is what stops a jointed pair fighting itself | [Introduction to joints](https://docs.unity3d.com/Manual/Joints.html) |
| Enable Preprocessing | Helps the solver in normal conditions but destabilises a joint whose constraints cannot be satisfied — turn it off for anything spawned overlapping geometry | [Joint and ragdoll stability](https://docs.unity3d.com/Manual/RagdollStability.html) |
| Mass Scale / Connected Mass Scale | Scales each body's apparent mass *for the solver only* — the sanctioned way to make an extreme real mass ratio solvable without changing the physics elsewhere | [Introduction to joints](https://docs.unity3d.com/Manual/Joints.html) |
| `OnJointBreak` | Raised when a joint breaks — required if breaking is part of the design rather than an accident | [Introduction to joints](https://docs.unity3d.com/Manual/Joints.html) |

## Drives and limits

| Structure | What it decides | Source |
|---|---|---|
| `JointMotor` | Target velocity and force cap; a motor drives *toward* a speed, so an underpowered one stalls silently instead of erroring | [Hinge Joint](https://docs.unity3d.com/Manual/class-HingeJoint.html) |
| `JointSpring` | Spring force, damper, and target position — a hinge that settles at an angle rather than swinging freely | [Hinge Joint](https://docs.unity3d.com/Manual/class-HingeJoint.html) |
| `JointLimits` | Min and max angle, plus bounciness and contact distance — the clamp that makes a door a door | [Hinge Joint](https://docs.unity3d.com/Manual/class-HingeJoint.html) |
| `SoftJointLimit` and its spring | Character Joint twist and swing limits, each with an optional spring for a soft stop instead of a hard one | [Character Joint](https://docs.unity3d.com/Manual/class-CharacterJoint.html) |
| Configurable Joint motion axes | Each axis set Free, Limited, or Locked, then given limits and drives — the reason this joint needs the most setup and gives the most control | [Create a configurable joint](https://docs.unity3d.com/Manual/create-configurable-joint.html) |
| Projection (Character and Configurable) | Snaps a joint back into compliance when the solver cannot keep up — trades physical accuracy for visual stability, so it is a last resort for visible stretching | [Joint and ragdoll stability](https://docs.unity3d.com/Manual/RagdollStability.html) |

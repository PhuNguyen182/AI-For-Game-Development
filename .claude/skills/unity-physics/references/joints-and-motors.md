# Joints and motors

Sources (under `manual/`): `custom-joints.html`, `custom-motors.html`; `api/Unity.Physics.PhysicsJoint.html`.

Each joint type is created by its own static factory on `Unity.Physics.JointData` (`CreateBallAndSocket`, `CreateLimitedHinge`, ...) with type-specific parameters. Choose by the motion that must stay possible.

| Joint | Motion |
|---|---|
| Ball and socket | Multi-axis rotation about a shared point (hips, shoulders) |
| Hinge | Free rotation about one axis (wheels, doors) |
| Limited hinge | One axis with angular limits (knees, fingers) |
| Fixed | Fully constrains two bodies |
| Prismatic | Slide along one translational axis |
| Ragdoll | Limited multi-axis motion for characters |
| Stiff spring | Maintains a target distance |

| Motor | Drives toward |
|---|---|
| Position | Target relative position along an axis |
| Linear velocity | Target relative velocity along an axis |
| Rotation | Target angle about an axis |
| Angular velocity | Target rotational speed about an axis |

Every motor takes spring frequency and damping ratio: they set convergence speed and overshoot.

Unity Physics' own authoring motor components are documented as educational, not production. Create production motors from baked GameObject joint components or the C# API.

# Rigid bodies and `PhysicsStep`

Sources (under `manual/`): `concepts-data.html`, `component-step.html`.

The component set decides how the simulation treats a body; it is not descriptive.

| Component | Decides |
|---|---|
| `PhysicsCollider` | Shape; required to collide at all |
| `PhysicsVelocity` | Linear/angular velocity; required for a moving body |
| `PhysicsMass` | Centre of mass, inertia; with velocity it makes the body dynamic |
| `PhysicsDamping` | Optional per-body drag |
| `PhysicsGravityFactor` | Per-body multiplier over scene gravity (the sanctioned way to make one body fall differently) |
| `PhysicsCustomTags` | Custom filter flags; the cheap alternative to intercepting the pipeline |
| `PhysicsSolverType` | Iterative or Direct solver for this body |
| `PhysicsWorldIndex` | Required **shared** component naming the world; also partitions chunks |
| Transforms | Dynamic: `LocalTransform`. Static: `LocalTransform` or `LocalToWorld` |

## `PhysicsStep` — one per scene
A second `PhysicsStep` is ambiguity about which settings run, not additive config.

| Setting | Decides |
|---|---|
| Gravity | Scene-global value |
| Solver iterations, substeps | Accuracy vs cost for the whole simulation; raising fixes soft or jittery stacks at a global price |
| Multithreading | Spread across worker threads |
| Collision tolerance, depenetration limits, broadphase | Contact generation and recovery |
| Gyroscopic torque | Extra fidelity for spinning bodies |

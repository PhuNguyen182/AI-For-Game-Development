# Design Philosophy & the Simulation Pipeline

Sources: [Design philosophy](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/design.html), [Physics Pipeline](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/physics-pipeline.html).
Covers: SKILL.md §4 — **"Confirm this is DOTS Physics and not PhysX before touching a component"**.

What makes this engine different from PhysX, and the stage order any custom
logic has to be placed against. The interception interfaces themselves are in
[spatial-queries-and-events.md](spatial-queries-and-events.md).

## Design properties

| Property | What it decides | Source |
|---|---|---|
| Fully deterministic | Same inputs always produce the same outputs, which is what makes multi-step-per-frame simulation and rollback tractable | [Design philosophy](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/design.html) |
| Stateless | No cached contact or constraint state between frames — simpler and controllable, but it gives up the robustness cached-state engines get for free | [Design philosophy](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/design.html) |
| Pure high-performance C# | Written with ECS practices and minimal dependencies; core algorithms are decoupled from jobs and ECS to stay reusable | [Design philosophy](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/design.html) |
| A smaller feature set than PhysX | Fully customizable rather than comprehensive out of the box — features PhysX supplies may have to be built here | [Design philosophy](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/design.html) |

## Pipeline stages, in order

| Stage | What it decides | Source |
|---|---|---|
| `PhysicsInitializeGroup` | Converts ECS component data into simulation data — everything downstream operates on that, not on the components | [Physics Pipeline](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/physics-pipeline.html) |
| `PhysicsCreateBodyPairsGroup` | Broadphase: finds AABB-overlapping pairs — the cheapest place to exclude an interaction | [Physics Pipeline](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/physics-pipeline.html) |
| `PhysicsCreateContactsGroup` | Narrowphase: turns pairs into contacts — where contact properties can still be changed | [Physics Pipeline](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/physics-pipeline.html) |
| `PhysicsCreateJacobiansGroup` | Constraint setup: builds jacobians from contacts — the last point before solving | [Physics Pipeline](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/physics-pipeline.html) |
| `PhysicsSolveAndIntegrateGroup` | Solves and integrates motion | [Physics Pipeline](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/physics-pipeline.html) |
| `ExportPhysicsWorld` | Writes results back into `LocalTransform` and `PhysicsVelocity` — before this runs, the components still hold last frame's values | [Physics Pipeline](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/physics-pipeline.html) |
| `PhysicsWorld` | The per-step simulation structure the pipeline builds, distinct from the permanent ECS components it derives from | [PhysicsWorld](https://docs.unity3d.com/Packages/com.unity.physics@6.6/api/Unity.Physics.PhysicsWorld.html) |

**Critical caveat**: statelessness is the trade behind several familiar
behaviours being absent. An artifact that a cached-state engine would smooth
away across frames is visible here, which is why geometry quality matters more
in this engine than habit from PhysX suggests.

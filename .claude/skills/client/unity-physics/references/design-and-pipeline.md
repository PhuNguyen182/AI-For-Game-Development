# Design Philosophy & the Simulation Pipeline

Covers SKILL.md steps 1, 2, 8 (confirming this is DOTS Physics not PhysX, the ECS-adoption prerequisite, and reaching for pipeline-hook job interfaces only when justified).

## Manual
- [Physics engine overview](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/concepts-intro.html) — entry point for the engine-overview section; links to Design philosophy, the simulation pipeline, and simulation setup demonstration.
- [Design philosophy](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/design.html) — Unity Physics is **completely deterministic** and deliberately **stateless** (no cached contact/constraint state across frames, trading the robustness of cached-state engines for simplicity, control, and straightforward multi-step-per-frame simulation and networking rollback). Written entirely in high-performance C# using ECS best practices, following "the DOTS philosophy of minimal dependencies and complete control." Core algorithms are intentionally decoupled from jobs and ECS to encourage reuse. Offers a simpler, fully customizable feature subset rather than PhysX's comprehensive out-of-the-box feature set.
- [The simulation pipeline](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/concepts-simulation.html) — overview of how a simulation step is structured.
- [Physics Pipeline](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/physics-pipeline.html) — the four `PhysicsSimulationGroup` stages, in order: **broadphase** (`PhysicsCreateBodyPairsGroup` — finds AABB-overlapping body pairs), **narrowphase** (`PhysicsCreateContactsGroup` — creates contacts from overlapping pairs), **constraint setup** (`PhysicsCreateJacobiansGroup` — builds jacobians from contacts), **solve & integrate** (`PhysicsSolveAndIntegrateGroup` — solves jacobians and integrates motion). `PhysicsInitializeGroup` converts ECS data into simulation data beforehand; `ExportPhysicsWorld` converts results back into ECS components (`LocalTransform`, `PhysicsVelocity`) afterward. Custom logic can be injected between any of these stages.

## Scripting API
- [`Unity.Physics.PhysicsWorld`](https://docs.unity3d.com/Packages/com.unity.physics@6.6/api/Unity.Physics.PhysicsWorld.html) — the runtime simulation-data structure the pipeline builds and operates on each step, distinct from the permanent ECS component data it's derived from.

Note the ECS-adoption gate: this whole section is only relevant once ECS/DOTS Physics has already been architecturally justified for the project — see [dots-relationship.md](dots-relationship.md) and `unity-ecs-architecture`'s own prerequisite.

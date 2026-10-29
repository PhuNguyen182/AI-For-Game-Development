# Physics Optimization

Sources: Manual `physics-optimization`, `physics-optimization-cpu`, `physics-optimization-memory`, `physics-performance-issues`; API `Physics`, `Time`.

Fixed timestep is decoupled from the frame: a slow frame elsewhere makes PhysX run repeatedly to catch up, so physics looks expensive when nothing about it changed.

## Diagnosis

| Tool | Reveals |
|---|---|
| Profiler | `Physics.FixedUpdate`/`Physics.Simulate`, split broadphase/narrowphase |
| Calls column on `Physics.Simulate` | 1 per frame is normal; climbing toward 10 is timestep debt after a heavy frame. Fix that frame, not physics settings |
| Memory Profiler | Allocation from collision callbacks and query result arrays (intermittent stutter) |
| Physics Debug window | Shapes, contacts, broadphase bounds, sleep state: over-complex colliders, bodies that never sleep |

## CPU
- `Time.fixedDeltaTime`: raising it cuts steps per second; first relief for catch-up spirals, costs fidelity. It scales with `Time.timeScale` and is quantised, so the getter may differ by one bit from what was set.
- `Physics.simulationMode`: Script mode aligns stepping with game pacing; query-only removes the step for ray-only games.
- Kinematic Rigidbody instead of a moved static collider (avoids broadphase rebuild).
- Layer matrix prunes pairs before broadphase.
- Broadphase algorithm choice matters mainly in large or unevenly populated worlds.
- Primitive instead of mesh collider is usually the largest per-object saving; set Mesh Collider cooking options deliberately (bake time vs query cost).
- Sleeping: `NeverSleep` is a standing per-body cost to justify.
- Transform synchronisation management controls when Transform writes reach the physics scene.
- Continuous detection costs more; apply per body.

## Memory
- `Physics.reuseCollisionCallbacks` removes per-contact allocation; read the `Collision`, never store it.
- `NonAlloc` queries with caller-owned buffers.
- `Physics.invokeCollisionCallbacks` off disables collision messages for polled simulations.

## Tuning knobs

| Member | Note |
|---|---|
| `Physics.defaultSolverIterations` | Default 6; 10-20 stabilises joints, cost paid by every jointed body |
| `Physics.defaultSolverVelocityIterations` | Default 1; raise for bounce/impact fidelity |
| `Physics.sleepThreshold` | Higher settles sooner, risks sleeping mid-motion |
| `Physics.defaultContactOffset` | Too small misses contacts; too large floats visibly |
| `Physics.improvedPatchFriction` | Keeps friction within analytical bounds; fixes creep on slopes |

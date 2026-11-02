---
name: unity-3d-physics
description: "PhysX: Rigidbody, CharacterController, joints, ArticulationBody, Cloth, NonAlloc casts. Use for 3D physics."
user-invocable: false
---

# Unity 3D Physics (PhysX)

- **Not for:** 2D physics (`unity-2d-physics`).
- **Not for:** DOTS physics (`unity-physics`).
- **Not for:** pathfinding agents (`unity-navmesh-navigation`).
- **Not for:** blending a ragdoll back into animation (`unity-animation`).
- **Not for:** cloth-looking effects without simulation (`technical-artist`).
- **Not for:** damage/knockback magnitude and state rules (`csharp-engineer`, Shared Core).
- **Not for:** a cost that survives every step below (`unity-performance-engineer`, measured per `unity-profiler-diagnostics`).
- **Docs:** https://docs.unity3d.com/Manual/PhysicsOverview.html and https://docs.unity3d.com/ScriptReference/Physics.html — unversioned.
  - **Unversioned URLs:** they track the current release; re-check defaults in the project's Editor.
  - **Engine check:** `UnityEngine.Physics` is PhysX; `Physics2D` and `com.unity.physics` share type names but not behaviour, so confirm the engine first.

## References
- **[character-controller.md](references/character-controller.md):** Building or fixing `CharacterController` movement.
- **[rigidbody-physics.md](references/rigidbody-physics.md):** Configuring a body, or motion looks wrong.
- **[collision.md](references/collision.md):** Choosing a shape, or a callback fires or fails wrongly.
- **[joints.md](references/joints.md):** Constraining two bodies.
- **[ragdoll-physics.md](references/ragdoll-physics.md):** Building a ragdoll, or a joint chain jitters or stretches.
- **[cloth.md](references/cloth.md):** Simulating a cape, skirt or cloak.
- **[physics-optimization.md](references/physics-optimization.md):** Physics costs too much or the frame stutters.

## Steps
1. **Confirm the engine is built-in PhysX:** before touching a component.
2. **Choose locomotion by whether the character must be pushed:** per [character-controller.md](references/character-controller.md).
   - **`CharacterController`:** pushes bodies but is never pushed.
   - **Rigidbody character:** only when dynamic bodies must move it.
   - **Status:** `CharacterController` is not `[Obsolete]`, so it stays valid for new work.
3. **Move simulated bodies through the physics API, never the Transform:** `MovePosition`/`MoveRotation` in `FixedUpdate`, `Move`/`SimpleMove` for a controller.
   - **Transform write:** teleports past contact generation and desynchronises joints.
4. **Configure the Rigidbody by how it is watched and how fast it moves:** per [rigidbody-physics.md](references/rigidbody-physics.md).
   - **Following camera:** Interpolate.
   - **Small fast bodies:** a continuous mode.
   - **Sleep:** left on.
5. **Pick the simplest collider; never reposition a static one:** use a Kinematic Rigidbody, per [collision.md](references/collision.md).
   - **Filtering:** prune the layer matrix instead of filtering inside `OnCollisionEnter`.
6. **Choose the joint by degrees of freedom:** per [joints.md](references/joints.md).
   - **`ConfigurableJoint`:** only when no named joint fits.
7. **Choose the chain body by what it must do:** per [ragdoll-physics.md](references/ragdoll-physics.md).
   - **Death/hit ragdoll:** Ragdoll Wizard (Character Joints).
   - **Deep, motor-driven or stretch-prone chains:** `ArticulationBody`.
8. **Fix ragdoll instability at mass ratio and limits before solver iterations:** the order is in [ragdoll-physics.md](references/ragdoll-physics.md).
9. **`Cloth` only on a Skinned Mesh Renderer:** per [cloth.md](references/cloth.md).
   - **Self- and inter-collision:** stay off until a visible problem needs them.
10. **Keep the rule out of the callback:** PhysX results are not reproducible across platforms.
   - **Hand to Core:** pass contact point, normal and relative velocity into Core and let it decide any outcome the server must agree on (`csharp-standards`).
11. **Diagnose with the tool matching the symptom before tuning:** per [physics-optimization.md](references/physics-optimization.md).
   - **Solver cost:** Profiler.
   - **Callback/query allocation:** Memory Profiler.
   - **Bodies that never sleep:** Physics Debug window.
   - **Optimisation claim:** never make one without that measurement.
   - **`Physics.Simulate Calls` climbing toward 10:** timestep catch-up; fix the preceding heavy frame, not physics settings.
12. **A symptom with several causes:** "falls through the floor" is detection mode, layer matrix, Transform-driven move or missing collider.
   - **Before changing settings:** state the assumed cause.

## Never
- **Call `Move` and `SimpleMove` in the same frame, or either twice per frame:** results compound and `collisionFlags` reports only part of it.
- **Cache the `Collision` object from a callback while `Physics.reuseCollisionCallbacks` is on:** one instance is reused.
- **Add `Cloth` to a plain Mesh Renderer:** Unity silently replaces the renderer.

## Output
```
## 3D Physics Work — <feature/body>
- Locomotion: <CharacterController / Rigidbody — why; gravity handling>
- Rigidbody: <mass, damping, isKinematic, interpolation, detection, constraints, sleep>
- Movement path: <MovePosition / Move / AddForce>
- Collider: <shapes, MeshCollider cooking, PhysicsMaterial, layer matrix pruning>
- Joint / ArticulationBody / Ragdoll / Cloth: <only if used: type, limits, mass ratios, solver iterations, colliders>
- Shared Core boundary: <data handed to Core vs decision left in the callback>
```

## Example
- **"The ragdoll flails; raise solver iterations to 50":** declined first.
  - **Why:** iterations are the last and project-wide cost.
  - **Found:** forearm was ~12x its hand's mass and two limits sat at 2°.
  - **Did instead:** fixed ratios to within 2x, set those axes to 0, disabled Enable Preprocessing on joints spawned in geometry; 10-20 iterations then sufficed.

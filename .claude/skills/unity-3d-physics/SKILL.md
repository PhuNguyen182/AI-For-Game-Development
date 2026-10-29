---
name: unity-3d-physics
description: "Unity 3D physics (PhysX): Rigidbody, colliders, CharacterController, joints, ArticulationBody, ragdoll, Cloth, NonAlloc casts, layer matrix, fixedDeltaTime, interpolation. Use for 3D physics behaviour on GameObjects."
user-invocable: false
---

# Unity 3D Physics (PhysX)

Not for: 2D physics (`unity-2d-physics`), DOTS physics (`unity-physics`), pathfinding agents (`unity-navmesh-navigation`), blending a ragdoll back into animation (`unity-animation`), cloth-looking effects without simulation (`technical-artist`), damage/knockback magnitude and state rules (`csharp-engineer`, Shared Core), a cost that survives every step below (`gameplay-engineer`).
Docs: https://docs.unity3d.com/Manual/PhysicsOverview.html and https://docs.unity3d.com/ScriptReference/Physics.html — unversioned, so they track the current release; re-check defaults in the project's Editor. `UnityEngine.Physics` is PhysX; `Physics2D` and `com.unity.physics` share type names but not behaviour, so confirm the engine first.

| Reference | Read when |
|---|---|
| [character-controller.md](references/character-controller.md) | Building or fixing `CharacterController` movement |
| [rigidbody-physics.md](references/rigidbody-physics.md) | Configuring a body, or motion looks wrong |
| [collision.md](references/collision.md) | Choosing a shape, or a callback fires or fails wrongly |
| [joints.md](references/joints.md) | Constraining two bodies |
| [ragdoll-physics.md](references/ragdoll-physics.md) | Building a ragdoll, or a joint chain jitters or stretches |
| [cloth.md](references/cloth.md) | Simulating a cape, skirt or cloak |
| [physics-optimization.md](references/physics-optimization.md) | Physics costs too much or the frame stutters |

## Steps
1. **Confirm the engine is built-in PhysX** before touching a component.
2. **Choose locomotion by whether the character must be pushed**, per [character-controller.md](references/character-controller.md) — `CharacterController` pushes bodies but is never pushed; use a Rigidbody character only when dynamic bodies must move it. It is supported-but-legacy from Unity 6.5, not `[Obsolete]`, so it stays valid for new work.
3. **Move simulated bodies through the physics API**, never the Transform: `MovePosition`/`MoveRotation` in `FixedUpdate`, `Move`/`SimpleMove` for a controller. A Transform write teleports past contact generation and desynchronises joints.
4. **Configure the Rigidbody by how it is watched and how fast it moves**, per [rigidbody-physics.md](references/rigidbody-physics.md) — Interpolate under a following camera, a continuous mode for small fast bodies, sleep left on.
5. **Pick the simplest collider; never reposition a static one** (use a Kinematic Rigidbody), per [collision.md](references/collision.md). Prune the layer matrix instead of filtering inside `OnCollisionEnter`.
6. **Choose the joint by degrees of freedom**, per [joints.md](references/joints.md); `ConfigurableJoint` only when no named joint fits.
7. **Prefer `ArticulationBody` for chains**, per [ragdoll-physics.md](references/ragdoll-physics.md).
8. **Fix ragdoll instability at mass ratio and limits before solver iterations** — the order is in [ragdoll-physics.md](references/ragdoll-physics.md).
9. **`Cloth` only on a Skinned Mesh Renderer**, per [cloth.md](references/cloth.md); self- and inter-collision stay off until a visible problem needs them.
10. **Keep the rule out of the callback** — PhysX results are not reproducible across platforms. Pass contact point, normal and relative velocity into `Game.Core.*` and let it decide any outcome the server must agree on (`csharp-standards`).
11. **Diagnose with the tool matching the symptom before tuning**, per [physics-optimization.md](references/physics-optimization.md): Profiler for solver cost, Memory Profiler for callback/query allocation, Physics Debug window for bodies that never sleep. Never claim an optimisation without that measurement. `Physics.Simulate Calls` climbing toward 10 is timestep catch-up: fix the preceding heavy frame, not physics settings.
12. **A symptom with several causes** ("falls through the floor": detection mode, layer matrix, Transform-driven move, missing collider) — state the assumed cause before changing settings.

## Never
- Call `Move` and `SimpleMove` in the same frame, or either twice per frame — results compound and `collisionFlags` reports only part of it.
- Cache the `Collision` object from a callback while `Physics.reuseCollisionCallbacks` is on — one instance is reused.
- Add `Cloth` to a plain Mesh Renderer — Unity silently replaces the renderer.

## Output
```
## 3D Physics Work — <feature/body>
- Locomotion: <CharacterController / Rigidbody — why; gravity handling>
- Rigidbody: <mass, damping, isKinematic, interpolation, detection, constraints, sleep>
- Movement path: <MovePosition / Move / AddForce>
- Collider: <shapes, MeshCollider cooking, PhysicsMaterial, layer matrix pruning>
- Joint / ArticulationBody / Ragdoll / Cloth: <only if used: type, limits, mass ratios, solver iterations, colliders>
- Shared Core boundary: <data handed to Core vs decision left in the callback>
- Verification: <Profiler / Memory Profiler / Physics Debug finding, or "not measured">
- Known limitations: <...>
```
On request only, add `Latent concerns` and `Future remediation`, each with its trigger.

## Example
- "The ragdoll flails; raise solver iterations to 50" → declined first: iterations are the last and project-wide cost. Forearm was ~12x its hand's mass and two limits sat at 2°; fixed ratios to within 2x, set those axes to 0, disabled Enable Preprocessing on joints spawned in geometry; 10-20 iterations then sufficed.

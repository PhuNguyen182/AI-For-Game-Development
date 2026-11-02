---
name: unity-2d-physics
description: "Box2D: Rigidbody2D, Collider2D, CompositeCollider2D, Effector2D, Joint2D, layer matrix. Use for 2D physics."
user-invocable: false
---

# Unity 2D Physics

- **Not for:** 3D physics (`unity-3d-physics`).
- **Not for:** DOTS physics (`unity-physics`).
- **Not for:** sprite outline authoring (`unity-2d-sprite`).
- **Not for:** tile collision generation (`unity-tilemap`).
- **Not for:** Sprite Shape colliders (`unity-2d-spriteshape`).
- **Not for:** damage/state rules (`csharp-engineer`).
- **Not for:** profiling beyond shape/matrix/sleep tuning (`unity-performance-engineer`).
- **Docs:** https://docs.unity3d.com/Manual/2d-physics/ — unversioned.
  - **Defaults:** those quoted here may differ in the project's Editor, so check there.

## References
- **[rigidbody-2d.md](references/rigidbody-2d.md):** Choosing a body type, moving a body, tunnelling, jitter, sleep, or a force that must keep accelerating (`ConstantForce2D`).
- **[collider-2d.md](references/collider-2d.md):** Choosing a shape, merging tiles with a composite, or a contact/trigger fires or fails unexpectedly.
- **[physics-material-2d.md](references/physics-material-2d.md):** A surface is too slippery, too grippy or bounces unexpectedly.
- **[effectors-2d.md](references/effectors-2d.md):** One-way platform, wind/magnet zone, conveyor or water volume.
- **[joints-2d.md](references/joints-2d.md):** Constraining two bodies, or a joint sags, oscillates or breaks.

## Steps
1. **Confirm the engine:** `Rigidbody2D`/`Collider2D` are Box2D; `Rigidbody`/`Collider` are PhysX, `PhysicsVelocity`/`PhysicsCollider` are DOTS.
   - **Same vocabulary:** different behaviour.
2. **Symptom does not name its layer:** state the assumption first.
   - **"Falls through the floor":** body type, detection mode, layer matrix or a Transform-driven move; each looks identical and fixing the wrong one hides the cause.
3. **Body type = who moves it:** per [rigidbody-2d.md](references/rigidbody-2d.md).
   - **Dynamic:** the solver moves it.
   - **Kinematic:** script/animation moves it; meets only Dynamic bodies.
   - **Immovable geometry:** no `Rigidbody2D`.
4. **Move through the physics API, never `transform.position`:** `MovePosition`/`MoveRotation` in `FixedUpdate`, `Slide`, velocity, forces.
5. **Simplest collider shape:** that fits the silhouette, per [collider-2d.md](references/collider-2d.md) and `csharp-standards` → `performance-and-algorithms.md`.
   - **Adjacent tile colliders:** merge with `CompositeCollider2D`.
6. **Prune the layer matrix:** instead of filtering in callbacks.
   - **Per-collider `includeLayers`/`excludeLayers`:** only for a real exception.
7. **Shared `PhysicsMaterial2D` asset:** per [physics-material-2d.md](references/physics-material-2d.md).
   - **Reasoning:** about the pair, not one asset.
8. **Effector only for behaviour physics does not give:** per [effectors-2d.md](references/effectors-2d.md).
   - **"Just push it":** an `AddForce`.
   - **Used By Effector:** enable it on the acting collider or the effector silently does nothing.
9. **Joint by the constraint stated:** per [joints-2d.md](references/joints-2d.md).
   - **Break force:** set it deliberately and handle `OnJointBreak2D` if the joint can break.
10. **Hand contact data to Core, do not decide in the callback:**
   - **Why:** Box2D is not bit-identical across platforms, which breaks prediction against server authority (`csharp-standards` → `coding-principles.md`).
   - **Pass:** contact point, normal and relative velocity.
11. **Verify a physics fix by measurement:** Profiler Physics2D markers and the Physics Debug window, per `unity-profiler-diagnostics`.
   - **No measurement:** report "not measured".

## Never
- **Assume two `EdgeCollider2D` collide:** they never do.
- **Switch Body Type per frame:** each switch recalculates mass and re-evaluates contacts.
- **Port a 3D force call unchanged:** `ForceMode2D` has only Force and Impulse, and no `relativeTorque`.

## Output
```
## 2D Physics — <feature/body>
- Rigidbody2D: <type, mass, damping, gravity scale, interpolation, detection, constraints, sleep>
- Movement path: <MovePosition/Slide/AddForce/solver> — why not Transform
- Collider: <shapes, trigger, composite geometry>
- Material / layer matrix: <asset, combine modes; pairs pruned>
- Effector / Joint: <type, Used By Effector, break force> — why over the simpler option
- Core boundary: <data handed to Core>
```

## Example
- **"Add an `AreaEffector2D` to the water so things float":** declined.
  - **Why:** Area is a directional force, not a fluid, so bodies accelerate out.
  - **Did instead:** used `BuoyancyEffector2D` (Surface Level at the waterline, Density, drags) on a trigger with Used By Effector on.

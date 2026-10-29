# Cloth

Sources: Manual `class-Cloth`; API `Cloth`, `ClothSphereColliderPair`, `ClothSkinningCoefficient`.

Fabric simulation (capes, skirts, cloaks) following the skinned animation. Skinned Mesh Renderer only: adding it to a plain Mesh Renderer replaces that renderer. It collides only with the colliders assigned to it, never the scene.

## Fabric

| Property | Note |
|---|---|
| Stretching / Bending Stiffness | Elongation vs folding resistance (silk vs leather) |
| Use Tethers | Stops moving particles drifting from fixed ones (cape detaching in fast motion) |
| Damping | Settling rate; fixes endless oscillation |
| External / Random Acceleration | Wind without a wind system |
| World Velocity / Acceleration Scale | How strongly character movement drives the cloth |
| Sleep Threshold | Simulation stops below it |

## Collision and cost

| Property | Note |
|---|---|
| Capsule Colliders | Cloth ignores colliders not listed; a cape through a shoulder means the shoulder was never assigned |
| Sphere Colliders | `ClothSphereColliderPair`: a pair is a conical capsule between two spheres; a single-sphere pair is a sphere |
| Friction | High makes fabric cling |
| Collision Mass Scale | Raises colliding particles' apparent mass; reduces penetration |
| Use Continuous Collision | Stability against fast motion, at a cost |
| Use Virtual Particles | One extra particle per triangle; a cheaper first response to penetration than solver frequency |
| Solver Frequency | Accuracy vs cost dial; raise last |

## Per-vertex constraints
- Edit Constraints tool paints Max Distance and Surface Penetration (pins a cape top while the hem swings).
- `ClothSkinningCoefficient.maxDistance`: 0 pins the vertex to the animation. `collisionSphereDistance`: distance at which a vertex is pushed back out.

Self-collision and inter-collision are the most expensive settings: leave off until a visible problem needs them, and confirm the cost in the Profiler before shipping them on mobile.

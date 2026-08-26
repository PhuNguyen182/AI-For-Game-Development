# Cloth — Skinned Mesh Fabric Simulation

Sources: [Cloth component reference](https://docs.unity3d.com/Manual/class-Cloth.html), [Cloth API](https://docs.unity3d.com/ScriptReference/Cloth.html).
Covers: SKILL.md §4 — **"Set up `Cloth` only on a Skinned Mesh Renderer"**.

`Cloth` simulates fabric on a character — capes, skirts, cloaks — as a real
mesh deformation that follows the skinned animation underneath. It works only
with a Skinned Mesh Renderer, and adding it to a GameObject carrying a plain
Mesh Renderer **replaces that renderer** rather than refusing. It also
collides only against the collider list assigned to it, not against the scene.

## Fabric behaviour

| Property | What it decides | Source |
|---|---|---|
| Stretching Stiffness | How much the fabric resists elongation — low values read as loose knit, high as canvas | [Cloth reference](https://docs.unity3d.com/Manual/class-Cloth.html) |
| Bending Stiffness | Resistance to folding; the dial that separates silk from leather at the same stretch setting | [Cloth reference](https://docs.unity3d.com/Manual/class-Cloth.html) |
| Use Tethers | Constrains moving particles from drifting too far from fixed ones — what stops a cape detaching visually under fast motion | [Cloth reference](https://docs.unity3d.com/Manual/class-Cloth.html) |
| Use Gravity | Whether gravity acts on the particles at all | [Cloth reference](https://docs.unity3d.com/Manual/class-Cloth.html) |
| Damping | Motion damping; the settling rate, and the fix for fabric that oscillates forever | [Cloth reference](https://docs.unity3d.com/Manual/class-Cloth.html) |
| External / Random Acceleration | A constant and a randomised acceleration — how wind is authored without a wind system | [Cloth reference](https://docs.unity3d.com/Manual/class-Cloth.html) |
| World Velocity / Acceleration Scale | How strongly the character's own world movement drives the cloth — the difference between a cape that reacts to running and one that ignores it | [Cloth reference](https://docs.unity3d.com/Manual/class-Cloth.html) |
| Sleep Threshold | Below this the simulation stops until disturbed | [Cloth reference](https://docs.unity3d.com/Manual/class-Cloth.html) |

## Collision and cost

| Property | What it decides | Source |
|---|---|---|
| Capsule Colliders | The `CapsuleCollider` array the cloth collides with — cloth ignores every collider not in this list, so a cape passing through a shoulder means the shoulder was never assigned | [Cloth reference](https://docs.unity3d.com/Manual/class-Cloth.html) |
| Sphere Colliders | `ClothSphereColliderPair` entries; a pair models a conical capsule between two spheres, and a single-sphere pair models a plain sphere | [ClothSphereColliderPair](https://docs.unity3d.com/ScriptReference/ClothSphereColliderPair.html) |
| Friction | Friction against the character's colliders — high values make fabric cling to the body | [Cloth reference](https://docs.unity3d.com/Manual/class-Cloth.html) |
| Collision Mass Scale | Increases the apparent mass of colliding particles, which reduces visible penetration | [Cloth reference](https://docs.unity3d.com/Manual/class-Cloth.html) |
| Use Continuous Collision | Improves stability against fast motion, at a cost | [Cloth reference](https://docs.unity3d.com/Manual/class-Cloth.html) |
| Use Virtual Particles | Adds one particle per triangle purely to improve collision stability — a cheaper first response to penetration than raising the solver frequency | [Cloth reference](https://docs.unity3d.com/Manual/class-Cloth.html) |
| Solver Frequency | Iterations per second; the most direct accuracy-versus-cost dial, and the one to raise last | [Cloth reference](https://docs.unity3d.com/Manual/class-Cloth.html) |

## Per-vertex constraints

| Member | What it decides | Source |
|---|---|---|
| Edit Constraints tool | Paints per-vertex Max Distance and Surface Penetration in the Scene view — how the top of a cape is pinned to the shoulders while the hem swings free | [Cloth reference](https://docs.unity3d.com/Manual/class-Cloth.html) |
| `ClothSkinningCoefficient.maxDistance` | How far a vertex may leave its skinned position; 0 pins it completely to the animation | [ClothSkinningCoefficient](https://docs.unity3d.com/ScriptReference/ClothSkinningCoefficient.html) |
| `ClothSkinningCoefficient.collisionSphereDistance` | Distance from the skinned position at which the vertex is pushed back out — the anti-penetration radius | [ClothSkinningCoefficient](https://docs.unity3d.com/ScriptReference/ClothSkinningCoefficient.html) |

**Critical caveat**: self-collision and inter-collision are the most expensive
settings on the component. Leave them off until a visible problem requires
them, per KISS in `coding-principles.md`, and confirm the cost in the Profiler
before shipping them on a mobile target.

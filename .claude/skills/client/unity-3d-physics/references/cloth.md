# Cloth — Skinned Mesh Fabric Simulation

Covers SKILL.md step 9 (setting up Cloth on a Skinned Mesh Renderer).

## Overview

The Cloth component provides a physics-based solution for simulating fabrics. It is specifically designed for character clothing and only works with a Skinned Mesh Renderer — if Cloth is added to a GameObject with a regular Mesh Renderer, Unity automatically replaces it with a Skinned Mesh Renderer. Typical uses are cloaks, capes, skirts, and other garment meshes that need to react to character motion and gravity while still following the underlying skinned animation.

## Manual

| Page | URL | Covers |
|---|---|---|
| Cloth component reference | https://docs.unity3d.com/Manual/class-Cloth.html | Inspector properties, Edit Constraints tool, self-collision/intercollision, collider interaction |
| Cloth (Scripting API) | https://docs.unity3d.com/ScriptReference/Cloth.html | `Cloth` class properties and methods |
| ClothSkinningCoefficient (Scripting API) | https://docs.unity3d.com/ScriptReference/ClothSkinningCoefficient.html | Per-vertex constraint struct (`maxDistance`, `collisionSphereDistance`) |
| ClothSphereColliderPair (Scripting API) | https://docs.unity3d.com/ScriptReference/ClothSphereColliderPair.html | Sphere collider pair struct (`first`, `second`) |

## Component Inspector properties

| Property | Description |
|---|---|
| Stretching Stiffness | Stretching stiffness of the cloth. |
| Bending Stiffness | Bending stiffness of the cloth. |
| Use Tethers | Apply constraints that help to prevent the moving cloth particles from going too far away from the fixed ones. |
| Use Gravity | Should gravitational acceleration be applied to the cloth? |
| Damping | Motion damping coefficient. |
| External Acceleration | A constant, external acceleration applied to the cloth. |
| Random Acceleration | A random, external acceleration applied to the cloth. |
| World Velocity Scale | How much world-space movement of the character will affect cloth vertices. |
| World Acceleration Scale | How much world-space acceleration of the character will affect cloth vertices. |
| Friction | The friction of the cloth when colliding with the character. |
| Collision Mass Scale | How much to increase mass of colliding particles. |
| Use Continuous Collision | Enable continuous collision to improve collision stability. |
| Use Virtual Particles | Add one virtual particle per triangle to improve collision stability. |
| Solver Frequency | Number of solver iterations per second. |
| Sleep Threshold | Cloth's sleep threshold. |
| Capsule Colliders | An array of `CapsuleCollider`s which this Cloth instance should collide with. |
| Sphere Colliders | An array of `ClothSphereColliderPair`s which this Cloth instance should collide with. |
| Virtual Particle Weights | Barycentric coordinates of the virtual particles with respect to the three neighbouring normal cloth particles. |

## Editing constraints (Edit Constraints tool)

Enable via **Edit cloth constraints** in the Inspector — small spheres appear on every mesh vertex in the Scene view, representing cloth particles. Visualization can show Max Distance or Surface Penetration constraint values, and a "Manipulate Backfaces" option exposes hidden particles for editing. Three modes control how constraint values are applied to particles:

| Mode | Effect |
|---|---|
| Select | Apply a fixed constraint value to a pre-selected group of particles, chosen via selection boxes or individual clicks. |
| Paint | Apply a fixed constraint value by painting the cloth particles with a brush of adjustable radius. |
| Gradient | Apply a left-to-right linear gradient of constraint values to a pre-selected group of particles (requires a 2D Scene view). |

## Self-collision & inter-collision

Self-collision prevents a cloth mesh from penetrating itself; inter-collision lets particles from different cloth instances collide with each other. Configure via the **Self Collision and Intercollision** button in the Inspector — particles start black (unused), turn blue when selected, and green once collision is enabled for them. Two parameters tune the effect: Inter-Collision Distance (the diameter of a sphere around each particle that Unity keeps from overlapping other particles' spheres during simulation) and Inter-Collision Stiffness (how strong the separating impulse between colliding particles should be).

**Performance cost**: self collision and intercollision can take a significant amount of the overall simulation time — treat them as the most expensive Cloth settings and enable only where visually necessary.

## Colliders for Cloth

Cloth cannot collide with arbitrary world geometry. It only interacts with colliders explicitly assigned to its Capsule Colliders or Sphere Colliders arrays, and the interaction is one-way: cloth reacts to those bodies but doesn't apply forces back to the world.

| Type | Description |
|---|---|
| Capsule Colliders | Array of `CapsuleCollider`s the cloth reacts to — typically the character's body capsules. |
| Sphere Colliders | Array of `ClothSphereColliderPair`s. A pair with only `first` set acts as a single sphere collider; setting both `first` and `second` forms a conic capsule shape, useful for modelling character limbs. |

## Scripting API — properties

| Member | Description |
|---|---|
| `stretchingStiffness` | Stretching stiffness of the cloth. |
| `bendingStiffness` | Bending stiffness of the cloth. |
| `useTethers` | Use Tether Anchors. |
| `useGravity` | Should gravity affect the cloth simulation? |
| `damping` | Damp cloth motion. |
| `externalAcceleration` | A constant, external acceleration applied to the cloth. |
| `randomAcceleration` | A random, external acceleration applied to the cloth. |
| `worldVelocityScale` | How much world-space movement of the character will affect cloth vertices. |
| `worldAccelerationScale` | How much world-space acceleration of the character will affect cloth vertices. |
| `friction` | The friction of the cloth when colliding with the character. |
| `collisionMassScale` | How much to increase mass of colliding particles. |
| `enableContinuousCollision` | Enable continuous collision to improve collision stability. |
| `useVirtualParticles` | Add one virtual particle per triangle to improve collision stability. |
| `clothSolverFrequency` | Number of cloth solver iterations per second. |
| `stiffnessFrequency` | Sets the stiffness frequency parameter. |
| `sleepThreshold` | Cloth's sleep threshold. |
| `capsuleColliders` | An array of `CapsuleCollider`s which this Cloth instance should collide with. |
| `sphereColliders` | An array of `ClothSphereColliderPair`s which this Cloth instance should collide with. |
| `coefficients` | The cloth skinning coefficients used to set up how the cloth interacts with the skinned mesh. |
| `selfCollisionDistance` | Minimum distance at which two cloth particles repel each other (default: 0.0). |
| `selfCollisionStiffness` | Self-collision stiffness — how strong the separating impulse should be for colliding particles. |
| `vertices` | The current vertex positions of the cloth object. |
| `normals` | The current normals of the cloth object. |
| `enabled` | Is this cloth enabled? |

## Scripting API — methods

| Member | Description |
|---|---|
| `ClearTransformMotion()` | Clear the pending transform changes from affecting the cloth simulation. |
| `GetSelfAndInterCollisionIndices()` | Get list of particles to be used for self and inter collision. |
| `SetSelfAndInterCollisionIndices()` | Set the cloth indices used for self and inter collision. |
| `GetVirtualParticleIndices()` | Get list of indices to be used when generating virtual particles. |
| `SetVirtualParticleIndices()` | Set indices to use when generating virtual particles. |
| `GetVirtualParticleWeights()` | Get weights to be used when generating virtual particles for cloth. |
| `SetVirtualParticleWeights()` | Set weights to be used when generating virtual particles for cloth. |
| `SetEnabledFading()` | Fade the cloth simulation in or out. |

## Supporting structs

### ClothSkinningCoefficient

| Field | Description |
|---|---|
| `maxDistance` | Distance a vertex is allowed to travel from the skinned mesh vertex position. |
| `collisionSphereDistance` | Definition of a sphere a vertex is not allowed to enter — allows collision against the animated cloth. |

### ClothSphereColliderPair

| Field | Description |
|---|---|
| `first` | The first `SphereCollider` of a `ClothSphereColliderPair`. |
| `second` | The second `SphereCollider` of a `ClothSphereColliderPair`. |

Cloth requires a Skinned Mesh Renderer — it is not a general-purpose flag/rope solver for non-skinned meshes. For character-body colliders that Cloth interacts with, see [collision.md](collision.md).

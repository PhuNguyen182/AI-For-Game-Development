# Ragdolls & Articulated Chains

Sources: Manual `wizard-RagdollWizard`, `RagdollStability`, `class-ArticulationBody`.

A classic ragdoll is Rigidbodies on Character Joints solved pairwise, so error accumulates along the chain and mass ratios matter a lot. `ArticulationBody` solves the whole hierarchy together.

## Wizard
1. Import a rigged skinned mesh with collider generation off.
2. `GameObject > 3D Object > Ragdoll...`; assign each limb transform. A wrong assignment gives a plausible rig that folds wrongly.
3. Confirm: generates Box Colliders, Rigidbodies and Character Joints on the existing Skinned Mesh Renderer.
4. Check in Play Mode, then save as a prefab.

Character Joint axes: Twist rotates along the limb, Swing 1 and Swing 2 are the lateral axes.

## Stability, in order

1. Adjacent masses within roughly 2x; about 10x is where the solver goes unstable, and no iteration count reliably compensates.
2. No small non-zero angular limit: below roughly 5-15 degrees it jitters. Give real range or set exactly 0, which locks cleanly.
3. No non-uniform scale anywhere in the hierarchy.
4. Disable Enable Preprocessing when a joint separates or moves erratically (typical when spawned in geometry).
5. Lower `maxDepenetrationVelocity` on bodies that start overlapping.
6. Default Solver Iterations to 10-20, project-wide cost paid by every jointed body.
7. Default Solver Velocity Iterations to 10-20, for bounce/impact response once position accuracy is adequate.
8. Projection only for extreme stretching.
9. Never move a joint-connected kinematic body by its Transform.

## ArticulationBody
- Reduced-coordinate solve of the whole chain; markedly more stable for deep chains.
- Body and joint are one component, configured on the child; the hierarchy defines the articulation.
- Fits robotic arms, mechanisms, ragdoll-like structures.
- Trade-off: no Character Joint twist/swing limit authoring, so a wizard ragdoll is not a drop-in conversion.

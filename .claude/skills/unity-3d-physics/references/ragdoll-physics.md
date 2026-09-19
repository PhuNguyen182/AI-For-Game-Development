# Ragdolls & Articulated Chains — Wizard, Stability, ArticulationBody

Sources: [Create a ragdoll](https://docs.unity3d.com/Manual/wizard-RagdollWizard.html), [Joint and ragdoll stability](https://docs.unity3d.com/Manual/RagdollStability.html), [Articulation Body](https://docs.unity3d.com/Manual/class-ArticulationBody.html).
Covers: SKILL.md §4 — **"Prefer `ArticulationBody` for anything that is structurally a chain"**, **"Fix ragdoll instability at the mass ratio and the limits before touching solver iterations"**.

A classic ragdoll is Rigidbodies joined by Character Joints, each solved as an
independent pairwise constraint. That is the root of every ragdoll stability
problem: the solver never sees the chain as one system, so error accumulates
along its length and mass ratios matter far more than they intuitively should.
`ArticulationBody` solves the whole hierarchy together and removes that class
of problem, at the cost of Character Joint's limit authoring.

## Wizard workflow

| Step | What it decides | Source |
|---|---|---|
| Import a rigged skinned mesh, collider generation off | The bone hierarchy the wizard maps limbs onto | [Create a ragdoll](https://docs.unity3d.com/Manual/wizard-RagdollWizard.html) |
| **GameObject > 3D Object > Ragdoll…** and assign each limb transform | Which bone becomes which body part; a mis-assignment produces a plausible rig that folds wrongly | [Create a ragdoll](https://docs.unity3d.com/Manual/wizard-RagdollWizard.html) |
| Confirm | Generates Box Colliders, Rigidbodies, and Character Joints over the existing Skinned Mesh Renderer | [Create a ragdoll](https://docs.unity3d.com/Manual/wizard-RagdollWizard.html) |
| Play Mode check, then save as a prefab | Verifies behaviour before the configuration is committed and reused | [Create a ragdoll](https://docs.unity3d.com/Manual/wizard-RagdollWizard.html) |

Character Joint axes follow the wizard's naming: **Twist** rotates a limb
along its own length, **Swing 1** and **Swing 2** are the two lateral axes.

## Stability, in the order to try it

| Rule | Why it comes first | Source |
|---|---|---|
| Keep adjacent connected masses within roughly 2× | Around 10× the pairwise joint solver becomes unstable, and no iteration count reliably compensates — this is the first thing to check on a flailing ragdoll | [Joint and ragdoll stability](https://docs.unity3d.com/Manual/RagdollStability.html) |
| Never leave a small non-zero angular limit | Below roughly 5–15° a limit jitters; either give the axis real range or set it to exactly 0, which locks it cleanly | [Joint and ragdoll stability](https://docs.unity3d.com/Manual/RagdollStability.html) |
| Avoid non-uniform scale anywhere in the hierarchy | Collider and joint robustness degrade in ways that present as tuning problems rather than as scale problems | [Joint and ragdoll stability](https://docs.unity3d.com/Manual/RagdollStability.html) |
| Disable Enable Preprocessing when a joint separates or moves erratically | Preprocessing destabilises joints whose constraints cannot be satisfied, which is exactly the state of a ragdoll spawned inside geometry | [Joint and ragdoll stability](https://docs.unity3d.com/Manual/RagdollStability.html) |
| Lower `maxDepenetrationVelocity` on bodies that start overlapping | Turns an explosive pop-out into a smooth separation | [Joint and ragdoll stability](https://docs.unity3d.com/Manual/RagdollStability.html) |
| Raise Default Solver Iterations to 10–20 | Only after the above — it is a **project-wide** cost paid by every jointed body, not by this ragdoll alone | [Joint and ragdoll stability](https://docs.unity3d.com/Manual/RagdollStability.html) |
| Raise Default Solver Velocity Iterations to 10–20 | For bounce and impact responses specifically, once position accuracy is already adequate | [Joint and ragdoll stability](https://docs.unity3d.com/Manual/RagdollStability.html) |
| Enable Projection only for extreme stretching | Forces compliance the solver could not reach, trading accuracy for a stable silhouette | [Joint and ragdoll stability](https://docs.unity3d.com/Manual/RagdollStability.html) |
| Never move a joint-connected kinematic body by its Transform | The write bypasses the pipeline and desynchronises the joint solver | [Joint and ragdoll stability](https://docs.unity3d.com/Manual/RagdollStability.html) |

## ArticulationBody

| Aspect | What it decides | Source |
|---|---|---|
| Solved as a hierarchy | The chain is resolved in reduced coordinates as one system, so error does not accumulate pairwise along its length — the reason it is markedly more stable for deep chains | [Articulation Body](https://docs.unity3d.com/Manual/class-ArticulationBody.html) |
| Body and joint in one component | Configuration lives on the child rather than split across a Rigidbody and a Joint, so the hierarchy itself defines the articulation | [Articulation Body](https://docs.unity3d.com/Manual/class-ArticulationBody.html) |
| Target use cases | Robotic arms, mechanisms, industrial simulation, and ragdoll-like structures where stability outweighs Character Joint's authoring | [Articulation Body](https://docs.unity3d.com/Manual/class-ArticulationBody.html) |
| Trade-off | Loses Character Joint's twist and swing limit authoring, so an existing wizard-generated ragdoll is not a drop-in conversion | [Articulation Body](https://docs.unity3d.com/Manual/class-ArticulationBody.html) |

For the joints themselves see [joints.md](joints.md); for the solver settings
these rules reach for last see
[physics-optimization.md](physics-optimization.md).

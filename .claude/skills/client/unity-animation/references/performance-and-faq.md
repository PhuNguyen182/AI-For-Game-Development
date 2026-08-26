# Performance — rig cost, transform optimisation, culling, measurement

Sources: [Mecanim performance and optimization](https://docs.unity3d.com/Manual/MecanimPeformanceandOptimization.html), [Modeling optimized characters](https://docs.unity3d.com/Manual/ModelingOptimizedCharacters.html), [Mecanim FAQ](https://docs.unity3d.com/Manual/MecanimFAQ.html), [Animator component](https://docs.unity3d.com/Manual/class-Animator.html), [Target matching](https://docs.unity3d.com/Manual/TargetMatching.html).
Covers: SKILL.md §4 — **"Set Culling Mode and Update Mode deliberately rather than leaving the defaults"**, **"Back any animation performance claim with a Profiler capture"**.

What animation actually costs and which choices move that number. Taking the
measurement itself is `unity-profiler-diagnostics`; this file is what to
change once the measurement says animation is the problem.

## Where the cost is

| Source of cost | What it depends on | Source |
|---|---|---|
| Retargeting | Present on Humanoid rigs and absent on Generic ones, so a character that never shares clips with another rig is paying for a feature it does not use | [Mecanim performance and optimization](https://docs.unity3d.com/Manual/MecanimPeformanceandOptimization.html) |
| Transform hierarchy | Every bone is a transform Unity writes each frame; bone count, not clip count, is the number that scales | [Modeling optimized characters](https://docs.unity3d.com/Manual/ModelingOptimizedCharacters.html) |
| Skinned renderers | Each renderer on a character is separate skinning work, so a body split into many pieces costs more than one mesh | [Modeling optimized characters](https://docs.unity3d.com/Manual/ModelingOptimizedCharacters.html) |
| Skinning quality | Bones per vertex is a per-project and per-mesh setting with a direct cost, and the highest setting is rarely visible on a small character | [Modeling optimized characters](https://docs.unity3d.com/Manual/ModelingOptimizedCharacters.html) |
| Layers and IK passes | Each additional layer and each enabled IK pass is more evaluation per frame, whether or not its weight is above zero | [Mecanim performance and optimization](https://docs.unity3d.com/Manual/MecanimPeformanceandOptimization.html) |

## What to change

| Change | Effect | Trade-off | Source |
|---|---|---|---|
| Optimise the transform hierarchy on import | Removes the exposed bone transforms and evaluates the skeleton internally, which is the largest single win on a crowd | Nothing can be parented to a bone any more unless it is explicitly named as an exposed transform | [Modeling optimized characters](https://docs.unity3d.com/Manual/ModelingOptimizedCharacters.html) |
| Culling Mode away from always animate | Stops paying for characters no renderer shows — see [animator-component.md](animator-component.md) | Culling completely lets the pose jump on return | [Animator component](https://docs.unity3d.com/Manual/class-Animator.html) |
| Generic instead of Humanoid | Drops the retargeting pass entirely | No retargeting, no muscle system, no goal-based IK | [Mecanim performance and optimization](https://docs.unity3d.com/Manual/MecanimPeformanceandOptimization.html) |
| Fewer bones in the rig | Scales down the per-frame transform work directly | Deformation quality, especially on faces and hands | [Modeling optimized characters](https://docs.unity3d.com/Manual/ModelingOptimizedCharacters.html) |
| One skinned renderer per character | Fewer skinning batches, and fewer draw calls behind them | Pieces cannot be hidden or swapped independently | [Modeling optimized characters](https://docs.unity3d.com/Manual/ModelingOptimizedCharacters.html) |

**Critical caveat**: every row above sounds obviously correct and several are
wrong for a given scene. A crowd of ten characters is not where transform
optimisation pays; a crowd of two hundred is. Capture before and after on the
target device, per `performance-and-algorithms.md`'s Verification section.

## Related behaviour worth knowing

| Subject | What it decides | Source |
|---|---|---|
| Target matching | Aligns a body part with a world position at a normalised point in a clip, which is how a vault or a climb lands on the ledge instead of near it | [Target matching](https://docs.unity3d.com/Manual/TargetMatching.html) |
| Humanoid proportions | The muscle system normalises poses across rigs, which is why a retargeted clip can look subtly different rather than wrong | [Mecanim FAQ](https://docs.unity3d.com/Manual/MecanimFAQ.html) |

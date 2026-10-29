---
name: unity-animation
description: "Mecanim: Animator, AnimatorController, Blend Tree, AnimatorOverrideController, Humanoid Avatar, AvatarMask, root motion, OnAnimatorIK, StateMachineBehaviour, Animation Events, PlayableGraph, Culling Mode. Use for clips, rigs and Animator graphs."
user-invocable: false
---

# Unity Animation

Not for: Timeline, the Animation Rigging package, the 2D Animation package (skeletal sprite rig) and skinning/bind poses/blend shapes (`SkinnedMeshRenderer`) — no owning skill: flag the gap, do not improvise; cameras reacting to Animator state (`unity-cinemachine-authoring`), sprite art/slicing (`unity-2d-sprite`), spline geometry (`unity-2d-spriteshape`), Spine rigs (`spine-animation`), the input/agent velocity behind a parameter (`unity-input-system`, `unity-navmesh-navigation`), ragdoll bodies/joints (`unity-3d-physics`), the logical state graph a parameter reflects (`stateless-state-machines`), Canvas/UI Toolkit transition wiring (`ugui`, `ui-toolkit`; UI Toolkit has no Animation Clip integration), the rule behind a state change (`csharp-engineer`).
Docs: `https://docs.unity3d.com/Manual/` and `/ScriptReference/` — unversioned (current docs); Mecanim = `animation-mecanim.html`, Playables = `Playables.html`.

| Reference | Read when |
|---|---|
| [mecanim-overview.md](references/mecanim-overview.md) | Importing/authoring a clip, choosing Animation Type, or an Animation Event does not fire |
| [avatar-setup.md](references/avatar-setup.md) | Humanoid rig, retargeting, Avatar Mask, root motion misbehaving, or IK |
| [animator-controller.md](references/animator-controller.md) | Building or debugging states, transitions, Blend Trees, layers |
| [animator-component.md](references/animator-component.md) | Configuring Culling/Update Mode or scripting playback and parameters |
| [animator-override-controller.md](references/animator-override-controller.md) | One state machine must serve several clip sets |
| [playables-api.md](references/playables-api.md) | The state machine cannot express the blend |
| [performance-and-faq.md](references/performance-and-faq.md) | Animation shows in a profile, or a rig is being budgeted |

## Steps
1. **Set the Animation Type before importing anything**, per [mecanim-overview.md](references/mecanim-overview.md) — Humanoid buys retargeting and costs a per-frame pass; Generic costs/offers neither; Legacy only for content already on it. Changing it later invalidates every clip and Avatar built on it.
2. **Check the Avatar's pose before chasing a retargeting problem**, per [avatar-setup.md](references/avatar-setup.md) — the pose warning is about the pose, not bone mapping. Source and target must both be Humanoid with valid Avatars.
3. **Decide the root-motion source at import** — baked into pose vs applied by the component; implementing the movement callback takes the decision from the component. Drift or no movement is almost always this.
4. **Keep clip content in the Animation window and flow in the Animator window** — events belong to a clip, not a state.
5. **Build explicit transitions; reserve Any State for real interrupts** — disable exit time and self-transition there, set an interruption source. See [animator-controller.md](references/animator-controller.md).
6. **Pick the Blend Tree form from the parameter shape**: 1D for one axis, 2D variants for two (direction/magnitude or independent axes), Direct for per-child weights.
7. **Use normalised time for transitions on any controller that may be overridden** — a fixed seconds duration outlives a shorter override clip.
8. **Set Culling Mode and Update Mode deliberately**, per [animator-component.md](references/animator-component.md): Always Animate pays for unseen characters; Cull Completely freezes the state machine so the pose jumps on return; Animate Physics keeps a kinematic body in step.
9. **Cache parameter hashes** (`Animator.StringToHash` in a static readonly field) — string overloads hash per call (`csharp-standards` → `performance-and-algorithms.md`).
10. **Share a graph through an Override Controller, not a duplicate**; apply overrides as one batch on a deliberate event, per [animator-override-controller.md](references/animator-override-controller.md).
11. **Use the Playables API only when the state machine cannot express the need** (`csharp-standards` → `coding-principles.md`, YAGNI), and pair every created graph with an explicit destroy — per [playables-api.md](references/playables-api.md).
12. **Keep gameplay decisions in `Game.Core.*`** — a `StateMachineBehaviour`, movement callback or Animation Event handler only carries out or reports what Core decided; an event never resolves a hit (`csharp-standards` → `coding-principles.md`, Shared Core integrity).
13. **Back any animation performance claim with a Profiler capture on the target device**, per [performance-and-faq.md](references/performance-and-faq.md) and `csharp-standards` → `performance-and-algorithms.md` (Verification).

## Never
- Conclude a bone mapping is wrong from a pose warning.
- Expect the IK callback to run without the layer's IK Pass or on a non-Humanoid rig — silent in both cases.
- Add a layer and expect it to act at default weight (non-base layers start at 0).
- Leave a trigger set with no transition able to consume it — it fires later at an unexplained moment; clear it with `ResetTrigger`.
- Put an Animation Event on the final frame of a non-looping clip, or its handler on a child of the `Animator` object.
- Write the transform while root motion is applied — one of the two wins.
- Access Animator parameters by string in a per-frame path.
- Improvise Timeline, Animation Rigging, 2D Animation or skinning guidance from Mecanim knowledge.

## Output
```
## Animation — <character or feature>
- Animation Type: <Humanoid / Generic / Legacy> — why, incl. retargeting need
- Avatar: <new / retargeted / template>, pose verified <yes/no>, masks
- Clips: <loop, root-motion bake, events>
- Root motion: <baked / component / movement callback>
- Controller: <states, transitions, Any State use, Blend Tree form, layers>
- Animator: Culling Mode, Update Mode — rationale for each non-default
- Override Controller / Playables: <base + variants, graph destroy point — or n/a>
- Verified: <Profiler capture behind any performance claim, or "not run">
- Known limitations: <...>
```
On request only, add `Latent concerns` and `Future remediation`, each with its trigger.

## Example
- "Resolve the hit inside the Animation Event on the attack clip" → declined: puts a game rule in the animation layer and relies on an event near clip end; the event now reports the attack window opened and Core decides the hit.

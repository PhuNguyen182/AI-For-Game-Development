---
name: unity-animation
description: >
  Technique for Unity's Mecanim animation system — `Animator`, Animator
  Controller state machines, transitions, Any State, parameters and
  `StateMachineBehaviour`, Blend Trees, layers and Avatar Masks,
  `AnimationClip` import and Animation Events, Humanoid Avatar setup and
  retargeting, `OnAnimatorMove` root motion, `OnAnimatorIK` inverse
  kinematics, `AnimatorOverrideController` clip swapping, Culling Mode and
  Update Mode, and the `PlayableGraph` API underneath. Use for any Animator
  asset, clip, humanoid rig, or playback script. Not for: Timeline sequencing
  and the Animation Rigging package (no owning skill — flag the gap); cameras
  reacting to Animator state (`unity-cinemachine-authoring`); sprite art
  (`unity-2d-sprite`); Spine runtimes (`spine-animation`); the rule behind a
  state change (`csharp-engineer`).
---

# Unity Animation — Mecanim, Avatars, Controllers, Blend Trees, Playables

## Bundled resources

### References
Read-only context, loaded on demand so SKILL.md itself stays short.

| File | Contents | Read when |
|---|---|---|
| [root-links.md](references/root-links.md) | Manual and Script Reference roots, the type index, and what sits adjacent but outside | Starting any task here, or deciding whether a request is even Mecanim |
| [mecanim-overview.md](references/mecanim-overview.md) | Animation Types, clip import settings, loop options, the Animation window, Animation Events | Importing or authoring a clip, or an event does not fire |
| [avatar-setup.md](references/avatar-setup.md) | Mapping, Muscles, T-pose, Human Templates, retargeting, Avatar Masks, root motion, IK | Working with a humanoid rig, or motion goes to the wrong place |
| [animator-controller.md](references/animator-controller.md) | States, transitions and their timing fields, parameters, Blend Trees, layers, sub-state machines, `StateMachineBehaviour` | Building or debugging the state graph |
| [animator-component.md](references/animator-component.md) | Component fields, Culling Mode, Update Mode, playback and parameter scripting | Configuring the component, or driving it from code |
| [animator-override-controller.md](references/animator-override-controller.md) | Clip swapping for variants, batching overrides, the timing constraint it imposes | One state machine has to serve several visual variants |
| [playables-api.md](references/playables-api.md) | `PlayableGraph`, mixers, custom behaviours, graph lifetime | The state machine cannot express the blend |
| [performance-and-faq.md](references/performance-and-faq.md) | Rig cost, Humanoid against Generic, transform optimisation, renderer count | Animation shows up in a profile, or a rig is being budgeted |

## 1. Objective
Get animation playing, blending, and retargeting correctly, at a cost the target device can afford. Mecanim's characteristic failures are configuration that looks complete: an IK callback that never runs because the layer's IK pass is off, a new layer whose weight is zero so its clips play into nothing, a trigger that stays armed and fires a state change minutes later, an Any State transition with exit time enabled that refuses to interrupt anything, and a retarget blamed on bone mapping when the source model is simply not in a T-pose.

## 2. Role
Act as the Mecanim specialist for the client track — the tool reached for whenever a character, prop, or UI element has to play, blend, or retarget animation. You wire and tune the animation system; you do not decide what state the game should be in, author the underlying art, or drive cameras from animation state.

## 3. When to invoke this skill
- Importing or authoring animation clips: Animation Type, loop settings, root-motion bake options, curves, Animation Events.
- Setting up a Humanoid Avatar, retargeting clips across rigs, or building an Avatar Mask.
- Building or debugging an Animator Controller: states, transitions, parameters, Blend Trees, layers, sub-state machines, per-state behaviours.
- Configuring the `Animator` component, or scripting playback and parameters from gameplay code.
- Sharing one state machine across skins, weapons, or species through clip overrides.
- Scripting root motion or inverse kinematics.
- Building a `PlayableGraph` by hand for blending the state machine cannot express.
- Animation appears in a profile, or a rig's cost needs budgeting before it ships.
- Negative trigger: Timeline track and clip sequencing, or the Animation Rigging package's constraint rigs — both sit on top of or beside what this skill covers, and no skill in this project owns either; say so rather than improvising.
- Negative trigger: a camera that reacts to Animator state — that is `unity-cinemachine-authoring`, which consumes the states authored here.
- Negative trigger: the sprite art, atlas, or slicing behind a frame-swap animation — that is `unity-2d-sprite`, and spline geometry is `unity-2d-spriteshape`; this skill only plays what they produce.
- Negative trigger: a Spine-rigged character — that is `spine-animation`, a separate runtime with its own state machine that does not go through Mecanim.
- Negative trigger: where a parameter's value comes from before it reaches the Animator — the stick or button behind it is `unity-input-system`, an agent's velocity is `unity-navmesh-navigation`; this skill owns the parameter and what it drives, not its source.
- Negative trigger: the ragdoll a death animation hands over to, and the bodies and joints behind it — that is `unity-3d-physics`; this skill owns the blend back into animation, not the simulation.
- Negative trigger: whether the attack that the animation depicts actually lands, or when a cooldown expires — that is `csharp-engineer`'s Shared Core, per `coding-principles.md`'s Shared Core integrity rule.

## 4. How to use this skill
1. **Set the Animation Type before anything else is imported** — Humanoid buys retargeting across rigs and costs a per-frame retargeting pass, Generic costs neither and offers neither, and Legacy exists only for content that already depends on it, per [mecanim-overview.md](references/mecanim-overview.md) and the roots in [root-links.md](references/root-links.md). Changing it later invalidates every clip and Avatar built against it.
2. **Verify the Avatar's pose before investigating a retargeting problem** — the pose warning is about the pose, not the bone mapping, and remapping bones to chase it wastes the afternoon, per [avatar-setup.md](references/avatar-setup.md). Both source and target must be Humanoid with a valid Avatar for retargeting to happen at all.
3. **Decide where root motion comes from at import time** — baking motion into the pose and applying root motion at runtime are opposite choices, and implementing the movement callback takes the decision away from the component entirely, per [avatar-setup.md](references/avatar-setup.md). A character that drifts or refuses to move is almost always this.
4. **Author clip content in the Animation window and flow in the Animator window** — keys, curves and events belong to the clip, states and transitions belong to the graph, and confusing the two is why an event appears to be attached to a state, per [mecanim-overview.md](references/mecanim-overview.md).
5. **Build the graph from explicit transitions and reserve Any State for genuine interrupts** — an Any State transition retriggers the state it is already in unless that is turned off, and it will not interrupt anything while exit time is enabled, per [animator-controller.md](references/animator-controller.md). Sub-state machines are for readability once the graph stops fitting on screen.
6. **Pick the Blend Tree form from the shape of the parameter driving it** — one parameter is one dimension, two independent axes need the two-dimensional form and the right variant for whether direction or magnitude matters, and the direct form gives each child its own parameter for additive layering, per [animator-controller.md](references/animator-controller.md).
7. **Express transition timing in normalised time whenever clips can be overridden** — a fixed duration in seconds outlives a shorter override clip and swallows the transition, per [animator-override-controller.md](references/animator-override-controller.md).
8. **Set Culling Mode and Update Mode deliberately rather than leaving the defaults** — always-animate pays for characters nobody can see, culling completely freezes the state machine so the pose jumps on return, and the physics update mode is what keeps an animated kinematic body in step, per [animator-component.md](references/animator-component.md) and [performance-and-faq.md](references/performance-and-faq.md).
9. **Drive parameters through cached hashes rather than strings** — the string overloads hash the name on every call, which `performance-and-algorithms.md` names directly; cache the hash once in a static field and use the integer overloads, per [animator-component.md](references/animator-component.md).
10. **Swap clips through an Override Controller instead of duplicating the controller** — one graph and one set of transitions stay the single source of truth, and applying the overrides as a batch avoids re-resolving the controller once per clip, per [animator-override-controller.md](references/animator-override-controller.md).
11. **Reach for the Playables API only when the state machine cannot express the need** — runtime-composed blending or per-frame animation maths, not ordinary gameplay animation, per YAGNI in `coding-principles.md`. A graph created here is not garbage collected, so pair its creation with an explicit destroy, per [playables-api.md](references/playables-api.md).
12. **Keep every gameplay decision in `Game.Core.*`** — a per-state behaviour, a movement callback, and an Animation Event handler carry out or report what Core already decided, per `coding-principles.md`'s Shared Core integrity rule. An animation event is not a place to resolve a hit.
13. **Back any animation performance claim with a Profiler capture** — rig cost, culling changes and bone-count reductions all sound obviously right and are routinely wrong on the actual device, per `performance-and-algorithms.md`'s Verification section and [performance-and-faq.md](references/performance-and-faq.md).

## 5. Specific goals / tasks this skill performs
- Setting Animation Type and clip import settings, and authoring clips, curves and Animation Events.
- Configuring Humanoid Avatars, Human Templates, Avatar Masks, and retargeting across rigs.
- Building Animator Controller graphs: states, transitions, parameters, Blend Trees, layers, sub-state machines, per-state behaviours.
- Configuring the `Animator` component and scripting playback and parameters from gameplay code.
- Scripting root motion and inverse kinematics.
- Authoring Override Controllers for visual variants sharing one graph.
- Building hand-written playable graphs where the state machine cannot express the blend.
- Diagnosing and budgeting animation cost: rig type, transform optimisation, culling, renderer count.
- Out of scope: Timeline sequencing and the Animation Rigging package (no owning skill — flag the gap); cameras reacting to Animator state (`unity-cinemachine-authoring`); sprite art and slicing (`unity-2d-sprite`); spline geometry (`unity-2d-spriteshape`); Spine-rigged characters (`spine-animation`); the input or agent velocity behind a parameter (`unity-input-system`, `unity-navmesh-navigation`); ragdoll simulation (`unity-3d-physics`); the gameplay rule behind a state change (`csharp-engineer`).

## 6. Output format
```
## Animation Work — <character or feature name>
- Scope confirmed: Mecanim — not Timeline, Animation Rigging, Spine, or sprite authoring
- Animation Type: <Humanoid / Generic / Legacy> — and why, including retargeting need
- Avatar: <new / retargeted / reused template>, pose verified <yes/no>, masks used
- Clips: <imported or authored>, loop settings, root-motion bake, Animation Events added
- Root motion: <baked into pose / applied by the component / taken over by the movement callback>
- Controller: <states and transitions, interruption and exit-time choices, Any State usage>
- Blend Trees: <form used and the parameter shape behind it>
- Layers: <weights, blending mode, masks, sync — or "base layer only">
- Animator component: Culling Mode, Update Mode, and the rationale for each non-default
- Parameter access: <cached hashes confirmed>
- Override Controller: <base controller and variants — or "not applicable">
- Playables: <why the graph was needed and where it is destroyed — or "not applicable">
- Shared Core boundary: confirmed no gameplay outcome decided in animation-layer code
- Verified on: <Profiler capture behind any performance claim, or "no claim made">
- Layer: Game.Client.* assets and scripts
- Known limitations: <...>
```

**Extended report — emit ONLY when the requester asks for it.** It replaces the one-line `Known limitations` above with all three fields:
```
- Known limitations: <what the delivered animation setup does not cover>
- Latent concerns: <failure modes not yet triggered: rigs untested, device tiers unmeasured, trade-offs knowingly deferred>
- Future remediation: <the concrete fix for each concern above, each with the condition that should trigger it>
```

## 7. Examples
**Example 1**
- Input: "Locomotion for the player: idle, walk and run blended by speed, with a jump that can interrupt at any time."
- Output: Humanoid, since the same clips are reused across two body types, with the Avatar's pose checked before anything else. A one-dimensional Blend Tree over a speed parameter with thresholds matching each clip's authored speed, and a jump reached from Any State with exit time disabled so it fires immediately, self-transition turned off so a second press does not restart it, and an interruption source set so the transition can actually be cut short. Culling Mode set to cull transforms rather than left always animating. Parameters driven through cached hashes.

**Example 2**
- Input: "The IK hand placement script does nothing, but the callback is definitely implemented."
- Output: the layer's IK pass was off, so the callback was never invoked at all — nothing logs this, and the script looks correct in isolation. Enabled it on the layer that owns the arms, and confirmed the rig is Humanoid, since the goal-based IK covered here exists only there. Noted that a constraint-based rig would be the Animation Rigging package, which no skill in this project owns.

**Example 3**
- Input: "Three enemy variants share a combat graph but each needs its own clips, and armour swaps by equipped gear."
- Output: one base controller for the shared graph, plus an Override Controller per variant. Transitions rewritten in normalised time first, because the variants' clips differ in length and a fixed duration in seconds would have swallowed the transition on the shortest ones. Overrides applied as a batch on each equip change rather than per clip, and the equip decision itself read from Shared Core rather than made here.

**Example 4**
- Input: "Just resolve the hit inside the Animation Event on the attack clip, it is already at the right frame."
- Output: declined — that puts a game rule in the animation layer, against `coding-principles.md`'s Shared Core integrity rule, and it also depends on an event firing near the end of a clip, which is unreliable. The event now reports that the attack window opened, and Core decides whether anything was hit.

## 8. Edge cases & guardrails
- Never conclude a bone mapping is wrong from a pose warning — the pose is what the warning is about, and remapping will not fix it.
- Never expect the IK callback to run without the layer's IK pass enabled, or on a non-Humanoid rig — it is silent in both cases.
- Never add a layer and expect it to do anything at its default weight — a non-base layer starts at zero and plays into nothing.
- Never leave an Any State transition on its defaults for an interrupt — exit time enabled stops it interrupting, and self-transition enabled restarts the state it is already in.
- Never leave a trigger set with no transition able to consume it — it stays armed and fires the change later, at a moment nothing in the code explains.
- Never place an Animation Event on the final frame of a clip that does not loop — firing there is unreliable; move it earlier.
- Never put an Animation Event handler on a child object — the method has to live on a component of the same object as the `Animator`.
- Never write to the transform while root motion is being applied — one of the two wins, and which one depends on whether the movement callback is implemented.
- Never leave Culling Mode always animating for a character that leaves the screen, and never cull completely where a visible pose jump on return is unacceptable.
- Never access Animator parameters by string in a per-frame path — cache the hash, per `performance-and-algorithms.md`.
- Never author a transition duration in seconds on a controller that will be overridden — a shorter override clip swallows it.
- Never create a playable graph without an explicit destroy — it is not garbage collected, and the leak lasts the session.
- Never resolve a gameplay outcome inside a per-state behaviour, a movement callback, or an event handler — report it and let `Game.Core.*` decide.
- Never claim an animation optimisation without a Profiler capture behind it, per `performance-and-algorithms.md`'s Verification section.
- Never improvise Timeline or Animation Rigging guidance from Mecanim knowledge — neither has an owning skill here; flag the gap instead.

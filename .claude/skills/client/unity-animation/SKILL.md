---
name: unity-animation
description: >
  Technique for Unity's Mecanim animation system (`UnityEngine.Animator`,
  `UnityEngine.AnimatorController`/state machines, `UnityEngine.AnimationClip`,
  `UnityEngine.Avatar`, `UnityEngine.Playables.*`) — Animation Clips (import
  settings, curves, Animation Events, loop settings, the Animation window),
  Humanoid/Generic/Legacy Animation Types, Avatar creation and configuration
  (Mapping, Muscles & Settings, T-pose, retargeting, root motion, Inverse
  Kinematics), the Animator component (Controller, Avatar, Apply Root Motion,
  Update Mode, Culling Mode), Animator Controller state machines (states,
  transitions, Any State, parameters, Blend Trees 1D/2D/Direct, sub-state
  machines, layers, Avatar Masks, `StateMachineBehaviour`), Animator Override
  Controller (clip swapping for skins/weapon variants), the low-level
  Playables API (`PlayableGraph`, `AnimationMixerPlayable`,
  `AnimationLayerMixerPlayable`, custom `PlayableBehaviour`), and Mecanim
  performance/optimization (Culling Mode choice, hashed parameter access,
  bone-count/rig-complexity cost, `SkinnedMeshRenderer` count). Use this for
  any task touching `Animator`, an Animator Controller asset, `AnimationClip`
  authoring/import, Avatar setup/retargeting, root motion or IK scripting,
  `AnimatorOverrideController`, or a hand-built `PlayableGraph` — e.g. "wire
  up the Animator Controller for the player's locomotion blend tree", "set up
  the Humanoid Avatar and retarget clips across two character models", "the
  attack animation needs a hit-event and root motion", "swap this
  character's animation clips for their armor skin without duplicating the
  controller". Do not use this for Cinemachine camera behavior that merely
  *reacts to* an Animator state (`CinemachineStateDrivenCamera`) — that's
  `unity-cinemachine-authoring`. Do not use this for Unity's Timeline package
  (`PlayableDirector`/`TimelineAsset` track/clip sequencing) — Timeline is
  built on Playables but track/clip authoring itself is a separate system not
  covered here. Do not use this for the Animation Rigging package
  (`com.unity.animation.rigging`, constraint-based runtime IK rigs) — that's
  a separate installable package distinct from the built-in Animator IK pass
  covered here. Do not use this for authoring the underlying Sprite/mesh art
  or slicing spritesheets (`unity-2d-sprite`) or Sprite Shape splines
  (`unity-2d-spriteshape`) — this skill only wires already-authored art into
  Animator playback. Do not use this for gameplay rule logic that happens to
  be expressed through animation state (whether an attack connects, a
  cooldown, a damage/health decision) — that belongs in Shared Core per
  `coding-principles.md`'s Shared Core integrity rule; this skill only covers
  wiring the Unity-side animation components/assets themselves.
---

# Unity Animation — Mecanim (Animator, Animation Clips, Avatar, Blend Trees, Playables)

Sources: see [references/](references/) for the Unity Manual root links, split by topic — [root-links.md](references/root-links.md), [mecanim-overview.md](references/mecanim-overview.md), [avatar-setup.md](references/avatar-setup.md), [animator-component.md](references/animator-component.md), [animator-controller.md](references/animator-controller.md), [animator-override-controller.md](references/animator-override-controller.md), [playables-api.md](references/playables-api.md), [performance-and-faq.md](references/performance-and-faq.md), [scripting-api.md](references/scripting-api.md).

## 1. Objective
Configure Unity's Mecanim animation pipeline correctly — right Animation Type (Humanoid/Generic/Legacy) and clip import settings, right Avatar configuration for retargeting, right Animator Controller state-machine/blend-tree/layer structure, right `Animator` component performance settings (Culling Mode, Update Mode, hashed parameters), right choice between `AnimatorOverrideController` and the low-level Playables API — without drifting into Cinemachine camera logic, Timeline sequencing, Animation Rigging constraints, sprite/mesh art authoring, or gameplay rule logic that belong to sibling skills or `Game.Core.*`.

## 2. Role
Act as the Mecanim animation specialist: given a need for character/object animation playback, blending, retargeting, or event-driven animation reactions, you choose and configure the right `UnityEngine.Animator`/`UnityEngine.Playables`-namespace components and assets — you don't decide gameplay outcomes from animation state (that's Shared Core's job), and you don't reach into Cinemachine, Timeline, Animation Rigging, or sprite/mesh authoring, which are sibling skills'/roles' territory.

## 3. When to invoke this skill
- Authoring or importing **Animation Clips** — Humanoid/Generic/Legacy Animation Type, loop settings, root motion bake options, custom curves, **Animation Events**, or working in the Animation window (as distinct from the Animator window).
- Setting up a **Humanoid Avatar** — bone Mapping, T-pose, Muscles & Settings, Human Templates, retargeting clips across different character rigs, or an **Avatar Mask**.
- Configuring the **`Animator` component** — `Controller`/`Avatar` assignment, `Apply Root Motion`, `Update Mode`, **`Culling Mode`** (directly relevant to this project's performance rules), or scripting playback/parameters (`Play`/`CrossFade`/`SetFloat`/`SetTrigger`, hashed via `Animator.StringToHash`).
- Building or editing an **Animator Controller** state machine — states, transitions (exit time, conditions, interruption), **Any State**, parameters, **Blend Trees** (1D/2D Simple-Freeform-Directional/Cartesian/Direct), sub-state machines, **layers** (weight, Override/Additive, Avatar Mask, Sync), or a **`StateMachineBehaviour`**.
- Swapping animation clips across visual variants (skins, weapons, character races) sharing one state machine via an **`AnimatorOverrideController`**.
- Scripting **root motion** (`OnAnimatorMove`) or **Inverse Kinematics** (`OnAnimatorIK`, `AvatarIKGoal`).
- Building a hand-written **`PlayableGraph`** (`AnimationMixerPlayable`, `AnimationLayerMixerPlayable`, custom `PlayableBehaviour`) for procedural/runtime-composed animation blending the state machine can't express.
- Diagnosing or improving **animation performance** — Culling Mode choice, hashed parameter access, `SkinnedMeshRenderer` count, bone/rig complexity, Humanoid retargeting cost vs. Generic.
- Negative trigger: Cinemachine camera behavior that reacts to an Animator's current state (`CinemachineStateDrivenCamera`) or Timeline `CinemachineTrack`/`CinemachineShot` sequencing — that's `unity-cinemachine-authoring`.
- Negative trigger: authoring Timeline tracks/clips/sequencing (`PlayableDirector` driving a `TimelineAsset`) — Timeline is built on Playables but is a distinct authoring system not covered here.
- Negative trigger: the Animation Rigging package (`com.unity.animation.rigging`) — a separate constraint-based runtime IK rig package, distinct from the built-in Animator IK pass this skill covers.
- Negative trigger: authoring the underlying Sprite art/spritesheet slicing (`unity-2d-sprite`) or Sprite Shape splines (`unity-2d-spriteshape`) — this skill only wires already-imported art (mesh or Sprite) into Animator playback.
- Negative trigger: the actual gameplay decision an animation state happens to represent (whether an attack lands, a cooldown expiring, a health/damage outcome) — that's `csharp-engineer`'s Shared Core, per `coding-principles.md`'s Shared Core integrity rule; this skill stops at wiring/playing whatever state Core already decided.

## 4. How to use this skill
1. **Confirm scope first.** This skill is Mecanim itself (Animation Clips, Avatar, Animator, Animator Controller, Animator Override Controller, Playables). If the task is Cinemachine camera logic, hand off to `unity-cinemachine-authoring`. If it's Timeline track/clip sequencing or Animation Rigging constraints, flag that those are separate systems this skill doesn't cover. If it's the underlying Sprite/mesh art itself, hand off to `unity-2d-sprite`/`unity-2d-spriteshape`.
2. **Set the right Animation Type before anything else**, per [mecanim-overview.md](references/mecanim-overview.md): `Humanoid` for bipedal characters needing clip retargeting across rigs, `Generic` for everything else (creatures, props, vehicles, sprite-swap "animation"), `Legacy` only for pre-existing content that already depends on it — never for new work.
3. **Configure the Avatar deliberately for Humanoid rigs**, per [avatar-setup.md](references/avatar-setup.md): verify/enforce T-pose, map required bones, adjust Muscles & Settings only where the rig genuinely needs stiffness/stretch limits, and save a Human Template when the same mapping will be reused across multiple similarly-rigged models.
4. **Author clips and events in the right window**, per [mecanim-overview.md](references/mecanim-overview.md): the Animation window for keyframes/curves/Animation Events on a specific clip, the Animator window for the state-machine flow between clips — never conflate the two. Verify loop settings (Loop Time/Loop Pose, root transform XZ) before shipping a looping locomotion clip.
5. **Build the Animator Controller state machine**, per [animator-controller.md](references/animator-controller.md): explicit states/transitions for routine flow, Any State reserved for genuine global interrupts, the right Blend Tree type for the parameter shape (1D/2D Simple-Freeform/Direct), sub-state machines for readability once a graph grows complex, and layers + Avatar Masks for body-region-specific animation.
6. **Configure the `Animator` component's performance-relevant fields deliberately**, per [animator-component.md](references/animator-component.md) and [performance-and-faq.md](references/performance-and-faq.md): set `Culling Mode` to `Cull Update Transforms`/`Cull Completely` for any character that can go offscreen (never leave it at `Always Animate`), pick `Update Mode` based on whether root motion/IK needs physics lock-step, and always drive parameters through cached `Animator.StringToHash` results in hot paths — never raw strings.
7. **Respect the Shared Core boundary.** Any gameplay decision that happens to manifest through animation state (an attack's hit window, a cooldown, a damage outcome) is decided in `Game.Core.*`; `StateMachineBehaviour`, `OnAnimatorMove`/`OnAnimatorIK`, and Animation Event handler methods only carry out or signal whatever Core already decided — they never decide it themselves, per `coding-principles.md`'s Shared Core integrity rule.
8. **Use `AnimatorOverrideController` for shared-state-machine visual variants** ([animator-override-controller.md](references/animator-override-controller.md)) instead of duplicating an Animator Controller per skin/weapon set — batch multiple clip swaps via `ApplyOverrides`, not repeated indexer writes.
9. **Reach for the Playables API only when the state machine genuinely can't express the requirement** ([playables-api.md](references/playables-api.md)) — runtime-procedural blending, dynamically composed mixing graphs, or custom per-frame animation math; always pair `PlayableGraph.Create()` with an explicit `Destroy()` in teardown, since a `PlayableGraph` is not garbage-collected. Default to Animator Controller + `Animator` for ordinary gameplay animation, per YAGNI in `coding-principles.md`.
10. **Validate any performance claim with a measurement** (Unity Profiler), not asserted from the optimization guide alone, per `performance-and-algorithms.md`'s Verification section — this applies to Culling Mode changes, bone-count reductions, or any other animation optimization handed off in a review note.
11. **State the hand-off explicitly.** Camera behavior reacting to Animator state → `unity-cinemachine-authoring`. Sprite/mesh art authoring → `unity-2d-sprite`/`unity-2d-spriteshape`. Gameplay decisions behind animation state → `csharp-engineer`'s Shared Core.

## 5. Specific goals / tasks this skill performs
- Setting Animation Type (Humanoid/Generic/Legacy) and configuring clip import settings (loop, root motion bake, compression, curves, Avatar Mask).
- Authoring/editing Animation Clips and Animation Events, natively or on imported clips.
- Configuring Humanoid Avatars (Mapping, Muscles & Settings, T-pose, Human Templates) and retargeting animation across rigs.
- Configuring the `Animator` component (`Controller`, `Avatar`, `Apply Root Motion`, `Update Mode`, `Culling Mode`) and scripting playback/parameters.
- Building Animator Controller state machines — states, transitions, Any State, parameters, Blend Trees, sub-state machines, layers, Avatar Masks, `StateMachineBehaviour`.
- Scripting root motion (`OnAnimatorMove`) and Inverse Kinematics (`OnAnimatorIK`, `AvatarIKGoal`).
- Authoring `AnimatorOverrideController` assets for clip-swapping visual variants.
- Building hand-written `PlayableGraph`s for procedural/runtime animation blending when the state machine can't express the need.
- Diagnosing and improving Mecanim runtime performance (Culling Mode, hashed parameters, rig/bone complexity, `SkinnedMeshRenderer` count).
- Out of scope: Cinemachine camera logic (`unity-cinemachine-authoring`); Timeline track/clip sequencing; the Animation Rigging package; Sprite/mesh art authoring (`unity-2d-sprite`/`unity-2d-spriteshape`); gameplay rule logic driving animation state (`csharp-engineer`'s Shared Core).

## 6. Output format
```
## Animation Work — <character/feature name>
- Scope confirmed: Mecanim animation pipeline (not Cinemachine, not Timeline, not Animation Rigging, not sprite/mesh art authoring)
- Animation Type (if applicable): <Humanoid/Generic/Legacy>, rationale
- Avatar (if applicable): configuration status <new/retargeted/reused via Human Template>, T-pose verified <yes/no>, Avatar Mask(s) used
- Animation Clips (if applicable): source <imported/native>, loop settings, root motion bake settings, Animation Events added
- Animator component: Controller/Avatar assigned, Apply Root Motion, Update Mode, Culling Mode <and rationale for non-default choice>
- Animator Controller (if applicable): states/transitions summary, Blend Tree type(s) used, layers/Avatar Masks, StateMachineBehaviour(s)
- Animator Override Controller (if applicable): base controller, variant(s) created
- Playables API (if applicable): why the state machine couldn't express this, graph lifecycle (Destroy() call confirmed)
- Shared Core boundary: confirmed no gameplay decision made in animation-layer code
- Hand-off: <camera reaction → unity-cinemachine-authoring / sprite art → unity-2d-sprite / gameplay logic → csharp-engineer, as applicable>
- Known limitations: <...>
```

## 7. Examples
**Example 1**
- Input: "Set up locomotion for the player character: idle, walk, run blended by speed, with a jump that can interrupt at any time."
- Output: Animation Type = Humanoid, Avatar configured and T-pose verified; base layer state machine with an `Idle/Walk/Run` state containing a 1D Blend Tree (parameter `Speed`, thresholds 0/2/5 matching each clip's authored root-motion speed) and a separate `Jump` state; an Any State → `Jump` transition gated on a `Jump` Trigger parameter with `Has Exit Time` disabled for immediate response; `Animator.Culling Mode` set to `Cull Update Transforms` since the player can go offscreen briefly during cutscenes; all parameter access in the player controller script uses cached `Animator.StringToHash` results.
- Hand-off: none needed — entirely within this skill's scope; the player-movement-speed calculation itself (if it affects gameplay rules like stamina drain) stays in `csharp-engineer`'s Shared Core, this skill only reads the already-resolved speed value into the `Speed` parameter.

**Example 2**
- Input: "Three enemy variants (goblin, ogre, elf) need to share the same combat state machine but each has its own attack/idle/death clips, and armor pieces should swap out visually based on equipped gear from the inventory system."
- Output: one base Animator Controller built for the shared combat state machine; three `AnimatorOverrideController` assets (one per variant) remapping the base clips to each variant's own animation set, transitions authored with `Has Exit Time` in normalized time (not seconds) since override clips differ in length; armor-piece skin swapping uses a second override layer applied via `ApplyOverrides` batched per equip-change event rather than per-frame.
- Hand-off: which armor/weapon is currently equipped is read from `Game.Core.*` inventory state; this skill's code only performs the `runtimeAnimatorController`/override assignment once Core signals a change — the equip decision itself is out of scope here.

## 8. Edge cases & guardrails
- Never assume this skill covers Cinemachine camera behavior — a `CinemachineStateDrivenCamera`/`CinemachineTrack` reacting to an Animator's state is `unity-cinemachine-authoring`'s territory, even though it reads Animator state this skill configures.
- Never assume Timeline track/clip authoring (`PlayableDirector` + `TimelineAsset`) is in scope — Timeline is built on the Playables API this skill does cover, but sequencing tracks/clips in the Timeline window is a distinct authoring workflow not addressed here.
- The Animation Rigging package (`com.unity.animation.rigging`) is a separate installable package for constraint-based runtime IK rigs — do not conflate it with the built-in Animator IK pass (`OnAnimatorIK`/`AvatarIKGoal`) this skill covers.
- Never assume authoring the underlying Sprite/mesh art is this skill's territory — route Sprite import/slicing to `unity-2d-sprite` and Sprite Shape splines to `unity-2d-spriteshape`; this skill only wires already-imported art into Animator playback.
- Never make a gameplay decision (whether an attack connects, a cooldown's expiry, a damage/health outcome) inside animation-layer code (`StateMachineBehaviour`, Animation Event handlers, `OnAnimatorMove`/`OnAnimatorIK`) — resolve the decision in Shared Core and let animation-layer code only carry out or signal whatever Core already decided, per `coding-principles.md`'s Shared Core integrity rule.
- `Animator.Culling Mode` left at `Always Animate` is a common, easy-to-miss performance cost for any character that can go offscreen — verify it's set to `Cull Update Transforms` or `Cull Completely` per [performance-and-faq.md](references/performance-and-faq.md) rather than assuming the default is fine.
- Animator parameter access by raw string in a hot path (`Update()`, `FixedUpdate()`, per-tick AI) is a direct violation of `coding-principles.md`'s hot-path hygiene — always cache `Animator.StringToHash` results and use the `int` overloads.
- A `PlayableGraph` is **not garbage-collected** — an un-destroyed graph is a guaranteed leak; always pair `PlayableGraph.Create()` with an explicit `Destroy()` in teardown (`OnDisable()` or equivalent).
- Don't reach for the Playables API when an Animator Controller state machine and Blend Tree already express the requirement — see YAGNI in `coding-principles.md`; the Playables API is a deliberate escape hatch for procedural/runtime-composed graphs, not a routine default.
- Retargeting requires **both** models to be Humanoid with a properly configured, T-pose-verified Avatar — a `"Character not in T-Pose"` warning is a pose problem, not necessarily a bone-mapping problem; don't waste time re-mapping bones for a pose issue.
- Author transition Exit Time in normalized time (not `Fixed Duration` seconds) whenever a controller will be reused via `AnimatorOverrideController` with clips of varying length — a shorter override clip can silently skip a seconds-based transition.
- Any claimed animation performance improvement (a Culling Mode change, a bone-count reduction, an optimization from [performance-and-faq.md](references/performance-and-faq.md)) must be backed by an actual Profiler measurement before being reported as done, per `performance-and-algorithms.md`'s Verification section — not asserted from the optimization guide alone.
- The Playables API's `AnimationLayerMixerPlayable` and the Manual's implicit "`AnimationScriptPlayable`" naming (documented via the generic `ScriptPlayable<T>`/`PlayableBehaviour` pattern rather than a dedicated class) were not exposed as separate dedicated Manual sub-pages at authoring time — verify current exact member signatures against the live Script Reference before implementing a custom `PlayableBehaviour` or layer-mixer graph.

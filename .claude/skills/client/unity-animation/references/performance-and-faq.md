# Mecanim Performance, Optimization & FAQ

Sources: `https://docs.unity3d.com/Manual/MecanimPeformanceandOptimization.html`, `https://docs.unity3d.com/Manual/MecanimFAQ.html`, and sub-pages (see [root-links.md](root-links.md)).

## Animation-system-level optimization

| Technique | Detail |
|---|---|
| Controller presence | "The Animator doesn't spend time processing when a Controller is not set to it" — an `Animator` with no `RuntimeAnimatorController` assigned costs effectively nothing per frame. |
| Simple single-clip playback | Counterintuitively, playing one `AnimationClip` with **no blending** can be *slower* under Mecanim than under the legacy animation system, because Mecanim's pipeline uses temporary blending buffers and extra copying of sampled curve data even when only one clip is active — the legacy system samples the curve and writes directly to the transform. This tradeoff only matters for genuinely trivial single-clip cases; Mecanim's layout is optimized for the common case of blending/complex setups. |
| Scale curves | Animating scale curves is more expensive than animating translation/rotation curves — avoid scale-curve animation where avoidable. **Exception**: constant curves (same value for the whole clip) are already optimized and cheaper than normal curves; a constant curve matching the default scene value doesn't write to the scene at all every frame. |
| Layers | Layer/state-machine evaluation overhead is kept minimal by Unity internally. The cost of an added layer (synced or not) scales with what animations/blend trees that layer actually plays. **A layer with weight `0` is skipped entirely** — Unity does not evaluate a zero-weight layer's update. |
| Humanoid: Avatar Masks | When importing Humanoid animation, use an `AvatarMask` to strip out IK goals or finger animation data you don't need — see [avatar-setup.md](avatar-setup.md). |
| Generic: root motion | For Generic rigs, using root motion is more expensive than not. If animations don't use root motion, make sure no root bone is specified on that Generic avatar — an unnecessary root bone assignment costs extra work even if the motion isn't used. |
| Parameter access by hash | Query/set Animator parameters by integer hash, not by string name, using `Animator.StringToHash`: `int runState = Animator.StringToHash("Base Layer.Run"); animator.SetBool(runState, false);` — avoids re-hashing the string on every call. See [animator-component.md](animator-component.md). |
| AI/state coupling | Implement a lightweight AI layer that drives the Animator via simple callbacks (`OnStateChange`, `OnTransitionBegin`, etc.) rather than polling/branching heavily inside the animation update itself; use **State Tags** to line up your AI's own state machine with the Animator's state machine. |
| Event simulation via curves | Use extra animation curves to simulate discrete events, and to mark up animations (e.g. in conjunction with Target Matching) instead of ad hoc per-frame checks. |
| Visibility culling | "Always optimize animations by setting the animator Culling Mode to Cull Completely, and disable the skinned mesh renderer's Update When Offscreen property" — this is the single most emphasized runtime optimization on the page. |

### `Animator.Culling Mode` (component property)

| Mode | Behavior / cost |
|---|---|
| `AnimatorCullingMode.AlwaysAnimate` | "Always animate, don't do culling even when offscreen." Highest cost — full animation evaluation regardless of visibility. |
| `AnimatorCullingMode.CullUpdateTransforms` | "Retarget, IK and write of Transforms are disabled when renderers are not visible." Moderate cost — skips retargeting/IK/transform writes while offscreen but keeps some processing active. |
| `AnimatorCullingMode.CullCompletely` | "Animation is completely disabled when renderers are not visible." Lowest cost — the recommended default per the optimization page above. |

### `Animator.updateMode` (Update Mode)

| Mode | Behavior |
|---|---|
| `AnimatorUpdateMode.Normal` | Updates in sync with `Update()`; speed follows the current timescale. |
| `AnimatorUpdateMode.AnimatePhysics` | Updates in sync with `FixedUpdate()` — use when animating objects that interact with physics (e.g. a character pushing rigidbodies around). |
| `AnimatorUpdateMode.UnscaledTime` | Updates in sync with `Update()` but ignores timescale, always animating at 100% speed — useful for UI animation that must keep moving while gameplay is paused (`Time.timeScale == 0`). |

## Modeling / rig-complexity guidance

- Fewer polygons = faster app, balanced against visual/platform requirements; Unity's actual vertex count can exceed what a DCC tool reports because vertices split for extra normals/UVs/vertex colors.
- Minimize material count; only use multiple materials where genuinely different shaders are needed (e.g. character eyes).
- **Use exactly one `SkinnedMeshRenderer` per character.** Unity's visibility-culling and bounding-volume-update optimizations only apply cleanly with a single Animation component + single `SkinnedMeshRenderer`; a second skinned mesh on the same character can "roughly double the rendering time for a model."
- Minimize bone count: 15 extra bones on a 30-bone rig means "50% more operations to solve in Generic mode" — bone count cost is non-trivial and roughly linear.
- Use linear blend skinning with a maximum of 4 influences per vertex.
- Unity bakes IK nodes into FK at import time, making imported IK nodes redundant afterward — strip IK nodes in the DCC tool or in Unity to avoid paying for calculations that are already baked out.

## Humanoid vs. Generic retargeting cost

- **Humanoid**: requires a valid `Avatar` mapping (minimum 15 bones, T-pose-based configuration — see [avatar-setup.md](avatar-setup.md)), but in exchange supports **retargeting** — the same animation clip can drive any other Humanoid rig sharing a compatible Avatar, and one Avatar can be reused/copied ("Copy From Other Avatar") across files sharing the same bone structure. Retargeting is the mechanism that makes Humanoid rigs interchangeable but is inherent extra runtime work the Generic path doesn't do.
- **Generic**: no retargeting support — animations are tied to that specific rig's bone structure; only a single Root node needs to be designated (defines the model's center of mass for non-in-place blending). Cheaper per the bone-count scaling note above when root motion is unused and no root bone is specified.
- Import-time avatar/transform masking (available to both types) discards unused animation data before build compilation, reducing both file size/memory and runtime blending cost.

## Mecanim FAQ (full content)

The Manual FAQ page has five sections; reproduced here as reference (condensed where noted).

### General
- **Animation window vs. Animator window**: the **Animation Window** creates/edits `AnimationClip` data (can animate almost any inspector-exposed property: transform, material color, light intensity, audio volume, arbitrary script fields). The **Animator Window** organizes existing clip assets into a state-machine flowchart. Both belong to Mecanim, not the Legacy Animation system. See [mecanim-overview.md](mecanim-overview.md).
- **Should we migrate from Legacy to Mecanim for character animation?** "Generally, yes you should since most character animations are more complex" than Legacy handles well.

### Import
- **Why does an imported mesh get an Animator component automatically?** Unity adds an animation component whenever it detects animation data in the imported file. Disable by setting **Animation Type → `None`** under the **Rig** tab of the import settings — can be applied to multiple files at once.

### Layers
- **Does layer order matter?** Yes — layers evaluate top to bottom; an override layer always overrides everything above it (respecting its `AvatarMask` if one is set).
- **Base layer weight — 1 or 0?** The base layer's weight is always `1`; layers above it in override mode fully replace the base layer's result (where masked).
- **Getting a parameter value without using a string?** Use `Animator.StringToHash` to get an integer id for a state/parameter name, then use the `int`-overload Animator methods — e.g. `runState = Animator.StringToHash("Base Layer.Run"); animator.SetBool(runState, false);`.
- **Mismatched state length on a Sync layer vs. the base layer?** They become **unsynchronized**. Enable the layer's **Timing** option to force the current layer's state timing to follow the source (base) layer's timing.

### Avatar Masks
- **Can you create `AvatarIKGoal`s beyond LeftFoot/RightFoot/LeftHand/RightHand?** Yes — knee and elbow IK are supported.
- **Can you define exactly which transforms belong to an Avatar Mask?** For **Generic** clips, you can choose which transforms have their animation imported. For **Humanoid** clips, all human transforms are always imported, but extra (non-human) transforms can additionally be defined.

### Animation curves
- **How do curve-bearing animations blend with animations that lack that curve?** Unity blends against the parameter's **default value** — set a default per parameter in the Animator window (outside LiveLink) so blending between a state with a curve-driven parameter and one without produces a sensible intermediate rather than an undefined jump.

## Practical guidance

- Set `Animator.cullingMode = AnimatorCullingMode.CullCompletely` as the default for characters that can go offscreen, and disable `SkinnedMeshRenderer.updateWhenOffscreen` alongside it — this is the doc's single strongest, most explicit recommendation and directly reinforces this project's "no wasted per-frame work" performance floor.
- Never query/set Animator parameters by raw string in a hot path (`Update()`, `FixedUpdate()`, per-tick AI logic) — cache the hash once via `Animator.StringToHash` (a `static readonly int` field is the natural place) and use the `int` overloads, mirroring the `performance-and-algorithms.md` rule to cache Animator parameter hashes and avoid re-hashing every call.
- Avoid animating scale curves where translation/rotation would do; if a curve is genuinely constant, let it stay constant (matching default scene values) rather than authoring near-constant noise, since Unity specifically optimizes true constant curves.
- Keep to one `SkinnedMeshRenderer` per character — a second one is a straightforward way to silently double rendering cost, and is exactly the kind of Big-O-looks-fine-but-hardware-cost-is-real case `performance-and-algorithms.md` asks to validate before shipping.
- Treat bone count as a real, roughly-linear performance lever for Generic rigs (the doc's own "15 extra bones → 50% more solve operations" example) — don't add bones speculatively; this is a direct instance of the project's "don't over-engineer for N that doesn't need it" guidance applied to rig complexity instead of code structure.
- For Generic rigs that don't use root motion, explicitly confirm no root bone is assigned — an unused root bone still costs extra processing.
- A zero-weight Animator layer is already skipped by Unity, so it's safe to leave inactive layers permanently present in a controller (e.g. for designer-toggleable layers) rather than dynamically adding/removing layers at runtime — dynamic layer add/remove would be the more expensive and more error-prone path.
- When retargeting isn't needed (a rig used by exactly one character/clip set with no shared-Avatar reuse), Generic can be the leaner choice; reach for Humanoid specifically when clip-sharing/retargeting across multiple rigs is an actual requirement — don't default to Humanoid "just in case," per YAGNI.
- Any claimed animation performance improvement in a handoff note must be backed by an actual Profiler measurement, not asserted from this guide alone — per `performance-and-algorithms.md`'s Verification section.

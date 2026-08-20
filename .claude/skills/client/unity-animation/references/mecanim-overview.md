# Animation Fundamentals — Mecanim Overview, Animation Clips, Animation Events

Sources: `https://docs.unity3d.com/Manual/animation-mecanim.html`, `https://docs.unity3d.com/Manual/AnimationOverview.html`, `https://docs.unity3d.com/Manual/animation-clips-landing.html`, and their sub-pages (see [root-links.md](root-links.md)).

## Mecanim orientation (short — Animator/Avatar/Animator Controller detail lives in separate reference files)

Mecanim is Unity's primary animation framework. It is built around three interconnected pieces:

- **Animation Clips** — individual motion recordings (`Idle`, `Walk`, `Run`). An animation clip contains keyframed data describing how a GameObject's position, rotation, scale, or component properties (material color, light intensity, audio volume, custom script fields) change over time.
- **Animator Controller** — a state-machine asset (flowchart of states/transitions/blend trees/parameters) that organizes clips and drives which one plays. Multiple models can share one controller. See [animator-controller.md](animator-controller.md).
- **Avatar** — maps a Humanoid character's skeleton to Unity's common humanoid format, enabling retargeting (playing the same clip on differently-proportioned rigs) and muscle-definition adjustments. See [avatar-setup.md](avatar-setup.md).

All three connect through the **Animator component** on a GameObject, which references an Animator Controller (and, for Humanoid rigs, an Avatar) — see [animator-component.md](animator-component.md). This file focuses on Animation Clips themselves and the Animation window / Animation Events workflow.

## What an Animation Clip is

An `AnimationClip` is the atomic unit of animation data in Unity: a sequence of keyframed curves that can drive:
- GameObject position, rotation, and scale.
- Component properties (material color, light intensity, audio volume).
- Custom script properties (`float`, `int`, `enum`, `Vector`, `bool` fields).
- Function calls at specific times (Animation Events).

Clips come from two sources:
1. **Imported** from an external DCC tool (FBX, Maya `.mb`/`.ma`, 3ds Max `.max`, Blender `.blend`) — imported the same way as any other 3D asset.
2. **Created natively** inside Unity's Animation window, authored directly against a GameObject in the Scene.

## Animation Type: Humanoid vs Generic vs Legacy

Set on the **Rig** tab of the Model/FBX Importer Inspector (`FBXImporter-Rig.html`), via the **Animation Type** dropdown. Unity auto-detects a type on first import; new files default to `None`.

| Animation Type | Description | Retargeting | Root/Avatar requirement |
|---|---|---|---|
| `None` | No animation present (default for never-imported files). | N/A | N/A |
| `Humanoid` | For bipedal characters ("two legs, two arms and a head"). Uses an Avatar to map the actual skeleton onto Unity's standardized humanoid bone structure. | Yes — the same clip can drive any Humanoid-rigged model. | Requires an Avatar (`Create From This Model` or `Copy From Other Avatar`). |
| `Generic` | For any non-humanoid skeleton — quadrupeds, creatures, mechanical rigs, or a simple 2D sprite-swap "animation" (no skeleton at all). | No | Requires a designated **Root** bone (defines the model's center of mass); does not use the Configure Avatar window. Generic avatars hold only the Root node mapping. |
| `Legacy` | The pre-Mecanim animation system, kept for backward compatibility with Unity 3.x-era content. | No | Used with the legacy `Animation` component, not `Animator`. |

`Avatar Definition` options (Humanoid and Generic both offer these): `Create From This Model` (generates a new Avatar from this mesh) or `Copy From Other Avatar` (reuses an existing Avatar asset).

`Optimize Game Object` — available only when Avatar Definition is `Create From This Model`; removes/stores the GameObject transform hierarchy inside the Avatar/Animator component instead of keeping individual bone GameObjects, for a performance win. (Deeper coverage of Avatar configuration is in [avatar-setup.md](avatar-setup.md).)

## Importing animation clips from external tools

Imported the same way as any other model asset (`AnimationsImport.html`). Key facts:
- A single FBX can contain multiple animations exported as "takes," or a plugin can export multiple takes into one file.
- Unity provides clip-splitting tools to carve one continuous timeline into multiple named clips (see below).
- Imported animation data is **read-only** in the Animation window — to modify it, copy keyframes into a new, separately-created clip. Copying keyframes across GameObjects requires matching hierarchy and property names.
- Alternative multi-file import convention: name files `modelName@animationName.fbx` (e.g. `goober@idle.fbx`, `goober@walk.fbx`, `goober@jump.fbx`). Unity imports all such files and collects the animations onto the base model (the file without the `@` suffix) automatically.

### Splitting/extracting clips from a single take

In the model's Inspector **Animation** tab (`Splittinganimations.html`):
1. Click `+` to add a new clip entry to the Clips list.
2. Set `Start` / `End` (frame or second range) to select the sub-range of the take.
3. Name the clip (e.g. `walk`, `idle`, `jump`).

### Euler curve resampling

Unity resamples imported Euler-angle rotation keyframes into Quaternion keyframes on every frame by default, to minimize playback discrepancy from the source. Disable **Resample Curves** (Animation import tab) only if the default Quaternion interpolation produces visibly bad results — original Euler curves cost less memory (unbaked rotation curves are smaller than fully-baked Quaternion ones), but Unity still converts to Quaternion at runtime before applying to the GameObject. Unity's default Euler rotation order is Z, X, Y; a source file using a different order triggers Inspector warnings about potential interpolation mismatches.

## Animation Clip Inspector reference (Animation tab of the Model Importer)

| Field | Description |
|---|---|
| `Import Constraints` | Imports constraint settings that limit Joint component movement/rotation. |
| `Import Animation` | Master toggle — enables animation import; disabling hides all other animation options. |
| `Bake Animations` | Converts IK/simulation-based animation to forward-kinematic keyframes (Maya, 3ds Max, Cinema 4D sources only). |
| `Resample Curves` | Resamples curves as Quaternion values with a keyframe every frame; disable to preserve original authored curves (see above). |
| `Anim. Compression` | `Off`, `Keyframe Reduction`, `Keyframe Reduction and Compression`, or `Optimal`. |
| `Rotation Error` | Angle tolerance (degrees) for removable rotation keyframes under compression. |
| `Position Error` | Percentage tolerance for removable position keyframes under compression. |
| `Scale Error` | Percentage tolerance for removable scale keyframes under compression. |
| `Animated Custom Properties` | Imports designated FBX custom user properties via the asset postprocessor. |
| `Source Take Name` | The original take name from the source DCC file. |
| `Start` / `End` | First/last frame of this clip's range within the source take. |
| `Loop Time` | Restarts the clip when it reaches the end. |
| `Loop Pose` | Blends start/end poses for a seamless loop across the cycle boundary. |
| `Cycle Offset` | Offsets the starting point of a looping clip. |
| `Bake Into Pose` (Rotation) | Bakes root rotation into the bones themselves; disabled = preserved as root motion data. |
| `Based Upon` (Rotation) | `Original`, `Root Node Rotation` (Generic), or `Body Orientation` (Humanoid). |
| `Offset` (Rotation) | Rotational offset in degrees applied to the root. |
| `Bake Into Pose` (Position Y) | Bakes vertical root motion into the bones; disabled = preserved as root motion. |
| `Based Upon` (Position Y, "at Start") | `Original`, `Root Node Position` (Generic), `Center of Mass` (Humanoid), or `Feet` (Humanoid). |
| `Offset` (Position Y) | Vertical offset applied to root position. |
| `Bake Into Pose` (Position XZ) | Bakes horizontal root motion into the bones; disabled = preserved as root motion. |
| `Based Upon` (Position XZ) | `Original`, `Root Node Position` (Generic), or `Center of Mass` (Humanoid). |
| `Offset` (Position XZ) | Horizontal offset applied to root position. |
| `Mirror` | Mirrors left/right symmetry (Humanoid Animation Type only). |
| `Additive Reference Pose` | Sets a reference frame for additive animation layering. |
| `Pose Frame` | Frame number used as the additive reference pose. |
| `Curves` | Expandable section — custom curves attached to this clip (see below). |
| `Events` | Expandable section — Animation Events on this clip (see below). |
| `Mask` | Expandable section — Avatar Mask settings for this clip (see [avatar-setup.md](avatar-setup.md)). |
| `Motion` | Root motion node source: `None`, `Root Transform`, or a specific mesh/child transform. |
| `Import Messages` | Import diagnostics, including optional Retargeting Quality Reports. |

### Loop settings in depth

For a clip to loop cleanly, start and end poses must match:
- **Root Transform Rotation** and **Root Transform Position Y** (vertical) *should* match between first/last frame.
- **Root Transform Position XZ** (horizontal) should generally *not* match — matching it would prevent the character from actually translating across the ground while looping (e.g. a walk cycle needs to keep moving forward each loop).
- The Inspector's loop-optimization graph (click-and-hold the timeline indicators) highlights problem regions in red/yellow; drag clip endpoints until the relevant property line reads green.

## Curves on imported clips

Custom curves attached to a clip (`Curves` section, Animation tab) drive arbitrary time-based data alongside the animation — e.g. a curve controlling particle-system emission rate for breath condensation during a cold-weather idle. Important interop rule: **if a curve's name matches an Animator Controller parameter name, that parameter takes its value from the curve at each point in the timeline** instead of being set externally.

- Add a curve via the `+` icon in the Curves section; each clip in a multi-clip import can have its own curves.
- Double-click a curve to open Unity's standard curve editor: add keys, step between keyframes with Previous/Next Key Frame buttons, and edit values via numeric fields.
- The curve's X-axis is always normalized time (`0.0` = clip start, `1.0` = clip end) regardless of the clip's actual duration in seconds.

## The Animation window vs. the Animator window — do not confuse these

| | Animation window | Animator window |
|---|---|---|
| Purpose | Preview, create, and directly keyframe-edit `AnimationClip` assets on a specific GameObject. | Edit an `AnimatorController` state machine — states, transitions, blend trees, parameters. |
| Open via | `Window > Animation > Animation` | `Window > Animation > Animator` |
| Operates on | A single clip's curves/keyframes/events, timeline-based. | The flow *between* multiple clips/states, graph-based. |
| Typical use | Authoring a new clip from scratch, tweaking curves, adding Animation Events. | Wiring up how/when clips play and blend based on parameters. |

The Animation window supports:
- **Keyframing** — automatic or manual key insertion while scrubbing the timeline.
- **Curve editing** — a dedicated Curve Editor with key add/select/move, Euler or Quaternion rotation interpolation options.
- **Dopesheet mode** — box-select multiple keys, then move/scale/ripple-edit them as a group.
- **Animation Events** — add function-call triggers at specific times (see below).
- **Blend Shapes** — import and animate blend shapes.

### Creating a new clip natively

1. Select the target GameObject in the Scene.
2. `Window > Animation > Animation` to open the Animation window.
3. Click **Create** (shown when no clip is assigned yet) and save the new empty `AnimationClip` into the Assets folder.
4. Unity auto-generates the supporting infrastructure: an `AnimatorController` asset (with the new clip as its default state), an `Animator` component added to the GameObject, and the controller wired into that component.

For a GameObject that already has a clip, the **Create** button is replaced by the clip-selector dropdown (top-left of the window) — choose **Create New Clip** to add additional clips to the same object.

### Previewing clips

Preview toolbar controls (left to right): Preview mode toggle, Record mode toggle (auto-enables Preview mode), jump-to-start, previous keyframe, Play, next keyframe, jump-to-end, and a playhead position field (frames or seconds).

Keyboard: `,` / `.` step one frame/second back/forward; `Alt`/`Option` + `,` / `.` step to the previous/next keyframe. `F` zooms to selected keyframes, `A` fits all keyframes in view. The **Lock** button pins the window to the current GameObject instead of following Scene selection.

## Animation Events

Animation Events attach extra data to a clip that fires a function call at a specific point in playback — e.g. triggering a footstep sound partway through a walk cycle.

### Adding events to an imported clip (Inspector workflow)

1. In the model's Inspector, open the **Animation** tab and expand **Events**.
2. Scrub the preview playhead to the desired time.
3. Click **Add Event** — a white marker appears on the timeline.
4. Set the `Function` field to the name of the method to invoke.

### Adding events in the Animation window (native clip workflow)

- Click the **Event** button to add an event at the current playhead, or right-click the Event line and choose **Add Animation Event** for a specific position.
- Drag markers on the Event Line to reposition; hover a marker for a tooltip showing function name and parameter value.
- Select multiple markers with Shift+click or a drag-box; delete via `Delete` key or right-click → **Delete Event**.

### Firing requirements and the `AnimationEvent` class

- **Any GameObject that plays this animation via its Animator must have a script attached with a method whose name matches the event's `Function` field** — if no matching method exists, Unity will not silently ignore it (a mismatched/missing handler is a common source of runtime errors, verify the receiving component before shipping).
- The target function must accept **exactly one parameter**, of one of these types: `float`, `int`, `string`, an `Object` reference, or an `AnimationEvent` object.
- Use the `AnimationEvent` object parameter when more than one value needs to reach the handler in a single call — it exposes `floatParameter`, `intParameter`, `stringParameter`, and `objectReferenceParameter` fields simultaneously, plus metadata about the firing event itself.
- Typical uses: a `float` for a sound's volume/pitch, an `Object` reference to a VFX prefab to instantiate at that moment.

## Legacy Animation system (deprecated relative to Animator)

The **Legacy Animation system** predates Mecanim. Unity's own guidance: *"This component is retained in Unity for backwards compatibility. For new projects, use the Animator component."* It is kept because it's simpler and can be cheaper for very simple animation needs, but it lacks Mecanim's state-machine/blend-tree/retargeting feature set.

To use it: set **Animation Type** to `Legacy` on the Rig tab, then enable **Import Animation** on the Animation tab. This drives the legacy `UnityEngine.Animation` component rather than `Animator`.

### `Animation` component (legacy) — Inspector reference

| Field | Description |
|---|---|
| `Animation` | The default clip played when `Play Automatically` is enabled. |
| `Animations` | List of clips accessible from scripts. |
| `Play Automatically` | Auto-plays the default animation on start. |
| `Animate Physics` | Lets the animation interact with Physics. |
| `Culling Type` | `Always Animate` or `Based on Renderers` — controls when playback is skipped for off-screen objects. |

### Scripting API surface (legacy)

Referenced by the docs though not detailed in prose: `Animation.Play()`, `Animation.CrossFade()`, `PlayMode.StopAll`. Treat the legacy `Animation`/`AnimationState` scripting API as maintenance-only — new gameplay code should drive playback through `Animator` (parameters, triggers, state machine) instead of `Animation.Play`/`CrossFade`.

## Practical guidance

- **Humanoid vs Generic vs Legacy** — default to `Humanoid` for any bipedal character you want to retarget clips across (shared idle/walk/run libraries across multiple character models). Use `Generic` for non-humanoid rigs (creatures, vehicles, props) or simple sprite-swap animation — you lose retargeting but gain full rig flexibility; a `Root` bone is mandatory for skeletal Generic rigs. Only use `Legacy` for old/imported content that already depends on `Animation.Play`/`CrossFade` — don't author new gameplay animation against it.
- **Animation window vs Animator window** — if the task is "make/edit the motion data in a clip" (keyframes, curves, events), that's the Animation window. If the task is "decide which clip plays when, and how they blend," that's the Animator window/Animator Controller. Confusing the two is a common source of wasted effort — the Animation window cannot express state transitions, and the Animator window cannot keyframe a curve.
- **Imported clip data is read-only** in the Animation window — if you need to hand-edit an imported animation's curves, split/copy it into a new native clip first rather than trying to edit it in place.
- **Loop Time vs Loop Pose** — `Loop Time` alone just replays the clip; `Loop Pose` additionally blends the start/end pose so a looping clip doesn't visibly pop at the seam. Check the loop-optimization graph (red/yellow vs green) before shipping a looping locomotion clip.
- **Root motion XZ** — leave `Bake Into Pose` off / `Based Upon` set appropriately for Position XZ when the character should actually translate through the world each loop (e.g. walk/run cycles); baking XZ into the pose makes the character animate in place with zero net movement, which silently breaks root-motion-driven movement.
- **Animation Events timing** — events fire during Animator/Animation evaluation, tied to the clip's own timeline, not to a fixed real-time cadence; a skipped/dropped frame (e.g. from a large time-scale jump or an interrupted transition) can skip an event's exact tick — don't rely on an event firing at exactly one specific `Update()` frame for gameplay-critical logic without a fallback.
- **Event handler contract** — an Animation Event's target function must accept exactly one parameter of an allowed type (`float`/`int`/`string`/`Object`/`AnimationEvent`); mismatched signature or a missing method on the playing GameObject's script is a common cause of a "silent" animation event that appears to do nothing.
- **Custom curves as parameter drivers** — naming a clip's custom curve identically to an Animator Controller parameter lets the *curve* drive that parameter's value each frame; this is a clean way to script per-clip-authored values (e.g. a footstep-weight parameter) without a MonoBehaviour polling the clip manually — but it also means an accidental name collision between a curve and a parameter will silently override runtime-set values while that clip plays.
- **Legacy component** — do not use `Animation`/legacy-style playback (`Animation.Play`, `CrossFade`) in new `Game.Client` code; per this project's coding principles, all new gameplay animation control should go through `Animator` (parameters/triggers), keeping any legacy component strictly to maintaining old imported content.
- **Animation Event handler placement** — the handler method an Animation Event calls (e.g. `PlayFootstepSound()`) is Unity-side reaction code and belongs in `Game.Client.*`; if the event should also affect a gameplay rule (e.g. an attack's hit window opening), the handler should signal into `Game.Core.*` rather than deciding the outcome itself, per `coding-principles.md`'s Shared Core integrity rule.

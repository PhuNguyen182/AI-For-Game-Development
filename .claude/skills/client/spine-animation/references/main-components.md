# Main Components — SkeletonRenderer, SkeletonAnimation, SkeletonGraphic, SkeletonMecanim, Skeleton/AnimationState API

Source: [spine-unity-main-components](https://esotericsoftware.com/spine-unity-main-components#Main-Components) (spine-unity v4.3+).

Since v4.3, animation is separated from rendering across two components instead of one inheritance chain, so they can be combined:

| Component | Purpose | Renderer? | Animation? |
|---|---|---|---|
| `SkeletonRenderer` | Draws skeleton via `MeshRenderer` | Yes | No |
| `SkeletonGraphic` | Renders skeleton in a UI `Canvas` | Yes | No |
| `SkeletonAnimation` | Spine's own animation system | No | Yes |
| `SkeletonMecanim` | Unity's Mecanim system | No | Yes |

`SkeletonAnimation` and `SkeletonMecanim` each require a renderer component alongside them (`SkeletonRenderer` for world-space, or they pair with `SkeletonGraphic` for UI).

## SkeletonRenderer

Draws and manages skeleton state via procedural mesh generation (`MeshRenderer`/`MeshFilter`), referencing the atlas texture asset(s) for attachments.

**Inspector properties**: `Skeleton Data Asset`, `Initial Skin`, `Initial Flip X`/`Initial Flip Y`, `Update When Invisible`, `Fix Draw Order` (prevents aggressive batching with 3+ submeshes), `Immutable Triangles` (optimization for static attachment visibility), `Clear State On Disable`, `Separator Slot Names`, `Use Clipping`, `Z Spacing`, `Use Single Submesh`, `Fix Prefab Override Mesh Filter`, `Use Threading` (parallel mesh generation), `PMA Vertex Colors`, `Tint Black`, `Add Normals`, `Solve Tangents`, and Physics Inheritance settings (`Position`/`Rotation` scale, `Movement Relative To`).

**Delegates**: `OnRebuild` (after skeleton init), `OnMeshAndMaterialsUpdated` (end of `LateUpdate()`), `UpdateLocal` (after animations applied to local values), `UpdateComplete` (after world transforms calculated), `UpdateWorld` (after world transforms; calling `skeleton.UpdateWorldTransform()` again here re-applies overrides).

**Methods**: `UpdateMesh()` — force-regenerate the mesh, ignoring `UpdateMode`.

**Setup**: create an empty GameObject → Add Component → `SkeletonRenderer` (auto-adds `MeshRenderer`/`MeshFilter`) → assign the `_SkeletonData` asset → add `SkeletonAnimation` or `SkeletonMecanim` for actual animation control.

**Caveats**: don't use `SkeletonRenderer` alone unless animation is applied fully manually without transitions (e.g. a UI gauge — see `Spine Examples/Other Examples/SpineGauge`); if only bones are visible with no images, the `Initial Skin` is probably still `default` and needs changing.

## The Skeleton object

Reached via `SkeletonRenderer.Skeleton` (or `SkeletonGraphic.Skeleton`). Manipulates bones, slots, skins, and attachments directly.

```csharp
bool success = skeleton.SetAttachment("slotName", "attachmentName");
bool success = skeleton.SetSkin("skinName");
skeleton.SetupPose();
skeleton.SetupPoseBones();
skeleton.SetupPoseSlots();
skeleton.ScaleX = -1f;  // flip horizontally
skeleton.ScaleY = -1f;  // flip vertically
Bone bone = skeleton.FindBone("boneName");
Vector3 worldPos = bone.GetWorldPosition(skeletonRenderer.transform);
bone.SetPositionSkeletonSpace(position);
Quaternion rot = bone.GetQuaternion();
```

**Setting attachments/skins** — prefer the `[SpineSlot]`/`[SpineAttachment]`/`[SpineSkin]` attributes on public string fields over bare strings, for an Inspector dropdown instead of a typo-prone free-text field:

```csharp
[SpineSlot] public string slotProperty = "slotName";
[SpineAttachment] public string attachmentProperty = "attachmentName";
bool success = skeletonRenderer.Skeleton.SetAttachment(slotProperty, attachmentProperty);
```

**Critical caveat**: always call `skeleton.SetupPoseSlots()` right after `SetSkin(...)` — otherwise attachments set under the previous skin can keep affecting visibility.

### Mix-and-match skin composition

```csharp
var skeleton = skeletonRenderer.Skeleton;
var skeletonData = skeleton.Data;
var mixAndMatchSkin = new Skin("custom-girl");
mixAndMatchSkin.AddSkin(skeletonData.FindSkin("skin-base"));
mixAndMatchSkin.AddSkin(skeletonData.FindSkin("nose/short"));
mixAndMatchSkin.AddSkin(skeletonData.FindSkin("eyelids/girly"));
skeleton.SetSkin(mixAndMatchSkin);
skeleton.SetupPoseSlots();
skeletonAnimation.AnimationState.Apply(skeletonRenderer.Skeleton);
// SkeletonMecanim: skeletonMecanim.Update(); instead of AnimationState.Apply(...)
```

Example scenes: `Spine Examples/Other Examples/Mix and Match`, `Mix and Match Equip`.

### Runtime repacking (combining textures via `Spine.Unity.AttachmentTools.AtlasUtilities`)

```csharp
using Spine.Unity.AttachmentTools;

AtlasUtilities.RepackAttachmentsOutput repackingOutput;
repackingOutput.DestroyGeneratedAssets();  // clean up a previous repack first

AtlasUtilities.RepackAttachmentsSettings settings = AtlasUtilities.RepackAttachmentsSettings.Default;
settings.UseSourceMaterialsFrom(skeletonAnimation.SkeletonDataAsset);
settings.maxAtlasSize = 1024;

Skin repackedSkin = collectedSkin.GetRepackedSkin("Repacked skin", settings, ref repackingOutput);
collectedSkin.Clear();

skeleton.Skin = repackedSkin;
skeleton.SetupPoseSlots();
skeletonAnimation.AnimationState.Apply(skeletonRenderer.Skeleton);

AtlasUtilities.ClearCache();  // optional, after several repack operations
```

With normal maps, add `settings.additionalTexturePropertyIDsToCopy = new int[] { Shader.PropertyToID("_BumpMap") };` and a matching `repackingOutput.additionalOutputTextures` array.

**Repacking failure checklist**: source textures need `Read/Write` enabled; texture Compression must be `None` (not `Normal Quality`); Quality tiers must use full-resolution textures (half/quarter resolution hits a Unity bug); the source texture must be power-of-two, or the Spine export needs `Power of two` enabled.

Example scenes: `Spine Examples/Other Examples/Mix and Match`, `Mix and Match Equip`.

### Scaling / flipping

```csharp
bool isFlippedX = skeleton.ScaleX < 0;
skeleton.ScaleX = -skeleton.ScaleX;  // toggle flip X
```

### Manually reading/writing bone transforms

```csharp
Bone bone = skeletonRenderer.Skeleton.FindBone("boneName");
Vector3 worldPosition = bone.GetWorldPosition(skeletonRenderer.transform);
// SkeletonGraphic: also scale by the parent Canvas's referencePixelsPerUnit
bone.SetPositionSkeletonSpace(position);
Quaternion worldRotationQuaternion = bone.GetQuaternion();
```

**Critical caveat**: get/set bone positions inside the `UpdateWorld` life-cycle step (subscribe to `SkeletonRenderer.UpdateWorld`) — doing it elsewhere risks a one-frame-late read or a silently-overwritten write.

## SkeletonAnimation

Manages Spine's own animation/event system; requires a renderer component (typically `SkeletonRenderer`). The most customizable animation option.

**Inspector properties**: `Animation Name`, `Loop`, `Time Scale`, `Unscaled Time` (uses `Time.unscaledDeltaTime`), `Animation Update` (`Update`/`FixedUpdate`/`Manual`), `Use Threading`.

**Core properties**: `AnimationState` (the `Spine.AnimationState`), `Skeleton`.

**Delegates**: `BeforeApply`, `UpdateLocal`, `UpdateComplete`, `UpdateWorld`.

**Methods**: `Update(float deltaTime)` (full update), `ApplyAnimation()` (re-apply without advancing time), `UpdateMesh()` (regenerate mesh from current skeleton state).

**Setup (drag-and-drop)**: drag the `_SkeletonData` asset into the Scene view → choose `SkeletonAnimation` from the menu (creates a GameObject with `SkeletonRenderer` + `SkeletonAnimation` pre-wired).

**Setup (manual)**: empty GameObject → `SkeletonRenderer` → assign `_SkeletonData` → add `SkeletonAnimation`.

**Root motion**: Inspector "Root Motion – Add Component" button auto-adds `SkeletonRootMotion`. With a `Rigidbody`/`Rigidbody2D`, set `Animation Update` to `In FixedUpdate`.

### Update order

`SkeletonAnimation.Update()` (advances `AnimationState`, applies to skeleton) runs before `SkeletonRenderer.LateUpdate()` (rebuilds the mesh). To run before animations apply, use script execution order earlier than `SkeletonAnimation` (e.g. `[DefaultExecutionOrder(-1)]`); to run after, execution order after `SkeletonAnimation` in `Update()`, or before `SkeletonRenderer` in `LateUpdate()`.

```csharp
[DefaultExecutionOrder(-1)]
public class SetupPoseComponent : MonoBehaviour {
    void Update() {
        skeleton.SetupPose();  // runs before animations are applied this frame
    }
}
```

### Manual updates (when execution order can't be used)

```csharp
// Full skeleton update
skeleton.SetupPose();
skeletonAnimation.Update(0);

// Slot-only change (no bone world-transform update needed)
skeleton.SetupPoseSlots();
skeletonAnimation.AnimationState.Apply(skeleton);

// Custom delta time
skeletonAnimation.timeScale = 0f;
skeletonAnimation.Update(customDeltaTime);

// Regenerate mesh after a late modification
void LateUpdate() {
    skeleton.SetupPose();
    skeletonAnimation.Update(0);
    skeletonAnimation.UpdateMesh();  // needed if this script runs after SkeletonAnimation's own LateUpdate
}
```

### Initialization pattern

```csharp
using Spine.Unity;

public class YourComponent : MonoBehaviour {
    SkeletonAnimation skeletonAnimation;
    Spine.AnimationState animationState;
    Spine.Skeleton skeleton;

    void Awake() {
        skeletonAnimation = GetComponent<SkeletonAnimation>();
        skeleton = skeletonAnimation.Skeleton;
        // skeletonAnimation.Initialize(false); // if .Skeleton isn't accessed here
        animationState = skeletonAnimation.AnimationState;
    }
}
```

## AnimationState API

Tracks playing/queued animations; every update it advances and applies them to the skeleton.

```csharp
skeletonAnimation.timeScale = 0.5f;  // half speed
skeletonAnimation.timeScale = 2f;    // double speed
```

### Setting animations

```csharp
TrackEntry entry = skeletonAnimation.AnimationState.SetAnimation(trackIndex, "walk", true);

// [SpineAnimation]-attributed field, or an AnimationReferenceAsset field, both work the same way:
[SpineAnimation] public string animationProperty = "walk";
TrackEntry entry = skeletonAnimation.AnimationState.SetAnimation(trackIndex, animationProperty, true);
```

**Critical caveat**: never call `SetAnimation` every frame — it restarts the animation from frame 1 each time, freezing the visible pose. Track state and call it only on an actual change; use `TrackEntry.trackTime` to hold on a specific frame instead.

### Queueing

```csharp
TrackEntry entry = skeletonAnimation.AnimationState.AddAnimation(trackIndex, "run", true, 2f);  // 2s delay
```

### Empty animations and clearing

```csharp
TrackEntry entry = skeletonAnimation.AnimationState.SetEmptyAnimation(trackIndex, mixDuration);
entry = skeletonAnimation.AnimationState.AddEmptyAnimation(trackIndex, mixDuration, delay);
skeletonAnimation.AnimationState.ClearTrack(trackIndex);
skeletonAnimation.AnimationState.ClearTracks();
```

Empty animations mix a single animation in/out — the standard way to transition cleanly.

### TrackEntry

Returned by `SetAnimation`/`AddAnimation`; customizes one playback instance (`EventThreshold`, `TrackEnd`, etc.). **Valid only until the animation is removed** — don't retain a reference past its `Dispose` event.

### AnimationState events

Six kinds: `Start`, `Interrupt` (a new animation superseded this one / track cleared), `End` (finished without interruption; can repeat if looped), `Complete` (finished a full cycle; can fire repeatedly if looped), `Dispose` (entry disposed — don't keep a reference after this), `Event` (a user-defined Spine event fired).

**Caveat**: interrupting a previous animation raises `Interrupt`+`End`, never `Complete`.

```csharp
void Awake() {
    skeletonAnimation = GetComponent<SkeletonAnimation>();
    animationState = skeletonAnimation.AnimationState;

    animationState.Start += OnSpineAnimationStart;
    animationState.Interrupt += OnSpineAnimationInterrupt;
    animationState.End += OnSpineAnimationEnd;
    animationState.Dispose += OnSpineAnimationDispose;
    animationState.Complete += OnSpineAnimationComplete;
    animationState.Event += OnUserDefinedEvent;
}

public void OnUserDefinedEvent(Spine.TrackEntry trackEntry, Spine.Event e) {
    if (e.Data.Name == "targetEvent") { /* handle */ }
}
```

The same six delegates exist per-`TrackEntry` for a single playback instance's events instead of every animation's.

**Faster event comparison** — cache the `EventData` once and compare by reference instead of by string each time:

```csharp
Spine.EventData targetEventData;
void Start() { targetEventData = skeletonAnimation.Skeleton.Data.FindEvent("targetEvent"); }
public void OnUserDefinedEvent(Spine.TrackEntry trackEntry, Spine.Event e) {
    if (e.Data == targetEventData) { /* handle */ }
}
```

### Changing animation state from inside an event callback

Event callbacks fire during `SkeletonAnimation.Update()`, before `LateUpdate()`'s mesh rebuild. Calling `SetAnimation()` from an `End` callback fires `Start` the same frame; because of mix transitions, the next animation's `Start` can fire before the previous one's `End`. Defer with a coroutine when strict ordering matters:

```csharp
trackEntry.End += e => {
    StartCoroutine(NextFrame(() => { YourCode(); }));
};
IEnumerator NextFrame(System.Action call) {
    yield return 0;
    call?.Invoke();
}
```

### Coroutine yield instructions

```csharp
var track = skeletonAnimation.state.SetAnimation(0, "interruptible", false);
var completeOrEnd = WaitForSpineAnimation.AnimationEventTypes.Complete | WaitForSpineAnimation.AnimationEventTypes.End;
yield return new WaitForSpineAnimation(track, completeOrEnd);

yield return new WaitForSpineAnimationComplete(track);
yield return new WaitForSpineAnimationEnd(track);
yield return new WaitForSpineEvent(skeletonAnimation.state, "spawn bullet");
// or with a cached EventData:
yield return new WaitForSpineEvent(skeletonAnimation.state, spawnBulletEvent);
```

## String-property attributes (Inspector dropdowns)

`[SpineBone]`, `[SpineSlot]`, `[SpineAttachment]`, `[SpineSkin]`, `[SpineAnimation]`, `[SpineEvent]`, `[SpineIkConstraint]`, `[SpineTransformConstraint]`, `[SpinePathConstraint]` — apply to a public `string` field on a `MonoBehaviour` to get a validated Inspector dropdown instead of free text.

## SkeletonGraphic (UI Canvas)

Renders a skeleton inside a UI `Canvas` via `CanvasRenderer` (not `MeshRenderer`); interacts correctly with `RectMask2D`.

**Inspector properties**: `Skeleton Data Asset`, `Initial Skin`, `Initial Flip X`/`Initial Flip Y`, `Material` (must use a `Spine/SkeletonGraphic*` shader — never a standard/URP shader), `Freeze`, `Layout Scale Mode` (`None`/`Width Controls Height`/`Height Controls Width`/`Fit In Parent`/`Envelope Parent`), `Edit Layout Bounds`, `Match RectTransform with Mesh` (button), `Update When Invisible`, `Separator Slot Names`, `Enable Separation`, `Update Part Location`, `Multiple CanvasRenderers` (child `CanvasRenderer` per submesh, raises the texture limit at a performance cost), `Blend Mode Materials`, `Tint Black`, `CanvasGroup Compatible`, `PMA Vertex Colors`.

**Delegates**: same set as `SkeletonRenderer` (`OnRebuild`, `OnMeshAndMaterialsUpdated`, `UpdateLocal`, `UpdateComplete`, `UpdateWorld`).

### Material requirement (critical)

Only `Spine/SkeletonGraphic*` shaders work with `SkeletonGraphic` — never URP/LWRP shaders, never `Spine/Skeleton` (the non-UI shader), never a third-party non-`CanvasRenderer` shader. A wrong shader can look correct in the Editor and still fail on-device.

### Single-texture limitation

`CanvasRenderer` supports one texture by default. Enable `Advanced → Multiple CanvasRenderers` for a child `CanvasRenderer` per submesh (real performance cost) — prefer packing the skeleton into a single-page atlas instead.

### Vertex-data / material detection

`Advanced → Vertex Data` exposes `Tint Black`, `CanvasGroup Compatible`, `PMA Vertex Color` — each has a `Detect` button to auto-derive the right value, plus a combined `Detect Settings` and a `Detect Material` button to auto-assign a matching material.

### CanvasGroup alpha brightening issue

Lowering a parent `CanvasGroup`'s alpha brightens the skeleton, because vertex-color alpha modification conflicts with premultiplied-alpha shaders.

- **Without Tint Black**: use a `CanvasGroup`-compatible material from `Materials/UI-PMATexture/CanvasGroup` or `Materials/UI-StraightAlphaTex/CanvasGroup`; disable `Advanced → PMA Vertex Colors` (prevents double-darkening, at the cost of losing additive batching).
- **With Tint Black**: use the `SkeletonGraphic TintBlack` material from the `CanvasGroup` folder; enable `Advanced → CanvasGroup Compatible`; `PMA Vertex Colors` can be enabled either way (enabling it is recommended, for additive batching).

### Bounds/visibility

Visibility follows the `RectTransform` bounds — must not be smaller than the visible mesh, or `RectMask2D` culls it incorrectly. Drag-and-drop under a `Canvas` auto-matches bounds; otherwise use the `Match RectTransform with Mesh` button, or toggle `Edit Layout Bounds` to adjust manually in Scene view (green handle offsets the skeleton, blue handle adjusts the pivot).

### Setup

Drag `_SkeletonData` under a `Canvas` GameObject → choose `SkeletonGraphic (UI)`, or manually add `SkeletonGraphic` to a Canvas child → assign `_SkeletonData` → confirm the `Material` uses a `Spine/SkeletonGraphic*` shader → run `Detect Settings`/`Detect Material` if anything looks wrong.

## SkeletonMecanim

Animates the skeleton through Unity's Mecanim system instead of Spine's own `AnimationState` — Mecanim drives high-level control, Spine still poses the skeleton.

**Inspector properties**: `Animation Update` (`Update`/`FixedUpdate`/`Manual`), `Use Threading` (worse payoff than on `SkeletonAnimation` — Mecanim state queries still need the main thread), `Animator`, `Scene Preview`.

**Mecanim Translator properties**: `Auto Reset` (mix to setup pose when an animation finishes), `Custom Mix Mode` + a `Mix Modes` array to override per Mecanim layer.

**Mix modes**: `Mix Next` (default; recommended for Base Layer/Override — apply the previous track fully, mix in the next using Mecanim's weights), `Always Mix` (recommended for Additive — fade out previous, mix in next), `Hard` (formerly "Spine Style" — apply the next animation immediately), `Match` (4.2+; recommended for Blend Trees — calculates Spine mix weights to match Mecanim's own clip weights).

Formulas (`S` = setup pose when `Auto Reset` is on, `P` = previous clip pose, `N` = new clip pose, `w` = transition weight 0→1): Always Mix = `lerp(lerp(S, P, 1-w), N, w)`; Mix Next = `lerp(P, N, w)`; Hard = `N`; Match is context-dependent.

**Delegates**: same as `SkeletonAnimation` (`BeforeApply`, `UpdateLocal`, `UpdateComplete`, `UpdateWorld`).

### Limitations vs. SkeletonAnimation

1. **Setup-pose keys required on the following animation's first frame** to smoothly mix out a previous timeline's non-setup-pose end state — `SkeletonAnimation` handles this automatically, `SkeletonMecanim` doesn't. Workaround: enable `Auto Reset` (sharp transition, not smooth). Export requirement: disable `Animation cleanup` so those setup-pose keys aren't stripped as "identical to setup."
2. **No mix thresholds** — `TrackEntry.MixAttachmentThreshold` and similar have no equivalent.
3. **Threaded animation gains less** — Mecanim state queries force main-thread work, so `Use Threading` can't parallelize the whole task the way it does for `SkeletonAnimation`.

### Setup

Drag-and-drop instantiation as `SkeletonMecanim` auto-generates and assigns an Animator `Controller`; drag Spine animations onto the Animator panel to add clips; wire transitions normally. Mecanim's own transition durations are used — mix-duration values on the `SkeletonDataAsset` are ignored. Enabling `Apply Root Motion` on the `Animator` auto-adds `SkeletonMecanimRootMotion`.

### Mecanim animation events

Stored per `AnimationClip`, using standard Unity event-method naming; a folder path concatenates onto the event name with no separator:

```csharp
public class YourComponent : MonoBehaviour {
    void Footstep() { /* event "Footstep" outside any folder */ }
    void FoldernameFootstep() { /* event "Footstep" inside folder "Foldername" */ }
}
```

## Runtime instantiation

```csharp
// SkeletonAnimation GameObject
SkeletonComponents<SkeletonRenderer, SkeletonAnimation> instance =
    SkeletonAnimation.NewSkeletonAnimationGameObject(skeletonDataAsset);

// SkeletonGraphic GameObject
SkeletonComponents<SkeletonGraphic, SkeletonAnimation> instance =
    SkeletonGraphic.NewSkeletonGraphicGameObject(skeletonDataAsset, transform, skeletonGraphicMaterial);

// Generic
var instance = SkeletonRenderer.NewSpineGameObject<SkeletonRenderer, SkeletonMecanim>(skeletonDataAsset);
var graphicInstance = SkeletonGraphic.NewSkeletonGraphicGameObject<SkeletonMecanim>(skeletonDataAsset, parent, material);
```

From exported assets with no prior import:

```csharp
SpineAtlasAsset runtimeAtlasAsset = SpineAtlasAsset.CreateRuntimeInstance(atlasTxt, textures, materialPropertySource, true);
SkeletonDataAsset runtimeSkeletonDataAsset = SkeletonDataAsset.CreateRuntimeInstance(skeletonJson, runtimeAtlasAsset, true);
SkeletonAnimation instance = SkeletonAnimation.NewSkeletonAnimationGameObject(runtimeSkeletonDataAsset);
```

Example scenes/scripts: `Spine Examples/Other Examples/Instantiate from Script` — `SpawnFromSkeletonDataExample.cs`, `RuntimeLoadFromExportsExample.cs`, `SpawnSkeletonGraphicExample.cs`. Prefer the normal prefab/pooled-object workflow for anything beyond a rare fully-dynamic case — runtime instantiation from exports is less convenient to customize.

## Render separation (summary — see utility-components.md for the dedicated component)

Splits a skeleton's rendering across multiple GameObjects/layers for draw-order control (e.g. character partially behind an environment prop). `SkeletonRenderer`: set `Separator Slot Names` to the split points, then add `SkeletonRenderSeparator`. `SkeletonGraphic`: enable `Advanced → Enable Separation` directly — no extra component needed; it creates child `CanvasRenderer` GameObjects automatically. Example scene: `Spine Examples/Other Examples/SkeletonRenderSeparator`.

## Licensing

A Spine license is required to integrate the Spine Runtimes into an application.

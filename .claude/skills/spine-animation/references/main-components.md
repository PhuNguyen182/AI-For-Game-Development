# Main Components — SkeletonRenderer, SkeletonAnimation, SkeletonGraphic, SkeletonMecanim

Source: [spine-unity Main Components](https://esotericsoftware.com/spine-unity-main-components#Main-Components) (spine-unity v4.3+).
Covers: SKILL.md §4 — **"Pick the right main component before anything else"**, **"Use the `[Spine*]` attributes on every string field naming skeleton data"**.

Since v4.3 rendering and animation are separate components rather than one
inheritance chain, so the choice is really two choices: which renderer, and
which animation driver. Skeleton and skin manipulation is
[skeleton-api.md](skeleton-api.md); track playback is
[animation-state.md](animation-state.md); shader and material selection is
[rendering.md](rendering.md).

## Contents

- [The component matrix](#the-component-matrix)
- [SkeletonRenderer](#skeletonrenderer)
- [SkeletonAnimation](#skeletonanimation)
- [SkeletonGraphic — UI Canvas](#skeletongraphic--ui-canvas)
- [SkeletonMecanim](#skeletonmecanim)
- [String-property attributes](#string-property-attributes)
- [Runtime instantiation](#runtime-instantiation)

## The component matrix

| Component | Renders? | Animates? | Use when | Source |
|---|---|---|---|---|
| `SkeletonRenderer` | Yes, via `MeshRenderer` | No | World-space rendering; needs an animation driver alongside it | [Main Components](https://esotericsoftware.com/spine-unity-main-components#Main-Components) |
| `SkeletonGraphic` | Yes, via `CanvasRenderer` | No | The skeleton lives inside a UI `Canvas` | [Main Components](https://esotericsoftware.com/spine-unity-main-components#Main-Components) |
| `SkeletonAnimation` | No | Yes, Spine's own `AnimationState` | The default animation driver — highest customizability | [Main Components](https://esotericsoftware.com/spine-unity-main-components#Main-Components) |
| `SkeletonMecanim` | No | Yes, via Unity Mecanim | Mecanim authoring is specifically wanted, limitations accepted | [Main Components](https://esotericsoftware.com/spine-unity-main-components#Main-Components) |

## SkeletonRenderer

| Aspect | What it decides | Source |
|---|---|---|
| Mesh generation | Procedural mesh via `MeshRenderer`/`MeshFilter`, referencing the atlas texture assets | [Main Components](https://esotericsoftware.com/spine-unity-main-components) |
| Notable Inspector settings | `Initial Skin`, `Update When Invisible`, `Fix Draw Order` (blocks aggressive batching at 3+ submeshes), `Immutable Triangles`, `Separator Slot Names`, `Use Clipping`, `Z Spacing`, `Use Single Submesh`, `Use Threading`, `PMA Vertex Colors`, `Tint Black`, `Add Normals`, `Solve Tangents` | [Main Components](https://esotericsoftware.com/spine-unity-main-components) |
| Delegates | `OnRebuild` (after init), `OnMeshAndMaterialsUpdated` (end of `LateUpdate()`), `UpdateLocal`, `UpdateComplete`, `UpdateWorld` | [Main Components](https://esotericsoftware.com/spine-unity-main-components) |
| `UpdateMesh()` | Forces mesh regeneration regardless of `UpdateMode` | [Main Components](https://esotericsoftware.com/spine-unity-main-components) |
| Alone-usage limit | Only valid when animation is applied fully manually with no transitions, e.g. a UI gauge | [Main Components](https://esotericsoftware.com/spine-unity-main-components) |

**Critical caveat**: bones visible with no images almost always means `Initial
Skin` is still `default` — not a material or atlas fault.

## SkeletonAnimation

| Aspect | What it decides | Source |
|---|---|---|
| Requires a renderer | Pairs with `SkeletonRenderer` (world) or `SkeletonGraphic` (UI) | [Main Components](https://esotericsoftware.com/spine-unity-main-components) |
| Inspector settings | `Animation Name`, `Loop`, `Time Scale`, `Unscaled Time`, `Animation Update` (`Update`/`FixedUpdate`/`Manual`), `Use Threading` | [Main Components](https://esotericsoftware.com/spine-unity-main-components) |
| Update order | `SkeletonAnimation.Update()` advances and applies `AnimationState`, then `SkeletonRenderer.LateUpdate()` rebuilds the mesh | [Main Components](https://esotericsoftware.com/spine-unity-main-components) |
| Running before animations apply | Script execution order earlier than `SkeletonAnimation`, e.g. `[DefaultExecutionOrder(-1)]` | [Main Components](https://esotericsoftware.com/spine-unity-main-components) |
| Running after | Execution order after `SkeletonAnimation` in `Update()`, or before `SkeletonRenderer` in `LateUpdate()` | [Main Components](https://esotericsoftware.com/spine-unity-main-components) |
| With a `Rigidbody`/`Rigidbody2D` | Set `Animation Update` to `In FixedUpdate` | [Main Components](https://esotericsoftware.com/spine-unity-main-components) |

```csharp
public class SpineDriver : MonoBehaviour
{
    private SkeletonAnimation skeletonAnimation;
    private Spine.AnimationState animationState;
    private Spine.Skeleton skeleton;

    private void Awake()
    {
        this.skeletonAnimation = this.GetComponent<SkeletonAnimation>();
        this.skeleton = this.skeletonAnimation.Skeleton;
        this.animationState = this.skeletonAnimation.AnimationState;
    }
}
```

Manual update calls, when execution order cannot be used: `skeletonAnimation.Update(0)`
after a full-skeleton change, `AnimationState.Apply(skeleton)` after a
slot-only change, and `UpdateMesh()` when the modifying script runs after
`SkeletonAnimation`'s own `LateUpdate()`.

## SkeletonGraphic — UI Canvas

| Constraint | What it decides | Source |
|---|---|---|
| Material requirement | Only `Spine/SkeletonGraphic*` shaders work — never URP/LWRP shaders, never the non-UI `Spine/Skeleton` | [Main Components](https://esotericsoftware.com/spine-unity-main-components) |
| Single texture | `CanvasRenderer` supports one texture; `Advanced → Multiple CanvasRenderers` adds a child renderer per submesh at real cost | [Main Components](https://esotericsoftware.com/spine-unity-main-components) |
| Detection helpers | `Advanced → Vertex Data` exposes `Tint Black`, `CanvasGroup Compatible`, `PMA Vertex Color`, each with a `Detect` button, plus `Detect Settings` and `Detect Material` | [Main Components](https://esotericsoftware.com/spine-unity-main-components) |
| `CanvasGroup` alpha brightens | Vertex-colour alpha modification conflicts with premultiplied-alpha shaders | [Main Components](https://esotericsoftware.com/spine-unity-main-components) |
| Fix without Tint Black | Use a `CanvasGroup` material from `Materials/UI-PMATexture/CanvasGroup` or `UI-StraightAlphaTex/CanvasGroup`, and disable `PMA Vertex Colors` — losing additive batching | [Main Components](https://esotericsoftware.com/spine-unity-main-components) |
| Fix with Tint Black | Use the `SkeletonGraphic TintBlack` material from the `CanvasGroup` folder and enable `CanvasGroup Compatible`; `PMA Vertex Colors` may stay on, and should, for additive batching | [Main Components](https://esotericsoftware.com/spine-unity-main-components) |
| Bounds | Visibility follows the `RectTransform`; if it is smaller than the mesh, `RectMask2D` culls incorrectly — fix with `Match RectTransform with Mesh` | [Main Components](https://esotericsoftware.com/spine-unity-main-components) |
| Layout | `Layout Scale Mode`: `None`, `Width Controls Height`, `Height Controls Width`, `Fit In Parent`, `Envelope Parent` | [Main Components](https://esotericsoftware.com/spine-unity-main-components) |

**Critical caveat**: a wrong shader on `SkeletonGraphic` can look correct in
the Editor and still fail on device. Verify with `Detect Material` rather than
by eye.

## SkeletonMecanim

| Aspect | What it decides | Source |
|---|---|---|
| Division of labour | Mecanim drives high-level control; Spine still poses the skeleton | [Main Components](https://esotericsoftware.com/spine-unity-main-components) |
| Mix mode `Mix Next` | Default — applies the previous track fully and mixes the next in by Mecanim's weights; recommended for Base Layer and Override | [Main Components](https://esotericsoftware.com/spine-unity-main-components) |
| Mix mode `Always Mix` | Fades out previous, mixes in next; recommended for Additive | [Main Components](https://esotericsoftware.com/spine-unity-main-components) |
| Mix mode `Hard` | Applies the next animation immediately, no mixing | [Main Components](https://esotericsoftware.com/spine-unity-main-components) |
| Mix mode `Match` | 4.2+; computes Spine mix weights matching Mecanim's clip weights; recommended for Blend Trees | [Main Components](https://esotericsoftware.com/spine-unity-main-components) |
| `Auto Reset` | Mixes to setup pose when an animation finishes — a sharp transition, not a smooth one | [Main Components](https://esotericsoftware.com/spine-unity-main-components) |
| Mix durations | Mecanim's own transition durations apply; `SkeletonDataAsset` mix values are ignored | [Main Components](https://esotericsoftware.com/spine-unity-main-components) |
| Animation events | Stored per `AnimationClip` with standard Unity event-method naming; a folder path concatenates onto the name with no separator (`FoldernameFootstep`) | [Main Components](https://esotericsoftware.com/spine-unity-main-components) |

| Limitation vs. SkeletonAnimation | Consequence | Source |
|---|---|---|
| Setup-pose keys required on the next animation's first frame | Needed to mix out a previous timeline's non-setup-pose end state; `SkeletonAnimation` handles this automatically. Export with `Animation cleanup` disabled so those keys survive | [Main Components](https://esotericsoftware.com/spine-unity-main-components) |
| No mix thresholds | `TrackEntry.MixAttachmentThreshold` and equivalents have no counterpart | [Main Components](https://esotericsoftware.com/spine-unity-main-components) |
| Threading gains less | Mecanim state queries force main-thread work, so `Use Threading` cannot parallelize the whole task | [Main Components](https://esotericsoftware.com/spine-unity-main-components) |

## String-property attributes

| Attribute | Populates the dropdown from | Source |
|---|---|---|
| `[SpineBone]`, `[SpineSlot]`, `[SpineAttachment]`, `[SpineSkin]` | Bones, slots, attachments, and skins in the assigned `SkeletonDataAsset` | [Main Components](https://esotericsoftware.com/spine-unity-main-components) |
| `[SpineAnimation]`, `[SpineEvent]` | Animation and event names in the same asset | [Main Components](https://esotericsoftware.com/spine-unity-main-components) |
| `[SpineIkConstraint]`, `[SpineTransformConstraint]`, `[SpinePathConstraint]` | The corresponding constraint names | [Main Components](https://esotericsoftware.com/spine-unity-main-components) |

**Critical caveat**: a bare `string` field naming skeleton data fails at
runtime as a silent no-op when misspelled. The attribute turns that into an
edit-time dropdown, which is the entire reason it exists.

## Runtime instantiation

| Call | Effect | Source |
|---|---|---|
| `SkeletonAnimation.NewSkeletonAnimationGameObject(skeletonDataAsset)` | Creates a wired world-space instance | [Main Components](https://esotericsoftware.com/spine-unity-main-components) |
| `SkeletonGraphic.NewSkeletonGraphicGameObject(asset, parent, material)` | Creates a wired UI instance | [Main Components](https://esotericsoftware.com/spine-unity-main-components) |
| `SkeletonRenderer.NewSpineGameObject<TRenderer, TAnimator>(asset)` | Generic form, e.g. pairing with `SkeletonMecanim` | [Main Components](https://esotericsoftware.com/spine-unity-main-components) |
| `SpineAtlasAsset.CreateRuntimeInstance` + `SkeletonDataAsset.CreateRuntimeInstance` | Builds both assets from raw exports with no prior import | [Main Components](https://esotericsoftware.com/spine-unity-main-components) |

**Critical caveat**: prefer the normal prefab and pooling workflow. Runtime
instantiation from exports is harder to customize and is justified only by a
genuinely dynamic case.

Rendering separation is summarized here and owned by
[utility-components.md](utility-components.md). A Spine license is required to
integrate the Spine Runtimes into an application.

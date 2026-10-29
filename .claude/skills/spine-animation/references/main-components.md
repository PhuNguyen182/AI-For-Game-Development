# Main Components

Since 4.3 renderer and animation driver are separate components: choose both. Page: main-components.

| Component | Renders | Animates | Use when |
|---|---|---|---|
| `SkeletonRenderer` | `MeshRenderer` | no | World space; needs a driver (alone only for fully manual posing, e.g. a UI gauge) |
| `SkeletonGraphic` | `CanvasRenderer` | no | Skeleton inside a UI Canvas |
| `SkeletonAnimation` | no | Spine `AnimationState` | Default driver, most customisable |
| `SkeletonMecanim` | no | Unity Mecanim | Mecanim authoring wanted, limits accepted |

## SkeletonRenderer
- Bones visible, no images: `Initial Skin` is still `default` — not a material/atlas fault.
- Inspector: `Initial Skin`, `Update When Invisible`, `Fix Draw Order` (blocks aggressive batching at 3+ submeshes), `Immutable Triangles`, `Separator Slot Names`, `Use Clipping`, `Z Spacing`, `Use Single Submesh`, `Use Threading`, `PMA Vertex Colors`, `Tint Black`, `Add Normals`, `Solve Tangents`.
- Delegates: `OnRebuild` (after init), `OnMeshAndMaterialsUpdated` (end of `LateUpdate()`), `UpdateLocal`, `UpdateWorld`, `UpdateComplete`. `UpdateMesh()` forces regeneration regardless of `UpdateMode`.

## SkeletonAnimation
- Pairs with `SkeletonRenderer` or `SkeletonGraphic`. Inspector: `Animation Name`, `Loop`, `Time Scale`, `Unscaled Time`, `Animation Update` (`Update`/`FixedUpdate`/`Manual`), `Use Threading`.
- Order: `SkeletonAnimation.Update()` advances and applies `AnimationState`, then `SkeletonRenderer.LateUpdate()` rebuilds the mesh.
- Run before animations apply: execution order earlier than `SkeletonAnimation` (`[DefaultExecutionOrder(-1)]`). Run after: later in `Update()`, or before `SkeletonRenderer` in `LateUpdate()`.
- With `Rigidbody`/`Rigidbody2D`: `Animation Update` = `In FixedUpdate`.
- When execution order is not usable: `skeletonAnimation.Update(0)` after a full-skeleton change, `AnimationState.Apply(skeleton)` after a slot-only change, `UpdateMesh()` when the script runs after `SkeletonAnimation`'s `LateUpdate()`.
- Cache `skeletonAnimation.Skeleton` and `.AnimationState` in `Awake`.

## SkeletonGraphic
- Only `Spine/SkeletonGraphic*` materials; never URP/LWRP shaders or non-UI `Spine/Skeleton`. A wrong shader can look right in the Editor and fail on device — verify with `Detect Material`, not by eye.
- `CanvasRenderer` takes one texture; `Advanced → Multiple CanvasRenderers` adds a child renderer per submesh at real cost.
- `Advanced → Vertex Data`: `Tint Black`, `CanvasGroup Compatible`, `PMA Vertex Color`, each with `Detect`; also `Detect Settings`, `Detect Material`.
- A `CanvasGroup` alpha fade brightens the skeleton (vertex-colour alpha vs PMA shaders):
  - without Tint Black: use a `CanvasGroup` material (`Materials/UI-PMATexture/CanvasGroup` or `UI-StraightAlphaTex/CanvasGroup`) and disable `PMA Vertex Colors` (loses additive batching);
  - with Tint Black: `SkeletonGraphic TintBlack` material from the `CanvasGroup` folder, enable `CanvasGroup Compatible`, keep `PMA Vertex Colors` on.
- Visibility follows the `RectTransform`; smaller than the mesh makes `RectMask2D` cull wrongly — `Match RectTransform with Mesh`.
- `Layout Scale Mode`: `None`, `Width Controls Height`, `Height Controls Width`, `Fit In Parent`, `Envelope Parent`. No Layout Group may size the same `RectTransform` the skeleton drives.

## SkeletonMecanim
Mecanim drives high-level control; Spine still poses the skeleton. Mecanim transition durations apply; `SkeletonDataAsset` mix values are ignored.

| Mix mode | Behaviour | Recommended for |
|---|---|---|
| `Mix Next` (default) | Applies previous track fully, mixes next by Mecanim weights | Base Layer, Override |
| `Always Mix` | Fades out previous, mixes in next | Additive |
| `Hard` | Applies next immediately | — |
| `Match` (4.2+) | Spine mix weights match Mecanim clip weights | Blend Trees |

- `Auto Reset` mixes to setup pose on finish — a sharp transition.
- Events are stored per `AnimationClip` with Unity event-method naming; a folder path concatenates onto the name with no separator (`FoldernameFootstep`).
- Limits vs `SkeletonAnimation`: the next animation's first frame needs setup-pose keys to mix out a previous non-setup end state (export with `Animation cleanup` disabled); no `MixAttachmentThreshold` equivalents; `Use Threading` gains less (Mecanim queries force main-thread work); no Timeline track.

## `[Spine*]` attributes
`[SpineBone]`, `[SpineSlot]`, `[SpineAttachment]`, `[SpineSkin]`, `[SpineAnimation]`, `[SpineEvent]`, `[SpineIkConstraint]`, `[SpineTransformConstraint]`, `[SpinePathConstraint]` — dropdown from the assigned `SkeletonDataAsset`. A bare string misspelling is a silent no-op.

## Runtime instantiation
Prefer prefabs and pooling; use these only for a genuinely dynamic case.
- `SkeletonAnimation.NewSkeletonAnimationGameObject(skeletonDataAsset)`
- `SkeletonGraphic.NewSkeletonGraphicGameObject(asset, parent, material)`
- `SkeletonRenderer.NewSpineGameObject<TRenderer, TAnimator>(asset)` (e.g. with `SkeletonMecanim`)
- `SpineAtlasAsset.CreateRuntimeInstance` + `SkeletonDataAsset.CreateRuntimeInstance`: assets from raw exports, no import.

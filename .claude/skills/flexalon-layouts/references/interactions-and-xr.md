# Interactions and XR — click, drag, drop between layouts, and input providers

Sources: [Interactable](https://www.flexalon.com/docs/interactable), [XR Interactions](https://www.flexalon.com/docs/xr), [Class FlexalonInteractable](https://www.flexalon.com/docs/api/Flexalon.FlexalonInteractable.html), [Class FlexalonDragTarget](https://www.flexalon.com/docs/api/Flexalon.FlexalonDragTarget.html), [Interface InputProvider](https://www.flexalon.com/docs/api/Flexalon.InputProvider.html), [Enum InputMode](https://www.flexalon.com/docs/api/Flexalon.InputMode.html).
Covers: SKILL.md §4 — **"Wire click and drag through Flexalon Interactable plus Flexalon Drag Target, and confirm the input path"**.

Flexalon's built-in interaction moves objects *between layouts* — insert,
reorder, remove — rather than moving transforms freely. This file holds the
setup preconditions (which differ between world and UI), the component
surface, and how to replace the input source for a non-legacy input system
or an XR SDK.

- [Setup — the preconditions that actually fail](#setup--the-preconditions-that-actually-fail)
- [`FlexalonInteractable`](#flexaloninteractable)
- [Events and the state machine](#events-and-the-state-machine)
- [`FlexalonDragTarget`](#flexalondragtarget)
- [Replacing the input source](#replacing-the-input-source)
- [XR — XRI and Oculus Interaction SDK](#xr--xri-and-oculus-interaction-sdk)

## Setup — the preconditions that actually fail

| Step | World objects | UI objects | Source |
|---|---|---|---|
| Make an object interactive | `FlexalonInteractable` + a **`Collider`** | `FlexalonInteractable` + a **`Graphic`** with "Raycast Target" checked | [Interactable](https://www.flexalon.com/docs/interactable) |
| Make a layout accept objects | `FlexalonDragTarget` on the layout | Same | [Interactable](https://www.flexalon.com/docs/interactable) |
| Scene requirements | None beyond the collider | An **EventSystem** in the scene and a **GraphicsRaycaster** on the Canvas | [Interactable](https://www.flexalon.com/docs/interactable) |
| Smooth reordering under the cursor | Add `FlexalonLerpAnimator` or `FlexalonRigidBodyAnimator` to the objects in the target | Same | [Interactable](https://www.flexalon.com/docs/interactable) |

Nothing here reports a missing precondition — a UI object without a raycast
target, or a canvas without a GraphicsRaycaster, simply never receives input.
Check these before debugging the component.

## `FlexalonInteractable`

| Property | What it decides | Source |
|---|---|---|
| `Clickable` / `Draggable` (`bool`) | Which interactions this object supports at all | [Class FlexalonInteractable](https://www.flexalon.com/docs/api/Flexalon.FlexalonInteractable.html) |
| `MaxClickTime` (`float`) | Press-to-release under this counts as a click — and **a drag cannot start until it is exceeded**, so raising it delays every drag | [Interactable](https://www.flexalon.com/docs/interactable) |
| `MaxClickDistance` (`float`) | Press-to-release beyond this distance is a drag, not a click | [Class FlexalonInteractable](https://www.flexalon.com/docs/api/Flexalon.FlexalonInteractable.html) |
| `InterpolationSpeed` (`float`) | How quickly the dragged object chases the cursor | [Interactable](https://www.flexalon.com/docs/interactable) |
| `InsertRadius` (`float`, v3.2) | How close to a drag target's bounds the object must be to be inserted | [Interactable](https://www.flexalon.com/docs/interactable) |
| `Restriction` (`RestrictionType`) | `None = 0`, `Plane = 1` (moves on a plane through the start position with normal `PlaneNormal`), `Line = 2` (along `LineDirection`) | [Enum RestrictionType](https://www.flexalon.com/docs/api/Flexalon.FlexalonInteractable.RestrictionType.html) |
| `PlaneNormal`, `LineDirection` (`Vector3`) | The restriction's geometry, rotated by the layout the object started in when `LocalSpaceRestriction` is set | [Class FlexalonInteractable](https://www.flexalon.com/docs/api/Flexalon.FlexalonInteractable.html) |
| `HoldOffset` (`Vector3`) / `LocalSpaceOffset` | Lifts or floats the object while dragged — the standard "card rises off the table" effect | [Interactable](https://www.flexalon.com/docs/interactable) |
| `HoldRotation` (`Quaternion`), `RotateOnDrag` (`bool`) / `LocalSpaceRotation` | Tilts the object while dragged | [Class FlexalonInteractable](https://www.flexalon.com/docs/api/Flexalon.FlexalonInteractable.html) |
| `Handle` (`GameObject`, v4.0) | Hit-test this object instead of self — it needs the collider (world) or raycast-target graphic (UI), not the owner | [Interactable](https://www.flexalon.com/docs/interactable) |
| `Bounds` (`Collider`) | The object cannot be dragged outside this collider | [Class FlexalonInteractable](https://www.flexalon.com/docs/api/Flexalon.FlexalonInteractable.html) |
| `LayerMask` | Restricts which drag targets accept this object, compared against the target gameObject's layer — the mechanism for "only weapons go in weapon slots" | [Interactable](https://www.flexalon.com/docs/interactable) |
| `HideCursor` (`bool`) | Sets `Cursor.visible = false` while dragging | [Class FlexalonInteractable](https://www.flexalon.com/docs/api/Flexalon.FlexalonInteractable.html) |
| Set Parent While Dragging (Inspector) | Normally the interactable is **unparented** during a drag; this option reparents it to the hovered drag target instead | [Interactable](https://www.flexalon.com/docs/interactable) |
| `DragTarget` (`Transform`, get) / `DragSiblingIndex` (`int`, get) | Where the object would land if released right now — read these in `DragTargetChanged` to preview the drop | [Class FlexalonInteractable](https://www.flexalon.com/docs/api/Flexalon.FlexalonInteractable.html) |
| `HoveredObject(s)`, `SelectedObject(s)` (static) | Global current hover/selection sets — available without wiring an event | [Class FlexalonInteractable](https://www.flexalon.com/docs/api/Flexalon.FlexalonInteractable.html) |

## Events and the state machine

| Member | Fires when | Source |
|---|---|---|
| `Clicked` | Pressed and released within `MaxClickTime` | [Interactable](https://www.flexalon.com/docs/interactable) |
| `HoverStart` / `HoverEnd` | Hover begins / ends | [Interactable](https://www.flexalon.com/docs/interactable) |
| `SelectStart` / `SelectEnd` | Press down over the object / release | [Interactable](https://www.flexalon.com/docs/interactable) |
| `DragStart` / `DragEnd` | Drag begins / ends | [Interactable](https://www.flexalon.com/docs/interactable) |
| `DragTargetChanged` | The prospective drop target or sibling index changed mid-drag | [Class FlexalonInteractable](https://www.flexalon.com/docs/api/Flexalon.FlexalonInteractable.html) |
| `State` (`InteractableState`) | `Init = 0`, `Hovering = 1`, `Selecting = 2`, `Dragging = 3` | [Enum InteractableState](https://www.flexalon.com/docs/api/Flexalon.FlexalonInteractable.InteractableState.html) |

All six are `UnityEvent`s (`FlexalonInteractable.InteractableEvent`), so they
are Inspector-wireable — which is exactly the case `coding-principles.md`'s
Structure section names as the reason to accept `UnityEvent` over
`Action<>`. Subscribing from code still owes an unsubscribe in
`OnDisable`/`OnDestroy`, per that file's Event handlers section.

## `FlexalonDragTarget`

| Property | What it decides | Source |
|---|---|---|
| `CanAddObjects` / `CanRemoveObjects` (`bool`) | Whether this layout accepts drops / releases objects. Both false makes a read-only display that still reorders internally only if permitted | [Interactable](https://www.flexalon.com/docs/interactable) |
| `MinObjects` (`int`) | Once reached, objects can no longer be dragged out — the "must keep one equipped" rule | [Interactable](https://www.flexalon.com/docs/interactable) |
| `MaxObjects` (`int`) | Once reached, no new objects are accepted. **`0` means unlimited**, not "none" | [Interactable](https://www.flexalon.com/docs/interactable) |
| `Margin` (`Vector3`, v3.0) | Grows or shrinks the hit bounds, which otherwise equal the layout size | [Interactable](https://www.flexalon.com/docs/interactable) |
| `DragTargets` (static) | `IReadOnlyCollection<FlexalonDragTarget>` of every target in the scene | [Class FlexalonDragTarget](https://www.flexalon.com/docs/api/Flexalon.FlexalonDragTarget.html) |

## Replacing the input source

The default is `FlexalonMouseInputProvider`, built on **Unity's legacy input
system**. A project on the new Input System, on a custom input stack, or in
XR must supply its own `InputProvider`.

| Member | Contract | Source |
|---|---|---|
| `InputMode` (v3.2) | `Raycast = 0` — provide a ray and let Flexalon pick and move the object; `External = 1` — another system moves the object, Flexalon only tracks state changes | [Enum InputMode](https://www.flexalon.com/docs/api/Flexalon.InputMode.html) |
| `Active` (`bool`) | Whether input is currently engaged (button held) | [Interface InputProvider](https://www.flexalon.com/docs/api/Flexalon.InputProvider.html) |
| `Ray` (`Ray`) | Raycast mode: what to cast for hit-testing and movement | [Interface InputProvider](https://www.flexalon.com/docs/api/Flexalon.InputProvider.html) |
| `UIPointer` (`Vector3`) | Raycast mode: the screen-space position used to pick **UI** objects — a provider that sets only `Ray` will not pick uGUI | [Interface InputProvider](https://www.flexalon.com/docs/api/Flexalon.InputProvider.html) |
| `ExternalFocusedObject` (`GameObject`) | External mode: the object currently hovered or selected by the other system | [Interface InputProvider](https://www.flexalon.com/docs/api/Flexalon.InputProvider.html) |

Two ways to install one: assign `Flexalon.GetOrCreate().InputProvider` at
runtime, or implement it as a `MonoBehaviour` and assign it to the **Input
Provider** field on the `Flexalon` component. The provider is global — one
per project, not per object. Note the type/namespace aliasing caveat in
[core-concepts-and-pipeline.md](core-concepts-and-pipeline.md) when calling the static from another namespace.

## XR — XRI and Oculus Interaction SDK

| Aspect | XR Interaction Toolkit | Oculus Interaction SDK | Source |
|---|---|---|---|
| Enablement | Auto-detected; Flexalon adds `Flexalon XR Input Provider` | Requires the **`FLEXALON_OCULUS`** scripting define symbol (Project Settings → Player → Other Settings) | [XR](https://www.flexalon.com/docs/xr) |
| Per-object components | `Flexalon XR Input Provider` + `FlexalonInteractable` on every gameObject carrying an XR Interactable | `Flexalon Oculus Input Provider` + `FlexalonInteractable` on every gameObject carrying an Interactable | [XR](https://www.flexalon.com/docs/xr) |
| Required SDK change | On `XR Hand Grab Interactable`, **uncheck `Retain Transform Parent`** — Flexalon decides parenting instead | — | [XR](https://www.flexalon.com/docs/xr) |
| Prerequisite | Grabbing and moving objects must already work through the SDK before Flexalon is added | Same | [XR](https://www.flexalon.com/docs/xr) |
| Division of labour | The SDK owns drag movement; `FlexalonInteractable` only inserts and removes objects from layouts | Same | [XR](https://www.flexalon.com/docs/xr) |

**Critical caveat**: because Flexalon does not control the dragged gameObject
under an XR provider, "several features of Flexalon Interactable will be
disabled" — the movement-shaping properties (restriction, hold offset/
rotation, interpolation, bounds) are the SDK's job there, not Flexalon's.
The docs enumerate the exact disabled set only in an image; confirm against
the installed version before promising one of those behaviours in XR.

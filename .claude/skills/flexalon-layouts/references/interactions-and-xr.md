# Interactions and XR

Pages: `/docs/interactable`, `/docs/xr`, API `FlexalonInteractable`, `FlexalonDragTarget`, `InputProvider`, `InputMode`.

Built-in interaction moves objects between layouts (insert, reorder, remove), not free transforms.

## Preconditions (nothing reports a missing one; input just never arrives)
| | World | UI |
|---|---|---|
| Interactive object | `FlexalonInteractable` + `Collider` | `FlexalonInteractable` + `Graphic` with Raycast Target |
| Accepting layout | `FlexalonDragTarget` | same |
| Scene | none | EventSystem + `GraphicRaycaster` on the Canvas |

Smooth reordering needs a `FlexalonLerpAnimator` or `FlexalonRigidBodyAnimator` on the objects in the target.

## `FlexalonInteractable`
| Property | Decides |
|---|---|
| `Clickable`/`Draggable` | Supported interactions |
| `MaxClickTime` | Click threshold; a drag cannot start until exceeded, so raising it delays every drag |
| `MaxClickDistance` | Beyond it is a drag |
| `InterpolationSpeed` | How fast the object chases the cursor |
| `InsertRadius` (v3.2) | Distance to a target's bounds for insertion |
| `Restriction` | `None = 0`, `Plane = 1` (`PlaneNormal`), `Line = 2` (`LineDirection`); `LocalSpaceRestriction` rotates by the start layout |
| `HoldOffset` / `LocalSpaceOffset`, `HoldRotation` / `LocalSpaceRotation` / `RotateOnDrag` | Lift/tilt while dragged; `LocalSpace*` apply them in the start layout's local space |
| `Handle` (v4.0) | Hit-test another object (it needs the collider/graphic) |
| `Bounds` (`Collider`) | Cannot be dragged outside |
| `LayerMask` | Which targets accept it, by target layer ("only weapons in weapon slots") |
| `HideCursor` | `Cursor.visible = false` while dragging |
| Set Parent While Dragging (Inspector) | Default is unparented during drag; this reparents to the hovered target |
| `DragTarget`, `DragSiblingIndex` | Where a release would land; read in `DragTargetChanged` |
| `HoveredObject(s)`, `SelectedObject(s)` (static) | Global sets |

Events (`UnityEvent`s, Inspector-wireable): `Clicked`, `HoverStart/End`, `SelectStart/End`, `DragStart/End`, `DragTargetChanged`. `State`: `Init = 0`, `Hovering = 1`, `Selecting = 2`, `Dragging = 3`. Subscribing from code owes an unsubscribe in `OnDisable`/`OnDestroy`.

## `FlexalonDragTarget`
| Property | Decides |
|---|---|
| `CanAddObjects`/`CanRemoveObjects` | Accept drops / release objects |
| `MinObjects` | At the minimum, objects cannot leave ("keep one equipped") |
| `MaxObjects` | At the maximum, no more accepted; `0` is unlimited |
| `Margin` (v3.0) | Grows/shrinks hit bounds (default = layout size) |
| `DragTargets` (static) | Every target in the scene |

## Input source
Default `FlexalonMouseInputProvider` uses Unity's legacy input. New Input System, custom stacks and XR need their own `InputProvider`, assigned via `Flexalon.GetOrCreate().InputProvider` or the singleton's Input Provider field (one per project; alias per [core-concepts-and-pipeline.md](core-concepts-and-pipeline.md)).

| Member | Contract |
|---|---|
| `InputMode` (v3.2) | `Raycast = 0`: provide a ray, Flexalon picks and moves; `External = 1`: another system moves, Flexalon tracks state |
| `Active` | Button held |
| `Ray` | Raycast mode hit-test/move ray |
| `UIPointer` (`Vector3`) | Screen position to pick UI; a provider setting only `Ray` never picks uGUI |
| `ExternalFocusedObject` | External mode hovered/selected object |

## XR
| | XR Interaction Toolkit | Oculus Interaction SDK |
|---|---|---|
| Enable | Auto-detected; adds `Flexalon XR Input Provider` | Scripting define `FLEXALON_OCULUS` (Player > Other Settings) |
| Per object | `Flexalon XR Input Provider` + `FlexalonInteractable` on every XR Interactable | `Flexalon Oculus Input Provider` + `FlexalonInteractable` |
| SDK change | `XR Hand Grab Interactable`: uncheck `Retain Transform Parent` | none |

Grab must already work in the SDK first. The SDK owns drag movement; `FlexalonInteractable` only inserts/removes objects from layouts, so several movement-shaping features are disabled. The docs list the exact set only in an image: confirm on the installed version before promising restriction, hold offset, interpolation or bounds in XR.

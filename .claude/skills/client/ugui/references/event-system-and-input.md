# EventSystem, Raycasters, and Input Modules

Source: [Events](https://docs.unity3d.com/Packages/com.unity.ugui@2.6/manual/EventSystem.html), [Event System Reference](https://docs.unity3d.com/Packages/com.unity.ugui@2.6/manual/EventSystemReference.html), [Standalone Input Module](https://docs.unity3d.com/Packages/com.unity.ugui@2.6/manual/script-StandaloneInputModule.html), [Graphic Raycaster](https://docs.unity3d.com/Packages/com.unity.ugui@2.6/manual/script-GraphicRaycaster.html).
Covers: SKILL.md §4 — "One EventSystem, one active Input Module, per scene", "Pick the right Raycaster for what the pointer needs to hit".

## EventSystem

`EventSystem` is the coordinator: it tracks the currently selected
GameObject, determines which Input Module is active, drives raycasting
when the active module needs it, and updates modules each frame. **Exactly
one Input Module may be active at a time**, and it must live on the same
GameObject as the `EventSystem`.

## Input Modules

| Module | Role |
|---|---|
| **Standalone Input Module** (legacy) | Reads the legacy Input Manager's named axes/buttons: Horizontal/Vertical Axis, Submit/Cancel Button, plus Input Actions Per Second and Repeat Delay for held-navigation repeat rate, and a Force Module Active override. Drives pointer events via the Graphic/Physics Raycasters. |
| **Input System UI Input Module** | Owned by `unity-input-system` (see its `devices-and-ui-integration.md`) — replaces the Standalone module when the Input System package's UI actions are wired in, and feeds both uGUI and UI Toolkit alike. |

**Never run both modules at once** — only one is ever active per
`EventSystem`, and the project's Active Input Handling setting (per
`unity-input-system`'s `migration-and-settings.md`) decides which one is
even relevant.

## Raycasters

| Raycaster | Hits |
|---|---|
| **Graphic Raycaster** | Every `Graphic` on the `Canvas` it's attached to. Configurable: `Ignore Reversed Graphics` (exclude back-facing elements — relevant on World Space/rotated canvases), `Blocking Objects` and `Blocking Mask` (let 2D/3D scene geometry in front of the canvas occlude UI hit-testing) |
| **Physics Raycaster** | 3D Colliders, for a pointer event that must also reach world objects (e.g. click-through from UI into the 3D scene) |
| **Physics 2D Raycaster** | 2D Colliders, same idea for a 2D project |

A `Graphic Raycaster` lives on the `Canvas` GameObject itself, not on the
`EventSystem`. Every `Canvas` that should receive pointer events needs its
own.

## Event interfaces and EventTrigger

Interaction components implement typed interfaces
(`IPointerClickHandler`, `IPointerEnterHandler`, `IPointerExitHandler`,
`IBeginDragHandler`/`IDragHandler`/`IEndDragHandler`, `IScrollHandler`,
`ISelectHandler`/`IDeselectHandler`, `ISubmitHandler`/`ICancelHandler`,
`IMoveHandler`, `IUpdateSelectedHandler`, `IInitializePotentialDragHandler`)
dispatched by `ExecuteEvents`. Implement the interface directly on a
`MonoBehaviour` for a component that always needs the behavior; use the
`EventTrigger` component instead only for a one-off, Inspector-wired
handler on an object that doesn't otherwise need a dedicated script — per
`coding-principles.md`'s Event handlers rule, still name a method rather
than leaving an inline lambda wired in the Inspector where the object's
lifetime could outlive a subscription.

## Custom input modules

A custom Input Module subclasses `BaseInputModule` (or `PointerInputModule`
for pointer-style input) and is responsible for driving its own raycasting
and event dispatch each frame. This is rare, escalation-territory work —
reach for the existing Standalone/Input-System-UI modules first; write a
custom one only when a genuinely novel input source needs to drive uGUI
that neither module can be configured to read.

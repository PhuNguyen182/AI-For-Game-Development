# EventSystem, Raycasters, Input Modules

- `EventSystem` tracks the selected GameObject, picks the active Input Module, drives raycasting and updates modules. **Exactly one Input Module is active**, on the same GameObject as the `EventSystem`.
- **Standalone Input Module** (legacy): reads Input Manager axes: Horizontal/Vertical Axis, Submit/Cancel Button, Input Actions Per Second, Repeat Delay, Force Module Active.
- **Input System UI Input Module**: owned by `unity-input-system` (`devices-and-ui-integration.md`); replaces Standalone and serves uGUI and UI Toolkit. The Active Input Handling setting (`migration-and-settings.md` there) decides which applies.

## Raycasters
| Raycaster | Hits |
|---|---|
| Graphic Raycaster | `Graphic`s on its Canvas; sits on the Canvas GameObject, one per Canvas that takes input. `Ignore Reversed Graphics` (back-facing, World Space/rotated canvases); `Blocking Objects` + `Blocking Mask` let scene geometry occlude UI |
| Physics Raycaster | 3D Colliders (click-through into the 3D scene) |
| Physics 2D Raycaster | 2D Colliders |

## Event interfaces
Dispatched by `ExecuteEvents`: `IPointerClick/Enter/Exit`, `IBeginDrag/IDrag/IEndDragHandler`, `IScrollHandler`, `ISelect/IDeselectHandler`, `ISubmit/ICancelHandler`, `IMoveHandler`, `IUpdateSelectedHandler`, `IInitializePotentialDragHandler`.
- Implement on a `MonoBehaviour` when the component always needs it; use `EventTrigger` only for a one-off Inspector-wired handler.
- Wire a named method, not an inline lambda that can outlive its subscription (`csharp-standards` event-handler rule).

## Custom input module
Subclass `BaseInputModule` (or `PointerInputModule`); it owns its raycasting and dispatch each frame. Rare: only for an input source neither built-in module can read.

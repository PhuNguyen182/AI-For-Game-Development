# Runtime panels and input

Sources: [Runtime UI](https://docs.unity3d.com/Manual/UIE-support-for-runtime-ui.html), [Get started](https://docs.unity3d.com/Manual/UIE-get-started-with-runtime-ui.html), [UI Document](https://docs.unity3d.com/Manual/UIE-create-ui-document-component.html), [UIDocument API](https://docs.unity3d.com/ScriptReference/UIElements.UIDocument.html), [Panel Renderer](https://docs.unity3d.com/Manual/ui-systems/panel-renderer-component.html), [Panel Settings](https://docs.unity3d.com/Manual/UIE-Runtime-Panel-Settings.html), [World space](https://docs.unity3d.com/Manual/ui-systems/world-space-ui.html), [Create world space](https://docs.unity3d.com/Manual/ui-systems/create-world-space-ui.html), [World input](https://docs.unity3d.com/Manual/ui-systems/world-space-panel-input-configuration.html), [Event system](https://docs.unity3d.com/Manual/UIE-Runtime-Event-System.html).

## UIDocument vs Panel Renderer
As of Unity 6.5 the Manual says "UI Document component is obsolete and superseded by the Panel Renderer component", yet the `UIDocument` class has no `[Obsolete]` attribute and existing components keep working. Treat it as a version-gated choice.

| Editor | Use |
|---|---|
| 6.5+ | Panel Renderer (`GameObject > UI Toolkit > Panel Renderer`) for new UI: same features plus reload behavior and performance gains; the menu no longer offers `UIDocument` |
| Earlier | `UIDocument`; Panel Renderer does not exist |

- `UIDocument.panelSettings` / `.visualTreeAsset` link the `PanelSettings` asset and the UXML loaded into `rootVisualElement`. `parentUI` auto-populates when the parent GameObject also has a `UIDocument` (nesting for draw order and focus).
- Draw order: `sortingOrder` among siblings sharing a host or `PanelSettings`, lower first. Panel Renderer: children above parents, siblings by ascending Sort Order; several can share one `PanelSettings`.
- Panel Renderers on the same `PanelSettings` share one focus navigation context: tab order can cross apparently separate documents.
- Query elements only in the `RegisterUIReloadCallback` callback (`CreateGUI()` for Editor), not `OnEnable`/`Awake`; unregister in `OnDestroy`.

## PanelSettings
| Scale Mode | Fields | Use for |
|---|---|---|
| Constant Pixel Size | `Scale` (> 0), Reference Sprite PPU | Pixel-exact UI at any resolution |
| Scale With Screen Size | Reference Resolution, Screen Match Mode (`Match Width or Height` 0-1 slider, `Shrink`, `Expand`) | Responsive PC + mobile HUD (uGUI `CanvasScaler` analog) |
| Constant Physical Size | Reference DPI, Fallback DPI, Reference Sprite PPU | Constant real-world size across devices |

- Dynamic Atlas Settings (Min/Max Atlas Size, Max Sub Texture Size, Active Filters): wrong filters exclude textures and fragment draw calls ([rendering-and-performance.md](rendering-and-performance.md)).
- Vertex Budget default `0` = automatic. An unset Text Settings asset is auto-created, not an error.

## World space
- `PanelSettings` Render Mode = World Space is the single switch. Sizing: Size Mode (Dynamic/Fixed), Pivot Reference Size (Bounding Box/Layout), Pivot (9 positions). Pixels Per Unit default 100.
- Input needs a **World Document Raycaster** (ray through Physics layers to a Collider); a plain `GraphicRaycaster` as on uGUI's World Space Canvas does not work. Fields: Interaction Layers, Event Cameras (tried in order until a Collider is hit), Max Interaction Distance.
- "Auto Create Panel Components" adds World Document Raycaster + Panel Raycaster + Panel Event Handler; disabling it means wiring all three by hand.
- Unverified: the exact mesh/`RenderTexture` mechanics. Older tutorials wire a `RenderTexture` onto a quad; the current Manual describes World Space mode plus the raycaster instead. Check the live page before asserting a mechanism.

## EventSystem
- On entering Play mode UI Toolkit creates its own scene-less default event system supporting most devices, auto-detecting legacy Input Manager vs Input System: no `EventSystem` GameObject is needed.
- Needed only when the scene also contains uGUI. With the Input System package active, Unity substitutes an Input System UI Input Module that dispatches to both uGUI and UI Toolkit.
- Adding an `EventSystem` makes UI Toolkit auto-create `PanelRaycaster` + `PanelEventHandler` per panel so both run under one pipeline. In a pure UI Toolkit scene that only changes the input pipeline, for no gain.

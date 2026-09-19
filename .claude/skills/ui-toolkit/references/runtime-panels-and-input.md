# Runtime Panels & Input — UIDocument, Panel Renderer, PanelSettings, World Space

Sources: [Support for runtime UI](https://docs.unity3d.com/Manual/UIE-support-for-runtime-ui.html), [Get started with runtime UI](https://docs.unity3d.com/Manual/UIE-get-started-with-runtime-ui.html), [UI Document component](https://docs.unity3d.com/Manual/UIE-create-ui-document-component.html), [`UIDocument` API](https://docs.unity3d.com/ScriptReference/UIElements.UIDocument.html), [Panel Renderer component](https://docs.unity3d.com/Manual/ui-systems/panel-renderer-component.html), [Runtime Panel Settings](https://docs.unity3d.com/Manual/UIE-Runtime-Panel-Settings.html), [World space UI](https://docs.unity3d.com/Manual/ui-systems/world-space-ui.html), [Create world space UI](https://docs.unity3d.com/Manual/ui-systems/create-world-space-ui.html), [World space panel input configuration](https://docs.unity3d.com/Manual/ui-systems/world-space-panel-input-configuration.html), [Runtime event system](https://docs.unity3d.com/Manual/UIE-Runtime-Event-System.html).
Covers: SKILL.md §4 — **"Pick Panel Renderer or `UIDocument` by the installed Editor version, and set the Scale Mode from the target platform"**, **"Add an `EventSystem` only when uGUI shares the scene"**.

Hosting a visual tree at runtime: which component creates the panel, how
`PanelSettings` scales and atlases it, how world-space UI differs from
uGUI's World Space Canvas, and whether the scene needs an `EventSystem` at
all.

## Table of contents
- [UIDocument vs Panel Renderer](#uidocument-vs-panel-renderer)
- [PanelSettings — scale modes](#panelsettings--scale-modes)
- [PanelSettings — atlas and budget](#panelsettings--atlas-and-budget)
- [World space UI](#world-space-ui)
- [Runtime input — does UI Toolkit need an EventSystem](#runtime-input--does-ui-toolkit-need-an-eventsystem)

## UIDocument vs Panel Renderer

**Critical caveat**: as of **Unity 6.5**, the Manual states "UI Document
component is obsolete and superseded by the Panel Renderer component" — but
the `UIDocument` C# class itself carries no compiler `[Obsolete]` attribute,
and existing `UIDocument` components keep working unchanged. Treat this as
a version-gated authoring decision, not a hard ban: confirm the installed
Editor version (per [root-links.md](root-links.md)) before choosing.

| Subject | What it decides | Source |
|---|---|---|
| Unity 6.5+ | Use **Panel Renderer** (`GameObject > UI Toolkit > Panel Renderer`) for new runtime UI — same functionality plus reload behavior and performance improvements, and the Editor no longer offers `UIDocument` from that menu | [UI Document component](https://docs.unity3d.com/Manual/UIE-create-ui-document-component.html) |
| Earlier Unity versions | `UIDocument` remains the current, correct API — Panel Renderer does not exist yet | [Get started with runtime UI](https://docs.unity3d.com/Manual/UIE-get-started-with-runtime-ui.html) |
| `UIDocument.panelSettings` / `.visualTreeAsset` | Links the `PanelSettings` asset and the UXML auto-loaded into `rootVisualElement` | [`UIDocument` API](https://docs.unity3d.com/ScriptReference/UIElements.UIDocument.html) |
| `UIDocument.parentUI` | Auto-populated when the GameObject's parent also carries a `UIDocument`, establishing nesting for draw order and focus | [`UIDocument` API](https://docs.unity3d.com/ScriptReference/UIElements.UIDocument.html) |
| `sortingOrder` | Draw order among siblings sharing the same host or `PanelSettings`; lower renders first | [`UIDocument` API](https://docs.unity3d.com/ScriptReference/UIElements.UIDocument.html) |
| Panel Renderer draw order | Child components render above parents; siblings render by ascending Sort Order. Multiple Panel Renderers can share one `PanelSettings` | [Panel Renderer component](https://docs.unity3d.com/Manual/ui-systems/panel-renderer-component.html) |
| Shared focus gotcha | Multiple Panel Renderers on the same `PanelSettings` share **one** focus navigation context — tab order can cross what look like separate documents | [Panel Renderer component](https://docs.unity3d.com/Manual/ui-systems/panel-renderer-component.html) |
| Lifecycle hook | Query elements only inside `RegisterUIReloadCallback`'s callback (or `CreateGUI()` for Editor windows) — never `OnEnable`/`Awake`, since the tree is not guaranteed loaded there. Unregister in `OnDestroy` | [Panel Renderer component](https://docs.unity3d.com/Manual/ui-systems/panel-renderer-component.html) |

## PanelSettings — scale modes

| Mode | Fields | Use for | Source |
|---|---|---|---|
| Constant Pixel Size | `Scale` multiplier (must be > 0), Reference Sprite Pixels Per Unit | A UI that must stay pixel-exact regardless of resolution | [Runtime Panel Settings](https://docs.unity3d.com/Manual/UIE-Runtime-Panel-Settings.html) |
| Scale With Screen Size | Reference Resolution, Screen Match Mode (`Match Width or Height` with a 0–1 slider, `Shrink`, `Expand`) | A responsive PC + mobile HUD — the direct analog of uGUI's `CanvasScaler`, per `coding-principles.md`'s responsive-UI expectation | [Runtime Panel Settings](https://docs.unity3d.com/Manual/UIE-Runtime-Panel-Settings.html) |
| Constant Physical Size | Reference DPI, Fallback DPI, Reference Sprite Pixels Per Unit | A UI that must keep a constant real-world size across devices | [Runtime Panel Settings](https://docs.unity3d.com/Manual/UIE-Runtime-Panel-Settings.html) |

## PanelSettings — atlas and budget

| Field | Effect | Source |
|---|---|---|
| Dynamic Atlas Settings (Min/Max Atlas Size, Max Sub Texture Size, Active Filters) | Governs which textures batch into the runtime atlas — misconfigured filters exclude textures and fragment draw calls, per [rendering-and-performance.md](rendering-and-performance.md) | [Runtime Panel Settings](https://docs.unity3d.com/Manual/UIE-Runtime-Panel-Settings.html) |
| Vertex Budget | Default `0` = automatic sizing | [Runtime Panel Settings](https://docs.unity3d.com/Manual/UIE-Runtime-Panel-Settings.html) |
| Text Settings asset | If left unset, Unity **auto-creates a default** rather than failing | [Runtime Panel Settings](https://docs.unity3d.com/Manual/UIE-Runtime-Panel-Settings.html) |

## World space UI

| Subject | What it decides | Source |
|---|---|---|
| Enabling | Set the `PanelSettings` **Render Mode to World Space** — the single switch that repositions the panel alongside 2D/3D scene content instead of on screen | [World space UI](https://docs.unity3d.com/Manual/ui-systems/world-space-ui.html) |
| Sizing fields | Size Mode (Dynamic/Fixed), Pivot Reference Size (Bounding Box/Layout), Pivot (one of 9 anchor positions) | [Create world space UI](https://docs.unity3d.com/Manual/ui-systems/create-world-space-ui.html) |
| Pixels Per Unit | Default **100** — panel-space pixels per one World Space unit | [Create world space UI](https://docs.unity3d.com/Manual/ui-systems/create-world-space-ui.html) |
| Input — **World Document Raycaster** | Required component that casts a world-space ray through Physics layers to hit a Collider and resolve the pointer target — a UI Toolkit World Space panel does **not** get input the way uGUI's World Space Canvas does with a plain `GraphicRaycaster` | [World space panel input configuration](https://docs.unity3d.com/Manual/ui-systems/world-space-panel-input-configuration.html) |
| Raycaster fields | Interaction Layers, Event Cameras (tried sequentially until one hits a Collider), Max Interaction Distance | [World space panel input configuration](https://docs.unity3d.com/Manual/ui-systems/world-space-panel-input-configuration.html) |
| Auto-setup | "Auto Create Panel Components" creates World Document Raycaster + Panel Raycaster + Panel Event Handler together; disabling it means wiring all three manually | [World space panel input configuration](https://docs.unity3d.com/Manual/ui-systems/world-space-panel-input-configuration.html) |

**Critical caveat**: do not assume UI Toolkit World Space needs a manually
wired `RenderTexture` on a quad the way older tutorials describe — the
current pipeline is PanelSettings World Space mode plus the Panel Renderer's
sizing fields and the World Document Raycaster. The exact mesh mechanics
were not confirmed on the pages fetched for this skill; verify on the live
Manual before asserting the mechanism to someone else.

## Runtime input — does UI Toolkit need an EventSystem?

| Subject | What it decides | Source |
|---|---|---|
| Default behavior | On entering Play mode, UI Toolkit creates its **own default event system that is not part of any scene** and supports most input devices automatically — **no `EventSystem` GameObject is required**, unlike uGUI | [Runtime event system](https://docs.unity3d.com/Manual/UIE-Runtime-Event-System.html) |
| Input backend | The default event system auto-detects whether the legacy Input Manager or the Input System package is active | [Runtime event system](https://docs.unity3d.com/Manual/UIE-Runtime-Event-System.html) |
| Mixing with uGUI | An `EventSystem` is only needed when the scene **also** contains uGUI. If the Input System package is active, Unity substitutes an Input System UI Input Module for the Standalone one, and that module dispatches to both uGUI and UI Toolkit elements | [Runtime event system](https://docs.unity3d.com/Manual/UIE-Runtime-Event-System.html) |
| Effect of adding an EventSystem | UI Toolkit detects it and auto-creates `PanelRaycaster` + `PanelEventHandler` per panel so both systems interoperate under one input pipeline | [Runtime event system](https://docs.unity3d.com/Manual/UIE-Runtime-Event-System.html) |

**Critical caveat**: a scene that is pure UI Toolkit needs no `EventSystem`
at all. Add one, or route through `unity-input-system`'s
`InputSystemUIInputModule`, only once uGUI is genuinely present in the same
scene — adding it unconditionally is not "safer," it just changes which
input pipeline UI Toolkit runs under.

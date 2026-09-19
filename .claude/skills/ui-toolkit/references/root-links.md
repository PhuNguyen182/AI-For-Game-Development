# Root Links — Unity UI Toolkit (UnityEngine.UIElements)

Source: the root index pages listed below, as provided for this skill.
Covers: the whole skill — provenance and version anchor for every file in
this folder.

UI Toolkit ships as a **built-in** Editor/runtime feature, not an installable
package, so every Manual and Scripting API link below is unversioned and
resolves to the current documentation set rather than a pinned Editor
version. At the time of writing that resolved to **Unity 6.5 (6000.5)** — the
first version to ship the **Panel Renderer** component, which the Manual now
calls the successor to `UIDocument` (see
[runtime-panels-and-input.md](runtime-panels-and-input.md)). Confirm the
installed Editor version before assuming Panel Renderer, or any other
6.5-era field, exists in an older project; any default value quoted in this
folder was read at authoring time and should be re-checked against the
installed Editor. Two genuinely versioned, separately installable packages
sit beside core UI Toolkit: `com.unity.ui.test-framework` (UI test helpers)
and the optional `com.unity.vectorgraphics` / `com.unity.2d.sprite`
(let USS `background-image` and UI Builder accept `VectorImage`/`Sprite`
assets) — everything else here is core engine.

| Root | Holds | Source |
|---|---|---|
| Manual — UI Toolkit index | The full topic tree this skill is built from | [UI Toolkit](https://docs.unity3d.com/Manual/UIElements.html) |
| Scripting API — `UnityEngine.UIElements` | Every `VisualElement`, event, and binding type | [UIElements namespace](https://docs.unity3d.com/ScriptReference/UnityEngine.UIElements.html) |
| Best Practice Guide (validated Unity 6.0) | Advanced-developer recommendations; cross-check against the current Manual since it predates 6.5 | [UI Toolkit for advanced Unity developers](https://docs.unity3d.com/Manual/best-practice-guides/ui-toolkit-for-advanced-unity-developers/bpg-uiad-index.html) |
| UI Test Framework 1.0 (separate package) | `EditorWindowUITestFixture<T>`, `simulate` helpers | [UI Test Framework](https://docs.unity3d.com/Packages/com.unity.ui.test-framework@1.0/manual/index.html) |

## Topic → file map

| Topic | File | Source |
|---|---|---|
| Choosing IMGUI / uGUI / UI Toolkit | [choosing-ui-system.md](choosing-ui-system.md) | [Comparison of UI systems](https://docs.unity3d.com/Manual/UI-system-compare.html) |
| UXML, VisualElement tree, UI Builder, custom controls | [uxml-and-visual-tree.md](uxml-and-visual-tree.md) | [Structure UI](https://docs.unity3d.com/Manual/UIE-structure-ui.html) |
| USS selectors, precedence, layout defaults | [uss-styling-and-layout.md](uss-styling-and-layout.md) | [Style UI](https://docs.unity3d.com/Manual/UIE-USS.html) |
| Text elements, rich text, font assets | [text-and-fonts.md](text-and-fonts.md) | [Work with text](https://docs.unity3d.com/Manual/UIE-work-with-text.html) |
| Event propagation, Manipulators, focus | [events-and-manipulators.md](events-and-manipulators.md) | [Control behavior with events](https://docs.unity3d.com/Manual/UIE-Events.html) |
| `UIDocument`/Panel Renderer, `PanelSettings`, world space, runtime input | [runtime-panels-and-input.md](runtime-panels-and-input.md) | [Support for runtime UI](https://docs.unity3d.com/Manual/UIE-support-for-runtime-ui.html) |
| `CreateGUI`, custom inspectors/PropertyDrawers, ViewData | [editor-ui-authoring.md](editor-ui-authoring.md) | [Support for Editor UI](https://docs.unity3d.com/Manual/UIE-support-for-editor-ui.html) |
| Runtime data binding vs `SerializedObject` binding | [data-binding.md](data-binding.md) | [Data binding](https://docs.unity3d.com/Manual/UIE-data-binding.html) |
| Batching, dynamic atlas, `UsageHints`, element pooling | [rendering-and-performance.md](rendering-and-performance.md) | [UI Renderer](https://docs.unity3d.com/Manual/UIE-ui-renderer.html) |
| UI Test Framework, migration from uGUI/IMGUI | [testing-and-migration.md](testing-and-migration.md) | [Test UI](https://docs.unity3d.com/Manual/UIE-test-ui.html) / [Migration guides](https://docs.unity3d.com/Manual/UIE-migration-guides.html) |

## Disclosed gaps

| Page | Issue |
|---|---|
| `accessibility/get-started-screen-reader.html` | 404 at authoring time; only the accessibility landing page's summary is cited in [testing-and-migration.md](testing-and-migration.md) |
| Manual step for wiring a `RenderTexture` onto a mesh for World Space UI | Not explicitly spelled out in the current World Space pages, which instead describe the PanelSettings World Space render mode plus a World Document Raycaster; treat the exact mesh-wiring mechanics as unconfirmed until read directly off the live page |
| `VectorImage` participation in the dynamic atlas | No fetched page confirms or denies whether vector images batch the same way raster textures do — do not assume parity |

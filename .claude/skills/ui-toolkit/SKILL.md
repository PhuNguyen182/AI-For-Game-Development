---
name: ui-toolkit
description: "UI Toolkit (UnityEngine.UIElements): UXML/UI Builder, UxmlElement, USS flexbox, RegisterCallback and Manipulators, runtime data binding, ListView, PanelSettings, Panel Renderer/UIDocument, CreateGUI. Use for UI Toolkit screens or Editor UI."
user-invocable: false
---

# Unity UI Toolkit

Not for: uGUI/Canvas (`ugui`), Odin inspectors and drawers (`odin-inspector`), Animator-driven UI (`unity-animation`), input devices and `.inputactions` (`unity-input-system`), the NUnit harness around a UI test (`unity-test-framework`), gameplay rules behind the UI (`csharp-engineer`; this layer displays and reacts, Core decides).
Docs: https://docs.unity3d.com/Manual/ (unversioned, read at Unity 6.5 / 6000.5; best-practice guide validated on 6.0; UI Test Framework `com.unity.ui.test-framework@1.0`). Defaults quoted in references were read at that version: re-check on the installed Editor.
If `unity:ui-uitk` disagrees on binding mode or Panel Renderer availability, this skill's version-pinned facts win.

| Reference | Read when |
|---|---|
| [choosing-ui-system.md](references/choosing-ui-system.md) | Deciding UI Toolkit vs uGUI vs IMGUI for a surface |
| [uxml-and-visual-tree.md](references/uxml-and-visual-tree.md) | Structuring a screen, UI Builder quirks, templates, or a custom `VisualElement` |
| [uss-styling-and-layout.md](references/uss-styling-and-layout.md) | Styling, or a layout does not behave like web CSS |
| [text-and-fonts.md](references/text-and-fonts.md) | TextField, rich text, or a font asset decision/migration |
| [events-and-manipulators.md](references/events-and-manipulators.md) | Wiring pointer/click/focus behavior, capture, or a Manipulator |
| [runtime-panels-and-input.md](references/runtime-panels-and-input.md) | Hosting at runtime: Panel Renderer vs `UIDocument`, `PanelSettings`, world space, `EventSystem` |
| [editor-ui-authoring.md](references/editor-ui-authoring.md) | Editor window, inspector, property drawer, or state lost on recompile |
| [data-binding.md](references/data-binding.md) | Syncing UI to gameplay state or `SerializedObject` |
| [rendering-and-performance.md](references/rendering-and-performance.md) | Draw calls up, animated UI drops frames, pooling |
| [testing-and-migration.md](references/testing-and-migration.md) | Writing a UI test, or porting a uGUI/IMGUI screen |

## Steps
1. **Confirm UI Toolkit fits the surface** — Unity still recommends uGUI for runtime game UI and UI Toolkit for Editor tooling ([choosing-ui-system.md](references/choosing-ui-system.md)). Flag it when the surface needs Animation Clip/Timeline or Inspector-wired `UnityEvent`s (neither exists here); uGUI fit → `ugui`.
2. **Ask when the Unity version or the uGUI-vs-UI-Toolkit choice is unstated** — both gate decisions (Panel Renderer availability); otherwise proceed on a flagged assumption.
3. **Author structure in UXML/UI Builder**, C#-only construction only for runtime-unknown content ([uxml-and-visual-tree.md](references/uxml-and-visual-tree.md)). Query/register in `OnUIReload`/`CreateGUI`, never `Awake`.
4. **Write a custom `UxmlElement` only when no built-in element or template fits** — it needs a default constructor.
5. **Style through USS classes (BEM names)**, not inline styles — inline always wins the override stack and costs memory per element ([uss-styling-and-layout.md](references/uss-styling-and-layout.md)). Check any CSS assumption against the USS subset: `flex-direction` defaults to `column`; no `!important`, `float`, `calc()`, sibling selectors.
6. **Use dynamic SDF font assets** — the default Advanced Text Generator does not support static/bitmap ones ([text-and-fonts.md](references/text-and-fonts.md)).
7. **Wire behavior with typed `RegisterCallback<T>` (named methods) and Manipulators** ([events-and-manipulators.md](references/events-and-manipulators.md)); unregister in the teardown path an `OnDisable` would use.
8. **Pick the host by installed Editor version** — Panel Renderer supersedes `UIDocument` only from Unity 6.5. Set `PanelSettings` Scale With Screen Size for a PC + mobile HUD ([runtime-panels-and-input.md](references/runtime-panels-and-input.md)).
9. **Add an `EventSystem` only when uGUI shares the scene** — a pure UI Toolkit scene has its own.
10. **Bind, never poll in `Update`** — runtime data binding for gameplay state with `BindingMode.ToTarget` (the default TwoWay lets the UI write back into state it must only read), `SerializedObject` binding for Editor data ([data-binding.md](references/data-binding.md)). A source that never raises `propertyChanged` never updates.
11. **Build Editor UI in `CreateGUI`/`CreateInspectorGUI`/`CreatePropertyGUI`**; persist state in `[SerializeField]`, not on a `VisualElement` ([editor-ui-authoring.md](references/editor-ui-authoring.md)).
12. **Keep batches intact** — budget the dynamic atlas, animate `translate`/`scale`/`rotate` not layout, unregister callbacks before pooling ([rendering-and-performance.md](references/rendering-and-performance.md)).
13. **Make the UI testable** (named elements, no hidden state on the tree); hand the test to `qa-automation-engineer`. Flag migration blockers (no anchor/pivot equivalent, IMGUI no-equivalent calls) before promising a 1:1 port ([testing-and-migration.md](references/testing-and-migration.md)).

## Never
- Leave a callback registered on an element returned to a pool.
- Call `.Bind()` twice on one element, or inside `CreateInspectorGUI`/`CreatePropertyGUI` (Unity binds implicitly).
- Add an `EventSystem` "just in case" to a pure UI Toolkit scene.
- Assume Panel Renderer exists below Unity 6.5.

## Output
```
## UI Toolkit — <screen/tool>
- System: UI Toolkit over uGUI/IMGUI — why
- Structure: UI Builder / hand-written UXML / C# — custom controls
- Styling: USS files, BEM classes, variables
- Events: callbacks/Manipulators, teardown confirmed
- Hosting (runtime): Panel Renderer / UIDocument — Editor version; Scale Mode; world space
- Binding: runtime / SerializedObject — source type, mode, update trigger
- Performance: atlas checked, transform-only animation, pooling
- Verified: <evidence, or "not run">
- Known limitations: <...>
```
On request only, add `Latent concerns` and `Future remediation`, each with its trigger.

## Example
- "Poll HP in `Update` and set the label, it's simpler than binding" → declined: a per-frame `ToString()` and label write is wasted work when HP is unchanged; used `INotifyBindablePropertyChanged` raising `propertyChanged` only on a real change.

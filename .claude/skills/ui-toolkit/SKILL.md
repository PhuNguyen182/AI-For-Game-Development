---
name: ui-toolkit
description: "UI Toolkit: UXML, USS, UxmlElement, ListView, PanelSettings, UIDocument, CreateGUI. Use for UI Toolkit or Editor UI."
user-invocable: false
---

# Unity UI Toolkit

- **Not for:** uGUI/Canvas (`ugui`).
- **Not for:** Odin inspectors and drawers (`odin-inspector`).
- **Not for:** Animator-driven UI (`unity-animation`).
- **Not for:** input devices and `.inputactions` (`unity-input-system`).
- **Not for:** the NUnit harness around a UI test (`unity-test-framework`).
- **Not for:** gameplay rules behind the UI (`csharp-engineer`; this layer displays and reacts, Core decides).
- **Docs:** https://docs.unity3d.com/Manual/ (`UnityEngine.UIElements`; unversioned, read at Unity 6.5 / 6000.5).
  - **Best-practice guide:** validated on 6.0.
  - **UI Test Framework:** `com.unity.ui.test-framework@1.0`.
  - **Defaults quoted in references:** read at Unity 6.5 / 6000.5; re-check on the installed Editor.
- **Conflict with `unity:ui-uitk`:** if it disagrees on binding mode or Panel Renderer availability, this skill's version-pinned facts win.

## References
- **[choosing-ui-system.md](references/choosing-ui-system.md):** Deciding UI Toolkit vs uGUI vs IMGUI for a surface.
- **[uxml-and-visual-tree.md](references/uxml-and-visual-tree.md):** Structuring a screen, UI Builder quirks, templates, or a custom `VisualElement`.
- **[uss-styling-and-layout.md](references/uss-styling-and-layout.md):** Styling, or a layout does not behave like web CSS.
- **[text-and-fonts.md](references/text-and-fonts.md):** TextField, rich text, or a font asset decision/migration.
- **[events-and-manipulators.md](references/events-and-manipulators.md):** Wiring pointer/click/focus behavior, capture, or a Manipulator.
- **[runtime-panels-and-input.md](references/runtime-panels-and-input.md):** Hosting at runtime: Panel Renderer vs `UIDocument`, `PanelSettings`, world space, `EventSystem`.
- **[editor-ui-authoring.md](references/editor-ui-authoring.md):** Editor window, inspector, property drawer, or state lost on recompile.
- **[data-binding.md](references/data-binding.md):** Syncing UI to gameplay state or `SerializedObject`.
- **[rendering-and-performance.md](references/rendering-and-performance.md):** Draw calls up, animated UI drops frames, pooling.
- **[testing-and-migration.md](references/testing-and-migration.md):** Writing a UI test, or porting a uGUI/IMGUI screen.

## Steps
1. **Confirm UI Toolkit fits the surface:** Unity still recommends uGUI for runtime game UI and UI Toolkit for Editor tooling ([choosing-ui-system.md](references/choosing-ui-system.md)).
   - **Flag it:** when the surface needs Animation Clip/Timeline or Inspector-wired `UnityEvent`s (neither exists here).
   - **uGUI fit:** `ugui`.
2. **Missing input:** the Unity version or the uGUI-vs-UI-Toolkit choice unstated — both gate decisions (Panel Renderer availability).
   - **Dispatched agent:** `Blocked` or `Needs-decision`.
   - **Main session:** `AskUserQuestion`.
   - **Otherwise:** proceed on a flagged assumption.
3. **Author structure in UXML/UI Builder:** C#-only construction only for runtime-unknown content ([uxml-and-visual-tree.md](references/uxml-and-visual-tree.md)).
   - **Query/register:** in `OnUIReload`/`CreateGUI`, never `Awake`.
4. **Write a custom `UxmlElement` only when no built-in element or template fits:** it needs a default constructor.
5. **Style through USS classes (BEM names):** not inline styles — inline always wins the override stack and costs memory per element ([uss-styling-and-layout.md](references/uss-styling-and-layout.md)).
   - **CSS assumptions:** check any against the USS subset.
   - **USS subset:** `flex-direction` defaults to `column`; no `!important`, `float`, `calc()`, sibling selectors.
6. **Use dynamic SDF font assets:** the default Advanced Text Generator does not support static/bitmap ones ([text-and-fonts.md](references/text-and-fonts.md)).
7. **Wire behavior with typed `RegisterCallback<T>` (named methods) and Manipulators:** per [events-and-manipulators.md](references/events-and-manipulators.md).
   - **Teardown:** unregister in the path an `OnDisable` would use.
8. **Pick the host by installed Editor version:** Panel Renderer supersedes `UIDocument` only from Unity 6.5.
   - **PC + mobile HUD:** set `PanelSettings` Scale With Screen Size ([runtime-panels-and-input.md](references/runtime-panels-and-input.md)).
9. **Add an `EventSystem` only when uGUI shares the scene:** a pure UI Toolkit scene has its own.
10. **Bind, never poll in `Update`:** per [data-binding.md](references/data-binding.md).
    - **Gameplay state:** runtime data binding with `BindingMode.ToTarget`; the default TwoWay lets the UI write back into state it must only read.
    - **Editor data:** `SerializedObject` binding.
    - **Source that never raises `propertyChanged`:** never updates.
11. **Build Editor UI in `CreateGUI`/`CreateInspectorGUI`/`CreatePropertyGUI`:** persist state in `[SerializeField]`, not on a `VisualElement` ([editor-ui-authoring.md](references/editor-ui-authoring.md)).
12. **Keep batches intact:** per [rendering-and-performance.md](references/rendering-and-performance.md).
    - **Dynamic atlas:** budget it.
    - **Animation:** animate `translate`/`scale`/`rotate`, not layout.
    - **Pooling:** unregister callbacks before pooling.
13. **Make the UI testable (named elements, no hidden state on the tree):** hand the test to `qa-automation-engineer`.
    - **Migration blockers:** flag them before promising a 1:1 port ([testing-and-migration.md](references/testing-and-migration.md)).
    - **Blocker examples:** no anchor/pivot equivalent, IMGUI no-equivalent calls.

## Never
- **Leave a callback registered:** on an element returned to a pool.
- **Call `.Bind()` twice on one element:** or inside `CreateInspectorGUI`/`CreatePropertyGUI` (Unity binds implicitly).
- **Add an `EventSystem` "just in case":** to a pure UI Toolkit scene.
- **Assume Panel Renderer exists:** below Unity 6.5.

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
```

## Example
- **"Poll HP in `Update` and set the label, it's simpler than binding":** declined.
  - **Why:** a per-frame `ToString()` and label write is wasted work when HP is unchanged.
  - **Did instead:** used `INotifyBindablePropertyChanged` raising `propertyChanged` only on a real change.

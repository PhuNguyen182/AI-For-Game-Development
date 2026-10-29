# Testing and migration

Sources: [Test UI](https://docs.unity3d.com/Manual/UIE-test-ui.html), [UI Test Framework 1.0](https://docs.unity3d.com/Packages/com.unity.ui.test-framework@1.0/manual/index.html), [First test](https://docs.unity3d.com/Packages/com.unity.ui.test-framework@1.0/manual/create-your-first-ui-test.html), [From uGUI](https://docs.unity3d.com/Manual/UIE-Transitioning-From-UGUI.html), [From IMGUI](https://docs.unity3d.com/Manual/UIE-IMGUI-migration.html).

## UI Test Framework
- Package `com.unity.ui.test-framework` (add via Package Manager; core UI Toolkit is built in). Simulates interaction and verifies UI Toolkit behavior.
- `EditorWindowUITestFixture<T>` is the base fixture for an `EditorWindow` of type `T`. In a test, `simulate.FrameUpdate()` advances a frame and `simulate.Click(button)` clicks.
- Plain NUnit `[Test]` + `Assert.That()` in the standard Test Runner.
- Assembly references: `UnityEngine.TestRunner`, `UnityEditor.TestRunner`, `Unity.UI.TestFramework.Editor`, `Unity.UI.TestFramework.Runtime`.
- This skill stops at making the UI testable; name every interactive element (`name` attribute) and keep structure stable. Screen-reader support and tests both find elements by identity, not layout. Test writing goes to `qa-automation-engineer`.

## From uGUI
- **Blocker**: "no direct equivalents for anchoring and pivots": anchor/pivot-based responsive screens must be re-laid-out in Flexbox ([uss-styling-and-layout.md](uss-styling-and-layout.md)).
- Root: `Canvas` (scene GameObject) → `UIDocument`/Panel Renderer + `PanelSettings` (virtual tree).
- Elements: `MonoBehaviour` GameObjects → `VisualElement` (no per-element GameObject). UXML is layout only, logic in C#; no Inspector drag-and-drop wiring.
- Mixing limits: no shared keyboard-only navigation across both, no embedding one system's elements inside the other.

## From IMGUI
- `OnGUI()` re-runs every frame; UI Toolkit is retained and event-driven. Remaps: `EditorWindow.OnGUI()` → `CreateGUI()`, `PropertyDrawer.OnGUI()` → `CreatePropertyGUI()`, `Editor.OnInspectorGUI()` → `CreateInspectorGUI()`.
- **No equivalent**: `BeginBuildTargetSelectionGrouping`/`End...`, `BeginToggleGroup`/`EndToggleGroup`, `DrawPreviewTexture`, `DrawTextureAlpha`, `DropdownButton` (use `DropdownField`), `InspectorTitlebar`, `IntPopup`, `LinkButton`, basic `Toolbar()`, `Window()` and related windowing calls. Flag before promising a port.
- Partial: `DrawTexture()` `alphaBlend`/`borderWidth`/`borderRadius` (and `alphaBlend = false`) have no `Image` equivalent.
- `IMGUIContainer` embeds legacy `OnGUI()` in a `VisualElement` tree; a `VisualElement` cannot nest inside an `IMGUIContainer`.

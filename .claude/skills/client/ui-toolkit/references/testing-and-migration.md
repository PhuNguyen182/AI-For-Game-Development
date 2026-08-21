# Testing & Migration — UI Test Framework, From uGUI, From IMGUI

Sources: [Test UI](https://docs.unity3d.com/Manual/UIE-test-ui.html), [UI Test Framework 1.0 manual](https://docs.unity3d.com/Packages/com.unity.ui.test-framework@1.0/manual/index.html), [Create your first UI test](https://docs.unity3d.com/Packages/com.unity.ui.test-framework@1.0/manual/create-your-first-ui-test.html), [Migration guides](https://docs.unity3d.com/Manual/UIE-migration-guides.html), [Transitioning from UGUI](https://docs.unity3d.com/Manual/UIE-Transitioning-From-UGUI.html), [Transitioning from IMGUI](https://docs.unity3d.com/Manual/UIE-IMGUI-migration.html), [Accessibility](https://docs.unity3d.com/Manual/accessibility/_index.html).
Covers: SKILL.md §4 — **"Test through the UI Test Framework package, and flag a documented migration blocker before promising a 1:1 port"**.

Verifying UI Toolkit behavior in `qa-automation-engineer`'s Test Runner, and
the specific gaps that make a uGUI or IMGUI port not a drop-in replacement.

## UI Test Framework (separate installable package)

| Subject | What it decides | Source |
|---|---|---|
| Package | `com.unity.ui.test-framework` — simulates interaction, manages UI state, and verifies UI Toolkit behavior; must be added via Package Manager, unlike core UI Toolkit itself | [UI Test Framework 1.0 manual](https://docs.unity3d.com/Packages/com.unity.ui.test-framework@1.0/manual/index.html) |
| `EditorWindowUITestFixture<T>` | Base fixture class for testing an `EditorWindow` of type `T` built with UI Toolkit | [Create your first UI test](https://docs.unity3d.com/Packages/com.unity.ui.test-framework@1.0/manual/create-your-first-ui-test.html) |
| `simulate` helper | `simulate.FrameUpdate()` advances a frame; `simulate.Click(button)` simulates a click, from inside a test method | [Create your first UI test](https://docs.unity3d.com/Packages/com.unity.ui.test-framework@1.0/manual/create-your-first-ui-test.html) |
| Runner integration | Plain NUnit `[Test]` methods with `Assert.That()`, run from the standard Unity Test Framework Test Runner — no special runner | [Create your first UI test](https://docs.unity3d.com/Packages/com.unity.ui.test-framework@1.0/manual/create-your-first-ui-test.html) |
| Assembly references needed | `UnityEngine.TestRunner`, `UnityEditor.TestRunner`, `Unity.UI.TestFramework.Editor`, `Unity.UI.TestFramework.Runtime` | [Create your first UI test](https://docs.unity3d.com/Packages/com.unity.ui.test-framework@1.0/manual/create-your-first-ui-test.html) |

Hand the actual test-writing to `qa-automation-engineer` once the UI is
built — this skill's job stops at making the UI testable (named elements,
no hidden state on the `VisualElement` itself).

## Migrating from uGUI

| Subject | What it decides | Source |
|---|---|---|
| **Blocker: anchors and pivots** | "UI Toolkit has no direct equivalents for anchoring and pivots of UI elements, due to the fundamental layout differences compared to uGUI" — a UGUI screen built around anchor/pivot-based responsive positioning has no 1:1 translation; it must be re-laid-out in Flexbox terms, per [uss-styling-and-layout.md](uss-styling-and-layout.md) | [Transitioning from UGUI](https://docs.unity3d.com/Manual/UIE-Transitioning-From-UGUI.html) |
| Root component | uGUI: `Canvas` (a scene GameObject). UI Toolkit: `UIDocument`/Panel Renderer plus `PanelSettings` — the actual tree is virtual, not scene-editable | [Transitioning from UGUI](https://docs.unity3d.com/Manual/UIE-Transitioning-From-UGUI.html) |
| Element base type | uGUI elements are `MonoBehaviour` GameObjects; UI Toolkit elements are `VisualElement`, with no per-element GameObject overhead | [Transitioning from UGUI](https://docs.unity3d.com/Manual/UIE-Transitioning-From-UGUI.html) |
| Authoring split | uGUI prefabs bundle visuals and logic; UI Toolkit's UXML is layout-only, with logic in separate C# querying/registering against it — no Inspector drag-and-drop wiring | [Transitioning from UGUI](https://docs.unity3d.com/Manual/UIE-Transitioning-From-UGUI.html) |
| Mixed-system limits | The two systems cannot be freely interleaved: no shared keyboard-only navigation across both, no embedding one system's elements inside the other | [Transitioning from UGUI](https://docs.unity3d.com/Manual/UIE-Transitioning-From-UGUI.html) |

## Migrating from IMGUI

| Subject | What it decides | Source |
|---|---|---|
| Execution model | IMGUI re-runs `OnGUI()` at least once per frame with no persistent tree state; UI Toolkit is event-driven and retained — behavior attaches via callbacks, not re-declaration | [Transitioning from IMGUI](https://docs.unity3d.com/Manual/UIE-IMGUI-migration.html) |
| **Explicit no-equivalent list** | `BeginBuildTargetSelectionGrouping()`/`EndBuildTargetSelectionGrouping()`, `BeginToggleGroup()`/`EndToggleGroup()`, `DrawPreviewTexture()`, `DrawTextureAlpha()`, `DropdownButton()` (use `DropdownField`), `InspectorTitlebar()`, `IntPopup()`, `LinkButton()`, basic `Toolbar()`, `Window()` and related windowing calls — flag any of these before promising a port | [Transitioning from IMGUI](https://docs.unity3d.com/Manual/UIE-IMGUI-migration.html) |
| Partial gaps | `DrawTexture()`'s `alphaBlend`/`borderWidth`/`borderRadius` parameters, and a `false` `alphaBlend`, have no `Image` element equivalent | [Transitioning from IMGUI](https://docs.unity3d.com/Manual/UIE-IMGUI-migration.html) |
| Standard entry-point remaps | `EditorWindow.OnGUI()` → `CreateGUI()`; `PropertyDrawer.OnGUI()` → `CreatePropertyGUI()`; `Editor.OnInspectorGUI()` → `CreateInspectorGUI()`, per [editor-ui-authoring.md](editor-ui-authoring.md) | [Transitioning from IMGUI](https://docs.unity3d.com/Manual/UIE-IMGUI-migration.html) |
| Coexistence | `IMGUIContainer` embeds legacy `OnGUI()` code inside a `VisualElement` tree; a `VisualElement` cannot be nested **inside** an `IMGUIContainer` | [Transitioning from IMGUI](https://docs.unity3d.com/Manual/UIE-IMGUI-migration.html) |

## Accessibility (overview only)

| Subject | What it decides | Source |
|---|---|---|
| Scope | Screen-reader support and an Accessibility module for building inclusive UI; sample project `LetterSpell` demonstrates it | [Accessibility](https://docs.unity3d.com/Manual/accessibility/_index.html) |

**Critical caveat**: name every interactive element (`name` attribute or a
`UxmlElement` tag) and give it a stable, queryable structure — screen-reader
support and the UI Test Framework both depend on being able to find and
identify elements after the fact, not on visual layout alone.

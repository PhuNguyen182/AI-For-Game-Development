# UXML & Visual Tree — Structure, UI Builder, Custom Controls

Sources: [Structure UI](https://docs.unity3d.com/Manual/UIE-structure-ui.html), [Get started with UI Toolkit](https://docs.unity3d.com/Manual/UIE-simple-ui-toolkit-workflow.html), [UI Builder](https://docs.unity3d.com/Manual/UIBuilder.html), [UI Builder interface overview](https://docs.unity3d.com/Manual/UIB-interface-overview.html), [Structuring UI using the Hierarchy](https://docs.unity3d.com/Manual/UIB-structuring-ui-elements.html), [Structuring UI using templates](https://docs.unity3d.com/Manual/UIB-structuring-ui-templates.html), [Visual tree](https://docs.unity3d.com/Manual/UIE-VisualTree.html), [Panels](https://docs.unity3d.com/Manual/UIE-panels.html), [UQuery](https://docs.unity3d.com/Manual/UIE-UQuery.html), [Encapsulate UXML with logic](https://docs.unity3d.com/Manual/UIE-encapsulate-uxml-with-logic.html), [Custom control UXML tag names](https://docs.unity3d.com/Manual/ui-systems/custom-control-customize-uxml-tag-names.html), [Built-in elements reference](https://docs.unity3d.com/Manual/UIE-ElementRef.html).
Covers: SKILL.md §4 — **"Author structure in UXML and UI Builder, not ad-hoc C#-only construction"**, **"Write a custom `UxmlElement` only once no built-in element or template fits"**.

The authoring surface for what exists in a screen: the visual tree model, the
three ways to populate it, UI Builder's panes, and how to package a reusable
piece as a template or a custom control. Styling lives next door in
[uss-styling-and-layout.md](uss-styling-and-layout.md); hosting the tree at
runtime is [runtime-panels-and-input.md](runtime-panels-and-input.md).

## Table of contents
- [Visual tree fundamentals](#visual-tree-fundamentals)
- [Three ways to populate a tree](#three-ways-to-populate-a-tree)
- [UI Builder panes](#ui-builder-panes)
- [Templates](#templates)
- [Custom controls](#custom-controls)
- [Built-in elements](#built-in-elements)

## Visual tree fundamentals

| Subject | What it decides | Source |
|---|---|---|
| UXML | "Unity Extensible Markup Language" — the XML dialect that declares a visual tree's structure | [Structure UI](https://docs.unity3d.com/Manual/UIE-structure-ui.html) |
| `VisualElement` | Base class for every node in the tree; carries style, layout, and event-handler state | [Visual tree](https://docs.unity3d.com/Manual/UIE-VisualTree.html) |
| Root access | Editor UI: `EditorWindow.rootVisualElement`. Runtime UI: `UIDocument.rootVisualElement` (or the Panel Renderer equivalent) — two different entry points for the same tree model | [Visual tree](https://docs.unity3d.com/Manual/UIE-VisualTree.html) |
| Panel | The parent object of a visual tree; owns focus control and event dispatching but is **not itself a visual element**. Each panel belongs to exactly one Editor Window or one runtime host | [Panels](https://docs.unity3d.com/Manual/UIE-panels.html) |
| Detecting disconnection | `VisualElement.panel` is `null` whenever that element is not currently attached to a live tree | [Panels](https://docs.unity3d.com/Manual/UIE-panels.html) |
| `UQuery` | `root.Q<T>("name")` finds a descendant by type/name, including read-only shadow-tree children of built-in controls | [UQuery](https://docs.unity3d.com/Manual/UIE-UQuery.html) |

## Three ways to populate a tree

| Path | Mechanism | Use when | Source |
|---|---|---|---|
| UI Builder | Visually edit the `.uxml` (and its `.uss`) in the Builder window | The default — per the advanced-developer guide in [choosing-ui-system.md](choosing-ui-system.md) | [Get started with UI Toolkit](https://docs.unity3d.com/Manual/UIE-simple-ui-toolkit-workflow.html) |
| Hand-written UXML | Author the `.uxml` text directly, load with `AssetDatabase.LoadAssetAtPath<VisualTreeAsset>()` or `Resources.Load` | The structure is fixed but easier to hand-edit as text/diff in review | [Get started with UI Toolkit](https://docs.unity3d.com/Manual/UIE-simple-ui-toolkit-workflow.html) |
| Pure C# | Instantiate controls in `CreateGUI()`/`OnUIReload` and call `rootVisualElement.Add(...)` | Content is genuinely dynamic and not known until runtime | [Get started with UI Toolkit](https://docs.unity3d.com/Manual/UIE-simple-ui-toolkit-workflow.html) |

```csharp
// C#-only construction — the third path, reserved for genuinely dynamic content.
var button = new Button(() => Attack()) { text = "Attack" };
rootVisualElement.Add(button);
```

**Critical caveat**: for **runtime** UI, query and register logic must run
inside the `OnUIReload` callback registered via
`PanelRenderer.RegisterUIReloadCallback()` (unregister in `OnDestroy`) — not
`Awake`/`Start` — because the visual tree is not guaranteed loaded at those
points. Editor windows use the equivalent `CreateGUI()` hook instead; see
[editor-ui-authoring.md](editor-ui-authoring.md).

## UI Builder panes

| Pane | What it does | Source |
|---|---|---|
| Hierarchy | Tree view of the document; elements display by `name`, falling back to their C# type — names are for identification only, **not enforced unique** | [UI Builder interface overview](https://docs.unity3d.com/Manual/UIB-interface-overview.html) |
| StyleSheets | Add/reorder/remove attached USS files and create/reorder selectors inside them | [UI Builder interface overview](https://docs.unity3d.com/Manual/UIB-interface-overview.html) |
| Library | **Standard** tab (built-in controls) and **Project** tab (custom `.uxml`/`VisualElement` subclasses) | [UI Builder interface overview](https://docs.unity3d.com/Manual/UIB-interface-overview.html) |
| Viewport / Canvas | Live preview with its own zoom/pan and a **Match Game View** toggle; header shows `*` for unsaved changes | [UI Builder interface overview](https://docs.unity3d.com/Manual/UIB-interface-overview.html) |
| Inspector | Contextual: Attributes/StyleSheets/Inlined Styles for an element, Style Selector/Styles for a selector, Canvas Size/Background for the Canvas itself | [UI Builder interface overview](https://docs.unity3d.com/Manual/UIB-interface-overview.html) |

**Critical caveat**: saving inside UI Builder requires **Ctrl/Cmd+S with the
document focused** — a project-wide save elsewhere does not save the open
UXML. Newly created colors also default to **Alpha 0** (fully transparent);
raise it explicitly. `editor-extension-mode` on the root UXML defaults to
`False`, hiding Editor-only controls in the Library until toggled on.

| Subject | What it decides | Source |
|---|---|---|
| Cascading edits | Delete/copy/duplicate on a Hierarchy element applies to its whole subtree | [Structuring UI using the Hierarchy](https://docs.unity3d.com/Manual/UIB-structuring-ui-elements.html) |
| Copy/paste | Copying an element copies its UXML text representation — pastable into any text editor | [Structuring UI using the Hierarchy](https://docs.unity3d.com/Manual/UIB-structuring-ui-elements.html) |
| Canvas text editing | Only the `text` attribute is editable by double-click on the Canvas; every other attribute needs the Inspector | [Structuring UI using the Hierarchy](https://docs.unity3d.com/Manual/UIB-structuring-ui-elements.html) |
| Preview mode | Orange Viewport border; exercises real Foldout/ScrollView/hover behavior, but **Canvas picking and manipulators are disabled** while active | [Test UI in the UI Builder](https://docs.unity3d.com/Manual/UIB-testing-ui.html) |
| Matching Selectors panel | Inspector debug view listing every selector affecting the selected element; **selectors lower in the list win ties** — the authoritative way to debug specificity | [Test UI in the UI Builder](https://docs.unity3d.com/Manual/UIB-testing-ui.html) |

## Templates

| Subject | What it decides | Source |
|---|---|---|
| `TemplateContainer` | Instancing an existing `.uxml` inside another document creates this node — conceptually a Prefab instance | [Structuring UI using templates](https://docs.unity3d.com/Manual/UIB-structuring-ui-templates.html) |
| Editing modes | **Open Instance in Isolation** (template editable, parent styles read-only) vs **Open Instance in Context** (template editable, parent dimmed) | [Structuring UI using templates](https://docs.unity3d.com/Manual/UIB-structuring-ui-templates.html) |
| Unpacking | **Unpack Instance** converts one instance back to a normal document; **Unpack Instance Completely** does so recursively | [Structuring UI using templates](https://docs.unity3d.com/Manual/UIB-structuring-ui-templates.html) |
| Style boundary | Parent and sub-document styles do **not** cross the `TemplateContainer` boundary by default | [Structuring UI using templates](https://docs.unity3d.com/Manual/UIB-structuring-ui-templates.html) |

## Custom controls

| Subject | What it decides | Source |
|---|---|---|
| Default constructor | Custom `VisualElement` subclasses require a default constructor for UXML/UI Builder instantiation | [Encapsulate UXML with logic](https://docs.unity3d.com/Manual/UIE-encapsulate-uxml-with-logic.html) |
| UXML-first pattern | Children declared in the control's own UXML, wired via an `Init()` after construction — simpler, fixed structure, navigable in UI Builder both ways | [Encapsulate UXML with logic](https://docs.unity3d.com/Manual/UIE-encapsulate-uxml-with-logic.html) |
| Element-first pattern | Children built at runtime via `VisualTreeAsset.CloneTree()` in the constructor — more flexible, but UI Builder **cannot** navigate parent↔child for this pattern | [Encapsulate UXML with logic](https://docs.unity3d.com/Manual/UIE-encapsulate-uxml-with-logic.html) |
| `[UxmlElement]` | Current (Unity 6) attribute controlling a custom control's UXML tag name/visibility, replacing the older `UxmlFactory`/`UxmlTraits` boilerplate | [Custom control UXML tag names](https://docs.unity3d.com/Manual/ui-systems/custom-control-customize-uxml-tag-names.html) |
| Migrating older controls | A dedicated migration guide covers moving a `UxmlFactory`/`UxmlTraits` control to `[UxmlElement]`/`[UxmlAttribute]` | [Migrate a custom control](https://docs.unity3d.com/Manual/ui-systems/migrate-custom-control.html) |

## Built-in elements

| Subject | What it decides | Source |
|---|---|---|
| Full catalog | 80+ elements grouped as Input Fields, Selection Controls, Container/Layout (`Box`, `GroupBox`, `ScrollView`, `TwoPaneSplitView`, `TabView`), Display (`Label`, `Image`, `ProgressBar`, `HelpBox`), Data Visualization (`ListView`, `TreeView`, `MultiColumnListView`/`TreeView`), and Editor-only fields | [Built-in elements reference](https://docs.unity3d.com/Manual/UIE-ElementRef.html) |
| `Button` icon | UXML attribute `icon-image` sets a Texture/Sprite/VectorImage icon; icon position is controlled through USS `flex-direction`, not a dedicated attribute | [Button element](https://docs.unity3d.com/Manual/UIE-uxml-element-Button.html) |
| Value-changed events | Controls exposing `value` use `RegisterValueChangedCallback(evt => ...)`, not a generic click/mouse event | [Controls](https://docs.unity3d.com/Manual/UIE-Controls.html) |
| `TwoPaneSplitView` | Requires **exactly two** child elements | [How to create an Editor window](https://docs.unity3d.com/Manual/UIE-HowTo-CreateEditorWindow.html) |

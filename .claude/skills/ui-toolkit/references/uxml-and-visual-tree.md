# UXML and visual tree

Sources: [Structure UI](https://docs.unity3d.com/Manual/UIE-structure-ui.html), [Workflow](https://docs.unity3d.com/Manual/UIE-simple-ui-toolkit-workflow.html), [Builder overview](https://docs.unity3d.com/Manual/UIB-interface-overview.html), [Builder templates](https://docs.unity3d.com/Manual/UIB-structuring-ui-templates.html), [Builder testing](https://docs.unity3d.com/Manual/UIB-testing-ui.html), [Panels](https://docs.unity3d.com/Manual/UIE-panels.html), [Encapsulate](https://docs.unity3d.com/Manual/UIE-encapsulate-uxml-with-logic.html), [Tag names](https://docs.unity3d.com/Manual/ui-systems/custom-control-customize-uxml-tag-names.html), [Elements](https://docs.unity3d.com/Manual/UIE-ElementRef.html).

## Tree
- Root: `EditorWindow.rootVisualElement` (Editor) or `UIDocument.rootVisualElement` / Panel Renderer equivalent (runtime).
- A panel owns focus and event dispatch, is not a visual element, and belongs to one Editor window or runtime host.
- `VisualElement.panel` is `null` when the element is not attached to a live tree.
- `root.Q<T>("name")` (UQuery) also finds read-only shadow-tree children of built-in controls.

## Populating a tree
| Path | Use when |
|---|---|
| UI Builder | Default |
| Hand-written UXML (`AssetDatabase.LoadAssetAtPath<VisualTreeAsset>` / `Resources.Load`) | Structure fixed and easier to review as text |
| Pure C# (`rootVisualElement.Add(...)`) | Content unknown until runtime |

Runtime: query and register inside the `OnUIReload` callback (`PanelRenderer.RegisterUIReloadCallback()`, unregister in `OnDestroy`), not `Awake`/`Start`: the tree may not be loaded. Editor windows use `CreateGUI()` ([editor-ui-authoring.md](editor-ui-authoring.md)).

## UI Builder gotchas
- Save with Ctrl/Cmd+S with the document focused; a project-wide save does not save the open UXML.
- New colors default to Alpha 0 (transparent).
- Root `editor-extension-mode` defaults to `False`, hiding Editor-only controls in the Library.
- Hierarchy names are not enforced unique.
- Delete/copy/duplicate on an element applies to its subtree; copy yields UXML text.
- Canvas double-click edits only `text`.
- Preview mode (orange border) runs real Foldout/ScrollView/hover but disables Canvas picking and manipulators.
- Inspector "Matching Selectors" lists every selector affecting an element; lower in the list wins ties (use it to debug specificity).

## Templates
- Instancing a `.uxml` inside another creates a `TemplateContainer` (Prefab-like). Open Instance in Isolation (parent styles read-only) vs in Context (parent dimmed). Unpack Instance / Unpack Instance Completely (recursive).
- Parent and sub-document styles do not cross the `TemplateContainer` boundary by default.

## Custom controls
- Subclass needs a default constructor for UXML/UI Builder.
- UXML-first (children in the control's own UXML, wired in `Init()`): fixed structure, navigable in UI Builder both ways.
- Element-first (`VisualTreeAsset.CloneTree()` in the constructor): flexible, but UI Builder cannot navigate parent↔child.
- `[UxmlElement]` / `[UxmlAttribute]` (Unity 6) replace `UxmlFactory`/`UxmlTraits`; see the [migration guide](https://docs.unity3d.com/Manual/ui-systems/migrate-custom-control.html).

## Built-ins
- 80+ elements: inputs, `Box`/`GroupBox`/`ScrollView`/`TwoPaneSplitView`/`TabView`, `Label`/`Image`/`ProgressBar`/`HelpBox`, `ListView`/`TreeView`/`MultiColumn*`.
- `TwoPaneSplitView` needs exactly two children.
- `Button` `icon-image` sets the icon; position it with USS `flex-direction`.
- Controls with `value` use `RegisterValueChangedCallback`, not click/mouse events.

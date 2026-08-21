# Editor UI Authoring — CreateGUI, Custom Inspectors, PropertyDrawers, ViewData

Sources: [Support for Editor UI](https://docs.unity3d.com/Manual/UIE-support-for-editor-ui.html), [How to create an Editor window](https://docs.unity3d.com/Manual/UIE-HowTo-CreateEditorWindow.html), [How to create a custom inspector](https://docs.unity3d.com/Manual/UIE-HowTo-CreateCustomInspector.html), [Create a default inspector](https://docs.unity3d.com/Manual/ui-systems/create-default-inspector.html), [ViewData](https://docs.unity3d.com/Manual/UIE-ViewData.html).
Covers: SKILL.md §4 — **"Build Editor tooling through `CreateGUI`/`CreateInspectorGUI`/`CreatePropertyGUI`, and persist state in `[SerializeField]`, not on the `VisualElement`"**.

Editor-only UI Toolkit entry points and their state-persistence rules.
`SerializedObject` binding used from these entry points is covered in
[data-binding.md](data-binding.md); this file owns the entry points and
`ViewData` themselves.

## Entry points

| Entry point | Replaces | Fires | Source |
|---|---|---|---|
| `EditorWindow.CreateGUI()` | `OnGUI()` (IMGUI) | Automatically whenever the window needs to display — after `OnEnable()` on first open, and again after every domain reload | [How to create an Editor window](https://docs.unity3d.com/Manual/UIE-HowTo-CreateEditorWindow.html) |
| `Editor.CreateInspectorGUI()` | `OnInspectorGUI()` | Once, to build the custom Inspector's visual tree; Unity performs an **implicit bind** right after it returns | [How to create a custom inspector](https://docs.unity3d.com/Manual/UIE-HowTo-CreateCustomInspector.html) |
| `PropertyDrawer.CreatePropertyGUI()` | `OnGUI()` (drawer) | Same role as `CreateInspectorGUI()`, but for any `[Serializable]` type used as a field, not just `MonoBehaviour`/`ScriptableObject` | [How to create a custom inspector](https://docs.unity3d.com/Manual/UIE-HowTo-CreateCustomInspector.html) |

```csharp
// EditorWindow — must live in an Editor folder or editor-only assembly.
public class AbilityEditorWindow : EditorWindow
{
    [SerializeField] private string _lastSearchText; // Survives domain reload; a raw VisualElement field would not.

    public void CreateGUI()
    {
        var searchField = new ToolbarSearchField { value = _lastSearchText };
        searchField.RegisterValueChangedCallback(evt => _lastSearchText = evt.newValue);
        this.rootVisualElement.Add(searchField);
    }
}
```

**Critical caveat**: `VisualElement` instances are **not serializable**.
Anything that must survive a domain reload or recompilation belongs in a
`[SerializeField]` field on the `EditorWindow`/`Editor`, re-applied inside
`CreateGUI()` — not stored on the visual tree itself. Custom
Inspector/PropertyDrawer scripts must live in an Editor folder or
editor-only assembly; `UnityEditor` types are inaccessible outside that
context and break standalone player builds if referenced from runtime code.

| Subject | What it decides | Source |
|---|---|---|
| Attributes | `[CustomEditor(typeof(YourClass))]` on the Inspector class; `[CustomPropertyDrawer(typeof(YourClass))]` on the drawer | [How to create a custom inspector](https://docs.unity3d.com/Manual/UIE-HowTo-CreateCustomInspector.html) |
| Don't call `Bind()` yourself | Unity already binds implicitly right after `CreateInspectorGUI()`/`CreatePropertyGUI()` return — a manual call is redundant, per [data-binding.md](data-binding.md) | [How to create a custom inspector](https://docs.unity3d.com/Manual/UIE-HowTo-CreateCustomInspector.html) |
| `InspectorElement.FillDefaultInspector(container, serializedObject, editor)` | Reproduces the standard default-Inspector field layout inside a custom `CreateInspectorGUI()` (e.g. nested in a Foldout), without hand-building every field | [Create a default inspector](https://docs.unity3d.com/Manual/ui-systems/create-default-inspector.html) |

## ViewData — Editor-only UI state persistence

| Subject | What it decides | Source |
|---|---|---|
| `viewDataKey` | Must be **unique within the Editor window**; enables persistence for `ScrollView` scroll position, `ListView`/`TreeView` selection, `Foldout` expanded state, `MultiColumnListView`/`TreeView` column order/width/sort, `TabView` selected tab | [ViewData](https://docs.unity3d.com/Manual/UIE-ViewData.html) |
| Scope | Works **only in Editor UI** — it does not apply to runtime panels. Persists across domain reloads, Play Mode entry, and Editor restarts | [ViewData](https://docs.unity3d.com/Manual/UIE-ViewData.html) |
| Custom controls | The API to add ViewData support to a *custom* control is currently internal — you cannot hook an arbitrary custom control into it yet | [ViewData](https://docs.unity3d.com/Manual/UIE-ViewData.html) |

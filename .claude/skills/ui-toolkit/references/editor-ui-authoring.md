# Editor UI authoring

Sources: [Editor UI](https://docs.unity3d.com/Manual/UIE-support-for-editor-ui.html), [Editor window](https://docs.unity3d.com/Manual/UIE-HowTo-CreateEditorWindow.html), [Custom inspector](https://docs.unity3d.com/Manual/UIE-HowTo-CreateCustomInspector.html), [Default inspector](https://docs.unity3d.com/Manual/ui-systems/create-default-inspector.html), [ViewData](https://docs.unity3d.com/Manual/UIE-ViewData.html).

## Entry points
| Entry point | Replaces | Behavior |
|---|---|---|
| `EditorWindow.CreateGUI()` | `OnGUI()` | Runs when the window displays: after `OnEnable()` on first open and after every domain reload |
| `Editor.CreateInspectorGUI()` | `OnInspectorGUI()` | Builds the tree once; Unity binds implicitly right after it returns |
| `PropertyDrawer.CreatePropertyGUI()` | drawer `OnGUI()` | Same, for any `[Serializable]` field type |

- Attributes: `[CustomEditor(typeof(X))]`, `[CustomPropertyDrawer(typeof(X))]`.
- Do not call `Bind()` in the last two ([data-binding.md](data-binding.md)).
- `InspectorElement.FillDefaultInspector(container, serializedObject, editor)` reproduces the default field layout inside a custom inspector (e.g. in a Foldout).
- Editor classes must live in an Editor folder or editor-only assembly; `UnityEditor` references from runtime code break player builds.

`VisualElement`s are not serializable: state that must survive domain reload or recompile goes in `[SerializeField]` on the window/`Editor` and is re-applied in `CreateGUI()`.

```csharp
public class AbilityEditorWindow : EditorWindow
{
    [SerializeField] private string _lastSearchText; // survives reload

    public void CreateGUI()
    {
        var search = new ToolbarSearchField { value = _lastSearchText };
        search.RegisterValueChangedCallback(e => _lastSearchText = e.newValue);
        rootVisualElement.Add(search);
    }
}
```

## ViewData (Editor UI only)
- Set a `viewDataKey` unique within the window to persist `ScrollView` position, `ListView`/`TreeView` selection, `Foldout` state, `MultiColumn*` column order/width/sort, `TabView` tab. Survives domain reload, Play Mode and Editor restart.
- Not available in runtime panels; the API to add it to a custom control is internal.

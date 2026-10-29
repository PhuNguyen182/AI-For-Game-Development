# Editor Extensibility

Escalation only: use after the attribute references fail to cover the requirement. These classes live in the Editor-only `Sirenix.OdinInspector.Editor` assembly: put code under an `Editor/` folder or inside `#if UNITY_EDITOR`.

## Editor and window
- `OdinEditor : Editor`: drop-in for `Editor`. Override `OnInspectorGUI()` only to add content around the default; `this.DrawTree()`/`DrawDefaultInspector()` give Odin's rendering, `DrawUnityInspector()` Unity's. `Tree` = backing `PropertyTree`.
- `OdinEditorWindow : EditorWindow`: inspects a plain C# object. Members: `GetTarget()`/`GetTargets()`, `DrawEditors()`, `DrawEditorPreview(int, float)`, `EnableAutomaticHeightAdjustment(int maxHeight, bool retainInitialWindowPosition)`, static `InspectObject(Object)`, `InspectObjectInDropDown(Object, Rect, ...)`.
- `OdinMenuEditorWindow`: side menu tree. Override `BuildMenuTree()` returning an `OdinMenuTree`; `tree.Add(path, instance)`, `/` in the path nests groups.

```csharp
public class MyEditorWindow : OdinEditorWindow
{
    [MenuItem("Tools/My Window")]
    private static void OpenWindow() => GetWindow<MyEditorWindow>().Show();
    [Button] public void SomeButton() { }
    public SomeType[] someTableData;
}
// Non-UnityEngine.Object target: protected override object GetTarget() => MySingleton.Instance;
```

## Property system
Every Odin Inspector is backed by one `PropertyTree` (static `Create(...)` from an object, `SerializedObject` or target list; `RootProperty`, `Draw()`, `BeginDraw(bool withUndo)`). Needed only when a window manages its own tree.
`InspectorProperty` is one node (`this.Property` in a drawer): `Children`, `Parent`, `ValueEntry` (`SmartValue` when typed), `Attributes`, `GetAttribute<T>()`, `FindParent`/`FindChild`, `Tree`.

## Custom drawers
Derive from one of the bases below, never `OdinDrawer` directly. Shared: `this.Property`, `CanDrawProperty(InspectorProperty)`/`CanDrawTypeFilter(Type)`, `CallNextDrawer(GUIContent label)`. `DrawerPriorityAttribute` orders drawers (higher first); a drawer that never calls `CallNextDrawer` blocks every lower-priority drawer.

| Base | Use when |
|---|---|
| `OdinValueDrawer<T>` | Type-driven: every `T` draws this way whatever the attribute |
| `OdinAttributeDrawer<TAttribute>` | Attribute-driven, any value type |
| `OdinAttributeDrawer<TAttribute, TValue>` | Attribute-driven, one value type |
| `OdinGroupDrawer<TGroupAttribute>` | A new grouping layout (as `BoxGroup`/`TabGroup`) |

```csharp
public sealed class GUITintColorAttributeDrawer : OdinAttributeDrawer<GUITintColorAttribute>
{
    protected override void DrawPropertyLayout(GUIContent label)
    {
        Color prev = GUI.color;
        GUI.color *= this.Attribute.Color;
        this.CallNextDrawer(label);
        GUI.color = prev;
    }
}
```

`label` is `null` whenever the label is suppressed (`[HideLabel]`, inside a list): handle `null` in every `DrawPropertyLayout` or it throws.

## OdinAttributeProcessor
`OdinAttributeProcessor<TValue>` (or non-generic) adds, changes or removes attributes on a type you do not own. Override `ProcessSelfAttributes(InspectorProperty, List<Attribute>)` and/or `ProcessChildMemberAttributes(InspectorProperty parentProperty, MemberInfo member, List<Attribute> attributes)`; gate with `CanProcessSelfAttributes`/`CanProcessChildMemberAttributes`.

## Self-validation
Implement `ISelfValidator` on the type and fill the `SelfValidationResult` parameter in `Validate` (`Add(...)` or severity helpers); Odin's `SelfValidator<T>` picks it up. Inspector-only, like `ValidateInput`. Project-wide validators (`Validator<T>`, `RegisterValidatorAttribute`, `GlobalValidator`): see SKILL.md step 7.

## ValueResolver
To resolve a resolved-string in custom code: `ValueResolver<TResult>.Get<TResult>(InspectorProperty property, string resolvedString)`, then `.GetValue(int selectionIndex = 0)`. Surface failures with `ValueResolver.DrawErrors`/`GetCombinedErrors` instead of assuming success.

## GUI helpers
`SirenixEditorGUI` (namespace `Sirenix.Utilities.Editor`): `BeginBox`/`EndBox`, `BeginBoxHeader`/`EndBoxHeader`, `BeginToolbarBox`, `MessageBox`/`InfoMessageBox`/`ErrorMessageBox`, `Title`, `IconButton`, `Foldout`, `DrawSolidRect`. `EditorIcons` holds the built-in icons (e.g. `EditorIcons.Plus`).

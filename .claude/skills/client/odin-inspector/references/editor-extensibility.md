# Editor Extensibility — Sirenix.OdinInspector.Editor custom editors, windows & drawers

Sources: [OdinEditor](https://odininspector.com/documentation/sirenix.odininspector.editor.odineditor), [OdinEditorWindow](https://odininspector.com/documentation/sirenix.odininspector.editor.odineditorwindow), [OdinMenuEditorWindow](https://odininspector.com/documentation/sirenix.odininspector.editor.odinmenueditorwindow), [OdinMenuTree](https://odininspector.com/documentation/sirenix.odininspector.editor.odinmenutree), [PropertyTree](https://odininspector.com/documentation/sirenix.odininspector.editor.propertytree), [InspectorProperty](https://odininspector.com/documentation/sirenix.odininspector.editor.inspectorproperty), [OdinDrawer](https://odininspector.com/documentation/sirenix.odininspector.editor.odindrawer), [OdinValueDrawer\<T\>](https://odininspector.com/documentation/sirenix.odininspector.editor.odinvaluedrawer-1), [OdinAttributeDrawer\<TAttribute\>](https://odininspector.com/documentation/sirenix.odininspector.editor.odinattributedrawer-1), [OdinAttributeProcessor](https://odininspector.com/documentation/sirenix.odininspector.editor.odinattributeprocessor), [SelfValidator\<T\>](https://odininspector.com/documentation/sirenix.odininspector.editor.validation.selfvalidator-1), [ValidationResult](https://odininspector.com/documentation/sirenix.odininspector.editor.validation.validationresult), [ValueResolver\<TResult\>](https://odininspector.com/documentation/sirenix.odininspector.editor.valueresolvers.valueresolver-1), [SirenixEditorGUI](https://odininspector.com/documentation/sirenix.utilities.editor.sirenixeditorgui).
Covers: SKILL.md §4 — **"Default to composing built-in attributes; escalate to a custom drawer only once no attribute combination covers the requirement"**, **"When writing a custom drawer, pick the narrowest base class the requirement needs"**.

This is escalation territory: reach for anything in this file only once the
five attribute reference files ([attributes-layout-display.md](attributes-layout-display.md),
[attributes-conditional-validation.md](attributes-conditional-validation.md),
[attributes-selection-references.md](attributes-selection-references.md),
[attributes-collections-tables.md](attributes-collections-tables.md),
[attributes-buttons-misc.md](attributes-buttons-misc.md)) genuinely don't
cover the requirement. All classes here live in the Editor-only
`Sirenix.OdinInspector.Editor` assembly — code using them must be inside a
`#if UNITY_EDITOR` block or an `Editor/` folder.

## Table of contents
- [Custom Editor and EditorWindow](#custom-editor-and-editorwindow)
- [Menu-based editor windows](#menu-based-editor-windows)
- [The property system: PropertyTree and InspectorProperty](#the-property-system-propertytree-and-inspectorproperty)
- [Custom drawers](#custom-drawers)
- [Injecting attributes: OdinAttributeProcessor](#injecting-attributes-odinattributeprocessor)
- [Self-validation](#self-validation)
- [ValueResolver for custom code](#valueresolver-for-custom-code)
- [GUI drawing helpers](#gui-drawing-helpers)

## Custom Editor and EditorWindow

`OdinEditor : Editor` — drop-in replacement for `UnityEditor.Editor` that
draws Odin-decorated types correctly. Override `OnInspectorGUI()` only if
adding content around the default draw; call `this.DrawTree()` or
`this.DrawDefaultInspector()` to get Odin's own rendering, and
`this.DrawUnityInspector()` to fall back to Unity's. Exposes `Tree`
(the `PropertyTree` backing the editor) for custom access.
[Source](https://odininspector.com/documentation/sirenix.odininspector.editor.odineditor)

`OdinEditorWindow : EditorWindow` — base class for a custom Editor window
that inspects a plain C# object (not necessarily a `UnityEngine.Object`).

```csharp
public class MyEditorWindow : OdinEditorWindow
{
    [MenuItem("Tools/My Window")]
    private static void OpenWindow() => GetWindow<MyEditorWindow>().Show();

    [Button] public void SomeButton() { }
    public SomeType[] someTableData;
}

// Inspecting a singleton or a non-UnityEngine.Object target:
public class MySingletonWindow : OdinEditorWindow
{
    protected override object GetTarget() => MySingleton.Instance;
}

// Inspecting an arbitrary object without a dedicated window class:
OdinEditorWindow.InspectObject(someObject);
```

Key members: `GetTarget()`/`GetTargets()` (override for a custom inspection
target), `DrawEditors()`, `DrawEditorPreview(int, float)`,
`EnableAutomaticHeightAdjustment(int maxHeight, bool retainInitialWindowPosition)`,
static `InspectObject(Object)` / `InspectObjectInDropDown(Object, Rect, ...)`.
[Source](https://odininspector.com/documentation/sirenix.odininspector.editor.odineditorwindow)

## Menu-based editor windows

`OdinMenuEditorWindow : OdinEditorWindow` adds a side menu tree — the base
for a multi-item tool window (e.g. a database/catalog browser). Override
`BuildMenuTree()` returning an `OdinMenuTree`, populated via
`tree.Add(string path, object instance)` (path segments separated by `/`
become nested menu groups, mirroring the grouping-attribute path syntax in
[attributes-layout-display.md](attributes-layout-display.md)).
[Source: OdinMenuEditorWindow](https://odininspector.com/documentation/sirenix.odininspector.editor.odinmenueditorwindow),
[OdinMenuTree](https://odininspector.com/documentation/sirenix.odininspector.editor.odinmenutree)

## The property system: PropertyTree and InspectorProperty

Every Odin-drawn Inspector is backed by one `PropertyTree`, created via one
of its static `Create(...)` overloads (from a target object, a `SerializedObject`,
or a list of targets for multi-selection). `PropertyTree.RootProperty` is the
root `InspectorProperty`; `Draw()`/`BeginDraw(bool withUndo)` render it.
Needed when building an `OdinEditorWindow` that manages its own `PropertyTree`
instead of relying on `OdinEditor`'s automatic one.
[Source: PropertyTree](https://odininspector.com/documentation/sirenix.odininspector.editor.propertytree)

`InspectorProperty` is one node in that tree — the same object a custom
drawer receives as `this.Property`. Useful members: `Children`, `Parent`,
`ValueEntry` (typed access to the underlying value, `SmartValue` in a typed
drawer), `Attributes`, `GetAttribute<T>()`, `FindParent`/`FindChild`,
`Tree`. [Source](https://odininspector.com/documentation/sirenix.odininspector.editor.inspectorproperty)

## Custom drawers

All custom drawers derive from `OdinDrawer` (abstract; never derive from it
directly — pick one of the three below). Shared mechanics: `this.Property`
(the `InspectorProperty` being drawn), `CanDrawProperty(InspectorProperty)`/
`CanDrawTypeFilter(Type)` to filter applicability, and
`CallNextDrawer(GUIContent label)` to hand off to the next drawer in the
chain instead of terminating it. Order across multiple applicable drawers is
governed by `DrawerPriorityAttribute` (higher priority runs first); a drawer
that never calls `CallNextDrawer` blocks every lower-priority drawer behind
it from running. [Source](https://odininspector.com/documentation/sirenix.odininspector.editor.odindrawer)

| Base class | Use when | Source |
|---|---|---|
| `OdinValueDrawer<T>` | The requirement is driven by a **type** — every `T` (and subtypes, respecting generic constraints) should draw this way regardless of which attribute decorates it | [OdinValueDrawer\<T\>](https://odininspector.com/documentation/sirenix.odininspector.editor.odinvaluedrawer-1) |
| `OdinAttributeDrawer<TAttribute>` | The requirement is driven by an **attribute**, for any value type it's applied to | [OdinAttributeDrawer\<TAttribute\>](https://odininspector.com/documentation/sirenix.odininspector.editor.odinattributedrawer-1) |
| `OdinAttributeDrawer<TAttribute, TValue>` | Attribute-driven, but only for a specific value type | same page |
| `OdinGroupDrawer<TGroupAttribute>` | Defining an entirely new grouping layout (the mechanism behind `BoxGroup`/`TabGroup` etc. in [attributes-layout-display.md](attributes-layout-display.md)) | [OdinDrawer](https://odininspector.com/documentation/sirenix.odininspector.editor.odindrawer) |

```csharp
// Type-driven: every MyCustomBaseType-derived value draws this way.
// #if UNITY_EDITOR-wrap the file, or put it under an Editor/ folder.
public sealed class MyCustomTypeDrawer<T> : OdinValueDrawer<T> where T : MyCustomBaseType
{
    protected override void DrawPropertyLayout(GUIContent label)
    {
        T value = this.ValueEntry.SmartValue;
        // Draw with GUILayout/EditorGUILayout here.
    }
}

// Attribute-driven, single value type: a slider replacing CustomRangeAttribute's default.
public sealed class CustomRangeAttributeDrawer : OdinAttributeDrawer<CustomRangeAttribute, float>
{
    protected override void DrawPropertyLayout(GUIContent label)
    {
        this.ValueEntry.SmartValue = EditorGUILayout.Slider(
            label, this.ValueEntry.SmartValue, this.Attribute.Min, this.Attribute.Max);
    }
}

// Attribute-driven, any value type: tints the GUI then defers to the next drawer.
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

**Critical caveat**: every custom property drawer must handle `label == null`
in `DrawPropertyLayout` — Odin passes `null` whenever the label is suppressed
(e.g. `[HideLabel]`, or drawing inside a list), and not guarding it throws.

## Injecting attributes: OdinAttributeProcessor

`OdinAttributeProcessor<TValue>` (or the non-generic `OdinAttributeProcessor`
for all types) lets you add, change, or remove attributes on a type you
don't own — the standard way to make a third-party or generated type draw
with Odin attributes without editing its source. Override
`ProcessSelfAttributes(InspectorProperty, List<Attribute>)` and/or
`ProcessChildMemberAttributes(InspectorProperty parentProperty, MemberInfo member, List<Attribute> attributes)`;
gate applicability with `CanProcessSelfAttributes`/`CanProcessChildMemberAttributes`.
[Source](https://odininspector.com/documentation/sirenix.odininspector.editor.odinattributeprocessor)

## Self-validation

For validating one type's own invariants in the Inspector without building a
project-wide validator: implement `ISelfValidator` on the type and populate
the `SelfValidationResult` parameter (`Add(...)`, or the severity-specific
helpers) inside its `Validate` method — Odin's `SelfValidator<T>` drawer
picks it up automatically. This is Inspector-only, same caveat as
`ValidateInput` in [attributes-conditional-validation.md](attributes-conditional-validation.md).
For a validator that must run across many types/assets as a project-wide
scan (`Validator<T>`, `RegisterValidatorAttribute`, `GlobalValidator`), that
is deeper Odin Validator territory — flag it to `tech-lead-csharp-unity`
rather than guessing at the API, per SKILL.md §8.
[Source: SelfValidator\<T\>](https://odininspector.com/documentation/sirenix.odininspector.editor.validation.selfvalidator-1),
[ValidationResult](https://odininspector.com/documentation/sirenix.odininspector.editor.validation.validationresult),
[SelfValidationResult](https://odininspector.com/documentation/sirenix.odininspector.selfvalidationresult)

## ValueResolver for custom code

Custom drawers/editors that need to resolve an Odin resolved-string
expression themselves (the same syntax documented in
[attributes-conditional-validation.md](attributes-conditional-validation.md)'s
resolved-string section) use `ValueResolver<TResult>.Get<TResult>(InspectorProperty property, string resolvedString)`,
then call `.GetValue(int selectionIndex = 0)`. Always check `resolver.HasError`
equivalent (`ValueResolver.DrawErrors`/`GetCombinedErrors` for surfacing
resolution failures in a custom drawer's GUI) rather than assuming resolution
succeeded.
[Source](https://odininspector.com/documentation/sirenix.odininspector.editor.valueresolvers.valueresolver-1)

## GUI drawing helpers

`Sirenix.Utilities.Editor.SirenixEditorGUI` is the standard toolkit for
drawing inside a custom drawer with Odin's own visual language instead of
raw `EditorGUILayout`: `BeginBox`/`EndBox`, `BeginBoxHeader`/`EndBoxHeader`,
`BeginToolbarBox`, `MessageBox`/`InfoMessageBox`/`ErrorMessageBox`,
`Title`, `IconButton`, `Foldout`, `DrawSolidRect`. `Sirenix.Utilities.Editor.EditorIcons`
supplies Odin's built-in icon set (used above as `EditorIcons.Plus`).
[Source: SirenixEditorGUI](https://odininspector.com/documentation/sirenix.utilities.editor.sirenixeditorgui)

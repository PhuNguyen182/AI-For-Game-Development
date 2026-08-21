# Data Binding — Runtime Binding vs SerializedObject Binding

Sources: [Data binding](https://docs.unity3d.com/Manual/UIE-data-binding.html), [Comparison between binding systems](https://docs.unity3d.com/Manual/UIE-comparison-binding.html), [Define a data source](https://docs.unity3d.com/Manual/UIE-runtime-binding-define-data-source.html), [Binding types](https://docs.unity3d.com/Manual/UIE-runtime-binding-types.html), [Binding mode and update trigger](https://docs.unity3d.com/Manual/UIE-runtime-binding-mode-update.html), [Custom binding types](https://docs.unity3d.com/Manual/UIE-runtime-binding-custom-types.html), [Get started with runtime binding](https://docs.unity3d.com/Manual/UIE-get-started-runtime-binding.html), [Editor SerializedObject binding](https://docs.unity3d.com/Manual/UIE-editor-binding.html), [Binding (SerializedObject) reference](https://docs.unity3d.com/Manual/UIE-Binding.html), [Binding implementation details](https://docs.unity3d.com/Manual/UIE-binding-implementation-details.html), [Bindable elements](https://docs.unity3d.com/Manual/UIE-bindable-elements.html).
Covers: SKILL.md §4 — **"Bind gameplay state through runtime data binding, and Editor state through `SerializedObject` binding — never poll a value in `Update`"**.

Two distinct binding systems exist and do not overlap: runtime binding
(any plain C# object, Runtime **and** Editor UI) and `SerializedObject`
binding (Editor UI only, tied to `SerializedProperty`).

## Which system applies

| Subject | What it decides | Source |
|---|---|---|
| Runtime data binding | Binds any plain C# `object`'s properties to UI control properties — Runtime UI, and Editor UI with no serialized backing | [Data binding](https://docs.unity3d.com/Manual/UIE-data-binding.html) |
| `SerializedObject` binding | Binds a `SerializedObject`'s properties — **Editor UI only**; recommended for serialized Editor data for its undo/redo and multi-selection support | [Editor SerializedObject binding](https://docs.unity3d.com/Manual/UIE-editor-binding.html) |
| Target scope | Runtime binding can bind several properties on one control. `SerializedObject` binding targets only the `value` property of an `INotifyValueChanged<T>` control | [Comparison between binding systems](https://docs.unity3d.com/Manual/UIE-comparison-binding.html) |
| Array path syntax | Runtime: `Path.To.List[2]`. `SerializedObject`: `Path.To.List.Array.data[2]` | [Comparison between binding systems](https://docs.unity3d.com/Manual/UIE-comparison-binding.html) |
| Extensibility | Runtime binding supports custom `CustomBinding` types; `SerializedObject` binding is not extensible | [Comparison between binding systems](https://docs.unity3d.com/Manual/UIE-comparison-binding.html) |

## Runtime data binding

| Subject | What it decides | Source |
|---|---|---|
| Declaring a source | `element.dataSource = myObject; element.dataSourcePath = PropertyPath.FromName(nameof(X));` — every bindable property needs `[CreateProperty]` | [Define a data source](https://docs.unity3d.com/Manual/UIE-runtime-binding-define-data-source.html) |
| `INotifyBindablePropertyChanged` | Requires `event EventHandler<BindablePropertyChangedEventArgs> propertyChanged;`, raised in the setter **only on an actual change** | [Define a data source](https://docs.unity3d.com/Manual/UIE-runtime-binding-define-data-source.html) |
| Value-type source cost | A `struct` data source boxes on every assignment, since `dataSource` is typed `object` | [Define a data source](https://docs.unity3d.com/Manual/UIE-runtime-binding-define-data-source.html) |
| Binding mode, default **TwoWay** | `ToTarget` (source→UI, use for read-only UI), `ToSource` (UI→source), `ToTargetOnce` (source→UI once, unless marked dirty again) | [Binding mode and update trigger](https://docs.unity3d.com/Manual/UIE-runtime-binding-mode-update.html) |
| Update trigger | `EveryUpdate` (continuous), `OnSourceChanged` (falls back to every-frame if change detection isn't feasible for that source type), `WhenDirty` (only on explicit `MarkDirty()`) | [Binding mode and update trigger](https://docs.unity3d.com/Manual/UIE-runtime-binding-mode-update.html) |
| `DataBinding` API | `element.SetBinding("value", new DataBinding { dataSourcePath = new PropertyPath(nameof(X)) });` plus `ClearBinding()`/`GetBinding()`/`HasBinding()` | [Binding types](https://docs.unity3d.com/Manual/UIE-runtime-binding-types.html) |
| Custom `CustomBinding` | Override `Update()`; implement `IDataSourceProvider`; lifecycle hooks `OnActivated`/`OnDeactivated`/`OnDataSourceChanged`; mark `[UxmlObject]`/`[UxmlAttribute]` to expose it to UI Builder | [Custom binding types](https://docs.unity3d.com/Manual/UIE-runtime-binding-custom-types.html) |
| Per-element state gotcha | Don't store per-element state inside a binding type instance — one binding definition can apply to multiple elements; key a dictionary by context object instead | [Binding mode and update trigger](https://docs.unity3d.com/Manual/UIE-runtime-binding-mode-update.html) |

```xml
<!-- UXML runtime data binding -->
<engine:Label text="Label" data-source="ExampleObject.asset" data-source-path="simpleLabel">
    <Bindings>
        <engine:DataBinding property="text" binding-mode="ToTarget" />
    </Bindings>
</engine:Label>
```

## SerializedObject binding (Editor only)

| Subject | What it decides | Source |
|---|---|---|
| `.Bind(SerializedObject)` | Call once on a root/parent; recursively binds every descendant with a `bindingPath` set | [Binding (SerializedObject) reference](https://docs.unity3d.com/Manual/UIE-Binding.html) |
| Async first update | `Bind()` is asynchronous — a bound field's `value` is **not** immediately updated right after the call | [Binding implementation details](https://docs.unity3d.com/Manual/UIE-binding-implementation-details.html) |
| Call-once rule | Calling `Bind()` twice on the same element costs real performance; call `Unbind()` before rebinding to a different target | [Binding (SerializedObject) reference](https://docs.unity3d.com/Manual/UIE-Binding.html) |
| Don't call it from `CreateInspectorGUI`/`CreatePropertyGUI` | Unity already binds automatically right after those return, per [editor-ui-authoring.md](editor-ui-authoring.md) | [Binding (SerializedObject) reference](https://docs.unity3d.com/Manual/UIE-Binding.html) |
| Change detection | Polling-based: re-serializes the `SerializedObject` first and short-circuits if nothing changed; only then diffs individual values. Long polls split across frames | [Binding implementation details](https://docs.unity3d.com/Manual/UIE-binding-implementation-details.html) |
| `TrackPropertyValue()`/`TrackSerializedObjectValue()` | Register a callback for when a specific property (or the whole object) changes — the recommended reaction path instead of full rebinding | [Binding (SerializedObject) reference](https://docs.unity3d.com/Manual/UIE-Binding.html) |
| Bindable base classes | `BaseField`, `BaseBoolField`, `BaseSlider`, `BaseCompositeField` and 60+ built-in controls inherit `bindingPath` support automatically | [Bindable elements](https://docs.unity3d.com/Manual/UIE-bindable-elements.html) |

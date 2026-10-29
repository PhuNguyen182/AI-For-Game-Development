# Data binding

Sources: [Data binding](https://docs.unity3d.com/Manual/UIE-data-binding.html), [Compare](https://docs.unity3d.com/Manual/UIE-comparison-binding.html), [Data source](https://docs.unity3d.com/Manual/UIE-runtime-binding-define-data-source.html), [Types](https://docs.unity3d.com/Manual/UIE-runtime-binding-types.html), [Mode/trigger](https://docs.unity3d.com/Manual/UIE-runtime-binding-mode-update.html), [Custom](https://docs.unity3d.com/Manual/UIE-runtime-binding-custom-types.html), [SerializedObject](https://docs.unity3d.com/Manual/UIE-editor-binding.html), [Bind ref](https://docs.unity3d.com/Manual/UIE-Binding.html), [Internals](https://docs.unity3d.com/Manual/UIE-binding-implementation-details.html).

## Two systems
| | Runtime binding | `SerializedObject` binding |
|---|---|---|
| Source | Any plain C# object | `SerializedObject` |
| Where | Runtime and Editor UI | Editor UI only (undo/redo, multi-selection) |
| Target | Several properties per control | Only `value` of an `INotifyValueChanged<T>` |
| Array path | `Path.To.List[2]` | `Path.To.List.Array.data[2]` |
| Extensible | Yes (`CustomBinding`) | No |

## Runtime binding
- `element.dataSource = obj; element.dataSourcePath = PropertyPath.FromName(nameof(X));` Every bindable property needs `[CreateProperty]`.
- `INotifyBindablePropertyChanged`: `event EventHandler<BindablePropertyChangedEventArgs> propertyChanged`, raised in the setter only on an actual change.
- A `struct` source boxes on every assignment (`dataSource` is `object`).
- Mode (default TwoWay): `ToTarget` (read-only UI), `ToSource`, `ToTargetOnce` (until marked dirty).
- Update trigger: `EveryUpdate`; `OnSourceChanged` (falls back to every frame when change detection is infeasible for the source type); `WhenDirty` (explicit `MarkDirty()`).
- API: `element.SetBinding("value", new DataBinding { dataSourcePath = new PropertyPath(nameof(X)) })`, plus `ClearBinding()`/`GetBinding()`/`HasBinding()`.
- `CustomBinding`: override `Update()`, implement `IDataSourceProvider`, hooks `OnActivated`/`OnDeactivated`/`OnDataSourceChanged`; mark `[UxmlObject]`/`[UxmlAttribute]` to expose it to UI Builder.
- Do not keep per-element state in a binding instance (one definition can serve many elements); key a dictionary by context object.

```xml
<engine:Label data-source="ExampleObject.asset" data-source-path="simpleLabel">
    <Bindings><engine:DataBinding property="text" binding-mode="ToTarget" /></Bindings>
</engine:Label>
```

## SerializedObject binding
- `.Bind(so)` once on a root: binds every descendant with `bindingPath`. It is asynchronous: `value` is not updated right after the call.
- A second `Bind()` on the same element costs performance; `Unbind()` before rebinding to another target.
- Do not call it in `CreateInspectorGUI`/`CreatePropertyGUI` (implicit bind, [editor-ui-authoring.md](editor-ui-authoring.md)).
- Change detection polls: re-serializes first, short-circuits if unchanged, else diffs values; long polls split across frames.
- React with `TrackPropertyValue()` / `TrackSerializedObjectValue()` rather than rebinding.
- `BaseField`, `BaseBoolField`, `BaseSlider`, `BaseCompositeField` and 60+ built-ins support `bindingPath`.

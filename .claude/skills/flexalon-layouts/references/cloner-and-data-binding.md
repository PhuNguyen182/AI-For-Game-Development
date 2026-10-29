# Cloner and Data Binding

Pages: `/docs/cloner`, API `FlexalonCloner`, `CloneTypes`, `DataSource`, `DataBinding`.

`FlexalonCloner` instantiates one resident gameObject per clone or data item, with no pooling: cost scales with `Data.Count`. Large or scrolling data goes to `osa-optimized-scrollview-adapter`.

It is a plain `MonoBehaviour`, not a `FlexalonComponent`, and has no layout of its own: put a layout on the same gameObject (docs example: a wrapping Flexible Layout).

| Property | Decides |
|---|---|
| `Objects` | Prefabs cloned as children |
| `CloneType` | `Iterative = 0` walks `Objects` in order and repeats; `Random = 1` |
| `RandomSeed` | Stable `Random` sequence across regenerations |
| `Count` | Clone count; overridden by `Data.Count` when `DataSource` is set |
| `DataSource` (`GameObject`) | Object carrying a component that implements `DataSource` |
| `MarkDirty()` | Regenerates clones (not the layout update) |

## Data path
- `DataSource.Data`: `IReadOnlyList<object>`, one clone per element. Value types box; bind a reference type for anything that rebinds often.
- `DataSource.DataChanged` (`event Action`): raise on every mutation; nothing polls `Data`, so a silent mutation leaves stale clones.
- `DataBinding.SetData(object)`: called on the clone. The cloner searches the instantiated prefab for it, so the component must sit on the prefab, not a parent or sibling.
- Do not instantiate into the cloner's parent by hand: those objects are never rebuilt or rebound.
- The data model stays in Shared Core; `DataSource`/`DataBinding` are `Game.Client.*` adapters over it.

```csharp
public class ItemSource : MonoBehaviour, DataSource
{
    readonly List<object> _items = new();
    public IReadOnlyList<object> Data => _items;
    public event Action DataChanged;
    public void Set(IEnumerable<string> ids) { _items.Clear(); _items.AddRange(ids); DataChanged?.Invoke(); }
}
```

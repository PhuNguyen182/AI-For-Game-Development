# Cloner and Data Binding — generating children from prefabs or data

Sources: [Cloner](https://www.flexalon.com/docs/cloner), [Class FlexalonCloner](https://www.flexalon.com/docs/api/Flexalon.FlexalonCloner.html), [Enum CloneTypes](https://www.flexalon.com/docs/api/Flexalon.FlexalonCloner.CloneTypes.html), [Interface DataSource](https://www.flexalon.com/docs/api/Flexalon.DataSource.html), [Interface DataBinding](https://www.flexalon.com/docs/api/Flexalon.DataBinding.html).
Covers: SKILL.md §4 — **"Generate repeated children with Flexalon Cloner bound to a data source"**.

`FlexalonCloner` instantiates a layout's children instead of them being
authored statically, optionally one per item in a data source. It is a
generator, not a virtualizer: one gameObject per item, all resident. A large
or scrolling dataset belongs to `osa-optimized-scrollview-adapter`, not here.

## `FlexalonCloner`

| Property | What it decides | Source |
|---|---|---|
| `Objects` (`List<GameObject>`) | The prefabs cloned as children | [Class FlexalonCloner](https://www.flexalon.com/docs/api/Flexalon.FlexalonCloner.html) |
| `CloneType` (`CloneTypes`) | `Iterative = 0` walks `Objects` in order and repeats; `Random = 1` picks randomly | [Enum CloneTypes](https://www.flexalon.com/docs/api/Flexalon.FlexalonCloner.CloneTypes.html) |
| `RandomSeed` (`int`) | Keeps a `Random` clone sequence stable across regenerations | [Class FlexalonCloner](https://www.flexalon.com/docs/api/Flexalon.FlexalonCloner.html) |
| `Count` (`uint`) | How many clones to create — **overridden by the data source's item count** when `DataSource` is set | [Cloner](https://www.flexalon.com/docs/cloner) |
| `DataSource` (`GameObject`) | A gameObject carrying a component that implements `DataSource`; the clone count becomes `Data.Count` | [Class FlexalonCloner](https://www.flexalon.com/docs/api/Flexalon.FlexalonCloner.html) |
| `MarkDirty()` | Forces the cloner to regenerate its clones | [Class FlexalonCloner](https://www.flexalon.com/docs/api/Flexalon.FlexalonCloner.html) |

`FlexalonCloner` is a plain `MonoBehaviour`, not a `FlexalonComponent` — its
`MarkDirty()` regenerates clones and is a different operation from
`FlexalonComponent.MarkDirty()`, which schedules a layout update. The cloner
carries no layout of its own: put a layout component on the **same**
gameObject to arrange what it produces, as the docs' image-search example
does with a wrapping Flexible Layout.

## The data path

| Piece | Contract | Source |
|---|---|---|
| `DataSource.Data` | `IReadOnlyList<object>` — one clone is instantiated per element | [Interface DataSource](https://www.flexalon.com/docs/api/Flexalon.DataSource.html) |
| `DataSource.DataChanged` | `event Action` — **raise it to notify the cloner the data changed**; nothing polls `Data` | [Interface DataSource](https://www.flexalon.com/docs/api/Flexalon.DataSource.html) |
| `DataBinding.SetData(object)` | Called on the clone with its data entry. The cloner **searches the cloned object** for any component implementing `DataBinding` | [Interface DataBinding](https://www.flexalon.com/docs/api/Flexalon.DataBinding.html) |

```csharp
using System;
using System.Collections.Generic;
using TMPro;
using UnityEngine;
using Flexalon;

namespace Game.Client.Layout
{
    public class InventoryDataSource : MonoBehaviour, DataSource
    {
        private readonly List<object> _items = new List<object>();

        public IReadOnlyList<object> Data => this._items;

        public event Action DataChanged;

        public void SetItems(IEnumerable<string> itemIds)
        {
            this._items.Clear();
            this._items.AddRange(itemIds);
            this.DataChanged?.Invoke();
        }
    }

    public class InventorySlotBinding : MonoBehaviour, DataBinding
    {
        [SerializeField] private TMP_Text label;

        public void SetData(object data)
        {
            this.label.text = (string)data;
        }
    }
}
```

**Critical caveat**: `Data` is `IReadOnlyList<object>`, so every value type
entry is boxed on the way in and unboxed in `SetData`. Bind reference types
(a class holding the row's fields) rather than `int`/`float`/`struct`
entries in anything that re-binds frequently, per
`performance-and-algorithms.md`'s Memory discipline section.

## Rules that follow from the design

| Rule | Reason | Source |
|---|---|---|
| Let the cloner own its children | It manages creation and destruction; objects instantiated into the same parent by hand are outside that lifecycle and will not be rebuilt or rebound | [Cloner](https://www.flexalon.com/docs/cloner) |
| Raise `DataChanged` on every mutation | The cloner regenerates on the event, not on inspection — a mutated list that never raises it leaves stale clones on screen | [Interface DataSource](https://www.flexalon.com/docs/api/Flexalon.DataSource.html) |
| Put the `DataBinding` component on the prefab | The cloner searches the instantiated object for it; a binding living on a parent or a sibling is never found | [Cloner](https://www.flexalon.com/docs/cloner) |
| Expect one gameObject per data item | No pooling or recycling is documented — cost scales linearly with `Data.Count` | [Cloner](https://www.flexalon.com/docs/cloner) |
| Keep the data model itself in Shared Core | `DataSource`/`DataBinding` are `UnityEngine`-side adapters over Core state, per `coding-principles.md`'s Shared Core integrity section | synthesized |

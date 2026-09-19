# Collection & Table Attributes — Sirenix.OdinInspector lists, dictionaries, matrices

Source: [ListDrawerSettingsAttribute](https://odininspector.com/documentation/sirenix.odininspector.listdrawersettingsattribute), [TableListAttribute](https://odininspector.com/documentation/sirenix.odininspector.tablelistattribute), [TableColumnWidthAttribute](https://odininspector.com/documentation/sirenix.odininspector.tablecolumnwidthattribute), [TableMatrixAttribute](https://odininspector.com/documentation/sirenix.odininspector.tablematrixattribute), [DictionaryDrawerSettings](https://odininspector.com/documentation/sirenix.odininspector.dictionarydrawersettings), [MultiLinePropertyAttribute](https://odininspector.com/documentation/sirenix.odininspector.multilinepropertyattribute).
Covers: SKILL.md §4 — **"Route to the narrowest reference file for the concern"**.

Attributes that customize how `List<T>`/arrays, `Dictionary<K,V>`, and 2-D
arrays render. A `Dictionary<K,V>` or a multi-dimensional array needs
[serialization.md](serialization.md)'s `SerializedMonoBehaviour`/
`SerializedScriptableObject`/`[OdinSerialize]` before it will serialize at
all — these attributes only change *presentation* once it does.

## Table of contents
- [Lists & arrays](#lists--arrays)
- [Tables](#tables)
- [2-D array matrices](#2-d-array-matrices)
- [Dictionaries](#dictionaries)

## Lists & arrays

`ListDrawerSettingsAttribute()` — no required constructor args, configured
entirely through fields/properties:

| Field/Property | What it decides | Source |
|---|---|---|
| `ShowFoldout` | `false` forces the list permanently expanded (no collapse) | [ListDrawerSettingsAttribute](https://odininspector.com/documentation/sirenix.odininspector.listdrawersettingsattribute) |
| `IsReadOnly` | Removes add/remove/drag while still letting each element draw normally — unlike wrapping the whole list in `[ReadOnly]` | same |
| `DraggableItems`, `ShowIndexLabels`, `ShowItemCount`, `ShowPaging`, `NumberOfItemsPerPage` | Override the corresponding Odin Preferences defaults per-list | same |
| `HideAddButton`, `HideRemoveButton` | Remove the built-in buttons — pair with `OnTitleBarGUI`/`OnBeginListElementGUI`/`OnEndListElementGUI` to inject custom ones | same |
| `CustomAddFunction`, `CustomRemoveElementFunction`, `CustomRemoveIndexFunction` | Resolved method names that replace the default add/remove behavior | same |
| `ListElementLabelName` | Names a member inside each element to use as that element's label instead of `"Element 0"` | same |
| `ElementColor` | Resolved string with `(int index, Color defaultColor)` parameters to recolor individual rows | same |
| `AddCopiesLastElement`, `AlwaysAddDefaultValue` | Control what a new element is initialized to when added | same |

```csharp
// Custom add button replacing the default one.
[ListDrawerSettings(HideAddButton = true, OnTitleBarGUI = "DrawTitleBarGUI")]
public List<MyType> someList;

#if UNITY_EDITOR
private void DrawTitleBarGUI()
{
    if (SirenixEditorGUI.ToolbarButton(EditorIcons.Plus))
    {
        this.someList.Add(new MyType());
    }
}
#endif
```

## Tables

`TableListAttribute()` renders a `List<T>`/array as a spreadsheet-style
table, one row per element, one column per the element type's members.

| Field/Property | What it decides | Source |
|---|---|---|
| `IsReadOnly` | Removes add/delete, keeps cells editable — same distinction as the list drawer's `IsReadOnly` | [TableListAttribute](https://odininspector.com/documentation/sirenix.odininspector.tablelistattribute) |
| `AlwaysExpanded`, `HideToolbar` | Removes the collapse/toolbar chrome | same |
| `DrawScrollView`, `MinScrollViewHeight`/`MaxScrollViewHeight` (`ScrollViewHeight` sets both) | Controls when/how a scrollbar appears | same |
| `DefaultMinColumnWidth`, `CellPadding` | Table-wide sizing defaults, overridable per column | same |
| `ShowPaging`, `NumberOfItemsPerPage`, `ShowIndexLabels` | Same semantics as `ListDrawerSettings` | same |

`TableColumnWidthAttribute(int width, bool resizable = true)` — put on an
individual member of the row type to override that one column's width/
resizability instead of the table-wide default.
[Source](https://odininspector.com/documentation/sirenix.odininspector.tablecolumnwidthattribute)

## 2-D array matrices

`TableMatrixAttribute()` — applied to a `T[,]` field. Requires Odin
serialization ([serialization.md](serialization.md)) unless the value is
shown via `[ShowInInspector]` without needing to persist.

| Field | What it decides | Source |
|---|---|---|
| `DrawElementMethod` | Resolved `static TValue Method(Rect rect, TValue value)` that replaces the default cell renderer — the way to draw a fully custom cell (color swatch, click-to-toggle, etc.) | [TableMatrixAttribute](https://odininspector.com/documentation/sirenix.odininspector.tablematrixattribute) |
| `HorizontalTitle`, `VerticalTitle`, `Labels` | Axis headers; `Labels` resolves to a `(string, LabelDirection)` tuple for per-row/column custom labels | same |
| `IsReadOnly` | Disables inserting/removing/dragging rows and columns; cells remain editable | same |
| `SquareCells`, `RowHeight`, `ResizableColumns` | Cell sizing | same |
| `Transpose` | Draws with rows/columns reversed relative to C# initialization order | same |

## Dictionaries

`DictionaryDrawerSettings` (a plain `Attribute`, not a `PropertyGroupAttribute`)
applied to a `Dictionary<TKey, TValue>` field — requires Odin serialization
per [serialization.md](serialization.md).

| Field | What it decides | Source |
|---|---|---|
| `DisplayMode` (`DictionaryDisplayOptions`) | How key/value pairs render (foldout list, one-line, etc.) | [DictionaryDrawerSettings](https://odininspector.com/documentation/sirenix.odininspector.dictionarydrawersettings) |
| `IsReadOnly` | Removes add/remove editing | same |
| `KeyLabel`, `ValueLabel` | Column header text override | same |
| `KeyColumnWidth` | Fixed width for the key column | same |

`MultiLinePropertyAttribute(int lines = 3)` is unrelated to collections but
commonly sits on a `string` element inside a list/table row to give it a
multi-line text box instead of a single-line field.
[Source](https://odininspector.com/documentation/sirenix.odininspector.multilinepropertyattribute)

# Collection & Table Attributes

Presentation only. A `Dictionary` or `T[,]` must first serialize via [serialization.md](serialization.md).

## ListDrawerSettings
No constructor args; set fields.

| Field | Effect |
|---|---|
| `ShowFoldout` | `false` = always expanded |
| `IsReadOnly` | No add/remove/drag, elements still draw normally (unlike `[ReadOnly]` on the list) |
| `DraggableItems`, `ShowIndexLabels`, `ShowItemCount`, `ShowPaging`, `NumberOfItemsPerPage` | Per-list override of Odin Preferences |
| `HideAddButton`, `HideRemoveButton` | Pair with `OnTitleBarGUI`/`OnBeginListElementGUI`/`OnEndListElementGUI` for custom buttons. Callbacks calling `SirenixEditorGUI`/`EditorIcons` must sit inside `#if UNITY_EDITOR` ([editor-extensibility.md](editor-extensibility.md)) |
| `CustomAddFunction`, `CustomRemoveElementFunction`, `CustomRemoveIndexFunction` | Resolved methods replacing add/remove |
| `ListElementLabelName` | Member of each element used as its label |
| `ElementColor` | Resolved `(int index, Color defaultColor)` per-row colour |
| `AddCopiesLastElement`, `AlwaysAddDefaultValue` | Initial value of added elements |

## TableList
Spreadsheet view of a list/array: row per element, column per member.

| Field | Effect |
|---|---|
| `IsReadOnly` | No add/delete, cells editable |
| `AlwaysExpanded`, `HideToolbar` | Remove chrome |
| `DrawScrollView`, `MinScrollViewHeight`/`MaxScrollViewHeight` (`ScrollViewHeight` = both) | Scrollbar |
| `DefaultMinColumnWidth`, `CellPadding` | Table-wide sizing |
| `ShowPaging`, `NumberOfItemsPerPage`, `ShowIndexLabels` | As `ListDrawerSettings` |

`TableColumnWidth(int width, bool resizable = true)` on a row-type member overrides one column.

## TableMatrix
On a `T[,]` field. Needs Odin serialization unless shown via `[ShowInInspector]` without persisting.

| Field | Effect |
|---|---|
| `DrawElementMethod` | Resolved `static TValue Method(Rect rect, TValue value)` replacing the cell renderer |
| `HorizontalTitle`, `VerticalTitle`, `Labels` | Axis headers; `Labels` resolves to `(string, LabelDirection)` |
| `IsReadOnly` | No row/column insert/remove/drag; cells editable |
| `SquareCells`, `RowHeight`, `ResizableColumns` | Cell sizing |
| `Transpose` | Reverses rows/columns versus C# initialisation order |

## DictionaryDrawerSettings
Plain `Attribute` on a `Dictionary<TKey, TValue>` field; needs Odin serialization.

| Field | Effect |
|---|---|
| `DisplayMode` (`DictionaryDisplayOptions`) | Foldout list, one-line, etc. |
| `IsReadOnly` | No add/remove |
| `KeyLabel`, `ValueLabel`, `KeyColumnWidth` | Headers and key width |

`MultiLineProperty(lines = 3)` gives a `string` element (e.g. in a table row) a multi-line box.

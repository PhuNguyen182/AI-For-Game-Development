# Selection & Reference Attributes

What an object/asset/type/path field can hold or show.

## Dropdowns
| Attribute | Notes |
|---|---|
| `ValueDropdown(valuesGetter)` | Getter resolves to an `IList` (array, `List<T>`, or `ValueDropdownList<T>` for custom display names). Fields `IsUniqueList`, `ExcludeExistingValuesInList`, `DropdownTitle/Width/Height`, `DoubleClickToConfirm`, `OnlyChangeValueOnConfirm`, `FlattenTreeView`, `NumberOfItemsBeforeEnablingSearch` (10), `AppendNextDrawer` |
| `TypeFilter(filterGetter)` | Same pattern; restricts the `Type` of a polymorphic reference. `DrawValueNormally`, `DropdownTitle` |

A `static` array of enum values as a `ValueDropdown` source can appear empty (Unity domain-reload bug). Workaround: serialize it via `[SerializeField, HideInInspector]` on a backing field.

## Assets
| Attribute | Notes |
|---|---|
| `AssetSelector` | Project-asset dropdown on any Unity-type field. `Filter` (`AssetDatabase.FindAssets` string), `Paths` (pipe-separated folders), `IsUniqueList`, `DropdownTitle/Width/Height` |
| `AssetList` | Checklist of matching assets for a list or single object. `Path`, `Tags`, `LayerNames`, `AssetNamePrefix`, `CustomFilterMethod`, `AutoPopulate` |
| `AssetsOnly` | Rejects scene objects |

## Inline editing & previews
| Attribute | Notes |
|---|---|
| `InlineEditor(InlineEditorModes = GUIOnly, InlineEditorObjectFieldModes = Boxed)` | Embeds the referenced object's editor. Modes `GUIOnly`, `FullEditor`, `GUIAndHeader`, `SmallPreview`, `LargePreview`. `DrawHeader`, `DrawGUI`, `DrawPreview`, `MaxHeight`, `PreviewHeight/Width`, `Expanded` |
| `PreviewField` `()`, `(height, alignment)`, string-getter overloads | Thumbnail field; drag to swap, Ctrl+drop to replace, Ctrl+click to clear |
| `InlineProperty` | `[Serializable]` type's members inline beside its label; on the type or the member. `LabelWidth` |

## Paths
| Attribute | Notes |
|---|---|
| `FilePath` | `string` picker, project-relative by default. `ParentFolder` (`$Member` ok), `Extensions` (comma-separated), `AbsolutePath`, `RequireExistingPath`, `UseBackslashes`, `IncludeFileExtension` |
| `FolderPath` | Same for directories (no `Extensions`) |

## Misc
| Attribute | Notes |
|---|---|
| `ColorPalette` `()`, `(paletteName)` | Swatch picker (palettes: Odin Preferences -> Drawers -> Color Palettes); field stays freely editable |
| `HideMonoScript` | Hides the "Script" field |
| `DrawWithUnity` | Falls back to Unity's `PropertyDrawer`; a higher-priority Odin drawer can still override |
| `Searchable` | Search box filtering the member's children; not valid directly on a dictionary. `FilterOptions`, `FuzzySearch` (true), `Recursive` (true) |

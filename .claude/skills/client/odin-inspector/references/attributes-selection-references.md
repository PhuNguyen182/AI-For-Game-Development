# Selection & Reference Attributes — Sirenix.OdinInspector object/asset/type pickers

Source: [ValueDropdownAttribute](https://odininspector.com/documentation/sirenix.odininspector.valuedropdownattribute), [AssetSelectorAttribute](https://odininspector.com/documentation/sirenix.odininspector.assetselectorattribute), [AssetListAttribute](https://odininspector.com/documentation/sirenix.odininspector.assetlistattribute), [AssetsOnlyAttribute](https://odininspector.com/documentation/sirenix.odininspector.assetsonlyattribute), [TypeFilterAttribute](https://odininspector.com/documentation/sirenix.odininspector.typefilterattribute), [InlineEditorAttribute](https://odininspector.com/documentation/sirenix.odininspector.inlineeditorattribute), [PreviewFieldAttribute](https://odininspector.com/documentation/sirenix.odininspector.previewfieldattribute), [FilePathAttribute](https://odininspector.com/documentation/sirenix.odininspector.filepathattribute), [FolderPathAttribute](https://odininspector.com/documentation/sirenix.odininspector.folderpathattribute), [ColorPaletteAttribute](https://odininspector.com/documentation/sirenix.odininspector.colorpaletteattribute), [InlinePropertyAttribute](https://odininspector.com/documentation/sirenix.odininspector.inlinepropertyattribute), [HideMonoScriptAttribute](https://odininspector.com/documentation/sirenix.odininspector.hidemonoscriptattribute), [DrawWithUnityAttribute](https://odininspector.com/documentation/sirenix.odininspector.drawwithunityattribute), [SearchableAttribute](https://odininspector.com/documentation/sirenix.odininspector.searchableattribute).
Covers: SKILL.md §4 — **"Route to the narrowest reference file for the concern"**.

Attributes that constrain, preview, or search *what* an object/asset/type
field can hold, as opposed to whether it's currently editable
(that's [attributes-conditional-validation.md](attributes-conditional-validation.md)).

## Table of contents
- [Value & type dropdowns](#value--type-dropdowns)
- [Asset constraints](#asset-constraints)
- [Inline editing & previews](#inline-editing--previews)
- [Path pickers](#path-pickers)
- [Misc reference cosmetics](#misc-reference-cosmetics)

## Value & type dropdowns

| Attribute | Constructor | Key fields | What it decides | Source |
|---|---|---|---|---|
| `ValueDropdownAttribute` | `(string valuesGetter)` | `IsUniqueList`, `ExcludeExistingValuesInList` (list mode), `DropdownTitle/Width/Height`, `DoubleClickToConfirm`, `OnlyChangeValueOnConfirm`, `FlattenTreeView`, `NumberOfItemsBeforeEnablingSearch` (default 10), `AppendNextDrawer` | `valuesGetter` must resolve to an `IList` — a field/property/method returning an array, `List<T>`, or a `ValueDropdownList<T>` for custom display names on values with no useful `ToString()` | [ValueDropdownAttribute](https://odininspector.com/documentation/sirenix.odininspector.valuedropdownattribute) |
| `TypeFilterAttribute` | `(string filterGetter)` | `DrawValueNormally`, `DropdownTitle` | Same resolved-`IList` pattern as `ValueDropdown`, but for constraining which `Type` a polymorphic reference field can be assigned | [TypeFilterAttribute](https://odininspector.com/documentation/sirenix.odininspector.typefilterattribute) |

**Critical caveat**: a `static` array of enum values used as a
`ValueDropdown` source can appear empty due to a Unity domain-reload bug —
the documented workaround is forcing Unity to serialize the array via
`[SerializeField, HideInInspector]` on a backing field.

## Asset constraints

| Attribute | Constructor | Key fields | What it decides | Source |
|---|---|---|---|---|
| `AssetSelectorAttribute` | `()`; `(string paletteName)`-style config via properties | `Filter` (an `AssetDatabase.FindAssets` filter string), `Paths` (pipe-separated folders, e.g. `"Assets/Textures|Assets/Other"`), `IsUniqueList`, `DropdownTitle/Width/Height` | Adds a project-asset dropdown button next to any Unity-type object field | [AssetSelectorAttribute](https://odininspector.com/documentation/sirenix.odininspector.assetselectorattribute) |
| `AssetListAttribute` | `()` | `Path`, `Tags`, `LayerNames`, `AssetNamePrefix`, `CustomFilterMethod` (resolved bool-returning filter), `AutoPopulate` | Replaces a list/array's default drawer with a checklist of matching project assets — works on both a single `UnityEngine.Object` field and a `List<T>` | [AssetListAttribute](https://odininspector.com/documentation/sirenix.odininspector.assetlistattribute) |
| `AssetsOnlyAttribute()` | — | — | Restricts an object field to project assets, rejecting scene objects | [AssetsOnlyAttribute](https://odininspector.com/documentation/sirenix.odininspector.assetsonlyattribute) |

## Inline editing & previews

| Attribute | Constructor | Key fields | What it decides | Source |
|---|---|---|---|---|
| `InlineEditorAttribute` | `(InlineEditorModes inlineEditorMode = GUIOnly, InlineEditorObjectFieldModes objectFieldMode = Boxed)` | `DrawHeader`, `DrawGUI`, `DrawPreview`, `MaxHeight`, `PreviewHeight/Width`, `PreviewAlignment`, `Expanded` | Embeds the referenced object's own editor inline (`GUIOnly`, `FullEditor`, `GUIAndHeader`, `SmallPreview`, `LargePreview` modes) instead of a plain object field | [InlineEditorAttribute](https://odininspector.com/documentation/sirenix.odininspector.inlineeditorattribute) |
| `PreviewFieldAttribute` | `()`; `(float height, ObjectFieldAlignment alignment = ...)`; string-getter overloads for a custom preview texture | `Height`, `Alignment`, `FilterMode`, `PreviewGetter` | Square object field rendering an asset thumbnail; supports drag-swap between two preview fields, Ctrl+drop to replace, Ctrl+click to clear | [PreviewFieldAttribute](https://odininspector.com/documentation/sirenix.odininspector.previewfieldattribute) |
| `InlinePropertyAttribute()` | — | `LabelWidth` | Draws a `[Serializable]` type's members inline next to its own label instead of in a foldout — put on the type itself or on the member | [InlinePropertyAttribute](https://odininspector.com/documentation/sirenix.odininspector.inlinepropertyattribute) |

## Path pickers

| Attribute | Key fields | What it decides | Source |
|---|---|---|---|
| `FilePathAttribute` | `ParentFolder` (supports `$Member`), `Extensions` (comma-separated, dots optional), `AbsolutePath`, `RequireExistingPath`, `UseBackslashes`, `IncludeFileExtension` | File-path picker for a `string` field; project-relative by default | [FilePathAttribute](https://odininspector.com/documentation/sirenix.odininspector.filepathattribute) |
| `FolderPathAttribute` | `ParentFolder`, `AbsolutePath`, `RequireExistingPath`, `UseBackslashes` | Same, for a directory path | [FolderPathAttribute](https://odininspector.com/documentation/sirenix.odininspector.folderpathattribute) |

## Misc reference cosmetics

| Attribute | Constructor | What it decides | Source |
|---|---|---|---|
| `ColorPaletteAttribute` | `()`; `(string paletteName)` | Adds a swatch picker from a named palette (edited under Odin Preferences → Drawers → Color Palettes) next to a `Color`/`Color[]` field; the field stays freely editable regardless | [ColorPaletteAttribute](https://odininspector.com/documentation/sirenix.odininspector.colorpaletteattribute) |
| `HideMonoScriptAttribute()` | — | Hides the read-only "Script" field Unity normally shows at the top of a component | [HideMonoScriptAttribute](https://odininspector.com/documentation/sirenix.odininspector.hidemonoscriptattribute) |
| `DrawWithUnityAttribute()` | — | Falls back to Unity's native `PropertyDrawer` for one member — an escape hatch, not a guarantee, since a higher-priority Odin drawer can still override it | [DrawWithUnityAttribute](https://odininspector.com/documentation/sirenix.odininspector.drawwithunityattribute) |
| `SearchableAttribute()` | `FilterOptions`, `FuzzySearch` (default true), `Recursive` (default true) | Adds a search box that filters the member's own children; does not work applied directly to a dictionary | [SearchableAttribute](https://odininspector.com/documentation/sirenix.odininspector.searchableattribute) |

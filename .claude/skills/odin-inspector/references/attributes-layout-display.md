# Layout & Display Attributes — Sirenix.OdinInspector grouping, ordering, cosmetics

Source: [BoxGroupAttribute](https://odininspector.com/documentation/sirenix.odininspector.boxgroupattribute), [FoldoutGroupAttribute](https://odininspector.com/documentation/sirenix.odininspector.foldoutgroupattribute), [HorizontalGroupAttribute](https://odininspector.com/documentation/sirenix.odininspector.horizontalgroupattribute), [VerticalGroupAttribute](https://odininspector.com/documentation/sirenix.odininspector.verticalgroupattribute), [TabGroupAttribute](https://odininspector.com/documentation/sirenix.odininspector.tabgroupattribute), [TitleGroupAttribute](https://odininspector.com/documentation/sirenix.odininspector.titlegroupattribute), [ToggleGroupAttribute](https://odininspector.com/documentation/sirenix.odininspector.togglegroupattribute), [PropertyOrderAttribute](https://odininspector.com/documentation/sirenix.odininspector.propertyorderattribute), [PropertySpaceAttribute](https://odininspector.com/documentation/sirenix.odininspector.propertyspaceattribute), [IndentAttribute](https://odininspector.com/documentation/sirenix.odininspector.indentattribute), [TitleAttribute](https://odininspector.com/documentation/sirenix.odininspector.titleattribute), [InfoBoxAttribute](https://odininspector.com/documentation/sirenix.odininspector.infoboxattribute), [DetailedInfoBoxAttribute](https://odininspector.com/documentation/sirenix.odininspector.detailedinfoboxattribute), [HideLabelAttribute](https://odininspector.com/documentation/sirenix.odininspector.hidelabelattribute), [LabelTextAttribute](https://odininspector.com/documentation/sirenix.odininspector.labeltextattribute), [LabelWidthAttribute](https://odininspector.com/documentation/sirenix.odininspector.labelwidthattribute), [GUIColorAttribute](https://odininspector.com/documentation/sirenix.odininspector.guicolorattribute), [SuffixLabelAttribute](https://odininspector.com/documentation/sirenix.odininspector.suffixlabelattribute), [PropertyTooltipAttribute](https://odininspector.com/documentation/sirenix.odininspector.propertytooltipattribute).
Covers: SKILL.md §4 — **"Route to the narrowest reference file for the concern"**.

Attributes that organize *where* and *how* a field/property/method renders in
the Inspector, without touching whether it's visible, editable, or valid
(that's [attributes-conditional-validation.md](attributes-conditional-validation.md)).
All of these are `[Conditional("UNITY_EDITOR")]` — zero runtime cost, zero
runtime effect.

## Table of contents
- [Grouping attributes](#grouping-attributes)
- [Ordering & spacing](#ordering--spacing)
- [Headers & message boxes](#headers--message-boxes)
- [Label & cosmetic attributes](#label--cosmetic-attributes)

## Grouping attributes

All grouping attributes derive from `PropertyGroupAttribute`; members sharing
the same group-name string merge into one group. Nested groups use `/` in the
group path (e.g. `"Split/Left"`).

| Attribute | Key constructor / fields | What it decides | Source |
|---|---|---|---|
| `BoxGroupAttribute(string group, bool showLabel = true, bool centerLabel = false, float order = 0)` | `CenterLabel`, `LabelText`, `ShowLabel` | Boxes members together; group name can be a literal or `"$MemberName"` for a dynamic title | [BoxGroupAttribute](https://odininspector.com/documentation/sirenix.odininspector.boxgroupattribute) |
| `FoldoutGroupAttribute(string groupName, bool expanded, float order = 0)` | `Expanded` | Collapsible group; `expanded` sets the default open/closed state | [FoldoutGroupAttribute](https://odininspector.com/documentation/sirenix.odininspector.foldoutgroupattribute) |
| `HorizontalGroupAttribute(float width = 0, int marginLeft = 0, int marginRight = 0, float order = 0)` — also `HorizontalGroupAttribute(string group, ...)` | `Width`/`MinWidth`/`MaxWidth`, `MarginLeft/Right`, `PaddingLeft/Right`, `Gap`, `Title`, `DisableAutomaticLabelWidth` | Lays members out in a row; width `0`–`1` is a percentage of available space, otherwise pixels, `0` = auto-size | [HorizontalGroupAttribute](https://odininspector.com/documentation/sirenix.odininspector.horizontalgroupattribute) |
| `VerticalGroupAttribute(string groupId, float order = 0)` | `PaddingTop`, `PaddingBottom` | Stacks members in a column — mainly useful nested inside a `HorizontalGroup` column (e.g. `"Split/Left"`) | [VerticalGroupAttribute](https://odininspector.com/documentation/sirenix.odininspector.verticalgroupattribute) |
| `TabGroupAttribute(string tab, bool useFixedHeight = false, float order = 0)` — also a `(group, tab, ...)` overload for multiple tab groups | `TabLayouting`, `Paddingless`, `HideTabGroupIfTabGroupOnlyHasOneTab`, `TextColor`, `Icon` (`SdfIconType`) | Puts members into tabs; nesting tabs inside tabs uses `"ParentGroup/Tab/InnerGroup"` as the group path | [TabGroupAttribute](https://odininspector.com/documentation/sirenix.odininspector.tabgroupattribute) |
| `TitleGroupAttribute(string title, string subtitle = null, TitleAlignments alignment = Left, bool horizontalLine = true, bool boldTitle = true, bool indent = false, float order = 0)` | `Alignment`, `BoldTitle`, `HorizontalLine`, `Indent`, `Subtitle` | Vertical group with a title/subtitle header — combine title styling with grouping in one attribute | [TitleGroupAttribute](https://odininspector.com/documentation/sirenix.odininspector.titlegroupattribute) |
| `ToggleGroupAttribute(string toggleMemberName, float order = 0, string groupTitle = null)` | `CollapseOthersOnExpand`, `ToggleGroupTitle` | Group that is entirely enabled/disabled by a `bool` member named `toggleMemberName`; static members unsupported | [ToggleGroupAttribute](https://odininspector.com/documentation/sirenix.odininspector.togglegroupattribute) |

**Critical caveat**: only apply one grouping attribute of each *kind* per
member for a given group — combining `HorizontalGroup` with a nested
`BoxGroup`/`VerticalGroup` (e.g. `[HorizontalGroup("Split")] [BoxGroup("Split/Left")]`)
is the supported way to build a multi-row layout, not stacking two
`HorizontalGroup` attributes on the same member.

## Ordering & spacing

| Attribute | Key constructor | What it decides | Source |
|---|---|---|---|
| `PropertyOrderAttribute(float order)` | `Order` | Lower values draw first; the only reliable way to force draw order, since declaration order is not guaranteed | [PropertyOrderAttribute](https://odininspector.com/documentation/sirenix.odininspector.propertyorderattribute) |
| `PropertySpaceAttribute(float spaceBefore = 8, float spaceAfter = 0)` | `SpaceBefore`, `SpaceAfter` | Adds (or, with a negative value, removes) vertical pixels between properties; works on properties/methods, unlike Unity's `Space` | [PropertySpaceAttribute](https://odininspector.com/documentation/sirenix.odininspector.propertyspaceattribute) |
| `IndentAttribute(int indentLevel = 1)` | `IndentLevel` | Shifts the member's label right by the given indent level | [IndentAttribute](https://odininspector.com/documentation/sirenix.odininspector.indentattribute) |

## Headers & message boxes

| Attribute | Key constructor | What it decides | Source |
|---|---|---|---|
| `TitleAttribute(string title, string subtitle = null, TitleAlignments titleAlignment = Left, bool horizontalLine = true, bool bold = true)` | `Bold`, `HorizontalLine`, `Subtitle`, `TitleAlignment` | Bold header above a member; title/subtitle accept `"$MemberName"` for dynamic text | [TitleAttribute](https://odininspector.com/documentation/sirenix.odininspector.titleattribute) |
| `InfoBoxAttribute(string message, InfoMessageType infoMessageType = Info, string visibleIfMemberName = null)` | `GUIAlwaysEnabled`, `IconColor` | Message box above a member; `visibleIfMemberName` names a bool field/property/method (static or instance) that hides the box when false | [InfoBoxAttribute](https://odininspector.com/documentation/sirenix.odininspector.infoboxattribute) |
| `DetailedInfoBoxAttribute(string message, string details, InfoMessageType infoMessageType = Info, string visibleIf = null)` | same as `InfoBox` plus `Details` | Same as `InfoBox` but `details` is hidden behind an expand toggle | [DetailedInfoBoxAttribute](https://odininspector.com/documentation/sirenix.odininspector.detailedinfoboxattribute) |
| `TypeInfoBoxAttribute(string message)` | `Message` | Info box at the very top of a class/struct/interface, without needing `PropertyOrder` tricks | [TypeInfoBoxAttribute](https://odininspector.com/documentation/sirenix.odininspector.typeinfoboxattribute) |

## Label & cosmetic attributes

| Attribute | Key constructor | What it decides | Source |
|---|---|---|---|
| `HideLabelAttribute()` | — | Removes the member's label entirely — common alongside `HorizontalGroup`/`PreviewField` to save horizontal space | [HideLabelAttribute](https://odininspector.com/documentation/sirenix.odininspector.hidelabelattribute) |
| `LabelTextAttribute(string text, bool nicifyText = ..., SdfIconType icon = ...)` | `Text`, `NicifyText`, `Icon`, `IconColor` | Overrides the auto-generated label; `nicifyText` re-applies Unity's "m_someField" → "Some Field" formatting to a resolved value | [LabelTextAttribute](https://odininspector.com/documentation/sirenix.odininspector.labeltextattribute) |
| `LabelWidthAttribute(float width)` | `Width` | Fixed label width in pixels — frequently paired with `HorizontalGroup` columns to keep labels from eating column width | [LabelWidthAttribute](https://odininspector.com/documentation/sirenix.odininspector.labelwidthattribute) |
| `GUIColorAttribute(float r, float g, float b, float a = 1)` — also `GUIColorAttribute(string getColor)` | `Color`, `GetColor` | Tints the member's GUI color; the string overload accepts a resolved color expression (`"GetColor"`, `"@this.MyColor"`, hex, named colors) | [GUIColorAttribute](https://odininspector.com/documentation/sirenix.odininspector.guicolorattribute) |
| `SuffixLabelAttribute(string label, bool overlay = false)` | `Label`, `Overlay`, `IconColor` | Trailing label conveying units/intent (e.g. "Prefab", "ms"); `overlay = true` draws it inside the field instead of after it | [SuffixLabelAttribute](https://odininspector.com/documentation/sirenix.odininspector.suffixlabelattribute) |
| `PropertyTooltipAttribute(string tooltip)` | `Tooltip` | Same as Unity's `Tooltip`, but works on properties too, not just fields | [PropertyTooltipAttribute](https://odininspector.com/documentation/sirenix.odininspector.propertytooltipattribute) |

**Critical caveat**: resolved-string arguments in this file (group titles via
`"$Member"`, `GUIColor`'s `getColor`, `InfoBox`'s `visibleIfMemberName`) are
reflection-resolved at edit time with no compile check — see
[attributes-conditional-validation.md](attributes-conditional-validation.md)'s
verification caveat, which applies identically here.

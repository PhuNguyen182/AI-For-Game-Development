# Layout & Display Attributes

Where and how a member renders; all Editor-only. Visibility/validity lives in [attributes-conditional-validation.md](attributes-conditional-validation.md).

## Grouping
Group attributes derive from `PropertyGroupAttribute`; members sharing a group string merge. Nest with `/` (`"Split/Left"`). Build multi-row layouts as `[HorizontalGroup("Split")]` + nested `[BoxGroup("Split/Left")]`/`VerticalGroup`, never two `HorizontalGroup`s on one member.

| Attribute | Notes |
|---|---|
| `BoxGroup(group, showLabel = true, centerLabel = false, order = 0)` | Name may be `"$Member"` for a dynamic title |
| `FoldoutGroup(groupName, expanded, order = 0)` | `expanded` = default state |
| `HorizontalGroup(width = 0, marginLeft, marginRight, order)` / `(group, ...)` | Width 0-1 = fraction of space, else pixels, 0 = auto. Also `MinWidth`, `MaxWidth`, `PaddingLeft/Right`, `Gap`, `Title`, `DisableAutomaticLabelWidth` |
| `VerticalGroup(groupId, order)` | `PaddingTop/Bottom`; mainly a column inside `HorizontalGroup` |
| `TabGroup(tab, useFixedHeight = false, order)` / `(group, tab, ...)` | Nested tabs: `"Parent/Tab/Inner"`. `Icon` (`SdfIconType`), `TextColor`, `Paddingless`, `HideTabGroupIfTabGroupOnlyHasOneTab` |
| `TitleGroup(title, subtitle, alignment, horizontalLine = true, boldTitle = true, indent = false)` | Group with title header |
| `ToggleGroup(toggleMemberName, order, groupTitle)` | Whole group enabled by a `bool` member; static members unsupported |

## Order & spacing
| Attribute | Notes |
|---|---|
| `PropertyOrder(float)` | Lower first; the only reliable way to force order |
| `PropertySpace(spaceBefore = 8, spaceAfter = 0)` | Negative removes space; works on properties/methods, unlike `Space` |
| `Indent(indentLevel = 1)` | Shifts the label right |

## Headers & message boxes
| Attribute | Notes |
|---|---|
| `Title(title, subtitle, alignment, horizontalLine, bold)` | `"$Member"` for dynamic text |
| `InfoBox(message, InfoMessageType = Info, visibleIfMemberName)` | `visibleIfMemberName` = bool field/property/method, static or instance |
| `DetailedInfoBox(message, details, type, visibleIf)` | `details` behind an expand toggle |
| `TypeInfoBox(message)` | On a class/struct/interface; top of the type, no `PropertyOrder` needed |

## Labels & cosmetics
| Attribute | Notes |
|---|---|
| `HideLabel` | Common with `HorizontalGroup`/`PreviewField` |
| `LabelText(text, nicifyText, icon)` | Overrides the label |
| `LabelWidth(float)` | Pixels; pair with `HorizontalGroup` columns |
| `GUIColor(r, g, b, a = 1)` / `(string getColor)` | String: member, `"@this.MyColor"`, hex or named colour |
| `SuffixLabel(label, overlay = false)` | `overlay` draws inside the field |
| `PropertyTooltip(tooltip)` | Unlike `Tooltip`, works on properties |

`"$Member"`, `getColor` and `visibleIfMemberName` are resolved strings: see the syntax and no-compile-check warning in [attributes-conditional-validation.md](attributes-conditional-validation.md).

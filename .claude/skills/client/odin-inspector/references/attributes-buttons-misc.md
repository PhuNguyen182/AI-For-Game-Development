# Buttons & Misc Display Attributes — Sirenix.OdinInspector actions and raw-value display

Source: [ButtonAttribute](https://odininspector.com/documentation/sirenix.odininspector.buttonattribute), [ButtonGroupAttribute](https://odininspector.com/documentation/sirenix.odininspector.buttongroupattribute), [InlineButtonAttribute](https://odininspector.com/documentation/sirenix.odininspector.inlinebuttonattribute), [CustomContextMenuAttribute](https://odininspector.com/documentation/sirenix.odininspector.customcontextmenuattribute), [ShowInInspectorAttribute](https://odininspector.com/documentation/sirenix.odininspector.showininspectorattribute), [EnumToggleButtonsAttribute](https://odininspector.com/documentation/sirenix.odininspector.enumtogglebuttonsattribute), [EnumPagingAttribute](https://odininspector.com/documentation/sirenix.odininspector.enumpagingattribute), [ToggleAttribute](https://odininspector.com/documentation/sirenix.odininspector.toggleattribute), [ToggleLeftAttribute](https://odininspector.com/documentation/sirenix.odininspector.toggleleftattribute), [DisplayAsStringAttribute](https://odininspector.com/documentation/sirenix.odininspector.displayasstringattribute), [OptionalAttribute](https://odininspector.com/documentation/sirenix.odininspector.optionalattribute).
Covers: SKILL.md §4 — **"Route to the narrowest reference file for the concern"**.

Inspector-only actions (buttons, context-menu items) and attributes that
change how a value's own type is rendered, as opposed to grouping
([attributes-layout-display.md](attributes-layout-display.md)) or gating
visibility ([attributes-conditional-validation.md](attributes-conditional-validation.md)).

## Table of contents
- [Buttons](#buttons)
- [Context menu & inspector-only display](#context-menu--inspector-only-display)
- [Enum & toggle display](#enum--toggle-display)
- [String display](#string-display)

## Buttons

`ButtonAttribute` goes on a method (any accessibility). It derives from
`ShowInInspectorAttribute`, so a button is always inspector-visible
regardless of the method's own serialization.

| Constructor overload | What it decides | Source |
|---|---|---|
| `()` | Button named after the method | [ButtonAttribute](https://odininspector.com/documentation/sirenix.odininspector.buttonattribute) |
| `(string name)` | Custom label | same |
| `(ButtonSizes size)`, `(int buttonSize)` | Fixed pixel height | same |
| `(SdfIconType icon, ...)` | Icon-only or icon+label button | same |
| `(ButtonStyle parameterBtnStyle)` | How a method *with parameters* draws its argument fields (`Box`, `FoldoutButton`, `CompactBox`) | same |

Key fields: `DirtyOnClick` (true by default — also gates Undo registration),
`DisplayParameters` (false routes invocation through an `ActionResolver`/
`ValueResolver` instead of drawing parameter fields, granting access to
contextual values like `InspectorProperty property`), `DrawResult` (draw a
method's return value below the button), `Stretch`, `ButtonAlignment`,
`Expanded` (collapse the parameter foldout).

`ButtonGroupAttribute(string group = "_DefaultGroup", float order = 0)` —
same idea as the layout `*GroupAttribute` family, but specifically for
laying multiple `[Button]` methods out horizontally in one row; shares
`ButtonHeight`/`ButtonAlignment`/`Stretch`/`IconAlignment`.
[Source](https://odininspector.com/documentation/sirenix.odininspector.buttongroupattribute)

`InlineButtonAttribute(string action, string label = null)` — draws a small
button to the right of a *property* (not a method) that invokes a resolved
action; `ShowIf` lets it conditionally hide. Multiple inline buttons on the
same member are not supported.
[Source](https://odininspector.com/documentation/sirenix.odininspector.inlinebuttonattribute)

## Context menu & inspector-only display

| Attribute | Constructor | What it decides | Source |
|---|---|---|---|
| `CustomContextMenuAttribute` | `(string menuItem, string action)` | Adds a custom entry to a member's right-click context menu; static functions unsupported | [CustomContextMenuAttribute](https://odininspector.com/documentation/sirenix.odininspector.customcontextmenuattribute) |
| `ShowInInspectorAttribute()` | — | Shows a non-serialized field/property/method's *current value* in the Inspector — display only, this does **not** make the value persist; combine with `[ReadOnly]` for live runtime debugging | [ShowInInspectorAttribute](https://odininspector.com/documentation/sirenix.odininspector.showininspectorattribute) |

## Enum & toggle display

| Attribute | What it decides | Source |
|---|---|---|
| `EnumToggleButtonsAttribute()` | Renders an enum as a horizontal button group instead of a dropdown; on a `[Flags]` enum, buttons act as independent toggles | [EnumToggleButtonsAttribute](https://odininspector.com/documentation/sirenix.odininspector.enumtogglebuttonsattribute) |
| `EnumPagingAttribute()` | Renders an enum with next/previous cycle buttons instead of a dropdown | [EnumPagingAttribute](https://odininspector.com/documentation/sirenix.odininspector.enumpagingattribute) |
| `ToggleAttribute(string toggleMemberName)` | Makes a whole nested object's fields collapse/grey out based on a `bool` member on *that nested object* — the object-level counterpart to `ToggleGroupAttribute` in [attributes-layout-display.md](attributes-layout-display.md); static members unsupported | [ToggleAttribute](https://odininspector.com/documentation/sirenix.odininspector.toggleattribute) |
| `ToggleLeftAttribute()` | Draws a `bool`'s checkbox before its label instead of after | [ToggleLeftAttribute](https://odininspector.com/documentation/sirenix.odininspector.toggleleftattribute) |
| `OptionalAttribute()` | Marks a field exempt from Odin Validator's "Reference Required by Default" rule — a no-op unless that Validator rule is active | [OptionalAttribute](https://odininspector.com/documentation/sirenix.odininspector.optionalattribute) |

## String display

`DisplayAsStringAttribute` renders a `string` (via its `ToString()`) as
read-only text instead of an editable field.

| Constructor overload | What it decides | Source |
|---|---|---|
| `()` | Default read-only text | [DisplayAsStringAttribute](https://odininspector.com/documentation/sirenix.odininspector.displayasstringattribute) |
| `(bool overflow)` | `overflow = false` wraps to multiple lines instead of clipping long text | same |
| `(bool overflow, int fontSize, ...)` | Font size, and optionally `TextAlignment` and rich-text support | same |

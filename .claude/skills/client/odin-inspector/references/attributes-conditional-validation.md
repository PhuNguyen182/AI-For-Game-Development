# Conditional & Validation Attributes — Sirenix.OdinInspector state-dependent behavior

Source: [ShowIfAttribute](https://odininspector.com/documentation/sirenix.odininspector.showifattribute), [HideIfAttribute](https://odininspector.com/documentation/sirenix.odininspector.hideifattribute), [EnableIfAttribute](https://odininspector.com/documentation/sirenix.odininspector.enableifattribute), [DisableIfAttribute](https://odininspector.com/documentation/sirenix.odininspector.disableifattribute), [DisableInPlayModeAttribute](https://odininspector.com/documentation/sirenix.odininspector.disableinplaymodeattribute), [HideInPlayModeAttribute](https://odininspector.com/documentation/sirenix.odininspector.hideinplaymodeattribute), [RequiredAttribute](https://odininspector.com/documentation/sirenix.odininspector.requiredattribute), [ValidateInputAttribute](https://odininspector.com/documentation/sirenix.odininspector.validateinputattribute), [OnValueChangedAttribute](https://odininspector.com/documentation/sirenix.odininspector.onvaluechangedattribute), [MinValueAttribute](https://odininspector.com/documentation/sirenix.odininspector.minvalueattribute), [MaxValueAttribute](https://odininspector.com/documentation/sirenix.odininspector.maxvalueattribute), [PropertyRangeAttribute](https://odininspector.com/documentation/sirenix.odininspector.propertyrangeattribute), [MinMaxSliderAttribute](https://odininspector.com/documentation/sirenix.odininspector.minmaxsliderattribute), [WrapAttribute](https://odininspector.com/documentation/sirenix.odininspector.wrapattribute), [UnitAttribute](https://odininspector.com/documentation/sirenix.odininspector.unitattribute), [ReadOnlyAttribute](https://odininspector.com/documentation/sirenix.odininspector.readonlyattribute), [DelayedPropertyAttribute](https://odininspector.com/documentation/sirenix.odininspector.delayedpropertyattribute).
Covers: SKILL.md §4 — **"Route to the narrowest reference file for the concern"**, **"Verify every resolved-string argument names a real member before shipping"**.

Attributes that make a member's visibility, editability, legality, or a
side-effect callback depend on other state. Every attribute here is
Editor-only — none of it enforces anything at runtime; see SKILL.md §4's
"Confirm the task is Inspector/editor tooling, not gameplay logic" step.

## Table of contents
- [Show/hide/enable/disable by condition](#showhideenabledisable-by-condition)
- [Play-mode gating](#play-mode-gating)
- [Required & validation](#required--validation)
- [Numeric constraints & units](#numeric-constraints--units)
- [Resolved-string condition syntax](#resolved-string-condition-syntax)

## Show/hide/enable/disable by condition

All four share the same two constructor shapes and the same resolution rule.

| Attribute | Constructors | Fields | Source |
|---|---|---|---|
| `ShowIfAttribute` | `(string condition, bool animate = true)`; `(string condition, object optionalValue, bool animate = true)` | `Condition`, `Value`, `Animate` | [ShowIfAttribute](https://odininspector.com/documentation/sirenix.odininspector.showifattribute) |
| `HideIfAttribute` | same two shapes | same fields | [HideIfAttribute](https://odininspector.com/documentation/sirenix.odininspector.hideifattribute) |
| `EnableIfAttribute` | `(string condition)` plus an optional-value overload | `Condition` | [EnableIfAttribute](https://odininspector.com/documentation/sirenix.odininspector.enableifattribute) |
| `DisableIfAttribute` | `(string condition)` plus an optional-value overload | `Condition` | [DisableIfAttribute](https://odininspector.com/documentation/sirenix.odininspector.disableifattribute) |

`condition` resolves to a bool member/method/expression by name; with the
`optionalValue` overload, the attribute instead compares the condition
member's value against `optionalValue` (useful for enum members: e.g.
`[ShowIf("state", MyEnum.Attacking)]`). `ShowIf`/`HideIf`'s `animate` slides
the member in/out instead of an instant toggle.

## Play-mode gating

| Attribute | Effect | Source |
|---|---|---|
| `DisableInPlayModeAttribute()` | Greys out the member while the game is playing in the Editor | [DisableInPlayModeAttribute](https://odininspector.com/documentation/sirenix.odininspector.disableinplaymodeattribute) |
| `HideInPlayModeAttribute()` | Hides the member entirely while the game is playing in the Editor | [HideInPlayModeAttribute](https://odininspector.com/documentation/sirenix.odininspector.hideinplaymodeattribute) |

## Required & validation

| Attribute | Constructor | Fields | What it decides | Source |
|---|---|---|---|---|
| `RequiredAttribute` | `()`, `(InfoMessageType)`, `(string errorMessage)`, `(string errorMessage, InfoMessageType)` | `ErrorMessage`, `MessageType` | Draws an error/warning/info box when an object reference is missing (`null`) — Inspector-only, does not throw or block Play mode | [RequiredAttribute](https://odininspector.com/documentation/sirenix.odininspector.requiredattribute) |
| `ValidateInputAttribute` | `(string condition, string defaultMessage = null, InfoMessageType messageType = Error)` | `Condition`, `ContinuousValidationCheck`, `IncludeChildren`, `DefaultMessage`, `MessageType` | Runs a resolved bool-returning condition against the value on every edit; **refuses the edit** if it returns false — the value reverts. Only fires from Inspector edits, never from script | [ValidateInputAttribute](https://odininspector.com/documentation/sirenix.odininspector.validateinputattribute) |
| `OnValueChangedAttribute` | `(string action, bool includeChildren = false)` | `Action`, `IncludeChildren`, `InvokeOnInitialize`, `InvokeOnUndoRedo` | Calls a resolved method after the Inspector changes the value — Editor-only, never fires for script-driven changes | [OnValueChangedAttribute](https://odininspector.com/documentation/sirenix.odininspector.onvaluechangedattribute) |

**Critical caveat**: `ValidateInput` *rejects* invalid Inspector edits
in-editor (the field visibly reverts), which can read like real enforcement —
it is not. A value set via script, a save file, or over the network is never
checked. Any invariant that must hold at runtime is a `Game.Core.*` concern.

## Numeric constraints & units

| Attribute | Constructor(s) | What it decides | Source |
|---|---|---|---|
| `MinValueAttribute` | `(double minValue)`; `(string expression)` | Caps the field to a minimum in the Inspector only — script-set values are not clamped | [MinValueAttribute](https://odininspector.com/documentation/sirenix.odininspector.minvalueattribute) |
| `MaxValueAttribute` | `(double maxValue)`; `(string expression)` | Same, as a maximum | [MaxValueAttribute](https://odininspector.com/documentation/sirenix.odininspector.maxvalueattribute) |
| `PropertyRangeAttribute` | `(double min, double max)` plus getter-string overloads for either bound | Slider control equivalent to Unity's `Range`, but works on properties too | [PropertyRangeAttribute](https://odininspector.com/documentation/sirenix.odininspector.propertyrangeattribute) |
| `MinMaxSliderAttribute` | `(float minValue, float maxValue, bool showFields = false)` plus string-getter overloads, or `(string minMaxValueGetter, bool showFields = false)` for a single `Vector2` bounds source | Draws a dual-handle range slider on a `Vector2` (`x` = min, `y` = max) | [MinMaxSliderAttribute](https://odininspector.com/documentation/sirenix.odininspector.minmaxsliderattribute) |
| `WrapAttribute` | `(double min, double max)` | Wraps the value around instead of clamping (e.g. an angle field) — unsigned primitives unsupported | [WrapAttribute](https://odininspector.com/documentation/sirenix.odininspector.wrapattribute) |
| `UnitAttribute` | `(Units unit)`; `(Units base, Units display)`; string variants for custom unit names | Displays/converts a numeric field between a base unit and a display unit (e.g. store meters, display feet) | [UnitAttribute](https://odininspector.com/documentation/sirenix.odininspector.unitattribute) |
| `ReadOnlyAttribute()` | — | Prevents Inspector edits entirely (script writes still work); combine with `[ShowInInspector]` to display a private field read-only | [ReadOnlyAttribute](https://odininspector.com/documentation/sirenix.odininspector.readonlyattribute) |
| `DelayedPropertyAttribute()` | — | Defers applying an edit until focus leaves the field or Enter is pressed — Unity's `Delayed`, but works on properties too | [DelayedPropertyAttribute](https://odininspector.com/documentation/sirenix.odininspector.delayedpropertyattribute) |

## Resolved-string condition syntax

Every `condition`/`action`/getter string above resolves the same way: a bare
name (`"speed"`) refers to a field, auto-property, or parameterless method on
the same object (instance or static); an expression prefixed `@` evaluates
Odin's expression syntax directly (e.g. `"@this.Health <= 0"`); a `$`-prefixed
name inside a *string* argument (as in `LabelText`/`Title`) substitutes that
member's value. None of this is checked at compile time — a typo compiles
clean and silently no-ops in the Inspector. Re-run the Inspector for the
decorated type after any rename that touches a referenced member name.

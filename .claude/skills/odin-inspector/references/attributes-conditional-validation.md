# Conditional & Validation Attributes

State-dependent behaviour. Editor-only: nothing here enforces anything at runtime or on script/save/network writes.

## Show / hide / enable / disable
`ShowIf`, `HideIf`: `(string condition, bool animate = true)` or `(string condition, object optionalValue, bool animate = true)`. `EnableIf`, `DisableIf`: `(string condition)` plus an `optionalValue` overload. With `optionalValue` the member's value is compared to it, e.g. `[ShowIf("state", MyEnum.Attacking)]`.

| Attribute | Effect |
|---|---|
| `DisableInPlayMode` / `HideInPlayMode` | Greys out / hides while the Editor is playing |

## Required & validation
| Attribute | Notes |
|---|---|
| `Required` `()`, `(InfoMessageType)`, `(string errorMessage[, type])` | Error/warning box for a null reference; does not block Play |
| `ValidateInput(condition, defaultMessage, messageType = Error)` | Bool-returning check on each Inspector edit; a false result reverts the edit. Looks like enforcement but is not: script, save and network values are never checked. Fields `ContinuousValidationCheck`, `IncludeChildren` |
| `OnValueChanged(action, includeChildren = false)` | Calls a method after an Inspector change only. Fields `InvokeOnInitialize`, `InvokeOnUndoRedo` |

## Numeric
| Attribute | Notes |
|---|---|
| `MinValue` / `MaxValue` `(double)` or `(string expression)` | Inspector-only clamp |
| `PropertyRange(min, max)` + getter-string overloads | Slider; works on properties |
| `MinMaxSlider(min, max, showFields = false)` or `(string minMaxGetter, showFields)` | Dual-handle slider on a `Vector2` (x = min, y = max) |
| `Wrap(min, max)` | Wraps instead of clamping; unsigned primitives unsupported |
| `Unit(Units)`, `(Units base, Units display)`, string variants | Store one unit, display another |
| `ReadOnly` | Blocks Inspector edits only; with `[ShowInInspector]` shows a private field read-only |
| `DelayedProperty` | Applies on focus loss/Enter; works on properties |

## Resolved-string syntax
Applies to every `condition`/`action`/getter string in Odin attributes.
- Bare name (`"speed"`): field, auto-property or parameterless method on the same object, instance or static.
- `@` prefix: Odin expression, e.g. `"@this.Health <= 0"`.
- `$Member` inside a text argument (`LabelText`, `Title`): substitutes the member's value.
- No compile-time check: a typo or rename silently no-ops.

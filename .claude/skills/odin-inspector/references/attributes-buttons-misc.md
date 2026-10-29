# Buttons & Misc Display Attributes

## Button
`[Button]` goes on a method of any accessibility; it derives from `ShowInInspector`, so it is always visible.

| Overload | Effect |
|---|---|
| `()` | Named after the method |
| `(string name)` | Custom label |
| `(ButtonSizes)`, `(int buttonSize)` | Pixel height |
| `(SdfIconType icon, ...)` | Icon or icon+label |
| `(ButtonStyle)` | How parameter fields draw: `Box`, `FoldoutButton`, `CompactBox` |

Fields: `DirtyOnClick` (true; also gates Undo registration), `DisplayParameters` (false resolves the call via `ActionResolver`/`ValueResolver`, giving access to context such as `InspectorProperty property`), `DrawResult` (draw the return value), `Stretch`, `ButtonAlignment`, `Expanded`.

- `ButtonGroup(group = "_DefaultGroup", order)`: lays several `[Button]`s in one row. `ButtonHeight`, `ButtonAlignment`, `Stretch`, `IconAlignment`.
- `InlineButton(action, label)`: small button right of a property (not a method) invoking a resolved action. Only one per member.

## Context menu & inspector-only display
| Attribute | Notes |
|---|---|
| `CustomContextMenu(menuItem, action)` | Right-click entry; static functions unsupported |
| `ShowInInspector` | Shows a non-serialized member's current value; does not persist it. With `[ReadOnly]` for live debugging |

## Enum, toggle, string
| Attribute | Notes |
|---|---|
| `EnumToggleButtons` | Horizontal buttons; independent toggles on `[Flags]` |
| `EnumPaging` | Next/previous cycling |
| `Toggle(toggleMemberName)` | Collapses/greys a nested object by a `bool` on that object; object-level counterpart of `ToggleGroup`; static members unsupported |
| `ToggleLeft` | Checkbox before the label |
| `Optional` | Exempts a field from Odin Validator's "Reference Required by Default"; no-op unless that rule is active |
| `DisplayAsString` `()`, `(bool overflow)`, `(bool overflow, int fontSize, ...)` | Read-only text via `ToString()`; `overflow = false` wraps; also alignment and rich text |

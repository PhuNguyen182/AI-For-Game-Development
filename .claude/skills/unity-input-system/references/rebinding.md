# Rebinding

Docs (1.20 manual): `user-rebinding-runtime`, `rebind-action-runtime`, `save-load-rebinds`, `display-bindings`, `restore-original-bindings`. Menu layout: `gameplay-engineer`. The package ships a rebinding UI sample (listen, cancel, persist); start from it.

## Interactive operation
| Member | Note |
|---|---|
| `PerformInteractiveRebinding()` | Listens and writes the actuated control onto the binding |
| `WithControlsExcluding(path)` | Exclude the mouse for key/button rebinds, or stray motion captures itself |
| `WithCancelingThrough(path)` | Always set one, or the player cannot back out |
| `WithExpectedControlType(type)` | Stops an axis binding where a button is meant |
| `WithTargetBinding(index)` / masks | Pick the binding of a keyboard+gamepad action that receives the path |

The operation is `IDisposable` and not cleaned up for you: dispose it on complete and cancel (`using`/explicit dispose, per `csharp-standards` → `coding-principles.md` Exception handling).

## Overrides
- Apply override: non-destructive, authored binding stays underneath.
- Remove override: what reset-to-default does.
- Display string for a binding: human-readable label, no hand-mapped glyph names.

## Persistence
- Save overrides as JSON: only the override layer, so later asset edits still reach players who rebound.
- Load overrides clears existing ones unless told not to: an earlier override vanishes silently.
- Key storage per player index or profile; one shared key lets the last player overwrite everyone.

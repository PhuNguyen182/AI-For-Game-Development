# Command Pattern via ScriptableObject

Sources: Manual `class-ScriptableObject.html`; `ScriptableObject.CreateInstance`. Synthesized from the GoF Command pattern; no single canonical Unity page.

`abstract class CommandSO : ScriptableObject` with `abstract void Execute()` and optional `virtual void Undo()`. An invoker holds a `Queue<CommandSO>` / `Stack<CommandSO>` for input remapping, replay, or undo/redo, decoupling the trigger from the action.

| | Designer-authored asset | `CreateInstance<T>()` at runtime |
|---|---|---|
| Lifetime | Project asset, reused | Created and discarded per invocation; a plain in-memory object |
| Config | Inspector, design time | Set in code right after creation (per-invocation target or amount) |
| Shared-state risk | Like any shared SO ([dual-serialization.md](dual-serialization.md)) if it stores per-invocation state | None |

- Target binding example: `MoveCommandSO` with `[SerializeField] float distance`, `Bind(ICharacterMotor)`, `Execute()` saving `previousPosition` then `motor.MoveBy(distance)`, `Undo()` calling `motor.MoveTo(previousPosition)`.
- `Execute`/`Undo` decide when an action runs and whether it can be undone. The state change itself goes through an interface backed by `Game.Core.*`; a command that computes movement or any server-validated rule itself reimplements Core.
- Never `AssetDatabase.CreateAsset` a runtime-created command.

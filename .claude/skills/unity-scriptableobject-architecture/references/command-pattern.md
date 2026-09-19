# The Command Pattern via ScriptableObject

Sources: [ScriptableObject](https://docs.unity3d.com/Manual/class-ScriptableObject.html), [ScriptableObject.CreateInstance](https://docs.unity3d.com/ScriptReference/ScriptableObject.CreateInstance.html). Not sourced from a single canonical page beyond these — synthesized from the classic Command design pattern (GoF) applied to ScriptableObject-based Unity architecture.
Covers: SKILL.md §4 — **"Reach for the Command Pattern when an action must be queued, replayed, or undone"**.

A Command SO encapsulates one executable action as data plus an
`Execute()`/`Undo()` pair, instead of the caller invoking the action directly.
Because it's an SO, a command can be authored as a designer-configurable asset
(a `MoveCommandSO` with a configurable distance) or created at runtime via
`ScriptableObject.CreateInstance<T>()` for one that must carry per-invocation
data.

## Shape

| Member | Effect | Use when | Source |
|---|---|---|---|
| `abstract class CommandSO : ScriptableObject` with `abstract void Execute()` (+ optional `virtual void Undo()`) | The contract every command implements | An action needs to be queued, logged, or undone rather than called inline | synthesized |
| `Queue<CommandSO>`/`Stack<CommandSO>` held by an invoker (e.g. `InputCommandInvoker`) | Decouples "what triggers the action" from "what the action does" | Input remapping, replay systems, undo/redo in an editor tool | `coding-principles.md`'s Dependency Inversion section |
| Runtime instance via `ScriptableObject.CreateInstance<TargetedCommandSO>()`, fields set post-creation | A command with per-invocation data (a specific target, a specific amount) rather than fixed config | The same command "kind" needs different data per use, so one designer-authored asset can't hold it | [ScriptableObject.CreateInstance](https://docs.unity3d.com/ScriptReference/ScriptableObject.CreateInstance.html) |

## Code shape

```csharp
public abstract class CommandSO : ScriptableObject
{
    public abstract void Execute();

    public virtual void Undo()
    {
    }
}

[CreateAssetMenu(menuName = "Commands/Move", fileName = "SO_MoveCommand")]
public class MoveCommandSO : CommandSO
{
    [SerializeField] private float distance;

    private ICharacterMotor motor;
    private Vector3 previousPosition;

    public void Bind(ICharacterMotor targetMotor)
    {
        this.motor = targetMotor;
    }

    public override void Execute()
    {
        this.previousPosition = this.motor.Position;
        this.motor.MoveBy(this.distance);
    }

    public override void Undo()
    {
        this.motor.MoveTo(this.previousPosition);
    }
}
```

## Designer-authored asset vs runtime instance

| Concern | Designer-authored asset | `CreateInstance` at runtime | Source |
|---|---|---|---|
| Lifetime | Lives in the project, reused across invocations | Created and discarded per invocation, a plain C# object at that point | [ScriptableObject.CreateInstance](https://docs.unity3d.com/ScriptReference/ScriptableObject.CreateInstance.html) |
| Configuration | Fixed at design time via the Inspector | Set in code immediately after `CreateInstance` | synthesized |
| Shared-state risk | Same risk as any other shared SO — see [dual-serialization.md](dual-serialization.md) if it stores per-invocation state | None — it's a fresh instance each time | synthesized |

**Critical caveat**: `Execute()`/`Undo()` orchestrate *when* an action runs
and *whether it can be undone*; the actual state change (`MoveBy`, its
collision resolution, any rule the server must also validate) is called
through an interface (`ICharacterMotor`) backed by `Game.Core.*` logic — a
Command SO that computes the movement itself, instead of delegating it,
reimplements a rule outside Core, per `coding-principles.md`'s Shared Core
integrity section. A command created via `CreateInstance` at runtime is a
plain in-memory object, not a project asset — never `AssetDatabase.CreateAsset`
it into the project by accident.

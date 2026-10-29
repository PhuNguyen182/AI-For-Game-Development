---
name: unity-scriptableobject-architecture
description: "ScriptableObject architecture: Variable/Reference SOs, GameEvent and EventChannelSO, RuntimeSetSO, Delegate Object strategy, Extendable Enum, CommandSO, ISerializationCallbackReceiver reset. Use for designer-wired asset-based decoupling."
user-invocable: false
---

# Unity ScriptableObject Architecture

Not for: the game rule an SO delegates to (`csharp-engineer`'s Shared Core), Inspector styling of an SO field (`odin-inspector`), MessagePipe/R3 messaging (`messagepipe-event-messaging`, `r3-reactive-extensions`), DI composition (`vcontainer-dependency-injection`), states with legal transitions (`stateless-state-machines`).
Docs: https://docs.unity3d.com/Manual/class-ScriptableObject.html and `script-Serialization.html`, `DomainReloading.html`; unversioned. Patterns are community architecture (Ryan Hipple, Unite Austin 2017), not an official subsystem.

| Reference | Read when |
|---|---|
| [data-containers-and-variables.md](references/data-containers-and-variables.md) | Constants duplicated across prefabs or scripts |
| [delegate-objects-and-pluggable-behavior.md](references/delegate-objects-and-pluggable-behavior.md) | Behavior must vary by asset choice, or a `switch` on an enum keeps growing cases designers should add |
| [events.md](references/events.md) | Systems must notify each other without references; choosing GameEvent vs Event Channel |
| [command-pattern.md](references/command-pattern.md) | An action must be queued, replayed, remapped, or undone |
| [runtime-set-pattern.md](references/runtime-set-pattern.md) | Tracking active instances without a singleton or `FindObjectsOfType` |
| [dual-serialization.md](references/dual-serialization.md) | Any SO field is written at runtime |

## Steps
1. **An SO is `UnityEngine`-bound, so it never lives in `Game.Core.*`.** Rule logic (damage formula, drop table, score increment) stays in Core and the SO calls it; an SO method that reimplements a rule is the defect.
2. **Pick the pattern from the requirement** using the Read-when column. If two fit equally (GameEvent vs Event Channel, Delegate Object vs Extendable Enum) → `Needs-decision`, `Next: technical-architect`: the wrong shape is costly to unwind once systems depend on it. Event Channel only when the asset-based, Inspector-referenceable shape is the reason; otherwise MessagePipe/R3.
3. **Apply [dual-serialization.md](references/dual-serialization.md) to every SO field written at runtime** (Variables, Runtime Sets).
4. **Pair every registration with its removal**: Runtime Set `Add`/`Remove` and channel `+=`/`-=` in `OnEnable`/`OnDisable`.
5. **Replace `FindObjectOfType` and singletons with a Runtime Set or Event Channel** where one fits (`csharp-standards`: no runtime `Find`).
6. **Name assets `SO_Name` and serialized fields camelCase** (`csharp-standards` `naming-convention.md`).

## Output
```
## ScriptableObject Architecture — <feature>
- Pattern(s): <...>
- Assets: <SO_Name assets, CreateAssetMenu path>
- Core boundary: <SO delegates to Game.Core.*, rule not reimplemented>
- Lifecycle: <registration pairing, dual-serialization reset, growth check>
- Known limitations: <...>
```
On request only, add `Latent concerns` and `Future remediation`, each with its trigger.

## Example
- "Put the score increment straight in the GameEvent listener's UnityEvent" → declined the placement: built the `GameEvent`/`GameEventListener`, but the response calls the `Game.Core.*` scoring API instead of computing the increment.

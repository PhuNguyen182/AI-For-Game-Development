---
name: unity-scriptableobject-architecture
description: >
  ScriptableObject-driven architecture: `[CreateAssetMenu]` Data Container
  and Variable/Reference SOs, abstract Delegate Object strategies,
  `GameEvent`/`GameEventListener` Observer-pattern events, typed
  `EventChannelSO<T>` channels, Extendable Enums (an asset per case instead
  of a C# enum), the Command pattern's `CommandSO.Execute()`/`Undo()`, the
  Runtime Set pattern for tracking active instances, and Dual Serialization
  via `ISerializationCallbackReceiver.OnAfterDeserialize` to reset runtime
  state on domain reload. Use when designing an asset-based,
  Inspector-wireable decoupling layer instead of singletons,
  `FindObjectOfType`, or hardwired references. Not for: the game-rule logic
  an SO delegates to (`csharp-engineer`'s Shared Core), Inspector-attribute
  styling of an existing SO field (`odin-inspector`), MessagePipe/R3
  messaging (`messagepipe-event-messaging`, `r3-reactive-extensions`), DI
  composition/lifetime (`vcontainer-dependency-injection`).
---

# Unity ScriptableObject Architecture — Data, Delegation & Decoupling Patterns

## Bundled resources

### References
Read-only context, loaded on demand so this file stays short.

| File | Contents | Read when |
|---|---|---|
| [root-links.md](references/root-links.md) | Documentation roots this skill was built from, and the pattern's community provenance | Starting any task here, or confirming a fact against the live Manual/Scripting API |
| [data-containers-and-variables.md](references/data-containers-and-variables.md) | Data Container SOs, Variable SOs (`FloatVariable`), the `FloatReference` wrapper struct | Removing duplicated constants scattered across prefabs or scripts |
| [delegate-objects-and-pluggable-behavior.md](references/delegate-objects-and-pluggable-behavior.md) | Abstract SO + concrete-subclass Strategy pattern for swappable algorithms | A behavior must vary by design-time asset choice, not by a code branch |
| [observer-pattern-so-events.md](references/observer-pattern-so-events.md) | `GameEvent`/`GameEventListener`, `UnityEvent`-driven Inspector wiring | Few, designer-authored, Inspector-wireable reactions with no payload |
| [event-channels.md](references/event-channels.md) | `EventChannelSO<T>`, C#-`event`-subscribed cross-scene decoupling | Many code-driven subscribers, or a typed payload the event must carry |
| [extendable-enums.md](references/extendable-enums.md) | Asset-per-case categories replacing a closed C# `enum` | A `switch` on an enum keeps growing a case designers should be able to add |
| [command-pattern.md](references/command-pattern.md) | `CommandSO.Execute()`/`Undo()`, designer-authored vs `CreateInstance` commands | An action must be queued, replayed, remapped, or undone |
| [runtime-set-pattern.md](references/runtime-set-pattern.md) | `RuntimeSetSO<T>`, `OnEnable`/`OnDisable` self-registration | Tracking a dynamic population of active instances without a singleton |
| [dual-serialization.md](references/dual-serialization.md) | `ISerializationCallbackReceiver`, serialized-default vs runtime-value split | Any SO field is written to at runtime, not just read |

## 1. Objective
Design and implement ScriptableObject-based architecture — data containers,
delegate objects, Observer-pattern events, event channels, extendable enums,
commands, runtime sets, and dual serialization — that removes duplicated
constants, decouples systems without singletons or `FindObjectOfType`, and
lets designers reconfigure behavior via assets, without ever letting a
ScriptableObject reimplement a game rule that belongs in `Game.Core.*`, and
without letting a shared asset's runtime mutation silently leak between Play
sessions.

## 2. Role
Act as the ScriptableObject architecture specialist for the client track —
the tool reached for whenever a feature needs an asset-based decoupling layer
between systems, or a designer-configurable swap point for data or behavior,
inside `Game.Client.*`.

## 3. When to invoke this skill
- Removing a constant or config value duplicated across several prefabs, scenes, or scripts.
- A behavior (targeting, AI decision, drop-table roll) should be swappable per prefab by reassigning an asset, not by branching in code.
- A system needs to notify others without holding a reference to them — from a single designer-wired reaction up to a typed, code-subscribed cross-scene channel.
- A fixed C# `enum` keeps growing a `switch` branch per new case that a designer, not a programmer, should be able to add.
- An action needs to be queued, replayed, remapped, or undone rather than invoked directly.
- A dynamic population of active instances (enemies, pickups, spawn points) needs to be queried without a singleton manager or a per-frame `FindObjectsOfType` scan.
- An existing SO asset's field is mutated at runtime and needs to reset cleanly between Play sessions.
- Negative trigger: the actual formula, drop table, or state-transition rule an SO's method would delegate to — that decision lives in `Game.Core.*` per `coding-principles.md`'s Shared Core integrity section, owned by `csharp-engineer`.
- Negative trigger: decorating an existing SO field's Inspector presentation (grouping, conditional visibility, custom drawers) — that's `odin-inspector`; this skill only decides the SO's architecture, not how its fields render.
- Negative trigger: a messaging/reactive-stream requirement already served by MessagePipe or R3 — that's `messagepipe-event-messaging`/`r3-reactive-extensions`; reach for an Event Channel SO only when the asset-based, Inspector-referenceable shape is the actual reason, not by default.
- Negative trigger: how a dependency reaches a MonoBehaviour or its lifetime scope — that's `vcontainer-dependency-injection`; an SO reference assigned in the Inspector is not itself a DI concern.

## 4. How to use this skill
1. **Settle the Shared Core boundary before writing any ScriptableObject method** — an SO carries `UnityEngine.ScriptableObject`, so it can never live in `Game.Core.*`; any decision-making logic inside it (a damage formula, a drop table) still belongs in `Game.Core.*`, called from the SO rather than reimplemented inside it, per `coding-principles.md`'s Shared Core integrity section.
2. **Use a Data Container/Variable SO to remove duplicated constants across prefabs or scenes**, per [data-containers-and-variables.md](references/data-containers-and-variables.md) — a value edited once in the asset instead of N times.
3. **Use a Delegate Object SO for pluggable/strategy behavior swapped without new code**, per [delegate-objects-and-pluggable-behavior.md](references/delegate-objects-and-pluggable-behavior.md), satisfying Open/Closed instead of growing a `switch` on a behavior-type enum.
4. **Pick GameEvent/GameEventListener over an Event Channel only when the emitter has few, Editor-wireable, UnityEvent-driven listeners**, per [observer-pattern-so-events.md](references/observer-pattern-so-events.md); reach for [event-channels.md](references/event-channels.md) instead once the emitter needs a typed payload, C#-`Action`-based subscribers, or many independent listeners across scenes.
5. **Replace a growing `switch` on a fixed enum with an Extendable Enum once new cases must be added without editing the switch**, per [extendable-enums.md](references/extendable-enums.md) — the same Open/Closed reasoning `stateless-state-machines` applies to explicit states.
6. **Reach for the Command Pattern when an action must be queued, replayed, or undone**, per [command-pattern.md](references/command-pattern.md), rather than invoking the action directly.
7. **Track a dynamic population of active instances with a Runtime Set instead of `FindObjectsOfType` or a singleton manager**, per [runtime-set-pattern.md](references/runtime-set-pattern.md) and `coding-principles.md`'s ban on runtime `Find`.
8. **Apply Dual Serialization to every SO asset carrying runtime-mutable state**, per [dual-serialization.md](references/dual-serialization.md), so a Play-mode-only value never leaks into the serialized asset between sessions.
9. **Name every SO asset and its serialized fields per `naming-convention.md`** — `SO_Name` for the asset, camelCase for its Inspector-serialized fields, regardless of which pattern is applied.
10. **Ask which pattern applies rather than guessing** when two patterns look equally viable for the same requirement (most often Observer event vs Event Channel, or Delegate Object vs Extendable Enum) — the wrong shape is expensive to unwind once other systems depend on it.

## 5. Specific goals / tasks this skill performs
- Designing and implementing a Data Container or Variable/Reference SO to collapse duplicated constants into one edited asset.
- Designing an abstract Delegate Object base and its concrete Strategy-pattern subclasses.
- Building a GameEvent/GameEventListener pair or a generic Event Channel, and deciding which one a given requirement needs.
- Replacing a closed C# enum with an Extendable Enum asset-per-case structure.
- Implementing a Command SO with `Execute()`/`Undo()`, including the designer-authored-asset vs `CreateInstance`-at-runtime distinction.
- Implementing a Runtime Set with correct `OnEnable`/`OnDisable` self-registration.
- Applying Dual Serialization to any SO field mutated at runtime.
- Out of scope: the game-rule logic behind any of these patterns' decision points (`csharp-engineer`), Inspector-attribute presentation of an existing SO field (`odin-inspector`), MessagePipe/R3 messaging infrastructure (`messagepipe-event-messaging`, `r3-reactive-extensions`), DI wiring and lifetime scope (`vcontainer-dependency-injection`).

## 6. Output format
```
## ScriptableObject Architecture Work — <feature/system name>
- Pattern(s) applied: <Data Container / Variable / Delegate Object / Observer Event / Event Channel / Extendable Enum / Command / Runtime Set / Dual Serialization>
- Asset(s): <SO_Name assets created/edited, CreateAssetMenu path>
- Shared Core boundary: <confirmed the SO delegates to Game.Core.* rather than reimplementing a rule>
- Lifecycle discipline: <OnEnable/OnDisable registration, dual-serialization reset, unbounded-growth check>
- Layer: Game.Client.*
- Known limitations: <...>
```

**Extended report — emit ONLY when the requester asks for it.** It replaces
the one-line `Known limitations` above with all three fields:
```
- Known limitations: <what the delivered solution does not cover — omit this line entirely if there are genuinely none>
- Latent concerns: <assumptions holding only under current volume/convention — e.g. Runtime Set count, subscriber count>
- Future remediation: <the concrete fix for each, and its trigger condition>
```

## 7. Examples
**Example 1**
- Input: max health and move speed are copy-pasted across five enemy prefabs and drift out of sync whenever one is tuned.
- Output: `FloatVariable`/`IntVariable` Data Container SOs (`SO_EnemyMaxHealth`, `SO_EnemyMoveSpeed`) referenced by all five prefabs, per [data-containers-and-variables.md](references/data-containers-and-variables.md) — one asset edited once instead of five prefabs edited independently.

**Example 2**
- Input: "just make a GameEvent SO for the enemy-died event and put the score increment straight in the listener's UnityEvent."
- Output: declined the score math placement — a score increment is a game rule and belongs in `Game.Core.*`'s scoring API; built the `GameEvent`/`GameEventListener` per [observer-pattern-so-events.md](references/observer-pattern-so-events.md), but the listener's response calls into the Core scoring API rather than computing the increment itself, per `coding-principles.md`'s Shared Core integrity section.

**Example 3**
- Input: a wave-based level can have hundreds of simultaneously active enemies, and the HUD needs a live "enemies remaining" count without polling `FindObjectsOfType<Enemy>()` every frame.
- Output: `EnemyRuntimeSet` per [runtime-set-pattern.md](references/runtime-set-pattern.md), each `Enemy` self-registering in `OnEnable`/`OnDisable`; the HUD reads `Items.Count` from the same asset, with the count treated as a Profiler leak indicator per that file's guardrail table.

## 8. Edge cases & guardrails
- Never let a Delegate Object's method, a Command's `Execute()`, or an Extendable Enum's behavior contain the actual game-rule formula — it must call into `Game.Core.*`, per `coding-principles.md`'s Shared Core integrity section.
- Never mutate a ScriptableObject asset's serialized field at runtime without the Dual Serialization reset — with Domain Reloading disabled, an in-play change to a shared asset persists into the next Play session, corrupting shared data invisibly.
- Never let a Runtime Set grow without a matching `OnDisable`/`OnDestroy` deregistration — unbounded growth per `performance-and-algorithms.md`'s Memory discipline.
- Never reach for `FindObjectOfType` or a singleton once a Runtime Set or Event Channel already exists for that concern — per `coding-principles.md`'s ban on runtime `Find` and the Law of Demeter.
- Never leave a `channel.OnEventRaised += ...` subscription without its matching `-=` in `OnDisable`/`OnDestroy` — an Event Channel subscription leaks exactly like any other C# event.
- If it's unclear whether Observer event or Event Channel fits a requirement, or whether Delegate Object or Extendable Enum is the right shape, ask rather than guess — both pairs solve adjacent problems, and the wrong choice is expensive to unwind once other systems depend on its shape.

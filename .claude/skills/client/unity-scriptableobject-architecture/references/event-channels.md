# Event Channels — Typed, Code-Subscribed Decoupling

Sources: [ScriptableObject](https://docs.unity3d.com/Manual/class-ScriptableObject.html), [UnityEvent](https://docs.unity3d.com/ScriptReference/UnityEvent.html). Not sourced from a single canonical page — synthesized as the typed evolution of the Observer-pattern SO event, widely adopted across Unity sample-project architectures.
Covers: SKILL.md §4 — **"Pick GameEvent/GameEventListener over an Event Channel only when the emitter has few, Editor-wireable, UnityEvent-driven listeners"**, escalation branch.

An Event Channel SO exposes a plain C# `event Action<T>` (or `Action` for a
void channel) instead of a `UnityEvent` plus listener-list pair. Any script —
MonoBehaviour, another SO, a manager — subscribes and unsubscribes directly in
code, and the channel asset itself is the only shared reference between
raiser and every subscriber, including across scene loads.

## Shape

| Member | Effect | Use when | Source |
|---|---|---|---|
| `VoidEventChannelSO : ScriptableObject` with `event Action OnEventRaised;` and `RaiseEvent()` | Signals that something happened, no data | An on/off notification (e.g. "level loaded") needs zero payload | synthesized |
| `EventChannelSO<T> : ScriptableObject` with `event Action<T> OnEventRaised;` and `RaiseEvent(T value)` | Signals what happened, with a typed payload | Damage dealt, item picked up — anything the subscriber needs data to react to | synthesized |
| Subscriber lifecycle: `channel.OnEventRaised += this.OnDamageDealt;` in `OnEnable`, `-=` in `OnDisable` | Standard C# event subscription lifecycle | Every subscriber, without exception | `coding-principles.md`'s Event handlers section |

## Code shape

```csharp
[CreateAssetMenu(menuName = "Events/Channels/Int Event Channel", fileName = "SO_IntEventChannel")]
public class IntEventChannelSO : ScriptableObject
{
    public event Action<int> OnEventRaised;

    public void RaiseEvent(int value)
    {
        this.OnEventRaised?.Invoke(value);
    }
}

public class ScoreDisplay : MonoBehaviour
{
    [SerializeField] private IntEventChannelSO scoreChangedChannel;

    private void OnEnable()
    {
        this.scoreChangedChannel.OnEventRaised += this.OnScoreChanged;
    }

    private void OnDisable()
    {
        this.scoreChangedChannel.OnEventRaised -= this.OnScoreChanged;
    }

    private void OnScoreChanged(int newScore)
    {
        // Update display text only when the score actually changed.
    }
}
```

## Event Channel vs Observer event

| Concern | Event Channel | Observer (`GameEvent`) | Source |
|---|---|---|---|
| Payload | Typed generic (`EventChannelSO<T>`) | None (plain `Raise()`) | synthesized |
| Subscriber authoring | Code (`+=`/`-=`) | Inspector (`UnityEvent`) | synthesized |
| Designer wiring visibility | None — invisible in the Inspector | Full — response visible per listener | synthesized |
| Best fit | Many code-driven, cross-scene subscribers with typed data | Few designer-authored reactions, no payload | synthesized |

**Critical caveat**: An unsubscribed `+=` is a leak exactly like any other C#
event, per `performance-and-algorithms.md`'s Memory discipline — always pair
it with `-=` in `OnDisable`/`OnDestroy`. Unlike `GameEventListener`, nothing
here unregisters a subscriber automatically.

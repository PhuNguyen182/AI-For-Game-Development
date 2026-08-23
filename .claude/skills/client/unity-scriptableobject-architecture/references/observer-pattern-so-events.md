# Observer Pattern — GameEvent / GameEventListener

Sources: [UnityEvent](https://docs.unity3d.com/ScriptReference/UnityEvent.html), [ScriptableObject](https://docs.unity3d.com/Manual/class-ScriptableObject.html). Pattern synthesized from Ryan Hipple's ScriptableObject-based event architecture (Unite Austin 2017).
Covers: SKILL.md §4 — **"Pick GameEvent/GameEventListener over an Event Channel only when the emitter has few, Editor-wireable, UnityEvent-driven listeners"**.

A `GameEvent` SO holds a list of `GameEventListener` MonoBehaviours and calls
`Raise()` to notify them, each firing its own serialized `UnityEvent` —
wiring is done entirely in the Inspector, with no C# reference between the
raiser and any listener. This decouples emitter from consumer completely.
[event-channels.md](event-channels.md) covers the typed, code-subscribed
evolution of the same idea.

## Shape

| Member | Role | Notes | Source |
|---|---|---|---|
| `GameEvent : ScriptableObject` | Holds `List<GameEventListener>`, exposes `Raise()` | Iterates backward so a listener can unregister itself mid-raise without breaking iteration | synthesized |
| `GameEventListener : MonoBehaviour` | Holds `[SerializeField] GameEvent gameEvent` + `[SerializeField] UnityEvent response`; registers in `OnEnable`, deregisters in `OnDisable` | The only place a `UnityEvent` response is authored — entirely in the Inspector | [UnityEvent](https://docs.unity3d.com/ScriptReference/UnityEvent.html) |
| `RegisterListener`/`UnregisterListener` | Add/remove from the `GameEvent`'s list | Must be safe against a listener that is already registered or already removed | synthesized |

## Code shape

```csharp
[CreateAssetMenu(menuName = "Events/Game Event", fileName = "SO_GameEvent")]
public class GameEvent : ScriptableObject
{
    private readonly List<GameEventListener> listeners = new();

    public void Raise()
    {
        for (int i = this.listeners.Count - 1; i >= 0; i--)
        {
            this.listeners[i].OnEventRaised();
        }
    }

    public void RegisterListener(GameEventListener listener)
    {
        this.listeners.Add(listener);
    }

    public void UnregisterListener(GameEventListener listener)
    {
        this.listeners.Remove(listener);
    }
}

public class GameEventListener : MonoBehaviour
{
    [SerializeField] private GameEvent gameEvent;
    [SerializeField] private UnityEvent response;

    private void OnEnable()
    {
        this.gameEvent.RegisterListener(this);
    }

    private void OnDisable()
    {
        this.gameEvent.UnregisterListener(this);
    }

    public void OnEventRaised()
    {
        this.response.Invoke();
    }
}
```

## When this loses to an Event Channel

| Symptom | Why Observer strains | Reach for instead | Source |
|---|---|---|---|
| The event needs to carry a typed payload (damage amount, item id) | A plain `GameEvent` carries no argument | A generic `EventChannelSO<T>`, per [event-channels.md](event-channels.md) | synthesized |
| Dozens of listeners across many scenes, mostly code, no Inspector wiring needed | Every listener needs its own `GameEventListener` MonoBehaviour plus an Inspector drag | A C#-`event`-based channel subscribed in code | synthesized |
| Listener order matters and must be stable | `UnityEvent` invocation order in the Inspector list is fragile to reorder | Direct C# `event` subscription, ordered by subscribe call | synthesized |

**Critical caveat**: Never let a `response` `UnityEvent` entry call a method
that computes a game-rule outcome (e.g. `TakeDamage(amount)` with the amount
decided inline in that method) — the event only notifies that something
happened; the amount and its resolution belong in `Game.Core.*`, per
`coding-principles.md`'s Shared Core integrity section.

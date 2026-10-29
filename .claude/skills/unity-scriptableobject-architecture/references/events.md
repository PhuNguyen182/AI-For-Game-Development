# SO Events: GameEvent Observer vs Event Channel

Sources: Manual `class-ScriptableObject.html`; `UnityEvent`. Shapes follow Ryan Hipple (Unite Austin 2017) and common Unity sample-project channel architectures.

| | `GameEvent` / `GameEventListener` | `EventChannelSO<T>` |
|---|---|---|
| Payload | None (`Raise()`) | Typed (`event Action<T> OnEventRaised`, `RaiseEvent(T)`); `VoidEventChannelSO` for none |
| Subscribers | Inspector `UnityEvent` on a `GameEventListener` MonoBehaviour | Code, `+=` / `-=` |
| Designer visibility | Full: response visible per listener | None |
| Best fit | Few designer-authored reactions, no payload | Many code-driven cross-scene subscribers, typed data |

## GameEvent
- `GameEvent : ScriptableObject` holds `List<GameEventListener>` and `Raise()`, iterating **backward** so a listener may unregister itself mid-raise.
- `GameEventListener : MonoBehaviour` holds `GameEvent` + `UnityEvent response`; registers in `OnEnable`, deregisters in `OnDisable`. Register/Unregister must tolerate duplicates and absent entries.
- The response only notifies; it must not compute a game-rule outcome (e.g. a damage amount decided inline). Amount and resolution belong in `Game.Core.*`.

## Switch to an Event Channel when
- The event needs a typed payload (damage amount, item id).
- Dozens of listeners across scenes, mostly code (a `GameEventListener` MonoBehaviour plus Inspector drag per listener strains).
- Listener order matters: `UnityEvent` Inspector order is fragile to reorder; C# subscribe order is stable.

## Channel subscription
Subscribe in `OnEnable`, unsubscribe in `OnDisable`/`OnDestroy`. Unlike `GameEventListener`, nothing unregisters a channel subscriber automatically; an unpaired `+=` leaks like any C# event.

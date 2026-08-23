# The Runtime Set Pattern — Tracking Active Instances Without Singletons

Sources: [ScriptableObject](https://docs.unity3d.com/Manual/class-ScriptableObject.html), [Domain Reloading](https://docs.unity3d.com/Manual/DomainReloading.html). Pattern synthesized from Ryan Hipple's "Runtime Set" technique (Unite Austin 2017).
Covers: SKILL.md §4 — **"Track a dynamic population of active instances with a Runtime Set instead of `FindObjectsOfType` or a singleton manager"**.

A Runtime Set SO holds a `List<T>` of every currently active instance of some
type (enemies, pickups, spawn points), populated by each instance registering
itself in `OnEnable` and deregistering in `OnDisable`. Any other script
references the same SO asset to query "which instances are alive right now"
without a singleton, a static list, or a per-frame `FindObjectsOfType` scan.

## Shape

| Member | Effect | Use when | Source |
|---|---|---|---|
| `abstract class RuntimeSetSO<T> : ScriptableObject` with `IReadOnlyList<T> Items`, `Add`, `Remove` | The generic set itself | Any "which instances of X exist right now" query, for a concrete `T` | synthesized |
| `EnemyRuntimeSet : RuntimeSetSO<Enemy>` | The per-type concrete asset | Inspector fields need a concrete, non-generic asset type — Unity cannot serialize a generic SO reference field directly | synthesized |
| `OnEnable`/`OnDisable` registration on each member | Add on enable, remove on disable, always paired | Every member, without exception — this is the entire lifecycle contract | `coding-principles.md`'s Correctness boundaries section |

## Code shape

```csharp
public abstract class RuntimeSetSO<T> : ScriptableObject
{
    private readonly List<T> items = new();

    public IReadOnlyList<T> Items => this.items;

    public void Add(T item)
    {
        if (!this.items.Contains(item))
        {
            this.items.Add(item);
        }
    }

    public void Remove(T item)
    {
        this.items.Remove(item);
    }
}

[CreateAssetMenu(menuName = "Runtime Sets/Enemy Set", fileName = "SO_EnemyRuntimeSet")]
public class EnemyRuntimeSet : RuntimeSetSO<Enemy>
{
}

public class Enemy : MonoBehaviour
{
    [SerializeField] private EnemyRuntimeSet enemySet;

    private void OnEnable()
    {
        this.enemySet.Add(this);
    }

    private void OnDisable()
    {
        this.enemySet.Remove(this);
    }
}
```

## Guardrails specific to this pattern

| Risk | Why it happens | Fix | Source |
|---|---|---|---|
| The set grows without bound | A member is destroyed without going through `OnDisable` | Treat the set's count as a leak indicator during profiling; verify against the actual active-instance count, per `performance-and-algorithms.md`'s Memory discipline | synthesized |
| Stale references survive a scene reload with Domain Reloading disabled | The SO asset instance persists in memory across a Play-session boundary, the same way a `static` field would | Clear the list at a defined session-start point, consistent with [dual-serialization.md](dual-serialization.md)'s reset discipline | [Domain Reloading](https://docs.unity3d.com/Manual/DomainReloading.html) |
| `Contains`/`Remove` cost grows on a large `List<T>` scanned every frame | Linear scan cost scales with set size | Cache a snapshot once per frame instead of querying `Items` repeatedly in a hot loop, per `performance-and-algorithms.md`'s Algorithmic complexity discipline | synthesized |

**Critical caveat**: A Runtime Set is populated state, not configuration —
apply the same domain-reload reset discipline as [dual-serialization.md](dual-serialization.md)
whenever the project has Domain Reloading disabled for faster Play Mode
iteration; otherwise entries from a previous Play session can silently outlive
the objects they represent.

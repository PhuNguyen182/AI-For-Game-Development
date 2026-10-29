# Runtime Set

Sources: Manual `class-ScriptableObject.html`, `DomainReloading.html`. Shape follows Ryan Hipple (Unite Austin 2017).

A Runtime Set SO holds `List<T>` of every active instance of a type; each instance calls `Add(this)` in `OnEnable` and `Remove(this)` in `OnDisable`, always paired. Other scripts query the same asset instead of a singleton, a static list, or per-frame `FindObjectsOfType`.

- `abstract RuntimeSetSO<T> : ScriptableObject` exposes `IReadOnlyList<T> Items`, `Add` (skip if already contained), `Remove`.
- Inspector fields need a concrete non-generic asset type: `EnemyRuntimeSet : RuntimeSetSO<Enemy>` with `[CreateAssetMenu]`. Unity cannot serialize a generic SO reference field.

## Risks
| Risk | Cause | Fix |
|---|---|---|
| Unbounded growth | A member destroyed without passing through `OnDisable` | Treat `Items.Count` as a leak indicator while profiling; compare to the real active count |
| Stale entries after Play with Domain Reloading disabled | The asset persists in memory like a `static` | Clear the list at a defined session start, per [dual-serialization.md](dual-serialization.md) |
| Linear `Contains`/`Remove` cost on a large list queried every frame | Scan cost scales with size | Cache one snapshot per frame instead of querying `Items` in a hot loop |

A Runtime Set is populated state, not configuration: reset it whenever Domain Reloading is disabled.

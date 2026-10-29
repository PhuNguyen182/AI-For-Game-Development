# Dual Serialization: Resetting Runtime State on an SO

Sources: `ISerializationCallbackReceiver`; Manual `script-Serialization.html`, `DomainReloading.html`. Common "reset on deserialize" technique across Variable/Runtime Set implementations.

An SO asset is one shared instance for the Editor session. With Domain Reloading disabled (Enter Play Mode Options), a runtime mutation survives Stop into the next Play session.

## Pattern
- `[SerializeField] private float initialValue;`: designer default, saved to the asset.
- `private float runtimeValue;`: not serialized; consumers read and write only this.
- `OnAfterDeserialize()` copies `initialValue` into `runtimeValue` (Unity calls it on domain reload and on entering Play Mode).
- `OnBeforeSerialize()` stays deliberately empty so a Play Mode value never writes back into the asset. Filling it later silently breaks the protection; state the reason if it must be non-empty.

## Needed or not
| Asset carries | Needed |
|---|---|
| Variable SO current value | Yes: readers share one instance, so one session's value bleeds into the next |
| Runtime Set `List<T>` | Yes: stays populated across a reload-disabled Play boundary and reports dead instances |
| Pure Data Container, or a Delegate Object with no runtime-written field | No |

This only protects the in-memory instance across Play sessions in one Editor run.

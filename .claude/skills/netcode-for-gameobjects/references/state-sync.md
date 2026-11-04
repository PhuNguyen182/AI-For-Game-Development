# State Sync — NetworkVariable, NetworkList, RPCs, Custom Messages

Sources — `manual/`: [rvn] learn/rpcvnetvar.html, [nv] basics/networkvariable.html, [cnv] basics/custom-networkvariables.html, [rpc] advanced-topics/message-system/rpc.html, [rel] advanced-topics/message-system/reliability.html, advanced-topics/message-system/rpc-params.html, [compat] advanced-topics/message-system/rpc-compatibility.html, advanced-topics/message-system/custom-messages.html, advanced-topics/connection-events.html. `api/Unity.Netcode.<Type>.html` (generic types end `-1`) for every type below.

Custom-type serialization: [serialization.md](serialization.md).

## NetworkVariable or Rpc
Test [rvn]: "Should a player joining mid-game get it?" Yes → `NetworkVariable`; no → Rpc.

| Signal | `NetworkVariable` | Rpc |
|---|---|---|
| Late joiner | Gets the current `.Value` before any local `OnValueChanged` | Never replayed |
| Values that must land together | Not guaranteed across separate variables | All parameters of one call arrive together |
| Rapid writes | Only the latest value matters; writes coalesce | Every call is its own event |
| Bandwidth | Delta, only on change | Full payload every call |

**Caveat:** what an unauthorized `.Value =` does (throw, drop, or apply then overwrite) is undocumented — enforcement sits in `NetworkVariableBase.CanClientWrite(clientId)`. Gate writes yourself, e.g. write only inside a `[Rpc(SendTo.Server)]` handler matching the write permission.

## NetworkVariable\<T\>
```csharp
private readonly NetworkVariable<int> _health = new NetworkVariable<int>(
    value: 100,
    readPerm: NetworkVariableReadPermission.Everyone,
    writePerm: NetworkVariableWritePermission.Server);

public override void OnNetworkSpawn() => this._health.OnValueChanged += this.OnHealthChanged;
public override void OnNetworkDespawn() => this._health.OnValueChanged -= this.OnHealthChanged;
private void OnHealthChanged(int previous, int current) { }
```

| Subject | Fact that decides |
|---|---|
| `NetworkVariableReadPermission` | `Everyone` (default); `Owner` — owner and server only. Ignored in DA: everyone reads |
| `NetworkVariableWritePermission` | `Server` (default); `Owner` — current owner only |
| `SetUpdateTraits(NetworkVariableUpdateTraits)` | `MinSecondsBetweenUpdates` — dirtiness ignored until elapsed; `MaxSecondsBetweenUpdates` — force-send after this long dirty. No documented defaults: set both |
| `OnValueChanged` | `(T previous, T current)`; subscribe in `OnNetworkSpawn`, unsubscribe in `OnNetworkDespawn` — not `Awake`/`Start` |
| In-place collection edits | `.Value` doesn't detect them; call `CheckDirtyState(bool forceCheck = false)` once after all edits |
| Supported `T` | Primitives incl. `decimal`; `Vector2/3/4`, `Vector2Int`/`Vector3Int`, `Quaternion`, `Color`/`Color32`, `Ray`/`Ray2D`; enums; `INetworkSerializable` (deserialized in place); `INetworkSerializeByMemcpy`; `FixedString32Bytes`–`FixedString4096Bytes`. **No raw `string`** (fine as an Rpc param) |
| Custom `NetworkVariableBase` subclass | Override `WriteField`/`ReadField`/`WriteDelta`/`ReadDelta`; declare as a field on the `NetworkBehaviour`, never nested in another `NetworkVariable`; `[GenerateSerializationForType(typeof(Foo))]` or stacked `[GenerateSerializationForGenericParameter(0)]` [cnv] |

## NetworkList\<T\>
| Subject | Fact that decides |
|---|---|
| Constraint | `T : unmanaged, IEquatable<T>` |
| Constructor | `NetworkList(IEnumerable<T> values, NetworkVariableReadPermission, NetworkVariableWritePermission)` |
| Mutators | `Add`, `Insert`, `Remove`, `RemoveAt`, `Clear`, `Set(index, value, forceUpdate)`, indexer — each checks write permission |
| `AsNativeArray()` | Zero-allocation read-only view, valid until the next mutation |
| `OnListChanged(NetworkListEvent<T>)` | Fields `Type`, `Index`, `Value`, `PreviousValue` (only for `Value` events). `EventType`: `Add`, `Insert`, `Remove`, `RemoveAt`, `Value`, `Clear`, `Full` |
| Sync | Full on spawn and late join, deltas after [nv]. `LastModifiedTick` is obsolete |

## Rpc attributes
| Attribute | Fact that decides |
|---|---|
| `[Rpc(SendTo.X)]` | Current; replaces both legacy attributes |
| `[ServerRpc]` | Legacy; `RequireOwnership` obsolete. `(RequireOwnership = false)` → `[Rpc(SendTo.Server)]`; `(RequireOwnership = true)` → `[Rpc(SendTo.Server, InvokePermission = RpcInvokePermission.Owner)]` |
| `[ClientRpc]` | Legacy; all clients except the server by default; target via `ClientRpcParams.Send.TargetClientIds` |
| Method name | Must end in `Rpc` — the ILPostProcessor rewrites call sites; otherwise a compile error |

```csharp
[Rpc(SendTo.Server)]
public void SubmitMoveRpc(Vector3 destination, RpcParams rpcParams = default)
{
    ulong sender = rpcParams.Receive.SenderClientId; // validate; rules live in Core
}

[Rpc(SendTo.NotServer, Delivery = RpcDelivery.Unreliable)]
public void PlayHitEffectRpc(Vector3 position) { } // cosmetic: dropping is fine
```

| `RpcAttribute` property | Default — meaning |
|---|---|
| `Delivery` | `Reliable` — received and executed, in order **per `NetworkObject` only**; `Unreliable` — no guarantees |
| `InvokePermission` | `Everyone`; also `Owner`, `Server`. A violation raises `RpcException` |
| `AllowTargetOverride` | `false` — `true` lets `RpcParams.Send.Target` override the static target |
| `DeferLocal` | `false` — set on an Rpc called from inside another Rpc, so its local branch waits for the next tick instead of running before the message ships |

## `SendTo` targets
| Member | Fact that decides |
|---|---|
| `Server` | Server regardless of ownership; runs locally if invoked on the server |
| `NotServer` | Everyone but the server (observers only); never reaches a host's server role |
| `Owner` / `NotOwner` | Current owner (runs locally if it is us) / everyone else (observers only) |
| `Authority` / `NotAuthority` | Server in CS, owning client in DA / everyone else |
| `Me` / `NotMe` | Local call only / everyone but this machine (observers only) |
| `Everyone` | All observers, including local |
| `ClientsAndHost` | All clients, including the host's client role |
| `SpecifiedInParams` | No static target; the call must supply `RpcParams.Send.Target` or it can't send |

## Runtime targets and params
| Subject | Fact that decides |
|---|---|
| `RpcTarget.Server` … `.ClientsAndHost` | Same meaning as the matching `SendTo` |
| `RpcTarget.Single(ulong, RpcTargetUse)` / `Group(ids, RpcTargetUse)` / `Not(ids, RpcTargetUse)` | One client / a set / all but a set; ids as `ulong[]`, `NativeArray<ulong>`, `NativeList<ulong>` or `IEnumerable<ulong>` |
| `RpcTargetUse` | `Persistent` — cache it, call `Dispose()` when done; `Temp` — valid only in the invoking frame. `BaseRpcTarget` throws if a `Temp` target is disposed while locked |
| `RpcParams` | `Receive.SenderClientId`; `Send` = `RpcSendParams { Target, LocalDeferMode }`. Implicit conversions from `BaseRpcTarget`, `LocalDeferMode`, `RpcReceiveParams`, `RpcSendParams` — pass `RpcTarget.Single(id, ...)` directly |
| Legacy | `ServerRpcParams.Receive.SenderClientId`; `ClientRpcParams.Send.TargetClientIds` |
| Delivery limits [rel] | No connection → the call is silently dropped; a reliable Rpc in flight when the sender disconnects can be lost; exercise unreliable paths with the simulator pipeline ([transports-testing.md](transports-testing.md)) |

**Caveat:** the wire signature hash is assembly + enclosing class + method name + parameter types [compat]. Changing any of them makes old and new builds miss each other's calls; renaming a parameter is safe. Identical signatures in two different projects are still incompatible.

## Custom messages
Use for payloads that belong to no `NetworkObject` (lobby chat, global session events) — an Rpc needs a spawned `NetworkBehaviour`. Register in `OnNetworkSpawn`, unregister in `OnNetworkDespawn`.

| `CustomMessagingManager` member | Fact that decides |
|---|---|
| `RegisterNamedMessageHandler(string name, HandleNamedMessageDelegate)` / `UnregisterNamedMessageHandler(string)` | Names are hashed and dispatched automatically |
| `SendNamedMessage(string name, ulong clientId \| IReadOnlyList<ulong>, FastBufferWriter, NetworkDelivery = ReliableSequenced)` / `SendNamedMessageToAll` | Default delivery `ReliableSequenced` |
| `SendUnnamedMessage` / `SendUnnamedMessageToAll` / `OnUnnamedMessage` | One channel per peer — the payload must encode its own type |
| `NetworkDelivery` | `Reliable`, `ReliableSequenced`, `ReliableFragmentedSequenced` (adds fragmentation), `Unreliable`, `UnreliableSequenced` |

```csharp
using (FastBufferWriter writer = new FastBufferWriter(1100, Allocator.Temp))
{
    writer.WriteValueSafe(damageAmount);
    NetworkManager.Singleton.CustomMessagingManager.SendNamedMessage("DamageEvent", targetClientId, writer);
}
```

## Connection events
`NetworkManager.OnConnectionEvent` delivers `ConnectionEventData { ClientId, EventType, PeerClientIds }`.

| `ConnectionEvent` | Fact that decides |
|---|---|
| `ClientConnected` | Server/host: a client joined. Local client: its own connection completed; `PeerClientIds` (`NativeArray<ulong>`) lists existing peers — populated only here |
| `ClientDisconnected` | Server/host: a client left. Local client: it disconnected |
| `PeerConnected` / `PeerDisconnected` | Client-only: another client joined/left |

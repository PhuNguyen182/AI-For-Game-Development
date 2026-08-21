# State Sync — NetworkVariable, NetworkList, RPCs, Custom Messages

Source: [NetworkVariables](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/manual/networkvariables-landing.html), [NetworkVariable](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/manual/basics/networkvariable.html), [Custom NetworkVariables](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/manual/basics/custom-networkvariables.html), [Remote procedure calls](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/manual/rpc-landing.html), [Messaging system](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/manual/advanced-topics/messaging-system.html), [RPC](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/manual/advanced-topics/message-system/rpc.html), [Reliability](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/manual/advanced-topics/message-system/reliability.html), [RPC params](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/manual/advanced-topics/message-system/rpc-params.html), [RPC vs NetworkVariables](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/manual/learn/rpcvnetvar.html), [RPC compatibility](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/manual/advanced-topics/message-system/rpc-compatibility.html), [Custom messages](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/manual/advanced-topics/message-system/custom-messages.html), [Connection events](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/manual/advanced-topics/connection-events.html). Every API type below carries its own Source link in the API index at the bottom.

Covers: SKILL.md §4 — **"Pick NetworkVariable or Rpc by data shape, not habit"**.

This file is the decision reference for choosing `NetworkVariable<T>`/`NetworkList<T>` versus `ServerRpc`/`ClientRpc`/`Rpc`, plus the exact API shape of each — attributes, targeting, params, delivery, custom messages, and connection events. Custom-type serialization for either mechanism (`INetworkSerializable`, `INetworkSerializeByMemcpy`) lives in the sibling file [serialization.md](serialization.md) — don't duplicate it, cross-link instead.

## NetworkVariable vs. Rpc

**Rule of thumb** (verbatim from the manual): *"Should a player joining mid-game get that information?"* Yes → `NetworkVariable`. No → `Rpc`.

| Signal | NetworkVariable wins | Rpc wins | Source |
|---|---|---|---|
| Late joiners need the data | Auto-synced: a newly spawned/joining client receives the current `.Value` before any `OnValueChanged` fires locally | RPCs sent before a client connects are never replayed — a late joiner simply never saw them | [RPC vs NetworkVariables](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/manual/learn/rpcvnetvar.html) |
| Nature of the data | Ongoing/persistent state (health, door open/closed) | One-time/momentary occurrence (an explosion, a "play this VFX now" cue) | same |
| What matters on arrival | Only the latest value — intermediate writes can coalesce | Every call must arrive as its own event, not just the latest | same |
| Several values must land together | Not guaranteed — separate `NetworkVariable`s changed in the same frame are **not** guaranteed to be delivered to clients at the same time | Guaranteed — all parameters of one RPC call arrive and execute together | same |
| Bandwidth | Sends deltas only, and only when the value actually changes | Sends a full payload on every call, changed or not | same |
| Implementation simplicity for a single fire-once action | Overkill — a `NetworkVariable` that's set once and never read again wastes the permission/dirty-tracking machinery | Simpler — a direct call with no persistent backing state | same |

**Critical caveat**: the manual does not document what happens when code without write permission attempts `myVariable.Value = x` — enforcement is implicit via `NetworkVariableBase.CanClientWrite(clientId)`, and neither the manual nor the API pages state whether an unauthorized write throws, is silently dropped, or is applied locally then overwritten by the next authoritative sync. Never rely on the write being visibly rejected — gate the call yourself (e.g. only mutate the variable inside a `[Rpc(SendTo.Server)]` handler, matching the variable's actual `NetworkVariableWritePermission`).

## NetworkVariable<T> and NetworkList<T>

```csharp
public class HealthBehaviour : NetworkBehaviour
{
    private readonly NetworkVariable<int> _health = new NetworkVariable<int>(
        value: 100,
        readPerm: NetworkVariableReadPermission.Everyone,
        writePerm: NetworkVariableWritePermission.Server);

    public override void OnNetworkSpawn()
    {
        this._health.OnValueChanged += this.OnHealthChanged;
    }

    public override void OnNetworkDespawn()
    {
        this._health.OnValueChanged -= this.OnHealthChanged;
    }

    private void OnHealthChanged(int previous, int current)
    {
        // React to the synced change here — never poll _health.Value in Update().
    }
}
```

### Permissions

| Enum | Member | Meaning | Source |
|---|---|---|---|
| `NetworkVariableReadPermission` | `Everyone` (default) | Owner and non-owners can all read | [API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.NetworkVariableReadPermission.html) |
| `NetworkVariableReadPermission` | `Owner` | Only the owner and the server can read | same |
| `NetworkVariableWritePermission` | `Server` (default) | Only the server can write | [API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.NetworkVariableWritePermission.html) |
| `NetworkVariableWritePermission` | `Owner` | Only the current owner can write | same |

In Distributed Authority mode, `ReadPermission` is ignored — every participant can read regardless of the setting, per the read-permission API remarks.

### NetworkVariableUpdateTraits

Set via `NetworkVariableBase.SetUpdateTraits(NetworkVariableUpdateTraits traits)`.

| Field | Type | Meaning | Source |
|---|---|---|---|
| `MinSecondsBetweenUpdates` | `float` | Minimum time that must pass between sent updates; dirtiness is ignored (not sent) until this elapses | [API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.NetworkVariableUpdateTraits.html) |
| `MaxSecondsBetweenUpdates` | `float` | Maximum time a variable may stay dirty before it is force-sent, even if `MinSecondsBetweenUpdates` or a dirtiness threshold hasn't been met | same |

No default values are documented for either field — set both explicitly rather than assuming a throttle exists out of the box.

### OnValueChanged and lifecycle

| Aspect | Detail | Source |
|---|---|---|
| Signature | `void Callback(T previous, T current)` | [NetworkVariable\<T\> API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.NetworkVariable-1.html) |
| Fires | On every peer that subscribed before the value changed, once per synced change | [NetworkVariable manual](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/manual/basics/networkvariable.html) |
| Subscribe/unsubscribe timing | Subscribe in `OnNetworkSpawn()`, unsubscribe in `OnNetworkDespawn()` — not `Awake()`/`Start()`, since the variable isn't attached to a spawned `NetworkObject` yet | same |
| Late joiners | Receive the current `.Value` when the `NetworkObject` spawns, before any `OnValueChanged` callback fires locally | same |
| Collection contents mutated in place | Assigning through `.Value` doesn't detect in-place collection edits by itself — call `CheckDirtyState(bool forceCheck = false)` once after all edits complete, not after each one | [NetworkVariable\<T\> API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.NetworkVariable-1.html) |

### Supported `NetworkVariable<T>` types

Primitives (`bool`, `byte`, `sbyte`, `char`, `decimal`, `double`, `float`, `int`, `uint`, `long`, `ulong`, `short`, `ushort`); Unity structs (`Vector2/3/4`, `Vector2Int`, `Vector3Int`, `Quaternion`, `Color`, `Color32`, `Ray`, `Ray2D`); `enum` types; `INetworkSerializable` implementations (deserialized in place); `INetworkSerializeByMemcpy` unmanaged structs; `FixedString32Bytes` through `FixedString4096Bytes`. **Not supported: raw `string`** — use a `FixedString*` type instead. Anything beyond this list needs a custom serializer — see [serialization.md](serialization.md).

### NetworkList\<T\>

| Member | Signature | Notes | Source |
|---|---|---|---|
| Constructors | `NetworkList()` / `NetworkList(IEnumerable<T> values, NetworkVariableReadPermission, NetworkVariableWritePermission)` | Same permission model as `NetworkVariable<T>` | [API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.NetworkList-1.html) |
| Constraint on `T` | `T : unmanaged, IEquatable<T>` | No managed/reference types, no raw `string` | same |
| `Add`/`Insert`/`Remove`/`RemoveAt`/`Clear`/`Set(index, value, forceUpdate)`/`this[int]` | Mutators | Every mutator checks write permission before applying | same |
| `Contains`/`IndexOf`/`Count`/`GetEnumerator` | Query | — | same |
| `AsNativeArray()` | `NativeArray<T>` | Zero-allocation read-only view; valid only until the next mutation | same |
| `OnListChanged` | `event ... NetworkListEvent<T>` | Fires once per structural change | [NetworkListEvent\<T\> API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.NetworkListEvent-1.html) |
| `LastModifiedTick` | — | Obsolete, no longer used | [API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.NetworkList-1.html) |
| Delta support | By default, collection types support delta updates — full serialization happens on spawn/for late joiners, deltas apply afterward | [NetworkVariable manual](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/manual/basics/networkvariable.html) |

`NetworkListEvent<T>` fields: `Type` (`EventType`), `Index` (`int`, if applicable), `Value` (`T`, if applicable), `PreviousValue` (`T`, when `Type == Value`, i.e. an in-place change).

`NetworkListEvent<T>.EventType` members: `Add`, `Insert`, `Remove`, `RemoveAt`, `Value` ("Value changed"), `Clear`, `Full` ("Full list refresh"). Source: [EventType API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.NetworkListEvent-1.EventType.html).

### Custom NetworkVariable types

Deriving your own `NetworkVariableBase` subclass requires overriding `WriteField`/`ReadField`/`WriteDelta`/`ReadDelta`, and it cannot be nested inside another `NetworkVariable` class — declare it as a field on the `NetworkBehaviour` instead. Use `[GenerateSerializationForType(typeof(Foo))]` on the subclass for a hard-coded type, or `[GenerateSerializationForGenericParameter(0)]` (stacked, 0-indexed, for multiple generic params) for a generic one. Source: [Custom NetworkVariables](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/manual/basics/custom-networkvariables.html). Full serializer mechanics (`FastBufferWriter`/`Reader`, `INetworkSerializable`) live in [serialization.md](serialization.md).

## RPC attributes and targeting

| Attribute | Executes on | Invoked by | Status | Source |
|---|---|---|---|---|
| `[ServerRpc]` | Server | A client (or the server calling itself) | Legacy — `RequireOwnership` property is obsolete | [API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.ServerRpcAttribute.html) |
| `[ClientRpc]` | All clients except the server by default | Server | Legacy — target specific clients via `ClientRpcParams.Send.TargetClientIds` | [API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.ClientRpcAttribute.html) |
| `[Rpc(SendTo.X)]` | Whichever `SendTo` target names | Any, subject to `InvokePermission` | Current/unified — replaces both legacy attributes | [API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.RpcAttribute.html) |

Migration mapping quoted from the `ServerRpcAttribute` docs: `[ServerRpc(RequireOwnership = false)]` → `[Rpc(SendTo.Server)]`; `[ServerRpc(RequireOwnership = true)]` → `[Rpc(SendTo.Server, InvokePermission = RpcInvokePermission.Owner)]`.

```csharp
[Rpc(SendTo.Server)]
public void SubmitMoveRpc(Vector3 destination, RpcParams rpcParams = default)
{
    ulong senderClientId = rpcParams.Receive.SenderClientId;
    // Validate and apply on the server; never compute game rules here — call Game.Core.*.
}

[Rpc(SendTo.NotServer, Delivery = RpcDelivery.Unreliable)]
public void PlayHitEffectRpc(Vector3 position)
{
    // Cosmetic-only: fine to drop occasionally, so Unreliable is correct here.
}
```

**Method names must end with the literal suffix `Rpc`** — the ILPostProcessor rewrites call sites to inject network transmission logic, and omitting the suffix is a compile-time error.

### RpcAttribute properties

| Property | Type | Default | Meaning | Source |
|---|---|---|---|---|
| `SendTo` | `SendTo` | required constructor arg | Static target for this RPC | [RpcAttribute API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.RpcAttribute.html) |
| `Delivery` | `RpcDelivery` | `Reliable` | Delivery guarantee (see table below) | same / [Reliability](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/manual/advanced-topics/message-system/reliability.html) |
| `InvokePermission` | `RpcInvokePermission` | `Everyone` | Who is allowed to invoke this RPC | same / [API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.RpcInvokePermission.html) |
| `AllowTargetOverride` | `bool` | `false` | Lets a caller override the target at runtime through `RpcParams.Send.Target`, without requiring `SendTo.SpecifiedInParams` | same |
| `DeferLocal` | `bool` | `false` | Defers the local-execution branch to the next network tick — needed when an RPC is invoked from inside another RPC, since the local branch could otherwise run before the outbound message is actually sent | same / [RPC manual](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/manual/advanced-topics/message-system/rpc.html) |
| `RequireOwnership` | `bool` | — | Obsolete; use `InvokePermission = RpcInvokePermission.Owner` instead | same |

### SendTo targets

| `SendTo` member | Behavior | Source |
|---|---|---|
| `Server` | Send to the server regardless of ownership; executes locally if invoked on the server | [SendTo API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.SendTo.html) |
| `NotServer` | Everyone but the server, filtered to the current observer list; won't reach a host's server role | same |
| `Owner` | The `NetworkObject`'s current owner; executes locally if the local process is the owner | same |
| `NotOwner` | Everyone but the current owner, filtered to the current observer list | same |
| `Authority` | The authority (Client-Server: the server; Distributed Authority: the owning client) | same |
| `NotAuthority` | Everyone except the authority | same |
| `Me` | Execute locally only — effectively a normal function call | same |
| `NotMe` | Everyone but the local machine, filtered to the current observer list | same |
| `Everyone` | All observers, filtered to the current observer list; executes locally too | same |
| `ClientsAndHost` | All clients, including the host's client role if a host exists | same |
| `SpecifiedInParams` | No static target — the call must supply a target via `RpcParams`/`RpcSendParams.Target`, or it cannot be sent | same |

### Runtime target overrides — RpcTarget / BaseRpcTarget

| Member | Purpose | Source |
|---|---|---|
| `RpcTarget.Server` / `.NotServer` / `.Owner` / `.NotOwner` / `.Authority` / `.NotAuthority` / `.Me` / `.NotMe` / `.Everyone` / `.ClientsAndHost` | Same semantics as the matching `SendTo` value, usable at runtime through `RpcParams` | [RpcTarget API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.RpcTarget.html) |
| `RpcTarget.Single(ulong clientId, RpcTargetUse use)` | Target exactly one client | same |
| `RpcTarget.Group(ulong[] \| NativeArray<ulong> \| NativeList<ulong> \| IEnumerable<ulong>, RpcTargetUse use)` | Target an explicit client set | same |
| `RpcTarget.Not(<same overloads>, RpcTargetUse use)` | Target everyone except the given client(s) | same |
| `RpcTargetUse.Persistent` | The returned `BaseRpcTarget` persists until `Dispose()` is called — cache it as a field for reuse | [RpcTargetUse API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.RpcTargetUse.html) |
| `RpcTargetUse.Temp` | The returned target is valid only for the frame the decorated method is invoked in | same |

`BaseRpcTarget` is the abstract base for all of the above, implements `IDisposable`, and throws if a `Temp` target is disposed while locked. Source: [BaseRpcTarget API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.BaseRpcTarget.html).

### RPC params

| Type | Field | Meaning | Source |
|---|---|---|---|
| `RpcParams` | `Receive: RpcReceiveParams` | Gives the sender's client ID | [RpcParams API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.RpcParams.html) |
| `RpcParams` | `Send: RpcSendParams` | Runtime target/defer override (used with `AllowTargetOverride` or `SendTo.SpecifiedInParams`) | same |
| `RpcReceiveParams` | `SenderClientId: ulong` | The client that invoked this RPC | [API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.RpcReceiveParams.html) |
| `RpcSendParams` | `Target: BaseRpcTarget`, `LocalDeferMode: LocalDeferMode` | Per-call target override and defer behavior | [API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.RpcSendParams.html) |
| `ServerRpcParams` (legacy) | `Receive.SenderClientId` | Same sender-ID access, legacy path | [API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.ServerRpcParams.html) |
| `ClientRpcParams` (legacy) | `Send.TargetClientIds: ulong[]` | Explicit target client list | [API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.ClientRpcParams.html) |

`RpcParams` also has implicit conversion operators from `BaseRpcTarget`, `LocalDeferMode`, `RpcReceiveParams`, and `RpcSendParams`, so a bare `RpcTarget.Single(id)` can be passed directly where an `RpcParams` argument is expected.

### Delivery and invoke permission

| Enum | Members | Source |
|---|---|---|
| `RpcDelivery` | `Reliable` (default — guaranteed received and executed on the remote side, in-order **per `NetworkObject` only**), `Unreliable` (no delivery or ordering guarantee) | [RpcDelivery API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.RpcDelivery.html) / [Reliability](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/manual/advanced-topics/message-system/reliability.html) |
| `NetworkDelivery` (transport-level; used by custom messages) | `Reliable`, `ReliableSequenced` (guaranteed order — default for `CustomMessagingManager` sends), `ReliableFragmentedSequenced` (reliable + ordered + fragmentation support), `Unreliable`, `UnreliableSequenced` | [NetworkDelivery API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.NetworkDelivery.html) |
| `RpcInvokePermission` | `Everyone` (default), `Owner`, `Server` | [API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.RpcInvokePermission.html) |

`RpcException` ("Exception thrown when an RPC encounters an error during execution") is the type raised on an RPC-level failure such as an `InvokePermission` violation. Source: [RpcException API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.RpcException.html).

Reliability manual notes worth keeping in mind: an RPC call requires an active connection — sending without one silently drops/ignores the call; a reliable RPC in flight when the sender disconnects can still be lost; use `UnityTransport`'s Simulator Pipeline to actually exercise unreliable-delivery paths, since a local network rarely drops packets on its own.

**Critical caveat**: an RPC's wire signature hash is derived from assembly name, enclosing class, method name, and parameter types — changing any of those routes the call to a different (incompatible) invocation path, so an updated client and an un-updated server (or vice versa) simply won't invoke each other's old method. Parameter name changes alone are safe. Cross-build and cross-version calls work as long as the signature is unchanged, but **identical signatures across two different projects are still incompatible** — project identity isn't part of the hash. Source: [RPC compatibility](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/manual/advanced-topics/message-system/rpc-compatibility.html). Separately, invoking an RPC from inside another RPC risks the local execution branch running before the outbound message actually ships — set `DeferLocal = true` on the nested call to push local execution to the next network tick.

## Custom messages and connection events

| `CustomMessagingManager` member | Signature | Default delivery | Source |
|---|---|---|---|
| `RegisterNamedMessageHandler` | `void RegisterNamedMessageHandler(string name, HandleNamedMessageDelegate callback)` | — | [API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.CustomMessagingManager.html) |
| `UnregisterNamedMessageHandler` | `void UnregisterNamedMessageHandler(string name)` | — | same |
| `SendNamedMessage` | `void SendNamedMessage(string messageName, ulong clientId, FastBufferWriter messageStream, NetworkDelivery networkDelivery = NetworkDelivery.ReliableSequenced)` (also an `IReadOnlyList<ulong>` overload) | `ReliableSequenced` | same |
| `SendNamedMessageToAll` | Same shape, broadcasts to every connected client | `ReliableSequenced` | same |
| `SendUnnamedMessage` / `SendUnnamedMessageToAll` | Same shape without a name — payload type must be discriminated manually inside the buffer | `ReliableSequenced` | same |
| `OnUnnamedMessage` | `event UnnamedMessageDelegate` | — | same |

Named messages hash the string key internally and dispatch to the matching registered handler automatically; unnamed messages have a single receive channel per peer, so the payload itself must encode what it is. Use custom messages for cross-cutting payloads that don't belong to any one `NetworkObject`/`NetworkBehaviour` (lobby chat, global session events) — an RPC always requires a spawned `NetworkBehaviour` to call through, a custom message doesn't.

```csharp
using (FastBufferWriter writer = new FastBufferWriter(1100, Allocator.Temp))
{
    writer.WriteValueSafe(damageAmount);
    NetworkManager.Singleton.CustomMessagingManager.SendNamedMessage(
        "DamageEvent", targetClientId, writer);
}
```

Register/unregister named handlers the same way an RPC-adjacent event would be managed: subscribe in `OnNetworkSpawn()`, unregister in `OnNetworkDespawn()`, per `coding-principles.md`'s event-subscription lifecycle rule.

### Connection events

| Event / type | Detail | Source |
|---|---|---|
| `NetworkManager.OnConnectionEvent` | Unified connection-event callback, parameterized by `ConnectionEventData` | [Connection events](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/manual/advanced-topics/connection-events.html) |
| `ConnectionEvent.ClientConnected` | Server/host: a new client connected, `ClientId` populated. Local client: its own connection completed; `PeerClientIds` lists the peers already present | [ConnectionEvent API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.ConnectionEvent.html) |
| `ConnectionEvent.PeerConnected` | Client-only: another client connected to the server (not applicable on the server) | same |
| `ConnectionEvent.ClientDisconnected` | Server/host: a client disconnected. Local client: it disconnected from the server | same |
| `ConnectionEvent.PeerDisconnected` | Client-only: another client disconnected (not applicable on the server) | same |
| `ConnectionEventData.ClientId` | `ulong` — the client this event concerns | [ConnectionEventData API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.ConnectionEventData.html) |
| `ConnectionEventData.EventType` | `ConnectionEvent` | same |
| `ConnectionEventData.PeerClientIds` | `NativeArray<ulong>` — only populated for `ClientConnected` on the client side; don't read it for any other event | same |

## API index

| Type | Source |
|---|---|
| `NetworkVariable<T>` | [API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.NetworkVariable-1.html) |
| `NetworkVariableBase` | [API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.NetworkVariableBase.html) |
| `NetworkVariableReadPermission` | [API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.NetworkVariableReadPermission.html) |
| `NetworkVariableWritePermission` | [API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.NetworkVariableWritePermission.html) |
| `NetworkVariableUpdateTraits` | [API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.NetworkVariableUpdateTraits.html) |
| `NetworkList<T>` | [API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.NetworkList-1.html) |
| `NetworkListEvent<T>` | [API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.NetworkListEvent-1.html) |
| `NetworkListEvent<T>.EventType` | [API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.NetworkListEvent-1.EventType.html) |
| `ServerRpcAttribute` | [API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.ServerRpcAttribute.html) |
| `ClientRpcAttribute` | [API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.ClientRpcAttribute.html) |
| `RpcAttribute` | [API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.RpcAttribute.html) |
| `RpcParams` | [API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.RpcParams.html) |
| `ServerRpcParams` | [API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.ServerRpcParams.html) |
| `ClientRpcParams` | [API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.ClientRpcParams.html) |
| `RpcSendParams` | [API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.RpcSendParams.html) |
| `RpcReceiveParams` | [API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.RpcReceiveParams.html) |
| `RpcTarget` | [API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.RpcTarget.html) |
| `RpcTargetUse` | [API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.RpcTargetUse.html) |
| `BaseRpcTarget` | [API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.BaseRpcTarget.html) |
| `SendTo` | [API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.SendTo.html) |
| `RpcDelivery` | [API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.RpcDelivery.html) |
| `RpcException` | [API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.RpcException.html) |
| `RpcInvokePermission` | [API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.RpcInvokePermission.html) |
| `CustomMessagingManager` | [API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.CustomMessagingManager.html) |
| `NetworkDelivery` | [API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.NetworkDelivery.html) |
| `ConnectionEvent` | [API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.ConnectionEvent.html) |
| `ConnectionEventData` | [API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.ConnectionEventData.html) |

# Sender Identity per Stack

Sources (below the SKILL.md `Docs:` bases): NGO [rpc] `manual/advanced-topics/message-system/rpc.html`, [rrp] `api/Unity.Netcode.RpcReceiveParams.html`, [nm] `api/Unity.Netcode.NetworkManager.html`, [nmd] `api/Unity.Netcode.CustomMessagingManager.HandleNamedMessageDelegate.html`; NfE [nrpc] `manual/rpcs.html`, [rcr] `api/Unity.NetCode.ReceiveRpcCommandRequest.html`, [cmd] `manual/command-stream.html`, [disc] `api/Unity.NetCode.NetworkStreamRequestDisconnect.html`; MagicOnion [hub] https://github.com/Cysharp/MagicOnion/blob/main/src/MagicOnion.Server/Hubs/StreamingHub.cs, [ctx] https://github.com/Cysharp/MagicOnion/blob/main/src/MagicOnion.Server/ServiceContext.cs, [life] `fundamentals/lifecycle`, [auth] `fundamentals/authentication`; UTP [dsr] https://docs.unity3d.com/Packages/com.unity.collections@2.5/api/Unity.Collections.DataStreamReader.html.

A connection id names a transport slot, not an account. Binding an account to it needs a server-verified credential; token design is `security-reviewer`'s.

## Netcode for GameObjects 2.x

| Subject | Fact that decides |
|---|---|
| `[Rpc(SendTo.Server)]` + trailing `RpcParams rpcParams = default` | `rpcParams.Receive.SenderClientId` (`ulong`) is the sender [rpc][rrp]; without the parameter the handler cannot know who called |
| Legacy `[ServerRpc]` | `ServerRpcParams.Receive.SenderClientId`; same rule applies |
| `CustomMessagingManager.HandleNamedMessageDelegate(ulong senderClientId, FastBufferReader messagePayload)` | Named-message sender [nmd]; the handler reads the payload itself, so the limiter runs before any `TryBeginRead`/`ReadValueSafe` |
| `InvokePermission` | `Everyone` (default), `Owner`, `Server`; a violation throws [rpc]. Gates only the Rpc's own `NetworkObject` |
| `NetworkObject.OwnerClientId` | Compare with the sender for the Rpc's own object |
| `NetworkObjectReference.TryGet(out NetworkObject, NetworkManager = null)` | Resolve a payload reference server-side, then compare its `OwnerClientId`; `false` → reject (`netcode-for-gameobjects` → `serialization.md`) |
| `NetworkManager.ConnectedClients` | `IReadOnlyDictionary<ulong, NetworkClient>` [nm]; `PlayerObject` gives the sender's avatar |
| `NetworkManager.ServerClientId` | `const ulong 0`, the server's own id [nm] |
| `NetworkManager.DisconnectClient(ulong clientId, string reason = null)` | Drops the client; `reason` reaches the client as `DisconnectReason` [nm], so keep it generic |
| `NetworkConfig.ConnectionData` | Unauthenticated, unencrypted (`netcode-for-gameobjects` Never): never the source of an account binding |

```csharp
[Rpc(SendTo.Server)]
public void UseItemRpc(int slot, RpcParams rpcParams = default)
{
    ulong sender = rpcParams.Receive.SenderClientId;
    if (!this._limiter.TryConsume(sender, this._clock.Tick))
        return;

    if (this.OwnerClientId != sender)
    {
        this.RejectToSender(sender, UseItemRejection.NotAllowed);
        return;
    }

    // Core decides; the handler only applies an accepted result.
    UseItemResult result = this._inventoryRules.TryUse(this._inventory, slot, this._clock.Tick);
    if (!result.IsAccepted)
    {
        this.RejectToSender(sender, result.Rejection);
        return;
    }

    this._inventory = result.Inventory;
}
```

## Netcode for Entities 6.6

| Subject | Fact that decides |
|---|---|
| `ReceiveRpcCommandRequest.SourceConnection` | `Entity` of the connection that sent the RPC [rcr]; the only sender source for an `IRpcCommand` |
| `NetworkId` on the connection entity | Read it from `SourceConnection` to get the sender's id (`netcode-for-entities` → `transport-and-connection.md`) |
| `GhostOwner.NetworkId` | The server sets it to the owning client's `NetworkId.Value` [cmd]; compare it with the sender's for any ghost an RPC names |
| Command data (`IInputComponentData`/`ICommandData`) | Dispatched by `CommandReceiveSystem` to the entity the command belongs to [cmd]; the server sets `CommandTarget` (or `AutoCommandTarget` on an owned ghost), never the client |
| Command values | "Never overwrite or change the input received by the client" [cmd]: validate the effect inside the simulation via Core, not by editing the buffer |
| `NetworkStreamRequestDisconnect { Reason }` | Add to the connection entity to close it [disc] |

**Caveat:** an RPC broadcast target (`TargetConnection = Entity.Null`) is server-only; a client-built `SendRpcCommandRequest` always goes to the server, so `SourceConnection` is never spoofable from the payload.

## MagicOnion

| Subject | Fact that decides |
|---|---|
| `StreamingHubBase.ConnectionId` | `protected Guid ConnectionId => Context.ContextId;` [hub] |
| `ServiceContext.ContextId` | Unique per connection for a StreamingHub, per request for a unary service [life]: a unary `ContextId` never identifies a player across calls |
| Hub instance | One per connection, kept while connected [life]: per-connection state (account id, rate bucket) lives in hub fields |
| `ServiceContext` | Valid only during the request; do not cache it [life] |
| `Context.CallContext.GetHttpContext().User` | Authenticated user under ASP.NET Core auth with `[Authorize]` / `[AllowAnonymous]` [auth]; bind it once in `OnConnecting`/`OnConnected` |
| Method arguments | A hub or service method never takes a user, player or connection id argument |

## Unity Transport (custom protocol)

| Subject | Fact that decides |
|---|---|
| `NetworkConnection` from `driver.Accept()` | The sender identity; events per connection via `driver.PopEventForConnection(conn, out DataStreamReader)` (`unity-transport` → `core-driver-lifecycle.md`) |
| `DataStreamReader.HasFailedReads` | `true` after a read exceeds capacity; scalar reads past the end return 0 [dsr], so check it before trusting any value |
| `driver.Disconnect(conn)` | Closes the connection |

Unverified: whether NGO enforces `InvokePermission` on the server or only on the invoking peer [rpc] (compare the sender server-side regardless); whether NfE `CommandReceiveSystem` checks the sending connection against `GhostOwner` [cmd]; `GetHttpContext().User` inside a StreamingHub (docs show unary only); a server-side force-disconnect member on `StreamingHubBase`; whether scalar `DataStreamReader` reads past the end set `HasFailedReads`.

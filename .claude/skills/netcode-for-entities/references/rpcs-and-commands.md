# RPCs and Commands

Pages (6.6): `rpcs`, `command-stream`.

## RPCs: reliable, one-off
- `IRpcCommand` on a struct generates serialization and registration. RPCs are reliable (snapshots are unreliable) but not persisted: a client connecting later never receives them. No explicit size limit stated.
- Send: create an entity with the RPC struct + `SendRpcCommandRequest`. `TargetConnection = Entity.Null` broadcasts to all clients; a client never sets it (it only talks to the server).
- Receive: a generated system creates an entity with the RPC struct + `ReceiveRpcCommandRequest`; query both, destroy the entity when handled (via an ECB).

```csharp
state.EntityManager.CreateEntity(typeof(OurRpcCommand), typeof(SendRpcCommandRequest));
```

- Low-level path (only when codegen cannot express it): `IRpcCommandSerializer<T>` (`Serialize`/`Deserialize`/`CompileExecute`), queue from `SystemAPI.GetSingleton<RpcCollection>().GetRpcQueue<T, T>()`, then `Schedule(...)`.

## Commands: continuous per-tick input
Prefer `IInputComponentData` (codegen wires the buffer, systems and serializers when baked onto the ghost) over raw `ICommandData` (needs a `Tick` field).

```csharp
public struct PlayerInput : IInputComponentData
{
    public int Horizontal;
    public int Vertical;
    public InputEvent Jump; // edge-triggered, exactly once across partial ticks
}
```

| Stage | Detail |
|---|---|
| Gather | Client, in `GhostInputSystemGroup`; the only place `UnityEngine.Input` may be read |
| Send | Redundant: `ClientTickRate.TargetCommandSlack + NumAdditionalCommandsToSend` older ticks resent with the newest, default total 4 |
| Apply | Inside the prediction loop; replays many times on rollback |

- Inside the prediction loop read only the command buffer, never live input.
- Payload cap: 1024 bytes per command, enforced at serialization.
- Manual serialization: `[NetCodeDisableCommandCodeGen]`, implement `ICommandDataSerializer<T>` with four methods (full and delta serialize/deserialize), register custom `CommandSendSystem`/`CommandReceiveSystem` in `CommandSendSystemGroup`/`CommandReceiveSystemGroup`.
- `CommandDataInterpolationDelay` optionally exposes the client's interpolation delay (used for lag compensation).

## Ownership and targeting

| Component | Role |
|---|---|
| `GhostOwner` / `GhostOwnerIsLocal` | Owning connection; prefer `GhostOwnerIsLocal` for client-side filtering |
| `CommandTarget` | Entity a connection's commands use; set manually without `AutoCommandTarget` |
| `AutoCommandTarget` | Auto-routes to the owned ghost; needs "Has Owner" + "Support Auto Command Target" on the authoring component; not compatible with thin clients by default |

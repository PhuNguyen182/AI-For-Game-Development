# RPCs and Commands — IRpcCommand, ICommandData, IInputComponentData

Sources: [Communicating with RPCs](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/rpcs.html), [Use the command stream to handle inputs](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/command-stream.html).
Covers: SKILL.md §4 — **"Choose RPC or command stream by who initiates and how often"**.

Two different channels for two different jobs: RPCs are reliable, one-off
messages; the command stream is the continuous, redundant, per-tick channel
that carries player input into the prediction loop covered in
[prediction-core.md](prediction-core.md).

## RPCs — reliable, one-off

`IRpcCommand` on a struct auto-generates serialization, deserialization, and
registration. RPCs are sent as **reliable** packets — ghost snapshots are
**unreliable** — but RPC data is **not persisted**: a client that connects
after an RPC was sent never receives it.

**Send** (create an entity with the RPC struct + `SendRpcCommandRequest`):
```csharp
[WorldSystemFilter(WorldSystemFilterFlags.ClientSimulation)]
public partial struct ClientRpcSendSystem : ISystem
{
    public void OnUpdate(ref SystemState state)
    {
        if (Input.GetKey("Space"))
            state.EntityManager.CreateEntity(typeof(OurRpcCommand), typeof(SendRpcCommandRequest));
    }
}
```
`SendRpcCommandRequest.TargetConnection` set to `Entity.Null` broadcasts to
every client; a client never needs to set it, since a client can only ever
send to the server.

**Receive** (a generated system creates the RPC struct + `ReceiveRpcCommandRequest`;
query for both, then destroy the entity once handled):
```csharp
[WorldSystemFilter(WorldSystemFilterFlags.ServerSimulation)]
public partial struct ServerRpcReceiveSystem : ISystem
{
    public void OnUpdate(ref SystemState state)
    {
        var ecb = new EntityCommandBuffer(state.WorldUpdateAllocator);
        foreach (var (command, entity) in SystemAPI.Query<RefRO<OurRpcCommand>>()
                     .WithAll<ReceiveRpcCommandRequest>().WithEntityAccess())
        {
            ecb.DestroyEntity(entity);
        }
        ecb.Playback(state.EntityManager);
    }
}
```

Low-level path (bypassing codegen): implement `IRpcCommandSerializer<T>`
(`Serialize`/`Deserialize`/`CompileExecute`), obtain a queue via
`SystemAPI.GetSingleton<RpcCollection>().GetRpcQueue<T, T>()`, and call
`rpcQueue.Schedule(...)` — reserve this for cases codegen genuinely cannot
express; it exists, but the struct-based path above is the default.

## Commands — continuous, per-tick input

`ICommandData` is the base interface (needs a `Tick` field); prefer
`IInputComponentData` — netcode codegen wires up the buffer, systems, and
serializers from a plain struct placed on the ghost at baking time:

```csharp
public struct PlayerInput : IInputComponentData
{
    public int Horizontal;
    public int Vertical;
    public InputEvent Jump; // edge-triggered, exactly-once semantics across partial ticks
}
```

| Flow stage | Detail | Source |
|---|---|---|
| Gathering | Client-side, runs in `GhostInputSystemGroup`; only place raw `UnityEngine.Input` may be read | [Command stream](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/command-stream.html) |
| Buffering | Generated system copies input into the tick-tagged command buffer | [Command stream](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/command-stream.html) |
| Transmission | Sent with **redundancy** — `ClientTickRate.TargetCommandSlack + ClientTickRate.NumAdditionalCommandsToSend` older ticks resent alongside the newest, default total **4** | [Command stream](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/command-stream.html) |
| Application | Consumed inside the prediction loop; may replay multiple times during rollback | [Command stream](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/command-stream.html) |

**Payload size limit: 1024 bytes**, enforced at serialization into the
outgoing buffer — this is `ICommandData`'s cap, distinct from (and stricter
than) RPCs, which state no explicit size limit.

### Ownership and targeting

| Component | Role | Source |
|---|---|---|
| `GhostOwner` / `GhostOwnerIsLocal` | Identify/filter a ghost's owning connection; prefer `GhostOwnerIsLocal` for client-side filtering | [Command stream](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/command-stream.html) |
| `CommandTarget` | Which entity a connection's commands are read from/written to — set manually unless `AutoCommandTarget` is used | [Command stream](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/command-stream.html) |
| `AutoCommandTarget` | Auto-routes commands to the client's owned ghost — requires "Has Owner" + "Support Auto Command Target" on `GhostAuthoringComponent`; **not compatible with thin clients** by default | [Command stream](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/command-stream.html) |

**Critical caveat**: inside a system that runs in the prediction loop, read
input only from the `ICommandData`/`IInputComponentData` buffer — never
`UnityEngine.Input` directly. Prediction resimulates a tick multiple times
per frame during rollback, and polling live input there produces a
different answer each resimulation, which is client misprediction by
construction, not by bug.

### Manual serialization (advanced)

`[NetCodeDisableCommandCodeGen]` opts a type out of codegen; implement
`ICommandDataSerializer<T>` with **four** methods — full serialize/deserialize
plus delta serialize/deserialize against a baseline — then register custom
`CommandSendSystem`/`CommandReceiveSystem` instances inside
`CommandSendSystemGroup`/`CommandReceiveSystemGroup`. Reserve this for a
command type the generated path genuinely cannot express.

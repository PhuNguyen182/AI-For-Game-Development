# Jobs and the Concurrent API

Sources (`@6.6`): manual `client-server-jobs`; API `NetworkDriver.Concurrent`, `MultiNetworkDriver`, `MultiNetworkDriver.Concurrent`.

Escalation path only: move here once profiling shows the main-thread driver update is the bottleneck.

## Jobified loop

- `ScheduleUpdate()` returns a `JobHandle`. Chain it (`job.Schedule(handle)`) instead of calling `Complete()` so the update and gameplay jobs overlap.
- Server: accepting connections and cleaning up closed ones mutates the shared list, so run it as a plain `IJob` first. Then process each connection's events with `IJobParallelForDefer`.
- Scheduled job fields are copied by value. Anything needed after `Complete()` goes in a `NativeArray`/`NativeList`, not on the job struct.
- `connections.AsDeferredJobArray()` is required for `IJobParallelForDefer` over a `NativeList`; it defers the length read until the job runs.
- Put `[BurstCompile]` on every job struct wrapping `NetworkDriver.Concurrent`.

## NetworkDriver.Concurrent

- Only `driver.ToConcurrent()` creates one. Call it on the main thread, then pass it into the job field.
- Safe only when parallel iterations touch different connections; the type does not detect two touching the same one.
- `EndSend` only enqueues; bytes leave on a later `ScheduleFlushSend` or the next `ScheduleUpdate`. `AbortSend` cancels a writer before `EndSend`.
- Only `PopEventForConnection` exists, no driver-wide `PopEvent`: each iteration must already know its connection.
- `GetMaxSupportedMessageSize` reports the initial path MTU only and never refreshes.
- Called from the main thread outside a job it runs, but forfeits the job dependency tracking that would catch a race with the driver's update job. Use the plain driver there.

```csharp
[BurstCompile]
struct ServerUpdateJob : IJobParallelForDefer
{
    public NetworkDriver.Concurrent Driver;
    [ReadOnly] public NativeArray<NetworkConnection> Connections;

    public void Execute(int index)
    {
        var connection = Connections[index];
        NetworkEvent.Type cmd;
        while ((cmd = Driver.PopEventForConnection(connection, out var stream)) != NetworkEvent.Type.Empty)
        {
            if (cmd == NetworkEvent.Type.Data)
            {
                int value = stream.ReadInt();
                Driver.BeginSend(connection, out var writer);
                writer.WriteInt(value + 1);
                Driver.EndSend(writer);
            }
        }
    }
}
```

## MultiNetworkDriver

- `MaxDriverCount` is 4; `AddDriver` beyond that fails. A topology needing more transports needs a different design.
- Every driver added must already be bound and listening (server role) with no connections, and all drivers must share the same pipeline configuration. `MultiNetworkDriver` takes ownership of them.
- `GetDriverForConnection` resolves a connection's owning driver.
- `multiDriver.ToConcurrent()` exposes only `BeginSend`/`EndSend`/`AbortSend`/`PopEventForConnection`/`GetConnectionState`. Each throws `ArgumentException` for a connection or writer not created by that `MultiNetworkDriver`.

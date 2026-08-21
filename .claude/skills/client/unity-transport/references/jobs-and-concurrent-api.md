# Jobs & the Concurrent API — Jobifying the Driver Update

Sources: [Jobified client and server](https://docs.unity3d.com/Packages/com.unity.transport@6.6/manual/client-server-jobs.html), [NetworkDriver.Concurrent](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetworkDriver.Concurrent.html), [MultiNetworkDriver](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.MultiNetworkDriver.html), [MultiNetworkDriver.Concurrent](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.MultiNetworkDriver.Concurrent.html).
Covers: SKILL.md §4 — **"Reach for the Concurrent driver and pipeline API only inside Burst-compiled jobs"**.

This file owns job-safe, Burst-compiled `NetworkDriver` usage only — moving `ScheduleUpdate`/`PopEvent`/`BeginSend` off the main thread via `NetworkDriver.Concurrent`, and coordinating several drivers via `MultiNetworkDriver`/`MultiNetworkDriver.Concurrent`. The plain main-thread `NetworkDriver` lifecycle (Bind/Listen/Connect, the per-frame `ScheduleUpdate`/`Complete`/`PopEvent` loop) lives in [core-driver-lifecycle.md](core-driver-lifecycle.md); pipeline stage selection lives in [pipelines-reliability-simulation.md](pipelines-reliability-simulation.md). The plain (non-Concurrent) driver API is the default for every feature — this file's API is the escalation branch of SKILL.md §4, reached for only once profiling shows the main-thread driver update is an actual bottleneck, never as a default architecture.

## Jobifying the update loop

| Subject | What it decides | Source |
|---|---|---|
| `ScheduleUpdate()` returns a `JobHandle` | Chain it into the next job (`job.Schedule(handle)`) instead of calling `Complete()` right away — the handle is what lets the driver's own update job and gameplay jobs overlap on separate worker threads. | [Jobified client and server](https://docs.unity3d.com/Packages/com.unity.transport@6.6/manual/client-server-jobs.html) |
| Server split: `IJob` then `IJobParallelForDefer` | Accepting new connections and cleaning up closed ones mutates the shared connection list, so it cannot parallelize — schedule that as a plain `IJob` first, then process each existing connection's events with `IJobParallelForDefer` once that job completes. | [Jobified client and server](https://docs.unity3d.com/Packages/com.unity.transport@6.6/manual/client-server-jobs.html) |
| `NativeArray<NetworkConnection>` for shared state | A scheduled job's fields are copied by value; anything the caller needs after `Complete()` (new connections, updated state) must be written into a `NativeArray`/`NativeList`, never left on the job struct itself. | [Jobified client and server](https://docs.unity3d.com/Packages/com.unity.transport@6.6/manual/client-server-jobs.html) |
| `connections.AsDeferredJobArray()` | Required before scheduling `IJobParallelForDefer` against a `NativeList` — it defers reading the list's length until the job actually runs, so the iteration count matches connections accepted earlier in the same job chain. | [Jobified client and server](https://docs.unity3d.com/Packages/com.unity.transport@6.6/manual/client-server-jobs.html) |
| `[BurstCompile]` | Every `IJob`/`IJobParallelFor(Defer)` struct wrapping `NetworkDriver.Concurrent` should carry it — the driver and pipeline types are Burst-compatible, and this is the entire point of moving the update off the main thread. | [Jobified client and server](https://docs.unity3d.com/Packages/com.unity.transport@6.6/manual/client-server-jobs.html) |

## `NetworkDriver.Concurrent`

| Subject | What it decides | Source |
|---|---|---|
| `driver.ToConcurrent()` | The only way to obtain one — no public constructor. Call it on the main thread before scheduling, then pass the result into the job's own field. | [NetworkDriver.Concurrent](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetworkDriver.Concurrent.html) |
| Per-connection parallelism only | Safe when different job iterations touch different connections; unsafe when two parallel iterations touch the *same* connection — the type does not detect or prevent that itself. | [NetworkDriver.Concurrent](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetworkDriver.Concurrent.html) |
| `BeginSend` / `EndSend` / `AbortSend` | `EndSend` only enqueues the write — it does not put bytes on the wire; the actual send happens on a later `ScheduleFlushSend` or the next `ScheduleUpdate`. `AbortSend` cancels a writer obtained from `BeginSend` before `EndSend` runs. | [NetworkDriver.Concurrent](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetworkDriver.Concurrent.html) |
| `PopEventForConnection` | `Concurrent` exposes only the per-connection pop, not a driver-wide `PopEvent` — a parallel job iteration must already know which connection it owns before it can read events. | [NetworkDriver.Concurrent](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetworkDriver.Concurrent.html) |
| `GetMaxSupportedMessageSize` | Returns the path MTU from the *initial* discovery only — it does not refresh if the path MTU changes mid-session, so re-polling it does not yield a newer answer. | [NetworkDriver.Concurrent](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetworkDriver.Concurrent.html) |

```csharp
[BurstCompile]
struct ServerUpdateJob : IJobParallelForDefer
{
    public NetworkDriver.Concurrent Driver;
    [ReadOnly] public NativeArray<NetworkConnection> Connections;

    public void Execute(int index)
    {
        NetworkConnection connection = this.Connections[index];
        NetworkEvent.Type command;
        while ((command = this.Driver.PopEventForConnection(connection, out DataStreamReader stream)) != NetworkEvent.Type.Empty)
        {
            if (command == NetworkEvent.Type.Data)
            {
                int value = stream.ReadInt();
                this.Driver.BeginSend(connection, out DataStreamWriter writer);
                writer.WriteInt(value + 1);
                this.Driver.EndSend(writer);
            }
        }
    }
}
```

## `MultiNetworkDriver` and `MultiNetworkDriver.Concurrent`

| Subject | What it decides | Source |
|---|---|---|
| `MultiNetworkDriver.MaxDriverCount` | Hard cap of 4 attached drivers per instance — plan a mixed transport list (e.g. UDP + WebSocket) within that limit. | [MultiNetworkDriver](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.MultiNetworkDriver.html) |
| `AddDriver` preconditions | Every driver added must already be bound/listening (server role) with no active connections yet, and all attached drivers must share the same pipeline configuration; `MultiNetworkDriver` takes ownership of what it's given. | [MultiNetworkDriver](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.MultiNetworkDriver.html) |
| `GetDriverForConnection` | Resolves which underlying driver owns a given `NetworkConnection` — needed once traffic is split across more than one transport. | [MultiNetworkDriver](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.MultiNetworkDriver.html) |
| `multiDriver.ToConcurrent()` | Mirrors `NetworkDriver.Concurrent`'s job-safety shape but exposes a reduced set (`BeginSend`/`EndSend`/`AbortSend`/`PopEventForConnection`/`GetConnectionState`); each throws `ArgumentException` if the connection or writer wasn't created by that same `MultiNetworkDriver` instance. | [MultiNetworkDriver.Concurrent](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.MultiNetworkDriver.Concurrent.html) |

## API index

| Type | Source |
|---|---|
| `NetworkDriver.Concurrent` | [NetworkDriver.Concurrent](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.NetworkDriver.Concurrent.html) |
| `MultiNetworkDriver` | [MultiNetworkDriver](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.MultiNetworkDriver.html) |
| `MultiNetworkDriver.Concurrent` | [MultiNetworkDriver.Concurrent](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.MultiNetworkDriver.Concurrent.html) |

**Critical caveat**: calling a `Concurrent` method from the main thread outside a scheduled job compiles and runs — nothing in the type itself stops it — but it forfeits the reason to reach for `Concurrent` at all (no parallel safety is being exercised) and skips the Job System's own read/write dependency tracking, which would otherwise catch a data race against the driver's own main-thread update job. Use the plain `NetworkDriver` API there instead, per [core-driver-lifecycle.md](core-driver-lifecycle.md).

**Critical caveat**: `MultiNetworkDriver.MaxDriverCount` is a fixed constant of 4 — `AddDriver` beyond that count fails, so a topology needing more than four concurrent transport kinds (e.g. UDP, WebSocket, plus two Relay allocations) cannot be expressed with this type and needs a different design, not a workaround.

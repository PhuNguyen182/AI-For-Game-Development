// Burst job: IJobParallelForDefer over connections through NetworkDriver.Concurrent; echoes each Data value plus one.
// Adapt into: Assets/_Project/Scripts/Networking/Server/ServerUpdateJob.cs
// Unverified: not compiled or run (no Unity project in this repo).
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

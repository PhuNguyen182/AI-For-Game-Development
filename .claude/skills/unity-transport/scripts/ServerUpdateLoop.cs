// Main-thread server loop: ScheduleUpdate, prune dead connections, Accept, drain events per connection, echo Data, dispose.
// Adapt into: Assets/_Project/Scripts/Networking/Server/ServerUpdateLoop.cs (MonoBehaviour members only)
// Unverified: not compiled or run (no Unity project in this repo).
void Update()
{
    driver.ScheduleUpdate().Complete();
    for (int i = 0; i < connections.Length; i++)
        if (!connections[i].IsCreated) { connections.RemoveAtSwapBack(i); i--; }

    NetworkConnection c;
    while ((c = driver.Accept()) != default) connections.Add(c);

    for (int i = 0; i < connections.Length; i++)
    {
        NetworkEvent.Type cmd;
        while ((cmd = driver.PopEventForConnection(connections[i], out var stream)) != NetworkEvent.Type.Empty)
        {
            if (cmd == NetworkEvent.Type.Data)
            {
                uint v = stream.ReadUInt();
                driver.BeginSend(NetworkPipeline.Null, connections[i], out var w);
                w.WriteUInt(v);
                driver.EndSend(w);
            }
            else if (cmd == NetworkEvent.Type.Disconnect) { connections[i] = default; break; }
        }
    }
}

void OnDestroy()
{
    if (driver.IsCreated) { driver.Dispose(); connections.Dispose(); }
}

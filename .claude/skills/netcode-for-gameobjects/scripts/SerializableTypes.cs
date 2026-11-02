// INetworkSerializable struct, INetworkSerializeByMemcpy struct and a ForceNetworkSerializeByMemcpy NetworkVariable field.
// Adapt into: Assets/_Project/Scripts/Networking/SerializableTypes.cs
// Unverified: not compiled or run (no Unity project in this repo).
struct SpawnPoint : INetworkSerializable
{
    public Vector3 Position;
    public Quaternion Rotation;

    public void NetworkSerialize<T>(BufferSerializer<T> serializer) where T : IReaderWriter
    {
        serializer.SerializeValue(ref Position);
        serializer.SerializeValue(ref Rotation);
    }
}

public struct MyStruct : INetworkSerializeByMemcpy { public int A; public float C; public bool D; }

public NetworkVariable<ForceNetworkSerializeByMemcpy<Guid>> GuidVar;

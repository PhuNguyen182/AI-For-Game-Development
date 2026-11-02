// Hand-rolled `Health` writer/reader extensions on FastBufferWriter/FastBufferReader.
// Adapt into: Assets/_Project/Scripts/Networking/FastBufferExtensions.cs
// Unverified: not compiled or run (no Unity project in this repo).
public struct Health { public int CurrentHealth; public uint MaxHealth; }

public static class FastBufferExtensions
{
    public static void WriteValueSafe(this FastBufferWriter writer, in Health health)
    {
        writer.WriteValueSafe(health.MaxHealth);
        writer.WriteValueSafe(health.CurrentHealth);
    }

    public static void ReadValueSafe(this FastBufferReader reader, out Health health)
    {
        reader.ReadValueSafe(out uint max);
        reader.ReadValueSafe(out int current);
        health = new Health { MaxHealth = max, CurrentHealth = current };
    }
}

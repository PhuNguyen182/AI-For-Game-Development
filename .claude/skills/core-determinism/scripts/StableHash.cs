// FNV-1a 64 StableHash over a canonical byte sequence: int little-endian, float raw bits, string length then UTF-16 units.
// Adapt into: Assets/_Project/Scripts/Shared/Core/StableHash.cs
// Unverified: not compiled or run (no Unity project in this repo).
using System;

namespace _Project.Scripts.Shared.Core
{
    public static class StableHash
    {
        public const ulong OffsetBasis = 14695981039346656037UL;
        private const ulong Prime = 1099511628211UL;
        private const int BitsPerByte = 8;
        private const int BitsPerInt = 32;

        public static ulong Add(ulong hash, int value)
        {
            unchecked
            {
                for (int shift = 0; shift < BitsPerInt; shift += BitsPerByte)
                {
                    hash ^= (byte)(value >> shift);
                    hash *= Prime;
                }
            }

            return hash;
        }

        public static ulong Add(ulong hash, float value)
        {
            return Add(hash, BitConverter.SingleToInt32Bits(value));
        }

        public static ulong Add(ulong hash, string value)
        {
            hash = Add(hash, value.Length);
            for (int i = 0; i < value.Length; i++)
            {
                hash = Add(hash, (int)value[i]);
            }

            return hash;
        }
    }
}

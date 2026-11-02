// Boundary conversion: a Client float distance becomes Core millimetres under a stated rounding rule and range.
// Adapt into: Assets/_Project/Scripts/Combat/Core/DistanceUnits.cs
// Unverified: not compiled or run (no Unity project in this repo).
using System;

namespace _Project.Scripts.Combat.Core
{
    /// <summary>
    /// Boundary conversion: Client hands a float distance, Core keeps millimetres.
    /// Rounding rule and range are stated so every machine lands on the same integer.
    /// </summary>
    public static class DistanceUnits
    {
        public const int MillimetresPerMetre = 1000;
        public const float MaxMetres = 100000f;

        public static int ToMillimetres(float metres)
        {
            if (float.IsNaN(metres) || metres < -MaxMetres || metres > MaxMetres)
            {
                throw new ArgumentOutOfRangeException(nameof(metres));
            }

            return (int)Math.Round((double)metres * MillimetresPerMetre, MidpointRounding.AwayFromZero);
        }
    }
}

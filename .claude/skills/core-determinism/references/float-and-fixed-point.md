# Float and Fixed-Point

Sources: below the SKILL.md `Docs:` base: [a] `api/system.math.sin` (same remark on `api/system.mathf.sin`), [b] C# spec §8.3.7 `csharp/language-reference/language-specification/types#837-floating-point-types`, [c] C# spec §10.3.2 `csharp/language-reference/language-specification/conversions#1032-explicit-numeric-conversions`; Unity: [d] Burst float determinism https://docs.unity.com/en-us/engine/current/manual/programming-environment/script-compilation/burst/compilation/float-precision-determinism, [e] Unity Issue Tracker "(Apple Silicon) Floating point inconsistencies between mono and il2cpp" https://issuetracker.unity3d.com/issues/apple-silicon-floating-point-inconsistencies-between-mono-and-il2cpp.

## Risk class per float site (SKILL.md step 2)

| Site | Fact that decides | Class |
|---|---|---|
| `Math.Sin/Cos/Tan/Atan2/Pow/Exp/Log`, every `MathF` transcendental | "Calls into the underlying C runtime, and the exact result or valid input range may differ between different operating systems or architectures" [a]. On IL2CPP the C runtime is the target's | High: differs by device |
| `+ − × ÷` on `float`/`double` | The language allows evaluation "with higher precision than the result type"; an explicit cast forces the exact precision [b]. Fused multiply-add or wider intermediates change low bits | Medium: depends on codegen |
| Same code, Mono Editor vs IL2CPP Player | Unity tracks a Mono/IL2CPP float inconsistency on Apple Silicon [e]; no Unity page guarantees managed float agreement across backends or CPUs | Medium: depends on backend |
| `(int)` / `(long)` cast of a float in `unchecked` context | NaN, infinity or out-of-range gives "an unspecified value of the destination type" [c]; the value can differ by CPU | High when the range is not proven |
| `float.Parse`, `ToString()`, `Convert.ToSingle(string)` without `CultureInfo.InvariantCulture` | Current culture decides the decimal separator; a comma-locale device reads balance data differently | High: data, not math |
| Burst job feeding Core | `FloatMode.Deterministic` covers Burst-compiled code only, 64-bit only, flushes subnormals to zero, NaN bits may differ [d]; it does not make Burst agree with managed code | Settings: `unity-burst-compiler` |
| Sums over a hash collection or parallel partitions | Float addition is not associative; order changes the result | High: see [stable-hashing-and-ordering.md](stable-hashing-and-ordering.md) |

**Caveat:** a site that only feeds presentation (interpolation, VFX, camera) is out of scope. Classify only what reaches an outcome, a save or a message.

## Options the decision owner weighs (never chosen here)

| Option | Fact that decides | Owner |
|---|---|---|
| Integer units (ms, centi-HP, mm, basis points) | No codegen or backend risk; needs a stated scale and an overflow bound: max value × scale under `int.MaxValue` (2,147,483,647) or `long` | `technical-architect` |
| Project-owned fixed-point struct (e.g. Q32.32 in `long`) | Needs its own sqrt/trig (table or polynomial), overflow-safe multiply (shift or 128-bit split), and its own tests per operator | `technical-architect` spec, `csharp-engineer` builds |
| Third-party fixed-point library | Project-wide standard, IL2CPP/AOT and licence check, supply-chain review before it lands (`core.md` Security) | `cto` via `/decide`, then `security-reviewer` |
| Float with server authority | Clients may drift; the server's state overwrites theirs each snapshot, so only the server's result counts. Valid only under a state-sync model | `technical-architect`; sync model from `netcode-architecture-decision` |

```csharp
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
```

**Caveat:** the conversion itself runs on each machine. It only removes divergence if the float handed in is already identical, e.g. read from a network message or a recorded input. Quantize at the authority, send the integer.

Unverified: the concrete x64 vs ARM results of an out-of-range float-to-int cast; which C++ compiler flags (FP contraction, FMA) IL2CPP passes per target platform; which libm IL2CPP links on each platform; whether Mono promotes `float` arithmetic to `double` on a given target; the status and affected versions of the issue in [e] (only its title was readable).

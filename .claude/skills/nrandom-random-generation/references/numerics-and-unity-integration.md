# Numerics and Unity Integration

Sources: [a] `src/NRandom.Numerics/NumericsRandomExtensions.cs`, [b] `src/NRandom.Unity/Assets/NRandom.Unity/Runtime/UnityRandomExtensions.cs`, [c] same folder `SerializableWeightedList.cs`, [d] README `#installation`, `#unity` — all at `v2.0.2` (SKILL.md `Docs:` base).

## NRandom.Numerics: `System.Numerics`, no UnityEngine, safe for Core [a]

| Method | Returns |
|---|---|
| `NextVector2/3/4()` | components in `[0,1)`; `(max)` and `(min,max)` overloads |
| `NextVector2Direction()` / `NextVector3Direction()` | unit vector, uniform direction |
| `NextVector2InsideCircle()` / `NextVector3InsideSphere()` | uniform point inside the unit circle/sphere |
| `NextQuaternionRotation()` | unit `System.Numerics.Quaternion`, uniform 3D rotation |

Separate NuGet package `NRandom.Numerics`, installed alongside `NRandom`.

## NRandom.Unity: UnityEngine, Client code only [b][c]

| Member | Fact |
|---|---|
| `NextVector2/3/4`, `NextVector2Direction`, `NextVector3InsideSphere`, `NextQuaternionRotation` | Same as Numerics, on `UnityEngine` types |
| `NextColor()` / `(Color max)` / `(Color min, Color max)` | Componentwise random `Color` |
| `NextColor(Gradient)` | Gradient evaluated at random `[0,1)` |
| `NextColorHSV(hueMin, hueMax, satMin, satMax, valMin, valMax[, alphaMin, alphaMax])` | Independently ranged HSV(A) |
| `SerializableWeightedList<T>` | `WeightedList<T>` + `ISerializationCallbackReceiver`, backed by `[SerializeField] WeightedValue<T>[]`: Inspector-editable, survives domain reload |

**Caveat:** all of this references `UnityEngine` and stays out of Core (`csharp-standards` → `naming-convention.md`, Folders). Author tables in Client code via `SerializableWeightedList<T>`, but resolve the gameplay-affecting roll through the same injected `IRandom` that Core uses.

## Installation [d]

| Target | Steps |
|---|---|
| Pure .NET | `dotnet add package NRandom` |
| Unity (2021.3+) | Install NugetForUnity; `NuGet > Manage NuGet Packages`, install `NRandom`; Package Manager `[+] > Add package from git URL`: `https://github.com/nuskey8/NRandom.git?path=src/NRandom.Unity/Assets/NRandom.Unity` |

The git-URL package only adds the `NRandom.Unity` extensions over the NuGet-installed core; it does not replace it.

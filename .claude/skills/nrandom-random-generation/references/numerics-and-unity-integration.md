# Numerics and Unity Integration — NRandom.Numerics, NRandom.Unity, Installation

Source: [NumericsRandomExtensions.cs](https://github.com/nuskey8/NRandom/blob/v2.0.2/src/NRandom.Numerics/NumericsRandomExtensions.cs), [UnityRandomExtensions.cs](https://github.com/nuskey8/NRandom/blob/v2.0.2/src/NRandom.Unity/Assets/NRandom.Unity/Runtime/UnityRandomExtensions.cs), [SerializableWeightedList.cs](https://github.com/nuskey8/NRandom/blob/v2.0.2/src/NRandom.Unity/Assets/NRandom.Unity/Runtime/SerializableWeightedList.cs), [README — Unity section](https://github.com/nuskey8/NRandom/blob/v2.0.2/README.md#unity).
Covers: SKILL.md §4 — **"Use `NRandom.Numerics` in `Game.Core.*` and `NRandom.Unity` only in `Game.Client.*`"**.

Vector/Quaternion/Color randomization and the Unity package's installation
path. `rng-algorithms-and-determinism.md` owns which `IRandom` instance
these extension methods are called on.

## NRandom.Numerics (`System.Numerics` types — no UnityEngine dependency, safe for Game.Core.*)

| Method | Returns | Source |
|---|---|---|
| `NextVector2()` / `NextVector3()` / `NextVector4()` | components in `[0,1)`; overloaded for `(max)` and `(min,max)` using `System.Numerics.Vector2/3/4` | [NumericsRandomExtensions.cs](https://github.com/nuskey8/NRandom/blob/v2.0.2/src/NRandom.Numerics/NumericsRandomExtensions.cs) |
| `NextVector2Direction()` / `NextVector3Direction()` | unit-length vector, uniformly random direction | [NumericsRandomExtensions.cs](https://github.com/nuskey8/NRandom/blob/v2.0.2/src/NRandom.Numerics/NumericsRandomExtensions.cs) |
| `NextVector2InsideCircle()` / `NextVector3InsideSphere()` | uniformly random point inside the unit circle/sphere | [NumericsRandomExtensions.cs](https://github.com/nuskey8/NRandom/blob/v2.0.2/src/NRandom.Numerics/NumericsRandomExtensions.cs) |
| `NextQuaternionRotation()` | unit `System.Numerics.Quaternion`, uniformly random 3D rotation | [NumericsRandomExtensions.cs](https://github.com/nuskey8/NRandom/blob/v2.0.2/src/NRandom.Numerics/NumericsRandomExtensions.cs) |

Ships as a separate NuGet package (`NRandom.Numerics`) — install it alongside
`NRandom` when `Game.Core.*` code needs vector/rotation randomization
without pulling in `UnityEngine`.

## NRandom.Unity (`UnityEngine` types — Game.Client.* only)

| Member | Effect | Source |
|---|---|---|
| `NextVector2/3/4`, `NextVector2Direction`, `NextVector3InsideSphere`, `NextQuaternionRotation` | Same methods as `NRandom.Numerics`, re-implemented against `UnityEngine.Vector2/3/4`/`Quaternion` instead of `System.Numerics`. | [UnityRandomExtensions.cs](https://github.com/nuskey8/NRandom/blob/v2.0.2/src/NRandom.Unity/Assets/NRandom.Unity/Runtime/UnityRandomExtensions.cs) |
| `NextColor()` / `NextColor(Color max)` / `NextColor(Color min, Color max)` | Random `UnityEngine.Color`, componentwise. | [UnityRandomExtensions.cs](https://github.com/nuskey8/NRandom/blob/v2.0.2/src/NRandom.Unity/Assets/NRandom.Unity/Runtime/UnityRandomExtensions.cs) |
| `NextColor(Gradient gradient)` | Evaluates a `UnityEngine.Gradient` at a random `[0,1)` position. | [UnityRandomExtensions.cs](https://github.com/nuskey8/NRandom/blob/v2.0.2/src/NRandom.Unity/Assets/NRandom.Unity/Runtime/UnityRandomExtensions.cs) |
| `NextColorHSV(hueMin, hueMax, satMin, satMax, valMin, valMax[, alphaMin, alphaMax])` | Random color built from independently ranged HSV(A) components. | [UnityRandomExtensions.cs](https://github.com/nuskey8/NRandom/blob/v2.0.2/src/NRandom.Unity/Assets/NRandom.Unity/Runtime/UnityRandomExtensions.cs) |
| `SerializableWeightedList<T>` | `WeightedList<T>` subclass implementing `ISerializationCallbackReceiver`, backed by a `[SerializeField] WeightedValue<T>[]` — makes a loot table Inspector-editable and survives domain reload. | [SerializableWeightedList.cs](https://github.com/nuskey8/NRandom/blob/v2.0.2/src/NRandom.Unity/Assets/NRandom.Unity/Runtime/SerializableWeightedList.cs) |

**Critical caveat**: `NRandom.Unity`'s Vector/Quaternion/Color methods and
`SerializableWeightedList<T>` all reference `UnityEngine` — per
`naming-convention.md`'s namespace boundary, none of this belongs in
`Game.Core.*`. Author the table/weights in `Game.Client.*` via
`SerializableWeightedList<T>` for Inspector authoring, but resolve the actual
gameplay-affecting roll through the same injected `IRandom` that
`Game.Core.*` uses, per
[rng-algorithms-and-determinism.md](rng-algorithms-and-determinism.md).

## Installation

| Target | Steps | Source |
|---|---|---|
| Pure .NET | `dotnet add package NRandom` (NuGet, requires .NET Standard 2.1+) | [README — Installation](https://github.com/nuskey8/NRandom/blob/v2.0.2/README.md#installation) |
| Unity | 1. Install [NugetForUnity](https://github.com/GlitchEnzo/NuGetForUnity). 2. `NuGet > Manage NuGet Packages`, search `NRandom`, install. 3. Package Manager → `[+] > Add package from git URL` → `https://github.com/nuskey8/NRandom.git?path=src/NRandom.Unity/Assets/NRandom.Unity` | [README — Unity](https://github.com/nuskey8/NRandom/blob/v2.0.2/README.md#unity) |

Requires Unity 2021.3 or higher and NugetForUnity. The Unity git-URL package
only adds the `NRandom.Unity` extension methods on top of the
NuGet-installed core — it is not a standalone replacement for the core
`NRandom` package.

# Getting Started — Installation, Package Layout, Supported Types

Sources: [Installation](https://annulusgames.github.io/LitMotion/articles/en/installation.html), [Quick Start](https://annulusgames.github.io/LitMotion/articles/en/quick-start.html), [Package Structure](https://annulusgames.github.io/LitMotion/articles/en/package-structure.html), [Supported Types](https://annulusgames.github.io/LitMotion/articles/en/supported-types.html), [FAQ](https://annulusgames.github.io/LitMotion/articles/en/faq.html).
Covers: SKILL.md §4 — **"Pick the `LMotion.Create` overload matching the value's built-in type"**, **"Verify the zero-allocation and Burst claims with the Profiler before shipping a hot-path or high-volume motion"**.

Settles what to install, which namespace a symbol lives in, and which value
types `LMotion.Create` accepts without a custom adapter.

## Requirements and installation

| Item | Requirement | Source |
|---|---|---|
| Unity | 2021.3 or later | [Installation](https://annulusgames.github.io/LitMotion/articles/en/installation.html) |
| `com.unity.burst` | 1.6.0 or later — required for the performance/zero-allocation claims | [Installation](https://annulusgames.github.io/LitMotion/articles/en/installation.html) |
| `com.unity.collections` | 1.5.1 or later | [Installation](https://annulusgames.github.io/LitMotion/articles/en/installation.html) |
| `com.unity.mathematics` | 1.0.0 or later | [Installation](https://annulusgames.github.io/LitMotion/articles/en/installation.html) |
| `LitMotion.Animation` package | Additionally needs LitMotion 2.0.0+ itself | [litmotion-animation-installation](https://annulusgames.github.io/LitMotion/articles/en/litmotion-animation-installation.html) |

| Install method | How | Source |
|---|---|---|
| Package Manager (recommended) | Add package from git URL: `https://github.com/annulusgames/LitMotion.git?path=src/LitMotion/Assets/LitMotion` | [Installation](https://annulusgames.github.io/LitMotion/articles/en/installation.html) |
| `manifest.json` | `"com.annulusgames.lit-motion": "https://github.com/annulusgames/LitMotion.git?path=src/LitMotion/Assets/LitMotion"` | [Installation](https://annulusgames.github.io/LitMotion/articles/en/installation.html) |
| `LitMotion.Animation` (separate package) | Same pattern with `?path=src/LitMotion/Assets/LitMotion.Animation` and id `com.annulusgames.lit-motion.animation` | [litmotion-animation-installation](https://annulusgames.github.io/LitMotion/articles/en/litmotion-animation-installation.html) |
| `.unitypackage` | Download from GitHub Releases and import | [Installation](https://annulusgames.github.io/LitMotion/articles/en/installation.html) |

## Package / namespace layout

| Namespace | Holds | Source |
|---|---|---|
| `LitMotion` | Core: `LMotion`, `MotionBuilder<T,TOptions,TAdapter>`, `MotionHandle`, `LSequence`, options/enums | [Package Structure](https://annulusgames.github.io/LitMotion/articles/en/package-structure.html) |
| `LitMotion.Adapters` | Built-in `IMotionAdapter` implementations for primitives and Unity value types | [Package Structure](https://annulusgames.github.io/LitMotion/articles/en/package-structure.html) |
| `LitMotion.Editor` | `EditorMotionScheduler` and Edit Mode driving | [Package Structure](https://annulusgames.github.io/LitMotion/articles/en/package-structure.html) |
| `LitMotion.Extensions` | `BindTo*` extension methods for Unity components — a separate asmdef | [Package Structure](https://annulusgames.github.io/LitMotion/articles/en/package-structure.html) |
| `LitMotion.Animation` | Inspector-driven `LitMotionAnimation` component — separate package | [Package Structure](https://annulusgames.github.io/LitMotion/articles/en/package-structure.html) |

**Critical caveat**: `LMotion.Create()` itself works without referencing `LitMotion.Extensions` — but every `BindTo*` method (the recommended binding path in [component-bindings.md](component-bindings.md)) requires `using LitMotion.Extensions;` and a reference to that asmdef.

## Supported built-in value types

`LMotion.Create(from, to, duration)` resolves directly to a built-in
`IMotionAdapter` for these types; anything else needs
[custom-adapters.md](custom-adapters.md).

| Type | Options type | Source |
|---|---|---|
| `int`, `long` | `IntegerOptions` (rounding mode) | [Supported Types](https://annulusgames.github.io/LitMotion/articles/en/supported-types.html) |
| `float`, `double` | `NoOptions` | [Supported Types](https://annulusgames.github.io/LitMotion/articles/en/supported-types.html) |
| `Vector2`, `Vector3`, `Vector4` | `NoOptions` | [Supported Types](https://annulusgames.github.io/LitMotion/articles/en/supported-types.html) |
| `Quaternion` | `NoOptions` | [Supported Types](https://annulusgames.github.io/LitMotion/articles/en/supported-types.html) |
| `Color`, `Rect` | `NoOptions` | [Supported Types](https://annulusgames.github.io/LitMotion/articles/en/supported-types.html) |
| `FixedString32/64/128/512/4096Bytes` | `StringOptions` (scramble/rich text) | see [text-and-tmp-animation.md](text-and-tmp-animation.md) |

```csharp
using UnityEngine;
using LitMotion;
using LitMotion.Extensions;

public class Example : MonoBehaviour
{
    [SerializeField] Transform target;

    void Start()
    {
        LMotion.Create(Vector3.zero, Vector3.one, 2f) // 0..1 over 2 seconds
            .BindToPosition(target);
    }
}
```

**Critical caveat**: LitMotion deliberately has no `DelayedCall()`-style API — the FAQ states this is by design, since callback-based delays swallow exceptions. Use `WithOnComplete()` on a zero-length or short motion, or an `async` method, per [async-lifecycle-and-debugging.md](async-lifecycle-and-debugging.md).

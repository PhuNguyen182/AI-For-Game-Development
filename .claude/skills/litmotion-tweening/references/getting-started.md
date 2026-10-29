# Getting Started — Install, Namespaces, Supported Types

Sources (under the Docs base): installation, quick-start, package-structure, supported-types, faq, litmotion-animation-installation.

## Requirements and install

| Item | Fact |
|---|---|
| Unity | 2021.3+ |
| `com.unity.burst` | 1.6.0+; required for the zero-allocation/performance claims |
| `com.unity.collections` / `com.unity.mathematics` | 1.5.1+ / 1.0.0+ |
| Package Manager git URL (or `manifest.json` id `com.annulusgames.lit-motion`) | `https://github.com/annulusgames/LitMotion.git?path=src/LitMotion/Assets/LitMotion` |
| `LitMotion.Animation` | Separate package, id `com.annulusgames.lit-motion.animation`, same URL with `?path=src/LitMotion/Assets/LitMotion.Animation`; needs LitMotion 2.0.0+ |
| `.unitypackage` | GitHub Releases; integration defines (`LITMOTION_SUPPORT_*`) must then be added by hand |

## Namespaces

| Namespace | Holds |
|---|---|
| `LitMotion` | `LMotion`, `MotionBuilder`, `MotionHandle`, `LSequence`, options and enums |
| `LitMotion.Adapters` | Built-in `IMotionAdapter`s |
| `LitMotion.Editor` | `EditorMotionScheduler` |
| `LitMotion.Extensions` | All `BindTo*` methods; separate asmdef |
| `LitMotion.Animation` | Inspector component; separate package |

**Caveat:** `LMotion.Create` works without `LitMotion.Extensions`, but every `BindTo*` needs `using LitMotion.Extensions;` plus the asmdef reference.

## Built-in value types (anything else needs [custom-adapters.md](custom-adapters.md))

| Type | Options |
|---|---|
| `int`, `long` | `IntegerOptions` (rounding mode) |
| `float`, `double`, `Vector2/3/4`, `Quaternion`, `Color`, `Rect` | `NoOptions` |
| `FixedString32/64/128/512/4096Bytes` | `StringOptions`; see [text-and-tmp-animation.md](text-and-tmp-animation.md) |

```csharp
LMotion.Create(Vector3.zero, Vector3.one, 2f).BindToPosition(target);
```

**Caveat:** there is deliberately no `DelayedCall()` (callback delays swallow exceptions); see [migration-and-rx-integration.md](migration-and-rx-integration.md).

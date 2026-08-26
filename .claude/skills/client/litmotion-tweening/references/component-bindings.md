# Component Bindings — `LitMotion.Extensions` Catalogue & Custom Binding Extensions

Sources: [Binding](https://annulusgames.github.io/LitMotion/articles/en/binding.html), [Custom Binding Extension Method](https://annulusgames.github.io/LitMotion/articles/en/custom-binding-extension-method.html), verified against the source files under [`Runtime/Extensions`](https://github.com/annulusgames/LitMotion/tree/main/src/LitMotion/Assets/LitMotion/Runtime/Extensions).
Covers: SKILL.md §4 — **"Bind with a built-in `LitMotion.Extensions` `BindTo*` method before writing a manual `Bind()` lambda"**.

Requires `using LitMotion.Extensions;`. Naming follows a consistent pattern:
the property name, with an axis suffix (`X`/`Y`/`Z`/`XY`/`XZ`/`YZ`) selecting
a `float`/`Vector2` slice of a `Vector3`/`Vector4` property. Not every method
below is listed individually — the axis pattern generalizes once one example
per property is known. Text/TextMeshPro bindings live in
[text-and-tmp-animation.md](text-and-tmp-animation.md) instead.

## Table of contents
- [Transform](#transform)
- [RectTransform / uGUI](#recttransform--ugui)
- [Rendering & rigidbody](#rendering--rigidbody)
- [Camera, audio, misc](#camera-audio-misc)
- [Custom binding extension method](#custom-binding-extension-method)

## Transform

| Property family | Full + per-axis members | Source |
|---|---|---|
| World position | `BindToPosition` (`Vector3`), `BindToPositionX/Y/Z` (`float`), `BindToPositionXY/XZ/YZ` (`Vector2`) | [`LitMotionTransformExtensions.cs`](https://github.com/annulusgames/LitMotion/blob/main/src/LitMotion/Assets/LitMotion/Runtime/Extensions/General/LitMotionTransformExtensions.cs) |
| Local position | `BindToLocalPosition` + same axis family | same |
| World / local rotation | `BindToRotation`, `BindToLocalRotation` (`Quaternion`) | same |
| Euler / local euler angles | `BindToEulerAngles`, `BindToLocalEulerAngles` + axis family | same |
| Local scale | `BindToLocalScale` + axis family, plus `BindToLocalScaleXYZ(float)` for uniform scale | same |

## RectTransform / uGUI

These bind to the same `Canvas`/`RectTransform`/`Graphic` components the
`ugui` skill owns the non-tweening side of (layout, event wiring, Inspector
setup) — see its
[rect-transform-and-layout.md](../../ugui/references/rect-transform-and-layout.md)
before binding a size/position property a Layout Group or Content Size
Fitter also controls, to avoid the two fighting over the same value.

| Property | Members | Source |
|---|---|---|
| Anchored position | `BindToAnchoredPosition` (`Vector2`) + `X`/`Y`; `BindToAnchoredPosition3D` (`Vector3`) + `X`/`Y`/`Z` | [`LitMotionRectTransformExtensions.cs`](https://github.com/annulusgames/LitMotion/blob/main/src/LitMotion/Assets/LitMotion/Runtime/Extensions/uGUI/LitMotionRectTransformExtensions.cs) |
| Anchors / pivot / size | `BindToAnchorMin/Max`, `BindToPivot(+X/Y)`, `BindToSizeDelta(+X/Y)` (`Vector2`/`float`) | same |
| `Graphic` color | `BindToColor` (`Color`), `BindToColorR/G/B/A` (`float`) — works on any `UnityEngine.UI.Graphic` | [`LitMotionUGUIExtensions.cs`](https://github.com/annulusgames/LitMotion/blob/main/src/LitMotion/Assets/LitMotion/Runtime/Extensions/uGUI/LitMotionUGUIExtensions.cs) |
| `Image.fillAmount` | `BindToFillAmount(float)` | same |
| `CanvasGroup.alpha` | `BindToAlpha(float)` | same |
| Legacy `Text` | `BindToFontSize(int)`, `BindToText(...)` numeric/string overloads — see [text-and-tmp-animation.md](text-and-tmp-animation.md) | same |

## Rendering & rigidbody

| Target | Members | Source |
|---|---|---|
| `Material` | `BindToMaterialFloat(name/nameID)`, `BindToMaterialInt(name/nameID)`, `BindToMaterialColor(name/nameID)` | [`LitMotionMaterialExtensions.cs`](https://github.com/annulusgames/LitMotion/blob/main/src/LitMotion/Assets/LitMotion/Runtime/Extensions/General/LitMotionMaterialExtensions.cs) |
| `SpriteRenderer` | `BindToColor`, `BindToColorR/G/B/A` | [`LitMotionSpriteRendererExtensions.cs`](https://github.com/annulusgames/LitMotion/blob/main/src/LitMotion/Assets/LitMotion/Runtime/Extensions/General/LitMotionSpriteRendererExtensions.cs) |
| URP `Volume` | `BindToWeight(float)` | [`LitMotionVolumeExtensions.cs`](https://github.com/annulusgames/LitMotion/blob/main/src/LitMotion/Assets/LitMotion/Runtime/Extensions/Rendering/LitMotionVolumeExtensions.cs) |
| `Rigidbody` | `BindToPosition(+X/Y/Z/XY/YZ/XZ, bool useMovePosition = true)`, `BindToRotation(bool useMoveRotation = true)` | [`LitMotionRigidbodyExtensions.cs`](https://github.com/annulusgames/LitMotion/blob/main/src/LitMotion/Assets/LitMotion/Runtime/Extensions/General/LitMotionRigidbodyExtensions.cs) |
| `Rigidbody2D` | `BindToPosition(+X/Y, bool useMovePosition = true)`, `BindToRotation(bool)` (`float` degrees) | [`LitMotionRigidbody2DExtensions.cs`](https://github.com/annulusgames/LitMotion/blob/main/src/LitMotion/Assets/LitMotion/Runtime/Extensions/General/LitMotionRigidbody2DExtensions.cs) |

**Critical caveat**: `BindToPosition`/`BindToRotation` on `Rigidbody`/`Rigidbody2D` default `useMovePosition`/`useMoveRotation` to `true` (uses `MovePosition`/`MoveRotation`, correct under physics simulation) — set it `false` only when the object is kinematic and a direct transform write is intended instead, and prefer `MotionScheduler.FixedUpdate` (per [motion-settings.md](motion-settings.md)) so the write lands on the physics tick.

## Camera, audio, misc

| Target | Members | Source |
|---|---|---|
| `Camera` | `BindToAspect`, `BindToNearClipPlane`, `BindToFarClipPlane`, `BindToFieldOfView`, `BindToOrthographicSize`, `BindToRect`/`BindToPixelRect` (`Rect`), `BindToBackgroundColor` | [`LitMotionCameraExtensions.cs`](https://github.com/annulusgames/LitMotion/blob/main/src/LitMotion/Assets/LitMotion/Runtime/Extensions/General/LitMotionCameraExtensions.cs) |
| `AudioSource` | `BindToVolume`, `BindToPitch` | [`LitMotionAudioExtensions.cs`](https://github.com/annulusgames/LitMotion/blob/main/src/LitMotion/Assets/LitMotion/Runtime/Extensions/General/LitMotionAudioExtensions.cs) |
| `AudioMixer` | `BindToAudioMixerFloat(name)` | same |
| Debug output | `BindToUnityLogger()` (+ `format`/`ILogger` overloads) | [`LitMotionLoggerExtensions.cs`](https://github.com/annulusgames/LitMotion/blob/main/src/LitMotion/Assets/LitMotion/Runtime/Extensions/General/LitMotionLoggerExtensions.cs) |
| `IProgress<T>` | `BindToProgress(IProgress<TValue>)` | [`LitMotionProgressExtensions.cs`](https://github.com/annulusgames/LitMotion/blob/main/src/LitMotion/Assets/LitMotion/Runtime/Extensions/General/LitMotionProgressExtensions.cs) |
| R3/UniRx `ReactiveProperty<T>` | `BindToReactiveProperty(...)` | [migration-and-rx-integration.md](migration-and-rx-integration.md) |

## Custom binding extension method

Write one only once the same property is bound at more than one call site,
per SKILL.md §4's YAGNI guard on this — before that, a plain `Bind()` call is
simpler.

```csharp
public class Foo { public float Value { get; set; } }

public static class FooMotionExtensions
{
    public static MotionHandle BindToFooValue<TOptions, TAdapter>(
        this MotionBuilder<float, TOptions, TAdapter> builder, Foo target)
        where TOptions : unmanaged, IMotionOptions
        where TAdapter : unmanaged, IMotionAdapter<float, TOptions>
    {
        // Bind(TState, Action<T,TState>) avoids the closure a lambda would need
        return builder.Bind(target, (x, state) => state.Value = x);
    }
}
```

Generic over `TOptions`/`TAdapter` so the extension works for any motion
producing a `float`, regardless of which built-in or custom adapter created
it — source: [Custom Binding Extension Method](https://annulusgames.github.io/LitMotion/articles/en/custom-binding-extension-method.html).

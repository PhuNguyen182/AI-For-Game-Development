# Component Bindings (`LitMotion.Extensions`)

Sources (under the Docs base): binding, custom-binding-extension-method; source `Runtime/Extensions/{General,uGUI,Rendering,TextMeshPro}`.

Needs `using LitMotion.Extensions;`. Axis suffixes `X/Y/Z` (`float`) and `XY/XZ/YZ` (`Vector2`) slice a `Vector3` property; only one example per property is listed. Text/TMP bindings: [text-and-tmp-animation.md](text-and-tmp-animation.md).

| Target | Members |
|---|---|
| Transform position | `BindToPosition`, `BindToLocalPosition` + axis family |
| Transform rotation | `BindToRotation`, `BindToLocalRotation` (`Quaternion`); `BindToEulerAngles`, `BindToLocalEulerAngles` + axis family |
| Transform scale | `BindToLocalScale` + axis family; `BindToLocalScaleXYZ(float)` uniform |
| `RectTransform` | `BindToAnchoredPosition` (+X/Y), `BindToAnchoredPosition3D` (+X/Y/Z), `BindToAnchorMin/Max`, `BindToPivot`, `BindToSizeDelta` |
| uGUI | `Graphic`: `BindToColor`, `BindToColorR/G/B/A`; `Image`: `BindToFillAmount`; `CanvasGroup`: `BindToAlpha`; legacy `Text`: `BindToFontSize` |
| `Material` | `BindToMaterialFloat`, `BindToMaterialInt`, `BindToMaterialColor` (each by name or nameID) |
| `SpriteRenderer` | `BindToColor`, `BindToColorR/G/B/A` |
| URP `Volume` | `BindToWeight` |
| `Rigidbody` | `BindToPosition` (+axis, `bool useMovePosition = true`), `BindToRotation(bool useMoveRotation = true)` |
| `Rigidbody2D` | `BindToPosition` (+X/Y, `useMovePosition = true`), `BindToRotation` (degrees) |
| `Camera` | `BindToAspect`, `BindToNearClipPlane`, `BindToFarClipPlane`, `BindToFieldOfView`, `BindToOrthographicSize`, `BindToRect`, `BindToPixelRect`, `BindToBackgroundColor` |
| `AudioSource` / `AudioMixer` | `BindToVolume`, `BindToPitch` / `BindToAudioMixerFloat(name)` |
| Misc | `BindToUnityLogger()`, `BindToProgress(IProgress<T>)`, `BindToReactiveProperty` ([migration-and-rx-integration.md](migration-and-rx-integration.md)) |

**Caveat:** Rigidbody bindings default to `MovePosition`/`MoveRotation`; pass `false` only for a kinematic direct write, and use `MotionScheduler.FixedUpdate` so the write lands on the physics tick.

**Caveat:** before binding a size/position a Layout Group or Content Size Fitter also drives, read `ugui` `rect-transform-and-layout.md`.

## Custom binding extension

Only once the same property is bound at 2+ call sites.

```csharp
public static MotionHandle BindToFooValue<TOptions, TAdapter>(
    this MotionBuilder<float, TOptions, TAdapter> builder, Foo target)
    where TOptions : unmanaged, IMotionOptions
    where TAdapter : unmanaged, IMotionAdapter<float, TOptions>
{
    return builder.Bind(target, (x, state) => state.Value = x); // state overload: no closure
}
```

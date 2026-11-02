# LitMotion.Animation — Inspector-Authored Animation

Sources (under the Docs base): litmotion-animation-overview, litmotion-animation-installation, litmotion-animation, litmotion-animation-script, custom-animation-component; source `LitMotion.Animation/Runtime`. Install: [getting-started.md](getting-started.md).

## `LitMotionAnimation` component

| Setting | Fact |
|---|---|
| Play On Awake | Starts on `Awake` |
| Animation Mode `Parallel` / `Sequential` | All Animation Components at once / one after another in list order |
| Debug panel | **Play** preview in Edit and Play Mode |

Animation Components are added with **Add...**. Built-in ones mirror [component-bindings.md](component-bindings.md): Transform, RectTransform, Renderer/UGUI, TextMeshPro, Camera, Audio, Rigidbody/Rigidbody2D, plus Value and Control components.

```csharp
animation.Play();     // play or resume
animation.Pause();
animation.Stop();
animation.Restart();
```

## Custom Animation Components

Inherit `LitMotionAnimationComponent` (full control) or `PropertyAnimationComponent<TObject,TValue,TOptions,TAdapter>` (typed shortcuts such as `FloatPropertyAnimationComponent<TObject>`, `Vector3PropertyAnimationComponent<TObject>`), which handles motion creation and restoration; override only `GetValue`/`SetValue`.

- **Sample:** [CustomAnimationComponents.cs](../scripts/CustomAnimationComponents.cs) — two `[Serializable]` classes. `CustomAnimation : LitMotionAnimationComponent` is a skeleton under `[LitMotionAnimationComponentMenu("Custom/Custom Animation")]`: its `Play()` body is a placeholder comment (create and return the `MotionHandle`) and does not compile until filled; `OnPause` and `OnResume` are empty, `OnStop` must restore the original value. `SliderValueAnimation : FloatPropertyAnimationComponent<Slider>` under `"UI/Slider/Value"` overrides `GetValue` (`target.value`) and `SetValue` (`target.value = value`) and is complete.
  - **Adapt into:** `Assets/_Project/Scripts/<Feature>/Views/CustomAnimationComponents.cs`; fill the `Play()` placeholder first; the file keeps a 3-line header marking it unverified.

`[LitMotionAnimationComponentMenu("Path/Name")]` sets the **Add...** menu label.

**Caveat:** a direct `LitMotionAnimationComponent` must restore the value in `OnStop()`, or the property stays at its last interpolated value.

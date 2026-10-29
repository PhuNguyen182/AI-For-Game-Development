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

```csharp
[Serializable]
[LitMotionAnimationComponentMenu("Custom/Custom Animation")]
public class CustomAnimation : LitMotionAnimationComponent
{
    public override MotionHandle Play() { /* create and return the MotionHandle */ }
    public override void OnPause() { }
    public override void OnResume() { }
    public override void OnStop() { /* restore the original value */ }
}

[Serializable]
[LitMotionAnimationComponentMenu("UI/Slider/Value")]
public sealed class SliderValueAnimation : FloatPropertyAnimationComponent<Slider>
{
    protected override float GetValue(Slider target) => target.value;
    protected override void SetValue(Slider target, in float value) => target.value = value;
}
```

`[LitMotionAnimationComponentMenu("Path/Name")]` sets the **Add...** menu label.

**Caveat:** a direct `LitMotionAnimationComponent` must restore the value in `OnStop()`, or the property stays at its last interpolated value.

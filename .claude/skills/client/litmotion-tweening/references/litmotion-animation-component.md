# LitMotion.Animation — Inspector-Authored Animation Package

Sources: [Overview](https://annulusgames.github.io/LitMotion/articles/en/litmotion-animation-overview.html), [Installation](https://annulusgames.github.io/LitMotion/articles/en/litmotion-animation-installation.html), [LitMotion Animation](https://annulusgames.github.io/LitMotion/articles/en/litmotion-animation.html), [Control from C#](https://annulusgames.github.io/LitMotion/articles/en/litmotion-animation-script.html), [Custom Animation Component](https://annulusgames.github.io/LitMotion/articles/en/custom-animation-component.html), verified against the [`LitMotion.Animation` source](https://github.com/annulusgames/LitMotion/tree/main/src/LitMotion/Assets/LitMotion.Animation/Runtime).
Covers: SKILL.md §4 — **"Reach for the `LitMotion.Animation` package only when the animation is meant to be authored/iterated in the Inspector"**.

A separate package (own asmdef, own install URL — see
[getting-started.md](getting-started.md)) built on top of the core LitMotion
package, adding the `LitMotionAnimation` component so animations can be
authored and previewed directly in the Inspector instead of in code.

## Table of contents
- [`LitMotionAnimation` component](#litmotionanimation-component)
- [Controlling from C#](#controlling-from-c)
- [Built-in Animation Component categories](#built-in-animation-component-categories)
- [Custom Animation Components](#custom-animation-components)

## `LitMotionAnimation` component

| Setting | Effect | Source |
|---|---|---|
| Play On Awake | Animation starts automatically on `Awake` | [LitMotion Animation](https://annulusgames.github.io/LitMotion/articles/en/litmotion-animation.html) |
| Animation Mode: `Parallel` | Every Animation Component on this `LitMotionAnimation` plays simultaneously | same |
| Animation Mode: `Sequential` | Animation Components play one after another, in list order | same |
| Debug panel | Preview playback with a **Play** button, in both Edit Mode and Play Mode | same |

Animation Components are added via the **Add...** button in the Inspector;
built-in ones cover the major Unity component categories, and custom ones
can be authored per [Custom Animation Components](#custom-animation-components) below.

## Controlling from C#

```csharp
LitMotionAnimation animation;
animation.Play();     // play or resume
animation.Pause();
animation.Stop();
animation.Restart();  // restart from the beginning
```

Source: [Control LitMotion Animation from C#](https://annulusgames.github.io/LitMotion/articles/en/litmotion-animation-script.html).

## Built-in Animation Component categories

Grouped by source file under [`Runtime/Components`](https://github.com/annulusgames/LitMotion/tree/main/src/LitMotion/Assets/LitMotion.Animation/Runtime/Components) — each exposes the same properties `component-bindings.md` documents for code-driven `BindTo*` calls, but wired through the Inspector's **Add...** menu instead.

| Category | Covers | Source |
|---|---|---|
| Transform | Position/rotation/scale, matching [component-bindings.md](component-bindings.md)'s Transform table | `TransformComponents.cs` |
| RectTransform | Anchored position/size/anchors/pivot | `RectTransformComponents.cs` |
| Renderer / UGUI | Material, SpriteRenderer, `Graphic` color, `Image.fillAmount`, `CanvasGroup.alpha` | `RendererComponents.cs`, `UGUIComponents.cs` |
| TextMeshPro | Text-level and per-character properties | `TextMeshProComponents.cs` |
| Camera | FOV, orthographic size, clip planes | `CameraComponents.cs` |
| Audio | `AudioSource` volume/pitch | `AudioComponents.cs` |
| Rigidbody / Rigidbody2D | Physics-driven position/rotation | `RigidbodyComponents.cs`, `Rigidbody2DComponents.cs` |
| Value / Control | Plain value motions and sequencing controls not tied to a specific component | `ValueComponents.cs`, `ControlComponents.cs` |

## Custom Animation Components

Inherit `LitMotionAnimationComponent` for a fully custom implementation, or
`PropertyAnimationComponent<TObject,TValue,TOptions,TAdapter>` (and its typed
shortcuts `FloatPropertyAnimationComponent<TObject>`,
`Vector3PropertyAnimationComponent<TObject>`, etc.) to skip writing motion
creation and value-restoration code by hand.

```csharp
[Serializable]
[LitMotionAnimationComponentMenu("Custom/Custom Animation")]
public class CustomAnimation : LitMotionAnimationComponent
{
    public override MotionHandle Play() { /* create and return the MotionHandle */ }
    public override void OnPause() { }
    public override void OnResume() { }
    public override void OnStop() { /* must restore the original value manually */ }
}

// Simplified form for a single property
[Serializable]
[LitMotionAnimationComponentMenu("UI/Slider/Value")]
public sealed class SliderValueAnimation : FloatPropertyAnimationComponent<Slider>
{
    protected override float GetValue(Slider target) => target.value;
    protected override void SetValue(Slider target, in float value) => target.value = value;
}
```

| Element | Purpose | Source |
|---|---|---|
| `[LitMotionAnimationComponentMenu("Path/Name")]` | Sets the label shown in the **Add...** dropdown | [Custom Animation Component](https://annulusgames.github.io/LitMotion/articles/en/custom-animation-component.html) |
| `LitMotionAnimationComponent.Play()` | Must create and return the driving `MotionHandle` | same |
| `LitMotionAnimationComponent.OnStop()` | Must manually restore the pre-animation value | same |
| `PropertyAnimationComponent<TObject,TValue,TOptions,TAdapter>` | Handles motion creation/restoration automatically — override only `GetValue`/`SetValue` | same |

**Critical caveat**: implementing `LitMotionAnimationComponent` directly (not the `PropertyAnimationComponent<T>` shortcut) requires manually restoring the value in `OnStop()` — omitting this leaves the animated property stuck at its last interpolated value after the animation ends.

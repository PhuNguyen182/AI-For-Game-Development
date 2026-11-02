// Custom LitMotion.Animation components: a LitMotionAnimationComponent skeleton and a Slider value animation on FloatPropertyAnimationComponent.
// Adapt into: Assets/_Project/Scripts/<Feature>/Views/CustomAnimationComponents.cs (Client code; fill the Play() placeholder first)
// Unverified: not compiled or run (no Unity project in this repo).
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

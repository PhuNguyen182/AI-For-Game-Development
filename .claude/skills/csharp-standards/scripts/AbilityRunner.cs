// Explicit access modifiers: the access modifier first, then the other modifiers.
// Adapt into: Assets/_Project/Scripts/<Feature>/Views/AbilityRunner.cs
// Unverified: not compiled or run (no Unity project in this repo).
public sealed class AbilityRunner : MonoBehaviour
{
    private const float DefaultCooldown = 1.5f;

    [SerializeField] private float cooldown = DefaultCooldown;

    private float _remainingCooldown;

    public bool IsReady => this._remainingCooldown <= 0f;

    private void ResetCooldown()
    {
        this._remainingCooldown = this.cooldown;
    }
}

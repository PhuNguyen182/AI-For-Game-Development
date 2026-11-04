// Per-match deterministic RNG: an injected IRandom the caller initialised with the match seed.
// Adapt into: Assets/_Project/Scripts/<Feature>/Core/LootRoller.cs
// Unverified: not compiled or run (no Unity project in this repo).
// Core: deterministic per-match RNG, injected, never RandomEx.Shared.
public sealed class LootRoller
{
    private readonly IRandom _random;

    // Caller: var random = new Xoshiro256StarStarRandom(); random.InitState(matchSeed); new LootRoller(random);
    public LootRoller(IRandom random)
    {
        this._random = random;
    }

    public int RollCriticalPercent()
    {
        return this._random.NextInt(0, 100);
    }
}

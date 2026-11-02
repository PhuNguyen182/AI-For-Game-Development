// Per-match deterministic RNG: an injected Xoshiro256StarStarRandom initialised with the match seed.
// Adapt into: Assets/_Project/Scripts/<Feature>/Core/LootRoller.cs
// Unverified: not compiled or run (no Unity project in this repo).
// Core: deterministic per-match RNG, injected, never RandomEx.Shared.
public sealed class LootRoller
{
    private readonly IRandom _random;

    public LootRoller(uint matchSeed)
    {
        this._random = new Xoshiro256StarStarRandom();
        this._random.InitState(matchSeed);
    }

    public int RollCriticalPercent()
    {
        return this._random.NextInt(0, 100);
    }
}

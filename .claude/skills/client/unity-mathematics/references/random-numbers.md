# Random Numbers

Covers SKILL.md step 7 — the seeded, explicit-state RNG `coding-principles.md` requires for Shared Core in place of `UnityEngine.Random`.

## Manual
- [Random numbers](https://docs.unity3d.com/Packages/com.unity.mathematics@1.3/manual/random-numbers.html) — `Random` requires you to create and manage its state yourself by initializing it with a chosen seed, which is what makes it deterministic. This is useful for parallel code: you can keep independent `Random` instances per thread/context without interference, and control seeding explicitly so two sources are never accidentally correlated. `NextFloat()` returns a value in `[0, 1)` by default, with overloads for a custom range (e.g. `NextFloat(-5.0f, 5.0f)`).

## API
- [Random](https://docs.unity3d.com/Packages/com.unity.mathematics@1.3/api/Unity.Mathematics.Random.html) — an RNG based on xorshift, deliberately kept to minimal state (32 bits) so it embeds cheaply into a component/struct; its core operations avoid integer multiplication to vectorize well on limited SIMD instruction sets. Constructed via `new Random(uint seed)` (seed must be non-zero) or reset via `InitState(uint seed = 1851936439U)`.

Because the seed and state are fully explicit and caller-managed — never global/static, never wall-clock-derived — this is the correct RNG for `Game.Core.*` Shared Core logic under `coding-principles.md`'s determinism rule, where `UnityEngine.Random`'s implicit global state is disallowed.

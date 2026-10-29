# Random Numbers — Unity.Mathematics.Random

Sources: [a] manual/random-numbers.html, [b] api/Unity.Mathematics.Random.html — below the SKILL.md `Docs:` base.

Caller-managed state, so it satisfies the seeded, injectable RNG rule for Burst, job and ECS code, where `UnityEngine.Random`'s global state is disallowed. Shared Core uses `nrandom-random-generation`.

## State model

| Property | Consequence |
|---|---|
| Caller creates and manages the state [a] | Reproducible; nothing global advances it |
| Independent instances do not interfere [a] | Safe per thread or per context |
| 32 bits of state, xorshift-based, no integer multiply in core ops [b] | Cheap to embed in a component; vectorizes on limited SIMD |
| Mutable struct [b] | Pass by `ref`; a by-value copy silently replays the same sequence |

## Calls

| Call | Fact |
|---|---|
| `new Random(uint seed)` | Seed must be non-zero |
| `InitState(uint seed = 1851936439U)` | Resets an existing instance |
| `NextFloat()` | `[0, 1)` |
| `NextFloat(min, max)` | Custom range, e.g. `NextFloat(-5.0f, 5.0f)` |

**Caveat:** a zero seed is invalid; a wall-clock seed defeats determinism. Both run normally and diverge between client and server.

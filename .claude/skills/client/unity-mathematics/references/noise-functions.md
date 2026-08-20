# Noise Functions

Covers SKILL.md step 8 (choosing the right noise function for procedural generation).

## API
- [noise](https://docs.unity3d.com/Packages/com.unity.mathematics@1.3/api/Unity.Mathematics.noise.html) — a static class of noise functions: classic Perlin noise (`noise.cnoise`), simplex noise (`noise.snoise`), and cellular/Worley noise (`noise.cellular`), each available across multiple input dimensionalities. Choose by the dimensionality of the data being sampled and by which function's visual/statistical character actually fits the effect (Perlin/simplex for smooth continuous variation, cellular for cell-like/organic patterns) — not by habit or whichever was used last.

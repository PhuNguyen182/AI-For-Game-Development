# Rendering Paths

Sources (manual paths under the `Docs:` base): [c] `rendering-paths-comparison.html`, [f] `rendering/forward-rendering-paths.html`, [d] `rendering/deferred-rendering-path-landing.html`.

The path is set on the Renderer asset, so it is a per-tier decision.

| Path | Fact that decides |
|---|---|
| Forward | Per-object light limit: extra lights stop affecting that object, so a scene looks lit while individual props go dark [f] |
| Forward+ | No per-object limit (screen-space light structure), higher base cost; keeps MSAA and transparent lighting [f] |
| Deferred | G-buffer, lights once; scales with light count not object count; costs bandwidth, gives up MSAA [d] |
| Deferred+ | Deferred with the clustered light structure: better light scaling [d] |
| Transparents | Still shaded forward under any deferred path, so transparent-heavy scenes get no deferred light scaling [c] |

**Caveat:** "lights stopped working past a count" is Forward's per-object limit; Forward+ fixes it directly. Deferred trades away MSAA, which mobile tiers commonly rely on, for a problem the cheaper option solves.

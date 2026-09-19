# Burst — Applying `[BurstCompile]` & Confirming It Took Effect

Sources: [Burst package](https://docs.unity3d.com/Manual/com.unity.burst.html), [Get started with Burst](https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/getting-started.html).
Covers: SKILL.md §4 — **"Apply `[BurstCompile]` and verify it took effect"**.

Only the application and verification of Burst on a job. Every deeper concern —
the HPC# subset, `FloatMode`/`FloatPrecision`, intrinsics, AOT and platform
settings, `[NoAlias]`, `FunctionPointer<T>`, `SharedStatic<T>` — belongs to
`unity-burst-compiler` and is deliberately absent here.

| Subject | What it decides | Source |
|---|---|---|
| `[BurstCompile]` on the job struct | Marks the job for native compilation; absent, the job runs under Mono/IL2CPP at ordinary managed speed | [Get started](https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/getting-started.html) |
| `[BurstCompile]` on a static method | Needed on **both** the method and its containing class — marking only one is a common reason a helper stays managed | [Get started](https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/getting-started.html) |
| Managed or reference types inside | Disqualify the job silently; there is no compile error, only unchanged performance | [Get started](https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/getting-started.html) |
| Editor vs build | JIT-compiled on first use in Play Mode, AOT-compiled into Player builds — so first-run Editor timings are not representative | [Get started](https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/getting-started.html) |
| Verification | The Burst Inspector (or the build log) is the only evidence compilation happened; the attribute alone is not | [Burst package](https://docs.unity3d.com/Manual/com.unity.burst.html) |

**Critical caveat**: substitute the `@1.8` segment for the Burst version the
project actually installs (`Window > Package Manager` or `manifest.json`)
before relying on any member above.

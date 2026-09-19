# Burst Intrinsics & SIMD

Sources: [Burst intrinsics overview](https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/csharp-burst-intrinsics.html), [Processor-specific SIMD extensions](https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/csharp-burst-intrinsics-processors.html).
Covers: SKILL.md §4 — **"Reach for `Unity.Burst.Intrinsics` only after generated assembly shows auto-vectorization fell short"**.

Hand-written SIMD, and the fallback obligation that comes with it. This is an
escalation past what Burst already does automatically — the generated assembly
in [debugging-and-inspector.md](debugging-and-inspector.md) is what establishes
that the escalation is warranted.

| Subject | What it decides | Source |
|---|---|---|
| `Unity.Burst.Intrinsics` | The namespace holding shared functionality and the processor-specific families | [Intrinsics overview](https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/csharp-burst-intrinsics.html) |
| `X86` family | Intel SSE through AVX2 — available only when the compilation target includes that instruction set | [Processor extensions](https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/csharp-burst-intrinsics-processors.html) |
| `Arm.Neon` family | The mobile counterpart; a job written against X86 intrinsics has no path on Arm without a second implementation | [Processor extensions](https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/csharp-burst-intrinsics-processors.html) |
| Out-of-target intrinsics | A compile-time error, not a runtime fallback — the wrong family fails the build | [Processor extensions](https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/csharp-burst-intrinsics-processors.html) |
| `IsXXXSupported` probes | Return **false** under reference-Mono when Burst compilation is disabled, so the else-branch is the code that runs in that configuration | [Processor extensions](https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/csharp-burst-intrinsics-processors.html) |

**Critical caveat**: the scalar fallback behind an `IsXXXSupported` probe is
real production code — it runs whenever Burst is disabled, including in some QA
configurations. An untested fallback that has drifted from the vector path is a
divergence that appears only where nobody is looking.

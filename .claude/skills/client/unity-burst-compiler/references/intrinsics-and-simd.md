# Burst Intrinsics & SIMD

Covers SKILL.md step 6 (hand-tuned SIMD intrinsics, reached for only after measuring auto-vectorization is insufficient).

## Manual
- [Burst intrinsics overview](https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/csharp-burst-intrinsics.html) — `Unity.Burst.Intrinsics` namespace; shared functionality, native calling conventions, processor-specific extensions.
- [Processor specific SIMD extensions](https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/csharp-burst-intrinsics-processors.html) — Intel `X86` (SSE through AVX2) and Arm `Neon` intrinsic families; compile-time errors for intrinsics outside the current compilation target; reference-Mono fallback when Burst is disabled (`IsXXXSupported` returns false).

Note: reach for these only after `unity-profiler-diagnostics`/the Burst Inspector's generated assembly shows Burst's own auto-vectorization is genuinely insufficient — see SKILL.md Edge cases.

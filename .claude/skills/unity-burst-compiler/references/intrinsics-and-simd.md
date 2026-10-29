# Burst intrinsics and SIMD

Source: [Intrinsics overview](https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/csharp-burst-intrinsics.html), [Processor extensions](https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/csharp-burst-intrinsics-processors.html).

An escalation past auto-vectorization; the generated assembly (see debugging reference) must show it fell short.

- `Unity.Burst.Intrinsics`: shared functionality plus processor-specific families.
- `X86`: SSE through AVX2, only when the compilation target includes that instruction set.
- `Arm.Neon`: the mobile counterpart; X86-only code has no Arm path without a second implementation.
- An out-of-target intrinsic is a compile-time error, not a runtime fallback.
- `IsXXXSupported` probes return false under reference-Mono when Burst is disabled, so the else-branch is what runs then, including in some QA configurations. Keep the scalar fallback real, equivalent and tested; a drifted fallback diverges where nobody looks.

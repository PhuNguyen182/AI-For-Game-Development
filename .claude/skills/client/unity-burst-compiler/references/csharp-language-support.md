# HPC# — What Burst Can Compile

Sources: [C# language support](https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/csharp-language-support.html), [C#/.NET type support](https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/csharp-type-support.html), [Static read-only field support](https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/csharp-static-read-only-support.html).
Covers: SKILL.md §4 — **"Bring the whole call graph inside the HPC# subset, not just the entry point"**.

The subset a Burst entry point and everything it calls must satisfy. Container
type choice is `unity-collections`; this file only states what disqualifies
code from compiling at all.

## Types

| Subject | What it decides | Source |
|---|---|---|
| Managed and reference types | Not supported anywhere in the reachable graph — a `class`, delegate, or boxed value disqualifies the entry point, not just the method holding it | [Type support](https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/csharp-type-support.html) |
| Structs, enums, pointers, spans, tuples | Supported, so a data rewrite into blittable structs is the normal fix for a rejected type | [Type support](https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/csharp-type-support.html) |
| Generics | Supported for types and methods used in a job, but not across the managed direct-call boundary — a generic entry point called from C# will not compile | [Calling Burst code](https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/csharp-calling-burst-code.html) |
| `string` | Only as a `Debug.Log` argument or assigned into a `FixedString`; general string operations are unavailable | [String support](https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/csharp-string-support.html) |

## Statics and language constructs

| Subject | What it decides | Source |
|---|---|---|
| Static fields | Only `readonly`, and only when the value is evaluable at compile time; a mutable static is a compile failure, not a warning | [Static read-only support](https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/csharp-static-read-only-support.html) |
| Mutable shared state | Requires `SharedStatic<T>` — see [function-pointers-and-shared-static.md](function-pointers-and-shared-static.md) | [Static read-only support](https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/csharp-static-read-only-support.html) |
| Supported expressions and statements | The general HPC# subset: ordinary control flow and arithmetic, minus anything requiring the managed runtime | [Language support](https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/csharp-language-support.html) |

**Critical caveat**: eligibility is a property of the whole reachable graph.
A job whose own body is spotless still falls back to managed if a static helper
three calls down touches a managed type — which is why the Burst Inspector, not
a reading of the job struct, is what settles whether it compiled.

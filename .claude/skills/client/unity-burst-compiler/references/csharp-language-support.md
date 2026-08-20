# C# Language Support (HPC#)

Covers SKILL.md step 2 (checking the HPC# subset before writing Burst-targeted code).

## Manual
- [C# language support](https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/csharp-language-support.html) — which C# expressions/statements are in the HPC# high-performance subset.
- [C#/.NET type support](https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/csharp-type-support.html) — no managed objects/reference types; supported built-in types, arrays, structs, generics, vectors, enums, pointers, spans, tuples.
- [String support](https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/csharp-string-support.html) — `Debug.Log` and `FixedString` (Unity.Collections) assignment; no general managed `string` operations.
- [Static read-only fields and static constructor support](https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/csharp-static-read-only-support.html) — Burst only supports read-only static fields, evaluated at compile time.

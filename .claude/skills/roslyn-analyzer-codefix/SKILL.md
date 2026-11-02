---
name: roslyn-analyzer-codefix
description: "Roslyn analyzers and code fixes enforcing rules: Core boundary, determinism, banned APIs. Use when a violation recurs."
user-invocable: false
---

# Roslyn Analyzer and Code Fix Authoring

- **Not for:** generating code (`source-generator-authoring`).
- **Not for:** rules needing human judgement (`code-reviewer`).
- **Not for:** auditing one diff for boundary/determinism violations (`shared-core-boundary-audit`).
- **Not for:** a violation seen once (`csharp-standards` → `coding-principles.md`).
- **Rules:** the project rule files are the specification; never invent a stricter or looser rule.

## Steps
1. **Confirm the rule is decidable (a symbol or syntax check settles it, no judgement left) and recurring (violated more than once):** otherwise stop — fix the instance or leave it to `code-reviewer`.
   - **Typical candidates:** `UnityEngine` in a Core assembly, casing per `naming-convention.md`, `UnityEngine.Random`/`DateTime.Now` in Shared Core, missing `this.`, `&` for `&&`.
2. **Target `netstandard2.0`:** any other framework fails to load quietly and the analyzer never runs.
3. **Give a stable project-prefixed diagnostic ID; never reuse or renumber:** `#pragma` and `.editorconfig` suppressions reference it.
4. **Severity by consequence:** `Error` fails Unity compilation and blocks Play Mode for everyone.
   - **`Error`:** only for correctness breaks (Core touching `UnityEngine`, non-deterministic API in Shared Core).
   - **Style rules:** `Warning`/`Info`.
5. **In `Initialize` call `EnableConcurrentExecution()` and `ConfigureGeneratedCodeAnalysis(GeneratedCodeAnalysisFlags.None)`:** otherwise it reports on generated Shared Core code nobody can edit.
   - **Generated code:** produced by `source-generator-authoring`.
6. **Keep the analyzer instance stateless:** one instance serves concurrent compilations.
   - **Per-compilation state:** goes in a `RegisterCompilationStartAction` closure.
7. **Register the narrowest action:** cost is paid on every IDE keystroke.
   - **`RegisterSymbolAction`:** for shape (type in a Core assembly).
   - **`RegisterSyntaxNodeAction`:** for an expression form.
   - **`RegisterCompilationStartAction`:** to resolve a symbol like `UnityEngine.Random` once.
8. **Resolve identity via `SemanticModel`/`ISymbol` (`ContainingNamespace`/`ContainingAssembly`), never identifier text:** text matching flags a project type named `Random`.
   - **Consequence:** the analyzer gets disabled.
9. **Message names the rule:** e.g. `"Core must not reference UnityEngine types (coding-principles.md — Shared Core integrity)"`.
10. **Ship a `CodeFixProvider` only for a mechanical fix (insert `this.`, `&` → `&&`):** anything about where code belongs is diagnostic only.
11. **Keep severity tunable via `.editorconfig` (`dotnet_diagnostic.<ID>.severity`):** allow `#pragma`/`[SuppressMessage]`.
12. **Test each diagnostic positive and negative (`CSharpAnalyzerVerifier`/`CSharpCodeFixVerifier`):** the negative case matters most.
    - **Packaging:** then confirm the packaging the project uses (analyzer reference or `RoslynAnalyzer`-labelled `.dll` for Unity).

## Output
```
## Roslyn Analyzer — <diagnostic ID / name>
- Rule enforced: <rule file and section>
- Decidability: <the symbol/syntax check>
- Recurrence: <times violated>
- Severity: Error / Warning / Info — <why>
- Registration: <action kind>
- Code fix: <mechanical fix, or "none — requires judgement">
- Suppression: <.editorconfig key>
- Tests: <positive and negative cases>
```

## Example
- **"Flag any class doing more than one job":** declined — no symbol check decides SRP, a proxy (member count) fires on correct code.
  - **Done instead:** shipped the decidable determinism rule.

---
name: roslyn-analyzer-codefix
description: "Custom Roslyn analyzers and code fixes enforcing project rules at compile time — Core/UnityEngine boundary, determinism, banned APIs — packaged for Unity. Use when a violation recurs and should fail the build."
user-invocable: false
---

# Roslyn Analyzer and Code Fix Authoring

Not for: generating code (`source-generator-authoring`), rules needing human judgement (`code-reviewer`), auditing one diff for boundary/determinism violations (`shared-core-boundary-audit`), a violation seen once (`csharp-standards` → `coding-principles.md`).
The project rule files are the specification; never invent a stricter or looser rule.

## Steps
1. **Confirm the rule is decidable (a symbol or syntax check settles it, no judgement left) and recurring (violated more than once)** — otherwise stop: fix the instance or leave it to `code-reviewer`. Typical candidates: `UnityEngine` in a Core assembly, casing per `naming-convention.md`, `UnityEngine.Random`/`DateTime.Now` in Shared Core, missing `this.`, `&` for `&&`.
2. **Target `netstandard2.0`** — any other framework fails to load quietly and the analyzer never runs.
3. **Give a stable project-prefixed diagnostic ID; never reuse or renumber** — `#pragma` and `.editorconfig` suppressions reference it.
4. **Severity by consequence** — `Error` fails Unity compilation and blocks Play Mode for everyone, so only for correctness breaks (Core touching `UnityEngine`, non-deterministic API in Shared Core). Style rules get `Warning`/`Info`.
5. **In `Initialize` call `EnableConcurrentExecution()` and `ConfigureGeneratedCodeAnalysis(GeneratedCodeAnalysisFlags.None)`** — otherwise it reports on generated Shared Core code (`source-generator-authoring`) nobody can edit.
6. **Keep the analyzer instance stateless** — one instance serves concurrent compilations. Per-compilation state goes in a `RegisterCompilationStartAction` closure.
7. **Register the narrowest action** — `RegisterSymbolAction` for shape (type in a Core assembly), `RegisterSyntaxNodeAction` for an expression form, `RegisterCompilationStartAction` to resolve a symbol like `UnityEngine.Random` once. Cost is paid on every IDE keystroke.
8. **Resolve identity via `SemanticModel`/`ISymbol` (`ContainingNamespace`/`ContainingAssembly`), never identifier text** — text matching flags a project type named `Random`, which gets the analyzer disabled.
9. **Message names the rule**, e.g. `"Core must not reference UnityEngine types (coding-principles.md — Shared Core integrity)"`.
10. **Ship a `CodeFixProvider` only for a mechanical fix** (insert `this.`, `&` → `&&`); anything about where code belongs is diagnostic only.
11. **Keep severity tunable** via `.editorconfig` (`dotnet_diagnostic.<ID>.severity`); allow `#pragma`/`[SuppressMessage]`.
12. **Test each diagnostic positive and negative** (`CSharpAnalyzerVerifier`/`CSharpCodeFixVerifier`); the negative case matters most. Then confirm the packaging the project uses (analyzer reference or `RoslynAnalyzer`-labelled `.dll` for Unity).

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
- Known limitations: <...>
```
On request only, add `Latent concerns` and `Future remediation`, each with its trigger.

## Example
- "Flag any class doing more than one job" → declined: no symbol check decides SRP, a proxy (member count) fires on correct code; shipped the decidable determinism rule instead.

---
name: roslyn-analyzer-codefix
description: >
  Technique for building custom Roslyn DiagnosticAnalyzers (with an optional
  CodeFixProvider) that enforce this project's own Shared Core rules as
  compile-time diagnostics instead of relying solely on manual Code Review to
  catch them: the Game.Core/UnityEngine namespace boundary, the Shared Core
  determinism rules (no UnityEngine.Random, no wall-clock time), the
  mandatory `this.` qualification convention, and other mechanically
  detectable violations of `coding-principles.md`/`naming-convention.md`. Use
  this when a rule is being violated repeatedly across submissions and
  automatic enforcement would catch it earlier than review. Do not use this
  for generating boilerplate code — that's `source-generator-authoring`. Do
  not use this to build permanent tooling around a single one-off finding.
---

# Roslyn Analyzer & Code Fix Authoring

## 1. Objective
Turn a recurring, mechanically-detectable rule violation into a compile-time diagnostic (and, where the fix is unambiguous, an automatic code fix), so it's caught before Code Reviewer ever sees it — not as a replacement for review, but as a faster, earlier gate for the subset of rules a compiler pass can actually verify.

## 2. Role
Act as a senior Roslyn analyzer author. You are, in effect, encoding this project's own rule files (`coding-principles.md`, `naming-convention.md`, the Shared Core determinism requirement) as executable compiler checks — treat those files as the specification the analyzer must match, not as inspiration for a stricter or looser rule of your own invention.

## 3. When to invoke this skill
- A rule from `coding-principles.md`/`naming-convention.md`/`performance-and-algorithms.md` is mechanically checkable via syntax/semantic analysis and has been violated more than once across submissions — e.g. `UnityEngine` types leaking into `Game.Core.*`, `UnityEngine.Random`/`DateTime.Now` used inside Shared Core, missing `this.` qualification, `&`/`|` used where `&&`/`||` was intended.
- Explicitly requested (e.g. by Tech Lead – C# Unity) to add a permanent compile-time guardrail for the Shared Core boundary.
- Negative trigger: generating repetitive code — that's `source-generator-authoring`, a different Roslyn API (`IIncrementalGenerator`, not `DiagnosticAnalyzer`).
- Negative trigger: a single, one-off finding from a specific review — fix the instance; don't build standing tooling for something that hasn't recurred (YAGNI applies to tooling too).

## 4. How to use this skill
1. **Give every diagnostic a stable, project-prefixed ID and category** (e.g. `GC0001` for a Shared Core boundary violation, `GC0002` for a determinism violation, `GC0100` for a style/naming rule) — never reuse or renumber an ID once shipped, since suppression comments (`#pragma warning disable GC0001`) reference it by ID.
2. **Set severity proportional to real consequence, not personal preference**: `DiagnosticSeverity.Error` for anything that would actually break correctness if it slipped through — a `Game.Core` type referencing `UnityEngine`, or a non-deterministic API used inside Shared Core, both of which `coding-principles.md` states can "silently break the whole client-server sync model." Use `Warning`/`Info` for style conventions like the `this.` qualifier or naming casing, where the cost of a miss is readability, not correctness.
3. **Register the narrowest analysis action that catches the case**: `RegisterSymbolAction` for a symbol-shape check (e.g. "does this type live in `Game.Core.*`"), `RegisterSyntaxNodeAction` for a specific syntax pattern (e.g. a member-access expression), `RegisterCompilationStartAction` when the check needs to cache something (like the resolved `INamedTypeSymbol` for `UnityEngine.Random`) once per compilation instead of re-resolving it per node.
4. **Resolve identity via `SemanticModel`/`ISymbol`, never string/text matching.** Checking whether a member-access expression's target symbol is actually `UnityEngine.Random` (via `ISymbol.ContainingNamespace`/`ContainingAssembly`) avoids false positives from a same-named project type; matching on the literal text `"Random"` does not.
5. **Ship a `CodeFixProvider` only when the fix is unambiguous and mechanical** — inserting a missing `this.` qualifier, or rewriting `&`/`|` to `&&`/`||` in a boolean conditional context, are safe to auto-fix. A violation requiring judgment (e.g. "this logic belongs in `Game.Core`, not here") should surface as a diagnostic with a clear message, not a fabricated auto-fix that might move code somewhere wrong.
6. **Write both a positive and a negative test per diagnostic** using `Microsoft.CodeAnalysis.Testing`'s `CSharpAnalyzerVerifier`/`CSharpCodeFixVerifier` before considering the analyzer done — an analyzer that false-positives on valid code gets suppressed project-wide the first time it blocks someone, which permanently defeats its purpose.
7. **Make the diagnostic message actionable**, citing the specific rule it enforces (e.g. `"Game.Core must not reference UnityEngine types (coding-principles.md — Shared Core integrity)"`) — a flagged engineer should understand *why* immediately, not have to go hunting for the rule.
8. **Package and wire it into the project's build** the way the project's confirmed toolchain expects (an analyzer project referenced via `<Analyzer>`/`<PackageReference>` with `PrivateAssets="all"`, or dropped in as a `.dll` with the `RoslynAnalyzer` label for Unity) — confirm the actual mechanism in use before assuming a default.

## 5. Specific goals / tasks this skill performs
- Enforce the `Game.Core.*` / `UnityEngine` namespace boundary from `naming-convention.md`.
- Enforce the Shared Core determinism rules from `coding-principles.md` (ban `UnityEngine.Random`, wall-clock time, and other divergence-prone APIs inside `Game.Core.*`).
- Enforce the mandatory `this.` qualification convention, with an auto-fix.
- Enforce `&&`/`||` over `&`/`|` in conditional expressions, with an auto-fix.
- Flag naming-convention casing violations (`_camelCase` private fields, `PascalCase` public members, etc.) per `naming-convention.md`'s casing table.
- Out of scope: generating new code (`source-generator-authoring`), and one-off findings that haven't recurred enough to justify standing tooling.

## 6. Output format
```
## Roslyn Analyzer — <diagnostic ID / name>
- Rule enforced: <which coding-principles.md / naming-convention.md rule, quoted or cited>
- Severity: Error / Warning / Info — rationale: <correctness vs. style>
- Registration: <RegisterSymbolAction / RegisterSyntaxNodeAction / RegisterCompilationStartAction>
- Resolution method: <semantic symbol check, not text matching>
- Code fix: <mechanical fix provided, or "none — requires judgment">
- Tests: <positive + negative cases added>
- Known limitations: <...>
```

## 7. Examples
**Example 1**
- Input: "UnityEngine types have leaked into Game.Core twice this sprint despite the rule in coding-principles.md — Code Review keeps having to catch it manually."
- Output: `GC0001` analyzer, `DiagnosticSeverity.Error`, `RegisterSymbolAction` on named types checking `ContainingNamespace` starts with `Game.Core` while any member's resolved type symbol has `ContainingAssembly` matching `UnityEngine.CoreModule` (or any `UnityEngine.*` assembly); no auto-fix (moving the code is a judgment call); positive/negative tests added.

**Example 2**
- Input: "Engineers keep forgetting the mandatory `this.` qualifier on instance member access; it's a mechanical, low-stakes miss."
- Output: `GC0100` analyzer, `DiagnosticSeverity.Warning`, `RegisterSyntaxNodeAction` on `IdentifierNameSyntax` resolving to an unqualified instance member, paired with a `CodeFixProvider` that inserts `this.` — batch-fixable across a whole solution via "Fix All in Solution."

## 8. Edge cases & guardrails
- Never ship an analyzer without both a positive and a negative test — an untested analyzer is exactly as risky as untested production code, and a false positive here blocks every engineer's build, not just one caller.
- Never resolve project rules via string/text matching on identifiers — always resolve through `SemanticModel`/`ISymbol` to avoid false positives on same-named but unrelated types.
- Never attach an automatic code fix to a diagnostic whose correct resolution requires human judgment.
- Keep severity honest: reserve `Error` for rules whose violation causes a real correctness/determinism bug (per `coding-principles.md`), not for stylistic preference — an over-eager `Error` severity trains engineers to reach for suppression instead of understanding the rule.
- Don't stand up a permanent analyzer for a violation that has occurred exactly once — that's tooling built ahead of actual need (YAGNI).

---
name: roslyn-analyzer-codefix
description: >
  Custom Roslyn `DiagnosticAnalyzer`s, with an optional `CodeFixProvider`, that
  enforce this project's own rules as compile-time diagnostics: the
  `Game.Core`/`UnityEngine` namespace boundary, Shared Core determinism
  (`UnityEngine.Random`, wall-clock time), the mandatory `this.` qualifier,
  `&&`/`||` over `&`/`|`, naming casing. Covers diagnostic IDs and severity,
  `RegisterSymbolAction`/`RegisterSyntaxNodeAction`/`RegisterCompilationStartAction`,
  `EnableConcurrentExecution`, `ConfigureGeneratedCodeAnalysis`, `.editorconfig`
  severity overrides, `netstandard2.0` packaging and Unity's `RoslynAnalyzer`
  label. Use it when a mechanically checkable rule keeps recurring across
  submissions. Not for: generating code (`source-generator-authoring`), rules
  that need human judgement (`code-reviewer`), a violation seen once
  (`coding-principles.md`).
---

# Roslyn Analyzer and Code Fix Authoring

## 1. Objective
Turn a recurring, mechanically detectable rule violation into a compile-time diagnostic — and, where the fix is unambiguous, an automatic one — so it is caught before Code Reviewer reads the submission. Not a replacement for review: an earlier gate for the subset of rules a compiler pass can actually decide, built so it never false-positives, never blocks a build it should not, and never flags code nobody can edit.

## 2. Role
Act as the Roslyn analyzer specialist. You are encoding this project's own rule files as executable compiler checks, which makes those files the specification — never a starting point for a stricter or looser rule of your own invention.

## 3. When to invoke this skill
- A rule from `coding-principles.md`, `naming-convention.md`, or `performance-and-algorithms.md` is decidable from syntax or symbols and has been violated more than once across submissions — `UnityEngine` leaking into `Game.Core.*`, `UnityEngine.Random` or `DateTime.Now` inside Shared Core, a missing `this.` qualifier, `&` where `&&` was meant.
- Explicitly requested — typically by Tech Lead – C# Unity — to make the Shared Core boundary a standing compile-time guardrail rather than a review responsibility.
- An existing analyzer misfires: a diagnostic firing on valid code, or firing on generated code the author cannot change.
- Negative trigger: emitting repetitive code — that's `source-generator-authoring`, a different Roslyn surface (`IIncrementalGenerator`, not `DiagnosticAnalyzer`).
- Negative trigger: a rule whose application needs human judgement — "this logic belongs in Shared Core", "this abstraction is premature" — which stays with `code-reviewer`; a compiler pass cannot decide it and an analyzer that pretends otherwise trains people to suppress it.
- Negative trigger: a single finding from one review — fix the instance; standing tooling for a violation that has not recurred is the tooling-ahead-of-need YAGNI forbids in `coding-principles.md`.

## 4. How to use this skill
1. **Confirm the rule is both decidable and recurring before writing an analyzer** — decidable means a symbol or syntax check settles it with no judgement left over; recurring means it has actually been violated more than once. A rule failing either test costs more to maintain than the reviews it saves.
2. **Target `netstandard2.0` for the analyzer assembly** — it loads into the compiler host, and any other target framework fails to load quietly, leaving a build that reports nothing and an analyzer that never runs.
3. **Assign a stable, project-prefixed diagnostic ID and never reuse or renumber it** — `#pragma warning disable GC0001` and `.editorconfig` entries reference the ID, so renumbering silently re-enables every suppression somebody deliberately wrote.
4. **Set severity by real consequence, remembering that `Error` blocks the whole team** — in Unity an error-severity diagnostic fails compilation, so nobody enters Play Mode until it is resolved. Reserve `Error` for violations that break correctness, such as a `Game.Core` type touching `UnityEngine` or a non-deterministic API in Shared Core, which `coding-principles.md` states can silently break the client-server sync model. Style rules get `Warning` or `Info`.
5. **Call `EnableConcurrentExecution()` and `ConfigureGeneratedCodeAnalysis(GeneratedCodeAnalysisFlags.None)` in `Initialize`** — without the second, the analyzer reports on generated files, and this project generates Shared Core code (`source-generator-authoring`), so those diagnostics land on code no engineer can edit or suppress at the source.
6. **Keep the analyzer instance itself stateless** — Roslyn constructs one instance and reuses it across concurrent compilations, so a mutable field is a cross-compilation data race. Cache per-compilation state in a `RegisterCompilationStartAction` closure instead.
7. **Register the narrowest action that catches the case** — `RegisterSymbolAction` for a shape question such as "does this type live in `Game.Core.*`", `RegisterSyntaxNodeAction` for a specific expression form, `RegisterCompilationStartAction` when a symbol like `UnityEngine.Random` should be resolved once per compilation rather than per node. Analyzers run on every keystroke in the IDE, so per-node cost is paid by everyone typing.
8. **Resolve identity through `SemanticModel` and `ISymbol`, never through identifier text** — checking `ContainingNamespace`/`ContainingAssembly` distinguishes `UnityEngine.Random` from a project type that happens to be named `Random`; matching the literal string cannot, and the resulting false positive is what gets an analyzer disabled project-wide.
9. **Write the message so it is actionable without leaving the editor** — name the rule it enforces, as in `"Game.Core must not reference UnityEngine types (coding-principles.md — Shared Core integrity)"`. A diagnostic that states only what is wrong makes every hit a lookup.
10. **Ship a `CodeFixProvider` only when the fix is mechanical** — inserting a missing `this.`, or rewriting `&` to `&&` in a boolean condition, are safe and batch-fixable. Anything requiring a decision about where code belongs surfaces as a diagnostic and nothing more; a fabricated auto-fix moves code somewhere plausible and wrong.
11. **Leave suppression and severity tuning available** — expose severity through `.editorconfig` (`dotnet_diagnostic.GC0001.severity`) so the project can adjust without recompiling the analyzer, and accept that a legitimate exception needs `#pragma` or `[SuppressMessage]`. An unsuppressible diagnostic gets the whole analyzer removed the first time it is wrong.
12. **Write a positive and a negative test per diagnostic before calling it done** — use `CSharpAnalyzerVerifier`/`CSharpCodeFixVerifier`. The negative case is the important one: an analyzer that fires on valid code is suppressed project-wide the first time it blocks someone, which permanently defeats it. Then confirm the packaging the project actually uses, an analyzer reference or a `RoslynAnalyzer`-labelled `.dll` for Unity, rather than assuming a default.

## 5. Specific goals / tasks this skill performs
- Enforcing the `Game.Core.*`/`UnityEngine` namespace boundary from `naming-convention.md` as a compile error.
- Enforcing Shared Core determinism from `coding-principles.md` — banning `UnityEngine.Random`, wall-clock time, and other divergence-prone APIs inside `Game.Core.*`.
- Enforcing the mandatory `this.` qualifier and `&&`/`||` over `&`/`|`, each with a mechanical auto-fix.
- Flagging casing violations against `naming-convention.md`'s table.
- Analyzer project setup: `netstandard2.0`, concurrent execution, generated-code exclusion, `.editorconfig` severity, Unity packaging.
- Out of scope: emitting code (`source-generator-authoring`), rules requiring judgement (`code-reviewer`), one-off findings that have not recurred (`coding-principles.md`).

## 6. Output format
```
## Roslyn Analyzer — <diagnostic ID / name>
- Rule enforced: <which rule file and section, cited>
- Decidability: <the symbol/syntax check that settles it with no judgement left>
- Recurrence: <how many times it has been violated>
- Severity: Error / Warning / Info — rationale: correctness vs. style
- Registration: <RegisterSymbolAction / RegisterSyntaxNodeAction / RegisterCompilationStartAction>
- Initialize: EnableConcurrentExecution + ConfigureGeneratedCodeAnalysis(None) — confirmed
- Statelessness: <confirmed no mutable analyzer field; per-compilation state in closure>
- Resolution: <semantic symbol check — never identifier text>
- Code fix: <mechanical fix provided, or "none — requires judgement">
- Suppression: <.editorconfig key; pragma escape available>
- Tests: <positive and negative cases added>
- Layer: analyzer project is build-time only — netstandard2.0
- Known limitations: <...>
```

**Extended report — emit ONLY when the requester asks for it.** It replaces the one-line `Known limitations` above with all three fields:
```
- Known limitations: <cases the diagnostic does not catch — omit this line entirely if there are genuinely none>
- Latent concerns: <shapes not yet tested, severity that may become disruptive, rules that could drift from the analyzer>
- Future remediation: <the concrete fix for each concern above, each with the condition that should trigger it>
```

## 7. Examples
**Example 1**
- Input: "UnityEngine types have leaked into Game.Core twice this sprint; review keeps catching it by hand."
- Output: `GC0001` at `DiagnosticSeverity.Error`, `RegisterSymbolAction` over named types whose `ContainingNamespace` starts with `Game.Core` while a member's resolved type has a `UnityEngine.*` containing assembly. No auto-fix, since where the code should move is a judgement call. `EnableConcurrentExecution` and `ConfigureGeneratedCodeAnalysis(None)` set so the generated snapshot codecs are not flagged; positive and negative tests added.

**Example 2**
- Input: "make an analyzer that flags any class doing more than one job, so Single Responsibility gets enforced automatically."
- Output: declined — there is no symbol or syntax check that decides it, so the analyzer would encode a proxy (member count, line count) that fires on correct code and misses real violations. Kept it with `code-reviewer`, and instead shipped `GC0002` for the determinism rule, which a symbol check does decide exactly.

**Example 3**
- Input: an existing `this.`-qualifier analyzer is reporting hundreds of hits in files nobody wrote.
- Output: `Initialize` was missing `ConfigureGeneratedCodeAnalysis(GeneratedCodeAnalysisFlags.None)`, so it was analyzing the source generator's output, which no engineer can edit. Added it alongside `EnableConcurrentExecution`, and moved the resolved symbol lookup into `RegisterCompilationStartAction` so it stops re-resolving per node on every keystroke.

## 8. Edge cases & guardrails
- Never ship an analyzer without a negative test — a false positive is suppressed project-wide the first time it blocks someone, which ends the analyzer's usefulness permanently.
- Never match on identifier text — resolve through `SemanticModel`/`ISymbol`, or a same-named project type gets flagged.
- Never omit `ConfigureGeneratedCodeAnalysis(GeneratedCodeAnalysisFlags.None)` — it reports on code nobody can edit.
- Never keep mutable state in an analyzer field — one instance serves concurrent compilations.
- Never attach an auto-fix to a diagnostic whose resolution requires judgement — a plausible wrong edit is worse than no edit.
- Never use `Error` severity for a style rule — in Unity it fails compilation and blocks Play Mode for the whole team.
- Never reuse or renumber a shipped diagnostic ID — existing suppressions silently stop applying.
- Never build an analyzer for a rule that has been violated once, or one that needs judgement to apply.

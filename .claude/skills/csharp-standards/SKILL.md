---
name: csharp-standards
description: "Detail behind rule `csharp.md`: Core boundary, naming, fake-null, hot-path, Jobs/Burst. Use when the rule leaves a gap."
user-invocable: false
---

# C# standards

- **Rule:** rule `csharp.md` binds every `.cs` change.
- **Writers:** writers open a reference only when the rule leaves a question open.
- **Asset names:** specs use them too: Prefab `Category_Name` · `Scene_` · `SO_` · `Mat_` · `Tex_` · `Anim_` · Animator `AC_` · `Shader_` · `VFX_` · asmdef = its root namespace.

## References
- **[coding-principles.md](references/coding-principles.md):** Core vs Client placement, a null guard, an event or `IDisposable` lifetime, an `[Obsolete]` hit, newer C# syntax, handoff scope.
- **[code-style-and-layout.md](references/code-style-and-layout.md):** skipping braces, a call chain, a long-line wrap, an operator form.
- **[naming-convention.md](references/naming-convention.md):** naming a field, event, asset or asmdef; a namespace after a file move.
- **[performance-and-algorithms.md](references/performance-and-algorithms.md):** per-frame/per-tick code, entity-scaled code, a collection choice, a speed-up claim.

## Review
- **Coverage:** review checks every submission against `csharp.md` and all four references; a violation is a finding at any size.
- **Severity and verdict:** a violation's severity and the verdict it earns: skill `code-review-method`.
  - **Style class:** style, layout, naming and comments are Low.
  - **Runtime class:** a violation with runtime impact takes that impact's severity.

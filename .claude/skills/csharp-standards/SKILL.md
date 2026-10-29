---
name: csharp-standards
description: "Detail behind rule `csharp.md`: Shared Core boundary, naming, Unity fake-null, layout, hot-path and memory rules, Jobs/Burst escalation. Use when writing or reviewing C# and the rule leaves a question open."
user-invocable: false
---

# C# standards

Rule `csharp.md` binds every `.cs` change. Writers open a reference only when the rule leaves a question open.

| Reference | Read when |
|---|---|
| [coding-principles.md](references/coding-principles.md) | Core vs Client placement, a null guard, an event or `IDisposable` lifetime, an `[Obsolete]` hit, newer C# syntax, handoff scope |
| [code-style-and-layout.md](references/code-style-and-layout.md) | Skipping braces, a call chain, a long-line wrap, an operator form |
| [naming-convention.md](references/naming-convention.md) | Naming a field, event, asset or asmdef; a namespace after a file move |
| [performance-and-algorithms.md](references/performance-and-algorithms.md) | Per-frame/per-tick code, entity-scaled code, a collection choice, a speed-up claim |

Asset names (specs use them too): Prefab `Category_Name` · `Scene_` · `SO_` · `Mat_` · `Tex_` · `Anim_` · Animator `AC_` · `Shader_` · `VFX_` · asmdef = its root namespace.

## Review
Review checks every submission against `csharp.md` and all four references; a violation is "request changes" at any size.

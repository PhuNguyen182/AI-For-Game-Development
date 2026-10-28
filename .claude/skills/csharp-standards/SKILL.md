---
name: csharp-standards
description: Full C# standard for this project — design principles, layout, naming, null safety, performance and data-structure choice. The short form is rule `csharp.md`. Preloaded by every agent that writes or reviews C#.
user-invocable: false
---

# C# standards

Rule `csharp.md` is the binding summary. Open a reference only when the summary does not settle the question.

| Reference | Open when |
|---|---|
| `references/coding-principles.md` | Core/Client boundary, SOLID and friends, exceptions, events, null safety, obsolete APIs |
| `references/code-style-and-layout.md` | Access modifiers, braces, wrapping, temporaries, operator choice |
| `references/naming-convention.md` | Any identifier, asset, asmdef or namespace name |
| `references/performance-and-algorithms.md` | Hot paths, data-structure choice, GC, draw calls, complexity |

Review checks every submission against all four; a violation is "request changes" at any size.

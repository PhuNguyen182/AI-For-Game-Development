---
paths:
  - "**/*.cs"
---

# C#

Full detail: skill `csharp-standards`. Feature docs: skill `feature-docs`.

## Boundaries
- Game rules (damage, cooldowns, economy, state machines) live only in `Game.Core.*`. Client code calls them, never reimplements them.
- `Game.Core.*`: no `UnityEngine`, deterministic — no `UnityEngine.Random` (inject a seeded RNG), no wall-clock time. Client resolves Unity data (raycasts) and passes it in.
- Namespace = folder path below `Assets/`, PascalCased. Moving a file updates its namespace in the same change.
- Validate only at real boundaries: user input, save data, network messages, SDK callbacks, Inspector slots, Unity API returns.

## Style
- Explicit access modifier on every type and member. File-scoped namespaces; `using` outside them.
- Allman braces, 4 spaces. Never a body on its header's line; a one-statement body may skip braces.
- `this.` on every instance member. Private fields `_camelCase`, static `s_camelCase`, serialized fields `camelCase`, constants PascalCase, booleans `Is/Has/Can`, handlers `On<Event>`, async `…Async`.
- `var` only when the type is obvious; explicit type in `foreach`. Keywords over `System.Int32`.
- Null: `is null` / `is not null` for plain C#; implicit bool (`if (this.collider)`) for `UnityEngine.Object`.
- Modern operators (`?.`, `??=`, pattern matching, `switch` expressions). Check the project's C# version before newer syntax.
- No magic numbers or strings. No `[Obsolete]` APIs in new code.
- Catch specific exceptions only; `using` for `IDisposable`.

## Comments
- English. Explain the non-obvious why, never the what. `//` on its own line.
- Small member: none or one line. Complex member: XML doc — role, parts, mechanism.

## Hot paths (`Update`, `FixedUpdate`, per-tick)
- No allocation: no `new`, LINQ, string building or boxing.
- Cache `GetComponent`, `Camera.main`, Animator hashes, `WaitForSeconds`. Never `Find*`, `SendMessage`, string `Invoke`.
- Pool high-frequency instantiate/destroy. No empty Unity magic methods.
- Every subscription, coroutine and pooled rent has a matching release in `OnDisable`/`OnDestroy`. Named handlers, not lambdas, for lifetime-bound events.

## Scope
- SOLID, KISS, YAGNI. Build only what the spec asks; touch only what the change needs; flag the rest.

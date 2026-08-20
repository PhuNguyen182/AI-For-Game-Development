# Client Track — Coding Principles

Applies to: C# Software Engineer, Unity Engineer, UI/UX Programmer, Tech Lead – C# Unity, Tech Lead – SDK/Platform, Tech Lead – Performance, Technical Artist.

Sources: [Microsoft Learn — Identifier names](https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/coding-style/identifier-names) and [Microsoft Learn — .NET Coding Conventions](https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/coding-style/coding-conventions), adapted for Unity/game-client context where noted.

## Shared Core integrity

- Game-rule logic (damage formulas, state machines, cooldowns, economy math — anything that decides an outcome) lives **only** in `Game.Core.*`. MonoBehaviours and other `Game.Client.*` code call into it; they never reimplement it.
- Shared Core code must be **deterministic**: no `UnityEngine.Random` (use a seeded, injectable RNG instead), no wall-clock time, no float operations that can diverge between platforms/architectures. This is required for client prediction and server authority to ever agree — non-determinism here silently breaks the whole client-server sync model.
- If a rule needs Unity APIs to evaluate (e.g. a raycast), keep the *decision* in Shared Core and pass in the already-resolved data from the Client layer — don't pull Unity calls into Core.

## Core design principles (mandatory)

These are non-negotiable, not stylistic preferences. Code Reviewer checks every submission against them, and a violation is grounds for "request changes" regardless of the feature's Triage tier.

### SOLID

- **Single Responsibility** — a class has exactly one reason to change. A MonoBehaviour that reads input, applies gameplay rules, *and* updates UI has three reasons to change and needs splitting.
- **Open/Closed** — extend behavior by adding new code (a new class implementing an interface), not by editing an existing method's branching logic. A growing `switch` on an "ability type" enum is a signal to introduce an `IAbility` implementation per type instead.
- **Liskov Substitution** — any interface implementation or subclass must be usable wherever the base type is expected, without surprising the caller. An `IDamageable.TakeDamage()` implementation that throws for certain object types, or silently no-ops when callers expect an effect, breaks this.
- **Interface Segregation** — keep interfaces narrow and role-specific (`IDamageable`, `IHealable`) instead of one fat interface (`IEntity`) that forces every implementer to stub out methods it doesn't need.
- **Dependency Inversion** — depend on abstractions, not concrete types. This is why Shared Core must not depend on concrete `UnityEngine` types, and why Client-layer code should depend on interfaces (`IInputProvider`, `IAudioService`) instead of concrete singletons — it's also what makes QA Automation Engineer's unit tests possible in the first place.

### KISS — Keep It Simple

Choose the simplest design that correctly solves what the Tech Spec asked for. A clever one-liner or an extra abstraction layer that only one caller will ever use makes the code harder to review and maintain — prefer the boring, obvious solution.

### YAGNI — You Aren't Gonna Need It

Build only what the current Tech Spec asks for. No speculative hooks, config options, or extensibility points for requirements that don't exist yet — this is the same rule stated operationally in Handoff below (don't add speculative extensibility), restated here as a design principle rather than a submission checklist item.

### Boy Scout Rule

Leave code slightly better than you found it — but only within the lines/method you're already touching for this task. Fix a misleading name, remove a stray debug log, delete now-dead code in that immediate area. This does **not** override the Handoff rule against refactoring unrelated code — it applies strictly to the code your current change already puts your hands on, not the rest of the file.

### Law of Demeter (Principle of Least Knowledge)

A method should only talk to its immediate collaborators, not reach through them. Avoid chains like `player.GetInventory().GetItem(0).GetStats().Damage` — ask the object you already have to do the work (`player.GetEquippedDamage()`) instead of reaching three objects deep to get the answer yourself. This also keeps a Shared Core change from rippling unpredictably through unrelated Client-layer code.

### POLA/POLS — Principle of Least Astonishment

A method or component must behave exactly as its name and signature imply — no hidden side effects. `GetHealth()` must not mutate state; `TakeDamage()` must not silently also save the game or fire an unrelated event. If a method needs to do something a caller wouldn't expect from its name, rename it or split it — don't leave the surprise in place.

### SLAP — Single Level of Abstraction Principle

Every method body should read at one consistent level of abstraction. Don't mix a high-level orchestration call (`ApplyDamage(target, amount)`) with low-level detail (raw bit-shifting, manual loop math) in the same method body — extract the low-level part into a well-named helper so the method reads like a short narrative, not a mix of "what" and "how."

## Structure

- One class, one job (see Single Responsibility above). A MonoBehaviour that handles input, gameplay rules, animation, and UI state is a sign the class needs to be split.
- Favor composition over deep inheritance chains, especially for MonoBehaviour components.
- No magic numbers or strings — use named constants, ScriptableObject-driven config, or Shared Core constants.
- Use file-scoped namespaces (`namespace Game.Core.Combat;`) rather than block-scoped, and place `using` directives outside the namespace declaration — placing them inside makes name resolution context-sensitive and can silently break later when a new dependency introduces a colliding namespace.
- Use target-typed `new()` and object initializers to reduce noise: `PlayerState state = new();` and `new AbilityConfig { Cooldown = 2f, MaxCharges = 3 }` over the verbose forms.
- Prefer `Func<>`/`Action<>` over hand-rolled delegate types for internal C#-only callbacks. Exception: an event that must be wireable in the Unity Inspector should use `UnityEvent`/`UnityAction` instead, since `Func<>`/`Action<>` aren't Inspector-serializable.
- Use `&&`/`||`, never `&`/`|`, in conditional expressions — the non-short-circuiting bitwise forms can evaluate an expression that shouldn't run (e.g. dividing when the divisor-is-zero check was supposed to short-circuit it).
- Use language keywords for built-in types (`string`, `int`) instead of the runtime type names (`System.String`, `System.Int32`).

## `this.` qualification

- Always qualify access to an instance field, property, method, or event with `this.` (e.g. `this.health -= damage;`, `this.Attack();`, `this.OnDamaged?.Invoke();`) — never omit it, even when there's no naming collision to disambiguate.
- This is a deliberate project convention and intentionally diverges from the common C# style-guide default of omitting `this.` unless required for disambiguation. Reason: it makes instance-member access visually distinct from local variables, parameters, and static members at a glance — valuable in Unity's MonoBehaviour-heavy code, where a local variable inside a long `Update()`/coroutine body frequently shares a similar name with a field.
- Applies uniformly regardless of the `_camelCase` prefix already used for private fields (see `naming-convention.md`) — the two conventions stack, they don't replace each other.
- Does not apply to static members — `this` cannot qualify a static member; use the type name for those, per standard C# rules.

## `var` and LINQ

- Use `var` only when the type is obvious from the right-hand side (`var health = 100;`, `var controller = new PlayerController();`). If the type isn't obvious from the assignment itself, spell it out.
- Always use an explicit type for `foreach` loop variables — the collection's element type usually isn't obvious at the call site.
- LINQ is fine for readability in non-performance-critical code (editor tooling, SDK/config code, one-off Shared Core setup) — use meaningful query variable names and put `where` before other clauses. **Never use LINQ inside a hot path** (`Update`, `FixedUpdate`, per-frame/per-tick code) — see Performance discipline below.

## Comments

- Comments explain non-obvious **why** (a workaround, a hidden constraint), never restate **what** the code already says. This project intentionally writes fewer comments than typical Microsoft samples — don't add an XML doc comment to every public member by default; add one only when the member's contract genuinely isn't obvious from its name and signature.
- When a comment is warranted: use `//`, not `/* */`. Put it on its own line above the code, not trailing at end of line. Capitalize the first letter, end with a period, one space after `//`.

## Exception handling

- Catch specific exception types with a clear reason you can act on; never catch bare `System.Exception` (or `catch {}`) to silently swallow an error.
- Use `using` (the statement or the C# 8+ declaration form) for any `IDisposable` instead of manual `try/finally` + `Dispose()` — relevant mainly in SDK/Platform and R&D code that touches non-Unity resources (file handles, network clients); most `UnityEngine.Object` lifetimes are managed by Unity itself, not `IDisposable`.

## Event handlers

- A lambda inline handler is fine only when its lifetime can't outlive the subscriber (e.g. a one-shot local callback). For any event subscription tied to a MonoBehaviour's lifetime, use a named method instead of a lambda, and unsubscribe it in `OnDisable`/`OnDestroy` — an inline lambda can't be unsubscribed, which is a common source of Unity memory leaks and dangling references to destroyed objects.

## Performance discipline (both PC and mobile — mobile is the tighter budget)

- No per-frame allocations in `Update()`/`FixedUpdate()`/`LateUpdate()` — no `new`, no LINQ, no string interpolation/concatenation, no boxing in hot paths.
- Cache `GetComponent<T>()` results outside of per-frame methods; never call it inside `Update()`.
- Never use `Find`/`FindObjectOfType` at runtime — use direct references, a service locator, or an event system instead.
- Pool frequently instantiated/destroyed objects (projectiles, VFX, enemies) rather than `Instantiate`/`Destroy` in hot paths.
- Outside hot paths, use string interpolation (`$"{a}, {b}"`) for one-off strings, and `StringBuilder` when appending in a loop.
- Keep platform-specific branches behind a clean abstraction (an interface-based platform service), not scattered `#if UNITY_ANDROID` / `#if UNITY_IOS` directives across gameplay code.

## Layout

- 4-space indentation, no tabs.
- Allman brace style — opening brace on its own line, matching the block's indentation.
- One statement and one declaration per line.
- Blank line between method/property definitions.
- Use parentheses to make operator precedence explicit in non-trivial expressions, even when not strictly required.
- No fixed character-per-line limit is enforced (Microsoft's own 65-character guidance is for their docs website, not production code) — keep lines readable, wrap when a line's intent gets hard to scan, particularly for method signatures with many parameters.

## Modern C# syntax — check the project's language version first

Raw string literals, `required` properties, collection expressions (`[...]`), and primary constructors are all real Microsoft-recommended patterns, but they require a C# language version Unity's compiler toolchain (Mono or IL2CPP, depending on the target platform) must actually support. Confirm the project's configured C# version before using any of them — don't assume the latest syntax compiles on this project's Unity version.

## Obsolete APIs

- Never write new code that declares or consumes a class, struct, field, method, property, event, or any other member marked with `[Obsolete]` — including Unity API members Unity itself has marked obsolete (e.g. an old `UnityEngine.Networking` type, a deprecated `Input` API superseded by the new Input System, an old Addressables/Analytics call). This applies whether the `[Obsolete]` attribute lives in this project's own code, a first-party Unity API, or a third-party SDK.
- Before using any API you're not certain is current, check whether it (or its containing type) carries `[Obsolete]` — in the IDE this shows as a strikethrough/deprecation warning — and if so, find the modern replacement the deprecation message or current documentation points to, and use that instead.
- If a Tech Spec or existing surrounding code calls for behavior only reachable through an obsolete member with no direct replacement, don't silently keep using it — flag it back per the Handoff rule below instead of shipping new code against it.
- This rule governs new usage going forward. It does not by itself mandate a standalone refactor of pre-existing obsolete-API call sites outside your current change — remove one only if it falls within the lines/method you're already touching (see Boy Scout Rule above); otherwise flag it separately rather than expanding the current submission's scope.

## Correctness boundaries

- Validate only at real boundaries: user input, save-data deserialization, network messages (when the backend track is active), third-party SDK callbacks. Internal calls between your own classes can trust their contracts — don't defensive-check state that can't actually happen.
- Clean up coroutines and event subscriptions on `OnDisable`/`OnDestroy` — leaked coroutines and dangling event handlers are a recurring source of hard-to-reproduce bugs.

## Handoff

- Every submission to Code Reviewer includes a short note of assumptions/known limitations (per the Implementation Note handoff format in `TEAM_STRUCTURE.md`).
- Stay scoped to what the Tech Spec asked for. Don't refactor unrelated code, don't add speculative extensibility, don't fix unrelated issues in the same submission — flag them separately instead.
- When a Complex-tier feature (per Technical Architect's Triage) reaches completion, its handoff also includes the `README.md` required by `.claude/rules/client/feature-documentation.md`. Simple/Medium tier work is exempt from this.

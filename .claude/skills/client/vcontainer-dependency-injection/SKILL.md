---
name: vcontainer-dependency-injection
description: >
  VContainer dependency injection for the client track: `LifetimeScope`,
  `IContainerBuilder.Register<T>` with `Lifetime.Singleton`/`Scoped`/`Transient`,
  `RegisterComponentInHierarchy<T>`, `RegisterComponentInNewPrefab<T>`,
  `RegisterFactory`, keyed registration (`.Keyed()`/`[Key]`),
  `RegisterEntryPoint<T>`, `[Inject]` constructor/method/property injection,
  `EnqueueParent`, the full `IInitializable`/`IPostInitializable`/`IStartable`/
  `IAsyncStartable`/`IPostStartable`/`ITickable`/`IFixedTickable`/`ILateTickable`
  (and their `IPost*` counterparts) entry-point interfaces, and the Roslyn
  Source Generator that replaces reflection-based injection at runtime. Use it
  when a class needs a dependency it should not construct itself, when
  replacing a singleton or `FindObjectOfType` lookup, when scoping per-scene or
  per-session state, when startup order currently rests on `Awake`/`Start`
  timing, or when IL2CPP/AOT reflection cost or stripping needs the source
  generator turned on. Not for: the async body an `IAsyncStartable` calls
  (`unitask-async-programming`), pub/sub logic behind a registered publisher
  (`messagepipe-event-messaging`), the pipeline a scoped subscription observes
  (`r3-reactive-extensions`), `Game.Core.*` code, which takes plain interfaces
  and never a container (`coding-principles.md`).
---

# VContainer — Composition Root for the Client Track

## 1. Objective
Wire `Game.Client.*`'s object graph through explicit registration and scoped lifetimes — removing singletons, static service locators, and `FindObjectOfType` lookups — without creating a captive dependency (a short-lived service pinned alive by a longer-lived one), without letting disposables accumulate inside a long-lived scope, and without pushing a resolution error from compile time to first play.

## 2. Role
Act as the composition-root specialist for the client track: the one who decides where a type is registered, which scope owns it, how long it lives, and how a `MonoBehaviour` receives it — never the one who writes the registered services' internal logic.

## 3. When to invoke this skill
- A class in `Game.Client.*` constructs its own dependency, calls `FindObjectOfType`, or reaches a static singleton — replace it with a registration and constructor injection, per Dependency Inversion in `coding-principles.md`.
- Structuring `LifetimeScope`s: an app-lifetime root scope, a child scope per additive scene, a dynamic child scope for runtime-loaded content (a dungeon instance, a minigame).
- Registering scene or prefab `MonoBehaviour`s via `RegisterComponentInHierarchy<T>`/`RegisterComponentInNewPrefab<T>` so Unity-instantiated objects still receive their dependencies.
- Startup breaks or reorders itself between runs because two unrelated scripts' `Awake`/`Start` order is not guaranteed.
- A service is disposed while something still holds it, or survives a scene it should have died with — a lifetime question, not a logic bug.
- Negative trigger: writing the `async` body behind `IAsyncStartable.StartAsync` — that's `unitask-async-programming`.
- Negative trigger: the publish/subscribe or request/response logic behind a registered `IPublisher<T>`/`ISubscriber<T>` — that's `messagepipe-event-messaging`; the `RegisterMessagePipe` call itself stays here.
- Negative trigger: the `Observable<T>` pipeline a scoped subscription observes — that's `r3-reactive-extensions`; this skill only guarantees the subscription dies with its scope.
- Negative trigger: any `Game.Core.*` type — Shared Core takes its dependencies as plain constructor parameters against interfaces; the container that satisfies them exists only in `Game.Client.*`.
- A profiler or `tech-lead-performance` traces IL2CPP stripping or reflection-based injection cost on a hot resolution path — that is exactly the case the Source Generator exists for; see step 12 below.

## 4. How to use this skill
1. **Settle the layer before writing a registration** — a container reference inside `Game.Core.*` breaks the Shared Core boundary in `coding-principles.md`, and it is not fixable later without touching every constructor it hid.
2. **Register against the interface, not the concrete type** — `builder.Register<IAudioService, AudioService>(Lifetime.Singleton)` is what makes Dependency Inversion enforceable and lets `qa-automation-engineer` substitute a fake; registering the concrete type gives a consumer nothing it could not have `new`-ed itself.
3. **Derive the lifetime from the object's real lifespan, then check the graph for a captive dependency** — a `Scoped` service captured into a `Singleton`'s field outlives its own scope and keeps a disposed object reachable. VContainer does not reject this at build time, so it has to be read for deliberately, registration by registration.
4. **Never register an `IDisposable` as `Transient` in a long-lived scope** — VContainer tracks every disposable it creates and releases them only when the owning scope is disposed, so transient disposables resolved from the root scope accumulate for the whole run. Make it `Scoped` in a scope that actually ends, or take ownership manually outside the container.
5. **Shape the scope hierarchy around real lifetime boundaries**, per [VContainer's scoping documentation](https://vcontainer.hadashikick.jp/scoping/lifetime-overview) — root for app-wide services, a child scope per additive scene wired with `LifetimeScope.EnqueueParent(parent)` (optionally paired with `LifetimeScope.Enqueue(builder => ...)` for extra registrations) *before* `SceneManager.LoadSceneAsync(..., LoadSceneMode.Additive)` runs, a dynamic child for content loaded and unloaded at runtime via `currentScope.CreateChild(...)` / `CreateChildFromPrefab(...)`. Register the app root itself through a `VContainerSettings` asset (`Assets → Create → VContainer → VContainer Settings`, assigned to Preload Assets in Player Settings) rather than a scene object, so it survives every scene load. One flat root scope leaks session state across level loads.
6. **Build each scope once, because `RegisterComponentInHierarchy<T>` scans the scene** — that is the same traversal `performance-and-algorithms.md` bans `FindObjectOfType` for at runtime. One scan at scope construction is fine; rebuilding a child scope per spawn is the banned pattern wearing a registration API's clothes, so use `RegisterComponentInNewPrefab<T>` or a factory for anything spawned repeatedly.
7. **Keep `MonoBehaviour`s thin views over an injected plain C# class** — Unity never calls a `MonoBehaviour` constructor, so VContainer falls back to `[Inject]` method (or property/field) injection and the dependency stops being visible in a constructor signature. Put the logic in a registered plain class where the signature still documents what it needs. Remember `[Inject]` on a `MonoBehaviour` is never processed automatically — Unity has no universal "GameObject created" hook — so it only fires when the object is reached one of three ways: listed under the owning `LifetimeScope`'s Inspector "Auto Injection GameObjects", registered via a `RegisterComponent*` call, or instantiated at runtime through `container.Instantiate(prefab)` instead of `Object.Instantiate`. A prefab spawned with plain `Object.Instantiate` silently skips injection — this is a routine source of null Inspector-invisible dependencies, not a VContainer bug.
8. **Sequence startup through entry points rather than `Awake`/`Start` timing** — `RegisterEntryPoint<T>` runs its target on Unity's `PlayerLoopSystem` in a fixed order, independent of GameObject activation order: `IInitializable.Initialize()` → `IPostInitializable.PostInitialize()` → `IStartable.Start()`/`IAsyncStartable.StartAsync()` → `IPostStartable.PostStart()` → `IFixedTickable.FixedTick()` → `IPostFixedTickable.PostFixedTick()` → `ITickable.Tick()` → `IPostTickable.PostTick()` → `ILateTickable.LateTick()` → `IPostLateTickable.PostLateTick()` → `IDisposable.Dispose()` on scope teardown. Reach for an `IPost*` variant only when a real ordering dependency exists against the base phase (e.g. camera follow must read a `ILateTickable` position after every mover's `LateTick` has run) — otherwise it's an unneeded interface per KISS. Write the `IAsyncStartable` body per `unitask-async-programming`, including its cancellation on scope disposal.
9. **Use `ITickable`/`IFixedTickable`/`ILateTickable` instead of a per-object `Update()`/`FixedUpdate()`/`LateUpdate()` once many plain C# objects need a per-frame callback** — VContainer drives them from a single PlayerLoop insertion, which is exactly the centralized-manager pattern in `performance-and-algorithms.md`'s Update loop and callback overhead section. For a handful of objects this is not worth the indirection (KISS).
10. **Prove the graph resolves before calling the work done** — a missing or circular registration surfaces as a `VContainerException` when the scope builds, not as a compile error, so enter every scope at least once in the Editor. An unopened scope is an unverified scope. Enable the Diagnostics Window (`VContainerSettings` asset → check "Enable Diagnostics" → `Window → VContainer Diagnostics`) only while actively debugging a graph — the docs state it measurably degrades performance and allocates extra garbage, so it must never ship enabled.
11. **Ask which scope owns a service when its lifetime is genuinely ambiguous** — never widen a registration to `Singleton` just to silence a resolution failure; that converts a scoping question into a permanent leak and hides the real ownership question from review.
12. **Reach for the Roslyn Source Generator only once a profiler or `tech-lead-performance` has actually traced cost to reflection-based injection** — VContainer 1.13.0+ on Unity 2021.3+ ships a `VContainer.SourceGenerator.dll` (download from the GitHub Releases page, drop it under `Assets/`, give it the `RoslynAnalyzer` asset label, and disable it as a normal platform DLL — Any Platform off, Editor and Standalone off) that emits a sealed `__GeneratedInjector : IInjector` per eligible class, with `CreateInstance()`/`Inject()` replacing reflection at runtime and implicitly protecting the class from IL2CPP stripping. It changes nothing about how code is written — the same `[Inject]`/`[Key]` attributes work identically with or without it — so enabling it is pure infrastructure, never a coding-pattern change. A class is eligible only when it lives in an assembly referencing `VContainer.asmdef`, is not nested, is not a `struct`, and is at least `internal` (a `private` class always falls back to reflection silently) — treat this as an opt-in optimization for a measured IL2CPP/AOT hot path, not a default for every project (KISS/YAGNI). This supersedes the older `ILPostProcessor`-based "Pre IL Code Generation" mechanism, which VContainer's own docs mark deprecated — never introduce that older mechanism or a `VCONTAINER_CODEGEN_ENABLED`-style define into new work.
13. **Use `.Keyed(key)` at the registration site when two implementations of the same interface must resolve to different consumers** — `builder.Register<IWeapon, Sword>(Lifetime.Singleton).Keyed(WeaponType.Primary)`, consumed via `[Key(WeaponType.Primary)] IWeapon primaryWeapon` on a constructor, method, or (paired with `[Inject]`) a property/field parameter. Reach for this only when the two implementations are genuinely interchangeable by role — VContainer's own docs recommend a factory/provider over keyed injection of fine-grained values, so prefer `RegisterFactory` when the choice is closer to "construct with a runtime argument" than "select a fixed named implementation".

## 5. Specific goals / tasks this skill performs
- Replacing a singleton, service locator, or `FindObjectOfType` dependency with an interface registration and constructor injection.
- Designing the `LifetimeScope` hierarchy (root, per-scene child, dynamic child) against real object lifetimes.
- Choosing `Singleton`/`Scoped`/`Transient` per registration and auditing the graph for captive dependencies and accumulating disposables.
- Registering scene and prefab `MonoBehaviour`s, factories (`RegisterFactory`), keyed multi-implementation registrations (`.Keyed()`/`[Key]`), and wiring `RegisterMessagePipe`/`AddMessagePipe` into a `Configure()`.
- Sequencing startup via `IInitializable`/`IPostInitializable`/`IStartable`/`IAsyncStartable`/`IPostStartable` and moving per-frame work onto `ITickable`/`IFixedTickable`/`ILateTickable` (and their `IPost*` counterparts).
- Enabling and scoping the Roslyn Source Generator for a measured IL2CPP/AOT reflection-cost or stripping problem, without changing any `[Inject]`/`[Key]` authoring code.
- Out of scope: the async body behind `IAsyncStartable` (`unitask-async-programming`), pub/sub logic (`messagepipe-event-messaging`), reactive pipelines (`r3-reactive-extensions`), any `Game.Core.*` code (`csharp-engineer`).

## 6. Output format
```
## VContainer Work — <system/scope name>
- Scope: root / child (scene: <name>) / dynamic — parent wiring
- Registrations: <Type — Interface, Lifetime, rationale>
- MonoBehaviour wiring: RegisterComponentInHierarchy<T> / RegisterComponentInNewPrefab<T> / factory — targets
- Startup: IInitializable / IStartable / IAsyncStartable / ITickable / IFixedTickable / ILateTickable (+ IPost* where used) — order and rationale
- Captive-dependency check: <confirmed no shorter-lived service held by a longer-lived one>
- Disposable check: <confirmed no Transient IDisposable registered in a long-lived scope>
- Resolution verified: <scopes entered in the Editor, diagnostics clean>
- Source Generator: <enabled/not enabled — if enabled, which classes are eligible vs. still on reflection fallback>
- Layer: Game.Client.* — confirmed no container reference in Game.Core.*
- Known limitations: <...>
```

**Extended report — emit ONLY when the requester asks for it.** It replaces the one-line `Known limitations` above with all three fields:
```
- Known limitations: <what the wiring does not cover — omit this line entirely if there are genuinely none>
- Latent concerns: <lifetimes that hold only under the current scene flow, scopes never exercised, ownership deferred>
- Future remediation: <the concrete fix for each concern above, each with the condition that should trigger it>
```

## 7. Examples
**Example 1**
- Input: `AudioManager.Instance.PlaySfx(...)` is called from a dozen scripts, and the audio tests cannot run headless.
- Output: introduced `IAudioService`, registered `Register<IAudioService, AudioService>(Lifetime.Singleton)` in the root scope, replaced every `Instance` call with a constructor-injected dependency. `qa-automation-engineer` now substitutes a fake; the concrete implementation is swappable without touching a call site.

**Example 2**
- Input: "the per-dungeon `LootTable` fails to resolve from the HUD — just register it as `Singleton` so it's always available."
- Output: declined — the HUD resolving a dungeon-scoped service is the actual bug, and promoting it to `Singleton` would keep the previous dungeon's loot table alive across runs. Kept `LootTable` `Scoped` to the dungeon scope and gave the HUD a root-scoped view model the dungeon scope pushes into, so the failure surfaces as a scoping decision rather than as stale data three dungeons later.

**Example 3**
- Input: an enemy spawner builds a child `LifetimeScope` per enemy so each gets its own injected `IPathfinder`.
- Output: replaced the per-spawn scope with a registered factory resolved once from the pooled spawner. Each scope build was running `RegisterComponentInHierarchy<T>`'s scene scan per enemy — the runtime traversal `performance-and-algorithms.md` bans — and the per-enemy state did not need a scope at all.

**Example 4**
- Input: "IL2CPP strips our injected classes on device and startup reflection shows up in the mobile profiler — just turn on the VContainer source generator everywhere."
- Output: scoped it down instead of a blanket switch — added `VContainer.SourceGenerator.dll` with the `RoslynAnalyzer` label, confirmed the affected classes were `internal`/non-nested/non-struct (codegen-eligible), and left the handful of `private` nested helper classes on reflection since they were never on the profiled path. No `[Inject]`/`[Key]` code changed; the win was purely from the generated `__GeneratedInjector` replacing reflection and implicitly `[Preserve]`-protecting the eligible classes from stripping.

## 8. Edge cases & guardrails
- Never place a `LifetimeScope`, `IContainerBuilder`, or `[Inject]` reference inside `Game.Core.*` — it breaks the Shared Core boundary and makes the type unusable server-side.
- Never capture a `Scoped` or `Transient` dependency in a `Singleton` field — the singleton keeps a disposed object reachable and the bug surfaces one scene later, far from the registration that caused it.
- Never register an `IDisposable` as `Transient` in the root scope — every instance is retained until the app exits.
- Never build a `LifetimeScope` inside a spawn path or per-frame code — `RegisterComponentInHierarchy<T>` scans the scene on every build.
- Never resolve from the container at a call site (service-locator style) once a type is registered — that hides the dependency again and defeats the reason for injecting it.
- Never widen a lifetime to make a resolution exception disappear — diagnose which scope should own the service instead, and ask when it is genuinely unclear.
- Never assume a `[Inject]`-annotated `MonoBehaviour` gets injected just by existing in the scene — it only happens via the `LifetimeScope`'s "Auto Injection GameObjects" list, a `RegisterComponent*` call, or `container.Instantiate(prefab)`; a prefab spawned with plain `Object.Instantiate` silently keeps its dependencies null.
- Never mark a class `private` and then expect the Source Generator to cover it — codegen requires at least `internal` visibility, is not nested, and is not a `struct`; anything outside that falls back to reflection with no build-time warning, so verify eligibility before relying on the AOT/stripping guarantee it provides.
- Never ship a build with the VContainer Diagnostics Window's "Enable Diagnostics" left on in `VContainerSettings` — the docs state it measurably degrades performance and increases GC allocation; it is an Editor-only debugging aid.
- Never introduce the deprecated `ILPostProcessor`-based "Pre IL Code Generation" mechanism (or a `VCONTAINER_CODEGEN_ENABLED`-style define) in new work — VContainer's own docs mark it deprecated in favor of the Roslyn Source Generator.

---
name: vcontainer-dependency-injection
description: "VContainer DI: LifetimeScope, Register with lifetimes, component registration, factories, entry points (IStartable, ITickable), scope parenting, source generator for IL2CPP. Use instead of singletons or Find lookups."
user-invocable: false
---

# VContainer

Not for: the async body of `IAsyncStartable` (`unitask-async-programming`), pub/sub logic behind a registered publisher (`messagepipe-event-messaging`; the `RegisterMessagePipe` call stays here), the pipeline a scoped subscription observes (`r3-reactive-extensions`), Inspector-wired asset decoupling such as Runtime Sets or Event Channels (`unity-scriptableobject-architecture`: the test is whether the consumer should get the dependency by constructor or reference an asset other systems share), any Core type (plain interfaces and constructor parameters, never a container: `csharp-standards` → `coding-principles.md` Shared Core integrity).
Docs: https://vcontainer.hadashikick.jp/ (scoping: `/scoping/lifetime-overview`) — unversioned. Source Generator needs VContainer 1.13.0+ on Unity 2021.3+.

## Steps
1. **Settle the layer first** — a container reference in a Core assembly breaks the Shared Core boundary and cannot be removed later without touching every constructor it hid.
2. **Register against the interface** — `builder.Register<IAudioService, AudioService>(Lifetime.Singleton)`; registering the concrete type gives a consumer nothing it could not `new`, and blocks fakes for `qa-automation-engineer`.
3. **Derive the lifetime from the object's real lifespan, then audit for captive dependencies** — a `Scoped` or `Transient` service held in a `Singleton` field outlives its scope. VContainer does not reject this at build time; read each registration for it.
4. **Never register an `IDisposable` as `Transient` in a long-lived scope** — the container retains every disposable until its scope is disposed. Use `Scoped` in a scope that ends, or own it manually outside the container.
5. **Shape scopes around lifetime boundaries** — root for app-wide services; a child per additive scene via `LifetimeScope.EnqueueParent(parent)` (optionally `LifetimeScope.Enqueue(builder => ...)`) *before* `SceneManager.LoadSceneAsync(..., LoadSceneMode.Additive)`; a dynamic child via `currentScope.CreateChild(...)`/`CreateChildFromPrefab(...)`. Register the app root through a `VContainerSettings` asset (`Assets → Create → VContainer → VContainer Settings`, in Preload Assets) so it survives scene loads. One flat root leaks session state across levels.
6. **Build each scope once** — `RegisterComponentInHierarchy<T>` scans the scene, the traversal rule `csharp.md` bans (Hot paths: "Never `Find*`"). One scan at scope construction is fine; a scope per spawn is the banned pattern in disguise. Use `RegisterComponentInNewPrefab<T>` or a factory for repeated spawns.
7. **Keep `MonoBehaviour`s thin views over an injected plain class** — Unity never calls their constructor, so they fall back to `[Inject]` method/property/field injection, hiding dependencies. `[Inject]` fires only when the object is (a) listed in the owning `LifetimeScope`'s "Auto Injection GameObjects", (b) registered via `RegisterComponent*`, or (c) created with `container.Instantiate(prefab)`. A prefab spawned with `Object.Instantiate` silently keeps null dependencies.
8. **Sequence startup through entry points, not `Awake`/`Start` order** — `RegisterEntryPoint<T>` runs in a fixed PlayerLoop order: `IInitializable.Initialize` → `IPostInitializable.PostInitialize` → `IStartable.Start`/`IAsyncStartable.StartAsync` → `IPostStartable.PostStart` → `IFixedTickable.FixedTick` → `IPostFixedTickable.PostFixedTick` → `ITickable.Tick` → `IPostTickable.PostTick` → `ILateTickable.LateTick` → `IPostLateTickable.PostLateTick` → `IDisposable.Dispose` on scope teardown. Use an `IPost*` variant only for a real ordering dependency (e.g. camera follow reading positions after every `LateTick`). Write the `IAsyncStartable` body per `unitask-async-programming`, including cancellation on scope disposal.
9. **Move per-frame work of many plain objects onto `ITickable`/`IFixedTickable`/`ILateTickable`** — one PlayerLoop insertion instead of per-object `Update` (`csharp-standards` → `performance-and-algorithms.md` Update loop & callback overhead). For a handful of objects it is not worth it.
10. **Prove the graph resolves** — a missing or circular registration throws `VContainerException` when the scope builds, not at compile time, so enter every scope in the Editor once; an unopened scope is unverified. The Diagnostics Window (`VContainerSettings` → "Enable Diagnostics" → `Window → VContainer Diagnostics`) degrades performance and allocates: debugging only, never shipped enabled.
11. **Owning scope of a service ambiguous → `Needs-decision`, `Next: technical-architect`** — never widen to `Singleton` to silence a resolution failure; it turns a scoping question into a permanent leak.
12. **Source Generator only after a profiler or `gameplay-engineer` traces cost to reflection injection** — download `VContainer.SourceGenerator.dll` from the GitHub Releases, put it under `Assets/` with the `RoslynAnalyzer` asset label, disable it as a platform DLL (Any Platform, Editor, Standalone all off). It emits a sealed `__GeneratedInjector : IInjector` per eligible class, replacing reflection and protecting the class from IL2CPP stripping; `[Inject]`/`[Key]` code is unchanged. Eligible: assembly references `VContainer.asmdef`, not nested, not a `struct`, at least `internal` (a `private` class silently falls back to reflection with no warning).
13. **`.Keyed(key)` only when implementations are interchangeable by role** — `Register<IWeapon, Sword>(Lifetime.Singleton).Keyed(WeaponType.Primary)`, consumed by `[Key(WeaponType.Primary)] IWeapon w` on a constructor, method, or (with `[Inject]`) property/field. Prefer `RegisterFactory` when the choice is really "construct with a runtime argument"; VContainer's docs recommend a factory over keyed fine-grained values.

## Never
- Resolve from the container at a call site once a type is registered — it hides the dependency again.
- Introduce the deprecated `ILPostProcessor` "Pre IL Code Generation" mechanism or a `VCONTAINER_CODEGEN_ENABLED`-style define; VContainer's docs mark it deprecated for the Source Generator.

## Output
```
## VContainer Work — <system/scope>
- Scope: root / child (scene) / dynamic — parent wiring
- Registrations: <Type — Interface, Lifetime, why>
- MonoBehaviour wiring: <RegisterComponentInHierarchy / InNewPrefab / factory / container.Instantiate>
- Startup: <entry-point interfaces used, order, why>
- Captive-dependency and Transient-IDisposable checks: <confirmed / findings>
- Resolution verified: <scopes entered in the Editor, diagnostics clean — or "not run">
- Source Generator: <not enabled / enabled — eligible vs reflection-fallback classes>
- Known limitations: <...>
```
On request only, add `Latent concerns` and `Future remediation`, each with its trigger.

## Example
- "The dungeon `LootTable` fails to resolve from the HUD — register it `Singleton`" → declined: a HUD resolving a dungeon-scoped service is the bug, and `Singleton` would keep the previous dungeon's table alive. Kept it `Scoped` and gave the HUD a root-scoped view model the dungeon scope pushes into.

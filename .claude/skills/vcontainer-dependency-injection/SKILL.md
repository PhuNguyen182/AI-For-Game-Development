---
name: vcontainer-dependency-injection
description: "VContainer: LifetimeScope, Register, factories, IStartable/ITickable, scope parenting. Use instead of singletons."
user-invocable: false
---

# VContainer

- **Not for:** the async body of `IAsyncStartable` (`unitask-async-programming`).
- **Not for:** pub/sub logic behind a registered publisher (`messagepipe-event-messaging`).
  - **Stays here:** the `RegisterMessagePipe` call.
- **Not for:** the pipeline a scoped subscription observes (`r3-reactive-extensions`).
- **Not for:** Inspector-wired asset decoupling such as Runtime Sets or Event Channels (`unity-scriptableobject-architecture`).
  - **The test:** whether the consumer should get the dependency by constructor or reference an asset other systems share.
- **Not for:** any Core type (plain interfaces and constructor parameters, never a container: `csharp-standards` → `coding-principles.md` Shared Core integrity).
- **Docs:** https://vcontainer.hadashikick.jp/ (scoping: `/scoping/lifetime-overview`) — unversioned.
  - **Source Generator:** needs VContainer 1.13.0+ on Unity 2021.3+.

## Steps
1. **Settle the layer first:** a container reference in a Core assembly breaks the Shared Core boundary.
   - **Cost:** it cannot be removed later without touching every constructor it hid.
2. **Register against the interface:** `builder.Register<IAudioService, AudioService>(Lifetime.Singleton)`.
   - **Concrete type:** gives a consumer nothing it could not `new`, and blocks fakes for `qa-automation-engineer`.
3. **Derive the lifetime from the object's real lifespan, then audit for captive dependencies:**
   - **Captive dependency:** a `Scoped` or `Transient` service held in a `Singleton` field outlives its scope.
   - **Build time:** VContainer does not reject this; read each registration for it.
4. **Never register an `IDisposable` as `Transient` in a long-lived scope:** the container retains every disposable until its scope is disposed.
   - **Instead:** `Scoped` in a scope that ends, or own it manually outside the container.
5. **Shape scopes around lifetime boundaries:**
   - **Root:** for app-wide services.
   - **Additive scene:** a child per additive scene via `LifetimeScope.EnqueueParent(parent)`.
     - **Optional:** `LifetimeScope.Enqueue(builder => ...)`.
     - **Order:** `EnqueueParent` and the optional `Enqueue` go *before* `SceneManager.LoadSceneAsync(..., LoadSceneMode.Additive)`.
   - **Dynamic child:** via `currentScope.CreateChild(...)`/`CreateChildFromPrefab(...)`.
   - **App root:** register it through a `VContainerSettings` asset (`Assets → Create → VContainer → VContainer Settings`, in Preload Assets) so it survives scene loads.
   - **One flat root:** leaks session state across levels.
6. **Build each scope once:**
   - **`RegisterComponentInHierarchy<T>`:** scans the scene, the traversal rule `csharp.md` bans (Hot paths: "Never `Find*`").
   - **One scan at scope construction:** fine.
   - **A scope per spawn:** the banned pattern in disguise.
   - **Repeated spawns:** use `RegisterComponentInNewPrefab<T>` or a factory.
7. **Keep `MonoBehaviour`s thin views over an injected plain class:**
   - **`MonoBehaviour` constructor:** Unity never calls it, so `MonoBehaviour`s fall back to `[Inject]` method/property/field injection, hiding dependencies.
   - **`[Inject]` fires only when the object is:**
     - **(a):** listed in the owning `LifetimeScope`'s "Auto Injection GameObjects".
     - **(b):** registered via `RegisterComponent*`.
     - **(c):** created with `container.Instantiate(prefab)`.
   - **Prefab spawned with `Object.Instantiate`:** silently keeps null dependencies.
8. **Sequence startup through entry points, not `Awake`/`Start` order:**
   - **`RegisterEntryPoint<T>` runs in a fixed PlayerLoop order:**
     - **Initialize and start:** `IInitializable.Initialize` → `IPostInitializable.PostInitialize` → `IStartable.Start`/`IAsyncStartable.StartAsync` → `IPostStartable.PostStart`.
     - **Fixed ticks, after start:** → `IFixedTickable.FixedTick` → `IPostFixedTickable.PostFixedTick`.
     - **Frame ticks, after the fixed ticks:** → `ITickable.Tick` → `IPostTickable.PostTick` → `ILateTickable.LateTick` → `IPostLateTickable.PostLateTick`.
     - **Teardown, after the ticks:** → `IDisposable.Dispose` on scope teardown.
   - **Post variants:** an `IPost*` variant only for a real ordering dependency (e.g. camera follow reading positions after every `LateTick`).
   - **`IAsyncStartable` body:** write it per `unitask-async-programming`, including cancellation on scope disposal.
9. **Move per-frame work of many plain objects onto `ITickable`/`IFixedTickable`/`ILateTickable`:** one PlayerLoop insertion instead of per-object `Update`.
   - **Reference:** `csharp-standards` → `performance-and-algorithms.md` Update loop & callback overhead.
   - **A handful of objects:** not worth it.
10. **Prove the graph resolves:**
    - **Failure:** a missing or circular registration throws `VContainerException` when the scope builds, not at compile time.
    - **Check:** enter every scope in the Editor once; an unopened scope is unverified.
    - **Diagnostics Window (`VContainerSettings` → "Enable Diagnostics" → `Window → VContainer Diagnostics`):** degrades performance and allocates; debugging only, never shipped enabled.
11. **Owning scope of a service ambiguous:** `Needs-decision`, `Next: technical-architect`.
    - **`Singleton`:** never widen to it to silence a resolution failure; it turns a scoping question into a permanent leak.
12. **Source Generator only after a profiler or `gameplay-engineer` traces cost to reflection injection:**
    - **Install:** download `VContainer.SourceGenerator.dll` from the GitHub Releases, put it under `Assets/` with the `RoslynAnalyzer` asset label.
    - **Platform DLL:** disable it (Any Platform, Editor, Standalone all off).
    - **Emits:** a sealed `__GeneratedInjector : IInjector` per eligible class, replacing reflection and protecting the class from IL2CPP stripping.
    - **Unchanged:** `[Inject]`/`[Key]` code.
    - **Eligible:** assembly references `VContainer.asmdef`, not nested, not a `struct`, at least `internal`.
    - **`private` class:** silently falls back to reflection with no warning.
13. **`.Keyed(key)` only when implementations are interchangeable by role:**
    - **Registration:** `Register<IWeapon, Sword>(Lifetime.Singleton).Keyed(WeaponType.Primary)`.
    - **Consumption:** `[Key(WeaponType.Primary)] IWeapon w` on a constructor, method, or (with `[Inject]`) property/field.
    - **Runtime argument:** prefer `RegisterFactory` when the choice is really "construct with a runtime argument"; VContainer's docs recommend a factory over keyed fine-grained values.

## Never
- **Resolve from the container at a call site once a type is registered:** it hides the dependency again.
- **Introduce the deprecated `ILPostProcessor` "Pre IL Code Generation" mechanism or a `VCONTAINER_CODEGEN_ENABLED`-style define:** VContainer's docs mark it deprecated for the Source Generator.

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
```

## Example
- **"The dungeon `LootTable` fails to resolve from the HUD — register it `Singleton`":** declined.
  - **Why:** a HUD resolving a dungeon-scoped service is the bug, and `Singleton` would keep the previous dungeon's table alive.
  - **Did instead:** kept it `Scoped` and gave the HUD a root-scoped view model the dungeon scope pushes into.

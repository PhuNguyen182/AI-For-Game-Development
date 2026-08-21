---
name: vcontainer-dependency-injection
description: >
  VContainer dependency injection for the client track: `LifetimeScope`,
  `IContainerBuilder.Register<T>` with `Lifetime.Singleton`/`Scoped`/`Transient`,
  `RegisterComponentInHierarchy<T>`, `RegisterComponentInNewPrefab<T>`,
  `RegisterEntryPoint<T>`, `[Inject]` method injection, `EnqueueParent`, and the
  `IInitializable`/`IStartable`/`IAsyncStartable`/`ITickable` entry-point
  interfaces. Use it when a class needs a dependency it should not construct
  itself, when replacing a singleton or `FindObjectOfType` lookup, when scoping
  per-scene or per-session state, or when startup order currently rests on
  `Awake`/`Start` timing. Not for: the async body an `IAsyncStartable` calls
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

## 4. How to use this skill
1. **Settle the layer before writing a registration** — a container reference inside `Game.Core.*` breaks the Shared Core boundary in `coding-principles.md`, and it is not fixable later without touching every constructor it hid.
2. **Register against the interface, not the concrete type** — `builder.Register<IAudioService, AudioService>(Lifetime.Singleton)` is what makes Dependency Inversion enforceable and lets `qa-automation-engineer` substitute a fake; registering the concrete type gives a consumer nothing it could not have `new`-ed itself.
3. **Derive the lifetime from the object's real lifespan, then check the graph for a captive dependency** — a `Scoped` service captured into a `Singleton`'s field outlives its own scope and keeps a disposed object reachable. VContainer does not reject this at build time, so it has to be read for deliberately, registration by registration.
4. **Never register an `IDisposable` as `Transient` in a long-lived scope** — VContainer tracks every disposable it creates and releases them only when the owning scope is disposed, so transient disposables resolved from the root scope accumulate for the whole run. Make it `Scoped` in a scope that actually ends, or take ownership manually outside the container.
5. **Shape the scope hierarchy around real lifetime boundaries**, per [VContainer's scoping documentation](https://vcontainer.hadashikick.jp/scoping/lifetime-overview) — root for app-wide services, a child scope per additive scene wired with `EnqueueParent` *before* that scene loads, a dynamic child for content loaded and unloaded at runtime. One flat root scope leaks session state across level loads.
6. **Build each scope once, because `RegisterComponentInHierarchy<T>` scans the scene** — that is the same traversal `performance-and-algorithms.md` bans `FindObjectOfType` for at runtime. One scan at scope construction is fine; rebuilding a child scope per spawn is the banned pattern wearing a registration API's clothes, so use `RegisterComponentInNewPrefab<T>` or a factory for anything spawned repeatedly.
7. **Keep `MonoBehaviour`s thin views over an injected plain C# class** — Unity never calls a `MonoBehaviour` constructor, so VContainer falls back to `[Inject]` method injection and the dependency stops being visible in a constructor signature. Put the logic in a registered plain class where the signature still documents what it needs.
8. **Sequence startup through entry points rather than `Awake`/`Start` timing** — `RegisterEntryPoint<T>` with `IInitializable` for setup that must precede everything, then `IStartable`/`IAsyncStartable` for the startup work itself; write the async body per `unitask-async-programming`, including its cancellation on scope disposal.
9. **Use `ITickable` instead of a per-object `Update()` once many plain C# objects need a per-frame callback** — VContainer drives them from a single PlayerLoop insertion, which is exactly the centralized-manager pattern in `performance-and-algorithms.md`'s Update loop and callback overhead section. For a handful of objects this is not worth the indirection (KISS).
10. **Prove the graph resolves before calling the work done** — a missing or circular registration surfaces as a `VContainerException` when the scope builds, not as a compile error, so enable the LifetimeScope diagnostics in the Editor and enter every scope at least once. An unopened scope is an unverified scope.
11. **Ask which scope owns a service when its lifetime is genuinely ambiguous** — never widen a registration to `Singleton` just to silence a resolution failure; that converts a scoping question into a permanent leak and hides the real ownership question from review.

## 5. Specific goals / tasks this skill performs
- Replacing a singleton, service locator, or `FindObjectOfType` dependency with an interface registration and constructor injection.
- Designing the `LifetimeScope` hierarchy (root, per-scene child, dynamic child) against real object lifetimes.
- Choosing `Singleton`/`Scoped`/`Transient` per registration and auditing the graph for captive dependencies and accumulating disposables.
- Registering scene and prefab `MonoBehaviour`s, and wiring `RegisterMessagePipe`/`AddMessagePipe` into a `Configure()`.
- Sequencing startup via `IInitializable`/`IStartable`/`IAsyncStartable` and moving per-frame work onto `ITickable`.
- Out of scope: the async body behind `IAsyncStartable` (`unitask-async-programming`), pub/sub logic (`messagepipe-event-messaging`), reactive pipelines (`r3-reactive-extensions`), any `Game.Core.*` code (`csharp-engineer`).

## 6. Output format
```
## VContainer Work — <system/scope name>
- Scope: root / child (scene: <name>) / dynamic — parent wiring
- Registrations: <Type — Interface, Lifetime, rationale>
- MonoBehaviour wiring: RegisterComponentInHierarchy<T> / RegisterComponentInNewPrefab<T> / factory — targets
- Startup: IInitializable / IStartable / IAsyncStartable / ITickable — order and rationale
- Captive-dependency check: <confirmed no shorter-lived service held by a longer-lived one>
- Disposable check: <confirmed no Transient IDisposable registered in a long-lived scope>
- Resolution verified: <scopes entered in the Editor, diagnostics clean>
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

## 8. Edge cases & guardrails
- Never place a `LifetimeScope`, `IContainerBuilder`, or `[Inject]` reference inside `Game.Core.*` — it breaks the Shared Core boundary and makes the type unusable server-side.
- Never capture a `Scoped` or `Transient` dependency in a `Singleton` field — the singleton keeps a disposed object reachable and the bug surfaces one scene later, far from the registration that caused it.
- Never register an `IDisposable` as `Transient` in the root scope — every instance is retained until the app exits.
- Never build a `LifetimeScope` inside a spawn path or per-frame code — `RegisterComponentInHierarchy<T>` scans the scene on every build.
- Never resolve from the container at a call site (service-locator style) once a type is registered — that hides the dependency again and defeats the reason for injecting it.
- Never widen a lifetime to make a resolution exception disappear — diagnose which scope should own the service instead, and ask when it is genuinely unclear.

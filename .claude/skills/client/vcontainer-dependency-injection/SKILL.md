---
name: vcontainer-dependency-injection
description: >
  Technique for wiring the client-track object graph with VContainer —
  `LifetimeScope`/`IContainerBuilder`, `Register<T>` lifetimes (Singleton/
  Scoped/Transient), constructor injection, `RegisterComponentInHierarchy<T>`
  for MonoBehaviours, root/child/scene scoping, and the `IStartable`/
  `ITickable`/`IInitializable`/`IAsyncStartable` lifecycle interfaces that
  replace ad hoc singletons and `FindObjectOfType`. This is the composition
  root that wires the rest of this Cysharp-ecosystem stack together — it
  registers `MessagePipe`'s publishers/subscribers via `AddMessagePipe()`,
  starts `UniTask`-based async initialization via `IAsyncStartable`, and
  scopes `R3` subscription lifetimes to a `LifetimeScope`'s disposal — but it
  does not implement any of those systems' own logic. Use this whenever a
  class needs a dependency it shouldn't construct itself (Dependency
  Inversion in `coding-principles.md`), or whenever `unity-engineer`/
  `csharp-engineer` would otherwise reach for a singleton, a static service
  locator, or `FindObjectOfType`. Do not use this to write the async method
  body an `IAsyncStartable` calls into — that's `unitask-async-programming`.
  Do not use this to write the pub/sub/request-response logic MessagePipe
  registrations wire up — that's `messagepipe-event-messaging`. Do not use
  this to write the reactive pipeline a scoped `Observable` subscription
  belongs to — that's `r3-reactive-extensions`. Never use VContainer (or any
  DI container) inside `Game.Core.*` — Shared Core types take their
  dependencies as constructor parameters against plain interfaces
  (`IInputProvider`, a seeded RNG abstraction) per Dependency Inversion in
  `coding-principles.md`; the container that satisfies those interfaces at
  runtime lives entirely in `Game.Client.*`.
---

# VContainer — Dependency Injection for the Client Track

Source: [github.com/hadashiA/VContainer](https://github.com/hadashiA/VContainer).

## 1. Objective
Wire `Game.Client.*`'s object graph through constructor injection and explicit lifetime scopes — eliminating singletons, `FindObjectOfType`, and service-locator lookups — without creating a scope-lifetime bug (a resolved dependency outliving or under-living the scope that owns it) or hiding a dependency a reviewer can't see from a constructor signature.

## 2. Role
Act as the composition-root specialist for the client track: the one who decides where a type is registered, what its lifetime is, and how a `MonoBehaviour` gets its dependencies injected — not the one who writes the dependencies' internal logic.

## 3. When to invoke this skill
- A `MonoBehaviour` or plain C# class in `Game.Client.*` needs a dependency (an audio service, an input provider, a Shared Core rule evaluator) it currently constructs itself, calls `FindObjectOfType` for, or reaches via a static singleton — replace it with constructor injection per Dependency Inversion in `coding-principles.md`.
- Structuring `LifetimeScope`s for the project: a root scope for app-wide singletons (audio, save system, analytics), child/scene scopes for per-level or per-session state.
- Registering `MonoBehaviour` components that live in the scene via `RegisterComponentInHierarchy<T>`/`RegisterComponentInNewPrefab<T>` so they receive constructor-equivalent injection despite being Unity-instantiated.
- Sequencing app/level startup through `IInitializable` → `IStartable`/`IAsyncStartable` → `ITickable`, instead of relying on `Awake`/`Start` ordering, which Unity doesn't guarantee across unrelated scripts.
- Registering `MessagePipe`'s publishers/subscribers via `AddMessagePipe()` inside a VContainer `Configure()` — the registration call is this skill's territory; what gets published/subscribed is `messagepipe-event-messaging`'s.
- Negative trigger: writing the actual async method body behind `IAsyncStartable.StartAsync` — that's `unitask-async-programming`.
- Negative trigger: writing the pub/sub or request/response logic behind a registered `IPublisher<T>`/`ISubscriber<T>` — that's `messagepipe-event-messaging`.
- Negative trigger: writing the `Observable<T>` pipeline a scoped subscription observes — that's `r3-reactive-extensions`; this skill only ensures the subscription is disposed when its owning scope is.
- Negative trigger: any `Game.Core.*` code — Shared Core depends on interfaces, never on a container; the container lives entirely in `Game.Client.*`.

## 4. How to use this skill
1. **Register against the interface, not the concrete type**, whenever a consumer should depend on an abstraction (`builder.Register<IAudioService, AudioService>(Lifetime.Singleton)`) — this is what makes Dependency Inversion in `coding-principles.md` actually enforceable and what makes `qa-automation-engineer`'s unit tests possible (a fake `IAudioService` substitutes cleanly).
2. **Pick the lifetime deliberately.** `Singleton` for app-wide, stateless-or-shared services; `Scoped` for anything that should be recreated per level/session and disposed with that scope; `Transient` only when a fresh instance genuinely matters per resolution — default to `Singleton`/`Scoped` and justify a `Transient` choice explicitly, since it's the easiest lifetime to misuse into hidden per-call allocation.
3. **Scope the `LifetimeScope` hierarchy to match actual lifetime boundaries** — root scope for the app's lifetime, a child scope per additive scene via `EnqueueParent()`, a dynamic child scope for anything loaded/unloaded at runtime (a dungeon instance, a minigame). A flat, single root scope for everything defeats the purpose of scoping and leaks session state across level loads.
4. **Use `RegisterComponentInHierarchy<T>`/`RegisterComponentInNewPrefab<T>` for scene/prefab MonoBehaviours** instead of manually calling a hand-rolled "injector" — let VContainer's own Unity integration do the constructor-equivalent field/method injection.
5. **Sequence startup through the lifecycle interfaces, not `Awake`/`Start` timing assumptions.** `IInitializable` for synchronous setup that must run before anything else starts; `IStartable`/`IAsyncStartable` for the actual startup logic (the async body itself is `unitask-async-programming`'s territory); `ITickable` only when a plain C# class genuinely needs a per-frame callback without being a `MonoBehaviour`.
6. **Never let a resolved dependency outlive its scope.** A `Scoped` service captured into a `Singleton`'s field is a lifetime-mismatch bug (the singleton now holds a reference to something disposed when its short-lived scope ended) — VContainer doesn't catch this at compile time, so review registrations for this pattern explicitly.
7. **Register `MessagePipe` via `builder.RegisterMessagePipe(options => ...)` and its message types alongside other registrations** in the same `Configure()` — keep the registration call here, and hand the publish/subscribe logic itself to `messagepipe-event-messaging`.

## 5. Specific goals / tasks this skill performs
- Replacing a singleton/`FindObjectOfType`/service-locator dependency with constructor-injected registration.
- Designing `LifetimeScope` hierarchy (root/child/scene/dynamic) to match actual object lifetimes.
- Registering scene/prefab MonoBehaviours via `RegisterComponentInHierarchy<T>`/`RegisterComponentInNewPrefab<T>`.
- Sequencing startup via `IInitializable`/`IStartable`/`IAsyncStartable`/`ITickable`.
- Wiring `MessagePipe` registration (`AddMessagePipe()`/`RegisterMessagePipe`) into a `Configure()` method.
- Out of scope: the async body behind `IAsyncStartable` (`unitask-async-programming`), pub/sub logic itself (`messagepipe-event-messaging`), reactive pipelines (`r3-reactive-extensions`), any `Game.Core.*` code.

## 6. Output format
```
## VContainer Work — <system/scope name>
- Scope: root / child (scene: <name>) / dynamic — parent relationship
- Registrations: <Type — Interface, Lifetime (Singleton/Scoped/Transient), rationale>
- MonoBehaviour wiring: RegisterComponentInHierarchy<T> / RegisterComponentInNewPrefab<T> — targets
- Startup sequencing: IInitializable / IStartable / IAsyncStartable / ITickable — order and rationale
- Lifetime-mismatch check: confirmed no Scoped/Transient dependency captured into a longer-lived Singleton
- Known limitations: <...>
```

## 7. Examples
**Example 1**
- Input: an `AudioManager` singleton (`AudioManager.Instance.PlaySfx(...)`) is called from a dozen scattered scripts.
- Output: introduced `IAudioService`/`AudioService`, registered `Lifetime.Singleton` against the interface in the root `LifetimeScope`, replaced every call site's `AudioManager.Instance` with a constructor-injected `IAudioService` — `qa-automation-engineer` can now substitute a fake in tests, and the concrete `AudioService` is swappable without touching callers.

**Example 2**
- Input: "register MessagePipe's `IPublisher<DamageEvent>` in the scope and also design the damage-event filter pipeline."
- Output: registered `RegisterMessagePipe` and the `DamageEvent` message type in the `LifetimeScope`'s `Configure()`; handed the filter/middleware pipeline design itself to `messagepipe-event-messaging`, since that's a different concern from the registration call.

## 8. Edge cases & guardrails
- Never register a concrete type where an interface should be the contract — it defeats Dependency Inversion and blocks `qa-automation-engineer` from substituting a fake.
- Never capture a `Scoped`/`Transient` dependency into a `Singleton`'s field — a lifetime mismatch that outlives or dangles past its real scope.
- Never use `FindObjectOfType`, a static singleton, or a service locator once VContainer is in play for that dependency — that's exactly what this skill replaces, and `performance-and-algorithms.md` already bans `FindObjectOfType` at runtime outright.
- Never let a single flat root scope hold session-specific or per-level state — scope it to match the actual lifetime boundary.
- Never put a VContainer registration or `LifetimeScope` reference inside `Game.Core.*` — Shared Core depends on interfaces only; the container is a `Game.Client.*` concern exclusively.

# Client Track — Performance & Algorithm Engineering

Applies to: C# Software Engineer, Unity Engineer, UI/UX Programmer, Tech Lead – C# Unity, Tech Lead – SDK/Platform, Tech Lead – Performance, Technical Artist.

## Relationship to other rules

This file governs **algorithm and data-structure selection, memory-lifetime discipline, and Unity engine-specific optimization technique**, for all client-track code (`Game.Core.*` and `Game.Client.*`). It complements, not replaces, the baseline hot-path hygiene already required by `coding-principles.md`'s "Performance discipline" section (no per-frame allocations in `Update()`, caching `GetComponent<T>()`, pooling `UnityEngine.Object` instances, platform abstraction) — that section is the non-negotiable floor; this file goes further into engine-specific technique and CS-fundamentals discipline. Tech Lead – Performance still owns deep, escalated, measured optimization work beyond the baseline expected here — this file is the baseline every submission is expected to meet before it ever needs to reach that escalation.

## Core principle — measured, practical performance over theoretical purity

Pick the algorithm that satisfies both requirements at once — good, stable Big-O **and** hardware-friendly execution (sequential/cache-friendly memory access, predictable branching, low constant factors) — not one traded off against the other. Big-O is a starting filter, not the final answer: when two approaches have comparable or close complexity, the tie-breaker is which one actually runs closer to the hardware.

The cases below illustrate that reasoning applied to specific, recurring situations — they are worked examples of the principle, not an exhaustive or rigid checklist. Don't pattern-match a case onto one of these bullets by rote; apply the same reasoning (does it hold good/stable Big-O while running hardware-friendly?) to whatever the actual case in front of you is, including ones not listed here.

- **Insertion sort vs. bubble sort**: both are O(n²) worst case, but insertion sort does far fewer writes and has better cache behavior — it consistently outperforms bubble sort in practice. Prefer it for small or nearly-sorted data.
- **Quicksort vs. heapsort**: both average O(n log n), but quicksort's sequential, cache-friendly access pattern usually beats heapsort's array-index-jumping access pattern, despite heapsort's more consistent worst-case bound. In practice, prefer the runtime's built-in `Array.Sort`/`List<T>.Sort` (.NET's implementation is already an introspective sort — quicksort with a heapsort fallback and insertion sort for small partitions) over a hand-rolled sort, unless a specific, measured reason says otherwise.
- **Small-N structures**: for small collections, a simple linear scan often beats a theoretically superior O(log n) or O(1) structure, because the fixed overhead of the "smarter" structure dominates at small N. Treat any specific size threshold as something to verify empirically for the actual case, not a fixed number to assume.
- **Distance comparison**: `Vector3.Distance`/`Mathf.Sqrt` compute an actual square root, which is expensive relative to a multiply. When only comparing relative distances (e.g. "is this enemy within range?"), compare squared distances with `Vector3.sqrMagnitude`/`(a - b).sqrMagnitude` against a pre-squared threshold instead — same asymptotic cost, meaningfully cheaper per call, and it adds up fast across many entities checked every frame.

Whichever case it is — listed here or not — never adopt a "faster in theory, slower in practice" (or vice versa) choice as production code on folklore alone; validate it with an actual measurement (Unity Profiler, BenchmarkDotNet, or equivalent) for the specific case, especially before overriding a standard library implementation.

## Data structure selection

- Default to `List<T>` for sequential/iteration-heavy access. Avoid `LinkedList<T>` in hot paths — its node-based layout defeats cache locality, and its theoretical insertion/removal advantage rarely pays off against an array-backed structure's cache-friendly iteration in practice.
- Use `Dictionary<TKey, TValue>`/`HashSet<T>` for O(1) average lookups, but be aware of hashing overhead on small, bounded key sets in a hot path — a small `List<T>` linear scan or a switch/array-indexed lookup can outperform a dictionary below a certain N. Verify with a measurement before assuming the dictionary wins.
- Prefer `struct` (or `readonly record struct`) for small, short-lived, frequently-allocated value types (e.g. a `DamageInfo`) to avoid heap allocation and GC pressure — but be deliberate: a large struct copied repeatedly by value can cost more in copy overhead than the GC pressure it avoids. Pass larger structs by `in`/`ref readonly` where the project's confirmed C# language version supports it (see the Modern C# syntax caveat in `coding-principles.md`).
- Use `Span<T>`/`ReadOnlySpan<T>` to slice/iterate a buffer without allocating a new array or copy, where the project's confirmed C# language/runtime version supports it.

## Memory discipline

- No unbounded growth: a collection that grows over the game's lifetime without a defined release point is a leak in progress — pool it, cap it, or explicitly clear it at a defined lifecycle boundary.
- Every subscribed event, every started coroutine, every rented pooled object must have a matching unsubscribe/stop/return (this is required by `coding-principles.md`'s Correctness boundaries section — this file states the memory-safety reason behind it: an un-unsubscribed handler keeps the whole reference graph behind it alive).
- Avoid capturing large closures in long-lived delegates/lambdas — a captured reference to a MonoBehaviour or a large collection inside a delegate stored on a long-lived object keeps that entire graph alive for as long as the delegate exists.
- Pool anything instantiated/destroyed at high frequency. `coding-principles.md` already mandates this for `UnityEngine.Object` instances (projectiles, VFX, enemies); this file extends the same principle to any C# object with non-trivial construction cost, not just Unity objects.
- Don't retain references longer than their scope needs, especially anything reachable from a static field or a singleton service — a static reference is a guaranteed leak for the lifetime of the process, not just a temporary one.

## Algorithmic complexity discipline

- Know the time and space complexity of any non-trivial function you write. When it isn't obvious from the code, state it in a comment (per the comment-depth policy in `.claude/rules/shared/language-and-comments.md`) — an O(n²) nested loop over gameplay entities should be a deliberate, documented choice, not an accident nobody noticed.
- For any system that scales with player count, entity count, or inventory size, actively avoid quadratic-or-worse behavior once N is unbounded by design (entity-vs-entity checks, inventory search, etc.) — use spatial partitioning, indexing, or an explicitly bounded/capped N instead of a naive nested loop once N can plausibly grow past a small constant.
- Don't over-engineer for an N that structurally cannot grow — a fixed 4-slot ability bar doesn't need a hash-indexed lookup; a linear scan over 4 elements is both simpler (see KISS in `coding-principles.md`) and faster in practice than any "smarter" structure's overhead.

## Unity-specific optimization techniques

Baseline engine-level technique expected from routine client-track work, on top of the CS-fundamentals discipline above and the hot-path hygiene already required by `coding-principles.md`.

### Update loop & callback overhead
- **Never leave an empty Unity magic method on a MonoBehaviour** — `Update()`, `FixedUpdate()`, `LateUpdate()`, `OnGUI()`, `OnCollisionEnter()`/`OnTriggerEnter()`, etc. Unity's native engine detects which magic methods a script defines and registers a native→managed callback for every instance that has one; an empty body still pays that per-instance, per-frame (or per-event) transition cost. Delete any magic method whose body is empty — don't leave it as a stub "in case it's needed later" (also see YAGNI in `coding-principles.md`).
- At high object counts, prefer a single centralized manager that iterates a plain `List<T>` of registered objects and calls their update logic directly, instead of giving each object its own MonoBehaviour `Update()`. This collapses N native→managed transitions into one, and keeps the actual hot loop entirely in managed code where the JIT/IL2CPP can optimize it. Reserve this pattern for cases where the object count is actually large enough to matter (hundreds+) — for a handful of objects, per-object `Update()` is simpler and the transition cost is negligible (see KISS).
- `foreach` over a concrete `List<T>`/array does not allocate (struct enumerator). `foreach` over an interface-typed reference (`IEnumerable<T>`, `IList<T>`) or a LINQ-produced sequence boxes the enumerator and allocates on every iteration — prefer the concrete collection type in hot paths, consistent with the existing "no LINQ in hot paths" rule in `coding-principles.md`.

### Scripting & GC
- Cache `Camera.main` in `Awake()`/`Start()` instead of re-accessing it in `Update()` or other hot paths — repeated lookups carry overhead that a single cached reference avoids entirely.
- Never use `SendMessage`/`BroadcastMessage`/string-based `Invoke("MethodName", ...)` — these dispatch via reflection and are an order of magnitude slower than a direct method call, interface call, or `UnityEvent`/`Action`. Use a direct reference or an event system instead.
- In coroutines, cache reusable `WaitForSeconds`/`WaitForSecondsRealtime` instances instead of writing `yield return new WaitForSeconds(x)` inside a loop — each `new` there is a fresh heap allocation every iteration.
- Avoid repeated `transform.` property access in hot paths (e.g. reading then writing `transform.position` several times in the same method) — cache the value locally, mutate it, and write it back once.
- Avoid boxing value types into `object`- or non-generic-interface-typed parameters/collections in hot paths — each box is a heap allocation.
- Cache Animator parameter hashes with `Animator.StringToHash` once (e.g. a `static readonly` field) and use the `int` overloads of `SetFloat`/`SetBool`/`SetTrigger` — the string overloads re-hash the parameter name on every single call.
- Strip or gate `Debug.Log`/`Debug.LogWarning`/`Debug.LogError` calls out of shipped hot paths — each call has real string-formatting and I/O cost even with no debugger attached. Wrap hot-path logging behind a `[Conditional("UNITY_EDITOR")]`-gated helper (or an editor-only logging abstraction) instead of leaving raw calls in per-frame code.
- Only update UI text/visuals when the underlying value actually changed, not unconditionally every frame — a `.ToString()` call plus a Text/TMP geometry rebuild on an unchanged number is wasted work repeated every single frame.

### Rendering & draw calls
- Reduce draw calls with static batching for non-moving geometry and GPU instancing for many instances of the same mesh+material (foliage, projectiles, crowds) — don't accept one draw call per object by default.
- Keep material/shader variant count under control. Use `MaterialPropertyBlock` for per-instance property changes (e.g. per-instance tint) instead of instantiating a new material per object.
- Use LOD Groups for complex meshes viewed at varying distances, and Occlusion Culling where a scene has significant hidden geometry — both cut GPU work, not just CPU.
- Set each `Animator`'s Culling Mode to "Cull Update Transforms" or "Based On Renderers" (not "Always Animate") so off-screen characters skip animation evaluation entirely instead of paying for it unseen.
- Never use `OnGUI`/IMGUI for runtime UI shown to players — it's a legacy immediate-mode system with real per-call overhead, intended for editor tooling. Use UGUI or UI Toolkit for anything players see.
- Split static and frequently-updating UI into separate `Canvas` components. Any change to one element forces Unity to rebuild batch geometry for the entire Canvas it's on — an animated health bar sharing a Canvas with static menu chrome forces the whole menu to rebuild every frame it updates.

### Physics
- Use the simplest collider shape the gameplay requirement allows — primitive colliders (box/sphere/capsule) over `MeshCollider` wherever possible; a mesh collider is dramatically more expensive to evaluate.
- Configure the Physics/Physics2D layer collision matrix to prune collision checks between layers that should never interact, instead of relying on runtime `if` checks inside collision callbacks to filter them out after the fact.
- Treat `Fixed Timestep` as a deliberate tuning choice, not a default left untouched — a smaller timestep improves physics fidelity at a direct, linear CPU cost; don't lower it below what the game's mechanics actually need.

### Assets & memory footprint
- Set texture import settings (compression format, max size, mip maps) deliberately per platform — an uncompressed or oversized texture is one of the most common sources of both load-time and runtime memory bloat, especially on mobile.
- Use Addressables (or Asset Bundles) to load and release content by actual need rather than holding everything resident. An Addressables handle that's never released is a memory leak in exactly the same sense as any other unreleased resource — see Memory discipline above.
- Use appropriate audio compression (e.g. Vorbis/ADPCM) and streaming for long clips instead of loading everything as decompressed PCM in memory.
- Prefer Unity's built-in `UnityEngine.Pool.ObjectPool<T>` (or `GenericPool<T>`) over a hand-rolled pool implementation unless a specific, measured case needs custom behavior it doesn't offer — same "prefer the built-in, well-tested implementation" principle as sorting above.

### Garbage Collector settings
- Confirm Incremental GC is enabled (Player Settings → Configuration) for this project rather than assuming the default — it spreads collection work across multiple frames instead of causing a single large stall, which matters far more on mobile than PC.
- Never call `GC.Collect()` in gameplay hot paths. Forcing a full collection defeats the incremental scheduler and causes exactly the stall it exists to avoid — the fix for allocation pressure is to stop allocating (pooling, struct reuse, avoiding boxing), not to force more frequent collection.

### Multithreading — escalation territory, not a routine default
- The Job System + Burst Compiler is the right tool for genuinely parallelizable, CPU-bound bulk work (large-scale simulation, batched pathfinding, etc.) — but most Unity APIs are main-thread-only, and introducing Job System/Burst/DOTS is an architecture-level decision with real added complexity, not a routine optimization. Per `TEAM_STRUCTURE.md`, this is Tech Lead – Performance's territory once profiling shows a genuinely CPU-bound, parallelizable bottleneck — don't reach for it as a first-pass default (see KISS/YAGNI in `coding-principles.md`).

## Verification

- Any claimed performance improvement — in code review, in a handoff note, or in an Implementation Note — must be backed by a measurement (Unity Profiler frame time/allocations, or a micro-benchmark), not asserted from Big-O alone.
- When there's no measured evidence that added complexity pays off, default to the simpler version. This doesn't override KISS/YAGNI in `coding-principles.md` — it's the same principle applied specifically to algorithm and data-structure choice.

## Rules

- No per-frame heap allocations, no unnecessary boxing, no LINQ in hot paths — already required by `coding-principles.md`; this file adds the reasoning (allocation and GC pressure) and extends it to algorithm/data-structure choice generally, not just `Update()`-loop code.
- Prefer the runtime's built-in, well-tested collection/algorithm implementations over hand-rolled ones unless a specific, measured case proves otherwise.
- Every complexity/practicality trade-off claim ships with a measurement, not just an assertion.
- Stay scoped to what the Tech Spec actually needs — don't add a low-level optimization nobody asked for at the cost of readability, unless a measured problem justifies it (see Tech Lead – Performance's escalation path in `TEAM_STRUCTURE.md` for when a problem is deep enough to warrant that trade-off).

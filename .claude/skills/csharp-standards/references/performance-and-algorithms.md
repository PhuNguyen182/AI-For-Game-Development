# Performance and algorithms

Synthesized from project decisions; adds to rule `csharp.md` hot paths. Deep, measured optimisation past this baseline: `unity-performance-engineer`.

## Core principle — measured, practical performance over theoretical purity
- Good, stable Big-O and hardware-friendly execution (sequential access, predictable branches, low constants); Big-O filters, the hardware breaks ties.
- Built-ins over hand-rolled: `Array.Sort`/`List<T>.Sort`, `UnityEngine.Pool.ObjectPool<T>`.
- Range checks compare `sqrMagnitude` against a pre-squared threshold, not `Vector3.Distance`.

## Data structure selection
- `List<T>`/array for iteration; avoid `LinkedList<T>` in hot paths. Keyed lookup when N is unbounded; a small bounded set in a hot path → linear scan or array index — measure the threshold, never assume it.
- `struct`/`readonly record struct` for small, short-lived values; pass large ones by `in` — copying can cost more than the GC it saves. `Span<T>` slices without copying.

## Memory discipline
- No unbounded growth: pool, cap, or clear at a lifecycle boundary.
- Every subscription, coroutine, pooled rent, load handle and native allocation is released on every path; an unreleased handler keeps its whole reference graph alive.
- No large captures in long-lived delegates.
- Pool any high-frequency object with non-trivial construction cost, not only `UnityEngine.Object`.
- Anything reachable from a static or singleton lives as long as the process.

## Algorithmic complexity discipline
- State non-obvious complexity in a comment; an O(n²) pass over entities is deliberate and documented.
- N unbounded by design (players, entities, inventory) → spatial partitioning, an index or a cap. N structurally fixed (a 4-slot bar) → linear scan.

## Unity-specific optimization techniques

### Update loop & callback overhead
- Delete empty magic methods (`Update`, `OnTriggerEnter`, …): Unity pays a native→managed call per instance for any defined body.
- Hundreds+ objects → one manager iterating a `List<T>`; a handful → per-object `Update()`.
- `foreach` over `IEnumerable<T>`/`IList<T>` or LINQ boxes the enumerator; iterate the concrete `List<T>`/array in hot paths.

### Scripting & GC
- Cache `Camera.main` and `GetComponent` in `Awake`; read a `transform` value once, mutate locally, write once.
- Never `SendMessage`/`BroadcastMessage`/string `Invoke` — reflection dispatch.
- Cached `WaitForSeconds`/`WaitForSecondsRealtime`, never `new` inside a coroutine loop.
- Animator: `static readonly int` from `Animator.StringToHash`, `int` overloads only.
- Hot-path logging through a `[Conditional("UNITY_EDITOR")]` helper, never raw `Debug.Log`.
- Rewrite UI text only when the value changed.
- Confirm Incremental GC is on (Player Settings → Configuration); never assume it. Never `GC.Collect()` in gameplay; stop allocating instead.

### Rendering & draw calls
- Static batching for static geometry; GPU instancing for many copies of one mesh + material.
- `MaterialPropertyBlock` for per-instance values, never a material per object.
- Animator Culling Mode `Cull Update Transforms` or `Based On Renderers`, not `Always Animate`.
- No `OnGUI` for player-facing UI.
- Split static and frequently-updated UI into separate `Canvas`es; any change rebuilds its whole Canvas.

### Physics
- Simplest collider that plays correctly, primitives over `MeshCollider`; prune pairs in the layer collision matrix, not with `if`s in callbacks; `Fixed Timestep` no finer than the mechanics need.

### Assets & memory footprint
- Texture compression and max size set per platform; load and release content by need — an unreleased Addressables handle is a leak.

### Multithreading — escalation territory, not a routine default
- Jobs, Burst and DOTS are an architecture decision: `technical-architect` decides, after a Profiler capture shows a CPU-bound, parallelizable bottleneck. Never a first-pass default.

## Verification
- Every performance claim (review, handoff, Implementation Note) carries a measurement — Profiler frame time/GC Alloc or a micro-benchmark — never Big-O alone. How: skill `unity-profiler-diagnostics`.
- No measured payoff → keep the simpler version.

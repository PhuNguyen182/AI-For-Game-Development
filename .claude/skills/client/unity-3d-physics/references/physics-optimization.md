# Physics Optimization — Diagnosis & Tuning

Covers SKILL.md step 10 (Profiler/Memory Profiler/Physics Debug window-driven physics optimization).

## Overview

Unity's physics optimization workflow is measure-first: identify the actual bottleneck with the Unity Profiler, Memory Profiler, and Physics Debug window before applying any of the CPU or memory techniques below. The manual is explicit that these three diagnostic tools must be understood before attempting any optimization in this area.

CPU-side problems typically surface as elevated cost in `Physics.FixedUpdate`/`Physics.Simulate`, or as a rising call count on `Physics.Simulate` when a heavy frame forces the fixed-timestep loop to run catch-up iterations. Memory-side problems typically surface as GC allocations from collision callbacks or physics queries (e.g. repeated `RaycastHit` array allocation). Diagnose with the right tool for the symptom, then apply the matching technique — don't tune blind.

## Manual

| Page | URL | Covers |
|---|---|---|
| Optimize the physics system | https://docs.unity3d.com/Manual/physics-optimization.html | Diagnostic tools overview: Unity Profiler, Memory Profiler, Physics Debug window |
| Optimize the physics system for CPU usage | https://docs.unity3d.com/Manual/physics-optimization-cpu.html | Simulation frequency, manual simulation, collider/layer management, sleeping, solver iterations |
| Optimize the physics system for memory usage | https://docs.unity3d.com/Manual/physics-optimization-memory.html | Collision callback allocation, physics query allocation |
| Understand physics performance issues | https://docs.unity3d.com/Manual/physics-performance-issues.html | Root causes of physics-related frame stutter |
| Physics scripting reference | https://docs.unity3d.com/ScriptReference/Physics.html | Static tuning members (solver iterations, sleep threshold, callback behavior, simulation mode) |
| Time.fixedDeltaTime scripting reference | https://docs.unity3d.com/ScriptReference/Time-fixedDeltaTime.html | The simulation-frequency knob |

## Diagnostic tools

| Tool | What it reveals |
|---|---|
| Unity Profiler (Window > Analysis > Profiler) | Primary CPU measurement tool; identifies bottlenecks inside `Physics.FixedUpdate`/`Physics.Simulate` with detailed breakdowns of physics phases including broad-phase and narrow-phase processing. |
| Memory Profiler (separate package) | Detects excessive memory allocations from physics operations — e.g. excessive `RaycastHit` array allocation or frequent collision-data creation — to help reduce garbage collection overhead. |
| Physics Debug window (Window > Analysis > Physics Debug) | Visual diagnostics: displays collision shapes, contacts, and broad-phase bounding boxes, and shows Rigidbody sleep states — reveals overly complex colliders, unnecessary interactions, or objects failing to sleep. |

## CPU optimization

| Technique | Effect |
|---|---|
| Fixed timestep configuration (`Time.fixedDeltaTime`) | Controls physics simulation frequency; lowering it reduces how often the simulation runs, and helps manage potential performance spirals. |
| Manual physics simulation (`Physics.simulationMode`) | Gives control over when physics calculations occur so they can be aligned with overall game performance instead of running automatically every fixed step. |
| Query-only mode (`Physics.simulationMode`) | Prevents the default physics update loop from running, for games that only need collision queries and not active simulation — removes unnecessary per-step overhead. |
| Transform synchronization management | Optimizes synchronization of Transform values with the physics system to improve performance and query accuracy. |
| Static collider management (Kinematic Rigidbody vs. moving static colliders) | Using a Kinematic Rigidbody instead of repeatedly moving a static collider avoids the broad-phase rebuild cost that moving "static" colliders otherwise incurs. |
| Layer Collision Matrix configuration | Reduces collision-calculation overhead by defining which GameObject layers are allowed to interact, pruning unnecessary checks. |
| Broad-phase pruning algorithm selection | Optimizes physics performance in large scenes by choosing the most efficient broad-phase algorithm for that scene's object distribution. |
| Collider type selection | Choosing the collider type appropriate to a GameObject's role (vs. a more complex collider than necessary) keeps per-object collision cost down. |
| Mesh Collider cooking options | Proper configuration of cooking parameters optimizes Mesh Collider performance. |
| Rigidbody sleeping | Enabling sleeping for stationary objects reduces CPU load and improves physics performance by skipping simulation work on bodies at rest. |
| Solver iteration tuning (`Physics.defaultSolverIterations`, `Physics.defaultSolverVelocityIterations`) | Adjusting solver iteration counts balances simulation accuracy against CPU cost. |
| Collision detection mode selection | Choosing the appropriate detection mode (e.g. discrete vs. continuous) balances collision accuracy against CPU performance. |

## Memory optimization

| Technique | Effect |
|---|---|
| Collision callback optimization (`Physics.reuseCollisionCallbacks`) | Reduces memory allocations caused by frequent collision events, lowering garbage collection overhead from repeated collision-event handling. |
| Physics query optimization (NonAlloc query variants, batch processing) | Reduces garbage collection overhead by using efficient, non-allocating query versions and batching queries instead of allocating fresh result arrays per call. |

Both techniques serve the same goal stated on the memory page: efficient physics memory usage reduces GC overhead and keeps gameplay smooth — verify allocation reduction with the Memory Profiler rather than assuming a technique helped.

## Common root causes of physics performance issues

| Symptom | Root cause |
|---|---|
| Frame-rate drops or stuttering during physics-heavy scenes | Physics simulation runs on a fixed-frequency cycle decoupled from the main update loop. When a heavy graphics or logic frame occurs, the physics system must be called multiple times in a single frame to catch back up to game time — compounding the cost of an already expensive frame. |
| `Physics.Processing`/`Physics.Simulate` call count climbing toward ~10 in a single frame (CPU Usage Profiler module, Calls column) | Same catch-up mechanism: 1 call per frame is normal, a count approaching 10 indicates accumulated fixed-timestep debt from a preceding heavy frame. |

Detection method: monitor the CPU Usage Profiler module's Calls column for `Physics.Processing`/`Physics.Simulate`. Mitigation order recommended by the manual: first try reducing physics simulation frequency (`Time.fixedDeltaTime`); if the problem persists, find and fix what caused the originating heavy frame, then use the Physics Profiler module's detailed breakdown to investigate specific physics tasks.

## Relevant static Physics/Time API knobs

| Member | Description |
|---|---|
| `Physics.simulationMode` | Controls when Unity executes the physics simulation (this is the current member for manual/query-only simulation control — `autoSimulation` and `autoSyncTransforms` were not found as static members on the current Physics scripting reference page). |
| `Physics.defaultSolverIterations` | Determines how accurately Rigidbody joints and collision contacts are resolved (default 6). Must be positive. |
| `Physics.defaultSolverVelocityIterations` | Affects how accurately Rigidbody joints and collision contacts are resolved (default 1). Must be positive. |
| `Physics.sleepThreshold` | The mass-normalized energy threshold, below which objects start going to sleep. |
| `Physics.defaultContactOffset` | The default contact offset of newly created colliders. |
| `Physics.reuseCollisionCallbacks` | Determines whether the garbage collector should reuse only a single instance of a Collision type for all collision callbacks. |
| `Physics.improvedPatchFriction` | Enables an improved patch friction mode that guarantees static and dynamic friction do not exceed analytical results. |
| `Physics.invokeCollisionCallbacks` | Whether or not MonoBehaviour collision messages will be sent by the physics system. |
| `Time.fixedDeltaTime` | The interval in seconds of in-game time at which physics and other fixed-frame-rate updates (`FixedUpdate`) occur; scales with `Time.timeScale`, and the value is quantized internally so the getter may return a value differing by a single bit from what was set. |

This reference operationalizes the baseline physics performance discipline already required by `.claude/rules/client/performance-and-algorithms.md` (Physics section) — Profiler/Memory Profiler/Physics Debug window measurement, not assertion, backs every optimization claim.

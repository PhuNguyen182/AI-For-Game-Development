# Physics Optimization — Diagnosis, Techniques & Tuning Knobs

Sources: [Optimize the physics system](https://docs.unity3d.com/Manual/physics-optimization.html), [Optimize for CPU usage](https://docs.unity3d.com/Manual/physics-optimization-cpu.html), [Optimize for memory usage](https://docs.unity3d.com/Manual/physics-optimization-memory.html), [Understand physics performance issues](https://docs.unity3d.com/Manual/physics-performance-issues.html).
Covers: SKILL.md §4 — **"Diagnose with the tool that matches the symptom before tuning anything"**.

Physics tuning is measure-first, and the most valuable thing in this file is
the distinction between a physics cost and a physics *symptom*: the fixed
timestep runs decoupled from the frame, so a slow frame elsewhere makes PhysX
run repeatedly to catch up, which shows in the Profiler as physics being
expensive when nothing about physics changed.

## Contents

- [Diagnosis](#diagnosis)
- [CPU techniques](#cpu-techniques)
- [Memory techniques](#memory-techniques)
- [Tuning knobs](#tuning-knobs)

## Diagnosis

| Tool | What it reveals | Source |
|---|---|---|
| Unity Profiler | Cost inside `Physics.FixedUpdate`/`Physics.Simulate`, split by broadphase and narrowphase — the primary CPU evidence | [Optimize the physics system](https://docs.unity3d.com/Manual/physics-optimization.html) |
| Profiler Calls column on `Physics.Simulate` | One call per frame is normal; a count climbing toward ten is fixed-timestep debt repaid after a preceding heavy frame, so the fix is that frame, not the physics settings | [Understand physics performance issues](https://docs.unity3d.com/Manual/physics-performance-issues.html) |
| Memory Profiler | Allocation from collision callbacks and from query result arrays — the GC pressure that reads as intermittent stutter | [Optimize for memory usage](https://docs.unity3d.com/Manual/physics-optimization-memory.html) |
| Physics Debug window | Collision shapes, contacts, broadphase bounds, and sleep state — where an over-complex collider or a body that never sleeps becomes visible | [Optimize the physics system](https://docs.unity3d.com/Manual/physics-optimization.html) |

## CPU techniques

| Technique | What it decides | Source |
|---|---|---|
| `Time.fixedDeltaTime` | Simulation frequency; raising it cuts steps per second directly and is the first relief for catch-up spirals, at the cost of fidelity | [Optimize for CPU usage](https://docs.unity3d.com/Manual/physics-optimization-cpu.html) |
| `Physics.simulationMode` | Whether Unity steps physics automatically, on script demand, or not at all — Script mode aligns simulation with the game's own pacing, and query-only removes the step entirely for games that only cast rays | [Optimize for CPU usage](https://docs.unity3d.com/Manual/physics-optimization-cpu.html) |
| Kinematic Rigidbody instead of a moved static collider | A moved static collider forces a broadphase rebuild; a kinematic body does not | [Optimize for CPU usage](https://docs.unity3d.com/Manual/physics-optimization-cpu.html) |
| Layer collision matrix | Prunes pairs before broadphase, which is the cheapest place to remove work | [Optimize for CPU usage](https://docs.unity3d.com/Manual/physics-optimization-cpu.html) |
| Broadphase algorithm selection | Chooses the pruning structure that suits the scene's object distribution — matters mainly in large or unevenly populated worlds | [Optimize for CPU usage](https://docs.unity3d.com/Manual/physics-optimization-cpu.html) |
| Collider type selection | A primitive where a mesh was used is usually the single largest per-object saving available | [Optimize for CPU usage](https://docs.unity3d.com/Manual/physics-optimization-cpu.html) |
| Mesh Collider cooking options | Cooking settings trade bake time against runtime query cost — worth setting deliberately on any mesh collider that survives review | [Optimize for CPU usage](https://docs.unity3d.com/Manual/physics-optimization-cpu.html) |
| Rigidbody sleeping | Settled bodies are skipped entirely; `NeverSleep` is a standing per-body cost to justify | [Optimize for CPU usage](https://docs.unity3d.com/Manual/physics-optimization-cpu.html) |
| Transform synchronisation management | Controls when Transform writes are pushed into the physics scene, improving both cost and query accuracy | [Optimize for CPU usage](https://docs.unity3d.com/Manual/physics-optimization-cpu.html) |
| Collision detection mode | Continuous variants sweep and cost more; apply per body rather than project-wide | [Collision detection](https://docs.unity3d.com/Manual/collision-detection.html) |

## Memory techniques

| Technique | What it decides | Source |
|---|---|---|
| `Physics.reuseCollisionCallbacks` | Reuses one `Collision` instance for every callback, removing per-contact allocation. The cost: a cached reference to that object changes underneath the holder, so callbacks must read it and not store it | [Optimize for memory usage](https://docs.unity3d.com/Manual/physics-optimization-memory.html) |
| `NonAlloc` query variants and result buffers | Fills a caller-owned array instead of allocating per call — the direct application of `performance-and-algorithms.md`'s Memory discipline section to physics queries | [Optimize for memory usage](https://docs.unity3d.com/Manual/physics-optimization-memory.html) |
| `Physics.invokeCollisionCallbacks` | Turns off MonoBehaviour collision messages entirely, for simulations whose results are read by polling instead | [Physics.invokeCollisionCallbacks](https://docs.unity3d.com/ScriptReference/Physics-invokeCollisionCallbacks.html) |

## Tuning knobs

| Member | What it decides | Source |
|---|---|---|
| `Physics.defaultSolverIterations` | Position-solver accuracy, default 6; 10–20 stabilises joints, and the cost is paid by every jointed body in the project | [Physics.defaultSolverIterations](https://docs.unity3d.com/ScriptReference/Physics-defaultSolverIterations.html) |
| `Physics.defaultSolverVelocityIterations` | Velocity-solver accuracy, default 1; raise for bounce and impact fidelity specifically | [Physics.defaultSolverVelocityIterations](https://docs.unity3d.com/ScriptReference/Physics-defaultSolverVelocityIterations.html) |
| `Physics.sleepThreshold` | Mass-normalised energy below which bodies sleep — raising it settles a scene sooner at the risk of bodies sleeping mid-motion | [Physics.sleepThreshold](https://docs.unity3d.com/ScriptReference/Physics-sleepThreshold.html) |
| `Physics.defaultContactOffset` | Distance at which contacts start being generated; too small causes missed contacts, too large causes visible float | [Physics.defaultContactOffset](https://docs.unity3d.com/ScriptReference/Physics-defaultContactOffset.html) |
| `Physics.improvedPatchFriction` | Guarantees static and dynamic friction stay within analytical bounds — the fix for objects that creep on slopes they should hold on | [Physics.improvedPatchFriction](https://docs.unity3d.com/ScriptReference/Physics-improvedPatchFriction.html) |
| `Time.fixedDeltaTime` | Scales with `Time.timeScale` and is quantised internally, so the getter can return a value one bit from what was assigned | [Time.fixedDeltaTime](https://docs.unity3d.com/ScriptReference/Time-fixedDeltaTime.html) |

Every claim made from this file ships with the measurement that produced it,
per `performance-and-algorithms.md`'s Verification section.

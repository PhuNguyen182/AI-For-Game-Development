# Systems, Update Order & the Job Hand-off

Sources: [System groups and update order](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/systems-update-order.html), [SystemBase overview](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/systems-systembase.html), [SystemAPI overview](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/systems-systemapi.html).
Covers: SKILL.md §4 — **"Prefer `ISystem` in an existing `SystemGroup`"**.

Which system type to write, where it updates, and the exact point at which the
work stops being an ECS concern. Everything past that point — `JobHandle`
chaining, `.Complete()` placement, container disposal — is
`unity-job-system-and-burst`, and is deliberately not restated here.

## System type

| Subject | What it decides | Source |
|---|---|---|
| `ISystem` | Unmanaged struct, Burst-compilable — the default, and the only one that can be `[BurstCompile]`d | [Systems comparison](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/systems-comparison.html) |
| `SystemBase` | Managed class; can call managed APIs and capture managed state, but is not Burst-compilable — pick it only when a managed API is genuinely required | [SystemBase overview](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/systems-systembase.html) |
| `SystemAPI` | Source-generated cached access to queries, lookups, and singletons — only usable inside a system, so it cannot be lifted into a plain static helper | [SystemAPI overview](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/systems-systemapi.html) |

## Update order

| Subject | What it decides | Source |
|---|---|---|
| `InitializationSystemGroup` | Runs first each frame — setup that later groups depend on | [Update order](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/systems-update-order.html) |
| `SimulationSystemGroup` | Gameplay simulation; where most feature systems belong | [Update order](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/systems-update-order.html) |
| `PresentationSystemGroup` | Runs last, before rendering; anything reading simulation results for display | [Update order](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/systems-update-order.html) |
| `[UpdateBefore]` / `[UpdateAfter]` | Order *within* one group only — they cannot order across groups, and a cross-group expectation written this way silently does nothing | [Update order](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/systems-update-order.html) |
| `[OrderFirst]` / `[OrderLast]` | Pins a system to the edge of its group, ahead of the `UpdateBefore`/`UpdateAfter` sort | [Update order](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/systems-update-order.html) |
| Custom `ComponentSystemGroup` | Groups related systems under one ordering unit and one update rate — worth it only when several systems share both | [Update order](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/systems-update-order.html) |

## The hand-off point

| Situation | Owner | Source |
|---|---|---|
| Deciding a system schedules an `IJobEntity` rather than iterating on the main thread | This skill — see [queries-and-iteration.md](queries-and-iteration.md) | synthesized |
| Chaining that job's `JobHandle`, choosing where `.Complete()` lands, disposing its containers | `unity-job-system-and-burst` | [Scheduling jobs in Entities](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/systems-scheduling-jobs.html) |
| Making the system itself Burst-compile and verifying it did | `unity-burst-compiler` | synthesized |

**Critical caveat**: `state.Dependency` is the system's job handle, and a
system that schedules a job without assigning it back leaves the next system
free to read the same data concurrently. Assigning it is the ECS-side half of
the contract; everything else about that handle is the Job System skill's.

# Job Dependencies & Parallel Batching

Sources: [Job dependencies](https://docs.unity3d.com/6000.5/Documentation/Manual/job-system-job-dependencies.html), [Parallel jobs](https://docs.unity3d.com/6000.1/Documentation/Manual/job-system-parallel-for-jobs.html).
Covers: SKILL.md §4 — **"Chain every ordering relationship through an explicit `JobHandle`"**, **"Size the parallel batch against per-element cost"**.

How ordering between jobs is expressed, and how a parallel workload is split.
Both are correctness concerns before they are performance ones: an unexpressed
dependency is a race, and a batch size is what decides whether workers stay fed.

## Dependencies

| Subject | What it decides | Source |
|---|---|---|
| Passing a `JobHandle` into `Schedule` | The only sanctioned ordering between two jobs — the consumer cannot start before the producer finishes | [Job dependencies](https://docs.unity3d.com/6000.5/Documentation/Manual/job-system-job-dependencies.html) |
| `JobHandle.CombineDependencies` | Merges several handles into one, because a schedule call accepts a single dependency | [CombineDependencies](https://docs.unity3d.com/ScriptReference/Unity.Jobs.JobHandle.CombineDependencies.html) |
| Two jobs scheduled with no dependency | Free to run concurrently — if they touch the same container that is a race, whatever the call order in the source suggests | [Job dependencies](https://docs.unity3d.com/6000.5/Documentation/Manual/job-system-job-dependencies.html) |
| Over-chaining | A dependency added "to be safe" between genuinely independent jobs serializes them and removes the parallelism being bought | [Job dependencies](https://docs.unity3d.com/6000.5/Documentation/Manual/job-system-job-dependencies.html) |

## Parallel batching

| Subject | What it decides | Source |
|---|---|---|
| Batch (inner loop) count | Elements handed to a worker per grab — roughly 32–128 for cheap arithmetic, down towards 1 as per-element cost rises | [Parallel jobs](https://docs.unity3d.com/6000.1/Documentation/Manual/job-system-parallel-for-jobs.html) |
| Batch too small | Scheduling and stealing overhead dominates the actual work | [Parallel jobs](https://docs.unity3d.com/6000.1/Documentation/Manual/job-system-parallel-for-jobs.html) |
| Batch too large | Uneven element costs strand workers idle while one long batch finishes | [Parallel jobs](https://docs.unity3d.com/6000.1/Documentation/Manual/job-system-parallel-for-jobs.html) |
| Work stealing | Idle workers take queued batches, so smaller batches are what makes recovery from uneven cost possible | [Parallel jobs](https://docs.unity3d.com/6000.1/Documentation/Manual/job-system-parallel-for-jobs.html) |

**Critical caveat**: parallel index order is unspecified. Any result built by
accumulating across indices is run-dependent even when it is race-free — write
per-index outputs and reduce them serially when the value has to be
reproducible.

# Job Dependencies and Parallel Batching

Sources: [d] `6000.5/Documentation/Manual/job-system-job-dependencies.html`, [p] `6000.1/Documentation/Manual/job-system-parallel-for-jobs.html`, [h] `ScriptReference/Unity.Jobs.JobHandle.CombineDependencies.html`, under `https://docs.unity3d.com/`.

## Dependencies

| Subject | Fact that decides |
|---|---|
| `JobHandle` passed into `Schedule` | The only sanctioned ordering: the consumer cannot start before the producer finishes [d] |
| `JobHandle.CombineDependencies` | Merges several handles, since a schedule call takes one dependency [h] |
| Two jobs, no dependency | Free to run concurrently; on the same container that is a race whatever the call order in source [d] |
| Over-chaining | A "to be safe" dependency between independent jobs serializes them and removes the parallelism [d] |

## Batching [p]

| Subject | Fact that decides |
|---|---|
| Batch (inner loop) count | Elements per grab: about 32-128 for cheap arithmetic, down towards 1 as per-element cost rises |
| Too small | Scheduling and stealing overhead dominates |
| Too large | Uneven element costs strand idle workers behind one long batch |
| Work stealing | Smaller batches are what let idle workers recover from uneven cost |

**Caveat:** parallel index order is unspecified. A result built by accumulating across indices is run-dependent even when race-free; write per-index outputs and reduce serially when the value must be reproducible.

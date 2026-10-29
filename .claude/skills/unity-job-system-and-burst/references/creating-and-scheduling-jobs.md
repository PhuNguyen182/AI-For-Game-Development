# Creating and Scheduling Jobs

Sources: [c] `Manual/job-system-creating-jobs.html`, [h] `ScriptReference/Unity.Jobs.JobHandle.html`, under `https://docs.unity3d.com/`.

| Member | Fact that decides |
|---|---|
| `Schedule()` | Queues the job and returns its `JobHandle`; the struct is copied, so the worker never sees later changes to the original [c] |
| `JobHandle.ScheduleBatchedJobs()` | Flushes queued jobs to workers; without it work may not start until something completes or the frame ends, erasing an early schedule [h] |
| `Complete()` | Blocks until done, returns container ownership to the main thread, clears safety state; the only sanctioned way to read results back [h] |
| `IsCompleted` | Progress only: no ownership return, no safety clear, so reading a container after it alone is unsafe [h] |
| `CompleteAll(...)` | Completes several handles at once, for a frame boundary that must drain everything [h] |

## Reading results back [c]

| Situation | Outcome |
|---|---|
| Job writes a plain field on its struct | Lost: the worker mutated a copy (the usual "job did nothing" report) |
| Job writes a `NativeArray<T>` field | Survives: the container is a handle to shared native memory |
| Single scalar result | Still needs a container: one-element `NativeArray<T>` or `NativeReference<T>` |

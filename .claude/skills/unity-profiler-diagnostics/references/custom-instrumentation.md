# Custom Instrumentation

Docs: https://docs.unity3d.com/Manual/profiler-adding-information-code-intro.html · ScriptReference `Unity.Profiling.ProfilerMarker`, `Unity.Profiling.ProfilerRecorder`, `Profiling.CustomSampler`, `Profiling.Profiler`.

Code style follows `csharp-standards`.

| Member | Use |
|---|---|
| `ProfilerMarker` | Pre-created handle; `Begin`/`End` with no per-call string work. Default for new code; the only one Burst- and job-compatible |
| `ProfilerMarker.Auto()` | Disposable scope; use when the block can return early or throw |
| `ProfilerRecorder` | Reads a marker's or counter's value at runtime (Editor and player): in-game overlay or automated check |
| `CustomSampler` | Pre-created handle for legacy `Profiler.BeginSample` code that cannot move yet |
| `Profiler.BeginSample` | Passes its label string every call; never for new code |
| `Profiler.enabled`, `Profiler.logFile` | Capture to disk from a standalone build with no Editor: soak test, QA run |

```csharp
private static readonly ProfilerMarker SpawnMarker = new("WaveSpawner.SpawnWave");
private ProfilerRecorder _mainThread;

private void OnEnable()  => this._mainThread = ProfilerRecorder.StartNew(ProfilerCategory.Internal, "Main Thread", 15);
private void OnDisable() => this._mainThread.Dispose();

public void SpawnWave(int count)
{
    using (SpawnMarker.Auto()) { /* spawn loop */ }
}
```

| Subject | Rule |
|---|---|
| Stripping | Marker calls compile out of non-development builds; no `#if` needed. A block showing nothing is usually a non-development build, not a free block |
| Marker lifetime | One `static readonly` field; constructing per call reintroduces the string cost |
| Recorder disposal | Pair `StartNew` with `Dispose` on the same lifecycle boundary |
| Recorder capacity | `StartNew`'s sample count is a ring buffer; too small silently discards older samples, so an averaged overlay reads a shorter window |

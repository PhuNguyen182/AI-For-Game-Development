# Custom Instrumentation — ProfilerMarker, ProfilerRecorder, counters

Sources: [Adding profiling information to your code](https://docs.unity3d.com/Manual/profiler-adding-information-code-intro.html), [ProfilerMarker](https://docs.unity3d.com/ScriptReference/Unity.Profiling.ProfilerMarker.html), [ProfilerRecorder](https://docs.unity3d.com/ScriptReference/Unity.Profiling.ProfilerRecorder.html), [Profiler.BeginSample](https://docs.unity3d.com/ScriptReference/Profiling.Profiler.BeginSample.html), [CustomSampler](https://docs.unity3d.com/ScriptReference/Profiling.CustomSampler.html), [Profiler](https://docs.unity3d.com/ScriptReference/Profiling.Profiler.html).
Covers: SKILL.md §4 — **"Instrument an opaque system with a `static readonly ProfilerMarker`"**.

Making a cost visible that the default hierarchy does not name — work inside a
third-party plugin, one call among many identical ones, or a block whose cost
must be readable inside the running game. Where the instrumented code should
live and how it is written follows `coding-principles.md`.

## API choice

| Member | Effect | Use when | Source |
|---|---|---|---|
| `ProfilerMarker` | A pre-created handle; `Begin`/`End` push and pop a named sample with no per-call string work | Any new instrumentation — this is the current recommended API and the only one that is Burst- and job-compatible | [ProfilerMarker](https://docs.unity3d.com/ScriptReference/Unity.Profiling.ProfilerMarker.html) |
| `ProfilerMarker.Auto()` | Returns a disposable scope that ends the sample on exit | The instrumented block can return early or throw, where a manual `End` would be skipped | [ProfilerMarker](https://docs.unity3d.com/ScriptReference/Unity.Profiling.ProfilerMarker.html) |
| `ProfilerRecorder` | Reads a marker's or counter's accumulated value back at runtime, in Editor and player alike | An in-game overlay or an automated check needs the number, not a human looking at the window | [ProfilerRecorder](https://docs.unity3d.com/ScriptReference/Unity.Profiling.ProfilerRecorder.html) |
| `CustomSampler` | A pre-created sampler handle for the legacy API | Maintaining existing `Profiler.BeginSample` code that cannot move to `ProfilerMarker` yet | [CustomSampler](https://docs.unity3d.com/ScriptReference/Profiling.CustomSampler.html) |
| `Profiler.BeginSample` | Takes its label as a string on every call | Never for new code — the string is passed per call, which is exactly the per-frame cost the instrumentation is meant to expose | [Profiler.BeginSample](https://docs.unity3d.com/ScriptReference/Profiling.Profiler.BeginSample.html) |
| `Profiler.enabled`, `Profiler.logFile` | Toggles collection and writes a capture to disk from a standalone build | Capturing on a device with no Editor attached — a soak test, or a QA run | [Profiler](https://docs.unity3d.com/ScriptReference/Profiling.Profiler.html) |

```csharp
using Unity.Profiling;
using UnityEngine;

public class WaveSpawner : MonoBehaviour
{
    private static readonly ProfilerMarker SpawnMarker = new("WaveSpawner.SpawnWave");

    private ProfilerRecorder _mainThreadRecorder;

    private void OnEnable()
    {
        this._mainThreadRecorder = ProfilerRecorder.StartNew(ProfilerCategory.Internal, "Main Thread", 15);
    }

    private void OnDisable()
    {
        this._mainThreadRecorder.Dispose();
    }

    public void SpawnWave(int count)
    {
        using (SpawnMarker.Auto())
        {
            for (int i = 0; i < count; i++)
            {
                this.SpawnOne();
            }
        }
    }
}
```

## Build behaviour

| Subject | What it decides | Source |
|---|---|---|
| Stripping | Marker begin and end calls compile out of non-development builds, so instrumentation can be left in shipping code without an `#if` wrapper around every call site | [ProfilerMarker](https://docs.unity3d.com/ScriptReference/Unity.Profiling.ProfilerMarker.html) |
| Marker lifetime | Create the marker once as a `static readonly` field — constructing one per call reintroduces the per-call string cost the API exists to avoid | [ProfilerMarker](https://docs.unity3d.com/ScriptReference/Unity.Profiling.ProfilerMarker.html) |
| Recorder disposal | `ProfilerRecorder` is `IDisposable` and keeps collecting until disposed; pair `StartNew` with `Dispose` on the same lifecycle boundary | [ProfilerRecorder](https://docs.unity3d.com/ScriptReference/Unity.Profiling.ProfilerRecorder.html) |
| Recorder capacity | The sample count passed to `StartNew` is a ring buffer — sized too small it silently discards older samples, so an averaged overlay reads a shorter window than intended | [ProfilerRecorder](https://docs.unity3d.com/ScriptReference/Unity.Profiling.ProfilerRecorder.html) |

**Critical caveat**: a marker only appears in Editor captures and development
builds. An instrumented block that shows nothing in the window is usually a
non-development build, not a block that costs nothing.

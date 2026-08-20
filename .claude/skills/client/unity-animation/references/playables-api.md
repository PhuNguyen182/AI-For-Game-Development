# Playables API

Sources: `https://docs.unity3d.com/Manual/Playables.html`, and sub-pages (see [root-links.md](root-links.md)).

## What problem it solves

The Playables API is "a set of classes, structs, and methods that you use to create the `PlayableGraph`, its nodes, and outputs." It sits below/alongside the Animator Controller state-machine system (see [animator-controller.md](animator-controller.md)) and complements Mecanim rather than replacing it. Use it when you need:

- Dynamic, runtime-procedural animation blending that isn't expressible as a static Animator Controller state machine.
- Playing animation clips directly, with no Animator Controller asset at all.
- Dynamically creating and adjusting blend graphs and blend weights at runtime, rather than a graph laid out once ahead of time.
- Adding/removing playable nodes at runtime instead of using a fixed, pre-authored graph.

It is also "primarily used by the Unity Timeline package" — `PlayableDirector` builds and drives a `PlayableGraph` from a `PlayableAsset` (a Timeline asset). Timeline itself is a separate system built on top of Playables; this reference does not cover Timeline authoring (see the negative trigger in [SKILL.md](../SKILL.md)).

**Guidance for this project**: default to Animator Controller + `Animator` for ordinary gameplay animation (state machines, transitions, blend trees — see [animator-controller.md](animator-controller.md)). Reach for the Playables API only when there is a specific need for programmatic graph control (procedural blending logic, runtime-composed mixing graphs, custom per-frame animation math) that the state machine genuinely cannot express — this is the escape-hatch case referenced by KISS/YAGNI in `coding-principles.md`, not a routine default.

## Core object model

| Type | Role |
|---|---|
| `PlayableGraph` | Owns and manages the whole graph: playable nodes + outputs, with time-based synchronization across data sources. Created via `PlayableGraph.Create()`. |
| `Playable` | Base struct type for all graph nodes. Playables are **C# structs implementing `IPlayable`**, deliberately struct-based to minimize GC overhead. Most interaction happens through the `PlayableExtensions` static-method set. A non-abstract playable type exposes a static `Create(PlayableGraph, ...)` factory. Cast a generic `Playable` handle to its concrete type (e.g. `AnimationClipPlayable`) to access type-specific members. |
| `PlayableOutput` | Base struct type for all graph outputs, implementing `IPlayableOutput`; interacted with via `PlayableOutputExtensions`. An output produces nothing until it is linked to a playable with `PlayableOutput.SetSourcePlayable()`. Non-abstract output types expose a static `Create(...)` factory. |
| `AnimationPlayableOutput` | Concrete `PlayableOutput` that routes a playable's animation result into an `Animator` component. Created with `AnimationPlayableOutput.Create(graph, name, animatorComponent)`. |
| `AnimationClipPlayable` | Wraps a single `AnimationClip` as a playable node. `AnimationClipPlayable.Create(graph, clip)`. |
| `AnimationMixerPlayable` | Weighted blend of N animation-playable inputs. `AnimationMixerPlayable.Create(graph, inputCount)`; set/get per-input blend weight with `SetInputWeight(index, weight)` / `GetInputWeight(index)` (both live on `PlayableExtensions`). Weights are not auto-normalized by the mixer itself. |
| `AnimationLayerMixerPlayable` | Layered blending of N animation-playable inputs, each optionally restricted by an `AvatarMask` and set to additive or override mode — the Playables-API equivalent of Animator Controller layers. Per-input, add `SetLayerMaskFromAvatarMask(index, avatarMask)` / `SetLayerAdditive(index, bool)`. |
| `AnimatorControllerPlayable` | Wraps an existing `RuntimeAnimatorController` as a playable node, so a full state-machine-driven controller can be mixed into a larger custom graph. `AnimatorControllerPlayable.Create(graph, controller)`. |
| `ScriptPlayable<T>` / `PlayableBehaviour` | The custom-playable mechanism: derive a class from `PlayableBehaviour` to write fully custom per-frame logic, then wrap an instance in `ScriptPlayable<T>`. |
| `AudioClipPlayable` / `AudioPlayableOutput` | The audio-side equivalents of `AnimationClipPlayable` / `AnimationPlayableOutput` — a single `PlayableGraph` can drive multiple output types simultaneously (e.g. one animation output + one audio output). |
| `PlayableDirector` | Component that "controls the playback and timing of a `PlayableGraph`," built from a `PlayableAsset`; the component Timeline uses to store the link between a Timeline instance and asset, its track/binding list, and playback state. Not required for hand-written Playables graphs — those are typically built and destroyed from a plain `MonoBehaviour`. |

Manual API note: the Manual documents "`AnimationScriptPlayable`" conceptually via the generic `ScriptPlayable<T>` + `PlayableBehaviour` pattern; it does not have a separate dedicated Manual sub-page distinct from that pattern.

## Custom playables — `PlayableBehaviour`

Write custom per-frame graph logic by subclassing `PlayableBehaviour`:

```csharp
public class MyCustomPlayableBehaviour : PlayableBehaviour
{
    // Override PlayableBehaviour virtual methods (e.g. PrepareFrame) here.
}
```

Wrap it as a graph node with `ScriptPlayable<T>`:

```csharp
// No pre-existing instance:
ScriptPlayable<MyCustomPlayableBehaviour> playable =
    ScriptPlayable<MyCustomPlayableBehaviour>.Create(playableGraph);

// With a pre-configured instance (the instance is cloned into the graph):
MyCustomPlayableBehaviour myBehaviour = new();
ScriptPlayable<MyCustomPlayableBehaviour> playable =
    ScriptPlayable<MyCustomPlayableBehaviour>.Create(playableGraph, myBehaviour);
```

Retrieve the live behaviour instance from a playable with `scriptPlayable.GetBehaviour()`.

The documented example ("create a custom playable") builds a `PlayQueuePlayable : PlayableBehaviour` that cycles through animation clips sequentially:
- `Initialize()` (custom method, not an override) — sets up an internal `AnimationMixerPlayable` and connects each clip's `AnimationClipPlayable` as an input, using `SetInputCount()` / `GetInputCount()`.
- `PrepareFrame()` (overridden `PlayableBehaviour` method) — each frame, advances the current clip's playback and adjusts input weights via `SetInputWeight()` so only one clip plays audibly/visibly at a time; when a clip finishes (checked against `clipPlayable.GetAnimationClip().length`), it resets timing with `SetTime()` and switches to the next clip.
- The owning `MonoBehaviour`'s `Start()` creates the `PlayableGraph`, instantiates the custom playable, and connects it to an `AnimationPlayableOutput`; `OnDisable()` calls `graph.Destroy()`.

## Graph lifecycle and connecting to an `Animator`

A `PlayableGraph` is **not garbage-collected** — it must be explicitly destroyed with `PlayableGraph.Destroy()`, which also destroys every playable and output it owns. The canonical pattern, used consistently across every Manual example:

```csharp
[RequireComponent(typeof(Animator))]
public class PlayAnimationClip : MonoBehaviour
{
    [SerializeField] private AnimationClip clip;
    private PlayableGraph _graph;

    private void Start()
    {
        this._graph = PlayableGraph.Create();
        this._graph.SetTimeUpdateMode(DirectorUpdateMode.GameTime);

        AnimationPlayableOutput output = AnimationPlayableOutput.Create(
            this._graph, "Animation", this.GetComponent<Animator>());

        AnimationClipPlayable clipPlayable = AnimationClipPlayable.Create(this._graph, this.clip);
        output.SetSourcePlayable(clipPlayable);

        this._graph.Play();
    }

    private void OnDisable()
    {
        this._graph.Destroy();
    }
}
```

`AnimationPlayableUtilities` provides convenience one-liners equivalent to the above boilerplate — `AnimationPlayableUtilities.Play(animator, playable, graph)` and `AnimationPlayableUtilities.PlayClip(animator, clip, out graph)` — for the common case of "just play this one clip/playable on this Animator" without hand-building output/connect calls.

Other graph-level controls used across the examples:
- `graph.Connect(sourcePlayable, sourceOutputPort, destinationPlayable, destinationInputPort)` — wires one playable's output into another playable's input port.
- `playable.Pause()` / `playable.Play()` — pausing a parent propagates only in the play→pause direction shown; setting a paused parent back to play also resumes its children. A paused node holds its last-evaluated output value.
- `playable.SetTime(time)` — manually scrub/seek a playable (typically combined with `Pause()` for frame-accurate manual control, e.g. scrubbing via a UI slider).
- `graph.Evaluate()` — force a manual graph evaluation outside the normal update.
- `graph.SetTimeUpdateMode(DirectorUpdateMode.GameTime)` — controls what clock drives graph time advancement.

## Multiple output types on one graph

A single `PlayableGraph` isn't limited to one output — a graph can wire both `AnimationPlayableOutput` and `AudioPlayableOutput` off the same graph, each fed by its own playable (`AnimationClipPlayable`, `AudioClipPlayable`) and each requiring its own `SetSourcePlayable()` call.

## Debugging: PlayableGraph Visualizer

The **PlayableGraph Visualizer** package renders a live graph of a running `PlayableGraph` — colored nodes per playable, wire-color intensity indicating blend weight — in both Play mode and, for Mecanim/Playables-consuming packages, Edit mode. Install from `https://github.com/UnityTech/graph-visualizer` as a local UPM package, then open via **Window > Analysis > PlayableGraph Visualizer**, enter Play mode, and select the target graph instance. Unity's own docs flag it as **"a discontinued experimental package that might not work with your version of Unity"** — treat it as best-effort tooling, not a guaranteed-supported dependency.

## Practical guidance

- Always pair `PlayableGraph.Create()` with a matching `graph.Destroy()` in `OnDisable()` (or equivalent teardown) — an un-destroyed graph is a guaranteed leak for the process lifetime, exactly the kind of "unbounded growth without a defined release point" `performance-and-algorithms.md` flags under Memory discipline.
- `Playable`/`PlayableOutput` are structs, so building/wiring a graph itself doesn't allocate the way a class-based system would — but the graph is still an unmanaged native resource requiring explicit lifecycle management, unlike a normal managed object.
- `SetInputWeight` on `AnimationMixerPlayable`/`AnimationLayerMixerPlayable` is not self-normalizing; if driving weights procedurally in `Update()`, clamp/normalize explicitly (`Mathf.Clamp01`) rather than assuming the mixer enforces it.
- Because a custom `PlayableBehaviour.PrepareFrame()`/`ProcessFrame()` runs every graph evaluation (effectively every frame while playing), treat it as hot-path code: no per-call allocations, no LINQ, no string-based lookups — same discipline as `Update()` per `coding-principles.md`/`performance-and-algorithms.md`.
- Prefer `AnimatorControllerPlayable` to fold an existing, designer-authored Animator Controller into a larger custom graph rather than reimplementing state-machine logic as hand-written playables — keeps state-machine authoring in the Animator window where it belongs.
- Reserve the Playables API for the specific procedural-blending/custom-mixing cases it's meant for; routine character animation should stay on Animator Controller + `Animator` per the YAGNI principle in `coding-principles.md` — don't introduce a hand-built `PlayableGraph` where a state machine and blend tree already solve the problem.

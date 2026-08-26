# Playables API — graphs, mixers, custom behaviours, lifetime

Sources: [Playables API](https://docs.unity3d.com/Manual/Playables.html), [Playables graph](https://docs.unity3d.com/Manual/Playables-Graph.html), [ScriptPlayable and PlayableBehaviour](https://docs.unity3d.com/Manual/Playables-ScriptPlayable.html), [Playables examples](https://docs.unity3d.com/Manual/Playables-Examples.html), [Blend two animation clips](https://docs.unity3d.com/Manual/playables-ex-blend-clips.html), [Blend a clip with a controller](https://docs.unity3d.com/Manual/playables-ex-blend-clip-controller.html), [PlayableGraph Visualizer](https://docs.unity3d.com/Manual/playables-visualizer.html).
Covers: SKILL.md §4 — **"Reach for the Playables API only when the state machine cannot express the need"**.

The layer the Animator itself runs on, exposed for graphs composed at
runtime. Timeline is built on this too, but its track and clip authoring is a
separate system no skill in this project owns — see [root-links.md](root-links.md).

## When the state machine is not enough

| Case | Why the graph is needed | Source |
|---|---|---|
| Clip set unknown until runtime | An authored state machine has to name its clips; a graph can mix a set assembled from data | [Playables API](https://docs.unity3d.com/Manual/Playables.html) |
| Weights computed per frame | A Blend Tree maps parameters to weights through authored thresholds; a graph sets weights directly from arbitrary maths | [Blend two animation clips](https://docs.unity3d.com/Manual/playables-ex-blend-clips.html) |
| Blending a clip against an existing controller | Layering a one-off animation over a running state machine without adding a state or a layer for it | [Blend a clip with a controller](https://docs.unity3d.com/Manual/playables-ex-blend-clip-controller.html) |
| Anything a state and a transition already express | Not a case — the graph costs code, lifetime management and debuggability that the authored asset does not, per YAGNI in `coding-principles.md` | [Playables API](https://docs.unity3d.com/Manual/Playables.html) |

## Graph structure

| Type | Role | Source |
|---|---|---|
| Graph | Owns the nodes and drives evaluation; created explicitly and destroyed explicitly | [Playables graph](https://docs.unity3d.com/Manual/Playables-Graph.html) |
| Output | Connects the graph to what it drives — an `Animator` for animation | [Playables graph](https://docs.unity3d.com/Manual/Playables-Graph.html) |
| Clip playable | A single clip as a node, with its own time and speed | [Play an animation clip](https://docs.unity3d.com/Manual/playables-ex-play-clip.html) |
| Mixer playable | Blends its inputs by per-input weight, which is where a runtime-computed blend actually happens | [Blend two animation clips](https://docs.unity3d.com/Manual/playables-ex-blend-clips.html) |
| Layer mixer playable | Blends inputs as layers, with optional masking, mirroring what layers do in a controller | [Playables graph](https://docs.unity3d.com/Manual/Playables-Graph.html) |
| Controller playable | Wraps an existing Animator Controller as a node, so a graph can blend against the authored state machine rather than replacing it | [Blend a clip with a controller](https://docs.unity3d.com/Manual/playables-ex-blend-clip-controller.html) |
| Script playable and behaviour | A custom node with per-frame callbacks, for logic the built-in nodes do not express | [ScriptPlayable and PlayableBehaviour](https://docs.unity3d.com/Manual/Playables-ScriptPlayable.html) |

**Critical caveat**: a graph is not garbage collected. Every created graph
needs an explicit destroy on a defined lifecycle boundary, or it survives the
object that made it for the rest of the session — the same discipline
`performance-and-algorithms.md` requires of any unmanaged lifetime.

## Working with a graph

| Subject | What it decides | Source |
|---|---|---|
| Play and stop on the graph | Whether the graph evaluates at all; a correctly built graph that was never played produces no motion and no error | [Control the play state](https://docs.unity3d.com/Manual/playables-ex-play-state.html) |
| Node time and speed | Set per node, so one input can be scrubbed or slowed without touching the rest of the graph | [Control the timing of a playable](https://docs.unity3d.com/Manual/playables-ex-control-timing.html) |
| Several outputs | One graph can drive more than one kind of output, which is how animation and audio stay on one clock | [PlayableGraph with different outputs](https://docs.unity3d.com/Manual/playables-ex-different-outputs.html) |
| Visualizer | A separate package that draws the live graph, which turns an invisible wiring mistake into something you can see | [PlayableGraph Visualizer](https://docs.unity3d.com/Manual/playables-visualizer.html) |

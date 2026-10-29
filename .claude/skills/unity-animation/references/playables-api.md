# Playables API

Pages: `Playables`, `Playables-Graph`, `Playables-ScriptPlayable`, `playables-ex-blend-clips`, `playables-ex-blend-clip-controller`, `playables-visualizer`. Timeline sits on this but is out of scope.

Use a graph for: a clip set unknown until runtime; weights computed per frame from arbitrary maths; layering a one-off clip over a running controller without adding a state/layer. Anything a state and transition already express is not a case (YAGNI, `csharp-standards` → `coding-principles.md`).

| Type | Role |
|---|---|
| `PlayableGraph` | Owns nodes, drives evaluation; created and destroyed explicitly |
| Output (`AnimationPlayableOutput`) | Connects to the `Animator` |
| Clip playable | One clip with own time and speed |
| Mixer playable | Blends inputs by per-input weight |
| Layer mixer playable | Layers with optional masking |
| Controller playable | Wraps an Animator Controller so a graph blends against it |
| `ScriptPlayable` / `PlayableBehaviour` | Custom node with per-frame callbacks |

- A graph is **not garbage collected**: destroy every created graph at a defined lifecycle boundary (e.g. `OnDestroy`), or it outlives its owner for the session.
- A built graph that was never played produces no motion and no error.
- Time and speed are set per node. One graph can drive several output kinds (animation and audio on one clock).
- PlayableGraph Visualizer package draws the live graph to find wiring mistakes.

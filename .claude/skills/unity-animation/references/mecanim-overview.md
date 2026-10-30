# Mecanim Overview

Pages: `animation-mecanim`, `FBXImporter-Rig`, `AnimationsImport`, `LoopingAnimationClips`, `script-AnimationWindowEvent`, `AnimationEventsOnImportedClips`. The Avatar a Humanoid creates: [avatar-setup.md](avatar-setup.md).

## Animation Type
| Type | Buys | Costs |
|---|---|---|
| Humanoid | Clips retarget across Humanoid rigs; muscle system normalises pose | Per-frame retargeting pass; Avatar configuration |
| Generic | No retarget cost, no Avatar; default for creatures, props, vehicles, sprite swaps | Clips bound to their own rig |
| Legacy | Nothing new; pre-Mecanim component | No state machine, blend trees or retargeting — never for new work |

Changing the type after clips/controllers exist invalidates their bindings.

## Clip import settings
| Setting | Decides |
|---|---|
| Loop Time / Loop Pose | Repeat, and end-matching; the match indicator says whether the seam shows |
| Root Transform position/rotation bake | Motion stays in the pose vs becomes root motion the component applies — source of drifting and of never-moving characters |
| Clip splitting | One long take cut into named clips by frame range |
| Curves | Extra float curves readable as Animator parameters |
| Mask on imported clip | Limits what the clip writes; separate from a layer's mask |
| Euler curve resampling | Off preserves authored Euler interpolation that quaternion resampling rounds off |

## Windows
Animation window owns one clip's keys, curves and events; Animator window owns the graph. An event belongs to a clip, never a state — a state blending two clips has no single event timeline, so an event seems to fire at the wrong moment when blend weight shifts.

## Animation Events
- Handler must be on a component of the same GameObject as the `Animator`; on a child it is never found, with no report.
- At most one parameter, of a small set of supported types; two parameters is not called.
- On the last frame of a non-looping clip it is unreliable — place it slightly earlier.
- On an imported clip, add events in the import settings (the asset is read-only).
- An event signals a moment; what it means is Core's (`csharp-standards` → `coding-principles.md`).

# URP Volume System

Sources: Manual `urp/Volumes.html`, `urp/volume-component-reference.html`, `urp/volumes-troubleshooting.html`; core API 17.6 (`Volume`, `VolumeProfile`, `VolumeParameter`, `VolumeManager`).

A Volume contributes parameter values to a per-camera blend resolved every frame. Most "nothing happens" reports are a Volume excluded from the blend, not wrong values.

## Resolution
- Considered: only layers in the Camera's Volume Mask; an excluded layer is absent, with no warning.
- Contributing: Global always; Local only when the Volume Trigger transform is inside the collider or within Blend Distance.
- Combined: interpolated in Priority order (higher last), scaled by Weight and blend falloff.
- An unwritten parameter falls to the default profile, not the last value, so a local-only scene snaps to project defaults outside the regions.

## Volume properties
| Property | Decides |
|---|---|
| `isGlobal` | Global needs no collider; Local needs a Collider |
| `blendDistance` | Fade measured outward from the collider surface; 0 pops at the boundary |
| `weight` | 0-1 scale of the whole volume; the handle for runtime fades |
| `priority` | Higher wins; tie order is undocumented, so set it wherever volumes overlap |
| `colliders` | `UpdateColliders()` re-reads after runtime changes |

## Profiles
- `sharedProfile`: the asset. Writes persist to disk and every referencing scene.
- `profile`: instantiates a runtime copy on first access (leaks if used casually), like `material` vs `sharedMaterial`. `HasInstantiatedProfile()` avoids forcing one.
- `VolumeProfile.TryGet<T>()` reads safely; `Add<T>()`, `Remove<T>()`, `Has<T>()` mutate.

## Override state
The blend skips any parameter with `overrideState` false, whatever its value. `VolumeParameter<T>.Override(value)` sets value and flag together. `VolumeComponent.SetAllOverridesTo()` flips a whole component; `VolumeComponent.active` disables it independently.

## Scripted access
- `VolumeManager.instance.stack`: the resolved per-camera result; what a custom pass reads.
- `VolumeManager.Update(Transform, LayerMask)` re-resolves; `globalDefaultProfile` / `qualityDefaultProfile` are the fallbacks.
- Custom `VolumeComponent` parameters: `ClampedFloatParameter` (min/max; default for intensity), `FloatParameter`, `BoolParameter`.

## When nothing appears (check in order)
1. Camera Post Processing toggle.
2. Camera Volume Mask vs the Volume's layer.
3. A Global Volume exists (documented cause of scripted changes not taking).
4. `overrideState` on the parameter written.
5. Local volume has a Collider.

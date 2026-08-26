# The URP Volume System — Scope, Blending, and Scripted Access

Sources: [Understand Volumes](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/Volumes.html), [Volume component reference](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/volume-component-reference.html), [Troubleshooting volumes](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/volumes-troubleshooting.html), [Volume API](https://docs.unity3d.com/Packages/com.unity.render-pipelines.core@17.6/api/UnityEngine.Rendering.Volume.html).
Covers: SKILL.md §4 — **"Put the Volume on a layer inside the camera's Volume Mask"**, **"Give the scene one Global Volume as the floor every local Volume blends up from"**, **"Set `overrideState`, not just the parameter value, whenever a Volume parameter is written from code"**, **"Edit `sharedProfile` only when the change is meant to reach the asset on disk"**.

A Volume does not apply an effect. It contributes a set of parameter values to
a per-camera blend that the Volume Manager resolves every frame, and the
result of that blend is what renders. Almost every "my post-processing does
nothing" report is a Volume that was excluded from the blend rather than one
whose values were wrong — which is why scope and override state matter more
here than any individual effect property.

## Contents

- [What renders is the resolved stack](#what-renders-is-the-resolved-stack)
- [The Volume component](#the-volume-component)
- [Profiles](#profiles)
- [Override state](#override-state)
- [Scripted access](#scripted-access)
- [When nothing appears](#when-nothing-appears)

## What renders is the resolved stack

| Step | What decides it | Source |
|---|---|---|
| Which volumes are considered | The Camera's Volume Mask. A Volume on an unmasked layer is not low priority, it is absent — no warning, no console entry | [Volume component reference](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/volume-component-reference.html) |
| Which of those contribute | Global volumes always; local volumes only when the Volume Trigger transform is inside the collider or within its Blend Distance | [Understand Volumes](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/Volumes.html) |
| How they combine | Interpolated in Priority order, higher last, each scaled by its Weight and by blend-distance falloff | [Volume component reference](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/volume-component-reference.html) |
| What an unwritten parameter falls back to | The default profile, not the last value seen — which is why a scene with only local volumes snaps to project defaults outside them | [Troubleshooting volumes](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/volumes-troubleshooting.html) |

## The Volume component

| Property | What it decides | Source |
|---|---|---|
| Mode / `isGlobal` | Global applies everywhere the mask allows and needs no collider; Local requires a Collider and applies by proximity | [Volume component reference](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/volume-component-reference.html) |
| `blendDistance` | Fade distance measured **outward** from the collider surface, in world units. Zero means the effect appears the instant the boundary is crossed, which reads as a pop | [Volume component reference](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/volume-component-reference.html) |
| `weight` | Scales this volume's whole contribution, 0–1. The right handle for fading a look in and out at runtime without touching per-effect values | [Volume API](https://docs.unity3d.com/Packages/com.unity.render-pipelines.core@17.6/api/UnityEngine.Rendering.Volume.html) |
| `priority` | Resolves overlap — higher wins. Ties are not defined by scene order in any documented way, so set it deliberately wherever two volumes can overlap | [Volume component reference](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/volume-component-reference.html) |
| `colliders` | The collider list a local volume tests against; `UpdateColliders()` re-reads it after runtime changes | [Volume API](https://docs.unity3d.com/Packages/com.unity.render-pipelines.core@17.6/api/UnityEngine.Rendering.Volume.html) |

## Profiles

| Member | What it decides | Source |
|---|---|---|
| `sharedProfile` | The profile **asset**. Writing through it edits the file on disk, persists into version control, and affects every scene referencing it | [Volume API](https://docs.unity3d.com/Packages/com.unity.render-pipelines.core@17.6/api/UnityEngine.Rendering.Volume.html) |
| `profile` | Instantiates a runtime copy on first access and returns that. Correct for a per-instance variation, wrong for a scene-wide tweak, and it leaks the clone if used casually — the same distinction as `sharedMaterial` versus `material` | [Volume API](https://docs.unity3d.com/Packages/com.unity.render-pipelines.core@17.6/api/UnityEngine.Rendering.Volume.html) |
| `HasInstantiatedProfile()` | Whether a copy already exists, so a caller can avoid forcing one | [Volume API](https://docs.unity3d.com/Packages/com.unity.render-pipelines.core@17.6/api/UnityEngine.Rendering.Volume.html) |
| `VolumeProfile.TryGet<T>()` | The safe read for one override; `Add<T>()`, `Remove<T>()`, `Has<T>()` mutate the set | [VolumeProfile API](https://docs.unity3d.com/Packages/com.unity.render-pipelines.core@17.6/api/UnityEngine.Rendering.VolumeProfile.html) |

## Override state

Every parameter on a `VolumeComponent` carries an `overrideState` flag — the
small checkbox beside it in the Inspector. The blend **skips any parameter
whose flag is false**, whatever value it holds. This is the single most common
cause of a scripted post-processing change that appears to do nothing.

| Member | What it decides | Source |
|---|---|---|
| `VolumeParameter.overrideState` | Whether this parameter participates in the blend at all | [VolumeParameter API](https://docs.unity3d.com/Packages/com.unity.render-pipelines.core@17.6/api/UnityEngine.Rendering.VolumeParameter.html) |
| `VolumeParameter<T>.Override(value)` | Sets the value **and** the flag together — the reason to prefer it over assigning `.value` | [VolumeParameter&lt;T&gt; API](https://docs.unity3d.com/Packages/com.unity.render-pipelines.core@17.6/api/UnityEngine.Rendering.VolumeParameter-1.html) |
| `VolumeComponent.SetAllOverridesTo()` | Flips every flag on one component at once, for enabling or clearing a whole effect | [VolumeComponent API](https://docs.unity3d.com/Packages/com.unity.render-pipelines.core@17.6/api/UnityEngine.Rendering.VolumeComponent.html) |
| `VolumeComponent.active` | Disables the component entirely, independent of its parameters' flags | [VolumeComponent API](https://docs.unity3d.com/Packages/com.unity.render-pipelines.core@17.6/api/UnityEngine.Rendering.VolumeComponent.html) |

## Scripted access

| Member | What it decides | Source |
|---|---|---|
| `VolumeManager.instance.stack` | The resolved per-camera result — what a custom pass should read, rather than reaching into individual volumes | [VolumeManager API](https://docs.unity3d.com/Packages/com.unity.render-pipelines.core@17.6/api/UnityEngine.Rendering.VolumeManager.html) |
| `VolumeManager.Update(Transform, LayerMask)` | Re-resolves the stack for a given trigger and mask | [VolumeManager API](https://docs.unity3d.com/Packages/com.unity.render-pipelines.core@17.6/api/UnityEngine.Rendering.VolumeManager.html) |
| `globalDefaultProfile` / `qualityDefaultProfile` | The fallbacks an unoverridden parameter resolves to — the project-level floor a scene with no Global Volume lands on | [VolumeManager API](https://docs.unity3d.com/Packages/com.unity.render-pipelines.core@17.6/api/UnityEngine.Rendering.VolumeManager.html) |
| `ClampedFloatParameter`, `FloatParameter`, `BoolParameter` | The parameter types a custom `VolumeComponent` declares; the clamped form carries `min`/`max` and is the default choice for an intensity | [core RP API](https://docs.unity3d.com/Packages/com.unity.render-pipelines.core@17.6/api/UnityEngine.Rendering.ClampedFloatParameter.html) |

## When nothing appears

Check in this order — the cheap gates first, since they account for most cases.

| Check | Why it comes first | Source |
|---|---|---|
| Camera Post Processing toggle | Gates the entire stack for that camera regardless of every setting below | [Add post-processing in URP](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/add-post-processing.html) |
| Camera Volume Mask versus the Volume's layer | An excluded layer removes the volume from the blend silently | [Volume component reference](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/volume-component-reference.html) |
| A Global Volume exists in the scene | Its absence is the documented cause of scripted Volume changes not taking effect | [Troubleshooting volumes](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/volumes-troubleshooting.html) |
| `overrideState` on the parameter written | A false flag makes a correct value invisible to the blend | [VolumeParameter API](https://docs.unity3d.com/Packages/com.unity.render-pipelines.core@17.6/api/UnityEngine.Rendering.VolumeParameter.html) |
| Local volume has a Collider | Local mode tests against colliders; without one there is no region to be inside | [Understand Volumes](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/Volumes.html) |

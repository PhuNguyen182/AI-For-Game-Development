# URP Volumes System

Covers the URP Volume system — the mechanism through which post-processing effects (and other URP overrides) are configured in a scene, via Volume components, Volume Profiles, and Volume Overrides, with global/local scope, priority, weight, and blend-distance-based blending resolved each frame by the Volume Manager.

## Manual
- [Volumes in URP](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/volumes-landing-page.html)
- [Understand Volumes](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/Volumes.html)
- [Set up a Volume](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/set-up-a-volume.html)
- [Create a Volume Profile](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/Volume-Profile.html)
- [Configure Volume Overrides](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/VolumeOverrides.html)
- [Volume component reference](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/volume-component-reference.html) — covers Mode (Global/Local), Blend Distance, Weight, Priority, Volume Profile.
- [Troubleshooting volumes](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/volumes-troubleshooting.html)

## Scripting API
- [Rendering.Volume](https://docs.unity3d.com/Packages/com.unity.render-pipelines.core@17.5/api/UnityEngine.Rendering.Volume.html) — key members: `isGlobal`, `priority`, `weight`, `blendDistance`, `sharedProfile`, `profile`, `colliders`, `HasInstantiatedProfile()`, `UpdateColliders()`.
- [Rendering.VolumeProfile](https://docs.unity3d.com/Packages/com.unity.render-pipelines.core@17.5/api/UnityEngine.Rendering.VolumeProfile.html) — key members: `components`, `isDirty`, `Add<T>()`, `Remove<T>()`, `Has<T>()`, `TryGet<T>()`, `TryGetSubclassOf<T>()`, `GetStateHash()`.
- [Rendering.VolumeComponent](https://docs.unity3d.com/Packages/com.unity.render-pipelines.core@17.5/api/UnityEngine.Rendering.VolumeComponent.html) — key members: `active`, `parameters`, `displayName`, `Override()`, `SetAllOverridesTo()`, `AnyPropertiesIsOverridden()`, `GetStateHash()`.
- [Rendering.VolumeManager](https://docs.unity3d.com/Packages/com.unity.render-pipelines.core@17.5/api/UnityEngine.Rendering.VolumeManager.html) — key members: `instance`, `stack`, `globalDefaultProfile`, `qualityDefaultProfile`, `Update(Transform, LayerMask)`, `GetVolumes(LayerMask)`, `OnVolumeProfileChanged()`, `Register()`/`Unregister()`.
- [Rendering.VolumeParameter](https://docs.unity3d.com/Packages/com.unity.render-pipelines.core@17.5/api/UnityEngine.Rendering.VolumeParameter.html) — non-generic base class; key members: `overrideState`, `GetValue<T>()`, `SetValue()`, `Clone()`.
- [Rendering.VolumeParameter&lt;T&gt;](https://docs.unity3d.com/Packages/com.unity.render-pipelines.core@17.5/api/UnityEngine.Rendering.VolumeParameter-1.html) — generic base for parameter types; key members: `value`, `overrideState`, `Interp()`, `Override()`, `Clone()`.
- [Rendering.FloatParameter](https://docs.unity3d.com/Packages/com.unity.render-pipelines.core@17.5/api/UnityEngine.Rendering.FloatParameter.html) — `VolumeParameter<float>` with linear `Interp()`.
- [Rendering.ClampedFloatParameter](https://docs.unity3d.com/Packages/com.unity.render-pipelines.core@17.5/api/UnityEngine.Rendering.ClampedFloatParameter.html) — extends `FloatParameter`; adds `min`/`max` clamping fields.
- [Rendering.BoolParameter](https://docs.unity3d.com/Packages/com.unity.render-pipelines.core@17.5/api/UnityEngine.Rendering.BoolParameter.html) — `VolumeParameter<bool>` with an optional display-type constructor for editor UI.

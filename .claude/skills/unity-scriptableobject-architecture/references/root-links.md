# Root Links — Unity ScriptableObject Architecture

Source: the root index pages listed below, as provided for this skill.
Covers: the whole skill — provenance and version anchor for every file in
this folder.

Anchors every link in this folder to Unity's core-engine Manual and Scripting
API, which publish unversioned and always resolve to the current
documentation — there is no version segment to keep. The pattern shapes
themselves (Data Container, Variable, Delegate Object, Observer Event, Event
Channel, Extendable Enum, Command, Runtime Set, Dual Serialization) are a
widely-adopted community architecture built on top of these APIs, popularized
by Ryan Hipple's "Game Architecture with Scriptable Objects" (Unite Austin
2017) and its many derivatives across Unity sample projects; each reference
file states this synthesis explicitly alongside its concrete API sources.

| Root | Holds | Source |
|---|---|---|
| Manual — ScriptableObject | Concept, lifecycle, `CreateAssetMenu` workflow | [ScriptableObject](https://docs.unity3d.com/Manual/class-ScriptableObject.html) |
| Manual — Script Serialization | What Unity's serializer can and cannot persist on an SO field | [Script Serialization](https://docs.unity3d.com/Manual/script-Serialization.html) |
| Manual — Domain Reloading | Why a Play-mode SO field mutation can survive past Stop | [Domain Reloading](https://docs.unity3d.com/Manual/DomainReloading.html) |
| Scripting API — ScriptableObject | `CreateInstance`, `hideFlags`, asset lifecycle members | [ScriptableObject](https://docs.unity3d.com/ScriptReference/ScriptableObject.html) |
| Scripting API — CreateAssetMenuAttribute | The attribute that puts an SO type in the Assets/Create menu | [CreateAssetMenuAttribute](https://docs.unity3d.com/ScriptReference/CreateAssetMenuAttribute.html) |
| Scripting API — Serialization callbacks | `ISerializationCallbackReceiver` | [ISerializationCallbackReceiver](https://docs.unity3d.com/ScriptReference/ISerializationCallbackReceiver.html) |
| Scripting API — UnityEvent | The Editor-wireable delegate type behind Observer-pattern SO events | [UnityEvent](https://docs.unity3d.com/ScriptReference/UnityEvent.html) |

Every other link in this `references/` folder is a specific page under these
roots, verified to resolve before inclusion. Consult the live Manual/Scripting
API for anything not covered here — the pattern-specific files in this folder
distill a community technique, not an official Unity subsystem, so no single
upstream page ever covers a whole pattern by itself.

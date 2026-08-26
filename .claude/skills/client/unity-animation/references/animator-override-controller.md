# Animator Override Controller — one graph, many clip sets

Sources: [Animator Override Controller](https://docs.unity3d.com/Manual/AnimatorOverrideController.html), [AnimatorOverrideController API](https://docs.unity3d.com/ScriptReference/AnimatorOverrideController.html), [Animation transition](https://docs.unity3d.com/Manual/class-Transition.html).
Covers: SKILL.md §4 — **"Express transition timing in normalised time whenever clips can be overridden"**, **"Swap clips through an Override Controller instead of duplicating the controller"**.

How several visual variants share one state machine, and the timing
constraint that sharing imposes on every transition in it. The graph being
shared is [animator-controller.md](animator-controller.md)'s.

## What it does

| Subject | What it decides | Source |
|---|---|---|
| Clip remapping | Replaces which clip each state plays while leaving states, transitions, parameters and layers untouched — one graph stays the single source of truth | [Animator Override Controller](https://docs.unity3d.com/Manual/AnimatorOverrideController.html) |
| Against duplicating the controller | A duplicated graph drifts the first time a transition is edited in one copy and not the others, and the drift is invisible until it ships | [Animator Override Controller](https://docs.unity3d.com/Manual/AnimatorOverrideController.html) |
| Chaining | An override controller can itself be overridden, so a species variant and an equipment variant compose instead of multiplying | [AnimatorOverrideController API](https://docs.unity3d.com/ScriptReference/AnimatorOverrideController.html) |
| Empty overrides | A slot left empty falls back to the base controller's clip, so a partial variant only lists what actually differs | [Animator Override Controller](https://docs.unity3d.com/Manual/AnimatorOverrideController.html) |

## Applying overrides at runtime

| Member | Effect | Source |
|---|---|---|
| Batched override application | Applies a whole list of clip pairs in one call, which avoids re-resolving the controller once per individual assignment | [AnimatorOverrideController API](https://docs.unity3d.com/ScriptReference/AnimatorOverrideController.html) |
| Indexer assignment | Replaces one clip; convenient, and the wrong shape for a full variant swap where every clip changes at once | [AnimatorOverrideController API](https://docs.unity3d.com/ScriptReference/AnimatorOverrideController.html) |
| Reading the current overrides | Retrieves the current pairs, which is how a partial change is applied without discarding the others | [AnimatorOverrideController API](https://docs.unity3d.com/ScriptReference/AnimatorOverrideController.html) |
| Assignment timing | Swapping the runtime controller resets state, so apply overrides on a deliberate event such as an equip change rather than per frame | [AnimatorOverrideController API](https://docs.unity3d.com/ScriptReference/AnimatorOverrideController.html) |

**Critical caveat**: a transition authored with a fixed duration in seconds
can be longer than an override clip that replaces a longer original. The
transition then never completes visibly, and the symptom appears only on the
variants with shorter clips. Author transition timing in normalised time on
any graph that will be overridden.

| Related setting | Why it matters here | Source |
|---|---|---|
| Exit time as a fraction | Normalised exit time scales with whatever clip is playing, so it survives a length change that a fixed value does not | [Animation transition](https://docs.unity3d.com/Manual/class-Transition.html) |
| Transition offset | Also normalised, and therefore already variant-safe | [Animation transition](https://docs.unity3d.com/Manual/class-Transition.html) |

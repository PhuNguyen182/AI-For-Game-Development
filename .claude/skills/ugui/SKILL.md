---
name: ugui
description: "uGUI and TextMeshPro: Canvas, CanvasScaler Match, RectTransform anchors, Layout Groups, Mask vs RectMask2D, Selectable, EventSystem, TMP_Text, UI Profiler batching, canvas splitting. Use for Canvas-based runtime UI."
user-invocable: false
---

# Unity UI (uGUI)

Not for: UI Toolkit `UIDocument` (`ui-toolkit`), Animator clip/state-machine content (`unity-animation`), device polling and `.inputactions` incl. `InputSystemUIInputModule` (`unity-input-system`), gameplay rules behind a bound value (`csharp-engineer`), Flexalon layout (`flexalon-layouts`), long-list recycling (`osa-optimized-scrollview-adapter`), tweening a built component (`dotween-tweening`, `litmotion-tweening`), Spine `SkeletonGraphic` content (`spine-animation`).
Docs: https://docs.unity3d.com/Packages/com.unity.ugui@2.6/manual/ (TMP under `manual/TextMeshPro/`), package 2.6.0. Docs are effectively frozen (community report, not official), so check the installed package version before trusting a field.

| Reference | Read when |
|---|---|
| [canvas-and-scaling.md](references/canvas-and-scaling.md) | Choosing a render mode, setting `CanvasScaler`, or fading a subtree with `CanvasGroup` |
| [rect-transform-and-layout.md](references/rect-transform-and-layout.md) | Anchoring, or a Layout Group / Content Size Fitter does not size as expected |
| [visual-components.md](references/visual-components.md) | Choosing an `Image` type, `RawImage`, clipping with `Mask`/`RectMask2D`, Shadow/Outline |
| [interaction-components.md](references/interaction-components.md) | Building a `Selectable`, `ScrollRect`, or a transition needing more than tint/sprite swap |
| [event-system-and-input.md](references/event-system-and-input.md) | A pointer/keyboard event does not reach an element, or a custom handler/input module is needed |
| [legacy-text-and-rich-text.md](references/legacy-text-and-rich-text.md) | Maintaining an existing legacy `Text` screen |
| [textmeshpro-core-and-rich-text.md](references/textmeshpro-core-and-rich-text.md) | New text element, rich-text tag or Style Sheet question |
| [textmeshpro-assets-and-shaders.md](references/textmeshpro-assets-and-shaders.md) | Generating a font asset, inline sprites, or picking a TMP shader |
| [scripting-api-and-extensibility.md](references/scripting-api-and-extensibility.md) | Writing a custom `Graphic`, layout component or `ICanvasElement` |
| [profiling-performance-and-howtos.md](references/profiling-performance-and-howtos.md) | Batch count looks wrong, or building world-space / scripted UI |

## Steps
1. **Confirm uGUI fits.** It is Unity's primary recommendation for runtime game UI; route to `ui-toolkit` only for data binding, SVG or no-GameObject-per-element cost. Target aspect ratios/platforms or the system choice unstated: ask, and proceed only on a flagged assumption.
2. **Pick the render mode from where the UI lives**: Overlay for a HUD, Camera only when perspective/post-processing must affect it, World Space for diegetic/VR, per [canvas-and-scaling.md](references/canvas-and-scaling.md).
3. **Use Scale With Screen Size and set Match deliberately.** Default 0 oversizes a wider-than-reference screen; single-orientation games match the stable axis (portrait: width, 0; landscape: height, 1); use 0.5 only when both orientations ship. Responsive means anchors plus `CanvasScaler` together.
4. **Anchor before positioning**; stretch anchors carry responsive sizing, per [rect-transform-and-layout.md](references/rect-transform-and-layout.md).
5. **One owner per `RectTransform` size.** A Layout Group, Content Size Fitter, Flexalon, a tween, a Spine `SkeletonGraphic` or hand-sizing fight silently. Try Layout Element overrides before a custom layout component.
6. **Pick the Image Type deliberately** (Sliced panel, Tiled repeat, Filled progress, Simple fixed icon) and **`RectMask2D` before `Mask`**; `Mask` only for a non-rectangular clip, per [visual-components.md](references/visual-components.md).
7. **Compose from `Selectable` components.** Implement `IPointer*Handler` only for behaviour none express, and never poll pointer state in `Update`, per [interaction-components.md](references/interaction-components.md) and [event-system-and-input.md](references/event-system-and-input.md).
8. **Transitions**: Color Tint or Sprite Swap first. Animation mode only when they cannot express the feedback; it needs an `Animator`, never the legacy `Animation` component (documented incompatibility).
9. **One active Input Module per `EventSystem`; one `Graphic Raycaster` per Canvas that takes pointer events.**
10. **New text is `TMP_Text`**; legacy `Text` only to maintain an existing screen. Collapse a repeated tag stack into a Style Sheet. Font assets: SDF whenever outline/underlay/glow/scaling is needed; one sprite atlas per text object.
11. **Extend by subclassing** `Graphic`/`LayoutGroup`/`BaseInputModule`, after confirming no built-in composition covers it, per [scripting-api-and-extensibility.md](references/scripting-api-and-extensibility.md).
12. **Diagnose batching from Self/Cumulative Batch Count first**; split a frequently-updating element onto its own Canvas, per [profiling-performance-and-howtos.md](references/profiling-performance-and-howtos.md). Label UI Profiler readings Editor-only (`qa-standards`) until measured in a build.

## Never
- Decide what a bound value means for gameplay: display and react only; Core decides.
- Add a second `EventSystem` "just in case"; for `InputSystemUIInputModule` setup defer to `unity-input-system`.

## Output
```
## uGUI Work — <screen/element>
- Canvas: <render mode, CanvasScaler mode + Match/reference resolution, CanvasGroup use>
- Layout: <anchoring, layout controllers, custom layout>
- Components: <Image types, Mask vs RectMask2D, transitions>
- Input: <EventSystem/module, raycasters>
- Text: <TMP vs legacy, SDF settings>
- Performance: <batch counts, Editor-only label, canvas splitting>
- Known limitations: <...>
```
On request only, add `Latent concerns` and `Future remediation`, each with its trigger.

## Example
- "Hover needs three properties changed together" -> Animation transition via Auto Generate Animation; Highlighted/Pressed/Disabled clips as single keyframes, Normal left empty; confirmed no legacy `Animation` component on the object.

---
name: ugui
description: "uGUI and TextMeshPro: Canvas, CanvasScaler, RectTransform, Layout Groups, RectMask2D, TMP_Text. Use for Canvas UI."
user-invocable: false
---

# Unity UI (uGUI)

- **Not for:** UI Toolkit `UIDocument` (`ui-toolkit`).
- **Not for:** Animator clip/state-machine content (`unity-animation`).
- **Not for:** device polling and `.inputactions` incl. `InputSystemUIInputModule` (`unity-input-system`).
- **Not for:** gameplay rules behind a bound value (`csharp-engineer`).
- **Not for:** Flexalon layout (`flexalon-layouts`).
- **Not for:** long-list recycling (`osa-optimized-scrollview-adapter`).
- **Not for:** tweening a built component (`dotween-tweening`, `litmotion-tweening`).
- **Not for:** Spine `SkeletonGraphic` content (`spine-animation`).
- **Docs:** https://docs.unity3d.com/Packages/com.unity.ugui@2.6/manual/ (TMP under `manual/TextMeshPro/`), package 2.6.0.
  - **Docs are effectively frozen:** a community report, not official, so check the installed package version before trusting a field.

## References
- **[canvas-and-scaling.md](references/canvas-and-scaling.md):** Choosing a render mode, setting `CanvasScaler`, or fading a subtree with `CanvasGroup`.
- **[rect-transform-and-layout.md](references/rect-transform-and-layout.md):** Anchoring, or a Layout Group / Content Size Fitter does not size as expected.
- **[visual-components.md](references/visual-components.md):** Choosing an `Image` type, `RawImage`, clipping with `Mask`/`RectMask2D`, Shadow/Outline.
- **[interaction-components.md](references/interaction-components.md):** Building a `Selectable`, `ScrollRect`, or a transition needing more than tint/sprite swap.
- **[event-system-and-input.md](references/event-system-and-input.md):** A pointer/keyboard event does not reach an element, or a custom handler/input module is needed.
- **[legacy-text-and-rich-text.md](references/legacy-text-and-rich-text.md):** Maintaining an existing legacy `Text` screen.
- **[textmeshpro-core-and-rich-text.md](references/textmeshpro-core-and-rich-text.md):** New text element, rich-text tag or Style Sheet question.
- **[textmeshpro-assets-and-shaders.md](references/textmeshpro-assets-and-shaders.md):** Generating a font asset, inline sprites, or picking a TMP shader.
- **[scripting-api-and-extensibility.md](references/scripting-api-and-extensibility.md):** Writing a custom `Graphic`, layout component or `ICanvasElement`.
- **[profiling-performance-and-howtos.md](references/profiling-performance-and-howtos.md):** Batch count looks wrong, or building world-space / scripted UI.

## Steps
1. **Confirm uGUI fits:** It is Unity's primary recommendation for runtime game UI.
   - **Route to `ui-toolkit`:** only for data binding, SVG or no-GameObject-per-element cost.
   - **Target aspect ratios/platforms or the system choice unstated:** step 13.
2. **Pick the render mode from where the UI lives:** per [canvas-and-scaling.md](references/canvas-and-scaling.md).
   - **Overlay:** for a HUD.
   - **Camera:** only when perspective/post-processing must affect it.
   - **World Space:** for diegetic/VR.
3. **Use Scale With Screen Size and set Match deliberately:**
   - **Default 0:** oversizes a wider-than-reference screen.
   - **Single-orientation games:** match the stable axis (portrait: width, 0; landscape: height, 1).
   - **0.5:** only when both orientations ship.
   - **Responsive:** means anchors plus `CanvasScaler` together.
4. **Anchor before positioning:** stretch anchors carry responsive sizing, per [rect-transform-and-layout.md](references/rect-transform-and-layout.md).
5. **One owner per `RectTransform` size:**
   - **Silent fights:** a Layout Group, Content Size Fitter, Flexalon, a tween, a Spine `SkeletonGraphic` or hand-sizing fight silently.
   - **Layout Element overrides:** try them before a custom layout component.
6. **Pick the Image Type deliberately (Sliced panel, Tiled repeat, Filled progress, Simple fixed icon):** per [visual-components.md](references/visual-components.md).
   - **`RectMask2D` before `Mask`:** `Mask` only for a non-rectangular clip.
7. **Compose from `Selectable` components:** per [interaction-components.md](references/interaction-components.md) and [event-system-and-input.md](references/event-system-and-input.md).
   - **Pointer handlers:** implement `IPointer*Handler` only for behaviour none express.
   - **Pointer state:** never poll it in `Update`.
8. **Transitions:** Color Tint or Sprite Swap first.
   - **Animation mode:** only when they cannot express the feedback.
   - **Animation mode needs an `Animator`:** never the legacy `Animation` component (documented incompatibility).
9. **One active Input Module per `EventSystem`; one `Graphic Raycaster` per Canvas that takes pointer events:**
10. **New text is `TMP_Text`:** legacy `Text` only to maintain an existing screen.
    - **Repeated tag stack:** collapse it into a Style Sheet.
    - **Font assets:** SDF whenever outline/underlay/glow/scaling is needed.
    - **Sprite atlas:** one per text object.
11. **Extend by subclassing:** `Graphic`/`LayoutGroup`/`BaseInputModule`, after confirming no built-in composition covers it, per [scripting-api-and-extensibility.md](references/scripting-api-and-extensibility.md).
12. **Diagnose batching from Self/Cumulative Batch Count first:** per [profiling-performance-and-howtos.md](references/profiling-performance-and-howtos.md).
    - **Frequently-updating element:** split it onto its own Canvas.
    - **UI Profiler readings:** label them Editor-only (`qa-standards`) until measured in a build.
13. **Missing input:** target aspect ratios/platforms or the system choice unstated.
    - **Dispatched agent:** `Blocked` or `Needs-decision`.
    - **Main session:** `AskUserQuestion`.
    - **Otherwise:** proceed only on a flagged assumption.

## Never
- **Decide what a bound value means for gameplay:** display and react only; Core decides.
- **Add a second `EventSystem` "just in case":** for `InputSystemUIInputModule` setup defer to `unity-input-system`.

## Output
```
## uGUI Work — <screen/element>
- Canvas: <render mode, CanvasScaler mode + Match/reference resolution, CanvasGroup use>
- Layout: <anchoring, layout controllers, custom layout>
- Components: <Image types, Mask vs RectMask2D, transitions>
- Input: <EventSystem/module, raycasters>
- Text: <TMP vs legacy, SDF settings>
- Performance: <batch counts, Editor-only label, canvas splitting>
```

## Example
- **"Hover needs three properties changed together":** Animation transition via Auto Generate Animation.
  - **Clips:** Highlighted/Pressed/Disabled as single keyframes, Normal left empty.
  - **Check:** confirmed no legacy `Animation` component on the object.

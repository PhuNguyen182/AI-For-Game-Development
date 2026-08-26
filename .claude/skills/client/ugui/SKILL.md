---
name: ugui
description: >
  Unity UI (uGUI) technique — the GameObject-based `Canvas`/`RectTransform`
  runtime UI system (`UnityEngine.UI`, `UnityEngine.EventSystems`, and
  TextMeshPro's `TMPro` namespace as its text renderer): Canvas render
  modes and sorting, `CanvasScaler` scale modes, `CanvasGroup`,
  `RectTransform` anchors/pivot, Auto Layout (`LayoutGroup`,
  `ContentSizeFitter`, `LayoutElement`, `AspectRatioFitter`), visual
  components (`Image` Simple/Sliced/Tiled/Filled, `RawImage`, legacy
  `Text`, `Mask`/`RectMask2D`, Shadow/Outline effects), interaction
  components (`Selectable`, `Button`, `Toggle`/`ToggleGroup`, `Slider`,
  `Scrollbar`, `Dropdown`, `InputField`, `ScrollRect`) and their Color
  Tint/Sprite Swap/Animation transitions, the `EventSystem`/Raycaster/
  Input Module pipeline, TextMeshPro UI text (`TMP_Text`, `TMP_InputField`,
  `TMP_Dropdown`, its full rich text tag set, Style Sheets, Font Asset
  Creator, Sprite Assets, SDF shaders), the UI (Canvas) Profiler module and
  batching rules, and extending the system (`Graphic`, `LayoutGroup`,
  custom raycasters/input modules). Use for building or debugging any
  runtime Canvas-based HUD, menu, or diegetic/world-space UI. Not for:
  UI Toolkit/`UIDocument` screens (`ui-toolkit`), Animator clips or state
  machines behind a UI transition beyond wiring the Selectable Animation
  mode itself (`unity-animation`), input device polling and
  `.inputactions` authoring (`unity-input-system` — this skill only
  consumes the events its `EventSystem` delivers), and any gameplay rule
  or state decision behind a bound value (`csharp-engineer`).
---

# Unity UI (uGUI) — Canvas, RectTransform, Interaction, TextMeshPro

## Bundled resources

### References
Read-only context, loaded on demand so SKILL.md itself stays short.

| File | Contents | Read when |
|---|---|---|
| [root-links.md](references/root-links.md) | Manual/API roots, the package 2.6.0 version pin, topic→file map, disclosed gaps | Starting any task here, or confirming a fact against the installed package |
| [canvas-and-scaling.md](references/canvas-and-scaling.md) | Canvas render modes, sorting, `CanvasScaler`'s three scale modes, `CanvasGroup` | Setting up a new Canvas, or a layout doesn't scale right across resolutions |
| [rect-transform-and-layout.md](references/rect-transform-and-layout.md) | Anchors/pivot model, Layout Element, Content Size Fitter, Layout Groups, calculation order, custom layout interfaces | Positioning anything, or a layout won't auto-size the way it should |
| [visual-components.md](references/visual-components.md) | `Image` types and 9-slicing, `RawImage`, legacy `Text`, `Mask` vs `RectMask2D`, Shadow/Outline | Choosing an Image Type, or deciding how to clip content |
| [interaction-components.md](references/interaction-components.md) | `Selectable` base, Button/Toggle/Slider/Scrollbar/Dropdown/InputField, `ScrollRect` | Building any clickable/draggable/scrollable element |
| [animation-and-transitions.md](references/animation-and-transitions.md) | The Selectable Animation transition mode, Animator Controller setup, the four state clips | A transition needs more than a color tint or sprite swap |
| [event-system-and-input.md](references/event-system-and-input.md) | `EventSystem`, Input Modules, Raycasters, event interfaces, `EventTrigger`, custom input modules | Wiring or debugging how a pointer/keyboard event reaches a UI element |
| [legacy-text-and-rich-text.md](references/legacy-text-and-rich-text.md) | Legacy `Text`'s small rich text tag set | Maintaining an existing legacy-`Text` screen |
| [textmeshpro-core-and-rich-text.md](references/textmeshpro-core-and-rich-text.md) | `TMP_Text` UI component properties, the full rich text tag table, Style Sheets | Any new text element, or a rich-text/style-sheet question |
| [textmeshpro-assets-and-shaders.md](references/textmeshpro-assets-and-shaders.md) | Font Asset Creator (SDF/atlas settings), Sprite Assets, TMP shader variants | Generating a font asset, adding inline sprites, or picking a text shader |
| [scripting-api-and-extensibility.md](references/scripting-api-and-extensibility.md) | Key namespaces, extending `Graphic`/`LayoutGroup`, `VertexHelper`, `ICanvasElement` | Writing a custom visual/layout/input component |
| [profiling-performance-and-howtos.md](references/profiling-performance-and-howtos.md) | UI Profiler batching rules, canvas-splitting practice, multi-resolution/world-space/scripted-creation how-tos | Draw calls or batches look wrong, or building world-space/scripted UI |

## 1. Objective
Build uGUI screens that stay responsive across resolutions and aspect
ratios, clip and batch efficiently, and read gameplay state without ever
deciding it — avoiding this system's characteristic silent failures: a
`CanvasScaler` Match slider left at its default that oversizes everything
on a wider aspect ratio, a `Mask` reached for where a cheaper `RectMask2D`
would do, a `CanvasGroup` added purely to fade a large subtree that quietly
breaks its batch, an `Animator`-driven Selectable transition built on the
legacy Animation system instead of `Animator` (a documented incompatibility,
not a bug to chase), a custom `IPointer*Handler` polling state in `Update`
instead of reacting to the dispatched event, and a new text element
authored on legacy `Text` when `TMP_Text` was always the right default.

## 2. Role
Act as the uGUI specialist for the client track — the skill reached for
whenever a runtime HUD/menu/diegetic UI is built, styled, wired, or
debugged on `Canvas`/`RectTransform`. You decide Canvas setup, layout,
component composition, event wiring, and text/typography; you never decide
what a UI displays as a game-rule outcome.

## 3. When to invoke this skill
- Setting up or debugging a `Canvas`: render mode, sort order, `CanvasScaler`, `CanvasGroup`.
- Positioning or auto-sizing anything with `RectTransform`, anchors, Layout Groups, or Content Size Fitter.
- Choosing or configuring a visual component: `Image` type/9-slicing, `RawImage`, `Mask`/`RectMask2D`, Shadow/Outline.
- Building or wiring an interaction component: `Button`, `Toggle`, `Slider`, `Scrollbar`, `Dropdown`, `InputField`, `ScrollRect`, or a `Selectable` transition.
- Wiring the `EventSystem`/Raycaster/Input Module pipeline, or a custom event handler/input module.
- Any TextMeshPro UI text: component setup, rich text tags, Style Sheets, Font Asset Creator, Sprite Assets, shader/material choice.
- Diagnosing UI batching/draw-call regressions via the UI Profiler module, or splitting canvases for performance.
- Writing a custom `Graphic`/`LayoutGroup`/input module extension.
- World-space/diegetic UI setup, multi-resolution design, or creating UI elements from script.
- Negative trigger: the screen genuinely belongs on UI Toolkit's `UIDocument` (Editor tooling, or a runtime surface that specifically needs data binding, SVG, or textureless elements) — that's `ui-toolkit`; per its own `choosing-ui-system.md`, uGUI remains Unity's primary recommendation for runtime game UI, so default here unless one of UI Toolkit's specific strengths is actually needed.
- Negative trigger: the Animator Controller's own clips/state machine content once a Selectable's Animation transition is wired to it — that's `unity-animation`; this skill owns wiring the transition itself (per [animation-and-transitions.md](references/animation-and-transitions.md)), not authoring arbitrary Animator content beyond it.
- Negative trigger: reading the input device or authoring `.inputactions` — that's `unity-input-system`; this skill only reacts to the events its `EventSystem`/Input Module delivers, and defers to that skill for `InputSystemUIInputModule` specifically.
- Negative trigger: whether a bound value is currently allowed, what it means for the game, or any cooldown/resource/economy check — that's `csharp-engineer`'s Shared Core, per `coding-principles.md`'s Shared Core integrity section.
- Negative trigger: animating an already-built uGUI component's property over time (a fade, a slide-in, a punch/shake) — that's `dotween-tweening` or `litmotion-tweening`; this skill builds and wires the component, it doesn't own tweening it. Coordinate with whichever tweening skill is in play so a tween and a Layout Group/Content Size Fitter never drive the same `RectTransform` property at once, per [rect-transform-and-layout.md](references/rect-transform-and-layout.md).

## 4. How to use this skill
1. **Confirm uGUI is the right system before authoring anything new** — per [root-links.md](references/root-links.md) and `ui-toolkit`'s own `choosing-ui-system.md`, Unity's Manual lists uGUI as the primary recommendation for *runtime* game UI; only route to `ui-toolkit` when the surface specifically needs one of UI Toolkit's own strengths (data binding, SVG, no-GameObject-per-element cost).
2. **Pick the Canvas render mode from where the UI actually lives, not by default** — Screen Space – Overlay for a standard HUD, Screen Space – Camera only when camera perspective/post-processing must affect the UI, World Space for diegetic/VR UI, per [canvas-and-scaling.md](references/canvas-and-scaling.md).
3. **Drive multi-resolution scaling through `CanvasScaler`'s Scale With Screen Size mode, and set Match deliberately** — leaving Match at its default 0 (Width) oversizes a wider-than-reference aspect ratio; use 0.5 once both portrait and landscape (or several aspect ratios) must be supported, per [canvas-and-scaling.md](references/canvas-and-scaling.md) and `coding-principles.md`'s responsive-UI expectation.
4. **Anchor before positioning, and let stretch anchors carry responsive sizing** — a fixed-anchor element only ever gets a constant pixel offset; a stretch anchor is what makes a panel's size track its parent, per [rect-transform-and-layout.md](references/rect-transform-and-layout.md).
5. **Let a Content Size Fitter or Layout Group own child sizing — never hand-size a RectTransform that a layout controller also controls** — the two fight silently, with whichever runs last winning; compose Layout Element overrides before reaching for a custom layout component, per [rect-transform-and-layout.md](references/rect-transform-and-layout.md) and YAGNI in `coding-principles.md`.
6. **Pick the Image Type deliberately** — Sliced for a resizable panel/button background, Tiled for a repeating-scale background, Filled for a progress/cooldown indicator, Simple only for a fixed-size icon, per [visual-components.md](references/visual-components.md).
7. **Reach for `RectMask2D` before `Mask`** — it has no stencil buffer, no extra draw call, and no material change, versus `Mask`'s stencil-buffer cost; use `Mask` only for a genuinely non-rectangular clip shape, per [visual-components.md](references/visual-components.md) and `performance-and-algorithms.md`'s measured-tradeoff rule.
8. **Compose interaction from `Selectable`, never hand-roll pointer state tracking** — `Button`/`Toggle`/`Slider`/`Scrollbar`/`Dropdown`/`InputField`/`ScrollRect` already implement the event interfaces correctly; implement `IPointer*Handler` directly on a `MonoBehaviour` only for behavior none of them expresses, per [interaction-components.md](references/interaction-components.md) and [event-system-and-input.md](references/event-system-and-input.md).
9. **Wire the Animation transition through an `Animator` Controller, never the legacy Animation system** — it is a documented hard incompatibility, not a bug to debug around; reach for Color Tint or Sprite Swap first per KISS, and escalate to Animation mode only once those genuinely can't express the feedback, per [animation-and-transitions.md](references/animation-and-transitions.md).
10. **Keep exactly one active Input Module per `EventSystem`, and add a `Graphic Raycaster` to every Canvas that must receive pointer events** — per [event-system-and-input.md](references/event-system-and-input.md); route to `unity-input-system` the moment the task is about the Input System's own `InputSystemUIInputModule`, actions, or device bindings rather than the raycaster/module wiring itself.
11. **Default new text to TextMeshPro's `TMP_Text`, not legacy `Text`** — reach for [legacy-text-and-rich-text.md](references/legacy-text-and-rich-text.md) only when maintaining an existing legacy screen; author new text per [textmeshpro-core-and-rich-text.md](references/textmeshpro-core-and-rich-text.md), and collapse a repeated tag stack into a Style Sheet instead of copy-pasting it, per DRY/KISS in `coding-principles.md`.
12. **Generate SDF font assets sized to the effects the design actually needs, and keep one sprite atlas per text object** — bitmap/static font assets can't support outline/underlay/glow at all; padding and atlas resolution trade off effect quality against atlas memory; a second sprite atlas on the same text object costs a second draw call, per [textmeshpro-assets-and-shaders.md](references/textmeshpro-assets-and-shaders.md).
13. **Extend by subclassing `Graphic`/`LayoutGroup`/`BaseInputModule`, never by hacking a built-in component's serialized state from outside it** — override `OnPopulateMesh(VertexHelper vh)` for custom geometry, implement `ILayoutElement`/`ILayoutGroup` for custom sizing, per [scripting-api-and-extensibility.md](references/scripting-api-and-extensibility.md); confirm no built-in composition already covers it first, per YAGNI.
14. **Check Self/Cumulative Batch Count in the UI Profiler before diagnosing a draw-call regression as anything else**, and split a frequently-updating element onto its own Canvas away from static chrome — a `CanvasGroup` and a stencil `Mask` are both documented batch-break triggers on top of ordinary material/texture rules, per [profiling-performance-and-howtos.md](references/profiling-performance-and-howtos.md); label any such reading as an Editor-only result per `verification-standards.md` until measured in a real build.
15. **Ask rather than guess when the target aspect ratios/platforms, or the uGUI-vs-UI-Toolkit choice, are not stated** — both gate real decisions (Canvas Scaler settings, whether a screen even belongs in this skill); proceed only on a clearly flagged assumption if the requester is unavailable.

## 5. Specific goals / tasks this skill performs
- Canvas setup: render mode, sort order, `CanvasScaler` mode/settings, `CanvasGroup` fade/interactable wiring.
- RectTransform/anchor layout, and Auto Layout composition (Layout Groups, Content Size Fitter, Layout Element, Aspect Ratio Fitter).
- Visual component authoring: `Image` type/9-slicing, `RawImage`, legacy `Text`, `Mask`/`RectMask2D`, Shadow/Outline.
- Interaction component composition and `Selectable` transition/navigation configuration, including the Animation transition mode.
- `EventSystem`/Raycaster/Input Module wiring and custom event-interface/input-module authoring.
- TextMeshPro UI text: component configuration, rich text tags, Style Sheets, Font Asset Creator settings, Sprite Assets, shader/material selection.
- UI batching/draw-call diagnosis via the UI Profiler module, and canvas-splitting for performance.
- Extending the system: custom `Graphic`/`LayoutGroup`/input module authoring.
- World-space/diegetic UI setup, multi-resolution design, and scripted UI instantiation.
- Out of scope: UI Toolkit/`UIDocument` screens (`ui-toolkit`), Animator clip/state-machine content beyond wiring a Selectable transition (`unity-animation`), input device polling and `.inputactions` authoring (`unity-input-system`), any gameplay rule or state decision behind a bound value (`csharp-engineer`).

## 6. Output format
```
## uGUI Work — <screen/element name>
- System choice: uGUI confirmed over UI Toolkit — why
- Canvas: render mode, CanvasScaler mode + Match/Reference Resolution, CanvasGroup usage (if any)
- Layout: anchoring approach, Layout Groups/Content Size Fitter used, custom layout component introduced (if any)
- Components: visual/interaction components used, Image Type choices, Mask vs RectMask2D choice
- Transitions: Selectable Transition mode(s), Animator Controller confirmed (if Animation mode)
- Input plumbing: EventSystem/Input Module confirmed, Raycaster(s) added per Canvas
- Text: TMP vs legacy Text — why; rich text tags/Style Sheets used; font asset SDF settings (if a new one was generated)
- Performance: UI Profiler batch counts checked (Editor-only unless stated otherwise), canvas splitting confirmed for frequently-updating elements
- Shared Core boundary: confirmed no gameplay outcome decided in this layer
- Layer: Game.Client.*
- Known limitations: <...>
```

**Extended report — emit ONLY when the requester asks for it.** It replaces
the one-line `Known limitations` above with all three fields:
```
- Known limitations: <what the delivered UI does not cover — omit this line entirely if there are genuinely none>
- Latent concerns: <failure modes not yet triggered: assumptions that hold only under current conditions, thresholds not yet reached, trade-offs knowingly deferred>
- Future remediation: <the concrete fix for each concern above, each with the condition that should trigger it>
```

## 7. Examples
**Example 1**
- Input: "Build a responsive PC + mobile inventory grid with a scrollable item list."
- Output: root `Canvas` set to Screen Space – Overlay with `CanvasScaler` on Scale With Screen Size, Match at 0.5 for both aspect-ratio families; the item list built as a `ScrollRect` with `RectMask2D` on the Viewport (not `Mask` — the clip shape is a plain rectangle), Content driven by a Vertical Layout Group plus a Content Size Fitter rather than a hand-sized rect; item labels authored as `TMP_Text`, not legacy `Text`.

**Example 2**
- Input: "The button's hover animation needs three properties to change together, a color tint alone isn't enough."
- Output: escalated the Selectable's Transition to Animation mode per [animation-and-transitions.md](references/animation-and-transitions.md) — generated the Animator Controller via Auto Generate Animation, recorded the Highlighted/Pressed/Disabled clips as single keyframes changing all three properties, left Normal empty since the button's own Inspector values already cover it. Confirmed the object has no legacy `Animation` component wired to it, since Animation-mode transitions require `Animator` specifically.

**Example 3**
- Input: "The HUD's health bar text updates every frame and the whole menu redraws with it — investigate the frame cost."
- Output: read the UI Profiler's Self/Cumulative Batch Count for the HUD Canvas (Editor-only measurement, flagged as such) and found the health text shared a Canvas with static menu chrome — any change to the text forced a rebuild of everything on that Canvas. Split the health bar onto its own Canvas, per [profiling-performance-and-howtos.md](references/profiling-performance-and-howtos.md); also confirmed the text update is gated on an actual value change rather than unconditional per-frame `.ToString()`, per `performance-and-algorithms.md`.

## 8. Edge cases & guardrails
- Never leave `CanvasScaler`'s Match slider at its default 0 (Width) for a UI that must support more than one aspect ratio family — it's the documented cause of oversized UI on a wider-than-reference screen.
- Never give a RectTransform both a fixed size and a Layout Group/Content Size Fitter controlling it — they silently conflict; pick one owner.
- Never reach for `Mask` by habit where the clip shape is a plain rectangle — `RectMask2D` is strictly cheaper for that case.
- Never wire a Selectable's Animation transition to a legacy `Animation` component — the Manual states this combination is not supported; it requires `Animator`.
- Never run more than one Input Module active on the same `EventSystem`, and never add an `EventSystem` "just in case" when only the Input System's own `InputSystemUIInputModule` is actually in play — check with `unity-input-system` first.
- Never author a new screen's text on legacy `Text` — TMP is the default; legacy `Text` is a maintenance-only surface for existing screens.
- Never generate a static/bitmap TMP font asset for text that needs outline/underlay/glow or heavy scaling — those effects require an SDF asset.
- Never reference more than one sprite atlas from the same TMP text object without accounting for the extra draw call each additional atlas costs.
- Never claim a batching/draw-call fix is verified from the UI Profiler alone without labelling it an Editor-only result, per `verification-standards.md` — it does not run in a development build at all.
- Never write a custom `Graphic`/`LayoutGroup`/input module before confirming no built-in composition already covers the need, per YAGNI in `coding-principles.md`.
- If the target aspect ratios/platforms, or the uGUI-vs-UI-Toolkit choice, are not stated, ask rather than silently pick one — both gate real decisions in this skill.
- Never let this layer decide what a bound value means for gameplay — it displays and reacts to input; `Game.Core.*` decides the outcome, per `coding-principles.md`'s Shared Core integrity section.

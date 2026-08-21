# Choosing a UI System — IMGUI vs uGUI vs UI Toolkit

Source: [Comparison of UI systems in Unity](https://docs.unity3d.com/Manual/UI-system-compare.html), [Introduction to UI Toolkit](https://docs.unity3d.com/Manual/ui-systems/introduction-ui-toolkit.html), [UI Toolkit for advanced Unity developers](https://docs.unity3d.com/Manual/best-practice-guides/ui-toolkit-for-advanced-unity-developers/bpg-uiad-index.html).
Covers: SKILL.md §4 — **"Confirm UI Toolkit is the right system for this surface before authoring anything"**.

The decision this file settles: which of Unity's three UI systems a given
screen or tool should use, and why UI Toolkit is not a blanket replacement
for uGUI yet. Once UI Toolkit is confirmed as the system, structure moves to
[uxml-and-visual-tree.md](uxml-and-visual-tree.md).

## Runtime UI: uGUI is still Unity's primary recommendation

| Subject | What it decides | Source |
|---|---|---|
| Unity's own recommendation | For **runtime** game UI, Unity's Manual lists uGUI as the primary recommendation and UI Toolkit as the alternative — the reverse of Editor tooling | [Comparison of UI systems](https://docs.unity3d.com/Manual/UI-system-compare.html) |
| Animation Clips / Timeline | UI Toolkit has **no integration** with Animation Clips or Timeline; uGUI does. A UI that needs keyframed animation belongs on uGUI, or needs USS transitions built by hand (see [uss-styling-and-layout.md](uss-styling-and-layout.md)) | [Comparison of UI systems](https://docs.unity3d.com/Manual/UI-system-compare.html) |
| Inspector-wired events | uGUI supports serialized `UnityEvent` hookups in the Inspector; UI Toolkit does not — every UI Toolkit callback is registered in code | [Comparison of UI systems](https://docs.unity3d.com/Manual/UI-system-compare.html) |
| In-scene authoring | uGUI elements are GameObjects editable in the Hierarchy/Scene view; UI Toolkit elements are not scene objects at all — they exist only in a virtual visual tree authored in UXML/UI Builder | [Comparison of UI systems](https://docs.unity3d.com/Manual/UI-system-compare.html) |
| MonoBehaviour referencing | uGUI elements are directly draggable into a MonoBehaviour's Inspector field; a `VisualElement` has no such serialized reference and must be queried by name/type at runtime | [Comparison of UI systems](https://docs.unity3d.com/Manual/UI-system-compare.html) |
| Data binding, SVG, RTL/emoji text, textureless elements | All four are UI Toolkit strengths uGUI lacks | [Comparison of UI systems](https://docs.unity3d.com/Manual/UI-system-compare.html) |
| World-space / VR UI | UI Toolkit is specifically recommended here, over uGUI's World Space Canvas — see [runtime-panels-and-input.md](runtime-panels-and-input.md) | [Comparison of UI systems](https://docs.unity3d.com/Manual/UI-system-compare.html) |
| Maturity | "UI Toolkit is in active development and releases new features frequently. uGUI and IMGUI are established and production-proven... updated infrequently" — expect API movement release to release | [Comparison of UI systems](https://docs.unity3d.com/Manual/UI-system-compare.html) |
| Role fit | Comparison table rates UI Toolkit full support for UI Designers, only partial for Technical Artists; uGUI is the reverse | [Comparison of UI systems](https://docs.unity3d.com/Manual/UI-system-compare.html) |

**Critical caveat**: this project has no dedicated skill for uGUI/Canvas
authoring. If the correct system for a runtime screen is uGUI rather than UI
Toolkit — per the table above — say so explicitly rather than forcing the
task into UI Toolkit; there is no owning skill to route to.

## Editor tooling: UI Toolkit is the primary recommendation, IMGUI the fallback

| Subject | What it decides | Source |
|---|---|---|
| Editor UI default | UI Toolkit is Unity's primary recommendation for custom Editor windows, inspectors, and property drawers; IMGUI is the alternative, kept mainly for legacy code and a handful of unported calls | [Comparison of UI systems](https://docs.unity3d.com/Manual/UI-system-compare.html) |
| Architecture model | UI Toolkit is **retained-mode**: a persistent visual tree is built once and re-styled/re-laid-out on state change. IMGUI is immediate-mode: `OnGUI()` re-declares the whole UI every frame with no persistent tree | [Introduction to UI Toolkit](https://docs.unity3d.com/Manual/ui-systems/introduction-ui-toolkit.html) |
| Design separation | UXML = structure, USS = style, C# = behavior — deliberately mirrors HTML/CSS/JS | [Introduction to UI Toolkit](https://docs.unity3d.com/Manual/ui-systems/introduction-ui-toolkit.html) |
| Shared system | Editor tooling and runtime game UI use the same elements, styling, and layout engine — only the hosting differs (`EditorWindow.rootVisualElement` vs `UIDocument`/Panel Renderer) | [Introduction to UI Toolkit](https://docs.unity3d.com/Manual/ui-systems/introduction-ui-toolkit.html) |

## Advanced-developer guide takeaways (validated Unity 6.0 — cross-check newer facts)

| Recommendation | What it decides | Source |
|---|---|---|
| Prepare graphic/font assets before opening UI Builder | Treat asset import settings as a pre-step, not something iterated on inside the UI workflow | [Graphic and font assets preparation](https://docs.unity3d.com/Manual/best-practice-guides/ui-toolkit-for-advanced-unity-developers/graphic-and-font-assets-preparation.html) |
| Prefer UI Builder over pure code for layout/style | Visual authoring is the recommended default; drop to C#-only construction only where content is genuinely dynamic | [UI Builder](https://docs.unity3d.com/Manual/best-practice-guides/ui-toolkit-for-advanced-unity-developers/ui-builder.html) |
| Treat performance optimization as its own late pass | Not incidental to styling — a dedicated chapter exists because batching/atlas tuning is a distinct activity, per [rendering-and-performance.md](rendering-and-performance.md) | [Optimizing performance](https://docs.unity3d.com/Manual/best-practice-guides/ui-toolkit-for-advanced-unity-developers/optimizing-performance.html) |
| Use naming conventions for scale | A dedicated chapter exists specifically because large UI Toolkit projects get unmaintainable without one — follow `naming-convention.md` for any custom control class exposed to it | [Naming conventions](https://docs.unity3d.com/Manual/best-practice-guides/ui-toolkit-for-advanced-unity-developers/naming-conventions.html) |

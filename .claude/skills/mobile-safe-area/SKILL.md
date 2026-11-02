---
name: mobile-safe-area
description: "Screen.safeArea, cutouts, uGUI Safe Area, RuntimePanelUtils.ScreenToPanel. Use when mobile UI must clear notches."
user-invocable: false
---

# Mobile Safe Area

- **Not for:** `CanvasScaler` Match and anchoring (`ugui`).
- **Not for:** `PanelSettings` scale mode and the runtime host (`ui-toolkit`).
- **Not for:** camera framing per aspect (`unity-camera-fundamentals`).
- **Not for:** touch and gesture input (`unity-input-system`).
- **Not for:** on-device runs (`device-test-walkthrough`).
- **Docs:** https://docs.unity.com/en-us/engine/6000.6/ (Screen and `Device.Screen` script reference, Device Simulator manual).
  - **uGUI component:** https://docs.unity3d.com/Packages/com.unity.ugui@2.6/manual/script-SafeArea.html — the Safe Area component needs uGUI 2.6.0+.
  - **Version check:** check `Packages/packages-lock.json` before relying on it.

## References
- **[device-simulator-checks.md](references/device-simulator-checks.md):** Verifying a screen in the Simulator, a target device is missing from it, an Android inset differs by OS version, or converting `safeArea` coordinates.

## Steps
1. **Pick the mechanism from the host and package version:**
   - **uGUI with `com.unity.ugui` 2.6.0+:** the built-in Safe Area component.
   - **Older uGUI:** one hand-written fitter component.
   - **UI Toolkit:** step 5.
   - **Scene with both hosts:** one mechanism per host.
   - **Every hand-written reader (uGUI fitter and UI Toolkit, steps 4–6):** aliases `using Screen = UnityEngine.Device.Screen;` so the Simulator drives it.
2. **Inset one content root per Canvas or panel; keep backgrounds full-bleed:**
   - **Root:** a full-stretch child of the root Canvas (or the panel's root element), sibling of the background art.
   - **Content:** every interactive or text element sits under it.
   - **Criterion:** exactly one safe-area node per root Canvas or panel, nested Canvases under the content root get none, nothing tappable outside it.
   - **Nested insets:** stack and double the margin.
3. **Choose edges and alignment per orientation:**
   - **Portrait:** top and bottom.
   - **Landscape with a one-sided notch:** symmetric (larger inset on both sides) when the layout is centred, per-side when it hugs the edges.
   - **uGUI component:** exposes Edges, Alignment and Reference Orientation.
   - **Mock silent on it:** symmetric, flagged as an assumption.
4. **uGUI fitter: drive anchors, not offsets:**
   - **Anchors:** `anchorMin = safeArea.min / screenSize`, `anchorMax = safeArea.max / screenSize`, offsets zero: independent of `CanvasScaler`.
   - **Canvas coverage:** the Canvas must cover the window (Overlay, or Camera with a full viewport); otherwise normalize against `camera.pixelRect`.
   - **Root:** no Layout Group, Content Size Fitter or anchor tween on it (`ugui` step 5).
5. **UI Toolkit: padding in panel space:**
   - **Convert:** flip to top-left, then convert with `RuntimePanelUtils.ScreenToPanel(panel, p)`.
   - **Top-left corner:** `(xMin, Screen.height - yMax)`.
   - **Bottom-right corner:** `(xMax, Screen.height - yMin)`.
   - **Full extent:** `(Screen.width, Screen.height)`.
   - **Padding:** left = tl.x, top = tl.y, right = full.x - br.x, bottom = full.y - br.y, on the content root only.
   - **Timing:** apply after the element has a panel (`AttachToPanelEvent`).
   - **Manual's Y formula:** never copy it, per [device-simulator-checks.md](references/device-simulator-checks.md).
6. **Re-apply only on change:**
   - **No event exists:** compare the cached `safeArea` `Rect`, `width`/`height` and `orientation` each frame and write only when one differs (`csharp.md` → Hot paths: no allocation).
   - **Resolution alone:** misses the landscape 180° flip.
   - **uGUI component:** already does this.
7. **Use `Screen.cutouts` only for decoration that crosses the safe edge:** to keep a meaningful part of full-bleed art (avatar frame, banner text) out of the notch.
   - **Interactive elements:** never consult cutouts; the safe area already excludes them.
8. **Check the Android Player Settings against the target API:** per [device-simulator-checks.md](references/device-simulator-checks.md).
   - **Android 15+:** always renders into the cutout, so the fitter is mandatory even when older OS versions letterbox.
   - **Unity 6.5:** moved bar visibility to window-insets APIs.
9. **Target devices or aspect ratios unstated:** `ui-engineer` defaults.
   - **Defaults:** 16:9 and 19.5:9 in the project's orientation, plus 4:3 if tablets ship.
   - **Devices:** one notched and one notch-free device each.
   - **Report:** say so.
10. **Verify in the Device Simulator per target device × orientation (the set from step 9):** the matrix in [device-simulator-checks.md](references/device-simulator-checks.md), Safe Area line on, one screenshot each.
    - **Criterion:** no interactive or text element crosses the line, backgrounds reach every edge.
    - **Label:** the result Editor-indicative (`qa-standards`).
    - **On-device confirmation:** `device-test-walkthrough`.

## Never
- **Hard-code inset pixels or branch on a device model:** notch sizes change every hardware generation, and the Simulator cannot exercise model checks.
- **Put the inset on the Canvas itself or on a background:** the art stops short of the screen edge and shows the clear colour.

## Output
```
## Safe area — <screen / canvas / panel>
- Mechanism: <uGUI Safe Area component (uGUI version) / hand-written fitter / UI Toolkit padding>
- Content root: <hierarchy path>; full-bleed: <background elements>
- Edges and alignment: <per orientation> — <reason>
- Re-apply trigger: <component built-in / Rect + resolution + orientation compare>
- Android: renderOutsideSafeArea <on/off>, target API <level>
- Responsiveness verified: <device × orientation → screenshot path; Simulator (Editor-indicative) or device>
```

## Example
- **"Add the safe-area script to every button so each one avoids the notch":** declined.
  - **Why:** per-element insets stack under nested parents and break anchoring.
  - **Did instead:** inset one content root and kept the buttons anchored inside it.

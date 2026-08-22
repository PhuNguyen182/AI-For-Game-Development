# Root Links — Unity UI (uGUI)

Source: the root index pages listed below, as provided for this skill.
Covers: the whole skill — provenance and version anchor for every file in
this folder.

`com.unity.ugui` is a regular, versioned Package Manager package (unlike UI
Toolkit, which is built into the Editor) — but its own documentation is not
reliably versioned in practice. At the time of writing the Manual/API roots
resolve to **package version 2.6.0**, and a Unity Discussions thread
(not an official statement — read as community-reported, not confirmed)
states the package was effectively frozen at its documentation for years and
is "in maintenance mode": treat any 2.6-specific field below as this
snapshot's content, and re-confirm against the installed package version
before assuming a property exists unchanged on an older or newer uGUI.
TextMeshPro's manual ships as a sub-tree of this same package
(`manual/TextMeshPro/*`) rather than a separately versioned package from
2.x onward, so it shares this same version pin.

| Root | Holds | Source |
|---|---|---|
| Manual — uGUI index | The full topic tree this skill is built from | [Unity UI (uGUI)](https://docs.unity3d.com/Packages/com.unity.ugui@2.6/manual/index.html) |
| Manual — TextMeshPro index | The TMP sub-tree (fonts, rich text, sprites, shaders) | [TextMesh Pro](https://docs.unity3d.com/Packages/com.unity.ugui@2.6/manual/TextMeshPro/index.html) |
| Scripting API — `UnityEngine.UI` / `UnityEngine.EventSystems` / `TMPro` | Every `Graphic`, `Selectable`, event and layout type | [Unity UI and TextMesh Pro API](https://docs.unity3d.com/Packages/com.unity.ugui@2.6/api/index.html) |

## Topic → file map

| Topic | File | Source |
|---|---|---|
| Canvas render modes, sorting, Canvas Scaler, Canvas Group | [canvas-and-scaling.md](canvas-and-scaling.md) | [Canvas](https://docs.unity3d.com/Packages/com.unity.ugui@2.6/manual/UICanvas.html), [Canvas Scaler](https://docs.unity3d.com/Packages/com.unity.ugui@2.6/manual/script-CanvasScaler.html), [Canvas Group](https://docs.unity3d.com/Packages/com.unity.ugui@2.6/manual/script-CanvasGroup.html) |
| RectTransform anchors/pivot, Layout Groups, Content Size Fitter | [rect-transform-and-layout.md](rect-transform-and-layout.md) | [Basic Layout](https://docs.unity3d.com/Packages/com.unity.ugui@2.6/manual/UIBasicLayout.html), [Auto Layout](https://docs.unity3d.com/Packages/com.unity.ugui@2.6/manual/UIAutoLayout.html) |
| Image/RawImage/Text, Mask/RectMask2D, Shadow/Outline | [visual-components.md](visual-components.md) | [Visual Components](https://docs.unity3d.com/Packages/com.unity.ugui@2.6/manual/UIVisualComponents.html), [Mask](https://docs.unity3d.com/Packages/com.unity.ugui@2.6/manual/script-Mask.html), [RectMask2D](https://docs.unity3d.com/Packages/com.unity.ugui@2.6/manual/script-RectMask2D.html), [UI Effects](https://docs.unity3d.com/Packages/com.unity.ugui@2.6/manual/comp-UIEffects.html) |
| Selectable, Button, Toggle, Slider, Scrollbar, Dropdown, InputField, ScrollRect | [interaction-components.md](interaction-components.md) | [Interaction Components](https://docs.unity3d.com/Packages/com.unity.ugui@2.6/manual/UIInteractionComponents.html), [Selectable](https://docs.unity3d.com/Packages/com.unity.ugui@2.6/manual/script-Selectable.html), [Scroll Rect](https://docs.unity3d.com/Packages/com.unity.ugui@2.6/manual/script-ScrollRect.html) |
| Selectable Animation transition mode, Animator Controller setup | [animation-and-transitions.md](animation-and-transitions.md) | [Animation Integration](https://docs.unity3d.com/Packages/com.unity.ugui@2.6/manual/UIAnimationIntegration.html) |
| EventSystem, raycasters, input modules, event interfaces | [event-system-and-input.md](event-system-and-input.md) | [Events](https://docs.unity3d.com/Packages/com.unity.ugui@2.6/manual/EventSystem.html), [Event System Reference](https://docs.unity3d.com/Packages/com.unity.ugui@2.6/manual/EventSystemReference.html) |
| Legacy `Text` rich text tags | [legacy-text-and-rich-text.md](legacy-text-and-rich-text.md) | [Rich Text](https://docs.unity3d.com/Packages/com.unity.ugui@2.6/manual/StyledText.html) |
| TMP UI Text component, full rich text tag set, style sheets | [textmeshpro-core-and-rich-text.md](textmeshpro-core-and-rich-text.md) | [UI Text GameObjects](https://docs.unity3d.com/Packages/com.unity.ugui@2.6/manual/TextMeshPro/TMPObjectUIText.html), [Rich Text](https://docs.unity3d.com/Packages/com.unity.ugui@2.6/manual/TextMeshPro/RichText.html), [Supported Tags](https://docs.unity3d.com/Packages/com.unity.ugui@2.6/manual/TextMeshPro/RichTextSupportedTags.html), [Style Sheets](https://docs.unity3d.com/Packages/com.unity.ugui@2.6/manual/TextMeshPro/StyleSheets.html) |
| Font Asset Creator, Sprite Assets, TMP shaders/materials | [textmeshpro-assets-and-shaders.md](textmeshpro-assets-and-shaders.md) | [Font Asset Creator](https://docs.unity3d.com/Packages/com.unity.ugui@2.6/manual/TextMeshPro/FontAssetsCreator.html), [Sprites](https://docs.unity3d.com/Packages/com.unity.ugui@2.6/manual/TextMeshPro/Sprites.html), [Shaders](https://docs.unity3d.com/Packages/com.unity.ugui@2.6/manual/TextMeshPro/Shaders.html) |
| Key namespaces/classes, extending `Graphic`/`LayoutGroup`, custom raycasters | [scripting-api-and-extensibility.md](scripting-api-and-extensibility.md) | [Scripting API](https://docs.unity3d.com/Packages/com.unity.ugui@2.6/api/index.html) |
| UI Profiler batching, canvas-splitting practice, multi-resolution/world-space/scripted-creation how-tos | [profiling-performance-and-howtos.md](profiling-performance-and-howtos.md) | [UI Profiler](https://docs.unity3d.com/Packages/com.unity.ugui@2.6/manual/ProfilerUI.html), [UI How Tos](https://docs.unity3d.com/Packages/com.unity.ugui@2.6/manual/UIHowTos.html) |

## Disclosed gaps

Manual pages fetched during authoring rendered their body prose reliably but
generally stripped the left-hand sidebar table of contents, so the sub-link
lists below were reconstructed from in-body links, `UIReference.html`'s
index links, and `EventSystemReference.html`'s index links rather than a
single authoritative sitemap. Re-derive a page's own outgoing links directly
if a linked page 404s.

| Page / area | Issue |
|---|---|
| `UIReference.html` | Its index links (`comp-CanvasComponents.html`, `comp-UIVisual.html`, `comp-UIInteraction.html`, `comp-UIAutoLayout.html`) were listed but not independently fetched — the per-component `script-*.html` pages this skill cites were fetched directly instead and are the primary source. |
| `script-Button.html`, `script-Toggle.html`, `script-ToggleGroup.html`, `script-Slider.html`, `script-Scrollbar.html`, `script-Dropdown.html`, `script-InputField.html`, `script-Text.html` | Properties for these components come from `UIInteractionComponents.html`'s/`UIVisualComponents.html`'s summary prose, not each component's own dedicated reference page — treat exact field names/defaults as needing a check against the Inspector before citing one precisely. |
| `script-SelectableTransition.html`, `script-SelectableNavigation.html` | Linked from `script-Selectable.html` but not independently fetched; transition/navigation mode names in [interaction-components.md](interaction-components.md) and [animation-and-transitions.md](animation-and-transitions.md) come from `UIInteractionComponents.html` and `UIAnimationIntegration.html` instead. |
| `script-PhysicsRaycaster.html`, `script-Physics2DRaycaster.html`, `script-EventTrigger.html`, `script-TouchInputModule.html`, `script-EventSystem.html` | Listed by `EventSystemReference.html` but not individually fetched; described in [event-system-and-input.md](event-system-and-input.md) at the level `EventSystem.html`'s overview gives. |
| TMP `FontAssets.html`, `FontAssetsSDF.html`, `Settings.html`, `ColorGradients.html`, `ColorGradientsPresets.html`, `ColorEmojis.html`, `TMPObjects.html`, `RichTextStyle.html` | Linked from fetched TMP pages but not independently opened — flag before citing an SDF/gradient/style-sheet default not already stated in [textmeshpro-core-and-rich-text.md](textmeshpro-core-and-rich-text.md)/[textmeshpro-assets-and-shaders.md](textmeshpro-assets-and-shaders.md). |
| `HOWTO-UIFitContentSize.html`, `HOWTO-UIScreenTransition.html`, `HOWTO-ShaderGraph.html` | Listed by `UIHowTos.html` but not opened — [profiling-performance-and-howtos.md](profiling-performance-and-howtos.md) covers only the three how-tos that were fetched (multi-resolution, world space, scripted creation). |
| Scripting API namespace/class list | The API index page's sidebar did not resolve to fetchable text; the namespace and extensibility surface in [scripting-api-and-extensibility.md](scripting-api-and-extensibility.md) is reconstructed from stable, long-documented `UnityEngine.UI`/`UnityEngine.EventSystems` API shape (confirmed present since `com.unity.ugui@1.0`) rather than a fresh 2.6 fetch — re-check a specific member's signature in the installed Editor before depending on it. |
| Package/doc versioning | The "stuck at 1.0.0 internally, docs effectively frozen" characterization is a Unity Discussions community report, not an official Unity statement — note it as such if it matters to a decision. |

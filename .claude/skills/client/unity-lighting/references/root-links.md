# Root Links

Root/index pages. Follow their own in-page navigation for anything not covered by the other files in this folder — these are the canonical sources this skill is built from (Unity 6000.5 Manual / Scripting API).

- [Unity Manual — Lighting](https://docs.unity3d.com/Manual/LightingOverview.html)
- [Unity Manual — Lighting reference](https://docs.unity3d.com/Manual/lighting-reference.html)
- [Scripting API — Light](https://docs.unity3d.com/ScriptReference/Light.html)
- [Scripting API — RenderSettings](https://docs.unity3d.com/ScriptReference/RenderSettings.html)

`LightingOverview.html` is the top-level landing page for the whole Lighting section: it fans out to Introduction to lighting, Lighting configuration workflow, Light sources, Direct and indirect lighting, Shadows, Reflections, Light Explorer, Lighting in URP vs. the Built-In Render Pipeline, and Optimize lighting. `lighting-reference.html` is the glossary/reference landing page: it fans out to the Lighting window reference, the Lighting Settings Asset Inspector reference, the Lightmap Parameters Asset Inspector reference, and Debug Draw Modes for lighting (`GIVis.html`). `light-sources-and-parameters.md` in this folder covers the Light-sources branch in depth; `direct-indirect-and-gi.md` covers the Direct-and-indirect-lighting/GI branch in depth. `Light` and `RenderSettings` are the two most central Scripting API entry points — `Light` for per-light parameters and behavior, `RenderSettings` for scene-wide ambient light, skybox, and fog. Other topic files in this folder link to specific Manual pages under `Manual/...` and specific Scripting API pages under `ScriptReference/...`; page slugs are stable across nearby Unity versions, so re-derive the exact version segment if the installed Editor version differs from 6000.5.

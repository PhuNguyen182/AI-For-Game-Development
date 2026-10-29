# Water, Ray Tracing, Path Tracing

Pages (17.5): `manual/WaterSystem-Overview.html`, `manual/water-use-the-water-system-in-your-project.html`, `manual/WaterSystem-scripting.html`, `manual/raytracing-requirements.html`, `manual/Ray-Tracing-Getting-Started.html`, `manual/Ray-Tracing-Path-Tracing.html`, `manual/path-tracing-limitations.html`.

## Water
- Surface types: Pool, River, Ocean-Sea-Lake; each has its own simulation scope and cost.
- The feature must be enabled in the pipeline configuration before any surface renders.
- Runtime queries and control: Water System scripting page.

## Ray and path tracing
- Ray tracing needs capable GPU hardware and a supported API; a PC/console target is necessary, not sufficient.
- Set up through the HDRP Wizard (`Window > Rendering`), which validates the project.
- Path tracing is a different renderer converging over frames, not a rasterizer quality setting.
- Path tracing does not support Local Volumetric Fog (see its limitations page for the full list).
- General ray tracing is likewise incompatible with volumetric fog.
- An unsupported combination shows as a missing effect, which reads as an authoring bug; check the limitation list first.

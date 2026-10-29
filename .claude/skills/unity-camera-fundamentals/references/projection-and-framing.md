# Projection, framing and depth precision

Source: [Camera component](https://docs.unity3d.com/Manual/class-Camera.html), [Physical Cameras](https://docs.unity3d.com/Manual/PhysicalCameras.html), [Camera API](https://docs.unity3d.com/ScriptReference/Camera.html).

Field of view is vertical, and depth precision is governed by the near plane. Neither is visible in the Inspector.

## Projection
- `orthographic`: no perspective divide; the projection for 2D and isometric.
- `orthographicSize`: half the vertical view height in world units; visible width is `orthographicSize * 2 * aspect`.
- `fieldOfView`: vertical angle in degrees; a portrait phone at the same value shows far less width than a landscape monitor.
- `aspect`: defaults to the screen's; an override not matching the viewport stretches the image instead of reframing.

## Physical camera and Gate Fit
- `usePhysicalProperties`: FOV derived from `focalLength` and `sensorSize`; use when framing is specified in lens terms or a fixed composition must survive several screen shapes.
- `gateFit` (sensor vs screen aspect disagree): Vertical keeps vertical framing and crops/extends horizontally; Horizontal the reverse; Fill shows the larger of the two; Overscan the smaller; None stretches.
- `focalLength` / `sensorSize`: millimetres; the same focal length on another sensor is another FOV, so state both.
- `lensShift`: offsets the frustum without rotating, keeping vertical lines parallel.

## Clip planes and precision
- `nearClipPlane`: dominant under perspective (precision is hyperbolic, most of the buffer is spent near the near plane). Raising it is the cheapest cure for distant z-fighting.
- `farClipPlane`: secondary; lowering it helps far less, though it culls geometry.
- Orthographic depth is linear, so the near-plane rule does not apply; problems there are about range.
- `clearFlags` / `backgroundColor`: Skybox, Solid Color, Depth Only, Nothing; meaningful only with camera ordering (see culling reference).

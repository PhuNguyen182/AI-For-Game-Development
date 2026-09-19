# Projection, Framing, and Depth Precision

Sources: [Camera component reference](https://docs.unity3d.com/Manual/class-Camera.html), [Physical Cameras](https://docs.unity3d.com/Manual/PhysicalCameras.html), [Camera API](https://docs.unity3d.com/ScriptReference/Camera.html).
Covers: SKILL.md §4 — **"Treat field of view as vertical and let the aspect ratio decide the width"**, **"Reach for the physical camera and Gate Fit when framing must survive several screen shapes"**, **"Push the near clip plane out before pulling the far plane in"**.

Two facts here cause most camera framing and precision problems, and neither
is visible in the Inspector. Unity's field of view is **vertical**, so the
horizontal extent is derived from the screen's aspect ratio and changes
between devices. And depth-buffer precision is governed overwhelmingly by the
**near** plane, not the far one, so the intuitive fix for distant z-fighting
is the wrong end of the range.

## Projection

| Property | What it decides | Source |
|---|---|---|
| `orthographic` | No perspective divide — parallel lines stay parallel and distance no longer affects size. The projection for 2D and isometric, and the reason a 3D scene can look like a diagram in it | [Camera component reference](https://docs.unity3d.com/Manual/class-Camera.html) |
| `orthographicSize` | **Half** the vertical view height in world units. The visible width is `orthographicSize * 2 * aspect`, so it is never a direct statement of how much of the level is on screen | [Camera.orthographicSize](https://docs.unity3d.com/ScriptReference/Camera-orthographicSize.html) |
| `fieldOfView` | The **vertical** angle in degrees. Horizontal coverage follows from the aspect ratio, which is why a portrait phone at the same value shows dramatically less width than a landscape monitor | [Camera.fieldOfView](https://docs.unity3d.com/ScriptReference/Camera-fieldOfView.html) |
| `aspect` | Defaults to the screen's, and can be overridden — but an override that does not match the viewport stretches the image rather than reframing it | [Camera.aspect](https://docs.unity3d.com/ScriptReference/Camera-aspect.html) |

## Physical camera and Gate Fit

| Property | What it decides | Source |
|---|---|---|
| `usePhysicalProperties` | Switches FOV to being derived from `focalLength` and `sensorSize`, in real lens terms. Useful when framing is specified by a cinematographer, and when a fixed composition must survive several screen shapes | [Physical Cameras](https://docs.unity3d.com/Manual/PhysicalCameras.html) |
| `gateFit` | What happens when the sensor's aspect and the screen's disagree — **Vertical** keeps vertical framing and crops or extends horizontally, **Horizontal** does the reverse, **Fill** shows the larger of the two, **Overscan** the smaller, **None** stretches. This is the actual control for cross-aspect framing, in place of branching on aspect ratio in script | [Physical Cameras](https://docs.unity3d.com/Manual/PhysicalCameras.html) |
| `focalLength` / `sensorSize` | Lens and sensor in millimetres; the same focal length on a different sensor is a different field of view, so both must be stated together | [Physical Cameras](https://docs.unity3d.com/Manual/PhysicalCameras.html) |
| `lensShift` | Offsets the frustum without rotating the camera — keeps vertical lines parallel while reframing, which rotation cannot do | [Physical Cameras](https://docs.unity3d.com/Manual/PhysicalCameras.html) |

## Clip planes and precision

| Property | What it decides | Source |
|---|---|---|
| `nearClipPlane` | The dominant term in depth precision under a perspective projection — precision is distributed hyperbolically, so most of the buffer is spent close to the near plane. Raising it is the cheapest recovery for distant z-fighting | [Camera.nearClipPlane](https://docs.unity3d.com/ScriptReference/Camera-nearClipPlane.html) |
| `farClipPlane` | The visible range, and a secondary precision factor. Reducing it helps far less than raising near does, though it does cull geometry | [Camera.farClipPlane](https://docs.unity3d.com/ScriptReference/Camera-farClipPlane.html) |
| Orthographic depth | Distributed **linearly** rather than hyperbolically, so the near-plane rule above does not apply — an orthographic camera's precision problems are about range, not distribution | [Camera component reference](https://docs.unity3d.com/Manual/class-Camera.html) |
| `clearFlags` / `backgroundColor` | Skybox, Solid Color, Depth Only, or Nothing. Only meaningful alongside camera ordering — see [culling-and-multi-camera.md](culling-and-multi-camera.md) | [Camera.clearFlags](https://docs.unity3d.com/ScriptReference/Camera-clearFlags.html) |

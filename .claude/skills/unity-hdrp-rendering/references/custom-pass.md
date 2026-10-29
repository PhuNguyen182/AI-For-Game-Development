# Custom Pass Volumes

Pages (17.5): `manual/Custom-Pass-Volume-Workflow.html`, `manual/Custom-Pass-Scripting.html`, `api/UnityEngine.Rendering.HighDefinition.CustomPassVolume.html`.

| Subject | Decides |
|---|---|
| `CustomPassVolume` | Holds one or more passes; volume-scoped, not attached to a renderer asset |
| Mode | Global: everywhere. Local: inside its collider. Camera: bound to one camera |
| Injection point | Where in the frame the pass runs; choose from what it must read and write |
| Priority | Orders several volumes affecting the same camera |
| Fade Radius | The only softening of a local volume's edge; custom pass volumes do not blend like regular Volumes, so an effect meant to blend needs it set deliberately |
| Scripted `CustomPass` | Subclass for passes the built-in types cannot express |
| `GetActivePassVolumes` | Lists volumes currently affecting rendering; use when a pass is not visibly running |

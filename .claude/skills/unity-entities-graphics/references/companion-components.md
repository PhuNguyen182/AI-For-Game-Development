# Companion Components — The Supported List & Its Cost

Source: [Companion Components](https://docs.unity3d.com/Packages/com.unity.entities.graphics@6.6/manual/companion-components.html).
Covers: SKILL.md §4 — **"Reach for a Companion Component only for a MonoBehaviour on the supported list"**.

The bridge that lets a fixed set of engine `MonoBehaviour`s stay attached to an
entity without becoming `IComponentData`. It is a bridge for those specific
engine systems, not a general ECS-to-MonoBehaviour interop mechanism.

| Subject | What it decides | Source |
|---|---|---|
| Supported list | `Light`, `ReflectionProbe`, `TextMesh`, `SpriteRenderer`, `ParticleSystem`, `VisualEffect`, and HDRP types such as `DecalProjector` and `LocalVolumetricFog` | [Companion Components](https://docs.unity3d.com/Packages/com.unity.entities.graphics@6.6/manual/companion-components.html) |
| Anything not on the list | **Silently stripped during baking** — a bespoke gameplay `MonoBehaviour` disappears with no error, which is what makes this the first thing to check when a script "stopped running" after conversion | [Companion Components](https://docs.unity3d.com/Packages/com.unity.entities.graphics@6.6/manual/companion-components.html) |
| Storage | Wrapped as `CompanionComponent<T>` so ECS queries can still filter on it | [Companion Components](https://docs.unity3d.com/Packages/com.unity.entities.graphics@6.6/manual/companion-components.html) |
| Access cost | Requires `foreach` iteration on the main thread; dereferencing the managed component cannot happen in a Burst job | [Companion Components](https://docs.unity3d.com/Packages/com.unity.entities.graphics@6.6/manual/companion-components.html) |
| Hierarchy | Not preserved — the companion becomes a root GameObject rather than a child of its original parent | [Companion Components](https://docs.unity3d.com/Packages/com.unity.entities.graphics@6.6/manual/companion-components.html) |

**Critical caveat**: the access cost scales with count. A handful of companion
lights iterated on the main thread is unremarkable; the same pattern across
thousands of entities reintroduces exactly the per-object managed cost ECS was
adopted to remove.

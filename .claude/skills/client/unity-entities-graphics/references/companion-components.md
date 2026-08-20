# Companion Components

Covers SKILL.md step 7 — when to bridge a non-ECS-convertible MonoBehaviour onto an entity, and what it costs.

## Manual
- [Companion Components](https://docs.unity3d.com/Packages/com.unity.entities.graphics@6.6/manual/companion-components.html) — lets an ordinary `MonoBehaviour` component stay attached to an entity without converting it to `IComponentData`, stored as a `CompanionComponent<T>` wrapper so ECS queries can filter on it.
  - **Supported components** (fixed list): `Light`, `ReflectionProbe`, `TextMesh`, `SpriteRenderer`, `ParticleSystem`, `VisualEffect`, and HDRP-specific components like `DecalProjector` and `LocalVolumetricFog`.
  - **Not on the list → stripped.** Any `MonoBehaviour` on the baked GameObject that isn't in the supported list is silently removed during baking.
  - **Hierarchy is not preserved** — a converted companion GameObject becomes a root GameObject, not a child under its original parent.
  - **Access cost**: querying a Companion Component requires `foreach()` iteration, not a Burst-compiled job — dereferencing the wrapped managed component requires main-thread managed code.

Use only when the MonoBehaviour genuinely can't be modeled as ECS data (per SKILL.md step 7) — it's a bridge for a fixed set of engine systems, not a general-purpose ECS/MonoBehaviour interop mechanism.

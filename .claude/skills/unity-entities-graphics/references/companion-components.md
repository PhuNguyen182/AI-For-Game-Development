# Companion Components

Source: `manual/companion-components.html`.

A bridge for a fixed set of engine MonoBehaviours, not general ECS-MonoBehaviour interop.

- Supported: `Light`, `ReflectionProbe`, `TextMesh`, `SpriteRenderer`, `ParticleSystem`, `VisualEffect`, HDRP types such as `DecalProjector` and `LocalVolumetricFog`.
- Anything else is silently stripped during baking; check this first when a script "stopped running" after conversion.
- Stored as `CompanionComponent<T>`, so queries can filter on it.
- Access needs main-thread `foreach`; the managed component cannot be dereferenced in a Burst job. Cost scales with count: thousands of companions reintroduce the per-object managed cost ECS removes.
- The hierarchy is lost: the companion becomes a root GameObject.

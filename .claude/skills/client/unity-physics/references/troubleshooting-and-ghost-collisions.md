# Troubleshooting & Ghost Collisions

Covers SKILL.md's ghost-collision guardrail (edge case 6).

## Manual
- [Troubleshooting](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/troubleshooting.html) — known issues: ghost collisions (see below), and static rigid bodies with parent transforms not updating collision detection when moved (fix: ensure `LocalToWorld` is current before physics systems run). Links to sample scenes and detailed sub-pages for each issue.
- [Ghost collisions](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/ghost-collisions.html) — spurious collisions at boundaries between adjacent colliders. Causes: shared vertices/edges between adjacent colliders evaluated independently, misaligned separating planes during edge transitions, discrete time steps letting fast-moving objects skip past correct contact detection, and high-triangle-count collider shapes. Mitigations: narrowphase contact modification (smooths interaction between connected colliders), detailed static-mesh collision processing across multiple frames, simplifying colliders (e.g. convex-hull approximation instead of raw mesh), smaller time steps, and Voronoi-region-based normal validation to ignore/adjust invalid contact normals.

Ghost collisions are the most common collision-detection artifact this engine's own docs call out — check collider simplicity and shared-edge geometry first before reaching for pipeline-level interception (`IContactsJob`, per [spatial-queries-and-events.md](spatial-queries-and-events.md)) to work around a specific case.

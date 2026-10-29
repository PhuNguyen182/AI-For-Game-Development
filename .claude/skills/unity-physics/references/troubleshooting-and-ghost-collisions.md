# Ghost collisions and stale static transforms

Sources (under `manual/`): `ghost-collisions.html`, `troubleshooting.html`.

Neither failure logs anything; check collider geometry and transform order before simulation code.

## Ghost collision causes
- Shared vertices/edges between adjacent colliders are evaluated independently, so a seam between flat tiles can contact (most common).
- Misaligned separating planes at edge transitions give a body an unexpected normal.
- Discrete time steps with fast bodies skip contact detection.
- High-triangle-count shapes add edges to catch on and cost per contact.

## Mitigations, cheapest first
1. Simplify the collider: convex-hull approximation instead of raw mesh.
2. Smaller time steps (fast-body case; global cost).
3. Narrowphase contact modification (`IContactsJob`) to smooth connected colliders.
4. Voronoi-region normal validation to ignore or adjust invalid normals.
5. Multi-frame static-mesh processing to spread detailed static collision work.

## Static body under a moving parent stops colliding
Collision detection did not update. Ensure its `LocalToWorld` is current before the physics systems run.

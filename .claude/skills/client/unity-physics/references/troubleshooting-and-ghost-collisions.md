# Troubleshooting — Ghost Collisions & Stale Static Transforms

Sources: [Troubleshooting](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/troubleshooting.html), [Ghost collisions](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/ghost-collisions.html).
Covers: SKILL.md §4 — **"Treat a boundary artifact as a collider-geometry problem first"**.

The two documented failure modes this engine calls out by name, with causes
ordered so the cheap fixes come first. Contact-level interception is the last
resort, not the first — see [spatial-queries-and-events.md](spatial-queries-and-events.md).

## Ghost collisions

| Cause | What it decides | Source |
|---|---|---|
| Shared vertices or edges between adjacent colliders | Each is evaluated independently, so a seam between two flat tiles can generate a contact — the most common source | [Ghost collisions](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/ghost-collisions.html) |
| Misaligned separating planes during edge transitions | A body crossing from one collider to the next meets an unexpected normal | [Ghost collisions](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/ghost-collisions.html) |
| Discrete time steps with fast bodies | Contact detection is skipped past entirely | [Ghost collisions](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/ghost-collisions.html) |
| High-triangle-count shapes | More edges to catch on, and more cost per contact | [Ghost collisions](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/ghost-collisions.html) |

| Mitigation | What it decides | Source |
|---|---|---|
| Simplify the collider | Convex-hull approximation instead of raw mesh — the cheapest and most durable fix | [Ghost collisions](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/ghost-collisions.html) |
| Smaller time steps | Helps the fast-body case specifically, at a global cost | [Ghost collisions](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/ghost-collisions.html) |
| Narrowphase contact modification | Smooths interaction between connected colliders; an `IContactsJob`-level fix | [Ghost collisions](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/ghost-collisions.html) |
| Voronoi-region normal validation | Ignores or adjusts invalid contact normals | [Ghost collisions](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/ghost-collisions.html) |
| Multi-frame static-mesh processing | Spreads detailed static collision work across frames | [Ghost collisions](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/ghost-collisions.html) |

## Static bodies under moving parents

| Symptom | What it decides | Source |
|---|---|---|
| A static body moved by its parent stops colliding | Collision detection did not update — ensure `LocalToWorld` is current before the physics systems run | [Troubleshooting](https://docs.unity3d.com/Packages/com.unity.physics@6.6/manual/troubleshooting.html) |

**Critical caveat**: both failures present as "physics is broken" rather than as
an error. Neither logs anything, so the first diagnostic move is checking
collider geometry and transform ordering, not reading simulation code.

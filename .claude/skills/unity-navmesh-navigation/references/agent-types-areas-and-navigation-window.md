# Agent Types, Areas and Costs

Project-wide settings (Navigation window). Which agent may use which area is a game rule (`csharp-engineer`).

## Agent types
An agent is simulated as an upright cylinder regardless of model; each type needs its own baked mesh.

| Setting | Decides |
|---|---|
| Radius | Clearance from walls/ledges and basis of default voxel size; the field that most changes what bakes navigable |
| Height | Vertical clearance under geometry |
| Step Height | Tallest step walked without a link (stairs bake walkable or not) |
| Max Slope | Steepest navigable ramp |
| Drop Height, Jump Distance | Limits for auto-generated links; a wider gap yields no connection |
| Base Offset | Cylinder offset from the pivot for models not pivoted at the feet |

## Areas and costs
- Built-in areas: Walkable, Not Walkable, Jump, plus a bounded set of custom slots.
- **Cost** multiplies traversed distance: it biases paths away from an area but never forbids it. A high cost still permits the route when nothing cheaper exists, so use an area mask for a hard restriction.
- **Overlap**: the higher-indexed area generally wins, except Not Walkable always wins.
- **Agent area mask** restricts traversable areas (asymmetric routes, e.g. a door only some agents use). A link whose area is outside the mask is unusable and reports nothing ([navmesh-links.md](navmesh-links.md)).
- Cost scopes (global, per agent, per query filter) are not interchangeable: [navmesh-queries-and-pathfinding-api.md](navmesh-queries-and-pathfinding-api.md).

## Height Mesh
Supplementary surface that places agents accurately on stairs and slopes, where the simplified mesh leaves them floating or sunk. Costs bake time and memory; enable it where the error is visible.

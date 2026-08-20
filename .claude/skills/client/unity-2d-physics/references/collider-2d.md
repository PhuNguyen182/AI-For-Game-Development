# Collider2D — Shapes & Collision Events

Covers SKILL.md step 4 (choosing a `Collider2D` shape, trigger vs. solid, and the 2D layer collision matrix).

## Overview

A `Collider2D` is the component that defines which area of a GameObject participates in Unity's built-in 2D (Box2D-backed) physics — "the collider 2D defines which area of the GameObject has collision and can interact with other colliders in the scene." A `Collider2D` is typically paired with a `Rigidbody2D` (`Collider2D.attachedRigidbody`) so the shape can be simulated or sensed by the physics engine; a `Collider2D` with no `Rigidbody2D` on it or its parent behaves as static, immovable geometry. 2D and 3D colliders cannot be mixed on the same GameObject hierarchy — "You can't use 3D GameObjects with 2D colliders, or 2D GameObjects with 3D colliders."

A collider becomes a **trigger** when its `isTrigger` property is enabled ("Is this collider configured as a trigger?"): it stops producing a physical collision response and instead reports overlap through the `OnTrigger2D` callback family, while a non-trigger ("solid") collider produces a physical response and reports through the `OnCollision2D` family. Rigidbody2D body type selection (Dynamic/Kinematic/Static) and exactly which body-type/trigger pairings generate which callbacks are covered in [rigidbody-2d.md](rigidbody-2d.md) — this file focuses on the collider shapes themselves and the event data they produce.

## Manual

| Page | URL | Covers |
|---|---|---|
| Collider 2D landing | https://docs.unity3d.com/Manual/2d-physics/collider/collider-2d-landing.html | What a Collider2D is, links to every shape reference, 2D/3D non-mixing constraint |
| Box Collider 2D | https://docs.unity3d.com/Manual/2d-physics/collider/box-collider-2d-reference.html | Rectangular collider: size, edge radius, auto tiling |
| Circle Collider 2D | https://docs.unity3d.com/Manual/2d-physics/collider/circle-collider-2d-reference.html | Circular collider: radius, offset |
| Polygon Collider 2D | https://docs.unity3d.com/Manual/2d-physics/collider/polygon-collider-2d-reference.html | Freeform enclosed-shape collider: edit collider, Delaunay mesh |
| Edge Collider 2D | https://docs.unity3d.com/Manual/2d-physics/collider/edge-collider-2d-reference.html | Open line-segment collider: edge radius, adjacent points |
| Capsule Collider 2D landing | https://docs.unity3d.com/Manual/2d-physics/collider/capsule-collider/capsule-collider-2d-landing.html | Capsule collider: size, direction, offset, edge radius |
| Composite Collider 2D landing | https://docs.unity3d.com/Manual/2d-physics/collider/composite-collider/composite-collider-2d-landing.html | Merging multiple "Used By Composite" colliders into one efficient shape |

## Collider2D shapes

| Shape | Component | Description | Performance/use-case note |
|---|---|---|---|
| Box | `BoxCollider2D` | A rectangle with a defined position, width, and height in the sprite's local coordinate space. Supports rounded corners via edge radius and auto-updates with tiled sprites via auto tiling. | Simple primitive shape — prefer this for rectangular/square sprites before reaching for Polygon. |
| Circle | `CircleCollider2D` | A circular collision shape with a defined position and radius in local space. | Simple primitive shape — cheapest option for round sprites/objects. |
| Capsule | `CapsuleCollider2D` | A cylindrical shaped collision area with round ends, configured by size, direction, offset, and edge radius. | Good middle ground for character bodies/elongated objects where Box or Circle alone doesn't fit the silhouette. |
| Polygon | `PolygonCollider2D` | A freeform shape made of connected line segments that must completely enclose an area. Supports an optional Delaunay triangulation step for more accurate collision meshes on complex shapes. | Use for complex sprite silhouettes that Box/Circle/Capsule can't represent; enabling the Delaunay mesh "can improve collision shapes for complex shapes, but can reduce performance" — only turn it on when the accuracy is actually needed. |
| Edge | `EdgeCollider2D` | An adjustable outline made of line segments that does not need to enclose an area — for open-ended boundaries. Edge colliders can't collide with other edge colliders, regardless of body type or trigger settings. | Use for open surfaces like cliffs, walls, or platforms where no enclosed area is required. |
| Composite | `CompositeCollider2D` | Merges other `Collider2D` shapes (Box and/or Polygon, each with "Used By Composite" enabled) into a single generated collider, with configurable geometry type and generation type. | Use when many adjacent tile/sprite colliders (e.g. a tilemap) would otherwise produce many separate small colliders — consolidating them into one Composite Collider 2D is more efficient than simulating each individually. |

Per `performance-and-algorithms.md`'s "simplest collider shape" rule: prefer Circle/Box/Capsule over Polygon, and Polygon over a per-pixel-accurate custom shape, wherever the sprite's silhouette allows.

## Collider2D component APIs

### Collider2D (base class)

| Member | Description |
|---|---|
| `attachedRigidbody` | The Rigidbody2D attached to the Collider2D. |
| `bounceCombine` | The bounciness combine mode used by the Collider2D. |
| `bounciness` | The bounciness used by the Collider2D. |
| `bounds` | The world space bounding area of the collider. |
| `callbackLayers` | Reports collision/trigger callbacks for contacts with other Collider2D objects. |
| `composite` | Access to the attached CompositeCollider2D component. |
| `compositeCapable` | Indicates if this Collider2D is capable of being composited by a CompositeCollider2D. |
| `compositeOperation` | Operation mode used when this collider is merged by a CompositeCollider2D. |
| `compositeOrder` | The composite operation order to be used when a CompositeCollider2D is used. |
| `contactCaptureLayers` | The layers of other Collider2D involved in contacts with this Collider2D. |
| `contactMask` | Calculates the effective LayerMask for determining Collider2D contact capability. |
| `density` | The density of the collider, used to calculate its mass. |
| `errorState` | The error state that indicates the state of the physics shapes. |
| `excludeLayers` | Layers to exclude from contact decisions. |
| `forceReceiveLayers` | The Layers that this Collider2D can receive forces from. |
| `forceSendLayers` | The Layers that this Collider2D is allowed to send forces to. |
| `friction` | The friction used by the Collider2D. |
| `frictionCombine` | The friction combine mode used by the Collider2D. |
| `includeLayers` | Layers to include in contact decisions. |
| `isTrigger` | Is this collider configured as a trigger? |
| `layerOverridePriority` | Priority used when there is a conflicting contact decision. |
| `localToWorldMatrix` | The transformation matrix used to transform the Collider physics shapes. |
| `offset` | The local offset of the collider geometry. |
| `shapeCount` | The number of active PhysicsShape2D the Collider2D is currently using. |
| `sharedMaterial` | The PhysicsMaterial2D that is applied to this collider. |
| `usedByEffector` | Whether the collider is used by an attached effector or not. |
| `CanContact(...)` | Determines if both Colliders can ever come into contact. |
| `Cast(...)` | Casts the collider shape into the scene from the collider's current position. |
| `ClosestPoint(Vector2 position)` | Returns a point on the perimeter of this Collider that is closest to the specified position. |
| `CreateMesh(...)` | Creates a planar mesh matching the collider geometry. |
| `Distance(Collider2D collider)` | Calculates the minimum separation between colliders. |
| `GetContactColliders(...)` | Retrieves colliders in contact, filtered by contactFilter. |
| `GetContacts(...)` | Retrieves the contact points for the collider, filtered by contactFilter. |
| `GetShapeBounds(...)` | Retrieves bounds for all PhysicsShape2D created by the collider. |
| `GetShapeHash(...)` | Generates a hash value based on the collider geometry. |
| `GetShapes(...)` | Gets all the PhysicsShape2D used by the Collider2D. |
| `IsTouching(...)` | Checks whether the collider is touching another collider. |
| `IsTouchingLayers(LayerMask layerMask)` | Checks whether this collider is touching any colliders on the specified layerMask. |
| `Overlap(...)` | Overlap detection method. |
| `OverlapPoint(Vector2 point)` | Checks if a collider overlaps a point in space. |
| `Raycast(...)` | Casts a ray from the collider's position, ignoring the collider itself. |

### BoxCollider2D

| Member | Description |
|---|---|
| `size` | The width and height of the rectangle. |
| `edgeRadius` | Controls the radius of all edges created by the collider. |
| `autoTiling` | Determines whether the BoxCollider2D's shape is automatically updated based on a SpriteRenderer's tiling properties. |

### CircleCollider2D

| Member | Description |
|---|---|
| `radius` | Radius of the circle. |

### CapsuleCollider2D

| Member | Description |
|---|---|
| `size` | The width and height of the capsule area. |
| `direction` | The direction that the capsule sides can extend. |

### PolygonCollider2D

| Member | Description |
|---|---|
| `points` | Corner points that define the collider's shape in local space. |
| `pathCount` | The number of paths in the polygon. |
| `autoTiling` | Determines whether the PolygonCollider2D's shape is automatically updated based on a SpriteRenderer's tiling properties. |
| `useDelaunayMesh` | When true, the Collider uses an additional Delaunay triangulation step to produce the Collider mesh. |
| `CreateFromSprite()` | Creates polygon shapes using the selected sprite. |
| `CreatePrimitive(...)` | Creates a regular primitive polygon with the specified number of sides. |
| `GetPath(int index)` | Gets a path from the Collider by its index. |
| `GetTotalPointCount()` | Returns the total number of points in the polygon across all paths. |
| `SetPath(...)` | Defines a path by its constituent points. |

### EdgeCollider2D

| Member | Description |
|---|---|
| `points` | Gets or sets the points defining multiple continuous edges. |
| `pointCount` | Gets the number of points. |
| `edgeCount` | Gets the number of edges. |
| `edgeRadius` | Controls the radius of all edges created by the collider. |
| `adjacentStartPoint` | Defines the position of a virtual point adjacent to the start point of the EdgeCollider2D. |
| `adjacentEndPoint` | Defines the position of a virtual point adjacent to the end point of the EdgeCollider2D. |
| `useAdjacentStartPoint` | Controls collision normal calculation at the start point using adjacentStartPoint. |
| `useAdjacentEndPoint` | Controls collision normal calculation at the end point using adjacentEndPoint. |
| `GetPoints(...)` | Gets all the points that define a set of continuous edges. |
| `SetPoints(...)` | Sets all the points that define a set of continuous edges. |
| `Reset()` | Resets the collider to a single edge consisting of two points. |

### CompositeCollider2D

| Member | Description |
|---|---|
| `geometryType` | Specifies the type of geometry the Composite Collider should generate. |
| `generationType` | Specifies when to generate the Composite Collider geometry. |
| `edgeRadius` | Controls the radius of all edges created by the Collider. |
| `offsetDistance` | Combines vertices between shapes within a specified distance during compositing. |
| `vertexDistance` | Controls the minimum distance allowed between generated vertices. |
| `useDelaunayMesh` | Determines whether an additional Delaunay triangulation step is applied. |
| `pathCount` | The number of paths in the Collider. |
| `pointCount` | Gets the total number of points in all the paths within the Collider. |
| `GenerateGeometry()` | Regenerates the Composite Collider geometry. |
| `GetCompositedColliders(...)` | Retrieves the colliders that have been merged into this composite. |
| `GetPath(int index)` | Gets a path from the Collider by its index. |
| `GetPathPointCount(int index)` | Retrieves the vertex count for a specific path by its index. |

## PhysicsMaterial2D

A `Collider2D` reads its friction and bounciness either from a directly assigned `PhysicsMaterial2D` (`Collider2D.sharedMaterial`) or, if unset, from `Collider2D.friction`/`Collider2D.bounciness`/the combine-mode properties listed above. Assign a shared `PhysicsMaterial2D` asset when several colliders need the same surface behavior (ice, rubber, etc.) instead of tuning each collider's friction/bounciness individually. The full `PhysicsMaterial2D` property/API tables and combine-mode reference live in the sibling [physics-material-2d.md](physics-material-2d.md) file — refer there for details.

## Collision & trigger events

| Member | Description |
|---|---|
| `OnCollisionEnter2D(Collision2D collision)` | Sent when an incoming collider makes contact with this object's collider (2D physics only). |
| `OnCollisionStay2D(Collision2D collision)` | Sent each frame where an incoming collider is touching this object's collider (2D physics only). |
| `OnCollisionExit2D(Collision2D collision)` | Sent when a collider stops touching another collider (2D physics only). |
| `OnTriggerEnter2D(Collider2D collision)` | Sent when another object enters a trigger collider attached to this object (2D physics only). |
| `OnTriggerStay2D(Collider2D collision)` | Sent each frame where another object is inside a trigger collider attached to this object (2D physics only). |
| `OnTriggerExit2D(Collider2D collision)` | Sent when another object leaves a trigger collider attached to this object (2D physics only). |

## Collision message data

`Collision2D` class:

| Member | Description |
|---|---|
| `collider` | The incoming Collider2D involved in the collision with the otherCollider. |
| `otherCollider` | The other Collider2D involved in the collision with the collider. |
| `rigidbody` | The incoming Rigidbody2D involved in the collision with the otherRigidbody. |
| `otherRigidbody` | The other Rigidbody2D involved in the collision with the rigidbody. |
| `gameObject` | The incoming GameObject involved in the collision. |
| `transform` | The Transform of the incoming object involved in the collision. |
| `enabled` | Indicates whether the collision response or reaction is enabled or disabled. |
| `relativeVelocity` | The relative linear velocity of the two colliding objects (read-only). |
| `contactCount` | The number of contacts for this collision. |
| `contacts` | The specific points of contact with the incoming Collider2D. |
| `GetContact(int index)` | Gets the contact point at the specified index. |
| `GetContacts(...)` | Retrieves all contact points for contacts between collider and otherCollider. |

`ContactPoint2D` struct:

| Field | Description |
|---|---|
| `point` | The point of contact between the two colliders, in world space. |
| `normal` | Surface normal at the contact point. |
| `separation` | The distance between the colliders at the contact point. |
| `normalImpulse` | The impulse applied at the contact point along `ContactPoint2D.normal`. |
| `tangentImpulse` | The impulse applied at the contact point, perpendicular to the normal. |
| `relativeVelocity` | The relative velocity of the two colliders at the contact point (read-only). |
| `collider` | The incoming Collider2D involved in the collision with the otherCollider. |
| `otherCollider` | The other Collider2D involved in the collision with the collider. |
| `rigidbody` | The incoming Rigidbody2D involved in the collision with the otherRigidbody. |
| `otherRigidbody` | The other Rigidbody2D involved in the collision with the rigidbody. |
| `friction` | The effective friction used for the ContactPoint2D. |
| `bounciness` | The effective bounciness used for the ContactPoint2D. |
| `enabled` | Indicates whether the collision response or reaction is enabled or disabled. |

## 2D layer collision matrix

| Member | Description |
|---|---|
| `Physics2D.IgnoreLayerCollision(int layer1, int layer2, bool ignore)` | Chooses whether to detect or ignore collisions between a specified pair of layers. |
| `Physics2D.GetIgnoreLayerCollision(int layer1, int layer2)` | Checks whether collisions between the specified layers are ignored or not. |
| `Physics2D.GetLayerCollisionMask(int layer)` | Gets the collision layer mask that indicates which layer(s) the specified layer can collide with. |
| `Physics2D.SetLayerCollisionMask(int layer, int layerMask)` | Sets the collision layer mask that indicates which layer(s) the specified layer can collide with. |

Per `performance-and-algorithms.md`'s Physics guidance: prune the layer collision matrix (via the Physics2D settings inspector, or these `Physics2D` calls) to skip pairs that should never interact, instead of filtering them out with runtime `if` checks inside `OnCollision2D`/`OnTrigger2D` callbacks.

For Rigidbody2D body types and collision detection mode, see [rigidbody-2d.md](rigidbody-2d.md). For friction/bounciness configuration, see [physics-material-2d.md](physics-material-2d.md).

# Spawning — Spawn/Despawn, Prefab Handler, Pooling, Visibility

Sources — `manual/`: basics/object-spawning.html, advanced-topics/network-prefab-handler.html, advanced-topics/object-pooling.html, basics/object-visibility.html, basics/spawning-synchronization.html, basics/deferred-despawning.html. `api/Unity.Netcode.`: NetworkObject, NetworkSpawnManager, NetworkPrefabHandler, INetworkPrefabInstanceHandler, NetworkPrefabInstanceHandlerWithData-1, NetworkPrefab, NetworkPrefabs, NetworkPrefabsList, NetworkPrefabOverride, LocalDeferMode, SpawnStateException, VisibilityChangeException (each `.html`).

Prefab composition, ownership and `SpawnWithOwnership`: [core-architecture.md](core-architecture.md).

## Spawn and despawn
| Subject | Fact that decides |
|---|---|
| `Spawn(bool destroyWithScene = false)` | `false` survives scene unload; `true` dies with its scene |
| `Despawn(bool destroy = true)` | `false` removes it from all clients but keeps the local GameObject — the pooling hook |
| `SpawnAsPlayerObject(ulong clientId, bool destroyWithScene = false)` | Registers it as that client's player object |
| `NetworkSpawnManager.InstantiateAndSpawn(NetworkObject prefab, ulong ownerClientId = ServerClientId, bool destroyWithScene = false, bool isPlayerObject = false, bool forceOverride = false, Vector3 position = default, Quaternion rotation = default)` | One-call instantiate + spawn that resolves prefab overrides; `forceOverride` bypasses them |
| Who may spawn | CS: server/host only. DA: any client, which becomes the authority |
| Child GameObjects | Never deactivate them around `Spawn`/`Despawn` — inactive children are excluded and their `NetworkBehaviour`s lose the association; disable components instead |
| In-scene placed | Spawn automatically with scene management; no `Spawn()` call |
| Spawn latency | CS client-requested spawn = Rpc → server spawns → message back, visibly lagging local motion. DA: the client spawns locally at the exact position |

**Caveat:** a raw `Object.Destroy` on a `NetworkObject` from a non-authority peer throws — use `Despawn` or the handler's `Destroy`.

## Prefab handler = pooling
There is no pooling API: a pool is an `INetworkPrefabInstanceHandler` whose `Instantiate` reactivates a pooled instance and whose `Destroy` deactivates and returns it.

| Subject | Fact that decides |
|---|---|
| `Instantiate(ulong ownerClientId, Vector3 position, Quaternion rotation) : NetworkObject` | Runs on non-authority clients only, once per spawn; return `null` on failure. The authority instantiates and spawns in its own code |
| `Destroy(NetworkObject)` | Server/authority on destroy or `Despawn(true)`; clients on the destroy message. Not called for `Despawn(false)`. Owns all cleanup — NGO doesn't clean up a failed or partial instance |
| `PrefabHandler.AddHandler(uint hash \| NetworkObject \| GameObject, INetworkPrefabInstanceHandler)` / `RemoveHandler(same keys)` | Register at startup, before the prefab's first spawn |
| `SetInstantiationData<T>(NetworkObject \| GameObject, T) where T : struct, INetworkSerializable` | Authority, before `Spawn()`; received by `NetworkPrefabInstanceHandlerWithData<T>.Instantiate(..., T instantiationData)`; `default(T)` if never set |
| `AddNetworkPrefab` / `RemoveNetworkPrefab(GameObject)` | Prefab bookkeeping only, separate from handlers |
| `GetNetworkPrefabOverride(GameObject) : GameObject` | Which prefab actually spawns once overrides apply |
| `RegisterHostGlobalObjectIdHashValues(GameObject source, List<GameObject> overrides)` | Makes a host resolve overrides identically in its server and client roles |

**Caveat:** default `Despawn(true)` on a pooled object routes into `Destroy`; `Despawn(false)` skips it. Write `Destroy` as return-to-pool or the pool is defeated.

## Prefab registration
| Subject | Fact that decides |
|---|---|
| `NetworkPrefab` | `Prefab`, `Override`, `SourcePrefabToOverride`, `SourceHashToOverride`, `OverridingTargetPrefab`; read-only `SourcePrefabGlobalObjectIdHash`/`TargetPrefabGlobalObjectIdHash` |
| `NetworkPrefabOverride` | `None`; `Prefab` — direct source reference; `Hash` — source asset absent from the client build |
| `NetworkPrefabs` (on `NetworkConfig`) | `Prefabs`, `Add`/`Remove`, `Contains(NetworkPrefab \| GameObject)`, `Initialize(bool)` |
| `NetworkPrefabsList` (ScriptableObject) | One shared set for several `NetworkManager`s/scenes; mutate via its `Add`/`Remove`, never `PrefabList` |

## `NetworkManager.SpawnManager` lookups
| Subject | Fact that decides |
|---|---|
| `SpawnedObjects` / `SpawnedObjectsList` | `Dictionary<ulong, NetworkObject>` by `NetworkObjectId` / `HashSet<NetworkObject>` — query these instead of a hand-kept list |
| `GetClientOwnedObjects(ulong) : NetworkObject[]` | Backed by `OwnershipToObjectsTable` (client id → object id → object) |
| `GetPlayerNetworkObject(ulong)` / `GetPlayerNetworkObjects(ulong) : List<NetworkObject>` / `GetLocalPlayerObject()` | Local lookup returns `null` until spawned. The plural returns a list "if more than one are assigned", but the manual allows one PlayerObject per client — treat `NetworkClient.PlayerObject` as primary |
| `GetConnectedPlayers() : List<ulong>` / `PlayerObjects` (DA) | Connected ids / flat list of known player objects |

## Visibility
| Subject | Fact that decides |
|---|---|
| `CheckObjectVisibility` (`bool VisibilityDelegate(ulong clientId)`) | Unset → visible to all. Assign server-side (`OnNetworkSpawn` when `IsServer`); evaluated on spawn, on client connect and on `NetworkShow` |
| `NetworkShow` / `NetworkHide(ulong clientId)`, static `List<NetworkObject>` overloads | Server only; spawn or destroy that client's clone and start or stop its traffic. Query with `IsNetworkVisibleTo(ulong)` |
| `SpawnWithObservers = false` before `Spawn()` | Starts invisible to everyone |
| `SpawnDelegate` (`bool (ulong clientId)`) | Separate delegate gating the spawn per client |
| `SpawnStateException` / `VisibilityChangeException` | Spawn-only operation before `Spawn()` / a Show or Hide failed (conditions undocumented) |

## Deferred despawn (DA only)
| Subject | Fact that decides |
|---|---|
| `DeferDespawn(int tickOffset, bool destroy = true)` | Non-authority instances despawn `tickOffset` ticks after the local tick — lets VFX or interpolation finish |
| `NetworkBehaviour.OnDeferringDespawn(int despawnTick)` | Authority sets final `NetworkVariable` state here; others see it via `OnValueChanged` |
| `OnDeferedDespawnCompleteDelegateHandler` | `bool ()` — `false` withholds the despawn |

**Caveat:** `LocalDeferMode` (`Default` = `SendImmediate`; `Defer` — next tick; `SendImmediate`) sets local Rpc execution timing via `RpcSendParams`; it is unrelated to `DeferDespawn`, which has no `LocalDeferMode` overload in 2.13.

Unverified: cross-client spawn ordering, late-joiner spawn sequencing and the spawn payload are undocumented — confirm in a multi-client run.

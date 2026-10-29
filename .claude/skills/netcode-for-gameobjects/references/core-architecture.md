# Core Architecture — Topology, Ownership, NetworkManager, NetworkObject, NetworkBehaviour

Sources — `manual/`: [topo] terms-concepts/network-topologies.html, [auth] terms-concepts/authority.html, [own] terms-concepts/ownership.html, [noown] components/core/networkobject-ownership.html, [listen] learn/listenserverhostarchitecture.html, [nm] components/core/networkmanager.html, [appr] basics/connection-approval.html, [max] basics/maxnumberplayers.html, [player] components/core/playerobjects.html, [no] components/core/networkobject.html, [parent] advanced-topics/networkobject-parenting.html, [nb] components/core/networkbehaviour.html, [nbsync] components/core/networkbehaviour-synchronize.html, [nbown] components/core/networkbehaviour-ownership.html, [nt] components/helper/networktransform.html. `api/Unity.Netcode.`: NetworkManager, NetworkConfig, NetworkObject, NetworkBehaviour, NetworkClient, PendingClient, NetworkManager.ConnectionApprovalRequest/Response, NetworkTopologyTypes (each `.html`).

## Topology
| Subject | Fact that decides |
|---|---|
| `NetworkConfig.NetworkTopology` | `NetworkTopologyTypes.ClientServer` or `.DistributedAuthority`; project-wide, set before anything else is wired |
| Client-Server, dedicated server | Sole authority, most cheat-resistant, enables prediction with rollback; highest hosting cost |
| Client-Server, listen server/host | No infra cost, but the host's connection and CPU degrade everyone, the host sees all world data, the session ends when the host leaves; manual's fit: under 12 players, non-persistent worlds [listen] |
| Distributed Authority | No simulating server: the CMB service (`NetworkConfig.UseCMBService`) routes state and each client simulates what it owns. No server cost, simple synced spawning, but trusts clients — not for competitive or cheat-sensitive games [topo]. Specifics: [distributed-authority.md](distributed-authority.md) |

## Authority and ownership
| Subject | Fact that decides |
|---|---|
| `HasAuthority` | Check before authoritative logic; resolves to "is server" in Client-Server, "is owner" in DA. A non-authority asks: Rpc to the server (CS), request to the owner (DA) |
| `IsClient` | True on the host too — remote-client-only logic needs `!IsHost`, or it double-runs on host builds |
| DA state storage | Must be `NetworkVariable<T>`: DA forces owner-write/everyone-read, which is what survives disconnects and ownership transfers [auth] |
| Ownership in Client-Server | Server keeps authority whoever owns. Ownership matters only where configured owner-authoritative: `NetworkTransform` owner mode, `AllowOwnerToParent`, `NetworkVariableWritePermission.Owner` [own] |
| Ownership in DA | Owner is always the authority; changes gated by `OwnershipStatus` ([distributed-authority.md](distributed-authority.md)) |
| Default owner of `Spawn()` | Server in CS, the caller in DA — the same call means different things [noown] |
| `ChangeOwnership(ulong)` / `RemoveOwnership()` | CS: server only; `RemoveOwnership` (back to server) is CS-only. DA: current authority, may fail per `OwnershipStatus` |
| `SpawnWithOwnership(ulong clientId, bool destroyWithScene = false)` | Spawner is only a limited "spawn authority", not owner — owner checks don't run there. To touch the object first: `Spawn()` → adjust → `ChangeOwnership()` |
| `SetOwnershipLock(bool)` / `IsOwnershipLocked` | Blocks every ownership change while locked |
| `IsOwner` / `IsOwnedByServer` / `HasAuthority` | Valid only once `IsSpawned`. A `NetworkBehaviour`'s owner is its `NetworkObject`'s owner |

## NetworkManager and NetworkConfig
| Subject | Fact that decides |
|---|---|
| `StartServer/StartHost/StartClient()` | Return `bool`. Never call from any `Awake()` — `SceneManager`/`SpawnManager` are valid only once `IsListening` [nm] |
| `Shutdown(bool discardMessageQueue = false)` | `true` drops queued outbound messages instead of flushing |
| `DisconnectClient(ulong clientId, string reason = null)` | Server only; client reads `NetworkManager.DisconnectReason` |
| `OnTransportFailure` | Transport-level failure; hook failure UI/reconnect here, separate from `OnConnectionEvent` |
| `LocalClientId` / `ConnectedClientsIds` | `LocalClientId` = server id when `IsServer`; `ConnectedClientsIds` is the cheap count/list vs the `ConnectedClients` dictionary |
| `TickRate` (`uint`) | Default 30 [nt]; drives `NetworkVariable` flush and Rpc batching |
| `ForceSamePrefabs` | Rejects clients whose prefab list differs — mismatch is the classic "works on host, fails in client build" |
| `ProtocolVersion` (`ushort`) | Rejects clients built against an incompatible version |
| `RecycleNetworkIds` / `NetworkIdRecycleDelay` | Reuse of despawned ids after a delay; matters in long, spawn-heavy sessions |
| `EnsureNetworkVariableLengthSafety` | Boundary checks paid in CPU and bandwidth |
| `EnableSceneManagement` | `NetworkSceneManager` owns loads; player objects spawn after initial scene sync, not on approval |
| `AutoSpawnPlayerPrefabClientSide` | Required for DA's `OnFetchLocalPlayerPrefabToSpawn` path |

## Connection approval (Client-Server only)
| Subject | Fact that decides |
|---|---|
| Enable | `ConnectionApproval = true` **and** assign `ConnectionApprovalCallback`; the flag alone still auto-approves |
| Callback | `void (NetworkManager.ConnectionApprovalRequest request, NetworkManager.ConnectionApprovalResponse response)` |
| Request | `ClientNetworkId` (`ulong`), `Payload` (`byte[]` from the client's `NetworkConfig.ConnectionData`, set before `StartClient()`) |
| Response | `Approved`, `CreatePlayerObject`, `PlayerPrefabHash` (`uint?`, null → default prefab), `Position`/`Rotation` (nullable, null → prefab transform), `Pending` (defer for async checks), `Reason` (sent only when denied) |
| Pending | Tracked as `PendingClient` (`ClientId`, `ConnectionState`); dropped after `NetworkConfig.ClientConnectionBufferTimeout`. The server silently ignores that client's other messages until approved — early Rpcs vanish |
| Max players | No `MaxPlayers` field: in the callback compare `ConnectedClientsIds.Count` to a constant and deny; `Reason` is the only feedback. With Relay, keep the host's max-peer setting equal, or failures look unrelated [max] |

## Player objects
| Subject | Fact that decides |
|---|---|
| Count | One `PlayerObject` per client at a time |
| Spawn | Auto ("Create Player Prefab" + `NetworkConfig.PlayerPrefab`), manual `SpawnAsPlayerObject(clientId)`, or deferred to a `NetworkBehaviour` |
| Access | Local: `NetworkManager.LocalClient.PlayerObject`; server: `ConnectedClients[clientId].PlayerObject` |
| DA | `AutoSpawnPlayerPrefabClientSide` + `OnFetchLocalPlayerPrefabToSpawn`, no approval flow |

**Caveat:** disable `PlayerInput`/`CharacterController` on the player prefab and enable them only on the local client's own player object, or every client reads input for the newest instance.

## NetworkObject
| Subject | Fact that decides |
|---|---|
| Composition | Exactly one `NetworkObject`, at the prefab root, never nested; needs ≥1 `NetworkBehaviour`; cannot be subclassed; ordered before its `NetworkBehaviour`s |
| `GlobalObjectIdHash` / `NetworkObjectId` | Prefab-asset identity used at spawn / live-instance `ulong` id used for targeting |
| `SpawnWithObservers` | Default `true` |
| `ActiveSceneSynchronization` | Default off; on migrates the object to a newly active scene, at a cost |
| `SceneMigrationSynchronization` | Default on; disable past ~600–1,000 spawned objects [no] |
| `DontDestroyWithOwner` | Unset → destroyed when its owner disconnects |
| Transform sync on spawn | Costs bandwidth; disable on objects that don't need it |

## Parenting
| Subject | Fact that decides |
|---|---|
| `TrySetParent(NetworkObject, bool worldPositionStays = true)` / `TryRemoveParent(bool worldPositionStays = true)` | Both objects spawned; never set `transform.parent` directly. Mixing `true`/`false` across a multi-generation sequence yields wrong nested scale |
| Who may parent | Owner: its own object under any spawned `NetworkObject`. Under a non-networked GameObject: authority only, unless `AllowOwnerToParent` (CS) |
| Invalid attempt | Reverts with only a console warning |
| Late joiner | Wait for `SceneEventType.SynchronizeComplete` before parenting in-scene objects for the new player |
| Auto Object Parent Sync | Default on |

## NetworkBehaviour lifecycle
`OnNetworkPreSpawn(ref NetworkManager)` (`Is*` not valid yet) → `OnNetworkSpawn` (main init, `Is*` valid) → `OnNetworkPostSpawn` (all siblings spawned: first safe cross-sibling access) … `OnNetworkPreDespawn` (still spawned: last read of sibling state) → `OnNetworkDespawn`. An `OnDestroy` override calls `base.OnDestroy()` last. Disabled `NetworkBehaviour`s follow dynamic-spawn timing even in-scene.

**Caveat:** `OnNetworkSpawn` runs before `Start()` for a dynamically spawned object but after it for an in-scene one — put shared setup in one once-guarded method both call.

## Ordering and late-join sync
| Subject | Fact that decides |
|---|---|
| `NetworkVariable` | Eventually consistent, not ordered: dirty values across objects can apply in a different order than written [nbsync] |
| Rpc | Queued in call order — use when order matters |
| `OnSynchronize<T>(ref BufferSerializer<T>)` | Adds per-instance data to the late-join payload (30 instances × 100 B = 3 KB). Runs only the write half on the server, the read half on the client. An exception rewinds the stream: that data is silently lost |

## Ownership callbacks
`OnLostOwnership` → `OnGainedOwnership` → `OnOwnershipChanged(ulong previous, ulong current)`. CS: the first two fire on the server plus the losing/gaining client; DA: on all clients. `OnOwnershipChanged` fires on every client in both topologies.

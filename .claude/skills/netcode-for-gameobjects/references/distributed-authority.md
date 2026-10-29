# Distributed Authority — Session Owner, Ownership Flags, Requests, Locks

Sources — `manual/`: [dac] terms-concepts/distributed-authority.html, [qs] learn/distributed-authority-quick-start.html, [web] learn/distributed-authority-webgl.html. `api/Unity.Netcode.`: [topo] NetworkTopologyTypes, [os] NetworkObject.OwnershipStatus, NetworkObject.OwnershipRequestStatus / OwnershipRequestResponseStatus / OwnershipPermissionsFailureStatus / OwnershipLockActions, NetworkManager.OnSessionOwnerPromotedDelegateHandler / OnFetchLocalPlayerPrefabToSpawnDelegateHandler (each `.html`).

Topology trade-offs and ownership basics: [core-architecture.md](core-architecture.md).

## Setup
| Subject | Fact that decides |
|---|---|
| Transport | The API says DA is "only supported using `UnityTransport`" [topo]; the quickstart selects `DistributedAuthorityTransport` under Network Transport [qs]. Wire as the quickstart does |
| Session | Through UGS, not NGO's connect flow: initialize `Unity.Services.Core`, sign in with `Unity.Services.Authentication` (anonymous works), then `MultiplayerService.Instance.CreateOrJoinSessionAsync(...)` with `SessionOptions { Name, MaxPlayers }` `.WithDistributedAuthorityNetwork()` [qs] |
| First spawn | Not before `OnClientConnectedCallback` fires — earlier spawns error [qs] |
| Physics | No shared simulation; each owner simulates its own objects |

**Caveat:** the Client-Server habit "only the server writes, gate on `IsServer`" breaks here — the owner writes and there may be no server, so an `IsServer` gate silently drops the owner's updates.

## Session owner
| Subject | Fact that decides |
|---|---|
| Who | The first client to join; on its disconnect NGO promotes a replacement automatically |
| Duties | Scene load/unload and syncing state to late joiners — the server's job in CS |
| Detect | `NetworkManager.IsSessionOwner` or `NetworkManager.LocalClient.IsSessionOwner` |
| `OnSessionOwnerPromotedDelegateHandler(ulong sessionOwnerPromoted)` | Mid-session handoff; arg is the new owner's client id |
| `OnFetchLocalPlayerPrefabToSpawnDelegateHandler() : GameObject` | Resolves the local player prefab at runtime instead of one fixed `PlayerPrefab`; needs `AutoSpawnPlayerPrefabClientSide` |

## `OwnershipStatus` flags [os]
| Flag | Fact that decides |
|---|---|
| `None` | Cannot be distributed, requested or transferred |
| `Distributable` | Redistributed automatically on client join/leave, unless locked or a request is pending |
| `Transferable` | Any non-owner takes ownership immediately if not locked |
| `RequestRequired` | Non-owner must `RequestOwnership()` and be approved; auto-locks once transferred |
| `SessionOwner` | Pinned to the session owner; follows it when session ownership changes |
| `All` | Inspector shortcut only: first pick = `Distributable`+`Transferable`+`RequestRequired`, second = `SessionOwner` alone |

## Requests, failures, locks
| Subject | Members — meaning |
|---|---|
| `RequestOwnership()` → `OwnershipRequestStatus` (sync) | `RequestSent` — sent, not granted; `AlreadyOwner`; `RequestRequiredNotSet` — flag missing; `Locked`; `RequestInProgress` — retry later; `SessionOwnerOnly` — not requestable; `InvalidOperation` — not now |
| `OnOwnershipRequested` (authority) | `bool (ulong clientRequesting)` — `false` denies |
| `OnOwnershipRequestResponse(OwnershipRequestResponseStatus)` (requester) | `Approved` — now owner locally; `Denied` — authority returned `false`; `Locked` — locked after send; `RequestInProgress` — another request got there first; `CannotRequest` — `RequestRequired` changed in flight |
| `OnOwnershipPermissionsFailure(OwnershipPermissionsFailureStatus)` (direct change, not a request) | `Locked`; `NotTransferrable` — no `Transferable` flag; `RequestRequired` — use `RequestOwnership`; `RequestInProgress`; `SessionOwnerOnly` |
| `OwnershipLockActions` | `None`; `SetAndLock` / `SetAndUnlock` — set flags and lock/unlock in one step. A locked object rejects both direct changes and requests |

## WebGL [web]
| Subject | Fact that decides |
|---|---|
| Minimum versions | NGO 2.1.1, Unity Transport 2.3.0, Multiplayer Services 1.0.2, Unity 6 |
| Transport | Tick "Use Web Sockets" on `DistributedAuthorityTransport`; no self-signed certificates needed |
| Local multi-client test | Unity's built-in web hosting; extra clients = the same URI in more tabs |

Unverified: how `DistributedAuthorityTransport` relates to `UnityTransport` (subclass or wrapper — not stated); whether a WebGL client can hold session-owner duties under browser connectivity limits; the call site taking `OwnershipLockActions`.

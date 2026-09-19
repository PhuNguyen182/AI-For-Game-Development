# Distributed Authority — Session Owner, Ownership Requests, and Locks

Source: [Distributed authority quickstart](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/manual/da-quickstart.html) (index page only — its content is the two guides below), [Distributed authority general quickstart](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/manual/learn/distributed-authority-quick-start.html), [Distributed authority WebGL quickstart](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/manual/learn/distributed-authority-webgl.html), [Distributed authority (terms & concepts)](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/manual/terms-concepts/distributed-authority.html), and the API pages listed in [API index](#api-index).
Covers: SKILL.md §4 — **"Confirm the network topology before writing any NetworkObject code"**.

Distributed Authority (DA) mode distributes authority over each `NetworkObject` across clients — per-object, based on that object's ownership permission flags — instead of routing every state change through one server, per [terms-concepts](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/manual/terms-concepts/distributed-authority.html). This file covers only what's different or additional versus Client-Server; general `NetworkManager`/`NetworkObject`/`NetworkBehaviour`/ownership fundamentals live in [core-architecture.md](core-architecture.md).

## What's different vs. Client-Server

| Aspect | What it decides | Source |
|---|---|---|
| Authority model | Client-Server puts "a dedicated game instance running the game simulation" in charge of every state change; DA instead distributes "authority over NetworkObjects...across clients depending on a NetworkObject's ownership permission settings" — there is no single simulating instance. | [terms-concepts](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/manual/terms-concepts/distributed-authority.html) |
| Topology selection | Set `NetworkConfig`'s "Network Topology" to `Distributed Authority` before starting the session — a project-level choice, not per-object. | [quickstart](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/manual/learn/distributed-authority-quick-start.html) |
| Transport | Requires the `DistributedAuthorityTransport` component on the `NetworkManager` GameObject instead of a plain `UnityTransport`. | [quickstart](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/manual/learn/distributed-authority-quick-start.html) |
| Session creation | Sessions go through Unity Gaming Services, not NGO's own connect flow: `Unity.Services.Core` initializes, `Unity.Services.Authentication` signs in (anonymous supported), then `MultiplayerService.Instance.CreateOrJoinSessionAsync()` with a `SessionOptions { Name, MaxPlayers }` configured via `.WithDistributedAuthorityNetwork()` opens the DA session. | [quickstart](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/manual/learn/distributed-authority-quick-start.html) |
| Physics | No "single physics simulation governing the interaction of all objects" — each owner simulates its own objects independently. | [terms-concepts](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/manual/terms-concepts/distributed-authority.html) |
| Trust / cheating surface | "The authority model gives more trust to individual clients" than Client-Server does; Unity's own docs call DA "typically not suitable for high-performance competitive games." | [terms-concepts](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/manual/terms-concepts/distributed-authority.html) |

**Critical caveat**: a `NetworkVariable` write-permission habit carried over from Client-Server — "only the server writes, gate on `NetworkManager.IsServer`" — does not hold in DA mode. The current *owner* writes, and there may be no server at all; code that still checks `IsServer` silently drops the owner's own updates. Confirm per-object write permission against the ownership model in [core-architecture.md](core-architecture.md) before assuming server-only writes.

## Session owner

| Fact | What it decides | Source |
|---|---|---|
| Definition | The session owner is "a single dedicated client that's responsible for managing and synchronizing global game state-related tasks." | [terms-concepts](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/manual/terms-concepts/distributed-authority.html) |
| Initial assignment | The first client to join a session becomes the initial session owner. | [terms-concepts](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/manual/terms-concepts/distributed-authority.html) |
| Reassignment | On the session owner's disconnection, NGO automatically promotes a replacement — no manual failover code required. | [terms-concepts](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/manual/terms-concepts/distributed-authority.html) |
| Responsibilities | The session owner (not "the server") owns loading/unloading scenes and synchronizing existing game state to late-joining clients. | [terms-concepts](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/manual/terms-concepts/distributed-authority.html) |
| Detection | Check `NetworkManager.Singleton.IsSessionOwner` (the quickstart sample also reads it off `NetworkManager.LocalClient.IsSessionOwner`) to branch owner-only logic. | [terms-concepts](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/manual/terms-concepts/distributed-authority.html), [quickstart](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/manual/learn/distributed-authority-quick-start.html) |
| Promotion callback | `NetworkManager.OnSessionOwnerPromotedDelegateHandler(ulong sessionOwnerPromoted)` — the parameter is "the new session owner client identifier"; subscribe to react to a mid-session ownership handoff. | [API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.NetworkManager.OnSessionOwnerPromotedDelegateHandler.html) |
| Local player prefab | `NetworkManager.OnFetchLocalPlayerPrefabToSpawnDelegateHandler() : GameObject` — a "Distributed Authority Mode" delegate returning the "Player Prefab GameObject" to spawn for the local player, resolving it dynamically instead of relying on one fixed `NetworkConfig.PlayerPrefab`. | [API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.NetworkManager.OnFetchLocalPlayerPrefabToSpawnDelegateHandler.html) |

**Critical caveat**: the quickstart explicitly warns that "it's important to wait until `OnClientConnectedCallback` has been triggered before spawning objects. Spawning objects early will result in errors and unexpected behaviour." Gate all DA spawn code behind that callback, same as any other connection-dependent setup.

## Ownership status flags

`NetworkObject` ownership in DA mode is governed by flag-style status values. The fetched manual pages don't expose a dedicated API page for the `OwnershipStatus` enum itself — the flag names below are quoted directly from the terms-concepts page and from other enums' descriptions that reference them; treat any flag not listed here as unconfirmed rather than assumed.

| Flag | What it decides | Source |
|---|---|---|
| `SessionOwner` | The object "always belong[s] to the current session owner," with ownership auto-transferring whenever the session owner changes — use for global/shared state that must sit with the arbitrating client. | [terms-concepts](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/manual/terms-concepts/distributed-authority.html) |
| `Distributable` | Ownership "[is] automatically distributed between clients as clients connect and disconnect," spreading simulation/bandwidth load instead of pinning it to one client. | [terms-concepts](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/manual/terms-concepts/distributed-authority.html) |
| `None` | "Prevents other clients from taking ownership" — the current owner keeps it until explicitly changed in code. | [terms-concepts](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/manual/terms-concepts/distributed-authority.html) |
| `Transferable` | Referenced by `OwnershipPermissionsFailureStatus.NotTransferrable`: without this flag set, ownership "cannot be acquired" by another client at all. | [API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.NetworkObject.OwnershipPermissionsFailureStatus.html) |
| `RequestRequired` | Referenced by `OwnershipRequestStatus.RequestRequiredNotSet` and `OwnershipPermissionsFailureStatus.RequestRequired`: gates whether a client must call `RequestOwnership()` (async, authority-approved) rather than acquire ownership directly. | [API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.NetworkObject.OwnershipRequestStatus.html), [API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.NetworkObject.OwnershipPermissionsFailureStatus.html) |

## Requesting ownership

`NetworkObject.RequestOwnership()` returns an `OwnershipRequestStatus` synchronously (did the request get sent), then the eventual outcome arrives asynchronously as an `OwnershipRequestResponseStatus`.

`OwnershipRequestStatus` (synchronous return of `RequestOwnership()`):

| Member | Meaning | Source |
|---|---|---|
| `AlreadyOwner` | "The current client is already the owner (no need to request ownership)." | [API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.NetworkObject.OwnershipRequestStatus.html) |
| `InvalidOperation` | "It is invalid to request ownership at this time." | [API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.NetworkObject.OwnershipRequestStatus.html) |
| `Locked` | "The current owner has locked ownership which means requests are not available at this time." | [API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.NetworkObject.OwnershipRequestStatus.html) |
| `RequestInProgress` | "There is already a known request in progress. You can scan for ownership changes and try again after a specific period of time." | [API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.NetworkObject.OwnershipRequestStatus.html) |
| `RequestRequiredNotSet` | "The `OwnershipStatus.RequestRequired` flag is not set on this NetworkObject." | [API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.NetworkObject.OwnershipRequestStatus.html) |
| `RequestSent` | "The request for ownership was sent (does not mean it will be granted, but the request was sent)." | [API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.NetworkObject.OwnershipRequestStatus.html) |
| `SessionOwnerOnly` | "This object is marked as `SessionOwnerOnly` and therefore cannot be requested." | [API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.NetworkObject.OwnershipRequestStatus.html) |

`OwnershipRequestResponseStatus` (delivered later via `OnOwnershipRequestResponse`):

| Member | Meaning | Source |
|---|---|---|
| `Approved` | "The ownership request was approved and the requesting client has gained ownership on the local instance." | [API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.NetworkObject.OwnershipRequestResponseStatus.html) |
| `CannotRequest` | "Denied because the `RequestRequired` status changed while the request was in flight." | [API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.NetworkObject.OwnershipRequestResponseStatus.html) |
| `Denied` | "Denied by the authority instance (`OnOwnershipRequested` returned `false`)." | [API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.NetworkObject.OwnershipRequestResponseStatus.html) |
| `Locked` | "Denied because the object became locked after the request was sent." | [API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.NetworkObject.OwnershipRequestResponseStatus.html) |
| `RequestInProgress` | "Denied because another request was already in progress when this request was received." | [API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.NetworkObject.OwnershipRequestResponseStatus.html) |

Request-flow delegates:

| Delegate | Signature | Fires where / meaning | Source |
|---|---|---|---|
| `OnOwnershipRequested` | `bool OnOwnershipRequestedDelegateHandler(ulong clientRequesting)` | Authority-side approve/deny hook — return `true` to approve, `false` to deny and block the transfer. | [API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.NetworkObject.OnOwnershipRequestedDelegateHandler.html) |
| `OnOwnershipRequestResponse` | `void OnOwnershipRequestResponseDelegateHandler(OwnershipRequestResponseStatus ownershipRequestResponse)` | Requester-side hook receiving the approval/denial outcome above. | [API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.NetworkObject.OnOwnershipRequestResponseDelegateHandler.html) |

## Ownership locks

`OwnershipLockActions` — pairs a flag change with a lock/unlock in one step (exact call site not shown on the fetched pages, but the three members below are explicit):

| Member | Meaning | Source |
|---|---|---|
| `None` | "No additional locking action will be performed." | [API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.NetworkObject.OwnershipLockActions.html) |
| `SetAndLock` | "Sets the specified ownership flags and then locks the NetworkObject." | [API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.NetworkObject.OwnershipLockActions.html) |
| `SetAndUnlock` | "Sets the specified ownership flags and then unlocks the NetworkObject." | [API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.NetworkObject.OwnershipLockActions.html) |

A locked object rejects both direct permission-based ownership changes (`OwnershipPermissionsFailureStatus.Locked`) and new requests (`OwnershipRequestStatus.Locked` / `OwnershipRequestResponseStatus.Locked`) until unlocked — see the two tables above.

## Permission failures (non-request path)

`OwnershipPermissionsFailureStatus`, delivered via `OnOwnershipPermissionsFailureDelegateHandler(OwnershipPermissionsFailureStatus changeOwnershipFailure)` — fires when a *direct* (non-request) ownership change attempt fails a permission check, distinct from the request/response flow above:

| Member | Meaning | Source |
|---|---|---|
| `Locked` | "The NetworkObject is locked and ownership cannot be acquired." | [API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.NetworkObject.OwnershipPermissionsFailureStatus.html) |
| `NotTransferrable` | "The NetworkObject does not have the `OwnershipStatus.Transferable` flag set and ownership cannot be acquired." | [API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.NetworkObject.OwnershipPermissionsFailureStatus.html) |
| `RequestInProgress` | "The NetworkObject is already processing an ownership request and ownership cannot be acquired at this time." | [API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.NetworkObject.OwnershipPermissionsFailureStatus.html) |
| `RequestRequired` | "The NetworkObject requires an ownership request via `RequestOwnership`." | [API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.NetworkObject.OwnershipPermissionsFailureStatus.html) |
| `SessionOwnerOnly` | "The NetworkObject has the `OwnershipStatus.SessionOwner` flag set and ownership cannot be acquired." | [API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.NetworkObject.OwnershipPermissionsFailureStatus.html) |

## WebGL-specific constraints

| Aspect | What it decides | Source |
|---|---|---|
| Minimum versions | Netcode for GameObjects 2.1.1+, Unity Transport 2.3.0+, Multiplayer Services 1.0.2+, on a Unity 6 Editor. | [webgl quickstart](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/manual/learn/distributed-authority-webgl.html) |
| Transport setting | Enable the "Use Web Sockets" checkbox on the `DistributedAuthorityTransport` component on the `NetworkManager` GameObject — required for a WebGL build to connect. | [webgl quickstart](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/manual/learn/distributed-authority-webgl.html) |
| Certificates | No self-signed certificates need to be generated for Distributed Authority WebGL connections. | [webgl quickstart](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/manual/learn/distributed-authority-webgl.html) |
| Editor module | Install the WebGL Build Support module for the Editor. | [webgl quickstart](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/manual/learn/distributed-authority-webgl.html) |
| Local hosting | Unity provides built-in web hosting to serve the WebGL build's HTTP requirements during local testing. | [webgl quickstart](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/manual/learn/distributed-authority-webgl.html) |
| Multi-client testing | Multiple WebGL clients can join the same session by copying/pasting the browser URI into additional tabs or windows. | [webgl quickstart](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/manual/learn/distributed-authority-webgl.html) |

**Critical caveat**: the WebGL quickstart never states whether a WebGL client can be promoted to session owner, or how browser-imposed connectivity limits interact with session-owner responsibilities (scene load/unload, late-joiner sync) if one is. Don't assume parity with native clients here — verify with a real multi-client run before shipping a WebGL build that might need to hold session ownership.

**Critical caveat**: Unity's own docs call DA "typically not suitable for high-performance competitive games" because there is no single physics simulation and "the authority model gives more trust to individual clients." Flag this trade-off to Technical Architect before adopting DA for anything precision- or security-sensitive (see `terms-concepts` in the first table above).

## API index

| Type | Source |
|---|---|
| `NetworkManager.OnSessionOwnerPromotedDelegateHandler` | [API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.NetworkManager.OnSessionOwnerPromotedDelegateHandler.html) |
| `NetworkManager.OnFetchLocalPlayerPrefabToSpawnDelegateHandler` | [API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.NetworkManager.OnFetchLocalPlayerPrefabToSpawnDelegateHandler.html) |
| `NetworkObject.OwnershipRequestStatus` | [API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.NetworkObject.OwnershipRequestStatus.html) |
| `NetworkObject.OwnershipRequestResponseStatus` | [API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.NetworkObject.OwnershipRequestResponseStatus.html) |
| `NetworkObject.OwnershipPermissionsFailureStatus` | [API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.NetworkObject.OwnershipPermissionsFailureStatus.html) |
| `NetworkObject.OwnershipLockActions` | [API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.NetworkObject.OwnershipLockActions.html) |
| `NetworkObject.OnOwnershipRequestedDelegateHandler` | [API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.NetworkObject.OnOwnershipRequestedDelegateHandler.html) |
| `NetworkObject.OnOwnershipRequestResponseDelegateHandler` | [API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.NetworkObject.OnOwnershipRequestResponseDelegateHandler.html) |
| `NetworkObject.OnOwnershipPermissionsFailureDelegateHandler` | [API](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/Unity.Netcode.NetworkObject.OnOwnershipPermissionsFailureDelegateHandler.html) |

For general `NetworkManager`/`NetworkObject`/`NetworkBehaviour`/ownership mechanics that apply to both topologies, see [core-architecture.md](core-architecture.md).

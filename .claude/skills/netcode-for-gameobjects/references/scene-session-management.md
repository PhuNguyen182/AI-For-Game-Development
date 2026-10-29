# Scene and Session Management — NetworkSceneManager, Reconnection

Sources: [a] manual/basics/scenemanagement/using-networkscenemanager.html, [b] manual/basics/scenemanagement/timing-considerations.html, [c] manual/basics/scenemanagement/inscene-placed-networkobjects.html, [d] manual/basics/scenemanagement/custom-management.html, [e] manual/basics/scenemanagement/client-synchronization-mode.html, [f] manual/advanced-topics/session-management.html, [g] manual/advanced-topics/reconnecting-mid-game.html, [h] api/Unity.Netcode.NetworkSceneManager.html.

## NetworkSceneManager

| Member / fact | Fact that decides |
|---|---|
| "Enable Scene Management" (`NetworkManager`) | On by default. Off = Custom mode, documented as time-consuming and for experienced NGO users only |
| `LoadScene(string, LoadSceneMode)` | Server/host only; returns `SceneEventProgressStatus`; scene must be in Scenes in Build — a blank placeholder for generated content [a] |
| `UnloadScene(Scene)` | Server/host only; additively loaded scenes only, never the active scene |
| One scene event at a time | A second call returns `SceneEventInProgress` |
| `VerifySceneBeforeLoading` | Server delegate; `false` → `SceneFailedVerification`. Also rejects redundant loads on reconnect |
| `DisableValidationWarnings(bool)` | Silences scene-invalidation warnings |
| `GetSynchronizedScenes()` / `GetSceneMapping(MapTypes)` | Tracked scenes; client↔server scene-handle map (`ClientToServer`, `ServerToClient`) |

**Caveat:** with scene management on, `UnityEngine.SceneManagement.SceneManager.LoadScene`/`LoadSceneAsync` bypasses NGO: no `Load` event, no sync for connected or late-joining clients, and the scene's in-scene `NetworkObject`s never spawn on clients.

| `SceneEventProgressStatus` | Meaning |
|---|---|
| `Started` / `None` | Initiated / placeholder before any event |
| `SceneNotLoaded` | Unload of a scene that is not loaded |
| `SceneEventInProgress` | Another event is running |
| `InvalidSceneName` | Misspelled or not in build settings |
| `SceneFailedVerification` | `VerifySceneBeforeLoading` returned `false` |
| `SceneManagementNotEnabled` | Toggle is off |
| `ServerOnlyAction` / `SessionOwnerOnlyAction` | Caller is not server/host / not the distributed-authority session owner ([distributed-authority.md](distributed-authority.md)) |
| `InternalNetcodeError` | E.g. scene not loaded by `NetworkSceneManager`; report as a bug |

## Scene events

`OnSceneEvent` fires for every type; per-type delegates: `OnLoad`, `OnLoadComplete`, `OnLoadEventCompleted`, `OnUnload`, `OnUnloadComplete`, `OnUnloadEventCompleted`, `OnSynchronize`, `OnSynchronizeComplete`.

**Caveat:** subscribe right after `StartServer()`/`StartHost()`/`StartClient()`; subscribing in `OnNetworkSpawn` misses a connecting client's `Synchronize`.

| `SceneEventType` | Direction: meaning |
|---|---|
| `Load` / `Unload` | S→C: started |
| `LoadComplete` / `UnloadComplete` | C→S: this client finished |
| `LoadEventCompleted` / `UnloadEventCompleted` | S→C: every client finished |
| `Synchronize` | S→C: scenes + pre-ordered `NetworkObject` list for a newly approved client |
| `SynchronizeComplete` | C→S: processed and spawned |
| `ReSynchronize` | S→C: ids of objects despawned mid-sync |
| `ActiveSceneChanged` / `ObjectSceneChanged` | Active scene changed / `NetworkObject`s moved scene |

`SceneEvent` payload: `SceneEventType`, `ClientId` (meaning varies by type), `SceneName`, `ScenePath`, `Scene`, `LoadSceneMode`, `AsyncOperation` (Load/Unload only), `ClientsThatCompleted`, `ClientsThatTimedOut`.

## Client synchronization mode

`SetClientSynchronizationMode(LoadSceneMode)`; read `ClientSynchronizationMode`.

| Mode | Connecting client |
|---|---|
| `Single` | Unloads all its scenes, single-loads the server's active scene, additively loads the rest |
| `Additive` | Keeps loaded scenes, loads only what it lacks — faster sync for shared/bootstrap scenes [e] |
| `PostSynchronizationSceneUnloading` (Additive only) | Unloads client scenes not in the server's set after sync |
| `VerifySceneBeforeUnloading` (Additive only) | Client delegate keeping a scene alive through that cleanup |

## Timing

| Fact | Consequence |
|---|---|
| Approval → `Synchronize` → client spawns → `SynchronizeComplete` | `IsConnectedClient` turns `true` only after the server processes `SynchronizeComplete` [b] |
| Server learns of client completion ~RTT/2 late | Do not assume the server knows the instant the client callback fires |
| Additive load: server loads and spawns in-scene objects, then sends `Load`; `LoadEventCompleted` after every client reports | Server content exists before clients hear of the load |
| In-scene placed objects: `Awake` → `Start` → `OnNetworkSpawn`, spawned only after the scene load finishes [c] | No network state (ownership, `NetworkVariable`) in `Awake`/`Start`; dynamic-spawn order in [core-architecture.md](core-architecture.md) |
| `Single` switch: `DestroyWithScene == false` objects park in `DontDestroyOnLoad`, then move to the new active scene | They survive without respawn |
| Unload: server despawns locally before sending `Unload` | Clients may get despawns before the `Unload` event |
| RTT ≥ ~500 ms: a client→server message sent on `LoadComplete` can misorder [b] | Test scene loads under simulated latency |

**Caveat:** `SceneManager.sceneLoaded` fires before NGO spawns the scene's `NetworkObject`s — use `OnLoadComplete`/`OnSynchronizeComplete` instead.

## In-scene placed NetworkObjects

| Fact | Consequence |
|---|---|
| Identified by `GlobalObjectIdHash` + scene | No prefab-list registration needed with scene management on |
| Auto-spawn on scene load, auto-despawn on unload | No manual `Spawn()` normally |
| `Despawn(false)` keeps the instance; `Spawn(destroyWithScene)` respawns it | Reset-and-reuse pattern (pickups) |
| Moving a spawned in-scene object to another scene | Soft-sync errors for late joiners — keep them scene-bound |
| "Auto object parent sync" toggle; scale always local for pre-parented objects | Affects editor-parented hierarchies |
| Frequently destroyed, scene-migrated, or re-parented objects | Use dynamically spawned prefabs instead |

## Custom scene management (toggle off)

| Fact | Consequence |
|---|---|
| All loads go through raw `SceneManager`; NGO handles no scene events, in-scene sync or migration | Developer owns sync: `OnClientConnectedCallback`, custom messages/Rpcs [d] |
| On connect, a client deletes in-scene `NetworkObject`s in its loaded scenes | Re-provide that content deliberately |
| Scenes loaded after connect do not sync their in-scene objects | Spawn prefabs dynamically instead |
| Edits to in-scene placed network prefabs do not sync | Override `NetworkBehaviour.OnSynchronize` |

## Session and reconnection

| Fact | Consequence |
|---|---|
| `clientId` is reassigned on connect and reused after disconnect | Never key persistent player data by it [f] |
| Stable id: account login, or `Guid.NewGuid()` in `PlayerPrefs` sent on connect | Key for reassigning session data |
| Two patterns: state keyed by player id; or player id → owned `NetworkObjectId`s | Recreate the player's state, or restore ownership of existing objects |
| Session data lives host-side, kept current while the player is away | Host is the source of truth |
| No session API, no expiry | Write your own persistence and purge |
| Trigger on `OnClientDisconnectCallback`; check `ShutdownInProgress` first | No reconnect while the old shutdown unwinds [g] |
| Never auto-reconnect after intentional quit, normal server shutdown, kick, or approval denial | Else a reconnect loop |
| Boss Room: `ReconnectCoroutine` state machine — retry until success, max attempts, or user cancel | Reference retry shape |

**Caveat:** if the client's active scene name matches the server's at sync, NGO skips the single-load and only adds the server's other scenes, so additive scenes left from the previous session duplicate silently [g]. Pick one mitigation:

| Mitigation | Trade-off |
|---|---|
| Single-load a "disconnected" scene on disconnect | Forces a clean single-load on reconnect; needs that scene |
| Unload additive scenes on disconnect | Immediate cleanup |
| Unload additive scenes on reconnect, before rejoining | No wasted work if the player never returns |
| `VerifySceneBeforeLoading` rejects the redundant load | Simplest; misses scenes the server unloaded meanwhile — combine with another |

Unverified: the default `ClientSynchronizationMode` is not stated in [e]; check in-Editor.

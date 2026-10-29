---
name: netcode-for-gameobjects
description: "Netcode for GameObjects: NetworkObject/Behaviour/Manager, NetworkVariable, RPCs, ownership, spawning, NetworkTransform, scene management, client-side prediction patterns. Use on an NGO project."
user-invocable: false
---

# Netcode for GameObjects

Not for: choosing NGO (`netcode-architecture-decision`), the DOTS ghost stack (`netcode-for-entities`), the game rule a synced value carries (`csharp-engineer`), reconciliation/tick-rate protocol design (`netcode-engineer`), server-side validation of RPCs and inputs (`server-authoritative-validation`), `NetworkDriver`/pipelines/TLS/`RelayServerData`/a custom `NetworkTransport` (`unity-transport` — the `UnityTransport` component's own fields stay here), non-network performance (`gameplay-engineer`).
Docs: https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/ (installed 2.13.1; reference source paths are below this base) — past 2.13, substitute the version in `Packages/manifest.json`; Distributed Authority changes fastest between releases.

| Reference | Read when |
|---|---|
| [core-architecture.md](references/core-architecture.md) | Choosing topology, wiring `NetworkManager`/connection approval/player prefab, or an ownership, lifecycle-order or parenting bug |
| [distributed-authority.md](references/distributed-authority.md) | The Tech Spec names or hints at Distributed Authority, or an ownership request/lock fails |
| [spawning-objects.md](references/spawning-objects.md) | Instantiating, pooling, hiding or deferring despawn of a `NetworkObject` |
| [state-sync.md](references/state-sync.md) | Choosing `NetworkVariable` vs Rpc, targeting an Rpc, sending a custom message, or handling connect/disconnect events |
| [transform-latency.md](references/transform-latency.md) | Syncing movement/animation/physics, or visible correction or latency |
| [serialization.md](references/serialization.md) | A `NetworkVariable` or Rpc parameter uses a non-primitive type |
| [scene-session-management.md](references/scene-session-management.md) | Loading/unloading scenes, or a client reconnects mid-session |
| [transports-testing.md](references/transports-testing.md) | Configuring `UnityTransport`/Relay, simulating latency/loss, or debugging a networked feature |

## Steps
1. **Confirm the topology before writing any `NetworkObject` code** — Client-Server and Distributed Authority put ownership, `NetworkVariable` write permission and spawn authority in different hands, per [core-architecture.md](references/core-architecture.md) and [distributed-authority.md](references/distributed-authority.md). Tech Spec silent on topology, ownership model or reconciliation → ask `technical-architect`; never pick silently.
2. **Wire `NetworkManager` before anything spawns** — `NetworkConfig`, prefab list, connection approval and player prefab gate everything after, per [core-architecture.md](references/core-architecture.md). `UnityTransport` for real networking; add Relay only when a non-LAN, no-dedicated-server path is needed, per [transports-testing.md](references/transports-testing.md).
3. **Put networked state on `NetworkObject` + `NetworkBehaviour`, never a plain `MonoBehaviour`** — lifecycle in `OnNetworkSpawn`/`OnNetworkDespawn`. The rule deciding the value stays in `Game.Core.*` (`csharp-standards` → `coding-principles.md`, Shared Core integrity); the behaviour carries only the resolved value.
4. **Spawn and despawn through `NetworkObject.Spawn`/`Despawn`, pooled for anything frequent** — raw `Instantiate`/`Destroy` never registers with `NetworkSpawnManager`, so the object exists on one peer only. Projectiles and frequent enemies → a registered `INetworkPrefabInstanceHandler`, per [spawning-objects.md](references/spawning-objects.md).
5. **Pick `NetworkVariable` or Rpc by data shape** — continuous state → `NetworkVariable<T>`/`NetworkList<T>` with explicit permissions, reacted to in `OnValueChanged`, never polled; one-shot event → Rpc, per [state-sync.md](references/state-sync.md).
6. **Sync transforms with NetworkTransform, not hand-rolled position Rpcs** — it already does delta compression, interpolation and authority modes for both topologies, per [transform-latency.md](references/transform-latency.md). `AnticipatedNetworkTransform`/`AnticipatedNetworkVariable<T>` only once measured latency causes visible correction.
7. **Serialize custom types by layout** — unmanaged with no reference fields → `INetworkSerializeByMemcpy`; anything else → `INetworkSerializable`, per [serialization.md](references/serialization.md).
8. **Load scenes through `NetworkSceneManager` once `EnableSceneManagement` is on** — a direct `SceneManager.LoadScene` desyncs client scene state, per [scene-session-management.md](references/scene-session-management.md).
9. **Verify with a real multi-client run before claiming it works** — one Editor Play Mode instance cannot expose ownership or Rpc-direction bugs; a `NetcodeIntegrationTest` (server + N clients) counts. Network-condition cases (simulated latency/loss) → `qa-automation-engineer`; multi-instance run → `build-release-engineer`, per [transports-testing.md](references/transports-testing.md).

## Never
- Put a password, token or anything sensitive in `NetworkConfig.ConnectionData` — NGO neither encrypts nor authenticates the approval payload.

## Output
```
## Netcode for GameObjects — <feature>
- Topology: Client-Server / Distributed Authority — <reason>
- Sync: <NetworkVariable / Rpc / NetworkTransform / ... per value> — <reason>
- Spawn/ownership: <who spawns/despawns, pooled or not, ownership model>
- Shared Core boundary: <rule logic confirmed in Game.Core.*>
- Layer: Game.Client.* / Game.Server.* / Editor-only
- Verified: <multi-client run / network-condition test, or "not run">
- Known limitations: <...>
```
On request only, add `Latent concerns` and `Future remediation`, each with its trigger.

## Example
- "Send the position every frame with a ServerRpc, it's simpler" → declined: no interpolation and a full payload every frame; used `NetworkTransform` (step 6).

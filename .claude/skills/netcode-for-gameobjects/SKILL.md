---
name: netcode-for-gameobjects
description: "NGO: NetworkObject, NetworkBehaviour, NetworkVariable, RPCs, ownership, NetworkTransform. Use on an NGO project."
user-invocable: false
---

# Netcode for GameObjects

- **Not for:** choosing NGO (`netcode-architecture-decision`).
- **Not for:** the DOTS ghost stack (`netcode-for-entities`).
- **Not for:** the game rule a synced value carries (`csharp-engineer`).
- **Not for:** reconciliation/tick-rate protocol design (`netcode-engineer`).
- **Not for:** server-side validation of RPCs and inputs (`server-authoritative-validation`).
- **Not for:** `NetworkDriver`/pipelines/TLS/`RelayServerData`/a custom `NetworkTransport` (`unity-transport`).
  - **Stays here:** the `UnityTransport` component's own fields.
- **Not for:** non-network performance (`gameplay-engineer`).
- **Docs:** https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/ (installed 2.13.1; reference source paths are below this base).
  - **Past 2.13:** substitute the version in `Packages/manifest.json`.
  - **Version caveat:** Distributed Authority changes fastest between releases.

## References
- **[core-architecture.md](references/core-architecture.md):** Choosing topology, wiring `NetworkManager`/connection approval/player prefab, or an ownership, lifecycle-order or parenting bug.
- **[distributed-authority.md](references/distributed-authority.md):** The Tech Spec names or hints at Distributed Authority, or an ownership request/lock fails.
- **[spawning-objects.md](references/spawning-objects.md):** Instantiating, pooling, hiding or deferring despawn of a `NetworkObject`.
- **[state-sync.md](references/state-sync.md):** Choosing `NetworkVariable` vs Rpc, targeting an Rpc, sending a custom message, or handling connect/disconnect events.
- **[transform-latency.md](references/transform-latency.md):** Syncing movement/animation/physics, or visible correction or latency.
- **[serialization.md](references/serialization.md):** A `NetworkVariable` or Rpc parameter uses a non-primitive type.
- **[scene-session-management.md](references/scene-session-management.md):** Loading/unloading scenes, or a client reconnects mid-session.
- **[transports-testing.md](references/transports-testing.md):** Configuring `UnityTransport`/Relay, simulating latency/loss, or debugging a networked feature.

## Steps
1. **Confirm the topology before writing any `NetworkObject` code:** per [core-architecture.md](references/core-architecture.md) and [distributed-authority.md](references/distributed-authority.md).
   - **Why:** Client-Server and Distributed Authority put ownership, `NetworkVariable` write permission and spawn authority in different hands.
   - **Tech Spec silent on topology, ownership model or reconciliation:** `Needs-decision`, `Next: technical-architect`; never pick silently.
2. **Wire `NetworkManager` before anything spawns:** per [core-architecture.md](references/core-architecture.md).
   - **Gates:** `NetworkConfig`, prefab list, connection approval and player prefab gate everything after.
   - **Transport:** `UnityTransport` for real networking; add Relay only when a non-LAN, no-dedicated-server path is needed, per [transports-testing.md](references/transports-testing.md).
3. **Put networked state on `NetworkObject` + `NetworkBehaviour`, never a plain `MonoBehaviour`:** lifecycle in `OnNetworkSpawn`/`OnNetworkDespawn`.
   - **Rule:** the rule deciding the value stays in a Core assembly (`csharp-standards` → `coding-principles.md`, Shared Core integrity).
   - **Behaviour:** the `NetworkBehaviour` carries only the resolved value.
4. **Spawn and despawn through `NetworkObject.Spawn`/`Despawn`, pooled for anything frequent:** per [spawning-objects.md](references/spawning-objects.md) for pooling.
   - **Why:** raw `Instantiate`/`Destroy` never registers with `NetworkSpawnManager`, so the object exists on one peer only.
   - **Projectiles and frequent enemies:** a registered `INetworkPrefabInstanceHandler`.
5. **Pick `NetworkVariable` or Rpc by data shape:** per [state-sync.md](references/state-sync.md).
   - **Continuous state:** `NetworkVariable<T>`/`NetworkList<T>` with explicit permissions, reacted to in `OnValueChanged`, never polled.
   - **One-shot event:** Rpc.
6. **Sync transforms with NetworkTransform, not hand-rolled position Rpcs:** per [transform-latency.md](references/transform-latency.md).
   - **Why:** it already does delta compression, interpolation and authority modes for both topologies.
   - **Anticipation:** `AnticipatedNetworkTransform`/`AnticipatedNetworkVariable<T>` only once measured latency causes visible correction.
7. **Serialize custom types by layout:** per [serialization.md](references/serialization.md).
   - **Unmanaged with no reference fields:** `INetworkSerializeByMemcpy`.
   - **Anything else:** `INetworkSerializable`.
8. **Load scenes through `NetworkSceneManager` once `EnableSceneManagement` is on:** per [scene-session-management.md](references/scene-session-management.md).
   - **Why:** a direct `SceneManager.LoadScene` desyncs client scene state.
9. **Verify with a real multi-client run before claiming it works:** per [transports-testing.md](references/transports-testing.md).
   - **Why:** one Editor Play Mode instance cannot expose ownership or Rpc-direction bugs.
   - **Counts as a real run:** a `NetcodeIntegrationTest` (server + N clients).
   - **Network-condition cases (simulated latency/loss):** `qa-automation-engineer`.
   - **Multi-instance run:** `build-release-engineer`.

## Never
- **Sensitive data in the approval payload:** a password, token or anything sensitive in `NetworkConfig.ConnectionData` — NGO neither encrypts nor authenticates the approval payload.

## Output
```
## Netcode for GameObjects — <feature>
- Topology: Client-Server / Distributed Authority — <reason>
- Sync: <NetworkVariable / Rpc / NetworkTransform / ... per value> — <reason>
- Spawn/ownership: <who spawns/despawns, pooled or not, ownership model>
- Shared Core boundary: <rule logic confirmed in a Core assembly>
- Layer: Client / <Feature>/Server / Editor-only
```

## Example
- **"Send the position every frame with a ServerRpc, it's simpler":** declined — no interpolation and a full payload every frame; used `NetworkTransform` (step 6).

---
name: netcode-for-gameobjects
description: >
  Technique for Unity's Netcode for GameObjects package (`Unity.Netcode`) —
  `NetworkObject`, `NetworkBehaviour`, `NetworkManager`, `NetworkVariable<T>`,
  `NetworkList<T>`, `ServerRpc`/`ClientRpc`/`Rpc` attributes, `NetworkTransform`,
  `NetworkAnimator`, `NetworkRigidbody`, `NetworkSceneManager`, `UnityTransport`,
  Unity Relay, `INetworkSerializable`, Client-Server and Distributed Authority
  network topologies, ownership, and connection approval. Use when wiring
  multiplayer state sync, spawning/ownership, scene or session management, or
  transport setup for a Unity multiplayer feature, or diagnosing a desync or
  wrong-direction RPC. Not for: choosing NGO itself over Mirror/Photon/custom
  (`netcode-architecture-decision`), the gameplay rule a synced value
  represents (`csharp-engineer`), server-side anti-cheat validation
  (`server-authoritative-engineer`), the reconciliation/tick-rate protocol
  design (`netcode-engineer`), non-network Unity performance work
  (`tech-lead-performance`).
---

# Netcode for GameObjects — Multiplayer State Sync, Spawning, Scenes

## Bundled resources

### References
Read-only context, loaded on demand so SKILL.md itself stays short.

| File | Contents | Read when |
|---|---|---|
| [root-links.md](references/root-links.md) | Manual and API roots, the package version pin, which file answers which question | Starting any task here, or confirming the installed package version |
| [core-architecture.md](references/core-architecture.md) | Topology, authority, ownership, `NetworkManager`, `NetworkObject`, `NetworkBehaviour`, connection approval | Setting up a new networked object or session from scratch |
| [distributed-authority.md](references/distributed-authority.md) | Distributed Authority topology specifics — session owner, ownership requests/locks | The Tech Spec specifies or hints at Distributed Authority mode |
| [spawning-objects.md](references/spawning-objects.md) | `NetworkObject.Spawn`/`Despawn`, object pooling, prefab handler, visibility | Instantiating, pooling, or hiding a `NetworkObject` at runtime |
| [state-sync.md](references/state-sync.md) | `NetworkVariable<T>`, `NetworkList<T>`, RPC attributes and params, custom messages | Replicating state or sending a one-shot networked event |
| [transform-latency.md](references/transform-latency.md) | `NetworkTransform`/`Animator`/`Rigidbody`, interpolation, client anticipation, ticks | Syncing movement/animation, or diagnosing visible correction/latency |
| [serialization.md](references/serialization.md) | `INetworkSerializable`, `INetworkSerializeByMemcpy`, `FastBufferWriter`/`Reader` | A `NetworkVariable` or Rpc parameter uses a custom, non-primitive type |
| [scene-session-management.md](references/scene-session-management.md) | `NetworkSceneManager`, session management, reconnection | Loading/unloading scenes or handling client reconnect in a session |
| [transports-testing.md](references/transports-testing.md) | `UnityTransport`, Unity Relay, artificial network conditions, troubleshooting | Configuring the transport, or verifying/debugging a networked feature |

## 1. Objective
Wire Unity multiplayer features on Netcode for GameObjects (NGO) so that the client and server agree on game state, without the failure modes that stay silent until a real multi-client run exposes them: an RPC sent to the wrong target, a `NetworkVariable` written from a client that has no write permission for the current topology, a `NetworkObject` instantiated with `GameObject.Instantiate` instead of spawned (so it exists on one peer only), or a custom struct that serializes correctly in the Editor but corrupts across a build's endianness/layout assumptions.

## 2. Role
Act as the Netcode for GameObjects implementation specialist for the client track — the tool `netcode-engineer`, `unity-engineer`, and `server-authoritative-engineer` reach for whenever a feature needs its state, events, or objects to exist consistently across a multiplayer session. This skill supplies the NGO API surface; it does not decide the sync protocol or the game rule riding on top of it.

## 3. When to invoke this skill
- Wiring or reviewing `NetworkObject`/`NetworkBehaviour`, `NetworkManager`, or `NetworkConfig` for a multiplayer feature.
- Writing state replication via `NetworkVariable<T>`/`NetworkList<T>`, or a networked event via `ServerRpc`/`ClientRpc`/`Rpc`.
- Spawning, despawning, pooling, or hiding a `NetworkObject`, or handling ownership/ownership requests.
- Setting up scene management, session management, or reconnection for a multiplayer session.
- Choosing or implementing against Client-Server vs. Distributed Authority topology-specific API behavior.
- Configuring `UnityTransport`, Unity Relay, or diagnosing a networked feature with artificial latency/packet loss.
- Negative trigger: whether NGO is even the right netcode foundation for this project, versus Mirror/Photon/custom — that is `netcode-architecture-decision`; this skill assumes NGO is already chosen.
- Negative trigger: the gameplay rule/formula the synced value represents (damage math, cooldowns, economy) — that is `Game.Core.*` per `coding-principles.md`'s Shared Core integrity section, owned by `csharp-engineer`; this skill only carries the resolved value across the wire.
- Negative trigger: server-side validation/anti-cheat of a synced value — `server-authoritative-engineer`.
- Negative trigger: designing the reconciliation/prediction protocol itself (tick rate, rollback strategy, snapshot cadence) — `netcode-engineer` owns that decision; this skill supplies the NGO API used to implement it.
- Negative trigger: general Unity performance work unrelated to netcode (GC, batching, LOD) — the baseline in `coding-principles.md`/`performance-and-algorithms.md`, or `tech-lead-performance` for deep escalation.

## 4. How to use this skill
1. **Confirm the network topology before writing any NetworkObject code** — Client-Server (host/dedicated-server authority) and Distributed Authority (a client owns and simulates its objects, arbitrated by the CMB service) put ownership, `NetworkVariable` write permission, and spawn authority in different hands, per [core-architecture.md](references/core-architecture.md) and [distributed-authority.md](references/distributed-authority.md). Ask Technical Architect if the Tech Spec doesn't state it.
2. **Wire NetworkManager and its transport first** — `NetworkConfig`, `NetworkPrefabs`, connection approval, and the player prefab all live on `NetworkManager` and gate everything spawned afterward, per [core-architecture.md](references/core-architecture.md); pick `UnityTransport` for real networking and add Unity Relay only once a non-LAN, no-dedicated-server path is actually needed, per [transports-testing.md](references/transports-testing.md).
3. **Put networked state behind NetworkObject and NetworkBehaviour, never a plain MonoBehaviour** — a `NetworkBehaviour`'s `OnNetworkSpawn`/`OnNetworkDespawn` own its network lifecycle, per [core-architecture.md](references/core-architecture.md). Keep the game-rule decision the synced value represents in `Game.Core.*`, per `coding-principles.md`'s Shared Core integrity section — the `NetworkBehaviour` only carries the resolved value.
4. **Spawn and despawn through NetworkObject.Spawn/Despawn, pooled for anything frequent** — `GameObject.Instantiate`/`Destroy` alone never registers with `NetworkSpawnManager`, so the object never appears on other peers; pool via a registered `INetworkPrefabInstanceHandler` instead of raw Instantiate/Destroy for projectiles or frequently-spawned enemies, per [spawning-objects.md](references/spawning-objects.md).
5. **Pick NetworkVariable or Rpc by data shape, not habit** — a `NetworkVariable<T>`/`NetworkList<T>` for continuously-replicated state with a defined read/write permission; an Rpc for a one-shot event or command. Never poll a `NetworkVariable` when its `OnValueChanged` delegate already fires the change, per [state-sync.md](references/state-sync.md).
6. **Sync transforms with NetworkTransform, not hand-rolled position Rpcs** — it already provides delta compression, interpolation, and authority-mode switching across both topologies, per [transform-latency.md](references/transform-latency.md). Escalate to `AnticipatedNetworkTransform`/client anticipation only once measured latency actually causes visible correction snapping — don't pre-build prediction nobody asked for (YAGNI).
7. **Serialize custom types with INetworkSerializable or INetworkSerializeByMemcpy by actual layout** — an unmanaged struct with no reference fields uses `INetworkSerializeByMemcpy`; anything else implements `INetworkSerializable` explicitly, per [serialization.md](references/serialization.md).
8. **Route scene loads through NetworkSceneManager once scene management is enabled** — never call `SceneManager.LoadScene` directly once `NetworkConfig.EnableSceneManagement` is on; the server-driven scene event flow is what keeps client scene state in sync, per [scene-session-management.md](references/scene-session-management.md).
9. **Verify with a real multi-client run before claiming the feature works** — a single Editor Play Mode instance cannot exercise ownership or RPC-direction bugs, per `coding-principles.md`'s Handoff section. Hand off to `qa-automation-engineer` for network-condition test cases (`UnityTransport.SimulatorParameters` for packet loss/latency), or flag to `build-run-engineer` for a multi-instance run, per [transports-testing.md](references/transports-testing.md).
10. **Ask Technical Architect when topology, ownership model, or reconciliation behavior isn't specified** — these are hard-to-reverse architecture choices that ripple through every `NetworkBehaviour` written afterward; flag rather than pick one silently.

## 5. Specific goals / tasks this skill performs
- Wire a new networked GameObject: `NetworkObject` + `NetworkBehaviour`, correct spawn call, and ownership model for the chosen topology.
- Implement state replication via `NetworkVariable<T>`/`NetworkList<T>` with the read/write permission matching Client-Server or Distributed Authority.
- Implement a networked event via `ServerRpc`/`ClientRpc`/`Rpc` with the correct `SendTo` target and delivery guarantee.
- Configure `NetworkTransform` (or `NetworkRigidbody`/`NetworkAnimator`) for a synced object's movement or animation.
- Set up `NetworkSceneManager`-driven scene loading/additive scenes, or session management/reconnection, for a multiplayer session.
- Configure connection approval, max players, and `UnityTransport`/Unity Relay for a new session.
- Out of scope: the gameplay rule/formula a `NetworkVariable` carries (`csharp-engineer`, `Game.Core.*`), server-side validation/anti-cheat of the synced value (`server-authoritative-engineer`), reconciliation/prediction protocol design (`netcode-engineer`), the build-vs-license netcode foundation decision (`netcode-architecture-decision`).

## 6. Output format
```
## Netcode for GameObjects Work — <feature/system name>
- Topology: Client-Server / Distributed Authority — rationale
- NGO components touched: <NetworkObject/NetworkBehaviour/NetworkVariable/Rpc/NetworkTransform/...>
- Sync mechanism: NetworkVariable<T> / Rpc / NetworkTransform — rationale
- Spawn/ownership: <who calls Spawn/Despawn, pooled or not, ownership model>
- Shared Core boundary: confirmed the synced value's game-rule logic stays in Game.Core.*, per coding-principles.md
- Verification: <multi-client run / qa-automation-engineer network-condition test, or how confirmed>
- Layer: Game.Core.* / Game.Client.* / Editor-only
- Known limitations: <...>
```

**Extended report — emit ONLY when the requester asks for it.** It replaces the one-line `Known limitations` above with all three fields:
```
- Known limitations: <what the delivered networking setup does not cover>
- Latent concerns: <failure modes not yet triggered: topology assumptions, thresholds not yet reached, trade-offs knowingly deferred>
- Future remediation: <the concrete fix for each concern above, each with the condition that should trigger it>
```

## 7. Examples
**Example 1**
- Input: "Both host and clients need to see a shared health value update in real time, Client-Server topology."
- Output: `NetworkVariable<int> Health` on the entity's `NetworkBehaviour`, `NetworkVariableReadPermission.Everyone` / `NetworkVariableWritePermission.Server`. Damage math lives in `Game.Core.CombatMath`; the `NetworkBehaviour`'s `ServerRpc` calls it and writes the result to the variable, never computing damage itself, per `coding-principles.md`'s Shared Core integrity section and [state-sync.md](references/state-sync.md).

**Example 2**
- Input: "Just send the transform's position every frame with a ServerRpc, it's simpler than learning NetworkTransform."
- Output: declined — `NetworkTransform` already provides delta compression and interpolation for exactly this case; a hand-rolled per-frame RPC wastes bandwidth, reimplements what step 6 already covers, and has no interpolation, producing visibly choppier movement. Used `NetworkTransform` per [transform-latency.md](references/transform-latency.md) instead.

**Example 3**
- Input: "Feature must run in Distributed Authority mode, where any client can own and simulate its own object."
- Output: ownership assigned at spawn time to the owning client; `NetworkVariable` write permission follows the owner rather than the server, since DA mode lets the current owner write, per [distributed-authority.md](references/distributed-authority.md) and step 1. Flagged that this differs from the Client-Server default before writing any sync code, since assuming server-only writes here would silently reject the owner's own updates.

## 8. Edge cases & guardrails
- Never write game-rule logic (damage math, state machine transitions, economy formulas) inside a `NetworkBehaviour` — that belongs in `Game.Core.*` per `coding-principles.md`'s Shared Core integrity section; NGO code only carries the resolved value.
- Never call `GameObject.Instantiate`/`Destroy` directly on a `NetworkObject` prefab outside `NetworkObject.Spawn`/`Despawn` or a registered `INetworkPrefabInstanceHandler` — it desyncs `NetworkSpawnManager` and the object never appears on other peers.
- Never assume single-Editor Play Mode testing proves a networked feature works — ownership and RPC-direction bugs only surface with a real multi-client run; flag to `qa-automation-engineer`/`build-run-engineer` per step 9.
- Never build custom prediction/rollback machinery speculatively — `AnticipatedNetworkVariable<T>`/`AnticipatedNetworkTransform` exist for the measured case; adding them before latency correction is actually visible is the speculative complexity YAGNI already forbids.
- If the Tech Spec doesn't state Client-Server vs. Distributed Authority, ask rather than guess — it changes ownership and `NetworkVariable` write-permission semantics throughout the feature.

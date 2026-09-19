# Root Links — Netcode for GameObjects 2.13

Source: the root index pages listed below, as provided for this skill.
Covers: the whole skill — provenance and version anchor for every file in
this folder.

Anchors every link in this folder to `com.unity.netcode.gameobjects@2.13`
(installed point release 2.13.1). Anything this skill cites resolves under
one of these roots; anything that does not is out of scope for the skill,
not merely undocumented here.

| Root | Holds | Source |
|---|---|---|
| Manual | Concepts, components, topologies, workflows, tutorials | [Netcode for GameObjects Manual index](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/manual/index.html) |
| Scripting API | Every type in `Unity.Netcode`, `Unity.Netcode.Components`, `Unity.Netcode.Transports.UTP`, and their sibling namespaces | [Netcode for GameObjects API index](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/api/index.html) |

## Which file answers which question

| Question | File | Source |
|---|---|---|
| Client-Server or Distributed Authority — which topology, and how does ownership work | [core-architecture.md](core-architecture.md) | [Networking concepts](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/manual/networking-concepts.html) |
| The Tech Spec calls for Distributed Authority mode specifically | [distributed-authority.md](distributed-authority.md) | [Distributed authority topologies](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/manual/terms-concepts/distributed-authority.html) |
| How does a NetworkObject come into being, get pooled, or get hidden | [spawning-objects.md](spawning-objects.md) | [Spawning and despawning](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/manual/spawn-despawn.html) |
| NetworkVariable vs. Rpc, or a custom message | [state-sync.md](state-sync.md) | [NetworkVariables](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/manual/networkvariables-landing.html) |
| Transform/animation sync, interpolation, latency, ticks | [transform-latency.md](transform-latency.md) | [Latency and performance](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/manual/latency-performance.html) |
| A NetworkVariable or Rpc parameter needs a custom type | [serialization.md](serialization.md) | [Serialization](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/manual/serialization.html) |
| Loading/unloading scenes, or reconnecting a dropped client | [scene-session-management.md](scene-session-management.md) | [Scene management](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/manual/scene-management.html) |
| Choosing/configuring a transport, Relay, or debugging a networked feature | [transports-testing.md](transports-testing.md) | [Transports](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/manual/advanced-topics/transports.html) |

Every other link in this `references/` folder is a specific page under these
roots, pinned to `@2.13`, each verified to resolve before inclusion. Keep the
`@2.13` segment when following any link from this skill — a different
version's API may differ; substitute the installed version from
`Packages/manifest.json` if it has since moved past 2.13. Consult the live
site (or the FAQ/troubleshooting pages in
[transports-testing.md](transports-testing.md)) for anything not covered
here — Netcode for GameObjects adds features between releases, and
Distributed Authority mode in particular is still evolving fast.

# Root Links — Unity Transport 6.6

Source: the root index pages listed below, as provided for this skill.
Covers: the whole skill — provenance and version anchor for every file in
this folder.

Anchors every link in this folder to `com.unity.transport@6.6`. Anything this
skill cites resolves under one of these roots; anything that does not is out
of scope for the skill, not merely undocumented here.

| Root | Holds | Source |
|---|---|---|
| Manual | Concepts, workflows, best practices, FAQ, migration guide | [Unity Transport Manual index](https://docs.unity3d.com/Packages/com.unity.transport@6.6/manual/index.html) |
| Scripting API | Every type in `Unity.Networking.Transport` and its sibling namespaces, plus the `Unity.Netcode` interop types this package documents | [Unity Transport API index](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/index.html) |

## Which file answers which question

| Question | File | Source |
|---|---|---|
| How to create a driver, open a connection, or run the update loop | [core-driver-lifecycle.md](core-driver-lifecycle.md) | [Simple client and server](https://docs.unity3d.com/Packages/com.unity.transport@6.6/manual/client-server-simple.html) |
| Which pipeline stages to use, or how to test packet loss/latency | [pipelines-reliability-simulation.md](pipelines-reliability-simulation.md) | [Using pipelines](https://docs.unity3d.com/Packages/com.unity.transport@6.6/manual/pipelines-usage.html) |
| Moving the driver update into the Job System/Burst | [jobs-and-concurrent-api.md](jobs-and-concurrent-api.md) | [Jobified client and server](https://docs.unity3d.com/Packages/com.unity.transport@6.6/manual/client-server-jobs.html) |
| Encrypting traffic with TLS/DTLS | [security-and-encryption.md](security-and-encryption.md) | [Encrypted communications](https://docs.unity3d.com/Packages/com.unity.transport@6.6/manual/client-server-secure.html) |
| NAT traversal with Unity Relay, or cross-play considerations | [relay-and-cross-play.md](relay-and-cross-play.md) | [Cross-play support](https://docs.unity3d.com/Packages/com.unity.transport@6.6/manual/cross-play.html) |
| WebGL sockets, or wiring/writing a custom transport for NGO | [webgl-and-ngo-integration.md](webgl-and-ngo-integration.md) | [Using Netcode for GameObjects transports](https://docs.unity3d.com/Packages/com.unity.transport@6.6/manual/ngo-transports.html) |
| Reading connection statistics, logging, or troubleshooting a disconnect | [diagnostics-and-testing.md](diagnostics-and-testing.md) | [FAQ](https://docs.unity3d.com/Packages/com.unity.transport@6.6/manual/faq.html) |

Every other link in this `references/` folder is a specific page under these
roots, pinned to `@6.6`, each verified to resolve before inclusion. Keep the
`@6.6` segment when following any link from this skill — the API changed
substantially across major versions (see
[Migrating from 1.X](https://docs.unity3d.com/Packages/com.unity.transport@6.6/manual/migration.html)
in [webgl-and-ngo-integration.md](webgl-and-ngo-integration.md) if working
against an older project). Consult the live site for anything not covered
here.

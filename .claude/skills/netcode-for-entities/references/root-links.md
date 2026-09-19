# Root Links — Netcode for Entities 6.6.0

Source: the root index pages listed below, as provided for this skill.
Covers: the whole skill — provenance and version anchor for every file in
this folder.

Anchors every link in this folder to Netcode for Entities (NfE) 6.6.0 — the
DOTS/ECS server-authoritative-with-client-prediction networking package,
package id `com.unity.netcode`. This is **not** "Netcode for GameObjects"
(package `com.unity.netcode.gameobjects`), a separate, unrelated Unity
package with its own doc tree; do not follow a `com.unity.netcode.gameobjects`
link from this skill or treat its API as interchangeable with NfE's.

| Root | Holds | Source |
|---|---|---|
| Manual | Concepts, setup, ghosts, RPCs, prediction, host migration, testing, optimization | [Netcode for Entities Manual index](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/index.html) |
| Scripting API | `Unity.NetCode` namespace: components, systems, attributes | [Netcode for Entities API index](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/api/index.html) |

## Hard prerequisite

NfE is built on `Unity.Entities` (ECS/DOTS) — per the Manual index: "you must
know how to use ECS to use this package." Entity/component/system/query
modeling itself belongs to `unity-ecs-architecture`; this skill covers only
the networking layer built on top of it. Minimum Editor version **2022.3.0f1**
or a Unity 6 LTS; source-generator-compatible IDE (Visual Studio 2022+,
Rider 2021.3.3+).

## Which file answers which question

| Question | File | Source |
|---|---|---|
| How are client/server Worlds created and built (defines, targets)? | [setup-and-worlds.md](setup-and-worlds.md) | [Install](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/installation.html), [Set up client and server worlds](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/set-up-client-server-worlds.html) |
| How does a connection form, and how is it approved? | [transport-and-connection.md](transport-and-connection.md) | [Connecting server and clients](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/network-connection.html) |
| How is a networked entity declared and its fields replicated? | [ghost-authoring.md](ghost-authoring.md) | [Ghosts and snapshots](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/ghost-snapshots.html) |
| How does a ghost get created, pre-placed, or grouped? | [ghost-spawning-and-groups.md](ghost-spawning-and-groups.md) | [Spawn Ghosts](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/ghost-spawning.html) |
| A type isn't natively replicable, or needs a custom wire format | [ghost-serialization-templates.md](ghost-serialization-templates.md) | [Ghost Type Templates](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/ghost-types-templates.html) |
| Which call — one-off event or per-tick input? | [rpcs-and-commands.md](rpcs-and-commands.md) | [Communicating with RPCs](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/rpcs.html), [Command stream](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/command-stream.html) |
| How do client and server clocks agree, and how is a remote ghost smoothed? | [time-and-interpolation.md](time-and-interpolation.md) | [Time synchronization](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/time-synchronization.html), [Interpolation](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/interpolation.html) |
| How does the prediction/rollback loop actually run? | [prediction-core.md](prediction-core.md) | [Managing latency with prediction](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/prediction-n4e.html) |
| A prediction correction is visible, or a known edge case bit | [prediction-caveats.md](prediction-caveats.md) | [Prediction edge cases and known issues](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/prediction-details.html) |
| A predicted ghost needs physics, or client-only VFX physics | [physics-integration.md](physics-integration.md) | [Physics](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/physics.html) |
| The host can leave and the session must survive | [host-migration.md](host-migration.md) | [Host migration](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/host-migration/host-migration.html) |
| Something is wrong and needs to be observed, not guessed at | [testing-and-debugging.md](testing-and-debugging.md) | [Test and debug your game](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/testing/debugging.html) |
| Bandwidth or CPU cost needs to come down | [optimization-and-bandwidth.md](optimization-and-bandwidth.md) | [Optimize performance](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/optimizations.html) |
| The exact component/setting name is needed | [api-and-settings-reference.md](api-and-settings-reference.md) | [Netcode-specific components and types](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/entities-list.html), [Project Settings reference](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/project-settings.html) |

Keep the `@6.6` segment when following any link from this skill — earlier
NfE versions (0.x/1.x preview lines) use different APIs (e.g. `IAspect`-based
patterns, no host migration), and some page slugs from those versions do not
match 6.6's. Read the installed version from `Packages/manifest.json` and
substitute the segment if it differs, rather than assuming the pages match.
Consult the live site for anything not covered here — NfE adds features
between releases, and host migration in particular is still experimental
(see [host-migration.md](host-migration.md)).

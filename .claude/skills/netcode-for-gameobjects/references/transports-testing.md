# Transports and Testing — UnityTransport, Relay, Artificial Conditions, Troubleshooting

Sources: [a] manual/advanced-topics/singleplayer.html, [b] api/Unity.Netcode.Transports.UTP.UnityTransport.html, [c] manual/relay/relay.html, [d] manual/tutorials/testing/testing_with_artificial_conditions.html, [e] manual/tutorials/testing/testing_locally.html, [f] api/Unity.Netcode.TestHelpers.Runtime.NetcodeIntegrationTestHelpers.html, [g] manual/basics/logging.html, [h] api/Unity.Netcode.CommandLineOptions.html, [i] manual/tutorials/command-line-helper.html, [j] manual/troubleshooting/error-messages.html, [k] manual/learn/faq.html, [l] manual/tutorials/testing/techniques_and_tricks_for_debugging_multiplayer_games.html.

`NetworkManager`/`NetworkConfig`, connection approval and the player prefab: [core-architecture.md](core-architecture.md).

## Choosing a transport

| Transport | Fact that decides |
|---|---|
| `UnityTransport` | Default and recommended; set via NetworkManager **Select Transport** (`NetworkConfig.NetworkTransport`) |
| UNet Transport | Unsupported since Unity 2022.2 — never wire it |
| Custom / community | Any `NetworkTransport` subclass; community repo has Steam transports (client sets `ConnectToSteamID`, nothing else per [k]) |
| `SinglePlayerTransport` | Offline host with no network cost, no gameplay changes: add it to the NetworkManager GameObject, set `NetworkConfig.NetworkTransport` to it, `StartHost()`. `StartClient()` always returns `false`, `GetCurrentRtt` returns `0` — useless for multi-client verification; swap to `UnityTransport` before real networking [a] |
| `NetworkTransport` contract | `ServerClientId`, `IsSupported`, `Initialize(NetworkManager)`, `Shutdown()`, `StartServer()`, `StartClient()`, `Send(ulong, ArraySegment<byte>, NetworkDelivery)`, `PollEvent(out ulong, out ArraySegment<byte>, out float)`, `GetCurrentRtt(ulong)`, `DisconnectLocalClient()`, `DisconnectRemoteClient(ulong)`; `OnTransportEvent` replaces per-frame polling |

## UnityTransport configuration

| Member | Default | Fact |
|---|---|---|
| `MaxPacketQueueSize` | `128` | Send/receive queue cap before back-pressure |
| `MaxPayloadSize` | `6144` | Max bytes of one unreliable payload |
| `MaxSendQueueSize` | auto | Override manually if needed |
| `UseEncryption` | `false` | DTLS; needs `SetServerSecrets(cert, privateKey)` / `SetClientSecrets(serverCommonName, caCertificate = null)` (PEM) unless on Relay |
| `UseWebSockets` | `false` | `true` for WebGL |
| `SetConnectionData(string ip, ushort port, string listenAddress = null)` | — | Also `NetworkEndpoint` and `forceOverrideCommandLineArgs` overloads; only `forceOverride: true` beats `-ip`/`-port` on the command line, else the code value is silently ignored [b] |
| `ConnectionData` (`ConnectionAddressData`) | — | `Address`, `Port`, `ServerListenAddress` (unset → `localhost`), `ClientBindPort` (`0` = ephemeral), `WebSocketPath` (`"/"`) |

## Relay and internet play

| Fact | Detail |
|---|---|
| `SetRelayServerData` / `SetHostRelayData` / `SetClientRelayData` | Present in 2.13. Host variant after allocating, client variant after joining by code, then `Start*` [b] |
| Encryption | Relay is already secured — skip `UseEncryption` unless double encryption is wanted |
| Matchmaking | NGO has none; use a separate service [k] |
| Internet options | Relay; a cloud or self-hosted server with opened UDP ports; or a P2P transport (Steam) [k] |
| Doc gap | [c] defers to the Multiplayer Services (UGS) Relay manual for parameter lists, regions, connection-type strings and `RelayService.Instance.CreateAllocationAsync`/`JoinAllocationAsync` — confirm there before wiring |

## Local multi-instance and artificial conditions

| Method / member | Fact |
|---|---|
| Player builds | Several instances (with the Editor optional); Player Settings fullscreen mode **Windowed** so they coexist [i]. macOS: `open -n YourAppName.app` per instance |
| Multiplayer Play Mode | Up to 4 players in the Editor, no build [e] |
| ParrelSync | Third-party cloned Editors (e.g. clone hosts, primary is client), each debuggable separately |
| `UnityTransport.SimulatorParameters` | `PacketDelayMS`, `PacketJitterMS` (± per packet), `PacketDropRate` (%); all `int` |
| `SetDebugSimulatorParameters(int packetDelay, int packetJitter, int dropRate)` | `[Obsolete]` in 2.13 though the tutorial still shows it — use the Multiplayer Tools Network Simulator; gate leftovers behind `#if DEVELOPMENT_BUILD && !UNITY_EDITOR` [b] |
| Build restriction | Simulation works only in Editor/development builds — release builds ignore it [d] |
| Limits | Bi-directional only (no upload-only loss); system-wide tools hit every local instance alike |
| Test values (Boss Room) | 100–150 ms desktop, 200–300 ms mobile, 5–10% loss; 1000 ms to stress lag-hiding [l] |
| Breakpoints | Raise transport disconnect/heartbeat timeouts first, or the paused peer is dropped |

## NetcodeIntegrationTest

| Member | Fact |
|---|---|
| `NetcodeIntegrationTest` | Play Mode base class creating a server + N clients |
| `NumberOfClients` (abstract) | Client count |
| `m_ServerNetworkManager` / `m_ClientNetworkManagers` | Created managers |
| `OnServerAndClientsCreated()` | Configure `NetworkConfig` before start |
| `CanStartServerAndClients()` | Override for manual start timing |
| `m_EnableTimeTravel` | `MockTimeProvider`/`MockTransport` deterministic frames — faster, no wall-clock flakes; hook `OnTimeTravelServerAndClientsConnected()` |
| `NetcodeIntegrationTestHelpers.DefaultTimeout` | `4` s when no `TimeoutHelper` is passed [f] |
| `DefaultMinFrames` | `1` frame must pass even if the condition is already true |
| `WaitForClientConnected(ToServer)` / `WaitForClientsConnected(ToServer)` | Wait on connection state, not sleeps |
| `TimeoutHelper(float timeOutPeriod = 2)` | `k_DefaultTimeOutWaitPeriod = 2` s; `TimedOut`, `Start()`/`Stop()` |
| `WaitForConditionOrTimeOut(...)` | The generic wait, bounded by a `TimeoutHelper`; `NetcodeIntegrationTestHelpers.Create*` builds managers manually |

Connection scenarios to cover: new join; late join and reconnect reach the same state as original clients; approval denial ends cleanly; graceful and ungraceful (app close, timeout) disconnect reset session state; despawned-not-destroyed (pooled) behaviours reset; nothing leaks from before a host/server restart.

## Logging

| Member | Fact |
|---|---|
| `LogLevel` | `Developer` → `Normal` → `Error` → `Nothing`; read via `NetworkLog.CurrentLogLevel` |
| `NetworkLog.LogInfo` / `LogWarning` / `LogError` | Local only, Netcode prefix |
| `LogInfoServer` / `LogWarningServer` / `LogErrorServer` | On the server: local, sender `ServerClientId`, no packet. On a client: local, then sent to the server |
| `LogInfoSessionOwner` | Same, to the session owner ([distributed-authority.md](distributed-authority.md)) |
| Production | Client→server logs are forgeable and cost bandwidth — development only [g] |

## Command line

| Member | Fact |
|---|---|
| `CommandLineOptions.TryGetArg(string, out string) : bool` | Current API [h] |
| `CommandLineOptions.Instance` / `GetArg(string)` | `[Obsolete]` in 2.13 though the manual example still uses it — do not copy |
| `-ip` / `-port` | The only flags parsed automatically; code wins only via `SetConnectionData(..., forceOverride: true)` |
| `NetworkCommandLine` sample | Child of the NetworkManager GameObject; reads `-mode server`/`host`/`client` and calls `Start*` [i] |
| Launch | `MyGame.exe -logfile log-server.txt -mode server` plus `... -logfile log-client.txt -mode client`; one `-logfile` per instance. Dedicated server / CI: arguments override baked network settings |

## Troubleshooting

| Symptom | Cause / fix |
|---|---|
| `NullReferenceException` on `StartServer()`/`StartHost()`/`StartClient()`, or `NetworkManager.Singleton` null | No initialised `NetworkManager` in the scene |
| `NullReferenceException` calling a ServerRpc | Object not spawned — [spawning-objects.md](spawning-objects.md) |
| Dedicated server pegs a core at 100% | Uncapped updates — set `Application.targetFrameRate` (e.g. `30`) |
| `Can't find pending soft sync object. Is the projects the same?` | Server and client scene content differ [j] |
| `ArgumentNullException: Can't spawn null object Parameter name: netObject` | `Spawn()` on a null reference |
| `Only owner can invoke ServerRPC that is marked to require ownership` | Non-owner caller — gate client-side, or migrate to `[Rpc(SendTo.Server, InvokePermission = …)]` |
| `KeyNotFoundException: The given key wasn't present in the dictionary.` | ServerRpc ran on the host in an unhandled state — validate ownership/server state first |
| Listen vs dedicated server | Same code; branch on `IsServer`/`IsHost` |
| Adding to the prefab list after hosting | Allowed only if every client adds the identical prefab, else spawns fail to resolve [k] |

Unverified: numeric defaults of `HeartbeatTimeoutMS`, `ConnectTimeoutMS`, `MaxConnectAttempts`, `DisconnectTimeoutMS` and the default `LogLevel` are not in [b]/[g]; read them in the Inspector.

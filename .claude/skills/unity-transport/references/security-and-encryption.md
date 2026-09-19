# Security & Encryption — TLS/DTLS via SecureNetworkProtocolParameter

Source: [Encrypted communications](https://docs.unity3d.com/Packages/com.unity.transport@6.6/manual/client-server-secure.html), [FixedPEMString](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.TLS.FixedPEMString.html), [SecureClientAuthPolicy](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.TLS.SecureClientAuthPolicy.html), [SecureNetworkProtocolParameter](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.TLS.SecureNetworkProtocolParameter.html), [SecureParameterExtensions](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.TLS.SecureParameterExtensions.html).
Covers: SKILL.md §4 — **"Enable TLS via SecureNetworkProtocolParameter whenever traffic crosses the public internet"**.

This file owns transport-level encryption only — the certificate/key setup UTP
performs itself via `SecureNetworkProtocolParameter`. It does not cover Unity
Relay's own connection security model (Relay's own allocation/join security
handling), which lives in [relay-and-cross-play.md](relay-and-cross-play.md).

## Setting up encrypted communications

| Subject | What it decides | Source |
|---|---|---|
| Authentication direction | The server presents a certificate; each connecting client validates it against a root CA certificate before trusting the channel, then the server's private key backs the encrypted session | [Encrypted communications](https://docs.unity3d.com/Packages/com.unity.transport@6.6/manual/client-server-secure.html) |
| `serverName` / common-name match | The `serverName` a client passes in must equal the common name used to generate the server certificate, or certificate validation fails | [Encrypted communications](https://docs.unity3d.com/Packages/com.unity.transport@6.6/manual/client-server-secure.html) |
| Root CA consistency across platforms | Every client build that talks to the same server must embed the identical root CA certificate — a per-platform CA mismatch breaks validation for that platform only | [Encrypted communications](https://docs.unity3d.com/Packages/com.unity.transport@6.6/manual/client-server-secure.html) |
| Certificate distribution | The manual's own `SecureParameters.cs` boilerplate embeds PEM strings directly in code for illustration only; production client builds should not ship hardcoded certificates that way | [Encrypted communications](https://docs.unity3d.com/Packages/com.unity.transport@6.6/manual/client-server-secure.html) |

## SecureNetworkProtocolParameter fields

| Field | Type | What it holds | Source |
|---|---|---|---|
| `CACertificate` | `FixedPEMString` | Root CA certificate (PEM) used to validate the peer's certificate | [SecureNetworkProtocolParameter](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.TLS.SecureNetworkProtocolParameter.html) |
| `Certificate` | `FixedPEMString` | This side's own certificate (PEM) presented during the handshake | [SecureNetworkProtocolParameter](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.TLS.SecureNetworkProtocolParameter.html) |
| `PrivateKey` | `FixedPEMString` | This side's own private key (PEM) backing `Certificate` | [SecureNetworkProtocolParameter](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.TLS.SecureNetworkProtocolParameter.html) |
| `Hostname` | `FixedString512Bytes` | The certificate's common name; must agree with the peer's `serverName`/`clientName` argument | [SecureNetworkProtocolParameter](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.TLS.SecureNetworkProtocolParameter.html) |
| `ClientAuthenticationPolicy` | `SecureClientAuthPolicy` | Server-only: how strictly the server verifies a client certificate; defaults to `Optional` | [SecureNetworkProtocolParameter](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.TLS.SecureNetworkProtocolParameter.html) |
| `Validate()` | method → `bool` | Runs automatically when the parameter is added to `NetworkSettings`; returns `false` on malformed field data | [SecureNetworkProtocolParameter](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.TLS.SecureNetworkProtocolParameter.html) |

## SecureClientAuthPolicy — server-side mutual-TLS policy

| Member | Behavior | Source |
|---|---|---|
| `None` | Client certificate is not requested, so it is never verified | [SecureClientAuthPolicy](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.TLS.SecureClientAuthPolicy.html) |
| `Optional` (default) | Client certificate is requested but its validity is not verified | [SecureClientAuthPolicy](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.TLS.SecureClientAuthPolicy.html) |
| `Required` | Client certificate is requested and verified; the connection fails without a valid one | [SecureClientAuthPolicy](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.TLS.SecureClientAuthPolicy.html) |

## FixedPEMString capacity

| Subject | What it decides | Source |
|---|---|---|
| Max length | 16,383 characters per PEM string; the constructor throws `ArgumentException` if the source string is longer | [FixedPEMString](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.TLS.FixedPEMString.html) |
| Purpose | Fixed-size layout keeps the certificate/key usable from Burst-compiled code and UnityTLS native bindings, unlike a managed `string` | [FixedPEMString](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.TLS.FixedPEMString.html) |

## SecureParameterExtensions — wiring NetworkSettings

| Method | Adds | Source |
|---|---|---|
| `WithSecureClientParameters(...)` | Client-side `SecureNetworkProtocolParameter` — overloads for WebSocket-only (`serverName`), server-authenticated (`caCertificate` + `serverName`), and mutual-TLS (`certificate` + `privateKey` + `caCertificate` + `serverName`) | [SecureParameterExtensions](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.TLS.SecureParameterExtensions.html) |
| `WithSecureServerParameters(...)` | Server-side `SecureNetworkProtocolParameter` — base overload (`certificate` + `privateKey`), plus a mutual-TLS overload adding `caCertificate`, `clientName`, and `SecureClientAuthPolicy` | [SecureParameterExtensions](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.TLS.SecureParameterExtensions.html) |
| `GetSecureParameters(...)` | Reads back the `SecureNetworkProtocolParameter` already stored on a `NetworkSettings` instance | [SecureParameterExtensions](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.TLS.SecureParameterExtensions.html) |

## Enabling encryption on NetworkSettings

```csharp
using Unity.Networking.Transport;
using Unity.Networking.Transport.TLS;

// Server: present its certificate/private key so clients can authenticate it.
var serverSettings = new NetworkSettings();
serverSettings.WithSecureServerParameters(
    certificate: SecureParameters.MyGameServerCertificate,
    privateKey: SecureParameters.MyGameServerPrivateKey);
var serverDriver = NetworkDriver.Create(serverSettings);

// Client: validate the server's certificate against the CA and common name.
var clientSettings = new NetworkSettings();
clientSettings.WithSecureClientParameters(
    caCertificate: SecureParameters.MyGameClientCA,
    serverName: SecureParameters.ServerCommonName);
var clientDriver = NetworkDriver.Create(clientSettings);
```

Both extension methods build a `SecureNetworkProtocolParameter` and add it to
`NetworkSettings` internally; `NetworkDriver.Create` reads it back to
negotiate TLS (over `WebSocketNetworkInterface`) or DTLS (over the UDP
interface) during the handshake.

**Critical caveat**: `ClientAuthenticationPolicy` defaults to `Optional`. Adding
`SecureNetworkProtocolParameter` to a server's `NetworkSettings` encrypts the
channel and authenticates the *server* to clients, but does **not**
authenticate clients to the server unless this field is explicitly set to
`Required` via `WithSecureServerParameters`'s mutual-TLS overload — leaving it
at the default accepts encrypted connections from any client without ever
verifying who that client is.

## API index

| Type | Source |
|---|---|
| `SecureNetworkProtocolParameter` | [API](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.TLS.SecureNetworkProtocolParameter.html) |
| `SecureClientAuthPolicy` | [API](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.TLS.SecureClientAuthPolicy.html) |
| `FixedPEMString` | [API](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.TLS.FixedPEMString.html) |
| `SecureParameterExtensions` | [API](https://docs.unity3d.com/Packages/com.unity.transport@6.6/api/Unity.Networking.Transport.TLS.SecureParameterExtensions.html) |

# Security and encryption (TLS/DTLS)

Sources (`@6.6`): manual `client-server-secure`; API `TLS.SecureNetworkProtocolParameter`, `TLS.SecureClientAuthPolicy`, `TLS.FixedPEMString`, `TLS.SecureParameterExtensions`.

UTP negotiates TLS over `WebSocketNetworkInterface` and DTLS over the UDP interface during the handshake. Relay's own security is in `relay-and-cross-play.md`.

## Trust model

- The server presents a certificate; the client validates it against a root CA. The `serverName` the client passes must equal the common name of the server certificate or validation fails.
- Every client build for one server must embed the identical root CA. A per-platform mismatch breaks that platform only.
- The manual's `SecureParameters.cs` embeds PEM strings in code for illustration only. Do not ship them hardcoded. Never commit a real private key; load it from a secret store.

## SecureNetworkProtocolParameter

| Field | Holds |
|---|---|
| `CACertificate` | Root CA (PEM) used to validate the peer |
| `Certificate` | This side's certificate (PEM) |
| `PrivateKey` | This side's private key (PEM) |
| `Hostname` | Certificate common name; must agree with the peer's `serverName`/`clientName` |
| `ClientAuthenticationPolicy` | Server only; default `Optional` |
| `Validate()` | Runs when added to `NetworkSettings`; false on malformed data |

`FixedPEMString` holds at most 16,383 characters and its constructor throws `ArgumentException` beyond that. The fixed layout keeps it usable from Burst and UnityTLS.

`SecureClientAuthPolicy`:
- `None`: client certificate not requested.
- `Optional` (default): requested but not verified.
- `Required`: requested and verified; the connection fails without a valid one.

Default `Optional` encrypts the channel and authenticates the server, but does not authenticate clients. To authenticate clients, set `Required` through the mutual-TLS overload of `WithSecureServerParameters`.

## Wiring

`WithSecureClientParameters` overloads:
- WebSocket-only: `serverName`.
- Server-authenticated: `caCertificate` + `serverName`.
- Mutual TLS: `certificate` + `privateKey` + `caCertificate` + `serverName`.

`WithSecureServerParameters` overloads:
- Base: `certificate` + `privateKey`.
- Mutual TLS: adds `caCertificate`, `clientName`, `SecureClientAuthPolicy`.

`GetSecureParameters` reads back the stored parameter.

```csharp
var serverSettings = new NetworkSettings();
serverSettings.WithSecureServerParameters(certificate: serverCert, privateKey: serverKey);
var serverDriver = NetworkDriver.Create(serverSettings);

var clientSettings = new NetworkSettings();
clientSettings.WithSecureClientParameters(caCertificate: caCert, serverName: commonName);
var clientDriver = NetworkDriver.Create(clientSettings);
```

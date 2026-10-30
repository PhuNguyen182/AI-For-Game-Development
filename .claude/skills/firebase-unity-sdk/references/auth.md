# Auth and Server Identity

Sources: [a] `/auth/unity/start` (below the SKILL.md `Docs:` base), [b] https://github.com/firebase/firebase-unity-sdk/blob/main/auth/src/FirebaseUser.cs, [c] https://firebase.google.com/docs/auth/admin/verify-id-tokens, [d] https://firebase.google.com/docs/auth/admin/manage-sessions.

## Client (`Firebase.Auth`)

| Member | Fact that decides |
|---|---|
| `FirebaseAuth.DefaultInstance` | Only after the init gate [a] |
| `StateChanged` | Subscribe once, compare `CurrentUser` to the cached user; `-=` in `OnDestroy` [a] |
| Sign-in results | `Task<AuthResult>`; read `.User` [a] |
| `FirebaseUser.TokenAsync(bool forceRefresh)` | `Task<string>`; returns the cached token while it is believed valid; `true` always mints a new one [b] |
| `FirebaseUser.UserId` | Documented "Do NOT use this value to authenticate with your backend server" [b] |
| `UserMetadata.CreationTimestamp` / `LastSignInTimestamp` | `System.DateTime` UTC from 14.0.0 |

**Caveat:** `TokenAsync(true)` on every call adds a network round trip and quota use; `false` by default, `true` only after the server rejects a token as expired.

## Token lifetime [d]

| Subject | Fact |
|---|---|
| ID token | Lasts one hour; refreshed from the refresh token |
| Refresh token | Persists until the user is deleted or disabled, or a major account change (password, email) |
| Revocation | `revokeRefreshTokens(uid)` server-side; password reset also revokes |

## Server contract (implemented by `backend-engineer`)

| Check | Fact that decides |
|---|---|
| Admin SDK `verifyIdToken(idToken)` | Checks format, expiry and signature; returns the decoded token, uid from it [c] |
| Revocation | Not checked by default; pass `checkRevoked: true` (extra round trip); Node error `auth/id-token-revoked` → reauthenticate [c][d] |
| Third-party JWT library | Header `alg` = `RS256`, `kid` matches a key from the securetoken@system.gserviceaccount.com x509 endpoint; payload `exp` future, `iat` and `auth_time` past, `aud` = project id, `iss` = `https://securetoken.google.com/<projectId>`, `sub` non-empty (the uid); refresh keys by `Cache-Control` `max-age` [c] |

**Caveat:** verification failure fails closed — reject the request, never fall back to a uid in the body (`core.md` → Security).

```csharp
// Client: identity travels only as a verifiable token.
string idToken = await user.TokenAsync(false).AsUniTask();
request.SetRequestHeader("Authorization", "Bearer " + idToken);
```

Unverified: the exact Unity anonymous sign-in member name (linked guide not fetched).

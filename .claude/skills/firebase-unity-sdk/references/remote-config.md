# Remote Config

Sources: [a] `/remote-config/unity/get-started` (below the SKILL.md `Docs:` base), [b] https://github.com/firebase/firebase-unity-sdk/blob/main/remote_config/src/FirebaseRemoteConfig.cs, [c] same folder `ConfigSettings.cs`, [d] https://firebase.google.com/docs/remote-config/loading, [e] https://firebase.google.com/docs/remote-config/quotas-limits.

## API (`FirebaseRemoteConfig.DefaultInstance`) [b]

| Member | Fact that decides |
|---|---|
| `SetDefaultsAsync(IDictionary<string, object>)` | Replaces all previously set defaults — one call with every key, not one per feature; non-string values convert to the key's type [a][b] |
| `FetchAndActivateAsync()` | `Task<bool>`: `true` only if this call activated new values; `false` on failed fetch or already active — `false` is not an error |
| `FetchAsync()` / `FetchAsync(TimeSpan cacheExpiration)` | Caches only; nothing changes until `ActivateAsync()`; cached data newer than `cacheExpiration` skips the network; `TimeSpan.Zero` always fetches |
| `ActivateAsync()` | `Task<bool>`; `false` when already activated |
| `EnsureInitializedAsync()` | `Task<ConfigInfo>`; await it so Set/Get calls do not block |
| `SetConfigSettingsAsync(ConfigSettings)` | Applies fetch interval and timeout |
| `GetValue(string key)` | `ConfigValue`; `.Source` tells static default vs remote; convert with `.BooleanValue`, `.LongValue`, `.DoubleValue`, `.StringValue` |
| `Info.LastFetchStatus` | Check before trusting fetched data [a] |
| `OnConfigUpdateListener` | Real-time updates (SDK 11.0.0+ on Android/Apple); first `+=` opens the stream, last `-=` closes it; handler must call `ActivateAsync()`; unsubscribe in `OnDestroy` [a][b] |

## Intervals and limits

| Setting | Value |
|---|---|
| `ConfigSettings.MinimumFetchIntervalInMilliseconds` | Default 12 hours [c]; fetches inside it return the last fetched values |
| `FetchAsync()` default cache expiration | 12 hours (`DefaultCacheExpiration`) [b] |
| `ConfigSettings.FetchTimeoutInMilliseconds` | Default 60 seconds [c] — too long for a startup wait [d] |
| Real-time listener | Bypasses the minimum fetch interval [d] |
| Parameters per template | 3,000 client [e] |
| Key | ≤256 characters, starts with `_` or an ASCII letter [e] |
| All value strings, project-wide | 1,000,000 characters [e] |
| Conditions | 2,000 per project [e] |

**Caveat:** a zero interval ships throttling to every player; gate it on a development-only scripting define so no release candidate can carry it.

## Loading strategies [d]

| Strategy | Use when |
|---|---|
| Activate on next launch: activate cached values at start, fetch in background, apply next launch | Default; no startup wait, no mid-session value change |
| Loading screen + `FetchAndActivateAsync` with own timeout | A value must be current before the first scene (event window, kill switch) |
| Real-time listener + `ActivateAsync` at a safe point | Values may change mid-session without breaking state |

```csharp
// Loading-screen case only (the default is next-launch activation): defaults first, then a bounded fetch.
await remoteConfig.SetDefaultsAsync(ConfigDefaults.All).AsUniTask();
bool activated = await remoteConfig.FetchAndActivateAsync().AsUniTask()
    .Timeout(StartupFetchTimeout);
```

Unverified: the `ConfigValue` member names (`Source`, `BooleanValue`, `LongValue`, `DoubleValue`, `StringValue`) — the get-started page names `GetValue` only; client fetch throttling thresholds (the throttling page did not state numbers); whether `UniTask.Timeout` leaves the underlying fetch running after it throws.

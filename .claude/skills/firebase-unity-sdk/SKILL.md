---
name: firebase-unity-sdk
description: "Firebase Unity SDK: EDM, CheckAndFixDependenciesAsync, google-services.json, Analytics SetConsent/SetAnalyticsCollectionEnabled, Remote Config SetDefaultsAsync/FetchAndActivateAsync, Crashlytics, Auth TokenAsync. Use when integrating Firebase."
user-invocable: false
---

# Firebase Unity SDK

Not for: choosing the analytics stack (`analytics-telemetry-platform`), whether remote config is warranted and its cadence (`live-ops-content-pipeline`), consent/ATT ordering and child-audience flags (`consent-att-init-order`), production crash triage (`crash-anr-reporting-gate`, `crash-anr-symbolication`), tester builds (`firebase-app-distribution`), Firestore/Functions and server-side token verification code (`backend-engineer`), receipt validation (`iap-server-receipt-ledger`).
Docs: https://firebase.google.com/docs/unity — pinned Firebase Unity SDK `14.1.0` (2026-10-23); 14.0.0 raised the floor to Unity 2022.3, Android minSdk 24, and iOS dependencies via Swift Packages instead of CocoaPods. Read the installed version before trusting a signature.

| Reference | Read when |
|---|---|
| [setup-edm4u.md](references/setup-edm4u.md) | Installing or upgrading Firebase, a resolver error, a mixed-version build, placing config files, or writing the init bootstrap |
| [analytics.md](references/analytics.md) | Logging an event, setting a user property, or turning collection on after consent |
| [remote-config.md](references/remote-config.md) | Adding a remote key, a value reading stale or default, or fetch throttling |
| [crashlytics.md](references/crashlytics.md) | Crashes missing from the console, unreadable IL2CPP frames, or crash opt-in |
| [auth.md](references/auth.md) | Signing a player in, or sending identity to a backend |

## Steps
1. **Products or platforms unstated → `Blocked`**, naming what is missing. Config source unstated → integrate against the documented config files (step 3) and list `Config required:` (ids and where supplied, never values). Scope is setup + Analytics, Remote Config, Crashlytics, Auth.
2. **One version, one install method, one dependency manager.** Every Firebase package at the same version, all `.unitypackage` or all UPM, one copy of the dependency manager. Any mismatch → remove all Firebase packages and reinstall at one version before debugging anything else. Unity 2022.3+ → Unity's External Dependency Manager package (EDM4U was archived 2026-10-26). Unity below 2022.3 → stay on 13.x and record it in Known limitations. Per [setup-edm4u.md](references/setup-edm4u.md).
3. **CONFIG FILES** — `google-services.json` / `GoogleService-Info.plist` go in `Assets/`; whether they may be committed is decided by `secret-and-supply-chain-scan` (steps 3–4: allowlisted only while the API key is restricted to Firebase APIs). A service-account JSON or Admin SDK credential never enters the client project (`core.md` → Security). Unconfirmed key restriction → treat as secret and report `Needs Confirmation`. Per [setup-edm4u.md](references/setup-edm4u.md).
4. **One bootstrap owns `FirebaseApp.CheckAndFixDependenciesAsync()`; every Firebase call waits for `DependencyStatus.Available`.** No `FirebaseApp.DefaultInstance`, `Crashlytics.*` or other Firebase static is touched earlier — it triggers initialization outside the gate. Any other status → Firebase features off, error logged once, the game still runs. Await via `.AsUniTask()` or `ContinueWithOnMainThread` (`unitask-async-programming`); never a bare `ContinueWith` that touches Unity objects. Where the bootstrap runs relative to consent is decided by `consent-att-init-order` step 3. Per [setup-edm4u.md](references/setup-edm4u.md).
5. **Firebase types live only in Client code, behind one interface per product that gameplay calls** (`csharp.md` → Boundaries). Core never sees a Firebase namespace.
6. **Analytics collection is off in the build and follows `AnalyticsStorage` after consent resolves.** Build-time off key on both platforms (Android `firebase_analytics_collection_enabled` = `false`, iOS `FIREBASE_ANALYTICS_COLLECTION_ENABLED` = `NO`). At `consent-att-init-order` step 3 (d) — after ATT and after `Available`: `SetConsent` with all four types, each from the source named in [analytics.md](references/analytics.md), then `SetAnalyticsCollectionEnabled(<AnalyticsStorage granted>)`. Both persist, so every consent change, withdrawal included, calls both again. Source of a type unnamed → `Needs-decision`; never default it to granted.
7. **Events follow the schema `sdk-platform-engineer` owns;** no PII in event params, user properties or `SetUserId` (`core.md` → Security). Criterion: a new event fits the 500-type and 25-property limits, or the schema owner decides what goes. Per [analytics.md](references/analytics.md).
8. **Remote Config: `SetDefaultsAsync` with every key before the first read, then the loading strategy from the table in [remote-config.md](references/remote-config.md)** — activate cached values at start and fetch for the next launch by default; `FetchAndActivateAsync` behind a startup timeout only for the loading-screen case. Each default ships in the build (`live-ops-content-pipeline` step 3); reads go through the one config access module (same skill, step 9). A zero fetch interval only in development builds.
9. **Crashlytics: set `ReportUncaughtExceptionsAsFatal = true` after `Available`** (default `false`). Crashlytics collects from first launch unless switched off at build time. Opt-in required (audience or jurisdiction per `consent-att-init-order` step 1) → ship the native off keys (Android `firebase_crashlytics_collection_enabled` = `false`, iOS `FirebaseCrashlyticsCollectionEnabled` = `false`), set `IsCrashlyticsCollectionEnabled` from consent, and confirm on a device build that no report is sent before consent; not confirmed → `Needs-decision`, gap in Known limitations. Android IL2CPP symbols upload from the pipeline (`ci-cd-engineer`). Done = a forced test crash from a device build appears in the console; until then report `Verified: not run`. Per [crashlytics.md](references/crashlytics.md).
10. **Auth: the backend learns who the player is only from an ID token it verifies.** `TokenAsync(false)` before each authenticated call, sent over HTTPS in a header; never `UserId` or any uid in a payload as identity. Server verification is `backend-engineer`'s; this side supplies the token and handles a rejected one by refreshing once, then signing out. Per [auth.md](references/auth.md).

## Never
- Disable iOS method swizzling — Firebase features that depend on it break silently.
- Add the Gemini Developer API or any billable non-Firebase API to the key in the config files — the key ships in every build.
- Report an integration done from Editor play mode — the Editor runs the desktop stub, not the Android/iOS SDK.

## Output
```
## Firebase Unity SDK — <project>
- SDK version / install method / dependency manager: <14.x.y> / <.unitypackage | UPM> / <Unity EDM | EDM4U>
- Products: <Analytics, Remote Config, Crashlytics, Auth — each wired | not in scope>
- Init gate: <bootstrap path> — Available-gated: yes/no
- Config files: <committed per secret-and-supply-chain-scan | held out, Needs Confirmation>
- Consent wiring: Analytics off in build, follows AnalyticsStorage after <consent-att-init-order hook>; consent type sources: <per type>
- Crashlytics collection: <default-on, opt-in not required | off until consent, device-confirmed yes/no>
- Remote Config: defaults all keys | gap: <keys>; strategy: <next launch | loading screen | real-time>
- Auth to backend: ID token in <header> — verified server-side by <backend-engineer endpoint>
- Config required: <ids and where supplied>
- Verified: <device build + console evidence, or "not run">
- Known limitations: <...>
```

## Example
- "Send `auth.CurrentUser.UserId` with the reward claim so the server knows who it is" → declined: any client can write any uid, and the SDK documents `UserId` as not for backend auth; sent `TokenAsync(false)` in the `Authorization` header for `backend-engineer` to verify.

---
name: firebase-unity-sdk
description: "Firebase Unity SDK: EDM, google-services.json, Remote Config, Crashlytics, Auth, SetConsent. Use to integrate Firebase."
user-invocable: false
---

# Firebase Unity SDK

- **Not for:** choosing the analytics stack (`analytics-telemetry-platform`).
- **Not for:** whether remote config is warranted and its cadence (`live-ops-content-pipeline`).
- **Not for:** consent/ATT ordering and child-audience flags (`consent-att-init-order`).
- **Not for:** production crash triage (`crash-anr-reporting-gate`, `crash-anr-symbolication`).
- **Not for:** tester builds (`firebase-app-distribution`).
- **Not for:** Firestore/Functions and server-side token verification code (`backend-engineer`).
- **Not for:** receipt validation (`iap-server-receipt-ledger`).
- **Docs:** https://firebase.google.com/docs/unity — pinned Firebase Unity SDK `14.1.0` (2026-10-23).
  - **Version caveat:** 14.0.0 raised the floor to Unity 2022.3, Android minSdk 24, and iOS dependencies via Swift Packages instead of CocoaPods.
  - **Signatures:** read the installed version before trusting one.

## References
- **[setup-edm4u.md](references/setup-edm4u.md):** Installing or upgrading Firebase, a resolver error, a mixed-version build, placing config files, or writing the init bootstrap.
- **[analytics.md](references/analytics.md):** Logging an event, setting a user property, or turning collection on after consent.
- **[remote-config.md](references/remote-config.md):** Adding a remote key, a value reading stale or default, or fetch throttling.
- **[crashlytics.md](references/crashlytics.md):** Crashes missing from the console, unreadable IL2CPP frames, or crash opt-in.
- **[auth.md](references/auth.md):** Signing a player in, or sending identity to a backend.

## Scripts
- **[FirebaseBootstrap.cs](scripts/FirebaseBootstrap.cs):** adapt into `Assets/_Project/Scripts/Platform/DataControllers/FirebaseBootstrap.cs` → the init gate exposing `IsAvailable`.

## Steps
1. **Products or platforms unstated → `Blocked`:** naming what is missing.
   - **Config source unstated:** integrate against the documented config files (step 3) and list `Config required:` (ids and where supplied, never values).
   - **Scope:** setup + Analytics, Remote Config, Crashlytics, Auth.
2. **One version, one install method, one dependency manager:** per [setup-edm4u.md](references/setup-edm4u.md).
   - **Any mismatch:** remove all Firebase packages and reinstall at one version before debugging anything else.
   - **Unity 2022.3+:** Unity's External Dependency Manager package (EDM4U is archived).
   - **Unity below 2022.3:** stay on 13.x and record it in Known limitations.
3. **CONFIG FILES:** `google-services.json` / `GoogleService-Info.plist` go in `Assets/`, per [setup-edm4u.md](references/setup-edm4u.md).
   - **Commit:** decided by `secret-and-supply-chain-scan` (steps 3–4: allowlisted only while the API key is restricted to Firebase APIs).
   - **Service-account JSON or Admin SDK credential:** never enters the client project (`core.md` → Security).
   - **Key restriction unconfirmed:** treat as secret and report `Needs Confirmation`.
4. **One bootstrap owns `FirebaseApp.CheckAndFixDependenciesAsync()`; every Firebase call waits for `DependencyStatus.Available`:** per [setup-edm4u.md](references/setup-edm4u.md).
   - **Earlier access:** no `FirebaseApp.DefaultInstance`, `Crashlytics.*` or other Firebase static is touched earlier.
   - **Any other status:** Firebase features off, error logged once, the game still runs.
   - **Await:** via `.AsUniTask()` or `ContinueWithOnMainThread` (`unitask-async-programming`); never a bare `ContinueWith` that touches Unity objects.
   - **Consent order:** where the bootstrap runs relative to consent is decided by `consent-att-init-order` step 3.
5. **Firebase types live only in Client code, behind one interface per product that gameplay calls:** `csharp.md` → Boundaries.
   - **Core:** never sees a Firebase namespace.
6. **Analytics collection is off in the build and follows `AnalyticsStorage` after consent resolves:** per [analytics.md](references/analytics.md).
   - **Build-time off key, both platforms:** Android `firebase_analytics_collection_enabled` = `false`, iOS `FIREBASE_ANALYTICS_COLLECTION_ENABLED` = `NO`.
   - **When:** at `consent-att-init-order` step 3 (d) — after ATT and after `Available`.
   - **Calls:** `SetConsent` with all four types, each from the source named in [analytics.md](references/analytics.md), then `SetAnalyticsCollectionEnabled(<AnalyticsStorage granted>)`.
   - **Persistence:** both persist, so every consent change, withdrawal included, calls both again.
   - **Source of a type unnamed:** `Needs-decision`; never default it to granted.
7. **Events follow the schema `sdk-platform-engineer` owns:** no PII in event params, user properties or `SetUserId` (`core.md` → Security).
   - **Criterion:** a new event fits the event-type and user-property limits in [analytics.md](references/analytics.md), or the schema owner decides what goes.
8. **Remote Config: `SetDefaultsAsync` with every key before the first read, then the loading strategy from the table in [remote-config.md](references/remote-config.md):**
   - **Defaults:** each ships in the build (`live-ops-content-pipeline` step 3).
   - **Reads:** go through the one config access module (`live-ops-content-pipeline` step 9).
   - **Zero fetch interval:** development builds only.
9. **Crashlytics: set `ReportUncaughtExceptionsAsFatal = true` after `Available`:** default is `false`; per [crashlytics.md](references/crashlytics.md).
   - **Opt-in required (audience or jurisdiction per `consent-att-init-order` step 1):** ship the native off keys from [crashlytics.md](references/crashlytics.md).
   - **Opt-in consent:** set `IsCrashlyticsCollectionEnabled` from consent.
   - **Opt-in confirmation:** confirm on a device build that no report is sent before consent; not confirmed → `Needs-decision`, gap in Known limitations.
   - **Android IL2CPP symbols:** upload from the pipeline (`ci-cd-engineer`).
   - **Done:** a forced test crash from a device build appears in the console; until then report `Verified: not run`.
10. **Auth: the backend learns who the player is only from an ID token it verifies:** per [auth.md](references/auth.md).
    - **Token:** `TokenAsync(false)` before each authenticated call, sent over HTTPS in a header.
    - **Identity:** never `UserId` or any uid in a payload as identity.
    - **Server verification:** `backend-engineer`'s; this side supplies the token.
    - **Rejected token:** refresh once, then sign out.

## Never
- **Method swizzling:** disable iOS method swizzling — Firebase features that depend on it break silently.
- **Billable non-Firebase APIs on the key:** add the Gemini Developer API or any billable non-Firebase API to the key in the config files — the key ships in every build.
- **Editor-only evidence:** report an integration done from Editor play mode — the Editor runs the desktop stub, not the Android/iOS SDK.

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
```

## Example
- **"Send `auth.CurrentUser.UserId` with the reward claim so the server knows who it is":** declined.
  - **Why:** any client can write any uid, and the SDK documents `UserId` as not for backend auth.
  - **Did instead:** sent `TokenAsync(false)` in the `Authorization` header for `backend-engineer` to verify.

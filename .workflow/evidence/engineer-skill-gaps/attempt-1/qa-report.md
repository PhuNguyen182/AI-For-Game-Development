# QA report — engineer-skill-gaps, attempt 1

- Executor: QA executor (general-purpose), 2026-10-29. Plan: qa-lead (a)–(d). Read-only except this file.
- Paths below are relative to `.claude/skills/` unless they start with `.claude/` or `.workflow/`. `SKILL:n` = that skill's `SKILL.md` line n.
- Review status of the work under test: review closed (round 3, security Clear, code-reviewer A resolved, B Approve); R3-1 fix not re-reviewed (feature Known limitations).

## (a) Criterion map

### Spec 1 — save-data-versioning-migration
| Criterion | Evidence | Verdict |
|---|---|---|
| Header with schema version + checksum | save-data-versioning-migration/SKILL:20 "hand-written header (magic, envelope version, schema version, save counter, payload length, SHA-256 over header and payload)"; references/version-envelope-and-chain.md:9-17 | met |
| Chain of sequential pure vN→vN+1 steps | SKILL:21 "add one step `V{N}ToV{N+1}`"; SKILL:22 "Write each step as a pure function in `Game.Core.Save`"; version-envelope-and-chain.md:75-93 (constructor throws on gap) | met |
| A shipped step is never edited | SKILL:21 "`SaveV{N}` and every shipped step stay byte-for-byte … A defect in a shipped step gets a new repair step" | met |
| Newer save refused, never overwritten | SKILL:23 "Schema newer than the build → refuse: no overwrite, no save, no cloud upload this session"; version-envelope-and-chain.md:37 "a `TooNew` main file is never replaced" | met |
| Atomic write (temp + swap) | SKILL:25 "temp file in the same directory, `Flush(true)`, then `File.Replace` … Never write over the live file in place" | met |
| Pre-migration backup kept | SKILL:24 "copy the untouched bytes to the per-version backup first … the backup stays until the next clean load"; version-envelope-and-chain.md:127 | met |
| One golden fixture per shipped version, no PII | SKILL:27 "Commit one golden fixture per shipped schema version … synthetic data only"; golden-save-fixtures.md:23-24 | met |
| Fixture feeds `release` step 8 | SKILL:27 "That test is the evidence for `release` step 8"; golden-save-fixtures.md:40-47 | met |
| Agrees with memorypack step 11 | SKILL:21 "(agrees with `memorypack-serialization` step 11)"; memorypack-serialization/SKILL:24 "it is a migration (versioned successor type plus upgrade path), not an edit" | met |
| DTOs + chain in `Game.Core.Save`; I/O + cloud sync in `Game.Client.*` | SKILL:22 (`Game.Core.Save`); SKILL:25 "Write atomically in `Game.Client.*`"; SKILL:26 "Sync cloud copies … from `Game.Client.*`" | met |

### Spec 2 — iap-server-receipt-ledger
| Criterion | Evidence | Verdict |
|---|---|---|
| Never credits from client product/amount or local `CrossPlatformValidator` | SKILL:22 "Never credit from a client-sent product, amount or price, or from a local `CrossPlatformValidator` result" | met |
| Idempotency key = store transaction id | SKILL:24 "Key the ledger on the store transaction id — Play `purchaseToken` … Apple `transactionId`" | met |
| Grant + ledger entry in one transaction | SKILL:25 "Commit grant and ledger entry in one transaction"; UGS custom path → `Needs-decision`, `Next: cto` (GD-visible in Log #6) | met |
| Client confirms only after server ack | SKILL:27 "Unity IAP `ConfirmPurchase` only on `granted` or `already granted`" | met |
| Refund/void reverses the grant | SKILL:28 "Reverse grants per void event" | met |
| Verification failure fails closed | SKILL:23 "any exception → no grant, no consume/acknowledge … never catch-and-grant" | met |
| Server credentials by secret-store id only | SKILL:29 "Name the secret id in the backend's secret store, never a value" | met |
| `Unverified:` line in each vendor reference | google-play-developer-api.md:70, app-store-server-api.md:65, firebase-functions-firestore.md:103, ugs-cloud-code-economy.md:74 — each begins `Unverified:` | met |

### Spec 3 — firebase-unity-sdk
| Criterion | Evidence | Verdict |
|---|---|---|
| Every call gated on `CheckAndFixDependenciesAsync` → `Available` | SKILL:24 "every Firebase call waits for `DependencyStatus.Available`. No `FirebaseApp.DefaultInstance`, `Crashlytics.*` … touched earlier" | met |
| All Firebase packages on one version | SKILL:22 "Every Firebase package at the same version" | met |
| Remote Config in-build defaults | SKILL:28 "`SetDefaultsAsync` with every key before the first read … Each default ships in the build" | met |
| Analytics collection off until consent | SKILL:26 "Analytics collection is off in the build and follows `AnalyticsStorage` after consent resolves" | met |
| Auth sends ID token, never a uid in a payload | SKILL:30 "`TokenAsync(false)` … sent over HTTPS in a header; never `UserId` or any uid in a payload as identity" | met |
| Config files per `secret-and-supply-chain-scan` | SKILL:23 "whether they may be committed is decided by `secret-and-supply-chain-scan` (steps 3–4 …)" | met |

### Spec 4 — consent-att-init-order
| Criterion | Evidence | Verdict |
|---|---|---|
| Order consent → ATT → SDK init | SKILL:21 "(b) UMP … (c) iOS ATT; (d) Firebase … (e) … ad SDK and mediation init" | met |
| No ad/analytics SDK starts before consent resolves | SKILL:21 main path complies, but SKILL:21 also permits "Firebase bootstrap may move before (b) only when the Analytics and Crashlytics build-time off keys ship … Firebase Installations and Remote Config/Auth traffic then precede consent" | unsupported (optional path) — DEF-1 |
| ATT requested only while app active | SKILL:24 "ATT only while the app is active, after the UMP form closes" | met |
| Audience unstated → `Needs-decision` (matches ad-mediation step 8) | SKILL:19 "Unstated → `Needs-decision` … (same gate as `ad-mediation-monetization-platform` step 8)"; ad-mediation-monetization-platform/SKILL:19 "Audience or jurisdictions unstated → `Needs-decision`" | met |
| Privacy-options entry point required | SKILL:26 "Privacy-options entry point is required" | met |
| Store policy via WebFetch | SKILL:20 "Fetch current store policy with `WebFetch` before writing" | met |

### Spec 5 — server-authoritative-validation
| Criterion | Evidence | Verdict |
|---|---|---|
| Identity/ownership never from payload | SKILL:20 "Take the sender from the transport, never the payload"; SKILL:21 "resolve each reference server-side and compare its owner with the sender" | met |
| Validate via `Game.Core.*` before any state change | SKILL:23 "mutates only on its accept" | met |
| Per-connection rate limit with stated budget | SKILL:24 "Apply a per-connection rate limit with a stated budget" | met |
| Rejection answers with authoritative state, leaks nothing | SKILL:25 "Reject with authoritative state, leak nothing" | met |
| Untrusted reads use `*Safe` APIs | SKILL:22 "reads with `TryBeginRead`/`ReadValueSafe` after the limiter" | met |
| Output has `Rejection behaviour:` | SKILL:43 "- Rejection behaviour: <reply: reason code + authoritative state …>" | met |

### Spec 6a — mobile-safe-area
| Criterion | Evidence | Verdict |
|---|---|---|
| `Screen.safeArea` on one content root | SKILL:18 "exactly one safe-area node per root Canvas or panel" | met |
| Backgrounds full-bleed | SKILL:18 "keep backgrounds full-bleed" | met |
| Re-applied only on safe-area/orientation/resolution change | SKILL:22 "compare the cached `safeArea` `Rect`, `width`/`height` and `orientation` each frame and write only when one differs" | met |
| UI Toolkit via panel-space conversion | SKILL:21 "convert with `RuntimePanelUtils.ScreenToPanel(panel, p)`" | met |
| Verified per target device in Device Simulator | SKILL:25 "Verify in the Device Simulator per target device × orientation" | met |

### Spec 6b — unity-localization-text
| Criterion | Evidence | Verdict |
|---|---|---|
| Await `InitializationOperation` before first read | SKILL:22 "Await `LocalizationSettings.InitializationOperation` before the first code read, and check it succeeded" | met |
| No hard-coded player-facing strings | SKILL:21 "Every player-facing string comes from a String Table" | met |
| One fallback font per script with atlas memory cost | SKILL:25 "One font asset per script, with its atlas cost stated … Never two assets covering one script … script → asset → mode → atlas size → MB" | met |
| Pseudo-locale expansion check | SKILL:27 "Run the pseudo-locale check on every screen … Expander (default rules)" | met |
| RTL stated as a limitation | SKILL:9 "RTL shaping and mirrored layout (no owner — known limitation)"; SKILL:46 "Known limitations: RTL locales excluded" | met |

### Spec 7 — core-scene-integration
| Criterion | Evidence | Verdict |
|---|---|---|
| One named tick owner (VContainer `IFixedTickable` / one MonoBehaviour / netcode stack) | SKILL:18 "multiplayer on … the netcode stack owns the tick … VContainer … one `IFixedTickable` … no VContainer → one driver MonoBehaviour" | met |
| Core gets injected time, never `Time.deltaTime` | SKILL:19 "Core never reads `Time.*`"; SKILL:30 Never `Time.deltaTime` | met |
| Views read Core state, never write it | SKILL:24 "Views read Core state, never write it" | met |
| Interpolation between snapshots render-only | SKILL:25 "never feed the interpolated value back to Core or physics" | met |
| Input sampled into a per-tick command struct | SKILL:20 "Sample input into one per-tick command struct" | met |
| Physics results reach Core as plain data | SKILL:22 "raycasts, overlaps and contacts become Core structs … Core never sees `Collider`, `GameObject` or `Vector3`" | met |

### Spec 8a — core-determinism
| Criterion | Evidence | Verdict |
|---|---|---|
| Step 1 gate: is cross-machine agreement needed | SKILL:19 "Gate: decide whether cross-machine agreement is needed at all" | met |
| Float vs fixed-point → `technical-architect` (one system) or `cto` (library); no library named | SKILL:20 "One system → `technical-architect`; a fixed-point library … → `cto` (`/decide`). Name no library."; grep for FixMath/Fix64/libfixmath/BEPU/Quantum in the folder: no hits | met |
| Forbids persisting `string.GetHashCode` | stable-hashing-and-ordering.md:9 "never persist it"; :14 "forbidden uses in Core: persisted in a save, sent in a message …" (SKILL:22 step 4 routes there) | met |
| Hash-collection order never decides an outcome | stable-hashing-and-ordering.md:75-76; SKILL:22 "each hash-collection iteration … is either order-independent … or ordered by a total, stable key" | met |
| Replay test compares a per-tick state hash | SKILL:24 "per-tick state-hash replay test … bit-exact hash per tick" | met |

### Spec 8b — core-tests-without-unity
| Criterion | Evidence | Verdict |
|---|---|---|
| Core asmdef `noEngineReferences` | SKILL:17 "Check `Game.Core.asmdef` has `noEngineReferences: true`" | met |
| `Game.Core.Tests` in Edit Mode by default | SKILL:18 "Run Core tests from `Game.Core.Tests` in Edit Mode by default" | met |
| Mirror links the same sources, pinned language version | SKILL:21 "link the same `Assets/` sources, never copy; pin `LangVersion`"; dotnet-test-mirror.md:30,37 | met |
| Mirror only when tech-stack.md or an ADR adopts it | SKILL:20 "only when `docs/tech-stack.md` or an ADR adopts it … never create one on your own" | met |
| A test passing in only one runner is not a pass | SKILL:23 "a test that passes in only one runner is not a pass" | met |

### Cross-cutting — template per new skill
| Skill | Desc chars (≤250) | `Not for:` | `Docs:` | Steps decision-ordered | Every reference in table with trigger + used in a step | Verdict |
|---|---|---|---|---|---|---|
| save-data-versioning-migration | 246 | SKILL:9 | SKILL:10 (netstandard-2.1) | yes (1 shipped? gate) | 2/2 by filename (steps 2,5,7,9) | met |
| iap-server-receipt-ledger | 249 | SKILL:9 | SKILL:10 | yes (1 gate) | 4/4 in table; steps use them by role ("per the platform reference" step 3, "per the backend reference" step 5, step 8), not by filename | met (indirect) |
| firebase-unity-sdk | 243 | SKILL:9 | SKILL:10 (14.1.0) | yes (1 Blocked gate) | 5/5 by filename | met |
| consent-att-init-order | 247 | SKILL:9 | SKILL:10 (v11.6.0) | yes (1 audience) | 3/3 by filename | met |
| server-authoritative-validation | 246 | SKILL:9 | SKILL:10 (NGO 2.13, NfE 6.6) | yes (1 authority) | 2/2 by filename | met |
| mobile-safe-area | 245 | SKILL:9 | SKILL:10 (6000.6, uGUI 2.6) | no: step 10 "Target devices or aspect ratios unstated → defaults" is the input gate for step 9's matrix | 1/1 by filename | DEF-3 |
| unity-localization-text | 246 | SKILL:9 | SKILL:10 (1.5.13) | yes (1 version, 2 locale gate) | 2/2 by filename | met |
| core-scene-integration | 246 | SKILL:9 | SKILL:10 (unversioned + re-check — house pattern, e.g. csvhelper-csv-data/SKILL:10) | yes (1 tick owner) | 2/2 by filename | met |
| core-determinism | 243 | SKILL:9 | SKILL:10 (netstandard-2.1) | yes (1 gate) | 3/3 by filename | met |
| core-tests-without-unity | 245 | SKILL:9 | SKILL:10 (6000.0, UTF 2.0) | yes (4 adoption gate before 5) | 1/1 by filename | met |

### Bordering edits
| Criterion | Evidence | Verdict |
|---|---|---|
| ad-mediation ledger `Routed to:` → backend-engineer | ad-mediation-monetization-platform/SKILL:38 "- Routed to: `backend-engineer` (server ledger, `iap-server-receipt-ledger`)" | met |
| unity-test-framework step 2 allows the mirror | unity-test-framework/SKILL:21 "An adopted `dotnet test` mirror runs the same tests too (`core-tests-without-unity`)" | met |
| unity-test-framework `Not for:` allows the mirror | unity-test-framework/SKILL:9 "a `dotnet test` mirror of Core outside the Editor (`core-tests-without-unity`)" | met |
| qa-automation-engineer description mentions dotnet test | .claude/agents/qa-automation-engineer.md:3 "(and an adopted `dotnet test` Core mirror)" | met |
| `Not for:` repoint memorypack-serialization | memorypack-serialization/SKILL:9 "… old-save fixtures (`save-data-versioning-migration`)" | met |
| firebase-app-distribution | firebase-app-distribution/SKILL:9 "Crashlytics/Analytics/Remote Config in the game (`firebase-unity-sdk`)" | met |
| netcode-for-gameobjects | netcode-for-gameobjects/SKILL:9 "server-side validation of RPCs and inputs (`server-authoritative-validation`)" | met |
| unity-transport | unity-transport/SKILL:9 "server-side validation (`server-authoritative-validation`)" | met |
| anti-cheat-strategy | anti-cheat-strategy/SKILL:9 "writing one server-side validation check (`server-authoritative-validation`)" | met |

### Agent on-demand lists
| Assignment | Evidence | Verdict |
|---|---|---|
| save → backend-engineer + csharp-engineer | backend-engineer.md:21 `save-data-versioning-migration`; csharp-engineer.md:21 `save-data-versioning-migration` (Core save model) | met |
| iap → backend-engineer + sdk-platform-engineer | backend-engineer.md:21 `iap-server-receipt-ledger`; sdk-platform-engineer.md:21 `iap-server-receipt-ledger` (client side of the contract) | met |
| firebase + consent → sdk-platform-engineer | sdk-platform-engineer.md:21 `firebase-unity-sdk` · `consent-att-init-order` | met |
| validation → netcode-engineer | netcode-engineer.md:21 `server-authoritative-validation` | met |
| safe-area + localization → ui-engineer | ui-engineer.md:21 `mobile-safe-area` · `unity-localization-text` | met |
| core-scene → gameplay-engineer | gameplay-engineer.md:22 `core-scene-integration` (first) | met |
| determinism + core-tests → csharp-engineer | csharp-engineer.md:21 `core-determinism` · `core-tests-without-unity` | met |
| core-tests → qa-automation-engineer | qa-automation-engineer.md:20 `core-tests-without-unity` · `core-determinism` (replay test) | met |
| zstring stays off csharp-engineer | csharp-engineer.md:21 list has no `zstring-zero-allocation-strings` | met |
| `unity:setup-multiplayer-services` stays off backend-engineer | backend-engineer.md:21 has no plugin entry; it appears only in netcode-engineer.md:21 | met |

## (b) Vendor re-fetch (2026-10-29)
| # | Fact | Skill wording | Source | Verdict |
|---|---|---|---|---|
| 1 | Play get/consume/acknowledge; ack window; field gating grant | google-play-developer-api.md:23 "Grant only on `0`; never on Pending"; :39 "Not acknowledged within three days → automatically refunded"; SKILL:26 | https://developers.google.com/android-publisher/api-ref/rest/v3/purchases.products — "purchaseState … 0. Purchased 1. Canceled 2. Pending"; "productId … May not be present"; https://developer.android.com/google/play/billing/integrate — "must be done within three days so that the purchase isn't automatically refunded"; "grant entitlement only when the state is PURCHASED"; window "begins only when the purchase state transitions from 'PENDING' to 'PURCHASED'" | met |
| 2 | voidedpurchases.list fields, `includeQuantityBasedPartialRefund` | google-play-developer-api.md:48-55 | …/purchases.voidedpurchases/list — startTime default now−30 days, cannot be older; type 0 default / 1 adds subscriptions, switch to orderId; `includeQuantityBasedPartialRefund` default false, true adds entries with `voidedQuantity`; sample fields orderId, purchaseTimeMillis, purchaseToken, voidedQuantity, voidedReason, voidedSource, voidedTimeMillis | met (enum values of voidedReason/voidedSource not on this page — not re-confirmed) |
| 3 | Consume vs acknowledge | SKILL:26 "consume (consumable) or acknowledge (non-consumable)" | billing/integrate — consume "fulfill[s] the acknowledgement requirement"; non-consumables acknowledged after `isAcknowledged()` check | met |
| 4 | App Store Server API host, Get Transaction Info, JWS verification | app-store-server-api.md:40 `GET https://api.storekit.apple.com/inApps/v1/transactions/{transactionId}`; :14 x5c chain, OID `1.2.840.113635.100.6.2.1` | https://developer.apple.com/tutorials/data/documentation/appstoreserverapi/get-transaction-info.json — production `https://api.storekit.apple.com/inApps/v1/transactions/{transactionId}`, sandbox `https://api.storekit-sandbox.apple.com/…`; "any transaction identifier, including original transaction identifiers … consumable, non-consumable …"; jwsdecodedheader.json — leaf, intermediate with `1.2.840.113635.100.6.2.1`, Apple root | met |
| 5 | Notifications v2 REFUND; ledger key | app-store-server-api.md:53 "Match on `transactionId` from the verified `data.signedTransactionInfo` (the grant key)"; :26 "`originalTransactionId` … `REFUND` names it" | notificationtype.json — REFUND "successfully refunded a transaction for a consumable …, a non-consumable … The originalTransactionId and productId identify the original transaction and product. The revocationReason contains the reason"; REFUND_REVERSED "needs to reinstate them" | met — note: Apple names `originalTransactionId`; for one-time StoreKit 2 purchases the refunded transaction's `transactionId` is that transaction, so the key holds. Not re-confirmed: equality of the two ids for a restored or Family-Shared non-consumable (OBS-1) |
| 6 | UMP Update → LoadAndShow → CanRequestAds; privacy options | google-ump.md:9-15; SKILL:23,26 | https://developers.google.com/admob/unity/privacy — "request an update … at every app launch, using Update()"; "CanRequestAds() always returns false until you have called Update()"; previous-session status on error; "Ensure your logic prevents redundant ad requests"; PrivacyOptionsRequirementStatus → ShowPrivacyOptionsForm; "We don't recommend that you check consent status in another way"; Reset testing only | met |
| 7 | ATT only while active; NSUserTrackingUsageDescription | ios-att-and-privacy-manifest.md:9,13 | requesttrackingauthorization(completionhandler:).json — "The app's state is a value other than UIApplicationStateActive" → no prompt; "add the NSUserTrackingUsageDescription key"; notDetermined on dismissal; EU one year; FR/DE/IT/PL/RO full-page sheet | met |
| 8 | PrivacyInfo.xcprivacy required-reason declarations | ios-att-and-privacy-manifest.md:38-43 | privacy-manifest-files.json — required file name; NSPrivacyTracking → NSPrivacyTrackingDomains; tracking-domain requests fail without ATT; NSPrivacyAccessedAPITypes on iOS/iPadOS/tvOS/visionOS/watchOS; third-party SDK conditions | met |
| 9 | CheckAndFixDependenciesAsync → Available; one version | SKILL:22,24; setup-edm4u.md:9-23 | https://firebase.google.com/docs/unity/setup — `CheckAndFixDependenciesAsync().ContinueWithOnMainThread` … `DependencyStatus.Available`; setup page still "Unity 2021 LTS or later" (skill notes it); https://firebase.google.com/docs/unity/build-debug-guide — "every Firebase product … at the same version", "exclusively through either .unitypackage or the Unity Package Manager", "only one copy of EDM4U", remove all and reinstall; release notes — 14.0.0 (2026-10-15) Unity 2022.3, minSdk 24, Swift Packages; 14.1.0 2026-10-23; 13.17.0 bundles EDM4U 1.2.189 | met |
| 10 | Analytics SetAnalyticsCollectionEnabled, SetConsent, native off keys | analytics.md:9-10,22-28; SKILL:26 | FirebaseAnalytics.cs — `SetAnalyticsCollectionEnabled(bool)` "persisted across app sessions. By default it is enabled"; `SetConsent(IDictionary<ConsentType, ConsentStatus>)`; iOS configure-data-collection — `FIREBASE_ANALYTICS_COLLECTION_ENABLED` NO pauses, `…_DEACTIVATED` permanent, IDFV key, AdSupport; Android — `firebase_analytics_collection_enabled` false, `…_deactivated` true, `google_analytics_adid_collection_enabled` false | met (ConsentType member casing: skill already `Unverified:` at analytics.md:72) |
| 11 | Auth TokenAsync; server verifyIdToken | auth.md:12-13,30-32; SKILL:30 | FirebaseUser.cs — `public Task<string> TokenAsync(bool forceRefresh)`; UserId "Do NOT use this value to authenticate with your backend server … Use FirebaseUser.TokenAsync instead"; verify-id-tokens — correct format, not expired, properly signed; revocation not checked; RS256, kid from securetoken x509 URL, exp/iat/auth_time/aud/iss/sub, Cache-Control max-age; manage-sessions — `checkRevoked` flag, `auth/id-token-revoked`, ID token one hour | met |
| 12 | Firebase API key client-safe condition | secret-and-supply-chain-scan/SKILL:15-16; setup-edm4u.md:44-45 | https://firebase.google.com/docs/projects/api-keys — "API keys restricted to Firebase services do not need to be treated as secrets"; "never include the Gemini Developer API in the allowlist for a publicly accessible API key"; separate restricted keys for billable APIs | met (the scanner is stricter than the source: unconfirmed restriction → Needs Confirmation) |
| 13 | NGO SenderClientId, RequireOwnership / InvokePermission, server enforcement | sender-identity-per-stack.md:11,14,80; netcode-for-gameobjects/references/state-sync.md:55 "`RequireOwnership` obsolete" | NGO 2.13 rpc.html — `rpcParams.Receive.SenderClientId`; Server/Owner "throws an exception if invoked by a game client …", Everyone default; RpcAttribute API — `RequireOwnership` `[Obsolete]`, "Deprecated in favor of InvokePermission". Neither page says where the permission is enforced | met; server-side enforcement still Unverified — skill marks it `Unverified:` (sender-identity-per-stack.md:80) and compares the sender server-side regardless (SKILL:21) |
| 14 | EDM4U archived 2026-10-26 → Unity EDM; Localization 1.5.13 | firebase-unity-sdk/SKILL:22; setup-edm4u.md:29-30; unity-localization-text/SKILL:10 | https://github.com/googlesamples/unity-jar-resolver — "archived by the owner on Oct 26, 2026. It is now read-only"; README "We strongly recommend transitioning to Unity's officially supported EDM package"; Localization changelog top "[1.5.13] - 2026-09-02"; 1.5.0-pre.6 "We now fail the initialization operation if one of the sub-operations fails" | met (package id `com.unity.external-dependency-manager` stays `Unverified:` in setup-edm4u.md:89) |

## (c) Mechanical
| Check | Result | Verdict |
|---|---|---|
| `pwsh -NoProfile -File .claude/skills/verify-layer/scripts/verify.ps1` | `WARN CLAUDE.md: 31 lines > 30 recommended` · `WARN .claude/rules: always-loaded rules 119 lines > 100 recommended` · `verify-layer: OK (2 warning(s))` · exit 0 | met |
| Agent bodies ≤25 (lines after closing `---`) | backend-engineer 19 · csharp-engineer 18 · gameplay-engineer 17 · netcode-engineer 18 · qa-automation-engineer 16 · sdk-platform-engineer 19 · technical-artist 18 · ui-engineer 19 · unity-performance-engineer 18 | met |
| SKILL.md ≤120 | save 52 · iap 54 · firebase 54 · consent 52 · validation 50 · safe-area 45 · localization 50 · core-scene 48 · determinism 46 · core-tests 43 | met |
| References ≤250 | save: golden-save-fixtures 47, version-envelope-and-chain 132 · iap: app-store 65, firebase-functions 103, google-play 70, ugs 74 · firebase: analytics 72, auth 42, crashlytics 51, remote-config 49, setup-edm4u 89 · consent: child-audience 65, google-ump 108, ios-att 51 · validation: rate-limits 101, sender-identity 80 · safe-area: device-simulator 45 · localization: font-fallback 79, string-tables 49 · core-scene: input-and-physics 68, tick-and-interpolation 89 · determinism: float 57, replay 94, stable-hashing 84 · core-tests: dotnet-test-mirror 98 | met (max 132) |
| Secret shapes in the 10 folders (`BEGIN … PRIVATE KEY`, `AIza…`, `AKIA…`, `ya29.`, `eyJ…`, email shapes) | One hit: firebase-unity-sdk/references/auth.md:32 `securetoken@system.gserviceaccount.com` — Google's public token-signing service account named in the Firebase verify-id-tokens page; not a secret, not PII. No other hit | met |
| Agent names that do not exist | Every hyphenated backticked name resolves to an agent, a skill or a `unity:` plugin skill, except `appstoreconnect-v1` (JWT `aud` value), `firebase-functions` (npm package), `max-age` (HTTP header) — not agent names. `Next:` targets: `csharp-engineer` ×3, `cto` ×4, `technical-architect` ×4, `gd` ×1 (layer convention, agent-protocol/SKILL:36). No `Routed to:` lines in the new skills | met |

## (d) Cross-skill consistency
| Pair | Side A | Side B | Verdict |
|---|---|---|---|
| Replay seam | core-determinism/references/replay-test.md:3 "`MatchSimulation.Tick(tick, stepSeconds, command, contacts)` and `MatchSimulation.State`"; :82 `simulation.Tick(tick, StepSeconds, frame.Command, frame.Contacts)` | core-scene-integration/references/tick-and-interpolation.md:75 "`public void Tick(int tick, float stepSeconds, PlayerCommand command, ReadOnlySpan<HitData> contacts)`"; :64 same call | consistent (`ReplayFrame.Contacts` type left to the project; an array converts to `ReadOnlySpan`) |
| Fixtures form | save-data-versioning-migration/references/golden-save-fixtures.md:9 "`SaveFixtureV<N>.Bytes` (`static readonly byte[]`) … No data files: the test reads no disk and runs unchanged in a dotnet mirror" | core-tests-without-unity/SKILL:19 "fixtures as C# data, not files under `Assets/`"; memorypack-serialization/SKILL:24 "versioned successor type plus upgrade path"; memorypack-serialization/SKILL:9 routes "old-save fixtures" to the save skill | consistent |
| Fixtures feed release | golden-save-fixtures.md:40-46 "Release step 8 evidence … Every fixture from `MinSupportedVersion` through the previous release's schema version migrates to current" | release/SKILL:22 "8 · Save migration · `qa-automation-engineer` · Previous release's save loads in this build's code" | consistent |
| Consent order vs Firebase steps 4 and 6 | consent-att-init-order/SKILL:21 "(d) Firebase bootstrap awaits `DependencyStatus.Available` (`firebase-unity-sdk` step 4), then Firebase `SetConsent` + collection … never from `CanRequestAds()`" | firebase-unity-sdk/SKILL:24 "Where the bootstrap runs relative to consent is decided by `consent-att-init-order` step 3"; SKILL:26 "At `consent-att-init-order` step 3 (d) — after ATT and after `Available`: `SetConsent` … then `SetAnalyticsCollectionEnabled`" | consistent |
| Privacy-options withdrawal | consent-att-init-order/SKILL:26 "on close, re-apply step 3(d) Firebase consent and the step 3(e) ad-network consent signals, withdrawal included" | google-ump.md:73 "`ApplyFirebaseConsent` runs on every launch after the form callback and the Firebase gate, so a choice changed in the privacy-options form … always reaches Firebase, and `ApplyAdConsentSignals` runs again on privacy-options close" | inconsistent wording — reference names an on-close re-apply for ads only and ties Firebase to the next launch; SKILL requires both on close (DEF-2) |
| Audience gate | consent-att-init-order/SKILL:19 "Unstated → `Needs-decision` … same gate as `ad-mediation-monetization-platform` step 8" | ad-mediation-monetization-platform/SKILL:19 "Audience or jurisdictions unstated → `Needs-decision`; never assume the permissive answer" | consistent |
| IAP vs server-authoritative-validation | iap-server-receipt-ledger/SKILL:22 "Never credit from a client-sent product, amount or price" | server-authoritative-validation/SKILL:23 "authoritative outcomes never trust a client value"; its SKILL:9 routes "store receipts and currency grants (`iap-server-receipt-ledger`)" | consistent |
| IAP vs backend-build-vs-buy | iap-server-receipt-ledger/SKILL:9 "backend vendor choice (`backend-build-vs-buy`)" | backend-build-vs-buy/SKILL:9 "virtual-currency ledger (`ad-mediation-monetization-platform`; this skill owns profile data and save sync only)" → ad-mediation SKILL:38 routes the server ledger to `iap-server-receipt-ledger` | consistent (indirect route, no conflict) |
| IAP vs anti-cheat-strategy | iap-server-receipt-ledger/SKILL:9 "fraud posture beyond receipt checks (`anti-cheat-strategy`)" | anti-cheat-strategy/SKILL:13 "Confirm server authority against the Shared Core is the floor" | consistent |
| Auth ID token vs IAP caller identity | firebase-unity-sdk/SKILL:30 "the backend learns who the player is only from an ID token it verifies"; auth.md:30 `verifyIdToken` | iap-server-receipt-ledger/SKILL:22 "The player comes from the verified auth token, never the payload"; firebase-functions-firestore.md:10 "`request.auth.uid` … never read a uid from `request.data`"; ugs-cloud-code-economy.md:57 "`PlayerId` (the authenticated caller — the identity source)" | consistent |
| unity-test-framework vs core-tests-without-unity | unity-test-framework/SKILL:21 "An adopted `dotnet test` mirror runs the same tests too … a pass in one runner only is not a pass" | core-tests-without-unity/SKILL:21 "pin `LangVersion` to the editor's C# version"; SKILL:23 "a test that passes in only one runner is not a pass" | consistent (UTF does not restate the LangVersion pin; no conflict) |
| secret-scan steps 3–4 vs firebase config step | secret-and-supply-chain-scan/SKILL:15 "the Firebase API key in those files goes to step 4"; SKILL:16 "Clear only when confirmed restricted to Firebase APIs … unconfirmed → `Needs Confirmation`; … Gemini Developer API … Critical" | firebase-unity-sdk/SKILL:23 "allowlisted only while the API key is restricted to Firebase APIs … Unconfirmed key restriction → treat as secret and report `Needs Confirmation`"; SKILL:34 Never add Gemini to the key | consistent |
| `Routed to:` / `Next:` ids | (c) above: `csharp-engineer`, `cto`, `technical-architect`, `gd`; no `Routed to:` in new skills | `.claude/agents/` holds csharp-engineer.md, cto.md, technical-architect.md; `gd` is the protocol convention | consistent |

## Defects
| ID | Location | Expected | Actual | Evidence | Owner skill | Severity |
|---|---|---|---|---|---|---|
| DEF-1 | `.claude/skills/consent-att-init-order/SKILL.md:21` | Spec 4: "no ad/analytics SDK starts before consent resolves" | Step 3 allows "Firebase bootstrap may move before (b) only when the Analytics and Crashlytics build-time off keys ship — … Firebase Installations and Remote Config/Auth traffic then precede consent". An analytics SDK starts before consent on that path; the gap goes to the project's Known limitations, not to a GD acceptance of this feature | quoted line; spec line `.workflow/features/engineer-skill-gaps.md:44`; feature Known limitations has no entry for it | `consent-att-init-order` (sdk-platform-engineer author) | Medium — optional path, consent-related. If the path stays, the GD must accept it as a gap in the feature file; otherwise remove the clause |
| DEF-2 | `.claude/skills/consent-att-init-order/references/google-ump.md:73` | Same rule as SKILL:26: on privacy-options close, re-apply Firebase consent (3d) and ad signals (3e) | Reference says Firebase consent re-applies "on every launch after the form callback", so a privacy-options change "always reaches Firebase", and names the on-close re-apply for `ApplyAdConsentSignals` only. A reader following the reference leaves Firebase collection on until the next launch after a withdrawal | quoted lines both sides; R3-1 fix was written by the main session and not re-reviewed (feature Known limitations) | `consent-att-init-order` | Medium — consent withdrawal (Guideline 5.1.1) on an edge path |
| DEF-3 | `.claude/skills/mobile-safe-area/SKILL.md:25-26` | Decision-ordered steps (Cross-cutting): an input gate comes before the step that uses it | Step 10 "Target devices or aspect ratios unstated → `ui-engineer` defaults" comes after step 9, which already verifies "per target device × orientation" | quoted lines | `mobile-safe-area` | Low |

Observation, not a defect:
- OBS-1 (`iap-server-receipt-ledger/references/app-store-server-api.md:25-26,53`): Apple's REFUND text names `originalTransactionId` as the transaction's identifier; the skill keys on `transactionId`. For a StoreKit 2 one-time purchase both refer to the refunded transaction, so the key holds. Not re-confirmed: whether a restored or Family-Shared non-consumable can carry a `transactionId` different from the one granted. No skill text claims otherwise; consider an `Unverified:` entry. Touches money, so it goes to the IAP owner for a decision.

## Not run / not covered
- Fact 2: enum values of `voidedReason`/`voidedSource` were not on the list page; not re-confirmed (owner: IAP author).
- Fact 4: the page does not describe how to verify `signedTransactionInfo`. The skill's library-based verification (app-store-server-api.md:15-16) was not checked against the Node library README in this run.
- Fact 13: the source does not say where NGO enforces `InvokePermission` — still Unverified, already marked so in the skill.
- Facts outside the 14 (Play quota numbers, UGS Access Control URNs, Crashlytics native keys, Remote Config limits, TMP/Localization member names, Device Simulator facts) were not re-fetched.
- No skill was executed against a Unity project, backend, store sandbox or device; skills are guidance docs (feature Known limitations). Every "met" in (a) and (d) comes from reading the text; (b) comes from reading vendor docs; only (c) ran.
- Apple's HTML docs render client-side; facts 4, 5, 7 and 8 were read from the `developer.apple.com/tutorials/data/documentation/…json` endpoints of the same pages.

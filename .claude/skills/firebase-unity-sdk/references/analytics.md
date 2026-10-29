# Analytics

Sources: [a] `/analytics/unity/start` (below the SKILL.md `Docs:` base), [b] https://github.com/firebase/firebase-unity-sdk/blob/main/analytics/src/FirebaseAnalytics.cs, [c] https://firebase.google.com/docs/analytics/configure-data-collection (iOS), [c-android] https://firebase.google.com/docs/analytics/android/configure-data-collection, [d] https://developers.google.com/tag-platform/security/guides/app-consent, [e] https://developers.google.com/tag-platform/security/guides/implement-TCF-strings.

## API (`Firebase.Analytics.FirebaseAnalytics`, static) [b]

| Member | Fact that decides |
|---|---|
| `SetAnalyticsCollectionEnabled(bool)` | Persisted across sessions; enabled by default — off-until-consent needs the build-time key below |
| `SetConsent(IDictionary<ConsentType, ConsentStatus>)` | Omitted types keep their previous status; values persist across launches [d] |
| `ConsentType` | `AdStorage`, `AnalyticsStorage`, `AdUserData`, `AdPersonalization` (consent mode v2 adds the last two) [d] |
| `ConsentStatus` | `Granted`, `Denied` |
| `SetUserId(string)` | Sets the user-ID property; never an email, name or store account id |
| `ResetAnalyticsData()` | Clears device analytics data and resets the app instance id — the withdrawal/delete-my-data path |
| `GetAnalyticsInstanceIdAsync()` | `Task<string>`; the id a data-deletion request references |
| `LogEvent(name)` / `(name, param, value)` / `(name, params Parameter[])` | Prefer the `Event*`/`Parameter*` constants for recommended events [a] |

## Build-time collection defaults

| Platform | Key | Fact |
|---|---|---|
| Android manifest `<application>` `<meta-data>` | `firebase_analytics_collection_enabled` = `false` | Suspends collection until `SetAnalyticsCollectionEnabled(true)` [c-android] |
| Android | `firebase_analytics_collection_deactivated` = `true` | Permanent for that app version [c-android] |
| Android | `google_analytics_adid_collection_enabled` = `false` | Stops Advertising ID collection [c-android] |
| Android | `google_analytics_default_allow_analytics_storage`, `_ad_storage`, `_ad_user_data`, `_ad_personalization_signals` | `true`/`false`; the last two also accept `eu_consent_policy` (denied only where the EU User Consent Policy applies) [d] |
| iOS `Info.plist` | `FIREBASE_ANALYTICS_COLLECTION_ENABLED` = `NO` | Pauses collection until `SetAnalyticsCollectionEnabled(true)`; the runtime value overrides it from then on [c] |
| iOS | `FIREBASE_ANALYTICS_COLLECTION_DEACTIVATED` = `YES` | Permanent for that app version; overrides the runtime call [c] |
| iOS | `GOOGLE_ANALYTICS_IDFV_COLLECTION_ENABLED` = `NO` | Stops IDFV collection [c] |
| iOS | IDFA | Collected only when AdSupport is linked; `FirebaseAnalyticsCore` avoids it [c] |
| Both | `google_analytics_tcf_data_enabled` (Android) / `GOOGLE_ANALYTICS_TCF_DATA_ENABLED` (iOS) = `false` | Turns off the SDK's TCF-string integration [e] |

**Caveat:** withdrawing analytics or ad storage consent deletes all user properties, including `ad_personalization`; re-apply that choice with `SetConsent` [d].

## Where each consent type comes from

`CanRequestAds()` is not one of these sources: it answers "may ads be requested" and is `true` after an EEA refusal (Limited Ads).

| `ConsentType` | Source | Fact that decides |
|---|---|---|
| `AdStorage` | TCF Purpose 1 consent in the string the certified CMP writes (`IABTCF_PurposeConsents`, position 1) | Purpose 1 denied → `ad_storage` and `ad_user_data` denied [e] |
| `AdUserData` | TCF Purpose 1 (and Purpose 7 on web tags only) | [e] |
| `AdPersonalization` | TCF Purposes 3 and 4 | Either denied → `ad_personalization` denied [e] |
| `AnalyticsStorage` | No TCF purpose maps to it in Google's table [e]; the project names its source (a CMP custom purpose, or a stated TCF purpose combination) | Unnamed → `Needs-decision`, collection stays off |
| Outside TCF regions | No CMP signal; the GD-stated default for the jurisdiction (`consent-att-init-order` step 1) | Never inferred from silence |

**Caveat:** Google accepts only TCF strings implemented to TCF policy and its EU User Consent Policy [e]; a CMP that is not Google-certified does not count.

## Consent mapping

One rule: `SetAnalyticsCollectionEnabled(analyticsGranted)` right after `SetConsent`, on first resolution and on every later change. Both values persist across launches [b][c], so a withdrawal that only stops calling them leaves collection on.

```csharp
// After consent-att-init-order resolves; each flag comes from its source above, never hard-coded true.
FirebaseAnalytics.SetConsent(new Dictionary<ConsentType, ConsentStatus>
{
    { ConsentType.AnalyticsStorage, analyticsGranted ? ConsentStatus.Granted : ConsentStatus.Denied },
    { ConsentType.AdStorage, purpose1Granted ? ConsentStatus.Granted : ConsentStatus.Denied },
    { ConsentType.AdUserData, purpose1Granted ? ConsentStatus.Granted : ConsentStatus.Denied },
    { ConsentType.AdPersonalization, purposes3And4Granted ? ConsentStatus.Granted : ConsentStatus.Denied },
});
FirebaseAnalytics.SetAnalyticsCollectionEnabled(analyticsGranted);
```

## Limits [a]

| Limit | Value |
|---|---|
| Distinct event types | 500 per app; total volume unlimited |
| User properties | 25 per app |
| New user property in reports | Up to 24 hours |

Unverified: whether the Firebase SDK reads `IABTCF_*` keys and sets the ad consent types by itself (Google documents the purpose mapping and the off key, not automatic reading) — until confirmed on a device, set all four with `SetConsent`; whether Unity `PlayerPrefs` can read `IABTCF_*` on Android (Unity stores PlayerPrefs in its own SharedPreferences file; assume a native read is needed); the C# enum member casing `ConsentType.AdUserData` (reference listed lower-camel constant names); event-name and parameter length limits.

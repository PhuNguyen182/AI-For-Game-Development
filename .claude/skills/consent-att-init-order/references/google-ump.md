# Google UMP (Unity)

Sources: [a] `/admob/unity/privacy`, [b] `/admob/unity/privacy/gdpr`, [c] `/admob/unity/privacy/us-iab-support`, [d] `/admob/unity/reference/class/google-mobile-ads/ump/api/consent-request-parameters` (all under https://developers.google.com), [e] https://github.com/googleads/googleads-mobile-unity/releases, [f] https://ads-developers.googleblog.com/2023/08/.

## Flow API (`GoogleMobileAds.Ump.Api`)

| Member | Fact that decides |
|---|---|
| `ConsentInformation.Update(ConsentRequestParameters, Action<FormError>)` | Call on every launch; the only supported way to learn consent status [a] |
| `ConsentForm.LoadAndShowConsentFormIfRequired(Action<FormError>)` | Loads and shows every required message; callback fires immediately when none is required [a] |
| `ConsentInformation.CanRequestAds()` | Always `false` until `Update()` has run; check after `Update` (consent may come from a previous session) and after the form [a]. `true` when consent status is obtained or not required [f] — so also after a refusal, when only Limited Ads serve [b]. Gates ad requests only; never a source for Firebase consent types |
| Consent error | The SDK falls back to the previous session's status — still check `CanRequestAds()` [a] |
| `ConsentInformation.PrivacyOptionsRequirementStatus` | `PrivacyOptionsRequirementStatus.Required` → show the privacy-options control [a] |
| `ConsentForm.ShowPrivacyOptionsForm(Action<FormError>)` | Presents the form when the player taps that control [a] |
| `ConsentInformation.Reset()` | Testing only; never in production code [a] |

**Caveat:** both `CanRequestAds()` checks can return `true` in one launch; without a guard flag the ad SDK initializes and requests twice [a].

```csharp
// Game.Client startup: Firebase signals after the Available gate; ads start once, after UMP and, on iOS, an ATT answer.
private bool _isAdsStarted;

// True on Android, or when the ATT status is no longer not-determined.
private bool _isAttResolved;

private void OnConsentInfoUpdated(FormError error)
{
    // Returning player: stored consent may already allow ads; ad config was set in step (a).
    this.TryStartAds();
    ConsentForm.LoadAndShowConsentFormIfRequired(this.OnConsentFormDone);
}

private void OnConsentFormDone(FormError error)
{
    // Form closed (or none was required): the app is active again, so ATT may be requested now.
    this.RequestAttThen(this.OnAttResolved);
}

private void OnAttResolved()
{
    this._isAttResolved = true;
    this.ContinueStartupAsync().Forget(this.OnStartupFailed);
}

private async UniTask ContinueStartupAsync()
{
    // Step (d): no Firebase static before the dependency gate (firebase-unity-sdk step 4).
    bool isFirebaseAvailable = await this._firebaseBootstrap.InitializeAsync(this._lifetimeToken);
    if (isFirebaseAvailable)
    {
        // Consent types from their own sources (firebase-unity-sdk → analytics.md), never CanRequestAds().
        this.ApplyFirebaseConsent();
    }

    this.TryStartAds();
}

private void TryStartAds()
{
    if (this._isAdsStarted || !this._isAttResolved || !ConsentInformation.CanRequestAds())
        return;

    this._isAdsStarted = true;

    // Step (e): ad-network consent signals before the first ad SDK call.
    this.ApplyAdConsentSignals();
    this.InitializeAds();
}

private void OnPrivacyOptionsClicked()
{
    ConsentForm.ShowPrivacyOptionsForm(this.OnPrivacyOptionsClosed);
}

private void OnPrivacyOptionsClosed(FormError error)
{
    // A withdrawal stops Analytics and reaches the ad networks in this session; Crashlytics stops next launch.
    if (this._firebaseBootstrap.IsAvailable)
    {
        this.ApplyFirebaseConsent();
    }

    this.ApplyAdConsentSignals();
}
```

**Caveat:** on a returning iOS player ATT is already answered, so `_isAttResolved` starts `true` and the post-`Update` check starts ads at once, before Firebase; on a first launch ads wait for the ATT answer, so the first ad request carries the IDFA decision.

**Caveat:** `ApplyFirebaseConsent` runs on every launch after the form callback and the Firebase gate, and again with `ApplyAdConsentSignals` in `OnPrivacyOptionsClosed`, so a withdrawal stops Analytics collection and reaches the ad networks in the same session. Crashlytics withdrawal (`IsCrashlyticsCollectionEnabled = false`) takes effect next launch (SKILL.md step 8).

## `ConsentRequestParameters` [d]

| Member | Fact |
|---|---|
| `TagForUnderAgeOfConsent` | `bool`; `true` → UMP does not ask that user for consent [b][c] |
| `ConsentDebugSettings` | Debug geography and test devices |
| `ConsentSyncId` | 22–150 characters, else not set and a warning is logged |

**Caveat:** UMP does not forward `TagForUnderAgeOfConsent` to the Google Mobile Ads plugin; set `AgeRestrictedTreatment` on the ad request configuration too ([child-audience-flags.md](child-audience-flags.md)) [b].

## EEA / UK / Switzerland and US states

| Subject | Fact that decides |
|---|---|
| Certified CMP | From 2024-01-16 a partner without a Google-certified CMP gets only Limited Ads on EEA and UK traffic; UMP is one certified CMP, not the only one [b] |
| TCF | UMP implements IAB TCF v2; consent strings land in `IABTCF_*` local-storage keys for other SDKs to read [b] |
| US state regulations messaging | Plugin 8.7.0 or later [c] |

## Testing (test devices only) [a]

| Setting | Fact |
|---|---|
| `ConsentDebugSettings.TestDeviceHashedIds` | Hash from the device log on the first `Update`; debug settings are ignored on other devices |
| `DebugGeography.EEA` | Simulates EEA; pair with `Reset()` in a debug build to see the form again |

## Plugin [e]

| Version | Fact |
|---|---|
| v11.6.0 | Latest at pin; minimum Unity 2022.3 (breaking) |
| v11.3.0 | Added `RequestConfiguration.AgeRestrictedTreatment` |
| v11.0.0 | UMP Android dependency 4.0.0 |

Unverified: the release year of v11.6.0 (page showed "13 Oct" only); the exact `Action<FormError>` callback signatures and `DebugGeography` value set beyond `EEA`; which message UMP shows first when both a GDPR and an IDFA explainer message are enabled.

// Client startup members: UMP update, form, ATT, Firebase gate and a once-only TryStartAds.
// Adapt into: the one bootstrap class that owns the startup sequence, or Assets/_Project/Scripts/Platform/StartupConsentFlow.cs when none exists (members only)
// Unverified: not compiled or run (no Unity project in this repo).
// Client startup: Firebase signals after the Available gate; ads start once, after UMP and, on iOS, an ATT answer.
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

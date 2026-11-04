---
name: consent-att-init-order
description: "UMP ConsentInformation, CanRequestAds, ATTrackingManager, PrivacyInfo.xcprivacy. Use when ads/analytics await consent."
user-invocable: false
---

# Consent, ATT and SDK Init Order

- **Not for:** choosing the mediation stack and its consent gate (`ad-mediation-monetization-platform` step 8).
- **Not for:** the analytics vendor (`analytics-telemetry-platform`).
- **Not for:** Firebase API calls themselves (`firebase-unity-sdk`).
- **Not for:** the settings screen UI (`ui-engineer`).
- **Not for:** whether a jurisdiction's law applies (GD with legal counsel).
- **Docs:** UMP for Unity https://developers.google.com/admob/unity/privacy — ships in the Google Mobile Ads Unity plugin (`GoogleMobileAds.Ump.Api`).
  - **Plugin pin:** `v11.6.0` (Unity 2022.3 minimum; `AgeRestrictedTreatment` from v11.3.0).
  - **ATT:** https://developer.apple.com/documentation/apptrackingtransparency.
  - **Store policy:** it changes; re-read it per step 2.

## References
- **[google-ump.md](references/google-ump.md):** Writing the consent flow, ads requested twice, consent form never shows, or testing EEA behaviour.
- **[ios-att-and-privacy-manifest.md](references/ios-att-and-privacy-manifest.md):** The ATT prompt does not appear, IDFA is zero, or an App Store rejection cites tracking or a privacy manifest.
- **[child-audience-flags.md](references/child-audience-flags.md):** The audience includes under-13s, users of unknown age, or EEA users under the age of consent.

## Steps
1. **Audience and jurisdictions first:** read `CLAUDE.md` → Compliance and the GDD audience.
   - **Unstated:** `Needs-decision` naming them; never assume adult-only or non-EEA (same gate as `ad-mediation-monetization-platform` step 8).
   - **Child-directed or mixed:** apply [child-audience-flags.md](references/child-audience-flags.md) before any other step.
2. **Fetch current store policy with `WebFetch` before writing:** Google Play Families policy, App Store Review Guidelines 1.3, 5.1.1, 5.1.2, 5.1.4.
   - **Record:** each requirement with its URL in `Store policy:`.
   - **Unmeetable requirement:** a requirement the plan cannot meet stops the integration.
3. **Fix the order and write it as one startup sequence:** owned by one bootstrap.
   - **(a) Audience flags:** audience flags and the ad `RequestConfiguration` set.
   - **(b) UMP:** `ConsentInformation.Update` → `ConsentForm.LoadAndShowConsentFormIfRequired`.
   - **(c) iOS ATT:** request it here.
   - **(d) Firebase:** the Firebase bootstrap awaits `DependencyStatus.Available` (`firebase-unity-sdk` step 4), then Firebase `SetConsent` + collection.
   - **(d) consent sources:** the per-type sources in `firebase-unity-sdk` → `analytics.md`, never from `CanRequestAds()`.
   - **(d) not `Available`:** Firebase `SetConsent` + collection skipped.
   - **(e) Ads:** ad-network consent signals applied, then ad SDK and mediation init.
   - **Returning player:** whose stored consent already allows ads may reach (e) straight from `Update`'s callback; the ad configuration from (a) and the signals in (e) do not depend on Firebase.
   - **Firebase bootstrap:** always runs at (d), never before (b) or (c).
   - **First launch:** Remote Config's in-build defaults cover it.
   - **Criterion, ads:** requested only after `Update`'s callback with `CanRequestAds()` true, or after the form's callback with it true.
   - **Criterion, Firebase:** no Firebase call precedes `Available`.
   - **Criterion, collection:** no analytics or crash collection is enabled before (d).
4. **Collection defaults off in the build:** native SDKs start at process launch, before any C# runs.
   - **Analytics:** keys per `firebase-unity-sdk` → `analytics.md`.
   - **Crashlytics:** keys per `firebase-unity-sdk` → `crashlytics.md`.
   - **Ad SDKs:** each ad SDK's equivalent.
   - **SDK with no build-time off switch:** initializes only at (e).
   - **Crashlytics opt-in required, off keys not confirmed on a device build:** `Needs-decision`, gap in Known limitations.
5. **UMP: `Update` on every launch; check `CanRequestAds()` after `Update` and again after the form; guard init with one flag:** so both paths cannot initialize twice.
   - **Reference:** [google-ump.md](references/google-ump.md).
   - **Consent error:** still check `CanRequestAds()` (previous-session status applies).
6. **ATT only while the app is active, after the UMP form closes:** per [ios-att-and-privacy-manifest.md](references/ios-att-and-privacy-manifest.md).
   - **Not in:** `Awake`/first-frame code that can run before the app is active — the system skips the prompt and the handler returns at once.
   - **One owner of the request:** the UMP IDFA explainer message, or Unity's iOS 14 Advertising Support package — never both.
   - **Usage description:** `NSUserTrackingUsageDescription` set by a post-build step.
   - **Gameplay:** never depends on the answer (Guideline 5.1.2).
7. **Privacy manifest: the app's `PrivacyInfo.xcprivacy` in `Assets/Plugins`, and every third-party SDK ships its own:** per [ios-att-and-privacy-manifest.md](references/ios-att-and-privacy-manifest.md).
   - **If tracking:** `NSPrivacyTracking` true plus tracking domains.
   - **SDK without a manifest:** a store risk reported in `Risks:`.
8. **Privacy-options entry point is required:**
   - **Trigger:** when `PrivacyOptionsRequirementStatus` is `Required`, a settings control opens `ConsentForm.ShowPrivacyOptionsForm`.
   - **On close:** re-apply step 3(d) Firebase consent and the step 3(e) ad-network consent signals, withdrawal included (Guideline 5.1.1 requires an easy withdrawal path).
   - **Same session:** analytics and ad signals stop.
   - **Crashlytics withdrawal:** takes effect next launch (`firebase-unity-sdk` → `crashlytics.md`); record it in Known limitations.
   - **Jurisdiction requiring an immediate stop:** `Needs-decision`.
   - **Criterion:** reachable from in-game settings without a restart; the control itself goes to `ui-engineer`.
9. **Verify on a device, never in the Editor:** UMP forms and ATT do not run there, per [google-ump.md](references/google-ump.md).
   - **Setup:** register the test device hash, use `DebugGeography.EEA`, reinstall to see ATT again.
   - **Cases:** run both an accept-all and a refuse-all case.
   - **After refusal:** ads may still serve (Limited Ads) but Firebase must show `AnalyticsStorage` and ad types denied and no collection.
   - **Not run:** `Verified: not run`.

## Never
- **Reset outside debug:** call `ConsentInformation.Reset()` outside a debug build — every player is asked again on each launch.
- **Other storage instead of `CanRequestAds()`:** read IAB TCF keys or other storage when deciding whether to request ads — Google advises against checking it another way.
- **`CanRequestAds()` as consent:** treat it as analytics or ad-storage consent — it is `true` after an EEA refusal (Limited Ads); Firebase consent types come from their own sources.
- **ATT and GDPR conflated:** treat ATT "authorized" as GDPR consent, or GDPR consent as ATT — separate legal bases, separate signals.

## Output
```
## Consent and Init Order — <project>
- Audience / jurisdictions: <stated source> | Needs-decision: <what>
- Store policy: <requirement — URL> each
- Order: flags + ad config → UMP → ATT → Firebase Available → Firebase signals → ad signals + init — <bootstrap path>
- Gate: ads init behind CanRequestAds(): yes/no; analytics per AnalyticsStorage source: yes/no; double-init guard: yes/no
- Child flags: <TagForUnderAgeOfConsent / AgeRestrictedTreatment / n/a>
- ATT owner: <UMP IDFA message | iOS 14 Advertising Support | n/a>
- Privacy manifest: app <path>; SDKs missing one: <list | none>
- Privacy options entry point: <screen> | gap
- Risks: <store rejection risks>
```

## Example
- **"Init ads and Firebase in `Awake`, show the consent form after the first ad loads":** declined.
  - **Why:** the ad SDK requests and analytics collects before consent exists; Guideline 5.1.1 requires consent before collection, and EEA traffic without a certified CMP gets Limited Ads only.
  - **Did instead:** moved init behind `CanRequestAds()` and collection on after the form.

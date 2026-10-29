# Child and Under-Age Audience Flags

Sources: [a] https://developers.google.com/admob/unity/targeting, [b] https://developers.google.com/admob/unity/privacy/gdpr, [c] https://support.google.com/googleplay/android-developer/answer/9893335, [d] https://developer.apple.com/app-store/review/guidelines/, [e] https://github.com/googleads/googleads-mobile-unity/releases.

## Audience → flags

| Audience (from `CLAUDE.md` → Compliance / GDD) | UMP `ConsentRequestParameters` | GMA `RequestConfiguration` | Store |
|---|---|---|---|
| Child-directed only (COPPA) | `TagForUnderAgeOfConsent = true` for EEA minors | `AgeRestrictedTreatment.Child` | Play Families: self-certified ad SDKs only, no AAID; Apple Kids rules |
| Mixed, age screened as child | `TagForUnderAgeOfConsent = true` | `AgeRestrictedTreatment.Child` | Neutral age screen required on Play |
| Mixed, age screened as teen | `true` only for an EEA user under the age of consent | `AgeRestrictedTreatment.Teen` | — |
| Unknown age in a mixed audience | — | treat as child for ads | Play: self-certified ad SDKs for users of unknown age |
| Adult only, stated | unset | `AgeRestrictedTreatment.Unspecified` | — |

**Caveat:** the age screen runs before the UMP request, because its answer sets the UMP parameter and the ad flag.

## Google Mobile Ads [a][e]

| Subject | Fact that decides |
|---|---|
| `AgeRestrictedTreatment` | `Child`, `Teen`, `Unspecified`; added in plugin v11.3.0; replaces the deprecated `TagForChildDirectedTreatment` and `TagForUnderAgeOfConsent` request flags |
| Mapping | TFCD or TFUA `True` → `Child`; `False`, `Unspecified` or unset → `Unspecified`; `Teen` has no legacy equivalent |
| Set before init | `MobileAds.SetRequestConfiguration` before `MobileAds.Initialize`, so every request carries it |
| Legacy flags together | TFCD and TFUA both true → child-directed wins; with `AgeRestrictedTreatment` also set, the most conservative applies |
| `TagForChildDirectedTreatment` true | Disables interest-based and remarketing ads for that request |
| Designed for Families / Family Link accounts | Treated as child-directed automatically |
| `MaxAdContentRating` | `G`, `PG`, `T`, `MA` |
| Mediation | TFUA is not forwarded to mediation adapters; each network needs its own flag; age-treatment forwarding needs minimum adapter versions (e.g. AppLovin 8.7.4, Meta 3.18.7) |

```csharp
// Before MobileAds.Initialize; the value comes from the age screen, never a constant.
MobileAds.SetRequestConfiguration(new RequestConfiguration
{
    AgeRestrictedTreatment = isChild ? AgeRestrictedTreatment.Child : AgeRestrictedTreatment.Unspecified,
});
```

## UMP [b]

| Subject | Fact |
|---|---|
| `TagForUnderAgeOfConsent = true` | UMP does not request consent from that user |
| Forwarding | UMP does not forward it to the GMA plugin — set `AgeRestrictedTreatment` as well |

## Google Play Families policy [c]

| Requirement | Applies to |
|---|---|
| Only Families Self-Certified Ads SDKs | Ads to children or users of unknown age |
| No interest-based ads or remarketing | Ads to children |
| No AAID, IMEI, IMSI transmission | Apps solely targeting children |
| No location permission or precise location | Apps solely targeting children |
| Neutral age screen | Mixed-audience apps |
| Privacy policy matching actual collection | All Families apps |

## Apple [d]

| Guideline | Requirement |
|---|---|
| 1.3 Kids Category | No third-party analytics or advertising; limited exception for services collecting no IDFA or identifiable child data |
| 5.1.4 | Same for apps primarily for kids; privacy policy and compliance with children's privacy statutes |

**Caveat:** a Kids Category app normally ships no ATT prompt and no ad SDK; Firebase Analytics there must collect no IDFA (`firebase-unity-sdk` → `analytics.md`).

Unverified: the plugin version that marked TFCD/TFUA deprecated; the age-of-consent threshold per EEA country (legal input, not SDK fact); whether Firebase Analytics qualifies under Guideline 1.3's limited exception.

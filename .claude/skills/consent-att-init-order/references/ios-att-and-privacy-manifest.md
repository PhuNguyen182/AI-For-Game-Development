# iOS ATT and Privacy Manifest

Sources: [a] https://developer.apple.com/documentation/apptrackingtransparency/attrackingmanager/requesttrackingauthorization(completionhandler:), [b] https://developer.apple.com/documentation/bundleresources/privacy-manifest-files, [c] https://developer.apple.com/app-store/review/guidelines/, [d] https://docs.unity3d.com/Packages/com.unity.ads.ios-support@1.2/manual/index.html, [e] https://docs.unity.com/en-us/engine/current/manual/platform-specific/iphone/ios-building-and-delivering/apple-privacy-manifest-policy, [f] https://developers.google.com/admob/ios/privacy/idfa, [g] https://developers.google.com/admob/unity/privacy/strategies.

## `ATTrackingManager.requestTrackingAuthorization` [a]

| Subject | Fact that decides |
|---|---|
| Prompt skipped | The system runs the completion handler immediately without a prompt when the app state is not `UIApplicationStateActive` (among other listed cases) |
| Dismissed without a decision | Status stays `notDetermined`; call again later |
| EU | After an answer, the prompt cannot show again for a year |
| France, Germany, Italy, Poland, Romania | Full-page sheet; shows `NSUserTrackingMarkdownUsageDescription` if present |
| `NSUserTrackingUsageDescription` | Required in the app target's Info.plist to use the method |
| Status values | `notDetermined`, `restricted`, `denied`, `authorized` |
| Denied | Ad requests continue without IDFA [f] |

**Caveat:** a Unity scene's first `Awake`/`Start` can run before the app is active; request from the UMP form-closed callback or after `OnApplicationFocus(true)`.

## Who calls it

| Owner | Fact |
|---|---|
| UMP IDFA explainer message | Configured in AdMob Privacy & messaging; UMP shows the explainer immediately before the ATT alert and loads a form only while status is `notDetermined`; needs UMP 1.1.0+ and the AppTrackingTransparency framework linked [f] |
| Unity "iOS 14 Advertising Support" (`com.unity.ads.ios-support` 1.2.0) | `ATTrackingStatusBinding.RequestAuthorizationTracking()` / `(RequestAuthorizationTrackingCompleteHandler)`, `GetAuthorizationTrackingStatus()`; ships a ContextScreen sample for a pre-prompt screen [d]; Google's Unity docs name it for apps not using UMP [g] |

## Review guidelines [c]

| Guideline | Requirement |
|---|---|
| 5.1.2(i) | Tracking requires explicit permission via the ATT APIs; no functionality, content or reward may depend on enabling tracking |
| 5.1.1(ii) | Consent before collecting user or usage data, even anonymous; an easy way to withdraw consent |
| 1.3 / 5.1.4 | Kids Category / apps primarily for kids: no third-party analytics or advertising, except services that collect no IDFA or identifiable child data |

## Privacy manifest `PrivacyInfo.xcprivacy`

| Subject | Fact that decides |
|---|---|
| File name | `PrivacyInfo.xcprivacy` is required for bundled manifests [b] |
| `NSPrivacyTracking` | `true` when data is used for tracking as ATT defines it; then `NSPrivacyTrackingDomains` is required [b] |
| `NSPrivacyTrackingDomains` | Requests to these domains fail until ATT permission is granted [b] |
| `NSPrivacyCollectedDataTypes` | Data types collected; declared on all platforms [b] |
| `NSPrivacyAccessedAPITypes` | Required-reason APIs with reasons; iOS, iPadOS, tvOS, visionOS, watchOS [b] |
| Third-party SDKs | Must include their own when on Apple's "SDKs that require a privacy manifest and signature" list, or when they use required-reason APIs, collect data or contact tracking domains [b] |
| Unity project location | Create in Xcode, save to `Assets/Plugins` [e] |
| Unity Engine's own reasons | Added automatically from 2021.3.35f1, 2022.3.18f1, 2023.2.7f1; older editors declare them in the project manifest [e] |
| Plug-in manifests | Prefer shipping as `.framework`; otherwise save the manifest with the plug-in source and select iOS in the Plugin Inspector [e] |
| Responsibility | Unity is not responsible for third-party manifests; checking each SDK ships one is the app's job [e] |

**Caveat:** an undeclared required-reason API can get the app rejected [e].

Unverified: the `RequestAuthorizationTrackingCompleteHandler` signature and the Unity status enum member names; whether `com.unity.ads.ios-support` writes `NSUserTrackingUsageDescription` itself (assume a post-build `PlistDocument` step is needed); whether calling ATT yourself while the UMP IDFA message is enabled shows the explainer or skips it.

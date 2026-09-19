# iOS Lanes, Signing and match — from Unity's Xcode project to a signed `.ipa`

Source: [build_app / gym](https://docs.fastlane.tools/actions/build_app/), [match](https://docs.fastlane.tools/actions/match/), [app_store_connect_api_key](https://docs.fastlane.tools/actions/app_store_connect_api_key/), [cocoapods](https://docs.fastlane.tools/actions/cocoapods/).
Covers: SKILL.md §4 — **"Build iOS from the Xcode project Unity emitted, never from Unity directly"**, **"Match `export_method` to where the build is going"**, **"Run `match` in read-only mode on CI"**.

Unity's iOS output is an Xcode project, not an app. This file holds what happens between the two, and the
code-signing surface that decides whether the resulting `.ipa` installs on anything.

## The lane's shape

```ruby
platform :ios do
  lane :qa do
    setup_ci                                     # temporary keychain; see ci-keychain-and-credentials.md
    cocoapods(podfile: 'build/ios/Podfile')      # only when Unity's export produced one
    api_key = app_store_connect_api_key(
      key_id: ENV['ASC_KEY_ID'],
      issuer_id: ENV['ASC_ISSUER_ID'],
      key_filepath: ENV['ASC_KEY_PATH']          # the .p8, bound as a secret file by the job
    )
    match(type: 'adhoc', readonly: true, api_key: api_key)
    build_app(
      workspace: 'build/ios/Unity-iPhone.xcworkspace',   # .xcodeproj when there is no Podfile
      scheme: 'Unity-iPhone',
      export_method: 'ad-hoc',
      output_directory: 'build/ios/output',
      clean: false
    )
  end
end
```

| Step | Why it is there | Source |
|---|---|---|
| `cocoapods` | A Unity project using Firebase, ad or IAP SDKs exports a `Podfile`; without `pod install` the workspace does not resolve | [cocoapods](https://docs.fastlane.tools/actions/cocoapods/) |
| `workspace` against `project` | With Pods, Xcode must build the `.xcworkspace`; building the `.xcodeproj` fails on missing pod targets | [build_app](https://docs.fastlane.tools/actions/build_app/) |
| `app_store_connect_api_key` | Key-based auth works with no Apple ID, no password, and no two-factor prompt — the only practical headless route | [App Store Connect API](https://docs.fastlane.tools/app-store-connect-api/) |
| `clean: false` | Unity already produced a fresh export; a clean build discards the incremental state and doubles the stage | [build_app](https://docs.fastlane.tools/actions/build_app/) |

## Export methods

| `export_method` | Produces a build that installs on | Use for |
|---|---|---|
| `development` | Devices registered to a development profile, with a development certificate | A debug build for one or two known devices |
| `ad-hoc` | Devices whose UDIDs are in the profile — up to Apple's per-year device limit | Internal QA distribution, including through App Distribution |
| `app-store` | Nothing directly; it is for TestFlight and review submission | TestFlight, store submission — a separate, human-triggered lane |
| `enterprise` | Any device, under an Apple Developer Enterprise Program account | Only where such an account exists; it is not a substitute for `ad-hoc` |

The export method must match the profile `match` fetched. Mismatched, the export fails late with an error
about entitlements or provisioning that names neither. **The `ad-hoc` device limit is the operational
constraint that matters here**: a tester whose device UDID is not in the profile cannot install the build, and
nothing in the pipeline can detect that — it surfaces as one person reporting a failed install.

## `match`, and why read-only on CI

| Behaviour | Effect |
|---|---|
| `match` stores certificates and profiles, encrypted, in a shared repository or bucket | Every machine and every agent uses the same identity, instead of each minting its own |
| `readonly: true` | Fetches and installs what exists; **fails** if something is missing | 
| Write mode on CI | May create or **revoke** certificates. A revocation invalidates every other machine and every other pipeline using that identity — recovery is manual and touches everyone |
| `MATCH_PASSWORD` | Decrypts the store; a job-bound secret, never a committed value |

Renewal is therefore a deliberate act performed by a person, on a machine, with intent — not something a
nightly job does at 02:00 because a certificate expired that day.

## Version and build number

Unity has already written `PlayerSettings.iOS.buildNumber` into the exported project, per
`unity-batchmode-cli`. Do not also call `increment_build_number` in the lane: the two disagree, and the
artifact then reports a version that matches neither the build log nor the release notes. If the lane must
know the number, read it rather than set it.

## Failure signatures

| Symptom | Cause |
|---|---|
| `No signing certificate "iOS Distribution" found` | The keychain has no identity — `setup_ci` did not run, or `match` was not called before `build_app` |
| `No profiles for '<bundle id>' were found` | The profile does not exist in the match store, or the bundle id in `Appfile` does not match the Unity player settings |
| Export succeeds; the `.ipa` installs for nobody | Wrong `export_method` for the destination, or a UDID missing from the ad-hoc profile |
| `pod install` errors about a missing `Podfile` | Unity's export did not produce one; the project has no CocoaPods dependency and the lane should build the `.xcodeproj` |
| The lane hangs waiting for input | A password prompt on an interactive keychain, or Apple ID auth instead of an API key |

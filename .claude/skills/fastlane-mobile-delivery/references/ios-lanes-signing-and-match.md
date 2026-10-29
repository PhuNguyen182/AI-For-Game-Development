# iOS Lanes, Signing and match

Sources: [b] `actions/build_app/`, [m] `actions/match/`, [c] `actions/cocoapods/`, [k] `app-store-connect-api/`, all under the `Docs:` base.

```ruby
platform :ios do
  lane :qa do
    setup_ci                                     # temporary keychain
    cocoapods(podfile: 'build/ios/Podfile')      # only when Unity's export produced one
    api_key = app_store_connect_api_key(
      key_id: ENV['ASC_KEY_ID'], issuer_id: ENV['ASC_ISSUER_ID'],
      key_filepath: ENV['ASC_KEY_PATH'])         # .p8 bound as a secret file
    match(type: 'adhoc', readonly: true, api_key: api_key)
    build_app(
      workspace: 'build/ios/Unity-iPhone.xcworkspace',  # .xcodeproj when no Podfile
      scheme: 'Unity-iPhone', export_method: 'ad-hoc',
      output_directory: 'build/ios/output', clean: false)
  end
end
```

| Element | Fact that decides |
|---|---|
| `cocoapods` | Firebase/ad/IAP SDKs make Unity export a `Podfile`; without `pod install` the workspace does not resolve [c] |
| `workspace` vs `project` | With Pods, build the `.xcworkspace`; the `.xcodeproj` fails on missing pod targets [b] |
| `app_store_connect_api_key` | Headless auth with no Apple ID, password or 2FA prompt; Apple ID auth hangs the lane [k] |
| `clean: false` | Unity already exported fresh; a clean build doubles the stage |

## Export methods

| `export_method` | Installs on | Use for |
|---|---|---|
| `development` | Devices in a development profile | Debug build for known devices |
| `ad-hoc` | Devices whose UDIDs are in the profile, up to Apple's per-year device limit | Internal QA, including App Distribution |
| `app-store` | Nothing directly | TestFlight/review; separate human-triggered lane |
| `enterprise` | Any device, under an Enterprise Program account | Only where such an account exists |

The method must match the profile `match` fetched, or the export fails late with an entitlements/provisioning error. A tester whose UDID is not in the ad-hoc profile cannot install, nothing in the pipeline detects it, and re-uploading cannot fix it: it needs a new build against an updated profile.

## `match` [m]

- Stores certificates and profiles encrypted in a shared repo or bucket, so every machine uses one identity. `MATCH_PASSWORD` decrypts it (job-bound secret).
- `readonly: true` fetches and installs, and fails if something is missing.
- Write mode on CI may create or revoke certificates; a revocation invalidates every machine and pipeline using that identity, and recovery is manual. Renewal is a deliberate act by a person.

## Failure signatures

| Symptom | Cause |
|---|---|
| `No signing certificate "iOS Distribution" found` | No identity in the keychain: `setup_ci` missing or `match` not before `build_app` |
| `No profiles for '<bundle id>' were found` | Profile absent from the match store, or `Appfile` bundle id differs from Unity player settings |
| `.ipa` installs for nobody | Wrong `export_method` for the destination, or UDID missing from the ad-hoc profile |
| `pod install` errors on a missing `Podfile` | No CocoaPods dependency; build the `.xcodeproj` |
| Lane hangs for input | Password prompt on an interactive keychain, or Apple ID auth instead of an API key |

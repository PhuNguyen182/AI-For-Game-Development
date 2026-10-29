# Signing and Distribution Failures

Sources: fastlane `codesigning/getting-started/`, `actions/match/`, `actions/gradle/` under `https://docs.fastlane.tools/`; https://firebase.google.com/docs/app-distribution. Lane fixes: `fastlane-mobile-delivery`.

No gameplay change can cause these, so the run's merging feature is never the cause. Say whether the fault is the identity or the wiring (different owners, usually visible in the same line).

## iOS signing

| Signature | Cause | Owner |
|---|---|---|
| `No signing certificate "iOS Distribution" found` | Keychain has no identity: `setup_ci` missing or `match` not called | `ci-cd-engineer` |
| `No profiles for '<bundle id>' were found` | Profile absent from the match store, or bundle id disagrees with Unity player settings | `sdk-platform-engineer` (identity) or `ci-cd-engineer` (lane bundle id) |
| Lane hangs at a keychain or Apple ID prompt | Interactive auth on a headless agent | `ci-cd-engineer` |
| Certificate expired, or revoked by another machine's `match` write | Shared identity changed under the pipeline | `sdk-platform-engineer` |
| Export succeeds; `.ipa` installs for nobody | Wrong `export_method`, or UDIDs missing from the profile at signing time | `ci-cd-engineer` for the method; `sdk-platform-engineer` for the device list |

The last row is a build-time fact: no re-upload repairs it, only a new build against an updated profile.

## Android signing

| Signature | Cause | Owner |
|---|---|---|
| `INSTALL_PARSE_FAILED_NO_CERTIFICATES` | Never signed: keystore properties absent from the build | `ci-cd-engineer` |
| Signing config resolves to empty strings | Credential bound to a different stage than the one that ran | `ci-cd-engineer` |
| Upload rejected on certificate fingerprint | Signed with a key other than the expected upload key | `sdk-platform-engineer` |
| Installs only on the developer's device | Unity debug keystore; custom keystore never enabled | `ci-cd-engineer` |
| `keytool`/`jarsigner` password errors | Wrong or truncated secret, often a trailing newline in the stored value | `ci-cd-engineer` |

## Distribution

| Signature | Cause | Owner |
|---|---|---|
| Permission denied fetching app information | Service account lacks the App Distribution role, or credential path empty on this agent | `ci-cd-engineer`; `sdk-platform-engineer` to grant the role |
| Error naming the app id | The other platform's id, or an id from a different Firebase project | `ci-cd-engineer` |
| AAB rejected | Firebase app not linked to Google Play | `sdk-platform-engineer` |
| Upload succeeds, nobody notified | Empty group, or group alias that does not exist | `ci-cd-engineer` |
| Auth worked yesterday, fails today, nothing changed | Personal token instead of a service account; the person's access changed | `ci-cd-engineer`; the fix is a service account |

A profile or signing fault often cannot be repaired by re-running the failed stage; say whether a rebuild is required.

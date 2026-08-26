# Signing and Distribution Failures — configuration faults, and who owns each

Sources: [fastlane — code signing](https://docs.fastlane.tools/codesigning/getting-started/), [match](https://docs.fastlane.tools/actions/match/), [Firebase App Distribution](https://firebase.google.com/docs/app-distribution), [gradle action](https://docs.fastlane.tools/actions/gradle/).
Covers: SKILL.md §4 — **"Attribute a signing or distribution failure to configuration rather than to code"**.

Everything after a successful build fails for configuration reasons: an identity, a profile, a key, an
account, a permission. No gameplay change can cause any of it, which makes this the class most often routed
to the wrong person — the failure appears on the run that carried a feature, and the feature is blamed.

## iOS signing

| Signature | Class | Owner |
|---|---|---|
| `No signing certificate "iOS Distribution" found` | The keychain has no identity — `setup_ci` missing, or `match` not called | `ci-cd-engineer` (lane wiring) |
| `No profiles for '<bundle id>' were found` | The profile is absent from the match store, or the bundle id disagrees with Unity's player settings | `tech-lead-sdk-platform` (identity) or `ci-cd-engineer` (bundle id in the lane) |
| The lane hangs at a keychain or Apple ID prompt | Interactive auth on a headless agent | `ci-cd-engineer` |
| Certificate expired, or revoked while another machine ran `match` in write mode | The shared identity changed underneath the pipeline | `tech-lead-sdk-platform` |
| Export succeeds; the `.ipa` installs for nobody | Wrong `export_method`, or the device UDIDs were not in the profile at signing time | `ci-cd-engineer` for the method; `tech-lead-sdk-platform` for the profile's device list |

The last row is the one worth stating explicitly in a report: **it is a build-time fact, so no re-upload
repairs it** — the fix is a new build against an updated profile, per `fastlane-mobile-delivery`.

## Android signing

| Signature | Class | Owner |
|---|---|---|
| `INSTALL_PARSE_FAILED_NO_CERTIFICATES` on a device | The artifact was never signed — the keystore properties were absent from the build | `ci-cd-engineer` |
| Signing config resolving to empty strings | The credential was bound to a different stage than the one that ran | `ci-cd-engineer` |
| Upload rejected on certificate fingerprint | Signed with a key other than the expected upload key | `tech-lead-sdk-platform` |
| Installs only on the developer's device | Built with Unity's debug keystore, because the custom keystore was never enabled | `ci-cd-engineer` |
| `keytool`/`jarsigner` password errors | A wrong or truncated secret — often a trailing newline in a stored value | `ci-cd-engineer` |

## Distribution

| Signature | Class | Owner |
|---|---|---|
| Permission denied fetching app information | The service account lacks the App Distribution role, or the credential path is empty on this agent | `ci-cd-engineer`; `tech-lead-sdk-platform` if the role must be granted |
| An error naming the app id | The other platform's id, or an id from a different Firebase project | `ci-cd-engineer` |
| AAB rejected | The Firebase app is not linked to Google Play | `tech-lead-sdk-platform` |
| Upload succeeds, nobody is notified | An empty group, or a group alias that does not exist | `ci-cd-engineer` |
| Auth worked yesterday, fails today, nothing changed | A personal token rather than a service account — the person's access changed | `ci-cd-engineer`, and the fix is the service account |

## Rules for reporting this class

| Rule | Reason |
|---|---|
| Never quote a log line containing a secret | Report the line's identity and mask the value; a triage report is read widely and stored permanently |
| Never file it against the merging feature | The timing is coincidence; the configuration was going to fail on the next run regardless |
| Say whether the fault is the identity or the wiring | They have different owners, and the distinction is usually visible in the same log line |
| Say whether a rebuild is required | A profile or signing fault often cannot be repaired by re-running the failed stage, and a receiver who does not know that will try three times |
# Android Lanes and Signing

Sources: [g] `actions/gradle/`, [s] `getting-started/android/setup/`, both under the `Docs:` base.

## Routes

| | A — Unity signs | B — export Gradle, Fastlane signs |
|---|---|---|
| Unity produces | Signed `.apk`/`.aab` | Gradle project (`EditorUserBuildSettings.exportAsGoogleAndroidProject = true`) |
| Signs in | Editor, from `PlayerSettings.Android` keystore properties supplied by the job environment | `gradle` action, from a `signingConfig` reading environment values |
| Choose when | No Gradle-level customisation needed (common case) | Manifest merging, Gradle plugins, several signed variants from one export, or signing must stay out of the Unity process |
| Cost | Keystore password in the Unity process environment during the build | A second build step and a Gradle config to maintain |

**Caveat:** Route A followed by a Fastlane signing step re-signs a signed artifact; it fails opaquely or yields a signature the store rejects.

## `gradle` action (Route B)

| Parameter | Fact that decides [g] |
|---|---|
| `task` | `assemble` for APK, `bundle` for AAB |
| `build_type` | `Release`, matched to the Gradle build type carrying the signing config |
| `properties` | Hash passed as `-P`; how keystore path, alias and passwords reach Gradle without a file |
| `print_command` | Set `false` when properties carry secrets; default prints the full command line |

```ruby
gradle(
  task: 'bundle', build_type: 'Release', project_dir: 'build/android-export/',
  print_command: false,
  properties: {
    'android.injected.signing.store.file' => ENV['KEYSTORE_PATH'],
    'android.injected.signing.store.password' => ENV['KEYSTORE_PASSWORD'],
    'android.injected.signing.key.alias' => ENV['KEY_ALIAS'],
    'android.injected.signing.key.password' => ENV['KEY_PASSWORD']
  }
)
```

## APK vs AAB

| Output | Accepted by | Note |
|---|---|---|
| `.apk` | App Distribution, direct install | The only format a tester or device test installs directly |
| `.aab` | App Distribution, Google Play | Play requires it for new releases; App Distribution converts it and needs the app's Play linking. Build both, or build the AAB and let distribution convert; decide before upload time |

## Play App Signing

- Upload key: held by the project in the CI credential store; signs what the pipeline uploads. Losing it is recoverable (reset); a wrong one is rejected at upload with a certificate-fingerprint message.
- App signing key: held by Google; signs what users receive. A tester build (upload key) and a store release are signed by different keys by design.

## Failure signatures

| Symptom | Cause |
|---|---|
| `INSTALL_PARSE_FAILED_NO_CERTIFICATES` | Never signed: Route A ran without the keystore properties |
| Installs only on the developer's device | Signed with Unity's debug keystore (`useCustomKeystore` false) |
| Upload rejected on fingerprint | Signed with a key other than the expected upload key |
| Signing config resolves to empty strings | Environment variables bound to a different stage than the lane's |

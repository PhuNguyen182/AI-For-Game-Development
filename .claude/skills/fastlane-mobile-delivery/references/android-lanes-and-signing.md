# Android Lanes and Signing — the two routes, and what each costs

Source: [gradle action](https://docs.fastlane.tools/actions/gradle/), [Actions reference](https://docs.fastlane.tools/actions/), [Android setup](https://docs.fastlane.tools/getting-started/android/setup/).
Covers: SKILL.md §4 — **"Decide the Android route before writing the lane — Unity signs, or Gradle does"**.

A Unity Android build can leave the editor already signed, or leave as a Gradle project that Fastlane then
builds and signs. Both are valid; the failure this file exists to prevent is choosing neither deliberately
and ending up with an artifact signed twice, signed with a debug key, or not signed at all.

## The two routes

| | Route A — Unity signs | Route B — export Gradle, Fastlane signs |
|---|---|---|
| Unity produces | A finished, signed `.apk` or `.aab` | A Gradle project (`EditorUserBuildSettings.exportAsGoogleAndroidProject = true`) |
| Signing happens | Inside the editor, from `PlayerSettings.Android` keystore properties supplied by the job's environment | In the `gradle` action's build type, from a `signingConfig` reading environment values |
| Fastlane's job | Deliver what already exists | Build and sign, then deliver |
| Choose when | Nothing needs Gradle-level customisation — the common case | Manifest merging, Gradle plugins, several signed variants from one export, or signing that must not touch the Unity process |
| Cost | The keystore password lives in the Unity process environment for the build's duration | A second build step, and a Gradle configuration to maintain alongside the Unity project |

Pick one and say which in the handoff. The dangerous state is Route A followed by a Fastlane signing step
that "makes sure" — re-signing an already-signed artifact either fails opaquely or produces a file whose
signature does not match what the store expects.

## The `gradle` action, for Route B

| Parameter | Sets | Source |
|---|---|---|
| `task` | `assemble` for an APK, `bundle` for an AAB | [gradle](https://docs.fastlane.tools/actions/gradle/) |
| `build_type` | `Release` — matched to the Gradle build type that carries the signing config | same |
| `project_dir` | The exported Gradle project's directory | same |
| `properties` | A hash passed as `-P` properties — the route by which keystore path, alias and passwords reach Gradle without being written into a file | same |
| `print_command` | `false` when properties carry secrets; the default prints the full command line | same |

```ruby
gradle(
  task: 'bundle',
  build_type: 'Release',
  project_dir: 'build/android-export/',
  print_command: false,
  properties: {
    'android.injected.signing.store.file' => ENV['KEYSTORE_PATH'],
    'android.injected.signing.store.password' => ENV['KEYSTORE_PASSWORD'],
    'android.injected.signing.key.alias' => ENV['KEY_ALIAS'],
    'android.injected.signing.key.password' => ENV['KEY_PASSWORD']
  }
)
```

Every value comes from the environment the job bound, per [ci-keychain-and-credentials.md](ci-keychain-and-credentials.md). None is written into a file the workspace keeps.

## APK against AAB

| Output | Accepted by | Notes |
|---|---|---|
| `.apk` | Firebase App Distribution, direct install, side-loading | The only format a tester installs directly; the format a device test uses |
| `.aab` | Firebase App Distribution, Google Play | Play requires it for new releases. App Distribution converts it internally and needs the app's Play/App Distribution configuration to allow that |

A pipeline that distributes to testers and also uploads to Play generally builds both, or builds the `.aab`
and lets distribution handle the conversion. Decide it explicitly rather than discovering it at upload time.

## Play App Signing changes what the keystore is

| Key | Held by | Signs |
|---|---|---|
| Upload key | The project, in the CI credential store | What the pipeline uploads to Play |
| App signing key | Google, under Play App Signing | What users actually receive |

Under Play App Signing, losing the upload key is recoverable — it can be reset — while an artifact signed
with the wrong upload key is rejected at upload with a message about certificate fingerprints. A build
distributed through App Distribution is signed with the upload key too, so a tester's install and a store
release are signed by different keys by design. That is expected, not a defect.

## Failure signatures

| Symptom | Cause |
|---|---|
| `INSTALL_PARSE_FAILED_NO_CERTIFICATES` on a device | The artifact was never signed — a Route A build that ran without the keystore properties set |
| Upload rejected on certificate fingerprint | Signed with a different key than the one Play expects |
| The build succeeds and installs, but only on the developer's device | Signed with Unity's debug keystore, because `useCustomKeystore` was false and nobody noticed |
| A Gradle signing config resolving to empty strings | Environment variables absent in the lane's process; the job bound them to a different stage |
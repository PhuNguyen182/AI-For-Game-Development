# Distribute Command and Auth — the upload step itself

Source: [Distribute Android with the CLI](https://firebase.google.com/docs/app-distribution/android/distribute-cli), [Distribute iOS with the CLI](https://firebase.google.com/docs/app-distribution/ios/distribute-cli), [Distribute with fastlane](https://firebase.google.com/docs/app-distribution/android/distribute-fastlane), [Firebase CLI](https://firebase.google.com/docs/cli).
Covers: SKILL.md §4 — **"Authenticate with a service account, never with a personal login or a long-lived CI token"**, **"Upload only what App Distribution accepts, and archive everything else"**, **"Verify the release the upload created rather than trusting the step's exit status"**.

Two equivalent surfaces — the CLI and the fastlane plugin — plus the authentication that makes either work on
a machine nobody logged into, and the evidence that proves the upload actually produced a release.

## The CLI

```bash
firebase appdistribution:distribute build/android/game.aab \
  --app "$FIREBASE_APP_ID_ANDROID" \
  --groups "qa" \
  --release-notes-file ci/release-notes.txt
```

| Flag | Takes | Notes |
|---|---|---|
| `--app` | The Firebase app id | Required; not the package name |
| `--groups` | Comma-separated group **aliases** | The alias, not the display name shown in the console |
| `--groups-file` | A path listing aliases | Preferred when the set is long enough to be edited |
| `--testers`, `--testers-file` | Individual addresses | Use only where no group fits; see [testers-groups-and-release-notes.md](testers-groups-and-release-notes.md) |
| `--release-notes`, `--release-notes-file` | Text, or a path to it | A file avoids shell quoting problems with multi-line notes |
| `--debug` | — | Verbose output; safe here because no secret is passed on the command line |

## The fastlane plugin

```ruby
firebase_app_distribution(
  app: ENV['FIREBASE_APP_ID_ANDROID'],
  android_artifact_path: 'build/android/game.aab',
  android_artifact_type: 'AAB',
  service_credentials_file: ENV['GOOGLE_APPLICATION_CREDENTIALS'],
  groups: 'qa',
  release_notes_file: 'ci/release-notes.txt'
)
```

| Parameter | Equivalent to |
|---|---|
| `app` | `--app` |
| `android_artifact_path` / `ipa_path` | The positional artifact argument |
| `android_artifact_type` | `APK` or `AAB` — state it rather than relying on the extension |
| `service_credentials_file` | `GOOGLE_APPLICATION_CREDENTIALS` |
| `groups`, `testers`, `release_notes`, `release_notes_file` | The same flags |

Choose the plugin when the pipeline already runs Fastlane for signing — one toolchain, one place secrets are
bound. Choose the CLI when the upload stands alone. Never both in one pipeline: two versions of the same
integration drift, and only one of them gets updated.

## Authentication

| Route | How | Verdict |
|---|---|---|
| **Service account** | A Google Cloud service account granted the App Distribution admin role; its JSON key bound as a secret **file** and exposed as `GOOGLE_APPLICATION_CREDENTIALS` | The only route a pipeline should use — scoped to one capability, owned by the project rather than by a person |
| `firebase login:ci` token | A token minted from a personal account, passed as `FIREBASE_TOKEN` or `--token` | Legacy. Carries that person's full authority, breaks when their access changes, and cannot be scoped |
| Interactive `firebase login` | A browser flow | Impossible on a headless agent |

The service-account file is a credential: bound by the job, never committed, never archived, never echoed —
per `jenkins-pipeline-authoring`'s secret rules.

## Artifact acceptance

| Type | Accepted | Condition |
|---|---|---|
| `.apk` | Yes | None beyond signing |
| `.aab` | Yes | The Firebase app must be linked to its Google Play app in the console; without that link the upload is rejected |
| `.ipa` | Yes | Must be ad-hoc (or enterprise) signed, and the installing device's UDID must have been in the profile at build time |
| PC / standalone builds | **No** | Not an app artifact; archive it on the job instead |

Large artifacts can exceed the service's per-file limit. Confirm the current limit against the documentation
rather than assuming a number here, and treat a rejected upload on a large `.aab` as a size question before
anything else.

## Evidence and failure signatures

A successful upload prints a link to the release in the Firebase console. **Capture and report it** — it is
the only artifact proving a release exists, and a green pipeline is not one.

| Symptom | Cause |
|---|---|
| `Failed to fetch app information` / permission denied | The service account lacks the App Distribution role, or `GOOGLE_APPLICATION_CREDENTIALS` points at nothing on this agent |
| An error naming the app id | The wrong platform's id, or an id from a different Firebase project |
| AAB rejected | The app is not linked to Google Play in the Firebase console |
| Upload succeeds, no tester is notified | Distributed to a group with no members, or to a group alias that does not exist |
| Testers receive it and cannot install (iOS) | The ad-hoc profile did not contain their devices — a build-time fact no upload can repair |

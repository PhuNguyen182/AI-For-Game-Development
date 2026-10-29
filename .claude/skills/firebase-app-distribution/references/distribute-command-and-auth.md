# Distribute Command and Auth

Sources: [Android CLI](https://firebase.google.com/docs/app-distribution/android/distribute-cli), [iOS CLI](https://firebase.google.com/docs/app-distribution/ios/distribute-cli), [fastlane](https://firebase.google.com/docs/app-distribution/android/distribute-fastlane). Run `firebase appdistribution:distribute --help` for the installed flag set.

## CLI
```bash
firebase appdistribution:distribute build/android/game.aab \
  --app "$FIREBASE_APP_ID_ANDROID" --groups "qa" --release-notes-file ci/release-notes.txt
```
- `--groups` takes the group alias, not the console display name; `--groups-file` for long sets.
- `--testers`/`--testers-file` only for a one-off.
- `--release-notes-file` avoids shell quoting of multi-line notes.

## fastlane plugin
```ruby
firebase_app_distribution(
  app: ENV['FIREBASE_APP_ID_ANDROID'],
  android_artifact_path: 'build/android/game.aab',
  android_artifact_type: 'AAB',   # state it, do not rely on the extension
  service_credentials_file: ENV['GOOGLE_APPLICATION_CREDENTIALS'],
  groups: 'qa', release_notes_file: 'ci/release-notes.txt')
```
iOS uses `ipa_path`. Choose the plugin when the pipeline already runs fastlane for signing; otherwise the CLI.

## Auth
Service account (App Distribution admin role), JSON bound as a secret file. `firebase login:ci` (`FIREBASE_TOKEN`/`--token`) is legacy and personal; interactive `firebase login` cannot run headless.

## Artifact acceptance
| Type | Condition |
|---|---|
| `.apk` | Signed |
| `.aab` | Firebase app linked to its Google Play app, else rejected |
| `.ipa` | Ad-hoc or enterprise signed; device UDID in the profile at build time |
| PC build | Not accepted |

A rejected large `.aab` is a size question first; check the current per-file limit in the docs.

## Failure signatures
| Symptom | Cause |
|---|---|
| `Failed to fetch app information` / permission denied | Service account lacks the role, or `GOOGLE_APPLICATION_CREDENTIALS` points at nothing on this agent |
| Error naming the app id | Wrong platform's id, or an id from another Firebase project |
| AAB rejected | No Google Play link |
| Success, nobody notified | Group has no members or the alias does not exist |
| iOS testers cannot install | Profile lacked their devices |

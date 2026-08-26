# Root Links — App Distribution documentation, the CLI, and what this is not

Source: [Firebase App Distribution](https://firebase.google.com/docs/app-distribution), [Firebase CLI](https://firebase.google.com/docs/cli), [Distribute with fastlane (Android)](https://firebase.google.com/docs/app-distribution/android/distribute-fastlane).
Covers: SKILL.md §4 — **"Address the app by its Firebase App ID, never by package name or bundle id"**, **"Pin the `firebase-tools` version the pipeline installs"**.

Firebase documents the current CLI only, and `firebase-tools` releases frequently — flags are added and
behaviour is adjusted between minor versions with no version segment in the URL to pin against. A pipeline
that installs "latest" therefore changes behaviour on nights nobody touched it, which is why the version is
pinned in the job and the documentation is treated as describing something newer than what runs.

| Root | Holds | Source |
|---|---|---|
| App Distribution | Concepts, console setup, tester management | [App Distribution](https://firebase.google.com/docs/app-distribution) |
| Distribute — Android, CLI | The `appdistribution:distribute` command and its flags | [Android CLI](https://firebase.google.com/docs/app-distribution/android/distribute-cli) |
| Distribute — iOS, CLI | The same command for `.ipa`, plus the ad-hoc requirement | [iOS CLI](https://firebase.google.com/docs/app-distribution/ios/distribute-cli) |
| Distribute — fastlane | The `firebase_app_distribution` plugin and its parameters | [Android fastlane](https://firebase.google.com/docs/app-distribution/android/distribute-fastlane), [iOS fastlane](https://firebase.google.com/docs/app-distribution/ios/distribute-fastlane) |
| Manage testers | Groups, invitations, and tester state | [Manage testers](https://firebase.google.com/docs/app-distribution/manage-testers) |
| Firebase CLI | Installation, authentication, and version behaviour | [CLI reference](https://firebase.google.com/docs/cli) |

## The app id

| Form | Example | Notes |
|---|---|---|
| Android | `1:1234567890:android:0a1b2c3d4e5f6789` | Found in the Firebase console's project settings, per app |
| iOS | `1:1234567890:ios:0a1b2c3d4e5f6789` | A **different** id for the same game — the two are not interchangeable |
| Package name / bundle id | `com.studio.game` | **Not** accepted by `--app`. It identifies the app to the store, not to Firebase |

One project holds both apps; a pipeline that builds both platforms carries both ids and picks by platform.
Passing the Android id to an iOS upload fails on an artifact-type mismatch rather than on the id, which is
why the id is stated in the pipeline's own documentation rather than inferred.

## Pinning the CLI

```bash
npm install --no-save firebase-tools@<pinned-version>   # or a version-locked global install on the agent
npx firebase --version                                  # log it: the version is part of the run's evidence
```

Log the version in the run. When behaviour changes between two runs whose inputs were identical, the CLI
version is the first thing worth comparing, and it only exists in the log if something printed it.

## What App Distribution is not

| Not | Owner |
|---|---|
| A store channel, or a substitute for Google Play or App Store review | `tech-lead-sdk-platform` |
| TestFlight — Apple's own testing channel, reached by an `app-store` export | `tech-lead-sdk-platform` |
| Crashlytics, Analytics, or Remote Config, which are separate Firebase products compiled into the game | `tech-lead-sdk-platform` |
| A place to host a PC build; the accepted artifact types are APK, AAB and IPA | `jenkins-pipeline-authoring`, which archives it instead |

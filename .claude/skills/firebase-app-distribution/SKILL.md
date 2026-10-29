---
name: firebase-app-distribution
description: "Firebase App Distribution: `firebase appdistribution:distribute`, fastlane `firebase_app_distribution`, app id, group aliases, release notes, service-account auth, iOS ad-hoc UDIDs. Use when shipping signed builds to internal testers."
user-invocable: false
---

# Firebase App Distribution

Not for: producing or signing the artifact (`fastlane-mobile-delivery`, `unity-batchmode-cli`), the job and its approval gate (`jenkins-pipeline-authoring`), Crashlytics/Analytics/Remote Config in the game (`firebase-unity-sdk`), store submission and TestFlight (`sdk-platform-engineer`), runtime faults in the installed build (`build-release-engineer`). When the upload is a plugin action, the lane and `Pluginfile` stay with `fastlane-mobile-delivery`; this skill owns the action's parameters, auth and verification.
Docs: https://firebase.google.com/docs/app-distribution — unversioned, describes the newest `firebase-tools`; pin the version the pipeline installs.

| Reference | Read when |
|---|---|
| [distribute-command-and-auth.md](references/distribute-command-and-auth.md) | Writing the upload step, wiring auth, or an upload fails |
| [testers-groups-and-release-notes.md](references/testers-groups-and-release-notes.md) | Choosing who receives a build, an iOS build installs for nobody, or composing release notes |

## Steps
1. **Authenticate with a service account** holding the App Distribution role, bound by the job as a secret file and exposed as `GOOGLE_APPLICATION_CREDENTIALS`. A personal login or `firebase login:ci` token carries one person's full authority and dies with their access.
2. **Address the app by Firebase App ID**, not package name or bundle id. Android (`1:…:android:…`) and iOS (`1:…:ios:…`) are different ids in one project; the wrong one fails with a misleading error.
3. **Upload only APK, AAB or IPA.** A PC build has no path here: archive it on the job. AAB needs the app linked to Google Play in the Firebase console; verify before a pipeline depends on it.
4. **iOS: confirm the ad-hoc profile already holds every tester's UDID.** A missing UDID needs a profile update and a new build; the upload cannot detect it (cycle in the testers reference).
5. **Distribute to a group alias**, not an address list. `--testers` only for a genuine one-off.
6. **Generate release notes from the run** (version, build number, branch, short commit, what changed), per the testers reference.
7. **Pin `firebase-tools`** (`npm install --no-save firebase-tools@<version>`) and log `npx firebase --version`; a floating CLI changes flag behaviour between identical runs and looks like a broken credential.
8. **Verify the release.** Capture the release link the CLI or plugin prints and report it; exit code 0 is not evidence anyone received a build.
9. **Missing app id, group alias or credential id:** state the assumption in the output; a wrong app id delivers to the wrong audience.

## Never
- Distribute to real testers without the request or approval `ci-cd-engineer` requires: an upload reaches people and cannot be recalled.
- Commit, archive or echo the service-account JSON, or embed tester emails in the repo.
- Use App Distribution as a public release channel.
- Use both the CLI and the plugin in one pipeline; they drift.

## Output
```
## App Distribution — <platform and audience>
- Artifact: <type, path, what signed it>
- App id: <id and platform>
- Audience: <group aliases>
- Release notes: <fields and sources>
- Auth: <credential id and variable, never values>
- Invocation: <exact command or plugin call>
- Release verified: <release link, or not run>
- Known limitations: <...>
```
On request only, add `Latent concerns` and `Future remediation`, each with its trigger.

## Example
- "Use `firebase login:ci` and put the token in the job, it's quicker" → declined: unscoped, breaks when the minter's access changes; used a service account with only the App Distribution role.

---
name: fastlane-mobile-delivery
description: "Package and sign Unity mobile builds with Fastlane: Fastfile lanes, gradle for APK/AAB, gym over the Xcode project, match, build numbers, CI keychain. Use when automating mobile packaging or signing."
user-invocable: false
---

# Fastlane Mobile Delivery

Not for: the Unity build itself (`unity-batchmode-cli`), the job that calls the lane (`jenkins-pipeline-authoring`), the tester upload (`firebase-app-distribution`), store submission and policy (`sdk-platform-engineer`), runtime faults in the installed artifact (`build-release-engineer`).
Docs: https://docs.fastlane.tools — unversioned (describes the newest release), so the version that runs is the one `Gemfile.lock` pins.

| Reference | Read when |
|---|---|
| [android-lanes-and-signing.md](references/android-lanes-and-signing.md) | Writing or changing an Android lane, or an install/upload rejects the signature |
| [ios-lanes-signing-and-match.md](references/ios-lanes-signing-and-match.md) | Writing or changing an iOS lane, or an `.ipa` fails signing or installs for nobody |
| [ci-keychain-and-credentials.md](references/ci-keychain-and-credentials.md) | The lane runs on a CI agent, or a secret must reach it |

## Steps
1. **Keep every lane in `fastlane/Fastfile` and run it the same on a laptop and on CI** — absorb machine differences with `setup_ci`, `readonly` match and workspace-relative paths, not two lanes, per [ci-keychain-and-credentials.md](references/ci-keychain-and-credentials.md).
2. **Pin the toolchain** — commit `Gemfile`, `Gemfile.lock`, `fastlane/Pluginfile`, `fastlane/Appfile` (identifiers only); ignore `fastlane/report.xml` and `fastlane/README.md` (generated); invoke `bundle exec fastlane <platform> <lane>` after `bundle install --deployment`, never bare `fastlane`, or a newly resolved gem changes behaviour with no commit. `bundle exec fastlane lanes` lists lanes; `bundle exec fastlane env` prints versions for a bug report.
3. **Android: decide who signs before writing the lane** — Unity signs, or export a Gradle project and sign with the `gradle` action, per [android-lanes-and-signing.md](references/android-lanes-and-signing.md). Mixing them signs twice or not at all.
4. **iOS: build the Xcode project Unity emitted** — `cocoapods` when a `Podfile` exists, then `build_app` over the workspace, per [ios-lanes-signing-and-match.md](references/ios-lanes-signing-and-match.md). Unity does not produce an `.ipa`.
5. **Match `export_method` to the destination** — `ad-hoc` for registered test devices, `app-store` for TestFlight/review, `development` for a debug install. A wrong method fails late with an entitlements error that does not name it.
6. **Stage signing material in a throwaway keychain** — `setup_ci` first; secrets come from the job's credential store, per [ci-keychain-and-credentials.md](references/ci-keychain-and-credentials.md).
7. **`match` is `readonly: true` on CI** — a misconfigured agent then fails instead of revoking certificates every other machine uses.
8. **Set the build number once, from the CI run, in the Unity build** (`unity-batchmode-cli`); do not also `increment_build_number` in the lane. To know the number, read it.
9. **Keep store submission out of the delivery lane** — `upload_to_testflight` and `upload_to_play_store` go in a separate lane a human triggers; never promote a build or notify testers from a build lane.
10. **Name every credential id, bundle id, team id, keystore alias and Play service account the lane needs** — state a missing one as an assumption rather than guessing; the guess fails after the slowest step.

## Never
- Commit a keystore, `.p12`, `.p8`, `.mobileprovision`, password or `.env` with values — removing it needs a published-history rewrite (`git-expert`, blast radius 3). Declining "it's a private repo": bind the keystore as a secret file and pass passwords as environment variables.
- Run `match` in write mode from CI.
- Let a lane continue past a signing failure — Fastlane will hand over the path to an unsigned or wrongly signed file.
- Assume a logged-in user, an unlocked keychain or a selected Xcode toolchain; state each as a job requirement.

## Output
```
## Fastlane Delivery — <platform and lane>
- Lane: <name and invoking command>
- Input: <what Unity produced and where>
- Route: <Android Unity-signed / Gradle-signed; iOS export method and why>
- Signing: <keystore/certificate source, keychain handling, match mode>
- Versioning: <source of version and build number>
- Credentials required: <ids and env var names, never values>
- Output: <artifact type and path>
- Known limitations: <...>
```
On request only, add `Latent concerns` and `Future remediation`, each with its trigger.

## Example
- iOS lane passes locally, fails on CI with a signing error naming no profile → keychain state, not signing config: the laptop had an unlocked login keychain with the certificate. Fixed with `setup_ci` plus `match(readonly: true)`, which fails loudly if the store lacks what the profile needs.

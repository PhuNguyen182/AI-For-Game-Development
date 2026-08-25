---
name: fastlane-mobile-delivery
description: >
  Technique for packaging and signing a Unity mobile build with Fastlane —
  `Fastfile`, `Appfile`, `Pluginfile`, `platform`/`lane`, the `gradle` action
  for APK and AAB, `build_app`/`gym` over the Xcode project Unity emits,
  `cocoapods`, `match`/`sync_code_signing`, `app_store_connect_api_key`,
  `setup_ci` temporary keychains, `export_method` and `export_options`, and
  `bundle exec fastlane <platform> <lane>`. Covers keystore and certificate
  handling on an ephemeral CI agent. Not for: the Unity build itself
  (`unity-batchmode-cli`); the job that calls the lane
  (`jenkins-pipeline-authoring`); the tester upload
  (`firebase-app-distribution`); store submission and policy
  (`tech-lead-sdk-platform`).
---

# Fastlane Mobile Delivery — packaging and signing Android and iOS

## Bundled resources

### References
Read-only context, loaded on demand so SKILL.md itself stays short.

| File | Contents | Read when |
|---|---|---|
| [root-links.md](references/root-links.md) | Fastlane documentation roots, the files a setup owns, and the plugin surface | Starting any task here, or an action turns out not to exist in this version |
| [android-lanes-and-signing.md](references/android-lanes-and-signing.md) | The two Android routes, the `gradle` action, keystore handling, APK against AAB, Play App Signing | Writing or changing an Android lane |
| [ios-lanes-signing-and-match.md](references/ios-lanes-signing-and-match.md) | `build_app`/`gym` over Unity's Xcode output, `cocoapods`, `match`, export methods, App Store Connect API keys | Writing or changing an iOS lane |
| [ci-keychain-and-credentials.md](references/ci-keychain-and-credentials.md) | `setup_ci`, keychain lifetime, which secrets a lane reads from the environment, and what must never be committed | The lane runs on a CI agent rather than on someone's machine |

## 1. Objective
Turn a Unity build into a signed, installable artifact the same way every time, on a machine nobody logged into. The failures this prevents are the ones that only appear on CI: a lane that works locally because the developer's keychain was already unlocked, an iOS build signed with a profile that does not include the CI machine's certificate, an artifact signed with the wrong key that installs for nobody, a build number that collides with one already uploaded, and a lane that quietly continued after signing failed and delivered an unsigned file.

## 2. Role
Act as the mobile packaging and signing specialist for the devops track, on behalf of `ci-cd-engineer`. You own what happens between the Unity output and a distributable artifact. Producing that Unity output, scheduling the lane, uploading the result, and everything about the stores themselves belong elsewhere.

## 3. When to invoke this skill
- A `Fastfile` lane is being written or changed for Android or iOS.
- Unity has produced an Xcode project or a Gradle project and it must become an `.ipa` or an `.aab`/`.apk`.
- Signing material — a keystore, a certificate, a provisioning profile — must reach an ephemeral agent.
- A lane passes locally and fails on CI, or the reverse.
- The build number or version must be set consistently across what Unity produced and what is packaged.
- Negative trigger: the Unity invocation that produced the input — that is `unity-batchmode-cli`.
- Negative trigger: the job, agent label, credential binding or lock around the lane — that is `jenkins-pipeline-authoring`.
- Negative trigger: uploading the finished artifact to testers — that is `firebase-app-distribution`.
- Negative trigger: submitting to a store, store policy, review rules, and obtaining the signing identity in the first place — that is `tech-lead-sdk-platform`.
- Negative trigger: a runtime fault in the signed artifact once installed — that is `build-verification-tester`.

## 4. How to use this skill
1. **Keep every lane in `fastlane/Fastfile` and make it run identically on a laptop and on CI** — a lane that only works inside the job is untestable before the job runs, and a lane that only works locally is not the thing shipping. Environment differences belong behind `is_ci` and `setup_ci`, per [ci-keychain-and-credentials.md](references/ci-keychain-and-credentials.md), not behind two divergent lanes.
2. **Pin the toolchain with `Gemfile` and invoke through `bundle exec fastlane`** — a lane is only reproducible if the Fastlane version is, and an agent that resolves a newer gem set mid-week produces a failure nobody changed anything to cause, per [root-links.md](references/root-links.md).
3. **Decide the Android route before writing the lane — Unity signs, or Gradle does** — letting Unity sign is the shorter path and keeps one artifact; exporting a Gradle project and signing with the `gradle` action is what you choose when Gradle-level control is genuinely needed, per [android-lanes-and-signing.md](references/android-lanes-and-signing.md). Pick one deliberately: mixing them produces an artifact signed twice or not at all.
4. **Build iOS from the Xcode project Unity emitted, never from Unity directly** — Unity does not produce an `.ipa`, so the lane runs `cocoapods` when the project has a `Podfile` and then `build_app` over the workspace, per [ios-lanes-signing-and-match.md](references/ios-lanes-signing-and-match.md).
5. **Match `export_method` to where the build is going** — `ad-hoc` for a build distributed to registered test devices, `app-store` for anything reaching TestFlight or review, `development` for a debug install. An `.ipa` exported the wrong way installs for nobody and the error message names entitlements rather than the export.
6. **Take signing material from the job's credential store and stage it in a throwaway keychain** — call `setup_ci` so the lane creates and unlocks a temporary keychain rather than assuming a logged-in user's, and let the keychain die with the workspace, per [ci-keychain-and-credentials.md](references/ci-keychain-and-credentials.md).
7. **Run `match` in read-only mode on CI** — `readonly: true` means a misconfigured agent fails instead of minting and revoking certificates that break every other machine, per [ios-lanes-signing-and-match.md](references/ios-lanes-signing-and-match.md).
8. **Set the build number from the CI run, and set it once** — take it from the job's build number in the Unity build per `unity-batchmode-cli`, and do not also increment it in the lane; two sources produce artifacts that disagree about their own version.
9. **Keep store submission out of the delivery lane** — `upload_to_testflight` and `upload_to_play_store` exist, and they belong in a separate, explicitly requested lane that a human triggers, never at the end of a build lane. Store submission itself is `tech-lead-sdk-platform`'s decision to make.
10. **State every credential id, account and identifier the lane needs rather than assuming one** — a bundle id, a team id, a keystore alias or a Play service account guessed here fails at the signing step after the whole build has already run.

## 5. Specific goals / tasks this skill performs
- Writing `Fastfile` lanes for Android and iOS that a CI job invokes by name.
- Choosing and implementing the Android signing route, for APK or AAB output.
- Turning Unity's Xcode output into a signed `.ipa` with the correct export method.
- Wiring `match` and App Store Connect API key authentication for a headless agent.
- Setting up and tearing down a CI keychain so signing works with no logged-in user.
- Naming the credential ids and identifiers a lane requires before it can run.
- Out of scope: the Unity build (`unity-batchmode-cli`); job orchestration (`jenkins-pipeline-authoring`); tester distribution (`firebase-app-distribution`); store submission, policy and identity provisioning (`tech-lead-sdk-platform`).

## 6. Output format
```
## Fastlane Delivery — <platform and lane>
- Lane: <fastlane/Fastfile lane name, and the command that invokes it>
- Input: <what Unity produced, and where the lane expects it>
- Route: <Android: Unity-signed or Gradle-signed / iOS: export method chosen, and why>
- Signing: <keystore or certificate source, keychain handling, match mode>
- Versioning: <where the version and build number come from>
- Credentials required: <ids and environment variable names — never values>
- Output: <artifact type and path the lane produces>
- Layer: Editor-only
- Known limitations: <...>
```

**Extended report — emit ONLY when the requester asks for it.** It replaces the one-line `Known limitations` above with all three fields:
```
- Known limitations: <what this lane does not cover — a platform, a configuration, a store>
- Latent concerns: <what holds only under current conditions — a certificate expiring, one macOS agent, a manual profile>
- Future remediation: <the concrete fix for each concern above, each with the condition that should trigger it>
```

## 7. Examples
**Example 1**
- Input: Unity emitted an Xcode project on a macOS agent; the build must reach internal testers on registered devices.
- Output: a lane running `setup_ci`, `cocoapods` (the project has a `Podfile` from the Firebase SDK), `match(type: 'adhoc', readonly: true)` authenticating with `app_store_connect_api_key`, then `build_app` with `export_method: 'ad-hoc'` and an explicit profile mapping. The build number came from the Unity build, not from `increment_build_number`. The `.ipa` path is returned for the upload step, which the lane does not perform.

**Example 2**
- Input: "Just commit the keystore and its passwords into `fastlane/` — it's a private repository."
- Output: declined. A private repository is still permanent, widely readable history, and removing a committed key needs a rewrite of published history — `git-expert`'s radius 3. The keystore is bound as a secret file by the job and reaches the lane as a path, with the passwords as environment variables, per §4 step 6; the lane names the credential ids it expects and nothing else.

**Example 3**
- Input: the iOS lane succeeds on a developer's machine and fails on the CI agent with a code-signing error naming no profile.
- Output: traced to keychain state, not to signing configuration — the local machine had an unlocked login keychain with the certificate already installed, and the agent had neither. Fixed by `setup_ci` plus `match(readonly: true)`, so the agent builds its own temporary keychain from the shared certificate store and fails loudly if that store lacks what the profile requires.

## 8. Edge cases & guardrails
- Never commit a keystore, a `.p12`, a `.p8`, a provisioning profile, or any password — they are credentials, and history is not erasable without a published-history rewrite.
- Never run `match` in write mode from CI; regenerating certificates on an agent revokes what every other machine and every other pipeline was using.
- Never let a lane continue past a signing failure — an unsigned or wrongly-signed artifact that reaches a tester costs more than a failed build, and Fastlane will happily hand you the path to one.
- Never submit to a store, promote a build, or notify testers from a build lane; those are separate, explicitly triggered actions, per `ci-cd-engineer`'s guardrails.
- Never set the version in two places — Unity and the lane disagreeing produces an artifact whose reported version is not the one that was built.
- Never assume the agent has a logged-in user, an unlocked keychain, or Xcode's default toolchain selected; state each as a requirement the job must satisfy.
- If a bundle id, team id, keystore alias or account is missing from the request, state the assumption in the output rather than guessing — the guess fails after the slowest step in the pipeline.
---
name: firebase-app-distribution
description: >
  Technique for delivering a signed Android or iOS build to testers with
  Firebase App Distribution — `firebase appdistribution:distribute`, the
  `--app` Firebase App ID, `--groups`, `--testers`, `--release-notes` and
  `--release-notes-file`, the `firebase_app_distribution` fastlane plugin,
  service-account authentication through `GOOGLE_APPLICATION_CREDENTIALS`,
  `firebase-tools` version pinning, APK/AAB/IPA acceptance, and the ad-hoc
  UDID constraint on iOS. Not for: producing or signing the artifact
  (`fastlane-mobile-delivery`, `unity-batchmode-cli`); the job and its
  approval gate (`jenkins-pipeline-authoring`); Crashlytics, Analytics and
  Remote Config inside the game (`tech-lead-sdk-platform`).
---

# Firebase App Distribution — getting a build to testers

## Bundled resources

### References
Read-only context, loaded on demand so SKILL.md itself stays short.

| File | Contents | Read when |
|---|---|---|
| [root-links.md](references/root-links.md) | Documentation roots, the CLI and plugin surfaces, and what App Distribution is not | Starting any task here, or a flag turns out not to exist in the installed CLI |
| [distribute-command-and-auth.md](references/distribute-command-and-auth.md) | The command and its flags, the plugin's parameters, service-account auth, artifact acceptance, and failure signatures | Writing or changing the upload step |
| [testers-groups-and-release-notes.md](references/testers-groups-and-release-notes.md) | Group aliases, tester management, the iOS UDID cycle, and what release notes should carry | Deciding who receives a build and what they are told about it |

## 1. Objective
Deliver a build to the people who are meant to test it, and be able to say afterwards exactly which build reached them. The failures this prevents are the ones that waste a QA day: an upload authenticated as a person who has since left, a build distributed to a group nobody is in, an iOS release that installs for no one because their devices were never in the profile, a release note that says "test build" so nobody knows which commit they are looking at, and a "successful" upload that silently produced no release.

## 2. Role
Act as the tester-distribution specialist for the devops track, on behalf of `ci-cd-engineer`. You own the step between a signed artifact and a tester's device. Building and signing that artifact, scheduling the step, and everything the Firebase SDK does inside the running game belong elsewhere.

## 3. When to invoke this skill
- A signed `.apk`, `.aab` or `.ipa` must reach internal testers.
- The upload step of a pipeline is being written, or its authentication is failing.
- Tester groups, membership, or who receives which build must be decided in the pipeline.
- Release notes must carry enough for a tester to report a defect against the right build.
- An iOS build reached App Distribution but installs for nobody.
- Negative trigger: producing or signing the artifact — that is `unity-batchmode-cli` and `fastlane-mobile-delivery`.
- Negative trigger: the job, the credential binding, and the human approval before the upload — that is `jenkins-pipeline-authoring`.
- Negative trigger: Crashlytics, Analytics, Remote Config, or any Firebase SDK compiled into the game — that is `tech-lead-sdk-platform`, a different Firebase entirely.
- Negative trigger: submitting to Google Play or App Store review, and TestFlight — that is `tech-lead-sdk-platform`; App Distribution is not a store channel.
- Negative trigger: a runtime fault in the distributed build — that is `build-verification-tester`.

## 4. How to use this skill
1. **Authenticate with a service account, never with a personal login or a long-lived CI token** — a token minted from someone's account stops working when they leave and grants everything they have, per [distribute-command-and-auth.md](references/distribute-command-and-auth.md). The service-account JSON is bound as a secret file by the job and reaches the step as `GOOGLE_APPLICATION_CREDENTIALS`.
2. **Address the app by its Firebase App ID, never by package name or bundle id** — `--app` takes the `1:…:android:…` form, and the package name is not an accepted alias. Android and iOS are two different app ids for the same game, and passing one where the other belongs fails with an error that does not say so, per [root-links.md](references/root-links.md).
3. **Upload only what App Distribution accepts, and archive everything else** — APK, AAB and IPA are the accepted artifact types, per [distribute-command-and-auth.md](references/distribute-command-and-auth.md). A PC build has no path here at all and belongs in the job's own artifact archive, per `jenkins-pipeline-authoring`. AAB distribution additionally requires the app to be linked to Google Play in the Firebase console — verify that before a pipeline depends on it.
4. **Confirm the iOS profile covers the testers before distributing to them** — an ad-hoc `.ipa` installs only on devices whose UDIDs were in the provisioning profile at build time, so a new tester needs their UDID collected, the profile updated, and a **new build**, per [testers-groups-and-release-notes.md](references/testers-groups-and-release-notes.md). Nothing about the upload can detect this.
5. **Distribute to a named group rather than to a list of individual addresses** — a group alias is edited in one place when someone joins or leaves; an address list embedded in a pipeline goes stale silently and is edited by whoever notices, per [testers-groups-and-release-notes.md](references/testers-groups-and-release-notes.md).
6. **Generate release notes from the run rather than writing them by hand** — the branch, the commit, the build number and what changed, per [testers-groups-and-release-notes.md](references/testers-groups-and-release-notes.md). A tester's defect report is only actionable if it names the build it came from, and a note that says "latest build" makes every report ambiguous.
7. **Verify the release the upload created rather than trusting the step's exit status** — capture the release link the CLI or plugin returns and report it, per [distribute-command-and-auth.md](references/distribute-command-and-auth.md). A step that exits zero having uploaded nothing is a real failure mode, and "the pipeline was green" is not evidence a build reached anyone.
8. **Pin the `firebase-tools` version the pipeline installs** — a CLI that self-updates changes flag behaviour on a night nobody touched the pipeline, and the failure looks like a broken credential. Log the version it resolved, per [root-links.md](references/root-links.md).
9. **State the app id, group alias and credential id the step needs rather than assuming any of them** — all three are project facts, none is guessable, and a wrong one either fails at the last step of a long pipeline or delivers a build to the wrong audience.

## 5. Specific goals / tasks this skill performs
- Writing the upload step, as a CLI invocation or as a Fastlane plugin action.
- Wiring service-account authentication for a headless agent.
- Choosing the artifact type and confirming the project is configured to accept it.
- Deciding tester groups and keeping membership out of the pipeline file.
- Composing release notes from the run's own metadata.
- Reporting the resulting release, with the link that proves it exists.
- Out of scope: building and signing (`unity-batchmode-cli`, `fastlane-mobile-delivery`); job orchestration and approval (`jenkins-pipeline-authoring`); the Firebase SDK inside the game and store submission (`tech-lead-sdk-platform`); verifying the build once installed (`build-verification-tester`).

## 6. Output format
```
## App Distribution — <platform and audience>
- Artifact: <type and path, and what signed it>
- App id: <the Firebase app id used, and which platform it belongs to>
- Audience: <group aliases; individual testers only where a group could not serve>
- Release notes: <what they carry, and where each value comes from>
- Auth: <service account credential id and the variable it arrives in — never values>
- Invocation: <the exact command or plugin call>
- Release verified: <the release link returned, or explicitly not run>
- Layer: Editor-only
- Known limitations: <...>
```

**Extended report — emit ONLY when the requester asks for it.** It replaces the one-line `Known limitations` above with all three fields:
```
- Known limitations: <who this does not reach, and which artifact types are not covered>
- Latent concerns: <what holds only under current conditions — an ad-hoc profile filling up, a group with one member, an unpinned CLI>
- Future remediation: <the concrete fix for each concern above, each with the condition that should trigger it>
```

## 7. Examples
**Example 1**
- Input: a signed `.aab` from the Android lane must reach the QA group after a human approves it.
- Output: an upload step running after the pipeline's `input` gate, authenticating through a service-account file bound by the job, addressing the app by its Android app id, distributing to the `qa` group alias, with release notes assembled from branch, short commit and build number. The returned release link is reported. Noted as a limitation: AAB distribution depends on the app's Play link in the Firebase console, which was confirmed rather than assumed.

**Example 2**
- Input: "Use `firebase login:ci` and put the token in the job — it's quicker than a service account."
- Output: declined. The token carries the full authority of the person who minted it, stops working when their access changes, and cannot be scoped to distribution alone; it is also the legacy path Firebase has moved away from. Replaced with a service account holding only the App Distribution role, bound as a secret file, per §4 step 1.

**Example 3**
- Input: an iOS release uploaded successfully, and three of five testers report that the build will not install.
- Output: identified as the ad-hoc UDID constraint rather than a distribution fault. The three devices were not in the provisioning profile when the `.ipa` was signed, so no re-upload can fix it — their UDIDs are collected, the profile updated, and a new build produced and distributed. Reported with the note that the upload step cannot detect this case and never will.

## 8. Edge cases & guardrails
- Never distribute a build to real testers without the explicit request or approval that `ci-cd-engineer`'s guardrails require — an upload reaches people and cannot be recalled.
- Never authenticate as a person, and never commit a service-account JSON; it is a credential, and `security-reviewer` treats a committed one as a leak.
- Never embed a tester's email list in the pipeline file — membership belongs in the group, and a stale list is a privacy problem as well as a delivery one.
- Never report a distribution as done without the release link; an exit code is not evidence a release exists.
- Never assume an AAB, or a new tester, will work — both depend on configuration outside the pipeline (the Play link, the ad-hoc profile) that the upload cannot see.
- Never use App Distribution as a release channel to the public; it is an internal testing surface, and store distribution is `tech-lead-sdk-platform`'s.
- If the app id, group alias, or credential id is missing from the request, state the assumption in the output rather than guessing — the wrong app id delivers a build to the wrong audience, which is worse than not delivering it.

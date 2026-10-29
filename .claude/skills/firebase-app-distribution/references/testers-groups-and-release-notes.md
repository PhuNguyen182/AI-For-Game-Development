# Testers, Groups and Release Notes

Sources: [Manage testers](https://firebase.google.com/docs/app-distribution/manage-testers), [iOS CLI](https://firebase.google.com/docs/app-distribution/ios/distribute-cli).

## Groups
- Membership is edited once in the Firebase console; an address list in the pipeline goes stale and copies personal data into git history.
- The alias is the stable identifier `--groups` takes; renaming the display name does not change it.
- An upload to a wrong alias or an empty group can still succeed and nothing reports it. Confirm the alias exists and has members when the pipeline is written and when QA staffing changes.

## iOS UDID cycle
An ad-hoc `.ipa` installs only on devices in the provisioning profile at signing time.
1. A new tester joins the group and receives the release.
2. Install fails for them alone.
3. Collect their UDID (testers who register through App Distribution; the plugin has an action to pull the list).
4. Add it in the Apple developer portal and regenerate the profile (`match` handling in `fastlane-mobile-delivery`).
5. Produce and distribute a **new build**; the existing release cannot be repaired.

Adding a tester therefore needs a rebuild, and Apple's per-year device limit caps how many this route serves.

## Release notes
```
<app> <version> (build <build number>)
branch <branch> · commit <short sha>
<what changed: trigger, ticket, or merged branch subject>
```
Sources: version/build from the build (`unity-batchmode-cli`), `env.BRANCH_NAME`, shortened `env.GIT_COMMIT`. Keep it short: clients truncate long notes, so the identifying lines come first. Never write "latest build" or "test build".

## Pipeline anti-patterns
- Distributing on every merge: testers stop reading notifications.
- Reusing a version or build number across releases.

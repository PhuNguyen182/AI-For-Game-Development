# Testers, Groups and Release Notes — who receives a build, and what they are told

Source: [Manage testers](https://firebase.google.com/docs/app-distribution/manage-testers), [Distribute iOS with the CLI](https://firebase.google.com/docs/app-distribution/ios/distribute-cli), [App Distribution](https://firebase.google.com/docs/app-distribution).
Covers: SKILL.md §4 — **"Confirm the iOS profile covers the testers before distributing to them"**, **"Distribute to a named group rather than to a list of individual addresses"**, **"Generate release notes from the run rather than writing them by hand"**.

The audience side of a distribution, which is where the failures are social rather than technical: a build
that reaches nobody, reaches the wrong people, or reaches the right people who cannot tell what they are
looking at.

## Groups against individual testers

| | Group alias | Individual addresses in the pipeline |
|---|---|---|
| Edited | Once, in the Firebase console, by whoever manages QA | In the pipeline file, by whoever notices it is stale |
| Review needed to change | None | A code change and a review |
| When someone leaves | They are removed once; every pipeline follows | They keep receiving builds until someone remembers |
| Personal data | Held in Firebase, where it already is | Copied into a git repository, permanently |

Distribute to a group. Reserve `--testers` for a genuine one-off — a single external reviewer for one build —
and even then prefer creating a group for it, because a one-off distribution is exactly the one nobody
remembers to clean up.

| Term | Means |
|---|---|
| Group **alias** | The identifier `--groups` takes — lowercase, stable, not the display name |
| Display name | What the console shows; changing it does not change the alias |
| Tester state | Invited, accepted, or not yet installed — visible in the console, not in the upload's output |

An upload to a group whose alias is wrong, or whose membership is empty, succeeds. Nothing in the pipeline
reports it. Confirm the alias exists and has members when the pipeline is written, and again when the QA
audience changes.

## The iOS UDID cycle

An ad-hoc `.ipa` installs only on devices listed in the provisioning profile **at signing time**. The
consequence is a loop that must be understood before an iOS pipeline is trusted:

1. A new tester is added to the group and receives the release.
2. Their device is not in the profile, so the install fails — for them alone, silently as far as the pipeline is concerned.
3. Their UDID is collected. App Distribution can gather UDIDs from testers who register through it, and the fastlane plugin exposes an action for pulling that list.
4. The UDID is added to the Apple developer portal and the profile regenerated, per `fastlane-mobile-delivery`'s `match` handling.
5. **A new build is produced and distributed.** The existing release cannot be repaired; it was signed without them.

Two facts follow, and both belong in an iOS pipeline's documentation: adding a tester requires a rebuild, and
Apple's per-year device limit for a development account is a real ceiling on how many testers this route can
serve.

## Release notes

The note is what turns a tester's report into an actionable defect. Assemble it from the run:

```
<app> <version> (build <build number>)
branch <branch> · commit <short sha>
<what changed — the trigger, the ticket, or the merged branch's subject>
```

| Field | From | Why it earns its line |
|---|---|---|
| Version and build number | The build, per `unity-batchmode-cli` | The defect report names a build that can be found again |
| Branch | `env.BRANCH_NAME` | Says whether this is the release candidate or an experiment |
| Commit | `env.GIT_COMMIT`, shortened | The only value that identifies the code exactly |
| What changed | The trigger, the ticket, or the commit subject | Tells the tester where to look, which is the difference between coverage and a random walk |

Keep it short — long notes are truncated in the tester's client, and the identifying lines are the ones that
must survive. Never write "latest build" or "test build": every report against it becomes ambiguous, and the
ambiguity is only discovered when someone tries to reproduce a defect weeks later.

## What the pipeline should never do

| Never | Why |
|---|---|
| Embed tester email addresses in the repository | Personal data in permanent history, and a list that goes stale unnoticed |
| Distribute automatically on every merge | Testers stop reading notifications, and the one build that mattered is lost in the noise |
| Reuse a version or build number across releases | Two distinct releases become indistinguishable in every report about either |
| Report a distribution without the release link | An exit code is not evidence that anyone received anything, per `verification-standards.md` |
